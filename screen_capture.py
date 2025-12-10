"""
LiteDesk - Simple Peer-to-Peer Remote Desktop
Inspired by RustDesk architecture

This module handles screen capture functionality.
"""
import mss
import io
from PIL import Image


class ScreenCapture:
    """Handles screen capture operations"""
    
    def __init__(self, monitor_number=1, quality=50):
        """
        Initialize screen capture
        
        Args:
            monitor_number: Monitor to capture (1 for primary)
            quality: JPEG quality (1-100, lower = smaller size)
        """
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[monitor_number]
        self.quality = quality
    
    def capture_screen(self):
        """
        Capture screen and return as compressed JPEG bytes
        
        Returns:
            tuple: (width, height, jpeg_bytes)
        """
        # Capture screen
        screenshot = self.sct.grab(self.monitor)
        
        # Convert to PIL Image
        img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
        
        # Compress to JPEG
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=self.quality, optimize=True)
        jpeg_bytes = buffer.getvalue()
        
        return (screenshot.size[0], screenshot.size[1], jpeg_bytes)
    
    def get_screen_size(self):
        """Get screen dimensions"""
        return (self.monitor['width'], self.monitor['height'])
    
    def close(self):
        """Clean up resources"""
        self.sct.close()
