# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for HAMIOS v5.5 (PySide6)

import os

block_cipher = None

a = Analysis(
    ['HAMIOS5.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=[
        ('worldmap_eq.jpg',              '.'),
        ('HAMIOS_LOGO.png',              '.'),
        ('hamios.ico',                   '.'),
        ('config',                       'config'),
        ('modules',                      'modules'),
        ('tools',                        'tools'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtNetwork',
        'serial',
        'serial.tools',
        'serial.tools.list_ports',
        'websocket',
        'websocket._core',
        'websocket._http',
        'timezonefinder',
        'zoneinfo',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', 'matplotlib', 'numpy', 'scipy',
        'PIL', 'Pillow', 'cv2', 'pandas',
    ],
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
    name='HAMIOS5',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='hamios.ico',
    version_file=None,
)
