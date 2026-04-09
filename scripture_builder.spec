# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['launch.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('sermon_parser.py', '.'),
        ('generator.py', '.'),
    ],
    hiddenimports=[
        'flask',
        'werkzeug',
        'docx',
        'jinja2',
        'click',
        'rumps',
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
    name='Scripture Builder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Scripture Builder',
)

app = BUNDLE(
    coll,
    name='Scripture Builder.app',
    icon=None,
    bundle_identifier='com.yourchurch.scripturebuilder',
    info_plist={
        'NSHighResolutionCapable': True,
        'LSBackgroundOnly': False,
        'LSUIElement': True,
    },
)