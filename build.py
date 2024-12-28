import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--name=firefox_bookmark_monitor',
    '--hidden-import=sqlite3',
    '--hidden-import=http.client',
    '--hidden-import=urllib.parse',
    '--hidden-import=pathlib',
    '--hidden-import=re',
    '--hidden-import=plistlib',
    '--clean',
    '--noconfirm'
])
