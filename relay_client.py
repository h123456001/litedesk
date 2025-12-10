"""
LiteDesk - Relay Client Module

Provides relay server connectivity for NAT traversal.
"""
import socket
import struct
import json
import threading
import time


class RelayClient:
    """Client for connecting to relay server"""
    
    def __init__(self, relay_host, relay_port=8877):
        """
        Initialize relay client
        
        Args:
            relay_host: Relay server address
            relay_port: Relay server port
        """
        self.relay_host = relay_host
        self.relay_port = relay_port
        self.socket = None
        self.connected = False
        self.peer_id = None
        self.peer_type = None
        self.public_ip = None
        self.public_port = None
        self.callbacks = {}
        self.running = False
    
    def connect(self, peer_id, peer_type):
        """
        Connect to relay server and register
        
        Args:
            peer_id: Unique identifier for this peer
            peer_type: 'server' or 'client'
        
        Returns:
            bool: True if connected and registered
        """
        try:
            self.peer_id = peer_id
            self.peer_type = peer_type
            
            # Connect to relay server
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.relay_host, self.relay_port))
            self.connected = True
            
            print(f"[Relay Client] Connected to relay server {self.relay_host}:{self.relay_port}")
            
            # Register with relay server
            self.send_message({
                'type': 'register',
                'peer_id': peer_id,
                'peer_type': peer_type
            })
            
            # Wait for registration confirmation
            msg = self.recv_message()
            if msg and msg.get('type') == 'registered':
                self.public_ip = msg.get('public_ip')
                self.public_port = msg.get('public_port')
                print(f"[Relay Client] Registered as '{peer_id}' (public: {self.public_ip}:{self.public_port})")
                
                # Start message handler thread
                self.running = True
                threading.Thread(target=self._message_handler, daemon=True).start()
                
                return True
            else:
                print(f"[Relay Client] Registration failed")
                self.connected = False
                return False
        
        except Exception as e:
            print(f"[Relay Client] Connection failed: {e}")
            self.connected = False
            return False
    
    def list_peers(self):
        """
        Get list of available peers from relay server
        
        Returns:
            list: List of peer dictionaries
        """
        if not self.connected:
            return []
        
        try:
            self.send_message({'type': 'list_peers'})
            
            # Wait for response
            msg = self.recv_message(timeout=5)
            if msg and msg.get('type') == 'peer_list':
                return msg.get('peers', [])
        except Exception as e:
            print(f"[Relay Client] Error listing peers: {e}")
        
        return []
    
    def get_peer_info(self, target_peer_id):
        """
        Get connection info for a specific peer
        
        Args:
            target_peer_id: ID of target peer
        
        Returns:
            dict: Peer info or None
        """
        if not self.connected:
            return None
        
        try:
            self.send_message({
                'type': 'get_peer_info',
                'target_id': target_peer_id
            })
            
            # Wait for response
            msg = self.recv_message(timeout=10)
            if msg and msg.get('type') == 'peer_info':
                return {
                    'peer_id': msg.get('peer_id'),
                    'peer_type': msg.get('peer_type'),
                    'public_ip': msg.get('public_ip'),
                    'public_port': msg.get('public_port')
                }
        except Exception as e:
            print(f"[Relay Client] Error getting peer info: {e}")
        
        return None
    
    def relay_data(self, target_peer_id, data):
        """
        Relay data to another peer through server
        
        Args:
            target_peer_id: Target peer ID
            data: Data to relay (must be JSON serializable)
        """
        if not self.connected:
            return False
        
        try:
            self.send_message({
                'type': 'relay_data',
                'target_id': target_peer_id,
                'data': data
            })
            return True
        except Exception as e:
            print(f"[Relay Client] Error relaying data: {e}")
            return False
    
    def set_callback(self, event_type, callback):
        """
        Set callback for relay events
        
        Args:
            event_type: 'connection_request' or 'relayed_data'
            callback: Function to call with message data
        """
        self.callbacks[event_type] = callback
    
    def _message_handler(self):
        """Handle incoming messages from relay server"""
        while self.running and self.connected:
            try:
                msg = self.recv_message(timeout=1)
                if not msg:
                    continue
                
                msg_type = msg.get('type')
                
                if msg_type == 'connection_request':
                    # Another peer wants to connect
                    callback = self.callbacks.get('connection_request')
                    if callback:
                        callback(msg)
                
                elif msg_type == 'relayed_data':
                    # Received relayed data
                    callback = self.callbacks.get('relayed_data')
                    if callback:
                        callback(msg)
                
                elif msg_type == 'ping':
                    # Respond to ping
                    self.send_message({'type': 'heartbeat'})
                
                elif msg_type == 'heartbeat_ack':
                    # Heartbeat acknowledged
                    pass
                
            except Exception as e:
                if self.running:
                    print(f"[Relay Client] Message handler error: {e}")
                break
    
    def send_message(self, msg):
        """Send a JSON message to relay server"""
        try:
            msg_json = json.dumps(msg).encode('utf-8')
            length = struct.pack('!I', len(msg_json))
            self.socket.sendall(length + msg_json)
        except Exception as e:
            self.connected = False
            raise
    
    def recv_message(self, timeout=None):
        """Receive a JSON message from relay server"""
        if timeout:
            self.socket.settimeout(timeout)
        else:
            self.socket.settimeout(None)
        
        try:
            # Receive message length
            length_data = self._recv_exact(4)
            if not length_data:
                return None
            
            length = struct.unpack('!I', length_data)[0]
            
            # Receive message data
            msg_data = self._recv_exact(length)
            if not msg_data:
                return None
            
            return json.loads(msg_data.decode('utf-8'))
        except socket.timeout:
            return None
        except:
            return None
    
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
        """Disconnect from relay server"""
        self.running = False
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
