"""HAMIOS v5 — Venster-geometrie opslaan/herstellen

Opgeslagen in hamios_config.json onder sleutel "dialog_geometries".
Valt terug op hamios_layouts.json voor achterwaartse compatibiliteit.

Gebruik:
    from .geometry import save_geom, restore_geom

    class MyDialog(QDialog):
        def __init__(self):
            restore_geom(self, "MyDialog")

        def closeEvent(self, event):
            save_geom(self, "MyDialog")
            super().closeEvent(event)
"""

import json
import os

from ._appdir import APP_DIR as _HERE

_CONFIG_FILE  = os.path.join(_HERE, "hamios_config.json")
_LAYOUTS_FILE = os.path.join(_HERE, "hamios_layouts.json")   # legacy / panel layouts


# ── Interne helpers ───────────────────────────────────────────────────────────

def _load_cfg() -> dict:
    try:
        if os.path.exists(_CONFIG_FILE):
            with open(_CONFIG_FILE, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_cfg(data: dict):
    try:
        with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ── Publieke API ──────────────────────────────────────────────────────────────

def save_geom(widget, name: str):
    """Sla geometrie op in hamios_config.json → dialog_geometries."""
    g    = widget.geometry()
    data = _load_cfg()
    data.setdefault("dialog_geometries", {})[name] = [
        g.x(), g.y(), g.width(), g.height()
    ]
    _save_cfg(data)


def restore_geom(widget, name: str):
    """Herstel geometrie vanuit hamios_config.json (of legacy layouts-bestand)."""
    # Zoek eerst in config, dan in legacy layouts JSON
    data = _load_cfg()
    geom = data.get("dialog_geometries", {}).get(name)

    if geom is None:
        # Fallback: legacy hamios_layouts.json
        try:
            if os.path.exists(_LAYOUTS_FILE):
                with open(_LAYOUTS_FILE, encoding="utf-8") as f:
                    legacy = json.load(f)
                geom = legacy.get("__dialogs__", {}).get(name)
        except Exception:
            pass

    if geom and len(geom) == 4:
        x, y, w, h = geom
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().availableGeometry()
        w = max(widget.minimumWidth(),  min(w, screen.width()))
        h = max(widget.minimumHeight(), min(h, screen.height()))
        x = max(screen.x(), min(x, screen.x() + screen.width()  - w))
        y = max(screen.y() + 30, min(y, screen.y() + screen.height() - h))
        widget.setGeometry(x, y, w, h)
