"""
HAMIOS v5 — App-directory helper

Geeft de map terug waar alle gebruikersdata (config, cache, history) staat.
ROOT: HAMIOS5 project directory (waar HAMIOS5.py staat)

  • Als Python-script: één niveau omhoog van modules/ naar HAMIOS root
  • Als PyInstaller EXE: de map van de EXE (HAMIOS5.exe)

Gebruik in alle hamios5-modules:
    from ._appdir import APP_DIR
    _CONFIG_FILE = os.path.join(APP_DIR, "config", "hamios_config.json")
"""

import os
import sys

if getattr(sys, 'frozen', False):
    # PyInstaller bundel: HAMIOS5.exe directory is de root
    APP_DIR: str = os.path.dirname(sys.executable)
else:
    # Normaal Python-script: HAMIOS5.py parent directory is de root
    # __file__ = modules/_appdir.py → dirname = modules/ → dirname = HAMIOS/
    APP_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
