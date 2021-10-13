# -*- mode: python ; coding: utf-8 -*-
VERSION = "0.0.1"
binaries = [(os.path.join("bin", f), '.') for f in os.listdir("bin") if not f == "StartupFiles"]
block_cipher = None

a = Analysis(['main.py'],
             pathex=[os.path.dirname(os.path.abspath('main.py'))],
             binaries=binaries,
             datas=[(os.path.join("bin", "StartupFiles"), "StartupFiles"), (os.path.join("src", "gui", "widgets", "ui_files"), "ui_files"), (os.path.join("src", "gui", "widgets", "resources"), "resources")],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name=f'GudPy-{VERSION}',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )

import sys
if sys.platform == "darwin":
    app = BUNDLE(exe,
                name=f'GudPy-{VERSION}.app')
elif os.name == "nt":
    exe1 = EXE(pyz,
            a.scripts,
            [],
            exclude_binaries=True,
            name=f'GudPy-{VERSION}',
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=True,
            console=True,
            disable_windowed_traceback=False,
            target_arch=None,
            codesign_identity=None,
            entitlements_file=None )
    coll = COLLECT(exe1,
                a.binaries,
                a.zipfiles,
                a.datas, 
                strip=False,
                upx=True,
                upx_exclude=[],
                name=f'GudPy-{VERSION}')
    
