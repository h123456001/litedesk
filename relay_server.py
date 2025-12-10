#!/usr/bin/env python3
"""
LiteDesk Relay Server - NAT Traversal Support

This server runs on a VPS with public IP and helps peers behind NAT
to discover each other and exchange connection information.

Run this on your VPS:
    python3 relay_server.py [--port 8877]
"""
import socket
import struct
import json
import threading
import argparse
import time
from datetime import datetime


class PeerInfo:
    """Information about a registered peer"""
    
    def __init__(self, peer_id, peer_type, socket_conn, addr):
        self.peer_id = peer_id
        self.peer_type = peer_type  # 'server' or 'client'
        self.socket = socket_conn
        self.addr = addr
        self.public_ip = addr[0]
        self.public_port = addr[1]
        self.registered_at = datetime.now()
        self.partner_id = None
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'peer_id': self.peer_id,
            'peer_type': self.peer_type,
            'public_ip': self.public_ip,
            'public_port': self.public_port,
            'partner_id': self.partner_id
        }


class RelayServer:
    """Relay server for NAT traversal"""
    
    def __init__(self, host='0.0.0.0', port=8877):
        """
        Initialize relay server
        
        Args:
            host: IP address to bind to
            port: Port number to listen on
        """
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.peers = {}  # peer_id -> PeerInfo
        self.lock = threading.Lock()
    
    def start(self):
        """Start the relay server"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(10)
        self.running = True
        
        print(f"[Relay Server] Started on {self.host}:{self.port}")
        print(f"[Relay Server] Waiting for peer connections...")
        
        # Start cleanup thread
        threading.Thread(target=self.cleanup_stale_peers, daemon=True).start()
        
        # Accept connections
        while self.running:
            try:
                client_socket, addr = self.socket.accept()
                print(f"[Relay Server] New connection from {addr}")
                threading.Thread(
                    target=self.handle_peer,
                    args=(client_socket, addr),
                    daemon=True
                ).start()
            except Exception as e:
                if self.running:
                    print(f"[Relay Server] Error accepting connection: {e}")
    
    def handle_peer(self, client_socket, addr):
        """Handle a peer connection"""
        peer_info = None
        
        try:
            # Receive registration message
            msg = self.recv_message(client_socket)
            if not msg or msg.get('type') != 'register':
                print(f"[Relay Server] Invalid registration from {addr}")
                client_socket.close()
                return
            
            peer_id = msg.get('peer_id')
            peer_type = msg.get('peer_type')
            
            if not peer_id or not peer_type:
                print(f"[Relay Server] Missing peer info from {addr}")
                client_socket.close()
                return
            
            # Register peer
            with self.lock:
                if peer_id in self.peers:
                    # Update existing peer
                    old_peer = self.peers[peer_id]
                    if old_peer.socket:
                        try:
                            old_peer.socket.close()
                        except:
                            pass
                
                peer_info = PeerInfo(peer_id, peer_type, client_socket, addr)
                self.peers[peer_id] = peer_info
                print(f"[Relay Server] Registered {peer_type} '{peer_id}' from {addr}")
            
            # Send registration confirmation
            self.send_message(client_socket, {
                'type': 'registered',
                'peer_id': peer_id,
                'public_ip': addr[0],
                'public_port': addr[1]
            })
            
            # Handle peer requests
            while self.running:
                msg = self.recv_message(client_socket)
                if not msg:
                    break
                
                msg_type = msg.get('type')
                
                if msg_type == 'list_peers':
                    # List available peers
                    self.handle_list_peers(peer_info)
                
                elif msg_type == 'get_peer_info':
                    # Get specific peer info for connection
                    target_id = msg.get('target_id')
                    self.handle_get_peer_info(peer_info, target_id)
                
                elif msg_type == 'relay_data':
                    # Relay data to another peer
                    target_id = msg.get('target_id')
                    data = msg.get('data')
                    self.handle_relay_data(peer_info, target_id, data)
                
                elif msg_type == 'heartbeat':
                    # Peer is alive
                    self.send_message(client_socket, {'type': 'heartbeat_ack'})
                
                else:
                    print(f"[Relay Server] Unknown message type: {msg_type}")
        
        except Exception as e:
            print(f"[Relay Server] Error handling peer {addr}: {e}")
        
        finally:
            # Unregister peer
            if peer_info:
                with self.lock:
                    if peer_info.peer_id in self.peers:
                        del self.peers[peer_info.peer_id]
                        print(f"[Relay Server] Unregistered '{peer_info.peer_id}'")
            
            try:
                client_socket.close()
            except:
                pass
    
    def handle_list_peers(self, requester):
        """Send list of available peers"""
        with self.lock:
            # Get peers of opposite type
            opposite_type = 'client' if requester.peer_type == 'server' else 'server'
            available_peers = [
                {'peer_id': p.peer_id, 'peer_type': p.peer_type}
                for p in self.peers.values()
                if p.peer_type == opposite_type and p.peer_id != requester.peer_id
            ]
        
        self.send_message(requester.socket, {
            'type': 'peer_list',
            'peers': available_peers
        })
    
    def handle_get_peer_info(self, requester, target_id):
        """Send connection info for a specific peer"""
        with self.lock:
            target = self.peers.get(target_id)
            
            if target:
                # Send target's connection info to requester
                self.send_message(requester.socket, {
                    'type': 'peer_info',
                    'peer_id': target.peer_id,
                    'peer_type': target.peer_type,
                    'public_ip': target.public_ip,
                    'public_port': target.public_port
                })
                
                # Notify target about requester
                self.send_message(target.socket, {
                    'type': 'connection_request',
                    'from_peer_id': requester.peer_id,
                    'from_peer_type': requester.peer_type,
                    'from_public_ip': requester.public_ip,
                    'from_public_port': requester.public_port
                })
            else:
                self.send_message(requester.socket, {
                    'type': 'error',
                    'message': f'Peer {target_id} not found'
                })
    
    def handle_relay_data(self, sender, target_id, data):
        """Relay data between peers"""
        with self.lock:
            target = self.peers.get(target_id)
            
            if target:
                self.send_message(target.socket, {
                    'type': 'relayed_data',
                    'from_peer_id': sender.peer_id,
                    'data': data
                })
            else:
                self.send_message(sender.socket, {
                    'type': 'error',
                    'message': f'Peer {target_id} not found'
                })
    
    def cleanup_stale_peers(self):
        """Remove stale peer connections"""
        while self.running:
            time.sleep(60)  # Check every minute
            
            with self.lock:
                stale_peers = []
                for peer_id, peer in list(self.peers.items()):
                    try:
                        # Check if connection is still alive
                        self.send_message(peer.socket, {'type': 'ping'})
                    except:
                        stale_peers.append(peer_id)
                
                for peer_id in stale_peers:
                    print(f"[Relay Server] Removing stale peer: {peer_id}")
                    del self.peers[peer_id]
    
    def send_message(self, sock, msg):
        """Send a JSON message"""
        try:
            msg_json = json.dumps(msg).encode('utf-8')
            length = struct.pack('!I', len(msg_json))
            sock.sendall(length + msg_json)
        except Exception as e:
            raise
    
    def recv_message(self, sock):
        """Receive a JSON message"""
        try:
            # Receive message length
            length_data = self._recv_exact(sock, 4)
            if not length_data:
                return None
            
            length = struct.unpack('!I', length_data)[0]
            
            # Receive message data
            msg_data = self._recv_exact(sock, length)
            if not msg_data:
                return None
            
            return json.loads(msg_data.decode('utf-8'))
        except:
            return None
    
    def _recv_exact(self, sock, size):
        """Receive exact number of bytes"""
        data = b''
        while len(data) < size:
            packet = sock.recv(size - len(data))
            if not packet:
                return None
            data += packet
        return data
    
    def stop(self):
        """Stop the relay server"""
        self.running = False
        if self.socket:
            self.socket.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='LiteDesk Relay Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8877, help='Port to listen on')
    args = parser.parse_args()
    
    server = RelayServer(host=args.host, port=args.port)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[Relay Server] Shutting down...")
        server.stop()


if __name__ == '__main__':
    main()
