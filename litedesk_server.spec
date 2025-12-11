# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for LiteDesk Server (被控端)
Builds executable for the controlled/host machine
"""

block_cipher = None

a = Analysis(
    ['server.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'mss',
        'mss.linux',
        'mss.darwin',
        'mss.windows',
        'PIL',
        'PIL._imaging',
        'pynput',
        'pynput.keyboard',
        'pynput.mouse',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='litedesk-server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # UPX compression reduces file size but may trigger false positives in some antivirus software
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application, no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file path if available
)
