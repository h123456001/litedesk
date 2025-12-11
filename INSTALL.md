# LiteDesk Installation & Setup Guide

Complete cross-platform installation guide for Mac, Windows, and Linux.

## Table of Contents
- [System Requirements](#system-requirements)
- [macOS Installation](#macos-installation)
- [Windows Installation](#windows-installation)
- [Linux Installation](#linux-installation)
- [First Time Setup](#first-time-setup)
- [Platform-Specific Notes](#platform-specific-notes)

## System Requirements

### All Platforms
- Python 3.7 or higher
- At least 2GB RAM
- Network connectivity (LAN or Internet via relay)

### Platform-Specific
- **macOS**: macOS 10.12 (Sierra) or later
- **Windows**: Windows 10 or later
- **Linux**: X11 display server (most distributions)

## macOS Installation

### Step 1: Install Python

macOS usually comes with Python, but you may need Python 3:

```bash
# Check if Python 3 is installed
python3 --version

# If not installed, install via Homebrew
brew install python3
```

Or download from [python.org](https://www.python.org/downloads/macos/)

### Step 2: Clone and Install

```bash
# Clone the repository
git clone https://github.com/h123456001/litedesk.git
cd litedesk

# Install dependencies
pip3 install -r requirements.txt
```

### Step 3: Grant Permissions

**Screen Recording Permission** (for Server):
1. Open System Preferences > Security & Privacy
2. Click Privacy tab
3. Select Screen Recording from left sidebar
4. Click the lock to make changes
5. Check the box next to Terminal or your Python launcher
6. Restart the application

**Accessibility Permission** (for Server and Client):
1. Open System Preferences > Security & Privacy
2. Click Privacy tab
3. Select Accessibility from left sidebar
4. Click the lock to make changes
5. Add Terminal or your Python launcher
6. Restart the application

### Step 4: Launch

**Server (Controlled Machine):**
```bash
./start_server.sh
# or
python3 server.py
```

**Client (Controller Machine):**
```bash
./start_client.sh
# or
python3 client.py
```

## Windows Installation

### Step 1: Install Python

1. Download Python from [python.org](https://www.python.org/downloads/windows/)
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Click "Install Now"

Verify installation:
```cmd
python --version
```

### Step 2: Clone and Install

```cmd
# Clone the repository (requires Git)
git clone https://github.com/h123456001/litedesk.git
cd litedesk

# Or download ZIP from GitHub and extract

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Firewall Configuration

When you first run the server, Windows Defender Firewall will prompt:
1. Check "Private networks"
2. Click "Allow access"

Or manually add firewall rule:
```cmd
netsh advfirewall firewall add rule name="LiteDesk Server" dir=in action=allow protocol=TCP localport=9876
```

### Step 4: Launch

**Server (Controlled Machine):**
Double-click `start_server.bat` or run:
```cmd
python server.py
```

**Client (Controller Machine):**
Double-click `start_client.bat` or run:
```cmd
python client.py
```

**Note**: For best results, right-click and "Run as Administrator"

## Linux Installation

### Step 1: Install Python and Dependencies

**Ubuntu/Debian:**
```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3 python3-pip

# Install system dependencies
sudo apt install python3-tk python3-dev
sudo apt install libxcb-xinerama0  # For PyQt5

# For X11 support
sudo apt install xorg xserver-xorg
```

**Fedora/RHEL:**
```bash
sudo dnf install python3 python3-pip
sudo dnf install python3-tkinter
sudo dnf install libxcb  # For PyQt5
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip
sudo pacman -S tk
```

### Step 2: Clone and Install

```bash
# Clone the repository
git clone https://github.com/h123456001/litedesk.git
cd litedesk

# Install Python dependencies
pip3 install -r requirements.txt

# Or use --user flag if you don't have sudo
pip3 install --user -r requirements.txt
```

### Step 3: Configure Firewall

**UFW (Ubuntu):**
```bash
sudo ufw allow 9876/tcp
```

**Firewalld (Fedora/RHEL):**
```bash
sudo firewall-cmd --permanent --add-port=9876/tcp
sudo firewall-cmd --reload
```

### Step 4: Verify X11

Make sure you're running X11 (not just Wayland):
```bash
echo $DISPLAY
# Should output something like :0 or :1
```

If using Wayland, you may need to switch to X11 session at login.

### Step 5: Launch

**Server (Controlled Machine):**
```bash
chmod +x start_server.sh
./start_server.sh
# or
python3 server.py
```

**Client (Controller Machine):**
```bash
chmod +x start_client.sh
./start_client.sh
# or
python3 client.py
```

## First Time Setup

### Server Setup (Machine to be Controlled)

1. Launch the server application
2. You'll see your local IP address displayed
3. Choose connection mode:
   - **Direct Connection**: For LAN or if you have public IP
   - **Relay Mode**: If both machines are behind NAT
4. Click "Start Sharing"
5. Share your IP address (or relay ID) with the client user

### Client Setup (Controller Machine)

1. Launch the client application
2. Choose connection mode:
   - **Direct Connection**: Enter server's IP address
   - **Via Relay Server**: Enter relay server IP, then list and select server
3. Click "Connect"
4. You should now see the remote desktop

## Platform-Specific Notes

### macOS

**Common Issues:**
- **Permission denied**: Grant Screen Recording and Accessibility permissions
- **Command not found**: Make sure Python 3 is in your PATH
- **Application quit**: Check permissions in System Preferences

**Tips:**
- Use Terminal or iTerm2 to run the application
- On first run, macOS will prompt for permissions - grant them
- If using Apple Silicon (M1/M2), ensure you have native Python

### Windows

**Common Issues:**
- **Python not found**: Add Python to PATH or reinstall with PATH option
- **Firewall blocks connection**: Allow the application in Windows Defender
- **Input control doesn't work**: Run as Administrator

**Tips:**
- Run Command Prompt or PowerShell as Administrator for best results
- Disable Windows Defender temporarily if connection fails
- Check that port 9876 is not used by another application

### Linux

**Common Issues:**
- **DISPLAY not set**: Make sure you're in a GUI session with X11
- **Permission denied**: May need to run with sudo for input control
- **Wayland issues**: Switch to X11 session at login screen

**Tips:**
- Works best on X11, not Wayland
- On Ubuntu 22.04+, you may need to select "Ubuntu on Xorg" at login
- For headless servers, X11 must be configured and running

## Troubleshooting

### Dependencies Installation Failed

```bash
# Try upgrading pip first
pip3 install --upgrade pip

# Install dependencies one by one
pip3 install mss
pip3 install Pillow
pip3 install pynput
pip3 install PyQt5
```

### Cannot Connect

1. Check firewall settings on both machines
2. Verify both machines are on same network (for direct connection)
3. Confirm server is running and showing "Waiting for connection"
4. Try pinging the server IP from client machine
5. Use relay mode if direct connection fails

### Poor Performance

1. Adjust JPEG quality in server settings (lower = faster)
2. Close unnecessary applications
3. Use wired connection instead of WiFi
4. Check network bandwidth

## Getting Help

- **GitHub Issues**: [Report bugs](https://github.com/h123456001/litedesk/issues)
- **Documentation**: Check README.md and TROUBLESHOOTING.md
- **Platform Info**: Run `python3 platform_utils.py` for system info

## Security Notes

⚠️ **This is a demonstration project**

For production use, add:
- Connection passwords
- SSL/TLS encryption
- Session timeouts
- Connection logging

Do not use on untrusted networks without additional security measures.
