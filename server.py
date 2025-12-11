#!/usr/bin/env python3
"""
LiteDesk Server - Host/Share Desktop

Run this on the machine you want to share.
"""
import sys
import time
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLabel, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont
from screen_capture import ScreenCapture
from input_control import InputController
from network import NetworkServer, NetworkServerWithRelay
from platform_utils import (get_platform, get_default_network_interface, 
                            show_permission_instructions, check_display_available)


class ServerSignals(QObject):
    """Signals for server events"""
    client_connected = pyqtSignal(str)
    client_disconnected = pyqtSignal()
    error = pyqtSignal(str)


class LiteDeskServer(QMainWindow):
    """Main server window"""
    
    def __init__(self):
        super().__init__()
        self.server = None
        self.screen_capture = None
        self.input_controller = None
        self.running = False
        self.signals = ServerSignals()
        
        # Connect signals
        self.signals.client_connected.connect(self.on_client_connected)
        self.signals.client_disconnected.connect(self.on_client_disconnected)
        self.signals.error.connect(self.on_error)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        platform_name = get_platform().upper()
        self.setWindowTitle(f"LiteDesk Server - Share Desktop ({platform_name})")
        self.setGeometry(100, 100, 450, 450)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("LiteDesk Server")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Relay server input (optional)
        from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QCheckBox
        
        relay_layout = QHBoxLayout()
        self.use_relay_checkbox = QCheckBox("Use Relay Server:")
        self.use_relay_checkbox.setFont(QFont("Arial", 10))
        relay_layout.addWidget(self.use_relay_checkbox)
        
        self.relay_input = QLineEdit()
        self.relay_input.setPlaceholderText("Relay server IP (optional, for NAT)")
        self.relay_input.setFont(QFont("Arial", 10))
        self.relay_input.setEnabled(False)
        relay_layout.addWidget(self.relay_input)
        
        self.use_relay_checkbox.stateChanged.connect(
            lambda state: self.relay_input.setEnabled(state == Qt.Checked)
        )
        
        layout.addLayout(relay_layout)
        
        # Platform info label
        platform_name = get_platform().capitalize()
        local_ip = get_default_network_interface() or "N/A"
        self.platform_label = QLabel(f"Platform: {platform_name} | Local IP: {local_ip}")
        self.platform_label.setFont(QFont("Arial", 9))
        self.platform_label.setAlignment(Qt.AlignCenter)
        self.platform_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.platform_label)
        
        # Status label
        self.status_label = QLabel("Not sharing")
        self.status_label.setFont(QFont("Arial", 12))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: gray; padding: 10px;")
        layout.addWidget(self.status_label)
        
        # Connection info
        self.info_label = QLabel("")
        self.info_label.setFont(QFont("Arial", 10))
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        # Start button
        self.start_button = QPushButton("Start Sharing")
        self.start_button.setFont(QFont("Arial", 12))
        self.start_button.setMinimumHeight(50)
        self.start_button.clicked.connect(self.toggle_sharing)
        layout.addWidget(self.start_button)
        
        layout.addStretch(1)
    
    def toggle_sharing(self):
        """Start or stop sharing"""
        if not self.running:
            self.start_sharing()
        else:
            self.stop_sharing()
    
    def start_sharing(self):
        """Start the server and screen sharing"""
        try:
            # Check display availability
            if not check_display_available():
                msg = "Display not available. "
                msg += show_permission_instructions()
                QMessageBox.warning(self, "Display Not Available", msg)
                # Continue anyway as this might work in some cases
            
            # Check if relay mode is enabled
            use_relay = self.use_relay_checkbox.isChecked()
            relay_host = self.relay_input.text().strip() if use_relay else None
            
            # Initialize components
            if use_relay and relay_host:
                import socket
                peer_id = f"server_{socket.gethostname()}"
                self.server = NetworkServerWithRelay(
                    host='0.0.0.0', 
                    port=9876,
                    relay_host=relay_host,
                    relay_port=8877,
                    peer_id=peer_id
                )
                self.server.start_with_relay()
                info_text = f"Server is listening on port 9876\n"
                info_text += f"Registered with relay: {relay_host}\n"
                info_text += f"Server ID: {peer_id}\n"
                info_text += "Clients can connect via relay or direct IP"
            else:
                self.server = NetworkServer(host='0.0.0.0', port=9876)
                self.server.start()
                info_text = "Server is listening on port 9876\nShare your IP address with the client"
            
            self.screen_capture = ScreenCapture(quality=50)
            self.input_controller = InputController()
            
            self.running = True
            
            # Update UI
            self.status_label.setText("⏳ Waiting for connection...")
            self.status_label.setStyleSheet("color: orange; padding: 10px;")
            self.info_label.setText(info_text)
            self.start_button.setText("Stop Sharing")
            self.use_relay_checkbox.setEnabled(False)
            self.relay_input.setEnabled(False)
            
            # Start server thread
            threading.Thread(target=self.server_loop, daemon=True).start()
            
        except Exception as e:
            self.signals.error.emit(f"Failed to start server: {str(e)}")
    
    def server_loop(self):
        """Main server loop"""
        try:
            # Wait for client connection
            if self.server.accept_connection():
                self.signals.client_connected.emit("Client connected")
                
                # Main streaming loop
                while self.running and self.server.client_socket:
                    # Capture and send frame
                    width, height, jpeg_data = self.screen_capture.capture_screen()
                    if not self.server.send_frame(width, height, jpeg_data):
                        break
                    
                    # Check for commands (non-blocking)
                    cmd = self.server.receive_command()
                    if cmd:
                        self.process_command(cmd)
                    
                    # Control frame rate (approx 10 FPS)
                    time.sleep(0.1)
                
                self.signals.client_disconnected.emit()
        except Exception as e:
            self.signals.error.emit(f"Server error: {str(e)}")
    
    def process_command(self, cmd):
        """Process a command from the client"""
        try:
            cmd_type = cmd.get('type')
            data = cmd.get('data', {})
            
            if cmd_type == 'mouse_move':
                x, y = data.get('x'), data.get('y')
                self.input_controller.move_mouse(x, y)
            
            elif cmd_type == 'mouse_click':
                button = data.get('button', 'left')
                press = data.get('press', True)
                self.input_controller.click_mouse(button, press)
            
            elif cmd_type == 'mouse_scroll':
                dx, dy = data.get('dx', 0), data.get('dy', 0)
                self.input_controller.scroll_mouse(dx, dy)
            
            elif cmd_type == 'key_press':
                key = data.get('key')
                self.input_controller.press_key(key)
            
        except Exception as e:
            print(f"Error processing command: {e}")
    
    def stop_sharing(self):
        """Stop the server"""
        self.running = False
        
        if self.server:
            self.server.stop()
        
        if self.screen_capture:
            self.screen_capture.close()
        
        # Update UI
        self.status_label.setText("Not sharing")
        self.status_label.setStyleSheet("color: gray; padding: 10px;")
        self.info_label.setText("")
        self.start_button.setText("Start Sharing")
        self.use_relay_checkbox.setEnabled(True)
        if self.use_relay_checkbox.isChecked():
            self.relay_input.setEnabled(True)
    
    def on_client_connected(self, msg):
        """Handle client connection"""
        self.status_label.setText("✓ Client Connected - Sharing Desktop")
        self.status_label.setStyleSheet("color: green; padding: 10px;")
    
    def on_client_disconnected(self):
        """Handle client disconnection"""
        if self.running:
            self.status_label.setText("⏳ Waiting for connection...")
            self.status_label.setStyleSheet("color: orange; padding: 10px;")
    
    def on_error(self, msg):
        """Handle errors"""
        QMessageBox.critical(self, "Error", msg)
        self.stop_sharing()
    
    def closeEvent(self, event):
        """Handle window close"""
        self.stop_sharing()
        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    server = LiteDeskServer()
    server.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
