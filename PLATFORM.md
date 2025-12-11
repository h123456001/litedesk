# LiteDesk Cross-Platform Compatibility Guide

## Overview

LiteDesk is designed to work seamlessly across Mac, Windows, and Linux platforms. This guide details the platform-specific features, requirements, and best practices.

## Supported Platforms

| Platform | Controlled End (Server) | Controller (Client) | Status |
|----------|------------------------|---------------------|---------|
| **macOS** | ✓ Full Support | ✓ Full Support | 10.12+ |
| **Windows** | ✓ Full Support | ✓ Full Support | 10/11 |
| **Linux** | ✓ Full Support | ✓ Full Support | X11 Required |

## Platform Features

### macOS

**Advantages:**
- Native Python support
- Excellent GUI performance with PyQt5
- Smooth input control with pynput
- High-quality screen capture

**Requirements:**
- macOS 10.12 (Sierra) or later
- Python 3.7+
- Screen Recording permission (for server)
- Accessibility permission (for server and client)

**Known Limitations:**
- First run requires manual permission grants
- May need to restart application after granting permissions
- Apple Silicon (M1/M2) fully supported

### Windows

**Advantages:**
- Widest user base
- Straightforward installation
- Good performance

**Requirements:**
- Windows 10 or Windows 11
- Python 3.7+
- Windows Defender Firewall exception

**Known Limitations:**
- May require Administrator privileges for input control
- Firewall configuration needed for server
- Some antivirus software may flag the application

### Linux

**Advantages:**
- Open source friendly
- Lightweight and performant
- Excellent for headless server use (with X11)

**Requirements:**
- X11 display server (most distributions)
- Python 3.7+
- DISPLAY environment variable set

**Known Limitations:**
- Wayland support limited (use X11 session)
- May need sudo for some input control features
- Distribution-specific package dependencies

## Cross-Platform Features Matrix

| Feature | macOS | Windows | Linux |
|---------|-------|---------|-------|
| Screen Capture | ✓ | ✓ | ✓ (X11) |
| Input Control (Mouse) | ✓ | ✓ | ✓ (X11) |
| Input Control (Keyboard) | ✓ | ✓ | ✓ (X11) |
| GUI Interface | ✓ | ✓ | ✓ |
| Network P2P | ✓ | ✓ | ✓ |
| NAT Traversal (Relay) | ✓ | ✓ | ✓ |
| Multi-monitor | Partial | Partial | Partial |

## Platform Detection

LiteDesk automatically detects your platform and adapts its behavior:

```python
from platform_utils import get_platform

platform = get_platform()
# Returns: 'macos', 'windows', 'linux', or 'unknown'
```

The application displays the platform in the window title for easy identification.

## Installation Methods

### Method 1: Using Launch Scripts (Recommended)

**macOS/Linux:**
```bash
./start_server.sh  # For server
./start_client.sh  # For client
```

**Windows:**
```cmd
start_server.bat  # For server
start_client.bat  # For client
```

Launch scripts automatically:
- Check Python installation
- Install missing dependencies
- Show platform-specific instructions
- Launch the application

### Method 2: Direct Python Execution

```bash
# Server
python3 server.py  # macOS/Linux
python server.py   # Windows

# Client
python3 client.py  # macOS/Linux
python client.py   # Windows
```

### Method 3: Using setup.py

```bash
pip install -e .
litedesk-server  # Start server
litedesk-client  # Start client
```

## Platform-Specific Configuration

### macOS Configuration

**Granting Permissions:**

1. **Screen Recording** (Required for server):
   ```
   System Preferences → Security & Privacy → Privacy → Screen Recording
   Add: Terminal.app or your Python launcher
   ```

2. **Accessibility** (Required for input control):
   ```
   System Preferences → Security & Privacy → Privacy → Accessibility
   Add: Terminal.app or your Python launcher
   ```

3. **Network** (Automatic):
   - macOS will prompt for incoming connections
   - Click "Allow" when prompted

**Environment:**
```bash
# Check Python version
python3 --version

# Install dependencies
pip3 install -r requirements.txt
```

### Windows Configuration

**Firewall Configuration:**

Manual configuration:
```cmd
netsh advfirewall firewall add rule name="LiteDesk Server" dir=in action=allow protocol=TCP localport=9876
```

Or allow when Windows prompts on first run.

**Running as Administrator:**

Right-click start script or command prompt → "Run as Administrator"

**Environment:**
```cmd
# Check Python version
python --version

# Install dependencies
pip install -r requirements.txt
```

### Linux Configuration

**X11 Setup:**

Check if X11 is running:
```bash
echo $DISPLAY
# Should output: :0 or :1
```

If using Wayland, switch to X11:
- At login screen, click gear icon
- Select "Ubuntu on Xorg" (or similar)

**Firewall Configuration:**

**Ubuntu/Debian (UFW):**
```bash
sudo ufw allow 9876/tcp
sudo ufw enable
```

**Fedora/RHEL (firewalld):**
```bash
sudo firewall-cmd --permanent --add-port=9876/tcp
sudo firewall-cmd --reload
```

**System Dependencies:**

