# -*- mode: python ; coding: utf-8 -*-
VERSION = "0.3.3"
binaries = [
    (os.path.join("bin", f), '.')
    for f in os.listdir("bin")
    if f not in ["StartupFiles", "configs"]
]
block_cipher = None
import sys

main = 'gudpy/__main__.py'
pathex = [main, 'gudpy']
data = [(os.path.join("bin", "StartupFiles"), os.path.join("bin", "StartupFiles")), (os.path.join("bin", "configs"), os.path.join("bin", "configs"))]
ui = [(os.path.join("gudpy", "gui", "widgets", "ui_files"), "ui_files"), (os.path.join("gudpy", "gui", "widgets", "resources"), "resources")]
datas = [*data, *ui]

if sys.platform == "darwin":
    a = Analysis([main],
                pathex=pathex,
                binaries=binaries,
                datas=datas,
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
else:
    a = Analysis([main],
                pathex=pathex,
                binaries=binaries,
                datas=datas,
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
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )

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
            console=False,
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
    
