"""
HAMIOS v5 — QMainWindow (PySide6)

Sprint 1: fundament, header, desktop-canvas, floating panels.
"""
import sys
import json
import os

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QApplication
)
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QColor, QPalette

from .theme import BG_ROOT, BG_PANEL, PANEL_GRID, QSS
from .header import HeaderBar
from .panel import FloatingPanel

# Pad naar layouts-bestand (gedeeld met v4)
_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LAYOUTS_FILE = os.path.join(_HERE, "hamios_layouts.json")

# Standaard paneel-layout voor v5 (scherm-relatief t.o.v. desktop-canvas)
_PANEL_DEFAULTS = {
    "worldmap":   (440,  0,    740, 490, True),
    "solar":      (1190, 0,    370, 600, True),
    "band_rel":   (0,    0,    430, 600, True),
    "band_cond":  (0,    500,  200, 400, True),
    "storm_fc":   (0,    910,  200, 140, True),
    "band_sched": (440,  500,  370, 290, True),
    "band_hist":  (820,  500,  370, 290, True),
    "solar_hist": (820,  800,  370, 120, True),
    "kp_48h":     (440,  800,  370, 270, True),
    "bz_24h":     (820,  800,  370, 200, True),
    "xray_24h":   (820, 1010,  370, 200, True),
    "lightning":  (1200, 800,  370, 300, True),
    "alerts":     (0,    500,  200, 280, True),
    "dx_spots":   (1200, 610,  370, 460, True),
    "prop_adv":   (0,    610,  430, 460, True),
}

_PANEL_TITLES = {
    "worldmap":   "🌍  Wereldkaart",
    "solar":      "☀  Solar / Ionosfeer",
    "band_rel":   "📶  HF Band Betrouwbaarheid",
    "band_cond":  "📻  Bandcondities",
    "storm_fc":   "🌩  Stormprognose",
    "band_sched": "🗓  Bandopenings-schema",
    "band_hist":  "📈  Band Verloop",
    "solar_hist": "☀  Solar verloop",
    "kp_48h":     "🧲  Kp 48u",
    "bz_24h":     "⚡  Bz 24u (nT)",
    "xray_24h":   "☢  X-straling 24u",
    "lightning":  "⚡  Onweer",
    "alerts":     "🔔  Meldingen",
    "dx_spots":   "📡  Live DX Spots",
    "prop_adv":   "💡  Propagatie Advies",
}


class DesktopCanvas(QWidget):
    """Achtergrond-canvas waarop alle panels als child-widgets leven."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("desktop")
        self.setStyleSheet(f"background: {BG_ROOT};")


class HAMIOSMainWindow(QMainWindow):
    """Hoofdvenster HAMIOS v5."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("HAMIOS v5.0  —  HF Propagation & DX Monitor")
        self.setMinimumSize(900, 600)
        self.resize(1600, 900)

        # Stylesheet
        QApplication.instance().setStyleSheet(QSS)

        # Header bovenaan
        self._header = HeaderBar()
        self._header.btn_exit.clicked.connect(self.close)
        self._header.btn_fullscreen.clicked.connect(self._toggle_fullscreen)

        # Desktop-canvas voor panels
        self._desktop = DesktopCanvas()

        # Hoofdlayout: header + desktop
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._header)
        layout.addWidget(self._desktop, 1)
        self.setCentralWidget(container)

        # Panels aanmaken
        self._panels: dict[str, FloatingPanel] = {}
        self._build_panels()

        # Layout laden
        self._load_layout()

    # ── Panels ────────────────────────────────────────────────────────────────
    def _build_panels(self):
        """Maak alle panels aan als kind-widgets van _desktop."""
        for pid, title in _PANEL_TITLES.items():
            p = FloatingPanel(title, panel_id=pid, parent=self._desktop)
            p.hide()  # eerst verbergen, positie zetten via _load_layout
            self._panels[pid] = p

            # Placeholder content (Sprint 1)
            self._build_placeholder(p, pid)

    def _build_placeholder(self, panel: FloatingPanel, pid: str):
        """Tijdelijke lege content — wordt vervangen in latere sprints."""
        from PySide6.QtWidgets import QLabel
        lbl = QLabel(f"[ {pid} ]")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(f"color: #404850; font-size: 10pt;")
        from PySide6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(panel.content)
        layout.addWidget(lbl)

    # ── Layout opslaan/laden ──────────────────────────────────────────────────
    def _load_layout(self):
        """Laad panel-layout uit hamios_layouts.json of gebruik defaults."""
        saved = {}
        try:
            if os.path.exists(_LAYOUTS_FILE):
                with open(_LAYOUTS_FILE, encoding="utf-8") as f:
                    data = json.load(f)
                if "__default__" in data:
                    saved = data["__default__"]
        except Exception:
            pass

        for pid, p in self._panels.items():
            if pid in saved and len(saved[pid]) >= 5:
                x, y, w, h, vis = saved[pid][:5]
            elif pid in _PANEL_DEFAULTS:
                x, y, w, h, vis = _PANEL_DEFAULTS[pid]
            else:
                continue
            p.setGeometry(int(x), int(y), int(w), int(h))
            if vis:
                p.show_panel()
            else:
                p.hide_panel()

    def save_layout(self):
        """Sla huidige panel-layout op als __default__."""
        layout = {}
        for pid, p in self._panels.items():
            g = p.geometry()
            layout[pid] = [g.x(), g.y(), g.width(), g.height(),
                           p.is_panel_visible()]
        layout["__window__"] = [
            self.x(), self.y(), self.width(), self.height()
        ]
        try:
            data = {}
            if os.path.exists(_LAYOUTS_FILE):
                with open(_LAYOUTS_FILE, encoding="utf-8") as f:
                    data = json.load(f)
            data["__default__"] = layout
            with open(_LAYOUTS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Layout save failed: {e}")

    # ── Overige ───────────────────────────────────────────────────────────────
    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self._header.btn_fullscreen.setText("⛶")
        else:
            self.showFullScreen()
            self._header.btn_fullscreen.setText("⊡")

    def closeEvent(self, event):
        self.save_layout()
        super().closeEvent(event)
