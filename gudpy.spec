# -*- mode: python ; coding: utf-8 -*-
SEP = os.path.sep
SUFFIX = ""
if os.name == "nt":
    SUFFIX = ".exe"
block_cipher = None


a = Analysis(['gui/gudpy.py'],
             pathex=['gudrun_classes' + SEP, 'scripts' + SEP, 'widgets' + SEP],
             binaries=[('bin' + SEP + 'gudrun_dcs' + SUFFIX, '.'), ('bin' + SEP + 'calc_corrsx_in_out' + SUFFIX, '.'), ('bin' + SEP + 'purge_det' + SUFFIX, '.'), ('bin' + SEP + 'tophatsub' + SUFFIX, '.')],
             datas=[('bin' + SEP + 'StartupFiles', '.')],
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
          name='gudpy',
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
