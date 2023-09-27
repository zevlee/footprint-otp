# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
	['../footprintotp.py'],
	pathex=[],
	binaries=[],
	datas=[
		('../gui', 'gui'),
		('../footprintotp', 'footprintotp'),
		('../me.zevlee.FootprintOTP.svg', '.'),
		('../LICENSE', '.'),
		('../VERSION', '.'),
		('footprint-otp.desktop', '.'),
		('icons', 'usr/share/icons')
	],
	hooksconfig={
		'gi': {
			'icons': ['Adwaita'],
			'themes': ['Adwaita'],
			'module-versions': {
				'Gtk': '4.0'
			}
		}
	},
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
	a.binaries,
	a.zipfiles,
	a.datas,
	[],
	name='footprint-otp',
	debug=False,
	bootloader_ignore_signals=False,
	strip=False,
	upx=True,
	upx_exclude=[],
	console=False
)
