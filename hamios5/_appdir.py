"""
HAMIOS v5 — App-directory helper

Geeft de map terug waar alle gebruikersdata (config, cache, history) staat.

  • Als Python-script : twee niveaus omhoog van dit bestand (de HAMIOS5/-map)
  • Als PyInstaller EXE: de map van de EXE (sys.executable)

Gebruik in alle hamios5-modules:
    from ._appdir import APP_DIR
    _CONFIG_FILE = os.path.join(APP_DIR, "hamios_config.json")
"""

import os
import sys

if getattr(sys, 'frozen', False):
    # PyInstaller bundel: schrijf data naast de EXE
    APP_DIR: str = os.path.dirname(sys.executable)
else:
    # Normaal Python-script
    APP_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
