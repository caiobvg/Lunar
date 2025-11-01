# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['run.py'],
    pathex=[current_dir],
    binaries=[],
    datas=[
        ('firebase-key.json', '.'),  # Include Firebase key file
        ('app.ico', '.'),  # Include icon file
        ('src', 'src'),  # Include entire src directory
        ('license', 'license'),  # Include license directory
    ],
    hiddenimports=[
        'firebase_admin',
        'firebase_admin.credentials',
        'firebase_admin.firestore',
        'firebase_admin.auth',
        'customtkinter',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'ctypes',
        'ctypes.windll',
        'ctypes.windll.shell32',
        'tkinter.messagebox',
        'tkinter.ttk',
        'psutil',
        'colorama',
        'pybind11',
        'wmi',
        'requests',
        'json',
        'os',
        'sys',
        'hashlib',
        'secrets',
        'datetime',
        'typing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MidnightSpoofer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Hide console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app.ico',
    version_file='version_info.txt',  # Add version information
)
