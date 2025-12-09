#!/usr/bin/env python3
"""
LiteDesk Client - Connect to Remote Desktop

Run this on the machine you want to control from.
"""
import sys
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                            QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QPixmap, QImage, QPainter
from network import NetworkClient


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
        self.setWindowTitle("LiteDesk Client - Remote Desktop")
        self.setGeometry(100, 100, 900, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        
        # Connection panel
        conn_panel = QWidget()
        conn_layout = QHBoxLayout(conn_panel)
        
        conn_label = QLabel("Server IP:")
        conn_label.setFont(QFont("Arial", 10))
        conn_layout.addWidget(conn_label)
        
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter server IP address (e.g., 192.168.1.100)")
        self.ip_input.setFont(QFont("Arial", 10))
        conn_layout.addWidget(self.ip_input)
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.setFont(QFont("Arial", 10))
        self.connect_button.clicked.connect(self.toggle_connection)
        conn_layout.addWidget(self.connect_button)
        
        main_layout.addWidget(conn_panel)
        
        # Status label
        self.status_label = QLabel("Not connected")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: gray; padding: 5px;")
        main_layout.addWidget(self.status_label)
        
        # Remote desktop display
        self.desktop_widget = RemoteDesktopWidget()
        main_layout.addWidget(self.desktop_widget)
    
    def toggle_connection(self):
        """Connect or disconnect"""
        if not self.running:
            self.start_connection()
        else:
            self.stop_connection()
    
    def start_connection(self):
        """Connect to the server"""
        ip_address = self.ip_input.text().strip()
        if not ip_address:
            QMessageBox.warning(self, "Warning", "Please enter server IP address")
            return
        
        try:
            # Create client
            self.client = NetworkClient()
            self.desktop_widget.set_client(self.client)
            
            # Update UI
            self.status_label.setText("Connecting...")
            self.status_label.setStyleSheet("color: orange; padding: 5px;")
            self.connect_button.setEnabled(False)
            self.ip_input.setEnabled(False)
            
            # Connect in background thread
            threading.Thread(target=self.connect_thread, args=(ip_address,), daemon=True).start()
            
        except Exception as e:
            self.signals.error.emit(f"Failed to start client: {str(e)}")
    
    def connect_thread(self, ip_address):
        """Connection thread"""
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
        self.ip_input.setEnabled(True)
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
