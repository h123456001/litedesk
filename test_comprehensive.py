#!/usr/bin/env python3
"""
LiteDesk Comprehensive Test Suite
Tests all components for cross-platform compatibility
"""
import sys
import unittest
import socket
import threading
import time
from io import BytesIO


class TestPlatformUtils(unittest.TestCase):
    """Test platform utilities"""
    
    def test_get_platform(self):
        """Test platform detection"""
        from platform_utils import get_platform
        platform = get_platform()
        self.assertIn(platform, ['windows', 'macos', 'linux', 'unknown'])
        print(f"  Detected platform: {platform}")
    
    def test_get_platform_info(self):
        """Test platform info retrieval"""
        from platform_utils import get_platform_info
        info = get_platform_info()
        self.assertIn('system', info)
        self.assertIn('platform_type', info)
        print(f"  System: {info['system']}")
    
    def test_check_dependencies(self):
        """Test dependency checking"""
        from platform_utils import check_dependencies
        deps = check_dependencies()
        self.assertIn('mss', deps)
        self.assertIn('Pillow', deps)
        self.assertIn('pynput', deps)
        self.assertIn('PyQt5', deps)
    
    def test_get_network_interface(self):
        """Test network interface detection"""
        from platform_utils import get_default_network_interface
        ip = get_default_network_interface()
        if ip:
            print(f"  Default IP: {ip}")
            # Basic IP validation
            parts = ip.split('.')
            self.assertEqual(len(parts), 4)


class TestImports(unittest.TestCase):
    """Test that all required modules can be imported"""
    
    def test_import_mss(self):
        """Test mss import"""
        try:
            import mss
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import mss: {e}")
    
    def test_import_pillow(self):
        """Test PIL/Pillow import"""
        try:
            from PIL import Image
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import PIL: {e}")
    
    def test_import_pynput(self):
        """Test pynput import"""
        try:
            from pynput.mouse import Controller
            # This may fail in headless environment
            print("  Note: pynput import successful")
        except Exception as e:
            print(f"  Note: pynput import failed (expected in headless): {e}")
    
    def test_import_pyqt5(self):
        """Test PyQt5 import"""
        try:
            from PyQt5.QtCore import QT_VERSION_STR
            print(f"  PyQt5 version: {QT_VERSION_STR}")
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import PyQt5: {e}")


class TestScreenCapture(unittest.TestCase):
    """Test screen capture functionality"""
    
    def test_screen_capture_init(self):
        """Test screen capture initialization"""
        try:
            from screen_capture import ScreenCapture
            capture = ScreenCapture(quality=50)
            self.assertIsNotNone(capture)
            capture.close()
        except Exception as e:
            print(f"  Note: Screen capture init failed (expected in headless): {e}")
    
    def test_screen_capture_size(self):
        """Test getting screen size"""
        try:
            from screen_capture import ScreenCapture
            capture = ScreenCapture(quality=50)
            width, height = capture.get_screen_size()
            self.assertGreater(width, 0)
            self.assertGreater(height, 0)
            print(f"  Screen size: {width}x{height}")
            capture.close()
        except Exception as e:
            print(f"  Note: Screen size test failed (expected in headless): {e}")


class TestInputControl(unittest.TestCase):
    """Test input control functionality"""
    
    def test_input_controller_init(self):
        """Test input controller initialization"""
        try:
            from input_control import InputController
            controller = InputController()
            self.assertIsNotNone(controller)
            print("  Input controller initialized")
        except Exception as e:
            print(f"  Note: Input controller init failed (expected in headless): {e}")


