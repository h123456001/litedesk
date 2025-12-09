"""
LiteDesk - Simple Peer-to-Peer Remote Desktop

A lightweight remote desktop application inspired by RustDesk.
Supports screen sharing and remote control over TCP/IP.

Author: LiteDesk Contributors
License: MIT
"""

__version__ = "1.0.0"
__author__ = "LiteDesk Contributors"
__license__ = "MIT"

from .screen_capture import ScreenCapture
from .input_control import InputController
from .network import NetworkServer, NetworkClient

__all__ = [
    'ScreenCapture',
    'InputController', 
    'NetworkServer',
    'NetworkClient',
]
