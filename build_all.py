#!/usr/bin/env python3
"""
Build script for creating LiteDesk executables
Supports Windows, macOS, and Linux platforms
"""
import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path


def get_platform_name():
    """Get standardized platform name"""
    system = platform.system().lower()
    if system == 'darwin':
        return 'macos'
    elif system == 'windows':
        return 'windows'
    elif system == 'linux':
        return 'linux'
    else:
        return system


def get_architecture():
    """Get system architecture"""
    machine = platform.machine().lower()
    if machine in ['x86_64', 'amd64']:
        return 'x64'
    elif machine in ['aarch64', 'arm64']:
        return 'arm64'
    elif machine in ['i386', 'i686']:
        return 'x86'
    else:
        return machine


def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} found")
        return True
    except ImportError:
        print("✗ PyInstaller not found")
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
        return True


def build_application(spec_file, app_name):
    """Build a single application using PyInstaller"""
    print(f"\n{'='*60}")
    print(f"Building {app_name}...")
    print(f"{'='*60}")
    
    cmd = ['pyinstaller', '--clean', '--noconfirm', spec_file]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ {app_name} built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to build {app_name}")
        print(f"Error: {e.stderr}")
        return False


def organize_output(platform_name, arch):
    """Organize built executables into platform-specific directories"""
    dist_dir = Path('dist')
    output_dir = Path('release') / f'{platform_name}-{arch}'
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy executables
    executables = {
        'litedesk-server': 'litedesk-server',
        'litedesk-client': 'litedesk-client',
        'litedesk-relay': 'litedesk-relay',
    }
    
    for exe_name, target_name in executables.items():
        if platform_name == 'windows':
            exe_name += '.exe'
            target_name += '.exe'
        
        source = dist_dir / exe_name
        if source.exists():
            dest = output_dir / target_name
            shutil.copy2(source, dest)
            print(f"✓ Copied {exe_name} to {dest}")
        else:
            print(f"⚠ {exe_name} not found in dist directory")
    
    # Copy documentation files - auto-discover markdown files in root
    root_dir = Path('.')
    doc_patterns = ['*.md', 'LICENSE']
    for pattern in doc_patterns:
        for doc_path in root_dir.glob(pattern):
            if doc_path.is_file() and not doc_path.name.startswith('.'):
                shutil.copy2(doc_path, output_dir / doc_path.name)
    
    # Copy vps.ini.example if exists
    vps_example = Path('vps.ini.example')
    if vps_example.exists():
        shutil.copy2(vps_example, output_dir / 'vps.ini.example')
    
    print(f"\n✓ Executables organized in: {output_dir}")
    return output_dir


def create_archive(output_dir):
    """Create a compressed archive of the executables"""
    platform_name = output_dir.name
    archive_base = Path('release') / platform_name
    
    print(f"\nCreating archive for {platform_name}...")
    
    # Create zip archive
    shutil.make_archive(str(archive_base), 'zip', output_dir.parent, output_dir.name)
    archive_path = f"{archive_base}.zip"
    
    print(f"✓ Archive created: {archive_path}")
    return archive_path


def main():
    """Main build process"""
    print("LiteDesk Build System")
    print("=" * 60)
    
    # Get platform info
    platform_name = get_platform_name()
    arch = get_architecture()
    print(f"Platform: {platform_name}")
    print(f"Architecture: {arch}")
    
    # Check PyInstaller
    if not check_pyinstaller():
        print("Failed to install PyInstaller")
        return 1
    
    # Build applications
    specs = [
        ('litedesk_server.spec', 'LiteDesk Server'),
        ('litedesk_client.spec', 'LiteDesk Client'),
        ('litedesk_relay.spec', 'LiteDesk Relay Server'),
    ]
    
    success = True
    for spec_file, app_name in specs:
        if not build_application(spec_file, app_name):
            success = False
    
    if not success:
        print("\n✗ Some builds failed")
        return 1
    
    # Organize output
    output_dir = organize_output(platform_name, arch)
    
    # Create archive
    archive_path = create_archive(output_dir)
    
    print("\n" + "=" * 60)
    print("Build completed successfully!")
    print("=" * 60)
    print(f"Executables: {output_dir}")
    print(f"Archive: {archive_path}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
