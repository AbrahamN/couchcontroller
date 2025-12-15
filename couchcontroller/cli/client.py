#!/usr/bin/env python3
"""
CouchController Client CLI

Runs on the remote player's machine.
Captures controller input, displays host's screen.
"""

import sys
import logging
import argparse
import time
import pygame
import av
import numpy as np
from ..client.controller_input import ControllerReader
from ..client.keyboard_input import KeyboardMapper
from ..network.client import GameClient
from ..common.protocol import ControllerState


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


class VideoDecoder:
    """Decode H264 video frames"""

    def __init__(self):
        self.codec = av.CodecContext.create('h264', 'r')
        self.codec.open()
        self.frame_count = 0
        self.first_frame_decoded = False

    def decode_frame(self, data: bytes) -> list:
        """
        Decode frame data

        Returns:
            List of decoded frames (usually 0 or 1)
        """
        try:
            packets = [av.Packet(data)]
            frames = []

            for packet in packets:
                try:
                    decoded_frames = self.codec.decode(packet)
                    frames.extend(decoded_frames)

                    if decoded_frames and not self.first_frame_decoded:
                        self.first_frame_decoded = True
                        logger.info("Successfully decoded first video frame!")

                except Exception as e:
                    logger.debug(f"Decode error: {e}")

            if not frames and self.frame_count < 100:
                logger.debug("No frames decoded - may be waiting for keyframe")

            self.frame_count += 1
            return frames
        except Exception as e:
            logger.error(f"Failed to decode frame: {e}")
            return []


