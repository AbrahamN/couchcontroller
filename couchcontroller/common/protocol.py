"""Network protocol definitions and message formats"""

import struct
from enum import IntEnum
from typing import NamedTuple


class MessageType(IntEnum):
    """Message types for network communication"""
    # Control messages
    HELLO = 0           # Client -> Host: Initial connection
    WELCOME = 1         # Host -> Client: Connection accepted
    PING = 2            # Bidirectional: Keep-alive
    PONG = 3            # Bidirectional: Keep-alive response
    DISCONNECT = 4      # Bidirectional: Clean disconnect

    # Controller messages
    CONTROLLER_STATE = 10   # Client -> Host: Controller input state
    CONTROLLER_ASSIGN = 11  # Host -> Client: Assigned controller slot

    # Video stream messages
    VIDEO_FRAME = 20        # Host -> Client: Encoded video frame
    VIDEO_CONFIG = 21       # Host -> Client: Video stream configuration


class ControllerState(NamedTuple):
    """Controller input state - compatible with Xbox 360 controller layout"""
    # Buttons (16 bits total)
    button_a: bool
    button_b: bool
    button_x: bool
    button_y: bool
    button_lb: bool
    button_rb: bool
    button_back: bool
    button_start: bool
    button_lstick: bool      # Left stick press
    button_rstick: bool      # Right stick press
    dpad_up: bool
    dpad_down: bool
    dpad_left: bool
    dpad_right: bool

    # Analog axes (16-bit signed integers, -32768 to 32767)
    lstick_x: int
    lstick_y: int
    rstick_x: int
    rstick_y: int

    # Triggers (8-bit unsigned, 0 to 255)
    trigger_l: int
    trigger_r: int

    @classmethod
    def pack(cls, state: 'ControllerState') -> bytes:
        """Pack controller state into bytes for network transmission"""
        # Pack buttons into 2 bytes (16 bits)
        buttons = 0
        buttons |= state.button_a << 0
        buttons |= state.button_b << 1
        buttons |= state.button_x << 2
        buttons |= state.button_y << 3
        buttons |= state.button_lb << 4
        buttons |= state.button_rb << 5
        buttons |= state.button_back << 6
        buttons |= state.button_start << 7
        buttons |= state.button_lstick << 8
        buttons |= state.button_rstick << 9
        buttons |= state.dpad_up << 10
        buttons |= state.dpad_down << 11
        buttons |= state.dpad_left << 12
        buttons |= state.dpad_right << 13

        # Pack: buttons(H), lstick_x(h), lstick_y(h), rstick_x(h), rstick_y(h), trigger_l(B), trigger_r(B)
        # Total: 14 bytes
        return struct.pack(
            '!Hhhh BB',
            buttons,
            state.lstick_x,
            state.lstick_y,
            state.rstick_x,
            state.rstick_y,
            state.trigger_l,
            state.trigger_r
        )

    @classmethod
    def unpack(cls, data: bytes) -> 'ControllerState':
        """Unpack controller state from bytes"""
        buttons, lstick_x, lstick_y, rstick_x, rstick_y, trigger_l, trigger_r = struct.unpack(
            '!Hhhh BB', data
        )

        return cls(
            button_a=bool(buttons & (1 << 0)),
            button_b=bool(buttons & (1 << 1)),
            button_x=bool(buttons & (1 << 2)),
            button_y=bool(buttons & (1 << 3)),
            button_lb=bool(buttons & (1 << 4)),
            button_rb=bool(buttons & (1 << 5)),
            button_back=bool(buttons & (1 << 6)),
            button_start=bool(buttons & (1 << 7)),
            button_lstick=bool(buttons & (1 << 8)),
            button_rstick=bool(buttons & (1 << 9)),
            dpad_up=bool(buttons & (1 << 10)),
            dpad_down=bool(buttons & (1 << 11)),
            dpad_left=bool(buttons & (1 << 12)),
            dpad_right=bool(buttons & (1 << 13)),
            lstick_x=lstick_x,
            lstick_y=lstick_y,
            rstick_x=rstick_x,
            rstick_y=rstick_y,
            trigger_l=trigger_l,
            trigger_r=trigger_r
        )


class NetworkMessage:
    """Base class for network messages"""

    HEADER_SIZE = 8  # Type(1) + Sequence(3) + Length(4)
    MAX_PAYLOAD_SIZE = 65507 - HEADER_SIZE  # UDP max - header

    def __init__(self, msg_type: MessageType, payload: bytes = b'', sequence: int = 0):
        self.msg_type = msg_type
        self.payload = payload
        self.sequence = sequence % (2**24)  # 24-bit sequence number

    def pack(self) -> bytes:
        """Pack message into bytes for transmission"""
        header = struct.pack(
            '!BII',
            self.msg_type,
            self.sequence & 0xFFFFFF,  # 24-bit sequence
            len(self.payload)
        )
        return header + self.payload

    @classmethod
    def unpack(cls, data: bytes) -> 'NetworkMessage':
        """Unpack message from bytes"""
        if len(data) < cls.HEADER_SIZE:
            raise ValueError(f"Message too short: {len(data)} < {cls.HEADER_SIZE}")

        msg_type, sequence, payload_len = struct.unpack('!BII', data[:cls.HEADER_SIZE])
        payload = data[cls.HEADER_SIZE:cls.HEADER_SIZE + payload_len]

        return cls(MessageType(msg_type), payload, sequence)


# Default ports
DEFAULT_CONTROL_PORT = 7777      # TCP for control messages and reliability
DEFAULT_VIDEO_PORT = 7778        # UDP for video stream
DEFAULT_INPUT_PORT = 7779        # UDP for controller input
