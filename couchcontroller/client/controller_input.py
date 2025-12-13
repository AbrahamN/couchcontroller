"""Controller input capture using pygame"""

import logging
import pygame
from typing import Optional, Callable
import threading
import time
from ..common.protocol import ControllerState


logger = logging.getLogger(__name__)


class ControllerReader:
    """
    Read controller input using pygame
    Maps various controller types to Xbox 360 layout
    """

    def __init__(self, controller_index: int = 0):
        """
        Initialize controller reader

        Args:
            controller_index: Index of controller to use (0 for first controller)
        """
        pygame.init()
        pygame.joystick.init()

        self.controller_index = controller_index
        self.joystick: Optional[pygame.joystick.Joystick] = None
        self.running = False
        self._read_thread = None

        # Deadzone for analog sticks
        self.deadzone = 0.1

        # Initialize controller
        self._init_controller()

    def _init_controller(self):
        """Initialize the controller"""
        joystick_count = pygame.joystick.get_count()

        if joystick_count == 0:
            logger.error("No controllers found!")
            return

        if self.controller_index >= joystick_count:
            logger.error(f"Controller index {self.controller_index} out of range (found {joystick_count} controllers)")
            return

        self.joystick = pygame.joystick.Joystick(self.controller_index)
        self.joystick.init()

        logger.info(f"Controller connected: {self.joystick.get_name()}")
        logger.info(f"  Axes: {self.joystick.get_numaxes()}")
        logger.info(f"  Buttons: {self.joystick.get_numbuttons()}")
        logger.info(f"  Hats: {self.joystick.get_numhats()}")

    def read_state(self) -> Optional[ControllerState]:
        """
        Read current controller state

        Returns:
            ControllerState or None if controller not available
        """
        if not self.joystick:
            return None

        # Process pygame events to update controller state
        pygame.event.pump()

        # Read buttons (mapping may vary by controller, this assumes Xbox layout)
        button_a = self.joystick.get_button(0) if self.joystick.get_numbuttons() > 0 else False
        button_b = self.joystick.get_button(1) if self.joystick.get_numbuttons() > 1 else False
        button_x = self.joystick.get_button(2) if self.joystick.get_numbuttons() > 2 else False
        button_y = self.joystick.get_button(3) if self.joystick.get_numbuttons() > 3 else False
        button_lb = self.joystick.get_button(4) if self.joystick.get_numbuttons() > 4 else False
        button_rb = self.joystick.get_button(5) if self.joystick.get_numbuttons() > 5 else False
        button_back = self.joystick.get_button(6) if self.joystick.get_numbuttons() > 6 else False
        button_start = self.joystick.get_button(7) if self.joystick.get_numbuttons() > 7 else False
        button_lstick = self.joystick.get_button(8) if self.joystick.get_numbuttons() > 8 else False
        button_rstick = self.joystick.get_button(9) if self.joystick.get_numbuttons() > 9 else False

        # Read D-pad (usually hat 0)
        dpad_up = False
        dpad_down = False
        dpad_left = False
        dpad_right = False

        if self.joystick.get_numhats() > 0:
            hat = self.joystick.get_hat(0)
            dpad_right = hat[0] > 0
            dpad_left = hat[0] < 0
            dpad_up = hat[1] > 0
            dpad_down = hat[1] < 0

        # Read analog sticks (axes 0-3 typically)
        lstick_x = 0
        lstick_y = 0
        rstick_x = 0
        rstick_y = 0

        if self.joystick.get_numaxes() >= 4:
            # Left stick
            lstick_x_raw = self.joystick.get_axis(0)
            lstick_y_raw = -self.joystick.get_axis(1)  # Invert Y axis

            # Apply deadzone
            lstick_x = lstick_x_raw if abs(lstick_x_raw) > self.deadzone else 0.0
            lstick_y = lstick_y_raw if abs(lstick_y_raw) > self.deadzone else 0.0

            # Right stick
            rstick_x_raw = self.joystick.get_axis(2)
            rstick_y_raw = -self.joystick.get_axis(3)  # Invert Y axis

            # Apply deadzone
            rstick_x = rstick_x_raw if abs(rstick_x_raw) > self.deadzone else 0.0
            rstick_y = rstick_y_raw if abs(rstick_y_raw) > self.deadzone else 0.0

        # Convert to int16 range (-32768 to 32767)
        lstick_x_int = int(lstick_x * 32767)
        lstick_y_int = int(lstick_y * 32767)
        rstick_x_int = int(rstick_x * 32767)
        rstick_y_int = int(rstick_y * 32767)

        # Read triggers (axes 4-5 typically, or buttons on some controllers)
        trigger_l = 0
        trigger_r = 0

        if self.joystick.get_numaxes() >= 6:
            # Triggers as axes (0.0 to 1.0, or -1.0 to 1.0)
            trigger_l_raw = self.joystick.get_axis(4)
            trigger_r_raw = self.joystick.get_axis(5)

            # Normalize to 0-255 (handle both -1..1 and 0..1 ranges)
            trigger_l = int((trigger_l_raw + 1) * 127.5) if trigger_l_raw < 0 else int(trigger_l_raw * 255)
            trigger_r = int((trigger_r_raw + 1) * 127.5) if trigger_r_raw < 0 else int(trigger_r_raw * 255)
        else:
            # Fallback: check if triggers are mapped to buttons
            # (some controllers report triggers as buttons 10, 11)
            if self.joystick.get_numbuttons() > 10:
                trigger_l = 255 if self.joystick.get_button(10) else 0
            if self.joystick.get_numbuttons() > 11:
                trigger_r = 255 if self.joystick.get_button(11) else 0

        # Clamp trigger values
        trigger_l = max(0, min(255, trigger_l))
        trigger_r = max(0, min(255, trigger_r))

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
            lstick_x=lstick_x_int,
            lstick_y=lstick_y_int,
            rstick_x=rstick_x_int,
            rstick_y=rstick_y_int,
            trigger_l=trigger_l,
            trigger_r=trigger_r
        )

    def start_reading(self, callback: Callable[[ControllerState], None], poll_rate: int = 120):
        """
        Start continuous controller reading in a separate thread

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

            state = self.read_state()
            if state:
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

    def get_controller_name(self) -> str:
        """Get the name of the connected controller"""
        if self.joystick:
            return self.joystick.get_name()
        return "No controller"

    def is_connected(self) -> bool:
        """Check if controller is connected"""
        return self.joystick is not None

    def __del__(self):
        """Cleanup"""
        self.stop_reading()
        if self.joystick:
            self.joystick.quit()
        pygame.quit()
