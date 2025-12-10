"""
LiteDesk - Input Control Module

Handles remote mouse and keyboard control.
"""
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key


class InputController:
    """Handles remote input control (mouse and keyboard)"""
    
    def __init__(self):
        """Initialize input controllers"""
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
    
    def move_mouse(self, x, y):
        """Move mouse to absolute position"""
        self.mouse.position = (x, y)
    
    def click_mouse(self, button='left', press=True):
        """
        Perform mouse click
        
        Args:
            button: 'left', 'right', or 'middle'
            press: True for press, False for release
        """
        btn = {
            'left': Button.left,
            'right': Button.right,
            'middle': Button.middle
        }.get(button, Button.left)
        
        if press:
            self.mouse.press(btn)
        else:
            self.mouse.release(btn)
    
    def scroll_mouse(self, dx, dy):
        """Scroll mouse wheel"""
        self.mouse.scroll(dx, dy)
    
    def press_key(self, key):
        """Press a keyboard key"""
        try:
            # Try as a regular character
            self.keyboard.press(key)
            self.keyboard.release(key)
        except (ValueError, AttributeError) as e:
            # Try as a special key
            try:
                special_key = getattr(Key, key.lower())
                self.keyboard.press(special_key)
                self.keyboard.release(special_key)
            except (AttributeError, ValueError) as e2:
                print(f"Warning: Could not press key '{key}': {e2}")
    
    def type_text(self, text):
        """Type a string of text"""
        self.keyboard.type(text)
