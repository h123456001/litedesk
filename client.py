#!/usr/bin/env python3
"""
LiteDesk Client - Connect to Remote Desktop

Run this on the machine you want to control from.
"""
import sys
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                            QMessageBox, QCheckBox, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QPixmap, QImage, QPainter
from network import NetworkClient, NetworkClientWithRelay
from platform_utils import get_platform, show_permission_instructions


class ClientSignals(QObject):
    """Signals for client events"""
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    frame_received = pyqtSignal(object)  # PIL Image
    error = pyqtSignal(str)


class RemoteDesktopWidget(QLabel):
    """Widget to display remote desktop"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.setAlignment(Qt.AlignCenter)
        self.setText("Not connected")
        self.setStyleSheet("background-color: black; color: white; border: 1px solid gray;")
        
        self.current_image = None
        self.scale_factor = 1.0
        self.client = None
        
        # Enable mouse tracking
        self.setMouseTracking(True)
    
    def set_client(self, client):
        """Set the network client for sending commands"""
        self.client = client
    
    def update_frame(self, pil_image):
        """Update the displayed frame"""
        self.current_image = pil_image
        
        # Convert PIL Image to QImage
        img_data = pil_image.convert('RGB').tobytes()
        qimage = QImage(img_data, pil_image.width, pil_image.height, 
                       pil_image.width * 3, QImage.Format_RGB888)
        
        # Scale to fit widget
        scaled = qimage.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        pixmap = QPixmap.fromImage(scaled)
        self.setPixmap(pixmap)
        
        # Calculate scale factor for mouse coordinates (prevent division by zero)
        if scaled.width() > 0 and scaled.height() > 0:
            self.scale_factor = pil_image.width / scaled.width()
        else:
            self.scale_factor = 1.0
    
    def mouseMoveEvent(self, event):
        """Handle mouse movement"""
        if self.client and self.client.connected and self.current_image:
            # Calculate actual coordinates on remote screen
            x = int(event.x() * self.scale_factor)
            y = int(event.y() * self.scale_factor)
            self.client.send_command('mouse_move', {'x': x, 'y': y})
    
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if self.client and self.client.connected:
            button = 'left' if event.button() == Qt.LeftButton else 'right'
            self.client.send_command('mouse_click', {'button': button, 'press': True})
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if self.client and self.client.connected:
            button = 'left' if event.button() == Qt.LeftButton else 'right'
            self.client.send_command('mouse_click', {'button': button, 'press': False})
    
    def wheelEvent(self, event):
        """Handle mouse wheel"""
        if self.client and self.client.connected:
            dy = 1 if event.angleDelta().y() > 0 else -1
            self.client.send_command('mouse_scroll', {'dx': 0, 'dy': dy})
    
    def keyPressEvent(self, event):
        """Handle keyboard input"""
        if self.client and self.client.connected:
            key = event.text()
            if key:
                self.client.send_command('key_press', {'key': key})


class LiteDeskClient(QMainWindow):
    """Main client window"""
    
    def __init__(self):
        super().__init__()
        self.client = None
        self.running = False
        self.signals = ClientSignals()
        
        # Connect signals
        self.signals.connected.connect(self.on_connected)
        self.signals.disconnected.connect(self.on_disconnected)
        self.signals.frame_received.connect(self.on_frame_received)
        self.signals.error.connect(self.on_error)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        platform_name = get_platform().upper()
        self.setWindowTitle(f"LiteDesk Client - Remote Desktop ({platform_name})")
        self.setGeometry(100, 100, 900, 750)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        
        # Connection mode panel
        mode_panel = QWidget()
        mode_layout = QHBoxLayout(mode_panel)
        
        mode_label = QLabel("Connection Mode:")
        mode_label.setFont(QFont("Arial", 10))
        mode_layout.addWidget(mode_label)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Direct Connection")
        self.mode_combo.addItem("Via Relay Server")
        self.mode_combo.setFont(QFont("Arial", 10))
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_combo)
        
        mode_layout.addStretch()
        main_layout.addWidget(mode_panel)
        
        # Direct connection panel
        self.direct_panel = QWidget()
        direct_layout = QHBoxLayout(self.direct_panel)
        
        conn_label = QLabel("Server IP:")
        conn_label.setFont(QFont("Arial", 10))
        direct_layout.addWidget(conn_label)
        
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter server IP address (e.g., 192.168.1.100)")
        self.ip_input.setFont(QFont("Arial", 10))
        direct_layout.addWidget(self.ip_input)
        
        main_layout.addWidget(self.direct_panel)
        
        # Relay connection panel
        self.relay_panel = QWidget()
        relay_layout = QVBoxLayout(self.relay_panel)
        
        relay_server_layout = QHBoxLayout()
        relay_label = QLabel("Relay Server:")
        relay_label.setFont(QFont("Arial", 10))
        relay_server_layout.addWidget(relay_label)
        
        self.relay_input = QLineEdit()
        self.relay_input.setPlaceholderText("Enter relay server IP")
        self.relay_input.setFont(QFont("Arial", 10))
        relay_server_layout.addWidget(self.relay_input)
        
        self.list_servers_button = QPushButton("List Servers")
        self.list_servers_button.setFont(QFont("Arial", 10))
        self.list_servers_button.clicked.connect(self.list_available_servers)
        relay_server_layout.addWidget(self.list_servers_button)
        
        relay_layout.addLayout(relay_server_layout)
        
        server_select_layout = QHBoxLayout()
        server_label = QLabel("Select Server:")
        server_label.setFont(QFont("Arial", 10))
        server_select_layout.addWidget(server_label)
        
        self.server_combo = QComboBox()
        self.server_combo.setFont(QFont("Arial", 10))
        server_select_layout.addWidget(self.server_combo)
        
        relay_layout.addLayout(server_select_layout)
        
        main_layout.addWidget(self.relay_panel)
        self.relay_panel.hide()
        
        # Connect button
        button_layout = QHBoxLayout()
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.setFont(QFont("Arial", 10))
        self.connect_button.clicked.connect(self.toggle_connection)
        button_layout.addWidget(self.connect_button)
        
        main_layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("Not connected")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: gray; padding: 5px;")
        main_layout.addWidget(self.status_label)
        
        # Remote desktop display
        self.desktop_widget = RemoteDesktopWidget()
        main_layout.addWidget(self.desktop_widget)
    
    def on_mode_changed(self, index):
        """Handle connection mode change"""
        if index == 0:  # Direct
            self.direct_panel.show()
            self.relay_panel.hide()
        else:  # Relay
            self.direct_panel.hide()
            self.relay_panel.show()
    
    
    def list_available_servers(self):
        """List available servers from relay"""
        relay_host = self.relay_input.text().strip()
        if not relay_host:
            QMessageBox.warning(self, "Warning", "Please enter relay server address")
            return
        
        try:
            self.status_label.setText("Listing servers...")
            self.status_label.setStyleSheet("color: orange; padding: 5px;")
            
            # Create temporary relay client to list servers
            import socket
            peer_id = f"client_{socket.gethostname()}"
            temp_client = NetworkClientWithRelay(relay_host=relay_host, peer_id=peer_id)
            
            servers = temp_client.list_available_servers()
            temp_client.disconnect()
            
            self.server_combo.clear()
            if servers:
                for server in servers:
                    self.server_combo.addItem(server['peer_id'])
                self.status_label.setText(f"Found {len(servers)} server(s)")
                self.status_label.setStyleSheet("color: green; padding: 5px;")
            else:
                self.status_label.setText("No servers found")
                self.status_label.setStyleSheet("color: gray; padding: 5px;")
                QMessageBox.information(self, "Info", "No servers available on relay")
        
        except Exception as e:
            self.status_label.setText("Error listing servers")
            self.status_label.setStyleSheet("color: red; padding: 5px;")
            QMessageBox.critical(self, "Error", f"Failed to list servers: {str(e)}")
    
    def toggle_connection(self):
        """Connect or disconnect"""
        if not self.running:
            self.start_connection()
        else:
            self.stop_connection()
    
    def start_connection(self):
        """Connect to the server"""
        # Check connection mode
        mode = self.mode_combo.currentIndex()
        
        if mode == 0:  # Direct connection
            ip_address = self.ip_input.text().strip()
            if not ip_address:
                QMessageBox.warning(self, "Warning", "Please enter server IP address")
                return
            
            self.connect_direct(ip_address)
        
        else:  # Relay connection
            relay_host = self.relay_input.text().strip()
            if not relay_host:
                QMessageBox.warning(self, "Warning", "Please enter relay server address")
                return
            
            target_server = self.server_combo.currentText()
            if not target_server:
                QMessageBox.warning(self, "Warning", "Please select a server or click 'List Servers'")
                return
            
            self.connect_via_relay(relay_host, target_server)
    
    def connect_direct(self, ip_address):
        """Direct connection to server"""
        try:
            # Create client
            self.client = NetworkClient()
            self.desktop_widget.set_client(self.client)
            
            # Update UI
            self.status_label.setText("Connecting...")
            self.status_label.setStyleSheet("color: orange; padding: 5px;")
            self.connect_button.setEnabled(False)
            self.ip_input.setEnabled(False)
            self.mode_combo.setEnabled(False)
            
            # Connect in background thread
            threading.Thread(target=self.connect_direct_thread, args=(ip_address,), daemon=True).start()
            
        except Exception as e:
            self.signals.error.emit(f"Failed to start client: {str(e)}")
    
    def connect_direct_thread(self, ip_address):
        """Direct connection thread"""
        try:
            # Connect to server
            if not self.client.connect(ip_address, 9876):
                self.signals.error.emit("Failed to connect to server")
                return
            
            self.running = True
            self.signals.connected.emit()
            
            # Receive frames loop
            while self.running and self.client.connected:
                frame = self.client.receive_frame()
                if frame:
                    self.signals.frame_received.emit(frame)
                else:
                    break
            
            self.signals.disconnected.emit()
            
        except Exception as e:
            self.signals.error.emit(f"Connection error: {str(e)}")
    
    def connect_via_relay(self, relay_host, target_server):
        """Connect via relay server"""
        try:
            # Create relay-enabled client
            import socket
            peer_id = f"client_{socket.gethostname()}"
            self.client = NetworkClientWithRelay(
                relay_host=relay_host,
                relay_port=8877,
                peer_id=peer_id
            )
            self.desktop_widget.set_client(self.client)
            
            # Update UI
            self.status_label.setText("Connecting via relay...")
            self.status_label.setStyleSheet("color: orange; padding: 5px;")
            self.connect_button.setEnabled(False)
            self.relay_input.setEnabled(False)
            self.server_combo.setEnabled(False)
            self.list_servers_button.setEnabled(False)
            self.mode_combo.setEnabled(False)
            
            # Connect in background thread
            threading.Thread(
                target=self.connect_relay_thread, 
                args=(target_server,), 
                daemon=True
            ).start()
            
        except Exception as e:
            self.signals.error.emit(f"Failed to start relay client: {str(e)}")
    
    def connect_relay_thread(self, target_server):
        """Relay connection thread"""
        try:
            # Connect via relay
            if not self.client.connect_via_relay(target_server):
                self.signals.error.emit("Failed to connect via relay")
                return
            
            self.running = True
            self.signals.connected.emit()
            
            # Receive frames loop
            while self.running and self.client.connected:
                frame = self.client.receive_frame()
                if frame:
                    self.signals.frame_received.emit(frame)
                else:
                    break
            
            self.signals.disconnected.emit()
            
        except Exception as e:
            self.signals.error.emit(f"Relay connection error: {str(e)}")
    
    def stop_connection(self):
        """Disconnect from server"""
        self.running = False
        
        if self.client:
            self.client.disconnect()
        
        # Update UI
        self.status_label.setText("Not connected")
        self.status_label.setStyleSheet("color: gray; padding: 5px;")
        self.connect_button.setText("Connect")
        self.connect_button.setEnabled(True)
        
        # Enable appropriate inputs based on mode
        mode = self.mode_combo.currentIndex()
        if mode == 0:  # Direct
            self.ip_input.setEnabled(True)
        else:  # Relay
            self.relay_input.setEnabled(True)
            self.server_combo.setEnabled(True)
            self.list_servers_button.setEnabled(True)
        
        self.mode_combo.setEnabled(True)
        self.desktop_widget.setText("Not connected")
        self.desktop_widget.setPixmap(QPixmap())
    
    def on_connected(self):
        """Handle successful connection"""
        self.status_label.setText("✓ Connected - Receiving desktop...")
        self.status_label.setStyleSheet("color: green; padding: 5px;")
        self.connect_button.setText("Disconnect")
        self.connect_button.setEnabled(True)
    
    def on_disconnected(self):
        """Handle disconnection"""
        if self.running:
            self.stop_connection()
    
    def on_frame_received(self, frame):
        """Handle received frame"""
        self.desktop_widget.update_frame(frame)
    
    def on_error(self, msg):
        """Handle errors"""
        QMessageBox.critical(self, "Error", msg)
        self.stop_connection()
    
    def closeEvent(self, event):
        """Handle window close"""
        self.stop_connection()
        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    client = LiteDeskClient()
    client.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
