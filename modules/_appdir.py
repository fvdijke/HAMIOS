"""
HAMIOS v5 — App-directory helper

Geeft de map terug waar alle gebruikersdata (config, cache, history) staat.

  • Als Python-script: één niveau omhoog van hamios5/ naar HAMIOS5 root
  • Als PyInstaller EXE: %LOCALAPPDATA%\HAMIOS (Windows app data dir)

Gebruik in alle hamios5-modules:
    from ._appdir import APP_DIR
    _CONFIG_FILE = os.path.join(APP_DIR, "config", "hamios_config.json")
"""

import os
import sys

if getattr(sys, 'frozen', False):
    # PyInstaller exe: use user's AppData\Local directory for config
    APP_DIR: str = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'HAMIOS')
else:
    # Python script: HAMIOS5.py parent directory is de root
    # __file__ = modules/_appdir.py → dirname = modules/ → dirname = HAMIOS/
    APP_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
