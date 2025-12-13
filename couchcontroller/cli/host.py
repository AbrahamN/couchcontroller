#!/usr/bin/env python3
"""
CouchController Host CLI

Runs on the machine with the game.
Captures screen, creates virtual controllers, and streams to clients.
"""

import sys
import logging
import argparse
import time
from ..host.screen_capture import ScreenStreamer
from ..host.virtual_controller import VirtualControllerManager
from ..network.server import GameServer
from ..common.protocol import ControllerState


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def check_vigem_driver():
    """
    Check if ViGEmBus driver is installed and working

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        import vgamepad as vg

        # Try to create a test controller
        try:
            test_gamepad = vg.VX360Gamepad()
            test_gamepad.reset()
            del test_gamepad
            return True, "ViGEmBus driver detected and working"
        except Exception as e:
            return False, f"ViGEmBus driver error: {e}"

    except ImportError:
        return False, "vgamepad module not installed"


class CouchControllerHost:
    """Main host application"""

    def __init__(self, monitor: int = 1, fps: int = 60, max_clients: int = 4):
        """
        Initialize host

        Args:
            monitor: Monitor to capture (1 = primary)
            fps: Target FPS for screen capture
            max_clients: Maximum number of clients
        """
        self.monitor = monitor
        self.fps = fps
        self.max_clients = max_clients

        # Components
        self.screen_streamer = None
        self.controller_manager = None
        self.server = None

        # State
        self.running = False
        self.frame_count = 0

    def start(self):
        """Start the host"""
        logger.info("=" * 60)
        logger.info("CouchController Host Starting")
        logger.info("=" * 60)

        try:
            # Initialize components
            self._init_components()

            # Start server
            self.server.start()

            # Start screen streaming
            self.screen_streamer.start(frame_callback=self._on_frame_encoded)

            self.running = True

            logger.info("")
            logger.info("=" * 60)
            logger.info("HOST READY!")
            logger.info("=" * 60)
            logger.info(f"Monitor: {self.monitor}")
            logger.info(f"Target FPS: {self.fps}")
            logger.info(f"Max clients: {self.max_clients}")
            logger.info("")
            logger.info("Clients can connect with:")
            logger.info(f"  couchcontroller-client --host {self.server._get_local_ip()}")
            logger.info("")
            logger.info("Press Ctrl+C to stop")
            logger.info("=" * 60)

            # Main loop - just keep alive
            try:
                while self.running:
                    time.sleep(1.0)

                    # Print stats every 5 seconds
                    if self.frame_count % (self.fps * 5) == 0:
                        clients = self.server.get_connected_clients()
                        logger.info(f"Status: {len(clients)} clients connected, {self.frame_count} frames sent")

            except KeyboardInterrupt:
                logger.info("\nShutdown requested...")

        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
        finally:
            self.stop()

    def _init_components(self):
        """Initialize all components"""
        logger.info("Initializing components...")

        # Screen streamer
        self.screen_streamer = ScreenStreamer(
            monitor=self.monitor,
            fps=self.fps
        )

        # Virtual controller manager
        self.controller_manager = VirtualControllerManager(
            max_controllers=self.max_clients
        )

        # Network server
        self.server = GameServer()
        self.server.on_client_connect = self._on_client_connect
        self.server.on_client_disconnect = self._on_client_disconnect
        self.server.on_controller_input = self._on_controller_input

        logger.info("Components initialized")

    def _on_client_connect(self, client_id: str) -> int:
        """Handle client connection"""
        logger.info(f"Client connecting: {client_id}")

        # Assign controller slot
        slot = self.controller_manager.assign_controller(client_id)

        if slot is not None:
            logger.info(f"Assigned controller slot {slot} to {client_id}")
        else:
            logger.warning(f"No controller slots available for {client_id}")

        return slot

    def _on_client_disconnect(self, client_id: str):
        """Handle client disconnect"""
        logger.info(f"Client disconnected: {client_id}")

    def _on_controller_input(self, client_id: str, slot: int, state: ControllerState):
        """Handle controller input from client"""
        # Update virtual controller
        self.controller_manager.update_controller(slot, state)

    def _on_frame_encoded(self, frame_data: bytes, timestamp: float):
        """Handle encoded video frame"""
        # Broadcast to all clients
        self.server.broadcast_video_frame(frame_data, self.frame_count)
        self.frame_count += 1

    def stop(self):
        """Stop the host"""
        if not self.running:
            return

        logger.info("Stopping host...")
        self.running = False

        # Stop components
        if self.screen_streamer:
            self.screen_streamer.stop()

        if self.controller_manager:
            self.controller_manager.disconnect_all()

        if self.server:
            self.server.stop()

        logger.info("Host stopped")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='CouchController Host - Share your screen and accept remote controllers',
        epilog='For more info: https://github.com/abrahamn/couchcontroller'
    )
    parser.add_argument(
        '--monitor',
        type=int,
        default=1,
        help='Monitor to capture (1 = primary monitor, 0 = all monitors)'
    )
    parser.add_argument(
        '--fps',
        type=int,
        default=60,
        help='Target frames per second (default: 60)'
    )
    parser.add_argument(
        '--max-clients',
        type=int,
        default=4,
        help='Maximum number of clients (default: 4)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    parser.add_argument(
        '--skip-driver-check',
        action='store_true',
        help='Skip ViGEmBus driver check (not recommended)'
    )

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Check for ViGEmBus driver
    if not args.skip_driver_check:
        success, message = check_vigem_driver()

        if not success:
            logger.error("")
            logger.error("=" * 60)
            logger.error("VIRTUAL CONTROLLER DRIVER NOT FOUND")
            logger.error("=" * 60)
            logger.error("")
            logger.error("CouchController Host requires the ViGEmBus driver to create")
            logger.error("virtual Xbox controllers that games can detect.")
            logger.error("")
            logger.error("Installation steps:")
            logger.error("")
            logger.error("1. Install vgamepad:")
            logger.error("   pip install vgamepad")
            logger.error("")
            logger.error("2. Download and install ViGEmBus driver:")
            logger.error("   https://github.com/ViGEm/ViGEmBus/releases")
            logger.error("   - Download: ViGEmBus_Setup_x64.exe")
            logger.error("   - Run as Administrator")
            logger.error("   - Restart your computer")
            logger.error("")
            logger.error("3. Verify installation:")
            logger.error("   couchcontroller-test")
            logger.error("")
            logger.error("Note: ViGEmBus is only needed on the HOST machine.")
            logger.error("Clients do NOT need it.")
            logger.error("")
            logger.error(f"Error details: {message}")
            logger.error("=" * 60)
            return 1
        else:
            logger.info(f"✓ {message}")

    # Create and run host
    host = CouchControllerHost(
        monitor=args.monitor,
        fps=args.fps,
        max_clients=args.max_clients
    )

    try:
        host.start()
    except KeyboardInterrupt:
        pass

    return 0


if __name__ == '__main__':
    sys.exit(main())
