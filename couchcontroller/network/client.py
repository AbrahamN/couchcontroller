"""Client networking - sends controller input, receives video stream"""

import socket
import threading
import logging
import time
from typing import Optional, Callable
from ..common.protocol import (
    NetworkMessage,
    MessageType,
    ControllerState,
    DEFAULT_CONTROL_PORT,
    DEFAULT_VIDEO_PORT,
    DEFAULT_INPUT_PORT
)


logger = logging.getLogger(__name__)


class GameClient:
    """
    Client that connects to host server
    Sends controller input, receives video stream
    """

    def __init__(self, host: str, input_port: int = DEFAULT_INPUT_PORT, video_port: int = DEFAULT_VIDEO_PORT):
        """
        Initialize game client

        Args:
            host: Host IP address or hostname
            input_port: Port for controller input
            video_port: Port for video stream
        """
        self.host = host
        self.input_port = input_port
        self.video_port = video_port

        # Sockets
        self.input_socket: Optional[socket.socket] = None
        self.video_socket: Optional[socket.socket] = None

        # Connection state
        self.connected = False
        self.controller_slot: Optional[int] = None

        # Callbacks
        self.on_video_frame: Optional[Callable[[bytes, int], None]] = None
        self.on_connected: Optional[Callable[[int], None]] = None
        self.on_disconnected: Optional[Callable[[], None]] = None

        # Running state
        self.running = False
        self._threads = []

        # Sequence numbers
        self.input_sequence = 0
        self.video_sequence = 0

    def connect(self) -> bool:
        """
        Connect to host server

        Returns:
            True if connection successful
        """
        logger.info(f"Connecting to {self.host}:{self.input_port}...")

        try:
            # Create sockets
            self.input_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.video_socket.bind(('0.0.0.0', self.video_port))
            self.video_socket.settimeout(1.0)

            # Increase buffer sizes
            try:
                self.input_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 256 * 1024)
                self.video_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024 * 1024)
            except:
                pass

            # Send HELLO message
            hello = NetworkMessage(MessageType.HELLO)
            self.input_socket.sendto(hello.pack(), (self.host, self.input_port))

            # Wait for WELCOME response (with timeout)
            self.input_socket.settimeout(5.0)
            try:
                data, address = self.input_socket.recvfrom(4096)
                msg = NetworkMessage.unpack(data)

                if msg.msg_type == MessageType.WELCOME:
                    # Parse controller slot assignment
                    if len(msg.payload) > 0:
                        self.controller_slot = msg.payload[0]
                        self.connected = True
                        logger.info(f"Connected! Assigned controller slot: {self.controller_slot}")

                        # Start receiver threads
                        self.running = True

                        video_thread = threading.Thread(target=self._video_receiver_loop)
                        video_thread.daemon = True
                        video_thread.start()
                        self._threads.append(video_thread)

                        # Keepalive thread
                        keepalive_thread = threading.Thread(target=self._keepalive_loop)
                        keepalive_thread.daemon = True
                        keepalive_thread.start()
                        self._threads.append(keepalive_thread)

                        # Callback
                        if self.on_connected:
                            self.on_connected(self.controller_slot)

                        return True
                    else:
                        logger.error("Invalid WELCOME message (no controller slot)")
                        return False
                else:
                    logger.error(f"Unexpected response: {msg.msg_type}")
                    return False

            except socket.timeout:
                logger.error("Connection timeout - no response from server")
                return False
            finally:
                self.input_socket.settimeout(None)

        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def _video_receiver_loop(self):
        """Receive video frames from server"""
        while self.running:
            try:
                data, address = self.video_socket.recvfrom(65536)

                # Parse message
                try:
                    msg = NetworkMessage.unpack(data)
                except Exception as e:
                    logger.warning(f"Failed to parse video message: {e}")
                    continue

                if msg.msg_type == MessageType.VIDEO_FRAME:
                    self.video_sequence = msg.sequence

                    # Callback with video frame
                    if self.on_video_frame:
                        self.on_video_frame(msg.payload, msg.sequence)

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    logger.error(f"Error in video receiver: {e}")

    def _keepalive_loop(self):
        """Send keepalive pings to server"""
        while self.running and self.connected:
            time.sleep(2.0)  # Send ping every 2 seconds

            try:
                ping = NetworkMessage(MessageType.PING)
                self.input_socket.sendto(ping.pack(), (self.host, self.input_port))
            except Exception as e:
                logger.error(f"Failed to send keepalive: {e}")

    def send_controller_state(self, state: ControllerState):
        """
        Send controller state to server

        Args:
            state: Controller state to send
        """
        if not self.connected or not self.input_socket:
            return

        try:
            # Pack controller state
            payload = ControllerState.pack(state)

            # Create and send message
            msg = NetworkMessage(MessageType.CONTROLLER_STATE, payload, self.input_sequence)
            self.input_sequence += 1

            self.input_socket.sendto(msg.pack(), (self.host, self.input_port))
        except Exception as e:
            logger.error(f"Failed to send controller state: {e}")

    def disconnect(self):
        """Disconnect from server"""
        if not self.connected:
            return

        logger.info("Disconnecting from server...")

        # Send disconnect message
        try:
            if self.input_socket:
                disconnect = NetworkMessage(MessageType.DISCONNECT)
                self.input_socket.sendto(disconnect.pack(), (self.host, self.input_port))
        except:
            pass

        self.running = False
        self.connected = False

        # Close sockets
        if self.input_socket:
            self.input_socket.close()
        if self.video_socket:
            self.video_socket.close()

        # Wait for threads
        for thread in self._threads:
            thread.join(timeout=2.0)

        self._threads.clear()

        # Callback
        if self.on_disconnected:
            self.on_disconnected()

        logger.info("Disconnected")

    def is_connected(self) -> bool:
        """Check if connected to server"""
        return self.connected

    def __del__(self):
        """Cleanup"""
        self.disconnect()
