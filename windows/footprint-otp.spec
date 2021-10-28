# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
	['../footprint-otp'],
	pathex=[],
	binaries=[],
	datas=[
		('../lib/__init__.py', 'lib'),
		('../lib/footprint_otp.py', 'lib'),
		('../lib/otp.py', 'lib'),
		('../gui/menu.xml', 'gui'),
		('../footprint-otp.svg', '.'),
		('../LICENSE', '.'),
		('../VERSION', '.')
  ],
  hiddenimports=[],
  hookspath=[],
  runtime_hooks=[],
  excludes=[],
  win_no_prefer_redirects=False,
  win_private_assemblies=False,
  cipher=block_cipher,
  noarchive=False
)

pyz = PYZ(
	a.pure,
	a.zipped_data,
	cipher=block_cipher
)

exe = EXE(
	pyz,
	a.scripts,
	[],
	exclude_binaries=True,
	name='footprint-otp',
	icon='footprint-otp.ico',
	debug=False,
	bootloader_ignore_signals=False,
	strip=False,
	upx=True,
	console=False
)

coll = COLLECT(
	exe,
	a.binaries,
	a.zipfiles,
	a.datas,
	strip=False,
	upx=True,
	upx_exclude=[],
	name='footprint-otp'
)
