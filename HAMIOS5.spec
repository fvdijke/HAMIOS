# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for HAMIOS (PySide6) — version: modules/version.py

import os

from PyInstaller.utils.hooks import copy_metadata

block_cipher = None

a = Analysis(
    ['HAMIOS5.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=[
        ('worldmap_eq.jpg',              '.'),
        ('HAMIOS_LOGO.png',              '.'),
        ('hamios.ico',                   '.'),
        ('config/hamios_resources_defaults.json', 'config'),
        ('config/hamios_resources.json',          'config'),
        ('modules',                      'modules'),
        ('tools',                        'tools'),
    # h3 (via timezonefinder) leest bij import zijn eigen pakketversie
    ] + copy_metadata('h3') + copy_metadata('timezonefinder'),
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
        'h3',
        'cffi',
        'zoneinfo',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # numpy NIET uitsluiten: timezonefinder (lokale tijdzone van de QTH) heeft
    # numpy, h3 en cffi nodig — zonder numpy viel de klok terug op de pc-tijdzone
    excludes=[
        'tkinter', 'matplotlib', 'scipy',
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
