"""
LiteDesk - Platform Utilities

Cross-platform compatibility utilities for Mac, Windows, and Linux.
"""
import sys
import platform
import os


def get_platform():
    """
    Detect the current operating system
    
    Returns:
        str: 'windows', 'macos', 'linux', or 'unknown'
    """
    system = platform.system().lower()
    if system == 'darwin':
        return 'macos'
    elif system == 'windows':
        return 'windows'
    elif system == 'linux':
        return 'linux'
    else:
        return 'unknown'


def get_platform_info():
    """
    Get detailed platform information
    
    Returns:
        dict: Platform details
    """
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'platform_type': get_platform()
    }


def check_display_available():
    """
    Check if display/GUI is available
    
    Returns:
        bool: True if display is available
    """
    platform_type = get_platform()
    
    if platform_type == 'linux':
        # Check for X11 display on Linux
        return 'DISPLAY' in os.environ and os.environ['DISPLAY'] != ''
    elif platform_type == 'macos':
        # macOS always has a display in GUI session
        return True
    elif platform_type == 'windows':
        # Windows always has display in normal session
        return True
    
    return False


def get_permissions_requirements():
    """
    Get platform-specific permission requirements
    
    Returns:
        dict: Permission requirements for each platform
    """
    return {
        'macos': [
            'Screen Recording permission (System Preferences > Security & Privacy > Privacy > Screen Recording)',
            'Accessibility permission (System Preferences > Security & Privacy > Privacy > Accessibility)'
        ],
        'windows': [
            'Run as Administrator may be required for input control',
            'Windows Defender Firewall exception for port 9876'
        ],
        'linux': [
            'X11 display server must be running',
            'DISPLAY environment variable must be set',
            'May need to run with sudo for input control in some distributions'
        ]
    }


def show_permission_instructions():
    """
    Display permission instructions for current platform
    
    Returns:
        str: Permission instructions
    """
    platform_type = get_platform()
    reqs = get_permissions_requirements()
    
    if platform_type in reqs:
        instructions = f"\n{platform_type.upper()} Permission Requirements:\n"
        for i, req in enumerate(reqs[platform_type], 1):
            instructions += f"{i}. {req}\n"
        return instructions
    
    return "No special permissions required."


def get_default_network_interface():
    """
    Get the default network interface IP address
    
    Returns:
        str: IP address or None
    """
    import socket
    try:
        # Create a socket to get the default route
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


def get_all_ip_addresses():
    """
    Get all IP addresses for this machine
    
    Returns:
        list: List of IP addresses
    """
    import socket
    hostname = socket.gethostname()
    try:
        addresses = socket.getaddrinfo(hostname, None)
        ips = []
        for addr in addresses:
            ip = addr[4][0]
            # Filter out IPv6 and loopback
            if ':' not in ip and not ip.startswith('127.'):
                if ip not in ips:
                    ips.append(ip)
        return ips
    except Exception:
        return []


def is_admin():
    """
    Check if running with administrator/root privileges
    
    Returns:
        bool: True if running with elevated privileges
    """
    platform_type = get_platform()
    
    if platform_type == 'windows':
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    else:
        # Unix-like systems (macOS, Linux)
        return os.geteuid() == 0


def get_platform_specific_notes():
    """
    Get platform-specific usage notes
    
    Returns:
        dict: Notes for each platform
    """
    return {
        'macos': {
            'screen_capture': 'First time running may prompt for Screen Recording permission. Go to System Preferences > Security & Privacy > Privacy > Screen Recording and enable the application.',
            'input_control': 'First time running may prompt for Accessibility permission. Go to System Preferences > Security & Privacy > Privacy > Accessibility and enable the application.',
            'network': 'macOS Firewall may prompt to allow incoming connections. Click Allow.',
        },
        'windows': {
            'screen_capture': 'Windows may show User Account Control prompt. Click Yes to allow.',
            'input_control': 'Windows may require running as Administrator for input control to work properly.',
            'network': 'Windows Defender Firewall will prompt to allow the application. Select "Private networks" and click Allow.',
        },
        'linux': {
            'screen_capture': 'Requires X11 display server. Wayland support may be limited.',
            'input_control': 'Works best on X11. Some Wayland compositors may require additional setup.',
            'network': 'Firewall rules may need to be configured: sudo ufw allow 9876/tcp',
        }
    }


def check_dependencies():
    """
    Check if all required dependencies are available
    
    Returns:
        dict: Dependency check results
    """
    results = {}
    
    # Check mss
    try:
        import mss
        results['mss'] = {'available': True, 'version': mss.__version__}
    except ImportError as e:
        results['mss'] = {'available': False, 'error': str(e)}
    
    # Check PIL/Pillow
    try:
        from PIL import Image
        results['Pillow'] = {'available': True, 'version': Image.__version__}
    except ImportError as e:
        results['Pillow'] = {'available': False, 'error': str(e)}
    
    # Check pynput
    try:
        import pynput
        results['pynput'] = {'available': True, 'version': pynput.__version__}
    except ImportError as e:
        results['pynput'] = {'available': False, 'error': str(e)}
    
    # Check PyQt5
    try:
        from PyQt5 import QtCore
        results['PyQt5'] = {'available': True, 'version': QtCore.PYQT_VERSION_STR}
    except ImportError as e:
        results['PyQt5'] = {'available': False, 'error': str(e)}
    
    return results


def format_dependency_status(check_results):
    """
    Format dependency check results as string
    
    Args:
        check_results: Results from check_dependencies()
    
    Returns:
        str: Formatted status message
    """
    lines = ["Dependency Status:"]
    all_ok = True
    
    for name, info in check_results.items():
        if info['available']:
            version = info.get('version', 'unknown')
            lines.append(f"  ✓ {name} (v{version})")
        else:
            error = info.get('error', 'unknown error')
            lines.append(f"  ✗ {name} - {error}")
            all_ok = False
    
    if not all_ok:
        lines.append("\nTo install missing dependencies:")
        lines.append("  pip install -r requirements.txt")
    
    return "\n".join(lines)


if __name__ == '__main__':
    # Self-test
    print("Platform Information:")
    print("=" * 50)
    info = get_platform_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    
    print("\n" + "=" * 50)
    print(show_permission_instructions())
    
    print("=" * 50)
    print(f"Display available: {check_display_available()}")
    print(f"Running as admin: {is_admin()}")
    
    print("\n" + "=" * 50)
    print("Network Interfaces:")
    default_ip = get_default_network_interface()
    if default_ip:
        print(f"Default IP: {default_ip}")
    all_ips = get_all_ip_addresses()
    if all_ips:
        print(f"All IPs: {', '.join(all_ips)}")
    
    print("\n" + "=" * 50)
    deps = check_dependencies()
    print(format_dependency_status(deps))
