"""Host server networking - receives controller input, sends video stream"""

import socket
import threading
import logging
import time
from typing import Dict, Callable, Optional
from ..common.protocol import (
    NetworkMessage,
    MessageType,
    ControllerState,
    DEFAULT_CONTROL_PORT,
    DEFAULT_VIDEO_PORT,
    DEFAULT_INPUT_PORT
)


logger = logging.getLogger(__name__)


class Client:
    """Represents a connected client"""

    def __init__(self, client_id: str, address: tuple, controller_slot: Optional[int] = None):
        self.client_id = client_id
        self.address = address
        self.controller_slot = controller_slot
        self.last_seen = time.time()
        self.sequence = 0

    def update_last_seen(self):
        """Update last seen timestamp"""
        self.last_seen = time.time()

    def is_active(self, timeout: float = 10.0) -> bool:
        """Check if client is still active"""
        return (time.time() - self.last_seen) < timeout


class GameServer:
    """
    Host server that manages client connections and data streams
    Uses UDP for low-latency video and input
    """

    def __init__(
        self,
        control_port: int = DEFAULT_CONTROL_PORT,
        video_port: int = DEFAULT_VIDEO_PORT,
        input_port: int = DEFAULT_INPUT_PORT
    ):
        """
        Initialize game server

        Args:
            control_port: Port for control messages (TCP)
            video_port: Port for video streaming (UDP)
            input_port: Port for controller input (UDP)
        """
        self.control_port = control_port
        self.video_port = video_port
        self.input_port = input_port

        # Client management
        self.clients: Dict[str, Client] = {}
        self.clients_lock = threading.Lock()

        # Sockets
        self.control_socket: Optional[socket.socket] = None
        self.video_socket: Optional[socket.socket] = None
        self.input_socket: Optional[socket.socket] = None

        # Callbacks
        self.on_client_connect: Optional[Callable[[str], Optional[int]]] = None
        self.on_client_disconnect: Optional[Callable[[str], None]] = None
        self.on_controller_input: Optional[Callable[[str, int, ControllerState], None]] = None

        # Running state
        self.running = False
        self._threads = []

    def start(self):
        """Start the server"""
        if self.running:
            return

        logger.info("Starting CouchController server...")

        # Create sockets
        self._create_sockets()

        self.running = True

        # Start receiver threads
        input_thread = threading.Thread(target=self._input_receiver_loop)
        input_thread.daemon = True
        input_thread.start()
        self._threads.append(input_thread)

        # Start client timeout checker
        timeout_thread = threading.Thread(target=self._client_timeout_loop)
        timeout_thread.daemon = True
        timeout_thread.start()
        self._threads.append(timeout_thread)

        logger.info(f"Server started on ports: input={self.input_port}, video={self.video_port}")
        logger.info(f"Clients can connect to: {self._get_local_ip()}:{self.input_port}")

    def _create_sockets(self):
        """Create UDP sockets for video and input"""
        # Input socket (receive controller data from clients)
        self.input_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.input_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.input_socket.bind(('0.0.0.0', self.input_port))
        self.input_socket.settimeout(1.0)  # 1 second timeout for clean shutdown

        # Video socket (send video frames to clients)
        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.video_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Increase socket buffer sizes for better performance
        try:
            self.video_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024)  # 1MB send buffer
            self.input_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 256 * 1024)   # 256KB receive buffer
        except:
            pass

    def _input_receiver_loop(self):
        """Receive controller input from clients"""
        while self.running:
            try:
                data, address = self.input_socket.recvfrom(4096)

                # Parse message
                try:
                    msg = NetworkMessage.unpack(data)
                except Exception as e:
                    logger.warning(f"Failed to parse message from {address}: {e}")
                    continue

                # Handle message based on type
                if msg.msg_type == MessageType.HELLO:
                    self._handle_hello(address, msg)
                elif msg.msg_type == MessageType.CONTROLLER_STATE:
                    self._handle_controller_input(address, msg)
                elif msg.msg_type == MessageType.PING:
                    self._handle_ping(address, msg)
                elif msg.msg_type == MessageType.DISCONNECT:
                    self._handle_disconnect(address, msg)

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    logger.error(f"Error in input receiver: {e}")

    def _handle_hello(self, address: tuple, msg: NetworkMessage):
        """Handle client connection request"""
        client_id = f"{address[0]}:{address[1]}"

        logger.info(f"Client connecting: {client_id}")

        # Check if already connected
        with self.clients_lock:
            if client_id in self.clients:
                client = self.clients[client_id]
                client.update_last_seen()
                # Resend welcome
                self._send_welcome(client)
                return

        # Assign controller slot via callback
        controller_slot = None
        if self.on_client_connect:
            controller_slot = self.on_client_connect(client_id)

        if controller_slot is None:
            logger.warning(f"Cannot accept client {client_id}: no controller slots available")
            return

        # Create client
        client = Client(client_id, address, controller_slot)

        with self.clients_lock:
            self.clients[client_id] = client

        # Send welcome message
        self._send_welcome(client)

        logger.info(f"Client {client_id} connected (controller slot {controller_slot})")

    def _send_welcome(self, client: Client):
        """Send welcome message to client"""
        # Payload: controller_slot (1 byte)
        payload = bytes([client.controller_slot])

        msg = NetworkMessage(MessageType.WELCOME, payload)
        self._send_to_client(client.address, msg)

    def _handle_controller_input(self, address: tuple, msg: NetworkMessage):
        """Handle controller input from client"""
        client_id = f"{address[0]}:{address[1]}"

        with self.clients_lock:
            if client_id not in self.clients:
                logger.warning(f"Received input from unknown client: {client_id}")
                return

            client = self.clients[client_id]
            client.update_last_seen()

        # Parse controller state
        try:
            state = ControllerState.unpack(msg.payload)
        except Exception as e:
            logger.warning(f"Failed to parse controller state from {client_id}: {e}")
            return

        # Callback with controller input
        if self.on_controller_input and client.controller_slot is not None:
            self.on_controller_input(client_id, client.controller_slot, state)

    def _handle_ping(self, address: tuple, msg: NetworkMessage):
        """Handle ping from client"""
        client_id = f"{address[0]}:{address[1]}"

        with self.clients_lock:
            if client_id in self.clients:
                self.clients[client_id].update_last_seen()

        # Send pong
        pong = NetworkMessage(MessageType.PONG)
        self._send_to_client(address, pong)

    def _handle_disconnect(self, address: tuple, msg: NetworkMessage):
        """Handle client disconnect"""
        client_id = f"{address[0]}:{address[1]}"

        logger.info(f"Client disconnecting: {client_id}")

        with self.clients_lock:
            if client_id in self.clients:
                client = self.clients[client_id]
                del self.clients[client_id]

                # Notify callback
                if self.on_client_disconnect:
                    self.on_client_disconnect(client_id)

    def _client_timeout_loop(self):
        """Check for client timeouts"""
        while self.running:
            time.sleep(5.0)  # Check every 5 seconds

            with self.clients_lock:
                # Find timed out clients
                timed_out = [
                    client_id
                    for client_id, client in self.clients.items()
                    if not client.is_active()
                ]

                # Remove timed out clients
                for client_id in timed_out:
                    logger.warning(f"Client timeout: {client_id}")
                    client = self.clients[client_id]
                    del self.clients[client_id]

                    # Notify callback
                    if self.on_client_disconnect:
                        self.on_client_disconnect(client_id)

    def broadcast_video_frame(self, frame_data: bytes, sequence: int = 0):
        """
        Broadcast video frame to all connected clients

        Args:
            frame_data: Encoded video frame data
            sequence: Sequence number for this frame
        """
        if not self.video_socket:
            return

        msg = NetworkMessage(MessageType.VIDEO_FRAME, frame_data, sequence)
        packed = msg.pack()

        with self.clients_lock:
            for client in self.clients.values():
                try:
                    self.video_socket.sendto(packed, (client.address[0], self.video_port))
                except Exception as e:
                    logger.error(f"Failed to send video to {client.client_id}: {e}")

    def _send_to_client(self, address: tuple, msg: NetworkMessage):
        """Send message to specific client"""
        if not self.input_socket:
            return

        try:
            self.input_socket.sendto(msg.pack(), address)
        except Exception as e:
            logger.error(f"Failed to send to {address}: {e}")

    def get_connected_clients(self) -> list:
        """Get list of connected client IDs"""
        with self.clients_lock:
            return list(self.clients.keys())

    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def stop(self):
        """Stop the server"""
        if not self.running:
            return

        logger.info("Stopping server...")
        self.running = False

        # Close sockets
        if self.input_socket:
            self.input_socket.close()
        if self.video_socket:
            self.video_socket.close()

        # Wait for threads
        for thread in self._threads:
            thread.join(timeout=2.0)

        self._threads.clear()
        self.clients.clear()

        logger.info("Server stopped")

    def __del__(self):
        """Cleanup"""
        self.stop()
