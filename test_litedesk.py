#!/usr/bin/env python3
"""
Simple test script to verify LiteDesk components
"""
import sys
import time

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import mss
        print("✓ mss imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import mss: {e}")
        return False
    
    try:
        from PIL import Image
        print("✓ PIL/Pillow imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PIL: {e}")
        return False
    
    try:
        from pynput.mouse import Controller
        from pynput.keyboard import Controller as KeyboardController
        print("✓ pynput imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import pynput: {e}")
        return False
    
    try:
        from PyQt5.QtWidgets import QApplication
        print("✓ PyQt5 imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PyQt5: {e}")
        return False
    
    return True


def test_screen_capture():
    """Test screen capture functionality"""
    print("\nTesting screen capture...")
    try:
        from screen_capture import ScreenCapture
        
        capture = ScreenCapture(quality=50)
        width, height, jpeg_data = capture.capture_screen()
        
        print(f"✓ Screen captured: {width}x{height}, {len(jpeg_data)} bytes")
        capture.close()
        return True
    except Exception as e:
        print(f"✗ Screen capture failed: {e}")
        return False


def test_input_control():
    """Test input control (minimal test)"""
    print("\nTesting input control...")
    try:
        from input_control import InputController
        
        controller = InputController()
        print("✓ Input controller initialized")
        return True
    except Exception as e:
        print(f"✗ Input control failed: {e}")
        return False


def test_network_modules():
    """Test network module imports"""
    print("\nTesting network modules...")
    try:
        from network import NetworkServer, NetworkClient
        print("✓ Network modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Network modules failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("LiteDesk Component Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_screen_capture,
        test_input_control,
        test_network_modules,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 50)
    
    if all(results):
        print("\n✓ All tests passed! LiteDesk is ready to use.")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
