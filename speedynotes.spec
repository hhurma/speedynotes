# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# qtawesome font ve icon dosyalarını topla
qtawesome_datas = collect_data_files('qtawesome')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('resources', 'resources'),
        ('icon.ico', '.'),
        ('icon.png', '.'),
        ('README.md', '.'),
    ] + qtawesome_datas,
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtPrintSupport',
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtWebEngineCore',
        'gui.css_highlighter',
        'gui.first_run_wizard',
        'gui.html_highlighter',
        'gui.main_gui',
        'gui.python_highlighter',
        'helpers.config_helper',
        'helpers.note_memory_helper',
        'helpers.translate_helper',
        'utils.logger',
        'qtawesome',
        'qtpy',
        'qtpy.QtCore',
        'qtpy.QtGui',
        'qtpy.QtWidgets',
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
    [],
    exclude_binaries=True,
    name='speedynotes',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='speedynotes',
)