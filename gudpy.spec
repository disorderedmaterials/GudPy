# -*- mode: python ; coding: utf-8 -*-
VERSION = "0.0.1"
binaries = [(os.path.join("bin", f), '.') for f in os.listdir("bin") if not f == "StartupFiles"]
print(binaries)
block_cipher = None
import sys

a = Analysis(['main.py'],
             pathex=[os.path.dirname(os.path.abspath('main.py'))],
             binaries=binaries,
             datas=[(os.path.join("bin", "StartupFiles"), "StartupFiles")],
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

if sys.platform == "darwin":
    app = BUNDLE(exe,
                name=f'GudPy-{VERSION}.app')