**Ubuntu/Debian:**
```bash
sudo apt install python3-tk python3-dev libxcb-xinerama0
```

**Fedora/RHEL:**
```bash
sudo dnf install python3-tkinter libxcb
```

**Environment:**
```bash
# Check Python version
python3 --version

# Install dependencies
pip3 install -r requirements.txt
```

## Testing Cross-Platform Compatibility

### Run Platform Tests

```bash
python3 platform_utils.py
```

This displays:
- Current platform information
- Permission requirements
- Network configuration
- Dependency status

### Run Comprehensive Tests

```bash
python3 test_comprehensive.py
```

Tests include:
- Platform detection
- Dependency availability
- Network protocol
- Image processing
- Socket communication

### Run Component Tests

```bash
python3 test_litedesk.py
```

Basic component verification for quick checks.

## Troubleshooting by Platform

### macOS Issues

**"Python not found"**
```bash
# Install via Homebrew
brew install python3
```

**"Permission denied" for screen capture**
- Grant Screen Recording permission
- Restart the application

**"Operation not permitted" for input control**
- Grant Accessibility permission
- May need to restart Terminal

### Windows Issues

**"Python is not recognized"**
- Add Python to PATH
- Or reinstall Python with "Add to PATH" option

**"Firewall blocking connection"**
```cmd
# Check firewall rules
netsh advfirewall firewall show rule name="LiteDesk Server"

# Add rule if missing
netsh advfirewall firewall add rule name="LiteDesk Server" dir=in action=allow protocol=TCP localport=9876
```

**"Input control not working"**
- Run as Administrator
- Check User Account Control settings

### Linux Issues

**"DISPLAY not set"**
```bash
# Set DISPLAY manually
export DISPLAY=:0

# Or run with DISPLAY
DISPLAY=:0 python3 server.py
```

**"X connection failed"**
- Make sure X11 is running (not Wayland)
- Check: `ps aux | grep X`

**"Permission denied" for input control**
```bash
# Run with sudo (not recommended for regular use)
sudo python3 server.py

# Or add user to input group
sudo usermod -a -G input $USER
```

## Performance Optimization

### All Platforms

1. **Adjust JPEG quality** in server.py:
   ```python
   self.screen_capture = ScreenCapture(quality=50)
   # Lower = faster, higher = better quality
   ```

2. **Adjust frame rate** in server.py:
   ```python
   time.sleep(0.1)  # ~10 FPS
   # Increase sleep for lower FPS
   ```

3. **Use wired connection** instead of WiFi for better latency

### Platform-Specific Optimizations

**macOS:**
- Close unnecessary applications
- Disable visual effects (System Preferences → Accessibility → Display → Reduce motion)

**Windows:**
- Disable Windows Defender real-time scanning temporarily
- Close background applications
- Use High Performance power plan

**Linux:**
- Use lightweight desktop environment (XFCE, LXDE)
- Disable compositing effects
- Use minimal window manager

## Development and Building

### Building Platform-Specific Packages

**macOS (.app bundle):**
```bash
pip install py2app
python setup.py py2app
```

**Windows (.exe):**
```bash
pip install pyinstaller
pyinstaller --onefile server.py
pyinstaller --onefile client.py
```

**Linux (AppImage):**
```bash
pip install pyinstaller
pyinstaller server.py
# Use AppImage tools to create AppImage
```

## Security Considerations

### Platform Security Features

**macOS:**
- Gatekeeper may block unsigned applications
- SIP (System Integrity Protection) enabled by default
- Keychain for secure credential storage

**Windows:**
- Windows Defender SmartScreen may warn
- UAC prompts for elevated privileges
- Windows Credential Manager available

**Linux:**
- SELinux/AppArmor may restrict access
- sudo required for some operations
- Various distro-specific security policies

### Recommendations

1. Use relay mode only with trusted relay servers
2. Run on private networks when possible
3. Keep Python and dependencies updated
4. Monitor connection logs
5. Use firewall rules to restrict access

## Contributing

When contributing cross-platform code:

1. Test on all three platforms (macOS, Windows, Linux)
2. Use platform-agnostic paths (`os.path.join()`)
3. Handle platform-specific exceptions gracefully
4. Update platform tests for new features
5. Document platform-specific behavior

## Resources

- **Python cross-platform**: https://docs.python.org/3/library/os.html
- **PyQt5 documentation**: https://www.riverbankcomputing.com/static/Docs/PyQt5/
- **mss (screen capture)**: https://python-mss.readthedocs.io/
- **pynput (input control)**: https://pynput.readthedocs.io/

## Support Matrix

| Component | macOS 10.12+ | Windows 10+ | Linux (X11) |
|-----------|--------------|-------------|-------------|
| Python 3.7 | ✓ | ✓ | ✓ |
| Python 3.8 | ✓ | ✓ | ✓ |
| Python 3.9 | ✓ | ✓ | ✓ |
| Python 3.10 | ✓ | ✓ | ✓ |
| Python 3.11 | ✓ | ✓ | ✓ |
| Python 3.12 | ✓ | ✓ | ✓ |

Last updated: 2025-12
