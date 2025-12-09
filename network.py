"""
LiteDesk - Network Module

Handles peer-to-peer network communication between client and server.
"""
import socket
import struct
import threading
import json
from io import BytesIO
from PIL import Image


class NetworkServer:
    """Server side - hosts the desktop for sharing"""
    
    def __init__(self, host='0.0.0.0', port=9876):
        """
        Initialize network server
        
        Args:
            host: IP address to bind to
            port: Port number to listen on
        """
        self.host = host
        self.port = port
        self.socket = None
        self.client_socket = None
        self.running = False
    
    def start(self):
        """Start the server and listen for connections"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        self.running = True
        print(f"Server listening on {self.host}:{self.port}")
    
    def accept_connection(self):
        """Wait for and accept a client connection"""
        if self.socket:
            self.client_socket, addr = self.socket.accept()
            print(f"Client connected from {addr}")
            return True
        return False
    
    def send_frame(self, width, height, jpeg_data):
        """
        Send a screen frame to the client
        
        Args:
            width: Frame width
            height: Frame height
            jpeg_data: JPEG compressed image data
        """
        if not self.client_socket:
            return False
        
        try:
            # Send frame header: width (4 bytes), height (4 bytes), data length (4 bytes)
            header = struct.pack('!III', width, height, len(jpeg_data))
            self.client_socket.sendall(header)
            
            # Send frame data
            self.client_socket.sendall(jpeg_data)
            return True
        except (BrokenPipeError, ConnectionResetError):
            print("Client disconnected")
            self.client_socket = None
            return False
    
    def receive_command(self):
        """
        Receive a command from the client
        
        Returns:
            dict: Command data or None if connection lost
        """
        if not self.client_socket:
            return None
        
        try:
            # Receive command length (4 bytes)
            length_data = self._recv_exact(4)
            if not length_data:
                return None
            
            length = struct.unpack('!I', length_data)[0]
            
            # Receive command data
            cmd_data = self._recv_exact(length)
            if not cmd_data:
                return None
            
            # Parse JSON command
            return json.loads(cmd_data.decode('utf-8'))
        except:
            return None
    
    def _recv_exact(self, size):
        """Receive exact number of bytes"""
        data = b''
        while len(data) < size:
            packet = self.client_socket.recv(size - len(data))
            if not packet:
                return None
            data += packet
        return data
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        if self.socket:
            self.socket.close()


class NetworkClient:
    """Client side - connects to remote desktop"""
    
    def __init__(self):
        """Initialize network client"""
        self.socket = None
        self.connected = False
    
    def connect(self, host, port=9876):
        """
        Connect to a remote server
        
        Args:
            host: Server IP address
            port: Server port number
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True
            print(f"Connected to {host}:{port}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def receive_frame(self):
        """
        Receive a screen frame from the server
        
        Returns:
            PIL.Image: Screen frame or None if connection lost
        """
        if not self.connected:
            return None
        
        try:
            # Receive frame header
            header = self._recv_exact(12)
            if not header:
                self.connected = False
                return None
            
            width, height, data_length = struct.unpack('!III', header)
            
            # Receive frame data
            jpeg_data = self._recv_exact(data_length)
            if not jpeg_data:
                self.connected = False
                return None
            
            # Decode JPEG image
            img = Image.open(BytesIO(jpeg_data))
            return img
        except Exception as e:
            print(f"Error receiving frame: {e}")
            self.connected = False
            return None
    
    def send_command(self, command_type, data):
        """
        Send a command to the server
        
        Args:
            command_type: Type of command (e.g., 'mouse', 'keyboard')
            data: Command data dictionary
        """
        if not self.connected:
            return False
        
        try:
            # Create command
            cmd = {'type': command_type, 'data': data}
            cmd_json = json.dumps(cmd).encode('utf-8')
            
            # Send command length and data
            length = struct.pack('!I', len(cmd_json))
            self.socket.sendall(length + cmd_json)
            return True
        except:
            self.connected = False
            return False
    
    def _recv_exact(self, size):
        """Receive exact number of bytes"""
        data = b''
        while len(data) < size:
            packet = self.socket.recv(size - len(data))
            if not packet:
                return None
            data += packet
        return data
    
    def disconnect(self):
        """Disconnect from server"""
        self.connected = False
        if self.socket:
            self.socket.close()