class CouchControllerClient:
    """Main client application"""

    def __init__(self, host: str, controller_index: int = 0, fullscreen: bool = False, use_keyboard: bool = False):
        """
        Initialize client

        Args:
            host: Host IP address or hostname
            controller_index: Index of controller to use (0 for first)
            fullscreen: Start in fullscreen mode
            use_keyboard: Use keyboard instead of controller
        """
        self.host = host
        self.controller_index = controller_index
        self.fullscreen = fullscreen
        self.use_keyboard = use_keyboard

        # Components
        self.controller_reader = None  # Can be ControllerReader or KeyboardMapper
        self.network_client = None
        self.video_decoder = None

        # Pygame display
        self.screen = None
        self.clock = None

        # State
        self.running = False
        self.connected = False
        self.controller_slot = None
        self.frames_received = 0
        self.last_stats_time = time.time()

    def start(self):
        """Start the client"""
        logger.info("=" * 60)
        logger.info("CouchController Client Starting")
        logger.info("=" * 60)

        try:
            # Initialize components
            self._init_components()

            # Connect to host
            if not self.network_client.connect():
                logger.error("Failed to connect to host")
                return 1

            self.connected = True

            # Wait for controller slot assignment
            time.sleep(0.5)

            if self.controller_slot is None:
                logger.error("No controller slot assigned")
                return 1

            logger.info("")
            logger.info("=" * 60)
            logger.info("CLIENT READY!")
            logger.info("=" * 60)
            logger.info(f"Connected to: {self.host}")
            logger.info(f"Controller: {self.controller_reader.get_controller_name()}")
            logger.info(f"Assigned slot: {self.controller_slot}")
            logger.info("")
            logger.info("Press ESC or close window to disconnect")
            logger.info("=" * 60)

            # Start controller reading
            self.controller_reader.start_reading(
                callback=self._on_controller_state,
                poll_rate=120  # 120 Hz for low latency
            )

            self.running = True

            # Main display loop
            self._display_loop()

        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            return 1
        finally:
            self.stop()

        return 0

    def _init_components(self):
        """Initialize all components"""
        logger.info("Initializing components...")

        # Initialize pygame
        pygame.init()
        self.clock = pygame.time.Clock()

        # Create display window (start small, will resize when video arrives)
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)

        pygame.display.set_caption(f"CouchController - Connecting to {self.host}...")

        # Input reader - keyboard or controller
        if self.use_keyboard:
            logger.info("Using keyboard input")
            self.controller_reader = KeyboardMapper()

            # Print keyboard mapping
            logger.info("")
            logger.info(self.controller_reader.get_mapping_description())
            logger.info("")
        else:
            logger.info("Using controller input")
            self.controller_reader = ControllerReader(controller_index=self.controller_index)

            if not self.controller_reader.is_connected():
                logger.error("")
                logger.error("=" * 60)
                logger.error("NO CONTROLLER DETECTED")
                logger.error("=" * 60)
                logger.error("")
                logger.error("Please connect a game controller and try again.")
                logger.error("")
                logger.error("Troubleshooting:")
                logger.error("1. Connect your controller via USB or Bluetooth")
                logger.error("2. Verify it works in Windows 'Game Controllers' settings")
                logger.error("   - Press Win+R, type 'joy.cpl', press Enter")
                logger.error("3. Try a different USB port")
                logger.error("4. Check for controller driver updates")
                logger.error("")
                logger.error("Alternative: Use keyboard instead")
                logger.error("  couchcontroller-client --host <IP> --keyboard")
                logger.error("")
                logger.error("=" * 60)
                raise RuntimeError("No controller found")

        # Network client
        self.network_client = GameClient(host=self.host)
        self.network_client.on_video_frame = self._on_video_frame
        self.network_client.on_connected = self._on_connected
        self.network_client.on_disconnected = self._on_disconnected

        # Video decoder
        self.video_decoder = VideoDecoder()

        logger.info("Components initialized")

    def _display_loop(self):
        """Main pygame display loop"""
        while self.running:
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            # Update display
            pygame.display.flip()

            # Maintain target FPS (60 for display, controller polling is separate)
            self.clock.tick(60)

            # Print stats every 5 seconds
            now = time.time()
            if now - self.last_stats_time > 5.0:
                logger.info(f"Stats: {self.frames_received} frames received")
                self.last_stats_time = now

    def _on_connected(self, controller_slot: int):
        """Handle connection established"""
        self.controller_slot = controller_slot
        pygame.display.set_caption(
            f"CouchController - Connected (Controller {controller_slot})"
        )

    def _on_disconnected(self):
        """Handle disconnection"""
        self.connected = False
        pygame.display.set_caption("CouchController - Disconnected")

    def _on_controller_state(self, state: ControllerState):
        """Handle controller input"""
        if not self.connected:
            return

        # Send to host
        self.network_client.send_controller_state(state)

    def _on_video_frame(self, frame_data: bytes, sequence: int):
        """Handle received video frame"""
        self.frames_received += 1
        logger.debug(f"Received frame {sequence}, size: {len(frame_data)} bytes")

        # Decode frame
        frames = self.video_decoder.decode_frame(frame_data)

        if not frames:
            logger.debug(f"No frames decoded from sequence {sequence}")
            return

        logger.debug(f"Decoded {len(frames)} frame(s) from sequence {sequence}")

        # Display first frame
        frame = frames[0]

        # Convert to pygame surface
        try:
            # Convert AVFrame to numpy array
            img = frame.to_ndarray(format='rgb24')

            # Create pygame surface
            surface = pygame.surfarray.make_surface(
                np.transpose(img, (1, 0, 2))
            )

            # Scale to fit screen
            screen_size = self.screen.get_size()
            scaled_surface = pygame.transform.scale(surface, screen_size)

            # Blit to screen
            self.screen.blit(scaled_surface, (0, 0))
            logger.debug(f"Frame {sequence} displayed successfully")

        except Exception as e:
            logger.error(f"Failed to display frame: {e}", exc_info=True)

    def stop(self):
        """Stop the client"""
        if not self.running and not self.connected:
            return

        logger.info("Stopping client...")
        self.running = False

        # Stop components
        if self.controller_reader:
            self.controller_reader.stop_reading()

        if self.network_client:
            self.network_client.disconnect()

        if self.screen:
            pygame.quit()

        logger.info("Client stopped")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='CouchController Client - Connect your controller to a remote game',
        epilog='For more info: https://github.com/abrahamn/couchcontroller'
    )
    parser.add_argument(
        '--host',
        type=str,
        required=True,
        help='Host IP address or hostname'
    )
    parser.add_argument(
        '--controller',
        type=int,
        default=0,
        help='Controller index to use (default: 0 = first controller)'
    )
    parser.add_argument(
        '--keyboard',
        action='store_true',
        help='Use keyboard instead of game controller (perfect if you don\'t have a controller!)'
    )
    parser.add_argument(
        '--fullscreen',
        action='store_true',
        help='Start in fullscreen mode'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create and run client
    client = CouchControllerClient(
        host=args.host,
        controller_index=args.controller,
        fullscreen=args.fullscreen,
        use_keyboard=args.keyboard
    )

    try:
        return client.start()
    except KeyboardInterrupt:
        return 0


if __name__ == '__main__':
    sys.exit(main())
