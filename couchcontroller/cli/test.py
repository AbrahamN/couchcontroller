#!/usr/bin/env python3
"""
Component Test Script

Tests individual CouchController components to verify installation.
"""

import sys
import time


def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")

    try:
        import mss
        print("  ✓ mss")
    except ImportError as e:
        print(f"  ✗ mss - {e}")
        return False

    try:
        import av
        print("  ✓ av (PyAV)")
    except ImportError as e:
        print(f"  ✗ av - {e}")
        return False

    try:
        import pygame
        print("  ✓ pygame")
    except ImportError as e:
        print(f"  ✗ pygame - {e}")
        return False

    try:
        import numpy
        print("  ✓ numpy")
    except ImportError as e:
        print(f"  ✗ numpy - {e}")
        return False

    try:
        import vgamepad
        print("  ✓ vgamepad")
    except ImportError as e:
        print(f"  ✗ vgamepad - {e}")
        print("    Note: vgamepad only needed on host machine")

    print()
    return True


def test_screen_capture():
    """Test screen capture"""
    print("Testing screen capture...")

    try:
        import mss
        import numpy as np

        sct = mss.mss()
        monitor = sct.monitors[1]  # Primary monitor

        print(f"  Primary monitor: {monitor['width']}x{monitor['height']}")

        # Capture a frame
        screenshot = sct.grab(monitor)
        frame = np.array(screenshot)

        print(f"  ✓ Captured frame: {frame.shape}")
        sct.close()

    except Exception as e:
        print(f"  ✗ Screen capture failed: {e}")
        return False

    print()
    return True


def test_video_encoding():
    """Test video encoding"""
    print("Testing video encoding...")

    try:
        import av
        import numpy as np

        # Create a test frame
        width, height = 640, 480
        test_frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)

        # Create encoder
        output = av.open('pipe:', mode='w', format='h264')
        stream = output.add_stream('h264', rate=30)
        stream.width = width
        stream.height = height
        stream.pix_fmt = 'yuv420p'

        # Encode a frame
        av_frame = av.VideoFrame.from_ndarray(test_frame, format='rgb24')
        av_frame.pts = 0

        packets = stream.encode(av_frame)
        output.close()

        print(f"  ✓ Encoded test frame ({len(packets)} packets)")

    except Exception as e:
        print(f"  ✗ Video encoding failed: {e}")
        return False

    print()
    return True


def test_controller():
    """Test controller detection"""
    print("Testing controller detection...")

    try:
        import pygame

        pygame.init()
        pygame.joystick.init()

        joystick_count = pygame.joystick.get_count()

        if joystick_count == 0:
            print("  ⚠ No controllers detected")
            print("    Connect a controller to test input capture")
        else:
            print(f"  ✓ Found {joystick_count} controller(s):")
            for i in range(joystick_count):
                joy = pygame.joystick.Joystick(i)
                joy.init()
                print(f"    [{i}] {joy.get_name()}")
                print(f"        Axes: {joy.get_numaxes()}, Buttons: {joy.get_numbuttons()}")
                joy.quit()

        pygame.quit()

    except Exception as e:
        print(f"  ✗ Controller detection failed: {e}")
        return False

    print()
    return True


def test_virtual_controller():
    """Test virtual controller creation (host only)"""
    print("Testing virtual controller (ViGEmBus)...")

    try:
        import vgamepad as vg

        # Try to create a virtual controller
        gamepad = vg.VX360Gamepad()
        print("  ✓ Created virtual Xbox 360 controller")

        # Test basic operation
        gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gamepad.update()
        time.sleep(0.1)
        gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gamepad.update()

        print("  ✓ Virtual controller responds to commands")

        # Clean up
        gamepad.reset()

    except ImportError:
        print("  ⚠ vgamepad not installed (only needed on host)")
        return True
    except Exception as e:
        print(f"  ✗ Virtual controller failed: {e}")
        print("    Make sure ViGEmBus driver is installed:")
        print("    https://github.com/ViGEm/ViGEmBus/releases")
        return False

    print()
    return True


def test_network():
    """Test basic network functionality"""
    print("Testing network...")

    try:
        import socket

        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()

        print(f"  ✓ Local IP: {local_ip}")

        # Test UDP socket creation
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_socket.bind(('0.0.0.0', 0))  # Bind to random port
        port = test_socket.getsockname()[1]
        print(f"  ✓ Created UDP socket on port {port}")
        test_socket.close()

    except Exception as e:
        print(f"  ✗ Network test failed: {e}")
        return False

    print()
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("CouchController Component Test")
    print("=" * 60)
    print()

    tests = [
        ("Imports", test_imports),
        ("Screen Capture", test_screen_capture),
        ("Video Encoding", test_video_encoding),
        ("Controller Detection", test_controller),
        ("Virtual Controller", test_virtual_controller),
        ("Network", test_network),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"Test '{name}' crashed: {e}")
            results.append((name, False))

    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    print()
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print()
        print("All tests passed! You're ready to use CouchController.")
        print()
        print("Next steps:")
        print("  1. On host: python host.py")
        print("  2. On client: python client.py --host <HOST_IP>")
        return 0
    else:
        print()
        print("Some tests failed. Please install missing dependencies:")
        print("  pip install -r requirements.txt")
        print()
        print("For virtual controller support (host only):")
        print("  1. pip install vgamepad")
        print("  2. Install ViGEmBus: https://github.com/ViGEm/ViGEmBus/releases")
        return 1


if __name__ == '__main__':
    sys.exit(main())
