"""HAMIOS v5 — Venster-geometrie opslaan/herstellen

Opgeslagen in hamios_layouts.json onder sleutel "__dialogs__".
Gebruik:
    from .geometry import save_geom, restore_geom

    class MyDialog(QDialog):
        def __init__(self):
            ...
            restore_geom(self, "MyDialog")

        def closeEvent(self, event):
            save_geom(self, "MyDialog")
            super().closeEvent(event)
"""

import json
import os

_HERE         = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LAYOUTS_FILE = os.path.join(_HERE, "hamios_layouts.json")


def _load() -> dict:
    try:
        if os.path.exists(_LAYOUTS_FILE):
            with open(_LAYOUTS_FILE, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save(data: dict):
    try:
        with open(_LAYOUTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def save_geom(widget, name: str):
    """Sla de huidige geometrie van een widget op."""
    g    = widget.geometry()
    data = _load()
    dialogs = data.setdefault("__dialogs__", {})
    dialogs[name] = [g.x(), g.y(), g.width(), g.height()]
    _save(data)


def restore_geom(widget, name: str):
    """Herstel eerder opgeslagen geometrie, of gebruik de huidige grootte."""
    data    = _load()
    dialogs = data.get("__dialogs__", {})
    geom    = dialogs.get(name)
    if geom and len(geom) == 4:
        x, y, w, h = geom
        # Zorg dat venster op scherm blijft
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().availableGeometry()
        w = max(widget.minimumWidth(),  min(w, screen.width()))
        h = max(widget.minimumHeight(), min(h, screen.height()))
        x = max(screen.x(), min(x, screen.x() + screen.width()  - w))
        y = max(screen.y() + 30, min(y, screen.y() + screen.height() - h))
        widget.setGeometry(x, y, w, h)
