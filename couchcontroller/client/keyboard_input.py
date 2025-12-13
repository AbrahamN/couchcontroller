"""Keyboard input capture and mapping to Xbox controller layout"""

import logging
import pygame
from typing import Optional, Callable, Dict
import threading
import time
from ..common.protocol import ControllerState


logger = logging.getLogger(__name__)


class KeyboardMapper:
    """
    Maps keyboard inputs to Xbox 360 controller layout
    Simple, intuitive mapping for players without controllers
    """

    # Default mapping - can be customized
    DEFAULT_MAPPING = {
        # Left stick (WASD)
        'lstick_up': pygame.K_w,
        'lstick_down': pygame.K_s,
        'lstick_left': pygame.K_a,
        'lstick_right': pygame.K_d,

        # Right stick (Arrow keys)
        'rstick_up': pygame.K_UP,
        'rstick_down': pygame.K_DOWN,
        'rstick_left': pygame.K_LEFT,
        'rstick_right': pygame.K_RIGHT,

        # Face buttons (IJKL - right hand on home row)
        'button_a': pygame.K_j,      # Jump/Accept (most common)
        'button_b': pygame.K_k,      # Back/Cancel
        'button_x': pygame.K_i,      # Left action
        'button_y': pygame.K_l,      # Top action

        # Triggers (Q/E for left/right)
        'trigger_l': pygame.K_q,
        'trigger_r': pygame.K_e,

        # Bumpers (1/2 or Tab/Backspace)
        'button_lb': pygame.K_1,
        'button_rb': pygame.K_2,

        # D-pad (Numpad for alternate or same as right stick)
        'dpad_up': pygame.K_KP8,
        'dpad_down': pygame.K_KP2,
        'dpad_left': pygame.K_KP4,
        'dpad_right': pygame.K_KP6,

        # Menu buttons
        'button_start': pygame.K_RETURN,
        'button_back': pygame.K_BACKSPACE,

        # Stick presses (Shift + WASD/Arrows)
        'button_lstick': pygame.K_LSHIFT,
        'button_rstick': pygame.K_RSHIFT,
    }

    # Alternative mapping for different preferences
    ALTERNATIVE_MAPPING = {
        # Left stick (Arrow keys)
        'lstick_up': pygame.K_UP,
        'lstick_down': pygame.K_DOWN,
        'lstick_left': pygame.K_LEFT,
        'lstick_right': pygame.K_RIGHT,

        # Right stick (IJKL)
        'rstick_up': pygame.K_i,
        'rstick_down': pygame.K_k,
        'rstick_left': pygame.K_j,
        'rstick_right': pygame.K_l,

        # Face buttons (WASD)
        'button_a': pygame.K_w,
        'button_b': pygame.K_s,
        'button_x': pygame.K_a,
        'button_y': pygame.K_d,

        # Rest same as default
        'trigger_l': pygame.K_q,
        'trigger_r': pygame.K_e,
        'button_lb': pygame.K_1,
        'button_rb': pygame.K_2,
        'dpad_up': pygame.K_KP8,
        'dpad_down': pygame.K_KP2,
        'dpad_left': pygame.K_KP4,
        'dpad_right': pygame.K_KP6,
        'button_start': pygame.K_RETURN,
        'button_back': pygame.K_BACKSPACE,
        'button_lstick': pygame.K_LSHIFT,
        'button_rstick': pygame.K_RSHIFT,
    }

    def __init__(self, mapping: Optional[Dict] = None):
        """
        Initialize keyboard mapper

        Args:
            mapping: Custom key mapping (uses DEFAULT_MAPPING if None)
        """
        self.mapping = mapping or self.DEFAULT_MAPPING
        self.running = False
        self._read_thread = None

        # Initialize pygame if not already done
        if not pygame.get_init():
            pygame.init()

    def read_state(self) -> ControllerState:
        """
        Read current keyboard state and convert to controller state

        Returns:
            ControllerState representing current keyboard input
        """
        # Get all pressed keys
        keys = pygame.key.get_pressed()

        # Buttons
        button_a = keys[self.mapping['button_a']]
        button_b = keys[self.mapping['button_b']]
        button_x = keys[self.mapping['button_x']]
        button_y = keys[self.mapping['button_y']]
        button_lb = keys[self.mapping['button_lb']]
        button_rb = keys[self.mapping['button_rb']]
        button_back = keys[self.mapping['button_back']]
        button_start = keys[self.mapping['button_start']]
        button_lstick = keys[self.mapping['button_lstick']]
        button_rstick = keys[self.mapping['button_rstick']]

        # D-pad
        dpad_up = keys[self.mapping['dpad_up']]
        dpad_down = keys[self.mapping['dpad_down']]
        dpad_left = keys[self.mapping['dpad_left']]
        dpad_right = keys[self.mapping['dpad_right']]

        # Left stick (convert keys to analog values)
        lstick_x = 0
        lstick_y = 0

        if keys[self.mapping['lstick_left']]:
            lstick_x -= 32767
        if keys[self.mapping['lstick_right']]:
            lstick_x += 32767
        if keys[self.mapping['lstick_up']]:
            lstick_y += 32767
        if keys[self.mapping['lstick_down']]:
            lstick_y -= 32767

        # Right stick (convert keys to analog values)
        rstick_x = 0
        rstick_y = 0

        if keys[self.mapping['rstick_left']]:
            rstick_x -= 32767
        if keys[self.mapping['rstick_right']]:
            rstick_x += 32767
        if keys[self.mapping['rstick_up']]:
            rstick_y += 32767
        if keys[self.mapping['rstick_down']]:
            rstick_y -= 32767

        # Triggers (0 or max, no analog)
        trigger_l = 255 if keys[self.mapping['trigger_l']] else 0
        trigger_r = 255 if keys[self.mapping['trigger_r']] else 0

        return ControllerState(
            button_a=bool(button_a),
            button_b=bool(button_b),
            button_x=bool(button_x),
            button_y=bool(button_y),
            button_lb=bool(button_lb),
            button_rb=bool(button_rb),
            button_back=bool(button_back),
            button_start=bool(button_start),
            button_lstick=bool(button_lstick),
            button_rstick=bool(button_rstick),
            dpad_up=dpad_up,
            dpad_down=dpad_down,
            dpad_left=dpad_left,
            dpad_right=dpad_right,
            lstick_x=lstick_x,
            lstick_y=lstick_y,
            rstick_x=rstick_x,
            rstick_y=rstick_y,
            trigger_l=trigger_l,
            trigger_r=trigger_r
        )

    def start_reading(self, callback: Callable[[ControllerState], None], poll_rate: int = 120):
        """
        Start continuous keyboard reading in a separate thread

        Args:
            callback: Function called with ControllerState for each read
            poll_rate: Polling rate in Hz (default 120Hz for low latency)
        """
        if self.running:
            return

        self.running = True
        self._read_thread = threading.Thread(
            target=self._read_loop,
            args=(callback, poll_rate)
        )
        self._read_thread.daemon = True
        self._read_thread.start()

    def _read_loop(self, callback: Callable[[ControllerState], None], poll_rate: int):
        """Continuous reading loop"""
        poll_interval = 1.0 / poll_rate

        while self.running:
            start = time.perf_counter()

            # Process pygame events to update key state
            pygame.event.pump()

            state = self.read_state()
            callback(state)

            # Maintain poll rate
            elapsed = time.perf_counter() - start
            sleep_time = max(0, poll_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def stop_reading(self):
        """Stop continuous reading"""
        self.running = False
        if self._read_thread:
            self._read_thread.join(timeout=2.0)
            self._read_thread = None

    def get_mapping_description(self) -> str:
        """Get human-readable description of current mapping"""
        return f"""
Keyboard Mapping:
==================
Movement (Left Stick):
  W/A/S/D       - Up/Left/Down/Right

Camera (Right Stick):
  Arrow Keys    - Up/Left/Down/Right

Action Buttons:
  J             - A button (Jump/Accept)
  K             - B button (Back/Cancel)
  I             - X button (Left action)
  L             - Y button (Top action)

Triggers & Bumpers:
  Q             - Left Trigger
  E             - Right Trigger
  1             - Left Bumper
  2             - Right Bumper

D-Pad:
  Numpad 8/4/2/6 - Up/Left/Down/Right

Menu:
  Enter         - Start
  Backspace     - Back/Select

Stick Press:
  Left Shift    - Left Stick Press
  Right Shift   - Right Stick Press

Tip: Press ESC to disconnect
==================
        """

    def is_connected(self) -> bool:
        """Check if keyboard input is available (always True)"""
        return True

    def get_controller_name(self) -> str:
        """Get the name of the input device"""
        return "Keyboard"

    def __del__(self):
        """Cleanup"""
        self.stop_reading()


def print_keyboard_help():
    """Print keyboard mapping help"""
    mapper = KeyboardMapper()
    print(mapper.get_mapping_description())