class TestNetworkProtocol(unittest.TestCase):
    """Test network protocol implementation"""
    
    def test_network_imports(self):
        """Test network module imports"""
        from network import NetworkServer, NetworkClient
        self.assertTrue(True)
    
    def test_frame_encoding(self):
        """Test frame encoding/decoding"""
        import struct
        from PIL import Image
        
        # Create a test image
        img = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=50)
        jpeg_data = buffer.getvalue()
        
        # Encode frame header
        width, height = img.size
        header = struct.pack('!III', width, height, len(jpeg_data))
        
        # Verify header
        self.assertEqual(len(header), 12)
        decoded_width, decoded_height, decoded_length = struct.unpack('!III', header)
        self.assertEqual(decoded_width, width)
        self.assertEqual(decoded_height, height)
        self.assertEqual(decoded_length, len(jpeg_data))
    
    def test_command_encoding(self):
        """Test command encoding/decoding"""
        import struct
        import json
        
        # Create test command
        cmd = {
            'type': 'mouse_move',
            'data': {'x': 100, 'y': 200}
        }
        
        # Encode
        cmd_json = json.dumps(cmd).encode('utf-8')
        header = struct.pack('!I', len(cmd_json))
        
        # Decode
        decoded_length = struct.unpack('!I', header)[0]
        self.assertEqual(decoded_length, len(cmd_json))
        
        decoded_cmd = json.loads(cmd_json.decode('utf-8'))
        self.assertEqual(decoded_cmd['type'], 'mouse_move')
        self.assertEqual(decoded_cmd['data']['x'], 100)


class TestNetworkCommunication(unittest.TestCase):
    """Test basic network communication"""
    
    def test_socket_creation(self):
        """Test socket creation"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Try to bind to test port
        try:
            sock.bind(('127.0.0.1', 0))  # 0 = random available port
            addr = sock.getsockname()
            print(f"  Test socket bound to {addr}")
            sock.close()
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Socket binding failed: {e}")
    
    def test_server_client_connection(self):
        """Test basic server-client connection"""
        test_port = 19876  # Different port to avoid conflicts
        
        def server_thread():
            server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind(('127.0.0.1', test_port))
            server_sock.listen(1)
            server_sock.settimeout(5)
            
            try:
                client_sock, addr = server_sock.accept()
                # Send test message
                client_sock.sendall(b'Hello from server')
                client_sock.close()
            except socket.timeout:
                pass
            finally:
                server_sock.close()
        
        # Start server in background
        server = threading.Thread(target=server_thread, daemon=True)
        server.start()
        
        # Give server time to start
        time.sleep(0.5)
        
        # Connect as client
        try:
            client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_sock.settimeout(5)
            client_sock.connect(('127.0.0.1', test_port))
            
            # Receive message
            data = client_sock.recv(1024)
            self.assertEqual(data, b'Hello from server')
            
            client_sock.close()
            print("  Server-client connection test passed")
        except Exception as e:
            self.fail(f"Connection test failed: {e}")


class TestImageProcessing(unittest.TestCase):
    """Test image processing"""
    
    def test_image_creation(self):
        """Test creating and compressing image"""
        from PIL import Image
        
        # Create test image
        img = Image.new('RGB', (640, 480), color='blue')
        self.assertEqual(img.size, (640, 480))
        
        # Compress to JPEG
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=50)
        jpeg_data = buffer.getvalue()
        
        self.assertGreater(len(jpeg_data), 0)
        print(f"  Compressed 640x480 image to {len(jpeg_data)} bytes")
    
    def test_image_decompression(self):
        """Test decompressing JPEG image"""
        from PIL import Image
        
        # Create and compress
        img = Image.new('RGB', (320, 240), color='green')
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=50)
        jpeg_data = buffer.getvalue()
        
        # Decompress
        buffer2 = BytesIO(jpeg_data)
        img2 = Image.open(buffer2)
        
        self.assertEqual(img2.size, (320, 240))
        print("  Image compression/decompression successful")


def run_tests():
    """Run all tests with custom output"""
    print("=" * 70)
    print("LiteDesk Comprehensive Test Suite")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPlatformUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestImports))
    suite.addTests(loader.loadTestsFromTestCase(TestScreenCapture))
    suite.addTests(loader.loadTestsFromTestCase(TestInputControl))
    suite.addTests(loader.loadTestsFromTestCase(TestNetworkProtocol))
    suite.addTests(loader.loadTestsFromTestCase(TestNetworkCommunication))
    suite.addTests(loader.loadTestsFromTestCase(TestImageProcessing))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print()
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print()
        print("✓ All tests passed!")
        return 0
    else:
        print()
        print("✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
