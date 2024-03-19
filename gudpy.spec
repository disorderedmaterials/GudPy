# -*- mode: python ; coding: utf-8 -*-
VERSION = "0.5.0"
binaries = [
    (os.path.join("bin", f), '.')
    for f in os.listdir("bin")
    if f not in ["StartupFiles", "configs"]
]
block_cipher = None
import sys

main_cli = os.path.join('gudpy', 'gudpy_cli.py')
main_gui = os.path.join('gudpy', 'gudpy_gui.py')
data = [(os.path.join("bin", "StartupFiles"), os.path.join("bin", "StartupFiles")), (os.path.join("bin", "configs"), os.path.join("bin", "configs"))]
ui = [(os.path.join("gudpy", "gui", "widgets", "ui_files"), "ui_files"), (os.path.join("gudpy", "gui", "widgets", "resources"), "resources")]
datas = [*data, *ui]

a_cli = Analysis([main_cli],
             pathex=[main_cli, 'gudpy'],
             binaries=[],
             datas=data,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['gui'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

a_gui = Analysis([main_gui],
                 pathex=[main_gui, 'gudpy'],
                 binaries=[],
                 datas=datas,
                 hiddenimports=[],
                 hookspath=[],
                 runtime_hooks=[],
                 excludes=[],
                 win_no_prefer_redirects=False,
                 win_private_assemblies=False,
                 cipher=block_cipher,
                 noarchive=False)

pyz_cli = PYZ(a_cli.pure, a_cli.zipped_data,
             cipher=block_cipher)

pyz_gui = PYZ(a_gui.pure, a_gui.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz_cli,
          a_cli.scripts,
          [],
          exclude_binaries=True,
          name='cli',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )

gui_exe = EXE(pyz_gui,
              a_gui.scripts,
              [],
              exclude_binaries=True,
              name='gui',
              debug=False,
              bootloader_ignore_signals=False,
              strip=False,
              upx=True,
              console=False )

coll = COLLECT(exe,
               a_cli.binaries,
               a_cli.zipfiles,
               a_cli.datas,
               strip=False,
               upx=True,
               name='gudpy')

# Now bundle everything in one folder
app = BUNDLE(coll,
             name='gudpy.app',
             icon=None,
             bundle_identifier=None)