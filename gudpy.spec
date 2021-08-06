# -*- mode: python ; coding: utf-8 -*-
SEP = os.path.sep

block_cipher = None


a = Analysis(['gui/gudpy.py'],
             pathex=['gudrun_classes' + SEP, 'scripts' + SEP, 'widgets' + SEP],
             binaries=[('bin' + SEP + 'gudrun_dcs', '.'), ('bin' + SEP + 'calc_corrsx_in_out', '.'), ('bin' + SEP + 'purge_det', '.'), ('bin' + SEP + 'tophatsub', '.')],
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
          [],
          exclude_binaries=True,
          name='gudpy',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='gudpy')
