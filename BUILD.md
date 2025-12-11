# Building LiteDesk

This guide explains how to build LiteDesk executables for different platforms.

## Quick Build

### Automated Build (Recommended)

The easiest way to build LiteDesk is using the provided build script:

```bash
# Install PyInstaller (if not already installed)
pip install pyinstaller

# Run the build script
python build_all.py
```

This will:
1. Build all three applications (server, client, relay)
2. Create platform-specific directories in `release/`
3. Generate a compressed archive ready for distribution

### Build Output

After building, you'll find:
- **Executables**: `release/{platform}-{arch}/`
- **Archive**: `release/{platform}-{arch}.zip`

Example outputs:
- `release/windows-x64/` - Windows executables
- `release/macos-x64/` - macOS Intel executables
- `release/macos-arm64/` - macOS Apple Silicon executables
- `release/linux-x64/` - Linux x86_64 executables

## Manual Build

If you prefer to build manually:

### Prerequisites

```bash
pip install -r requirements.txt
pip install pyinstaller
```

### Build Individual Applications

#### Server (被控端)
```bash
pyinstaller --clean --noconfirm litedesk_server.spec
```

#### Client (控制端)
```bash
pyinstaller --clean --noconfirm litedesk_client.spec
```

#### Relay Server (中继服务器)
```bash
pyinstaller --clean --noconfirm litedesk_relay.spec
```

The executables will be created in the `dist/` directory.

## Platform-Specific Notes

### Windows

**Requirements:**
- Python 3.7+
- Visual C++ Redistributable (usually included)

**Building:**
```cmd
python build_all.py
```

**Output:**
- `litedesk-server.exe` - Server application
- `litedesk-client.exe` - Client application
- `litedesk-relay.exe` - Relay server

### macOS

**Requirements:**
- Python 3.7+
- Xcode Command Line Tools

**Building:**
```bash
python3 build_all.py
```

**Code Signing (Optional):**
For distribution, you may want to sign the executables:
```bash
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/litedesk-server
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/litedesk-client
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/litedesk-relay
```

**Creating DMG (Optional):**
```bash
# Install create-dmg
brew install create-dmg

# Create DMG
create-dmg \
  --volname "LiteDesk" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --app-drop-link 425 120 \
  "LiteDesk.dmg" \
  "release/macos-x64/"
```

### Linux

**Requirements:**
- Python 3.7+
- X11 development libraries
- Qt5 libraries

**Install system dependencies:**

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y \
  python3-pyqt5 \
  python3-pyqt5.qtsvg \
  libxcb-xinerama0 \
  libxcb-cursor0 \
  libxkbcommon-x11-0
```

**Fedora/RHEL:**
```bash
sudo dnf install -y \
  python3-pyqt5 \
  libxcb \
  xcb-util-wm \
  xcb-util-image \
  xcb-util-keysyms \
  xcb-util-renderutil
```

**Building:**
```bash
python3 build_all.py
```

## GitHub Actions (CI/CD)

LiteDesk includes GitHub Actions workflows for automated building and releasing.

### Automatic Releases

When you push a version tag, GitHub Actions will automatically:
1. Build executables for Windows, macOS, and Linux
2. Create a GitHub Release
3. Upload all executables as release assets

### Creating a Release

```bash
# Tag a new version
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions will automatically build and create a release at:
`https://github.com/h123456001/litedesk/releases`

### Manual Workflow Trigger

You can also manually trigger builds from GitHub:
1. Go to Actions tab
2. Select "Build and Release" workflow
3. Click "Run workflow"

## Troubleshooting

### PyInstaller Not Found

```bash
pip install --upgrade pyinstaller
```

### Missing Dependencies

```bash
pip install -r requirements.txt
```

### Qt Platform Plugin Error (Linux)

If you see "Could not load the Qt platform plugin", install:
```bash
sudo apt-get install libxcb-xinerama0
```

### Import Errors

Make sure all hidden imports are included in the `.spec` files. Common ones:
- `PyQt5.QtCore`
- `PyQt5.QtGui`
- `PyQt5.QtWidgets`
- `mss.linux`, `mss.darwin`, `mss.windows`
- `PIL._imaging`
- `pynput.keyboard`, `pynput.mouse`

### Large Executable Size

To reduce size:
1. Use UPX compression (enabled by default in spec files)
2. Exclude unnecessary modules in `.spec` files
3. Use `--exclude-module` for modules you don't need

### Permission Issues (macOS)

On first run, macOS users need to:
1. Right-click the executable
2. Select "Open"
3. Click "Open" in the security dialog
4. Grant Screen Recording and Accessibility permissions

## Testing Builds

After building, test the executables:

### Server
```bash
./dist/litedesk-server
# Or on Windows:
dist\litedesk-server.exe
```

### Client
```bash
./dist/litedesk-client
# Or on Windows:
dist\litedesk-client.exe
```

### Relay Server
```bash
./dist/litedesk-relay --port 8877
# Or on Windows:
dist\litedesk-relay.exe --port 8877
```

## Distribution

### Creating Installers

For professional distribution, consider creating installers:

**Windows:**
- Use NSIS, Inno Setup, or WiX
- Example: `makensis installer.nsi`

**macOS:**
- Create `.dmg` or `.pkg` files
- Use `create-dmg` or `pkgbuild`

**Linux:**
- Create `.deb` packages: `dpkg-deb --build`
- Create `.rpm` packages: `rpmbuild`
- Use AppImage for universal distribution

## Advanced Configuration

### Custom Icons

To add custom icons, edit the `.spec` files:

```python
exe = EXE(
    ...
    icon='path/to/icon.ico',  # Windows
    # or
    icon='path/to/icon.icns',  # macOS
)
```

### Optimization

For smaller executables and faster startup:

```python
# In .spec file
a = Analysis(
    ...
    excludes=['unittest', 'pydoc', 'doctest'],
    ...
)
```

### Debug Mode

To debug build issues, enable console window temporarily:

```python
exe = EXE(
    ...
    console=True,  # Enable console for debugging
    ...
)
```

## Support

For build issues:
1. Check [GitHub Issues](https://github.com/h123456001/litedesk/issues)
2. Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Check PyInstaller documentation

## License

LiteDesk is released under the MIT License. See [LICENSE](LICENSE) for details.
