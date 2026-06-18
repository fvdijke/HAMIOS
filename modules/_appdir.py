"""
HAMIOS v5 — App-directory helper

Geeft de map terug waar alle gebruikersdata (config, cache, history) staat.

  • Als Python-script: één niveau omhoog van modules/ naar HAMIOS root
  • Als PyInstaller EXE:
    - Probeer map van de EXE (HAMIOS5.exe)
    - Fallback naar %LOCALAPPDATA%\HAMIOS als geen write-rechten

Gebruik in alle hamios5-modules:
    from ._appdir import APP_DIR
    _CONFIG_FILE = os.path.join(APP_DIR, "config", "hamios_config.json")
"""

import os
import sys

def _get_app_dir() -> str:
    """Bepaal app directory met fallback voor restrictieve permissions."""
    if getattr(sys, 'frozen', False):
        # PyInstaller exe: probeer eerst exe-directory
        exe_dir = os.path.dirname(sys.executable)
        try:
            # Test write-rechten: kan je een bestand aanmaken?
            test_file = os.path.join(exe_dir, ".hamios_write_test")
            open(test_file, 'w').close()
            os.remove(test_file)
            return exe_dir
        except (OSError, IOError, PermissionError):
            # Geen write-rechten in exe-dir, gebruik AppData
            return os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'HAMIOS')
    else:
        # Python script: HAMIOS5.py parent directory is de root
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APP_DIR: str = _get_app_dir()
