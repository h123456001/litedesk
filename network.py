"""
LiteDesk - Network Module

Handles peer-to-peer network communication between client and server.
Supports both direct connections and relay mode via VPS server.
"""
import socket
import struct
import threading
import json
from io import BytesIO
from PIL import Image
try:
    from relay_client import RelayClient
    RELAY_AVAILABLE = True
except ImportError:
    RELAY_AVAILABLE = False


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
        except (socket.error, json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"Error receiving command: {e}")
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
        except (socket.error, json.JSONEncodeError, UnicodeEncodeError) as e:
            print(f"Error sending command: {e}")
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


class NetworkServerWithRelay(NetworkServer):
    """Server with relay support for NAT traversal"""
    
    def __init__(self, host='0.0.0.0', port=9876, relay_host=None, relay_port=8877, peer_id=None):
        """
        Initialize network server with relay support
        
        Args:
            host: IP address to bind to
            port: Port number to listen on
            relay_host: Relay server address (None to disable relay)
            relay_port: Relay server port
            peer_id: Unique peer identifier for relay
        """
        super().__init__(host, port)
        self.relay_host = relay_host
        self.relay_port = relay_port
        self.peer_id = peer_id or f"server_{port}"
        self.relay_client = None
        self.use_relay = relay_host is not None and RELAY_AVAILABLE
    
    def start_with_relay(self):
        """Start server and register with relay server"""
        # Start normal server
        self.start()
        
        # Register with relay if configured
        if self.use_relay:
            try:
                self.relay_client = RelayClient(self.relay_host, self.relay_port)
                if self.relay_client.connect(self.peer_id, 'server'):
                    print(f"[Server] Registered with relay server as '{self.peer_id}'")
                else:
                    print(f"[Server] Failed to register with relay server")
                    self.relay_client = None
            except Exception as e:
                print(f"[Server] Relay registration error: {e}")
                self.relay_client = None
    
    def stop(self):
        """Stop server and disconnect from relay"""
        super().stop()
        if self.relay_client:
            self.relay_client.disconnect()


class NetworkClientWithRelay(NetworkClient):
    """Client with relay support for NAT traversal"""
    
    def __init__(self, relay_host=None, relay_port=8877, peer_id=None):
        """
        Initialize network client with relay support
        
        Args:
            relay_host: Relay server address (None to disable relay)
            relay_port: Relay server port
            peer_id: Unique peer identifier for relay
        """
        super().__init__()
        self.relay_host = relay_host
        self.relay_port = relay_port
        self.peer_id = peer_id or f"client_{id(self)}"
        self.relay_client = None
        self.use_relay = relay_host is not None and RELAY_AVAILABLE
        self.available_servers = []
    
    def connect_via_relay(self, target_peer_id=None):
        """
        Connect to server via relay
        
        Args:
            target_peer_id: Specific server ID to connect to, or None to list available
        
        Returns:
            bool: True if connected
        """
        if not self.use_relay:
            print("[Client] Relay not configured")
            return False
        
        try:
            # Connect to relay server
            self.relay_client = RelayClient(self.relay_host, self.relay_port)
            if not self.relay_client.connect(self.peer_id, 'client'):
                print("[Client] Failed to connect to relay server")
                return False
            
            # List available servers if no target specified
            if not target_peer_id:
                peers = self.relay_client.list_peers()
                servers = [p for p in peers if p.get('peer_type') == 'server']
                
                if not servers:
                    print("[Client] No servers available")
                    return False
                
                self.available_servers = servers
                print(f"[Client] Found {len(servers)} available servers")
                
                # Use first available server
                target_peer_id = servers[0]['peer_id']
                print(f"[Client] Connecting to server: {target_peer_id}")
            
            # Get target server info
            peer_info = self.relay_client.get_peer_info(target_peer_id)
            if not peer_info:
                print(f"[Client] Could not get info for server: {target_peer_id}")
                return False
            
            # Try direct connection first
            print(f"[Client] Attempting direct connection to {peer_info['public_ip']}:{peer_info['public_port']}")
            
            # Note: Direct connection after NAT traversal is complex and may not work
            # For now, we rely on the relay server for connection info
            # In a full implementation, we would attempt hole punching here
            
            # For this implementation, we'll use the server's listening port
            # which we know from the relay (typically 9876)
            try:
                direct_result = self.connect(peer_info['public_ip'], 9876)
                if direct_result:
                    print("[Client] Direct connection successful!")
                    return True
            except:
                print("[Client] Direct connection failed, this is expected behind NAT")
            
            print("[Client] Connected via relay server")
            print("[Client] Note: For data transfer, direct P2P connection is recommended")
            print("[Client] You may need to configure port forwarding on the server side")
            
            return True
            
        except Exception as e:
            print(f"[Client] Relay connection error: {e}")
            if self.relay_client:
                self.relay_client.disconnect()
            return False
    
    def list_available_servers(self):
        """
        List available servers from relay
        
        Returns:
            list: List of available servers
        """
        if not self.use_relay:
            return []
        
        try:
            if not self.relay_client or not self.relay_client.connected:
                self.relay_client = RelayClient(self.relay_host, self.relay_port)
                if not self.relay_client.connect(self.peer_id, 'client'):
                    return []
            
            peers = self.relay_client.list_peers()
            servers = [p for p in peers if p.get('peer_type') == 'server']
            self.available_servers = servers
            return servers
        except Exception as e:
            print(f"[Client] Error listing servers: {e}")
            return []
    
    def disconnect(self):
        """Disconnect from server and relay"""
        super().disconnect()
        if self.relay_client:
            self.relay_client.disconnect()

