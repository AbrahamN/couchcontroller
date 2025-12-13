"""Virtual controller management using ViGEmBus (Windows)"""

import logging
from typing import Dict, Optional
import vgamepad as vg
from ..common.protocol import ControllerState


logger = logging.getLogger(__name__)


class VirtualXboxController:
    """
    Wrapper for virtual Xbox 360 controller using ViGEmBus
    Translates ControllerState to vgamepad API calls
    """

    def __init__(self, controller_id: int):
        """
        Initialize virtual controller

        Args:
            controller_id: Unique ID for this controller instance
        """
        self.controller_id = controller_id
        self.gamepad = vg.VX360Gamepad()
        logger.info(f"Virtual Xbox controller {controller_id} created")

    def update_state(self, state: ControllerState):
        """
        Update virtual controller state

        Args:
            state: Controller state from network client
        """
        # Buttons
        if state.button_a:
            self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        else:
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)

        if state.button_b:
            self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
        else:
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_B)

        if state.button_x:
            self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
        else:
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_X)

        if state.button_y:
            self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
        else:
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)

        if state.button_lb:
            self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
        else:
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)

        if state.button_rb:
            self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
        else:
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)

        if state.button_back:
            self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK)
        else:
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK)

        if state.button_start:
            self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
        else:
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_START)

        if state.button_lstick:
            self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
        else:
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)

        if state.button_rstick:
            self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB)
        else:
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB)

        # D-pad
        if state.dpad_up:
            self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
        else:
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)

        if state.dpad_down:
            self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
        else:
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)

        if state.dpad_left:
            self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
        else:
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)

        if state.dpad_right:
            self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
        else:
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)

        # Analog sticks (normalize from -32768..32767 to -1.0..1.0)
        self.gamepad.left_joystick_float(
            x_value_float=state.lstick_x / 32767.0,
            y_value_float=state.lstick_y / 32767.0
        )
        self.gamepad.right_joystick_float(
            x_value_float=state.rstick_x / 32767.0,
            y_value_float=state.rstick_y / 32767.0
        )

        # Triggers (normalize from 0..255 to 0.0..1.0)
        self.gamepad.left_trigger_float(state.trigger_l / 255.0)
        self.gamepad.right_trigger_float(state.trigger_r / 255.0)

        # Update the virtual controller
        self.gamepad.update()

    def reset(self):
        """Reset controller to neutral state"""
        self.gamepad.reset()
        self.gamepad.update()

    def disconnect(self):
        """Disconnect virtual controller"""
        logger.info(f"Virtual Xbox controller {self.controller_id} disconnecting")
        self.reset()


class VirtualControllerManager:
    """
    Manages multiple virtual controllers for connected clients
    """

    def __init__(self, max_controllers: int = 4):
        """
        Initialize manager

        Args:
            max_controllers: Maximum number of simultaneous controllers
        """
        self.max_controllers = max_controllers
        self.controllers: Dict[int, VirtualXboxController] = {}
        self.next_slot = 0

    def assign_controller(self, client_id: str) -> Optional[int]:
        """
        Assign a virtual controller slot to a client

        Args:
            client_id: Unique client identifier

        Returns:
            Controller slot number (0-3), or None if no slots available
        """
        if len(self.controllers) >= self.max_controllers:
            logger.warning(f"Cannot assign controller to {client_id}: all slots full")
            return None

        # Find next available slot
        slot = self.next_slot
        while slot in self.controllers and slot < self.max_controllers:
            slot += 1

        if slot >= self.max_controllers:
            logger.warning(f"Cannot assign controller to {client_id}: all slots full")
            return None

        # Create virtual controller
        try:
            controller = VirtualXboxController(slot)
            self.controllers[slot] = controller
            self.next_slot = slot + 1
            logger.info(f"Assigned controller slot {slot} to client {client_id}")
            return slot
        except Exception as e:
            logger.error(f"Failed to create virtual controller: {e}")
            return None

    def update_controller(self, slot: int, state: ControllerState):
        """
        Update a controller's state

        Args:
            slot: Controller slot number
            state: New controller state
        """
        if slot not in self.controllers:
            logger.warning(f"Attempted to update non-existent controller slot {slot}")
            return

        self.controllers[slot].update_state(state)

    def remove_controller(self, slot: int):
        """
        Remove a virtual controller

        Args:
            slot: Controller slot to remove
        """
        if slot in self.controllers:
            self.controllers[slot].disconnect()
            del self.controllers[slot]
            logger.info(f"Removed controller slot {slot}")

            # Update next_slot if we removed an earlier slot
            if slot < self.next_slot:
                self.next_slot = slot

    def reset_all(self):
        """Reset all controllers to neutral state"""
        for controller in self.controllers.values():
            controller.reset()

    def disconnect_all(self):
        """Disconnect all virtual controllers"""
        for slot in list(self.controllers.keys()):
            self.remove_controller(slot)

    def get_available_slots(self) -> int:
        """Get number of available controller slots"""
        return self.max_controllers - len(self.controllers)

    def __del__(self):
        """Cleanup"""
        self.disconnect_all()
