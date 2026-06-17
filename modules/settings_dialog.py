"""HAMIOS v5 — Instellingen-dialoog (PySide6 QDialog)"""

import json
import math
import os
import subprocess
import sys
from dataclasses import asdict

# Pad naar het layouts-bestand
from ._appdir import APP_DIR as _HERE
from .profiel_manager import ProfileManager

# Legacy layouts-bestand (nog steeds gelezen voor achterwaartse compatibiliteit)
_LAYOUTS_FILE = os.path.join(_HERE, "config", "hamios_layouts.json")
_CONFIG_FILE  = os.path.join(_HERE, "config", "hamios_config.json")


def _load_layouts() -> dict:
    """Laad layouts — eerst uit config, dan uit legacy JSON."""
    # Primair: hamios_config.json → "layouts"
    try:
        if os.path.exists(_CONFIG_FILE):
            with open(_CONFIG_FILE, encoding="utf-8") as f:
                data = json.load(f)
            if data.get("layouts"):
                return data["layouts"]
    except Exception:
        pass
    # Fallback: legacy hamios_layouts.json
    try:
        if os.path.exists(_LAYOUTS_FILE):
            with open(_LAYOUTS_FILE, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_layouts(layouts: dict):
    """Sla layouts op in hamios_config.json → 'layouts' EN legacy JSON."""
    # Primair: config
    try:
        data = {}
        if os.path.exists(_CONFIG_FILE):
            with open(_CONFIG_FILE, encoding="utf-8") as f:
                data = json.load(f)
        data["layouts"] = layouts
        with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    # Secundair: legacy (voor v4-tools en scripts die het nog lezen)
    try:
        with open(_LAYOUTS_FILE, "w", encoding="utf-8") as f:
            json.dump(layouts, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
    QPushButton, QTabWidget, QWidget, QFrame,
    QCheckBox, QComboBox, QScrollArea
)

from .theme import ACCENT, BG_PANEL, BG_SURFACE, BG_ROOT, TEXT_H1, TEXT_DIM, BORDER, make_checkmark_path
from .config import AppConfig, save_config
from .cat_interface import CatInterface, serial_available, get_instance
from .i18n import tr

# ── Stylesheet constants ──────────────────────────────────────────────────────
_STYLE_STATUS_OK = "color: #4CAF50; font-size: 8pt;"
_STYLE_STATUS_ERR = "color: #EF5350; font-size: 8pt;"
_STYLE_STATUS_DIM = f"color: {TEXT_DIM}; font-size: 7pt;"
_STYLE_LABEL_DIM = f"color: {TEXT_DIM}; font-size: 8pt;"
_STYLE_LABEL_DIM_SMALL = f"color: {TEXT_DIM}; font-size: 7pt; font-style: italic;"
_STYLE_ERR_DIM = "color: #EF5350; font-size: 7pt;"
_STYLE_OK_NO_SIZE = "color: #4CAF50;"
_STYLE_ERR_NO_SIZE = "color: #EF5350;"

_MODES    = ["SSB", "CW", "FT8", "FT4", "WSPR", "AM", "FM", "PSK31", "RTTY"]
_POWERS   = ["5W", "10W", "25W", "50W", "100W", "200W", "400W", "1kW", "1.5kW"]
_ANTENNAS = [
    "Isotropic 0dBi", "Magnetic loop", "Ground loop", "Vertical",
    "Groundplane", "Inverted V", "Dipole ~2dBi", "EFHW", "OCFD",
    "J-pole", "Long wire", "Delta loop ~3dBi", "Quad ~8dBi",
    "Yagi ~7dBi", "Beam ~10dBi", "Stack 2×Yagi",
]
_GRIDS = [1, 5, 10, 20, 50]

# ── Maidenhead ────────────────────────────────────────────────────────────────

def latlon_to_locator(lat: float, lon: float) -> str:
    lon += 180; lat += 90
    loc  = chr(ord('A') + int(lon / 20))
    loc += chr(ord('A') + int(lat / 10))
    loc += str(int((lon % 20) / 2))
    loc += str(int(lat % 10))
    loc += chr(ord('A') + int((lon % 2) / (2 / 24)))
    loc += chr(ord('A') + int((lat % 1) / (1 / 24)))
    return loc.upper()


def locator_to_latlon(loc: str):
    loc = loc.strip().upper()
    if len(loc) < 4:
        return None
    try:
        lon = (ord(loc[0]) - ord('A')) * 20 - 180
        lat = (ord(loc[1]) - ord('A')) * 10 - 90
        lon += int(loc[2]) * 2
        lat += int(loc[3]) * 1
        if len(loc) >= 6:
            lon += (ord(loc[4]) - ord('A')) * 2 / 24
            lat += (ord(loc[5]) - ord('A')) * 1 / 24
        return round(lat + 0.5, 4), round(lon + 1.0, 4)
    except Exception:
        return None


# ── Stylesheet ────────────────────────────────────────────────────────────────

_QSS = f"""
QDialog {{ background: {BG_PANEL}; }}
QTabWidget::pane {{ background: {BG_SURFACE}; border: 1px solid {BORDER}; }}
QTabBar::tab {{
    background: {BG_PANEL}; color: {TEXT_DIM};
    padding: 5px 14px; border: none; min-width: 70px;
}}
QTabBar::tab:selected {{ background: {BG_SURFACE}; color: {ACCENT};
    border-bottom: 2px solid {ACCENT}; }}

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background: {BG_ROOT}; color: {TEXT_H1};
    border: 1px solid {BORDER}; padding: 3px 6px;
}}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border: 1px solid {ACCENT};
}}

QLabel {{ color: {TEXT_DIM}; background: transparent; }}
QPushButton {{
    background: {BG_SURFACE}; color: {TEXT_H1};
    border: 1px solid {BORDER}; padding: 4px 14px; border-radius: 3px;
    min-width: 80px;
}}
QPushButton:hover  {{ background: #32373F; border-color: {ACCENT}; }}
QPushButton:pressed {{ background: {ACCENT}; color: {BG_ROOT}; border-color: {ACCENT}; }}
QPushButton#ok {{
    background: {ACCENT}; color: {BG_ROOT};
    font-weight: bold; border-color: {ACCENT};
}}
QPushButton#ok:hover   {{ background: #E0C060; }}
QPushButton#ok:pressed {{ background: #A88030; }}
QPushButton#cancel {{
    background: {BG_PANEL}; color: {TEXT_DIM};
    border: 1px solid {BORDER};
}}
QPushButton#cancel:hover   {{ background: #32373F; color: {TEXT_H1}; }}
QPushButton#cancel:pressed {{ background: #EF5350; color: white; border-color: #EF5350; }}
QPushButton#danger {{ background: #5A1010; color: {TEXT_H1}; border-color: #8B1A1A; }}
QPushButton#danger:hover   {{ background: #8B1A1A; }}
QPushButton#danger:pressed {{ background: #EF5350; }}
QScrollArea {{ border: none; background: transparent; }}
"""


# ── Checkmark helper ─────────────────────────────────────────────────────────

# make_checkmark_path is now imported from theme


# ── Helpers ───────────────────────────────────────────────────────────────────

def _section(parent_layout: QVBoxLayout, title: str):
    """Sectieheader met amber accent."""
    sep = QFrame()
    sep.setFrameShape(QFrame.HLine)
    sep.setStyleSheet(f"background: {BORDER}; max-height: 1px;")
    parent_layout.addWidget(sep)
    lbl = QLabel(title)
    lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
    lbl.setStyleSheet(f"color: {ACCENT}; padding-top: 4px;")
    parent_layout.addWidget(lbl)


def _tab_scroll(content: QWidget) -> QScrollArea:
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(content)
    return scroll


# ── Dialoog ───────────────────────────────────────────────────────────────────

class SettingsDialog(QDialog):
    """Instellingen-dialoog met tabbladen."""

    applied = Signal(AppConfig)

    def __init__(self, cfg: AppConfig, panels: dict = None,
                 mainwindow=None, parent=None):
        super().__init__(parent)
        self._cfg          = cfg
        self._original_cfg = None      # voor Annuleren
        self._panels       = panels or {}
        self._mainwin      = mainwindow
        self._loading      = False     # blokkeert live-apply tijdens _load_cfg
        # Debounce-timer voor zware operaties (spinboxen)
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.timeout.connect(self._do_apply)
        self.setWindowTitle(tr("set.title"))
        self.setMinimumSize(480, 480)
        _check_path = make_checkmark_path()
        dialog_qss  = _QSS.replace(
            "image: url(CHECKMARK_PLACEHOLDER)",
            f'image: url("{_check_path}")')
        self.setStyleSheet(dialog_qss)
        self._build_ui()
        # Bewaar originele cfg voor Annuleren
        import dataclasses as _dc
        self._original_cfg = _dc.replace(cfg)
        self._load_cfg()

    # ── UI bouw ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(8)

        self._tabs = QTabWidget()
        outer.addWidget(self._tabs, 1)

        self._tabs.addTab(self._tab_station(),   tr("set.tab.station.lbl"))
        self._tabs.addTab(self._tab_map(),       tr("set.tab.map.lbl"))
        self._tabs.addTab(self._tab_lightning(), tr("set.tab.lightn.lbl"))
        self._tabs.addTab(self._tab_alerts(),    tr("set.tab.alerts.lbl"))
        self._tabs.addTab(self._tab_cat(),       tr("set.tab.cat.lbl"))
        self._tabs.addTab(self._tab_resources(), tr("set.tab.resources.lbl"))
        self._tabs.addTab(self._tab_layout(),    tr("set.tab.layout.lbl"))
        self._tabs.addTab(self._tab_about(),     tr("set.tab.about.lbl"))

        # Status-label voor feedback
        self._status_lbl = QLabel("")
        self._status_lbl.setStyleSheet(_STYLE_STATUS_OK)
        self._status_timer = QTimer(self)
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(lambda: self._status_lbl.setText(""))

        # Knoppen (geen Toepassen — alles is live)
        btn_row = QHBoxLayout()
        btn_row.addWidget(self._status_lbl)
        btn_row.addStretch()
        self._btn_ok     = QPushButton(tr("app.close_btn")); self._btn_ok.setObjectName("ok")
        self._btn_cancel = QPushButton(tr("app.cancel"));    self._btn_cancel.setObjectName("cancel")
        for b in [self._btn_cancel, self._btn_ok]:
            b.setMinimumWidth(90)
            btn_row.addWidget(b)
        outer.addLayout(btn_row)

        self._btn_ok.clicked.connect(self._on_ok)
        self._btn_cancel.clicked.connect(self._on_cancel)

        # Stel breedte in na het bouwen van alle tabs
        from PySide6.QtCore import QTimer as _QT
        _QT.singleShot(0, self._fit_to_tabs)

    # ── Tab: Station ──────────────────────────────────────────────────────────
    def _tab_station(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(12, 8, 12, 8)
        v.setSpacing(4)

        def row(lbl, widget):
            h = QHBoxLayout()
            l = QLabel(lbl)
            l.setFixedWidth(130)
            h.addWidget(l)
            h.addWidget(widget, 1)
            v.addLayout(h)

        _section(v, tr("sec.qth"))

        self._call_edit = QLineEdit()
        self._call_edit.setPlaceholderText("AB1CD")
        row(tr("set.station.call_lbl"), self._call_edit)

        self._loc_edit = QLineEdit()
        self._loc_edit.setPlaceholderText("JO22NC")
        self._loc_edit.editingFinished.connect(self._locator_to_latlon)
        row(tr("set.station.loc_lbl"), self._loc_edit)

        self._lat_spin = QDoubleSpinBox()
        self._lat_spin.setRange(-90, 90); self._lat_spin.setDecimals(4)
        self._lat_spin.valueChanged.connect(self._latlon_to_locator)
        row("Latitude (°N):", self._lat_spin)

        self._lon_spin = QDoubleSpinBox()
        self._lon_spin.setRange(-180, 180); self._lon_spin.setDecimals(4)
        self._lon_spin.valueChanged.connect(self._latlon_to_locator)
        row("Longitude (°E):", self._lon_spin)

        _section(v, tr("sec.setup"))

        self._mode_cb = QComboBox()
        self._mode_cb.addItems(_MODES)
        row("Modus:", self._mode_cb)

        self._power_cb = QComboBox()
        self._power_cb.addItems(_POWERS)
        row("Vermogen:", self._power_cb)

        self._ant_cb = QComboBox()
        self._ant_cb.addItems(_ANTENNAS)
        row("Antenne:", self._ant_cb)

        self._day_auto_cb = QCheckBox(tr("day_auto_cb"))
        self._day_auto_cb.setToolTip(tr("tip.day_auto"))
        v.addWidget(self._day_auto_cb)

        v.addStretch()
        return w

    # ── Tab: Kaart ────────────────────────────────────────────────────────────
    def _tab_map(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(12, 8, 12, 8)
        v.setSpacing(4)

        # Overlay-knoppen zijn verplaatst naar de header (🗺 Overlays popup).
        # Widgets blijven bestaan zodat _load_cfg / _collect_cfg werken.
        self._cb_night    = QCheckBox(); self._cb_night.hide()
        self._cb_grayline = QCheckBox(); self._cb_grayline.hide()
        self._cb_aurora   = QCheckBox(); self._cb_aurora.hide()
        self._cb_sun      = QCheckBox(); self._cb_sun.hide()
        self._cb_moon     = QCheckBox(); self._cb_moon.hide()
        self._cb_lightn   = QCheckBox(); self._cb_lightn.hide()
        self._cb_dxspots  = QCheckBox(); self._cb_dxspots.hide()
        self._cb_locator  = QCheckBox(); self._cb_locator.hide()

        note_ov = QLabel(tr("overlay_note"))
        note_ov.setStyleSheet(f"color: {TEXT_DIM}; font-size: 7pt; font-style: italic;")
        v.addWidget(note_ov)

        def row(lbl, widget):
            h = QHBoxLayout()
            l = QLabel(lbl); l.setFixedWidth(160)
            h.addWidget(l)
            h.addWidget(widget)
            h.addStretch()
            v.addLayout(h)

        _section(v, tr("sec.grat"))

        self._grat_step_cb = QComboBox()
        for lbl, val in [("10°", 10), ("20°", 20), ("30°", 30)]:
            self._grat_step_cb.addItem(lbl, val)
        row(tr("set.map.grat_step"), self._grat_step_cb)

        _section(v, tr("sec.overlay_fonts2"))

        self._font_spin = QSpinBox()
        self._font_spin.setRange(6, 72)
        self._font_spin.setSuffix(" pt")
        self._font_spin.setFixedWidth(80)
        row(tr("set.map.font_grat"), self._font_spin)

        self._maid_font_spin = QSpinBox()
        self._maid_font_spin.setRange(6, 72)
        self._maid_font_spin.setSuffix(" pt")
        self._maid_font_spin.setFixedWidth(80)
        row(tr("set.map.font_maid"), self._maid_font_spin)

        self._sat_font_spin = QSpinBox()
        self._sat_font_spin.setRange(6, 72)
        self._sat_font_spin.setSuffix(" pt")
        self._sat_font_spin.setFixedWidth(80)
        row(tr("set.map.font_sat"), self._sat_font_spin)

        self._sat_path_width_spin = QDoubleSpinBox()
        self._sat_path_width_spin.setRange(0.3, 6.0)
        self._sat_path_width_spin.setSingleStep(0.1)
        self._sat_path_width_spin.setDecimals(1)
        self._sat_path_width_spin.setSuffix(" px")
        self._sat_path_width_spin.setFixedWidth(80)
        row(tr("set.map.path_width"), self._sat_path_width_spin)

        self._callsign_font_spin = QSpinBox()
        self._callsign_font_spin.setRange(5, 72)
        self._callsign_font_spin.setSuffix(" pt")
        self._callsign_font_spin.setFixedWidth(80)
        row(tr("set.map.font_callsign"), self._callsign_font_spin)

        self._dx_map_font_spin = QSpinBox()
        self._dx_map_font_spin.setRange(6, 72)
        self._dx_map_font_spin.setSuffix(" pt")
        self._dx_map_font_spin.setFixedWidth(80)
        row(tr("set.map.font_dx_map"), self._dx_map_font_spin)

        self._dx_font_spin = QSpinBox()
        self._dx_font_spin.setRange(6, 72)
        self._dx_font_spin.setSuffix(" pt")
        self._dx_font_spin.setFixedWidth(80)
        row(tr("set.map.font_dx_tbl"), self._dx_font_spin)

        _section(v, tr("sec.icon_sizes2"))

        self._sun_size_spin = QSpinBox()
        self._sun_size_spin.setRange(8, 64)
        self._sun_size_spin.setSuffix(" px")
        self._sun_size_spin.setFixedWidth(80)
        row(tr("set.map.sun_size"), self._sun_size_spin)

        self._moon_size_spin = QSpinBox()
        self._moon_size_spin.setRange(8, 64)
        self._moon_size_spin.setSuffix(" px")
        self._moon_size_spin.setFixedWidth(80)
        row(tr("set.map.moon_size"), self._moon_size_spin)

        v.addStretch()
        return w

    # ── Tab: Bliksem ─────────────────────────────────────────────────────────
    def _tab_lightning(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(12, 8, 12, 8)
        v.setSpacing(4)

        _section(v, tr("sec.lightn_blitz"))

        # Enable checkbox + status
        h_en = QHBoxLayout()
        self._cb_lightn_en = QCheckBox(tr("set.lightn.enable"))
        self._cb_lightn_en.setToolTip(tr("tip.lightn.en"))
        h_en.addWidget(self._cb_lightn_en)

        self._lightn_status = QLabel("")
        self._lightn_status.setFont(QFont("Segoe UI", 8))
        self._lightn_status.setStyleSheet(f"color: {TEXT_DIM};")
        h_en.addWidget(self._lightn_status)
        h_en.addStretch()

        # Connect checkbox to status updates
        self._cb_lightn_en.toggled.connect(self._update_lightn_status)

        v.addLayout(h_en)

        h = QHBoxLayout()
        h.addWidget(QLabel(tr("set.lightn.fade")))
        self._fade_spin = QSpinBox()
        self._fade_spin.setRange(30, 3600)
        self._fade_spin.setSingleStep(30)
        self._fade_spin.setFixedWidth(80)
        h.addWidget(self._fade_spin)
        h.addStretch()
        v.addLayout(h)

        _section(v, "Alert")
        h2 = QHBoxLayout()
        h2.addWidget(QLabel(tr("set.lightn.alert")))
        self._lightn_radius_spin = QSpinBox()
        self._lightn_radius_spin.setRange(0, 5000)
        self._lightn_radius_spin.setSingleStep(50)
        self._lightn_radius_spin.setFixedWidth(80)
        self._lightn_radius_spin.setToolTip(tr("tip.lightn.radius"))
        h2.addWidget(self._lightn_radius_spin)
        h2.addStretch()
        v.addLayout(h2)

        # Alert sound pitch
        h_pitch = QHBoxLayout()
        h_pitch.addWidget(QLabel("Sound pitch (Hz):"))
        self._lightn_pitch_spin = QSpinBox()
        self._lightn_pitch_spin.setRange(1000, 8000)
        self._lightn_pitch_spin.setSingleStep(100)
        self._lightn_pitch_spin.setFixedWidth(80)
        h_pitch.addWidget(self._lightn_pitch_spin)
        h_pitch.addStretch()
        v.addLayout(h_pitch)

        # Alert sound duration
        h_duration = QHBoxLayout()
        h_duration.addWidget(QLabel("Sound duration (ms):"))
        self._lightn_duration_spin = QSpinBox()
        self._lightn_duration_spin.setRange(1, 100)
        self._lightn_duration_spin.setSingleStep(1)
        self._lightn_duration_spin.setFixedWidth(80)
        h_duration.addWidget(self._lightn_duration_spin)
        h_duration.addStretch()
        v.addLayout(h_duration)

        _section(v, tr("set.lightn.sound_sec"))

        self._lightn_beep_cb = QCheckBox(tr("set.lightn.beep"))
        self._lightn_beep_cb.setToolTip(tr("tip.lightn.beep"))
        v.addWidget(self._lightn_beep_cb)

        h_beep = QHBoxLayout()
        h_beep.addWidget(QLabel(tr("set.lightn.beep_r")))
        self._lightn_beep_r_spin = QSpinBox()
        self._lightn_beep_r_spin.setRange(0, 5000)
        self._lightn_beep_r_spin.setSingleStep(50)
        self._lightn_beep_r_spin.setFixedWidth(80)
        self._lightn_beep_r_spin.setToolTip(tr("tip.lightn.beep_r"))
        h_beep.addWidget(self._lightn_beep_r_spin)
        h_beep.addStretch()
        v.addLayout(h_beep)

        # Normal sound pitch (outside alert zone)
        h_pitch_normal = QHBoxLayout()
        h_pitch_normal.addWidget(QLabel("Sound pitch (Hz):"))
        self._lightn_beep_pitch_spin = QSpinBox()
        self._lightn_beep_pitch_spin.setRange(1000, 8000)
        self._lightn_beep_pitch_spin.setSingleStep(100)
        self._lightn_beep_pitch_spin.setFixedWidth(80)
        h_pitch_normal.addWidget(self._lightn_beep_pitch_spin)
        h_pitch_normal.addStretch()
        v.addLayout(h_pitch_normal)

        # Normal sound duration
        h_duration_normal = QHBoxLayout()
        h_duration_normal.addWidget(QLabel("Sound duration (ms):"))
        self._lightn_beep_duration_spin = QSpinBox()
        self._lightn_beep_duration_spin.setRange(1, 100)
        self._lightn_beep_duration_spin.setSingleStep(1)
        self._lightn_beep_duration_spin.setFixedWidth(80)
        h_duration_normal.addWidget(self._lightn_beep_duration_spin)
        h_duration_normal.addStretch()
        v.addLayout(h_duration_normal)

        _section(v, tr("set.lightn.anim"))

        h_scale = QHBoxLayout()
        h_scale.addWidget(QLabel(tr("set.lightn.ring_size")))
        self._lightn_anim_scale_spin = QDoubleSpinBox()
        self._lightn_anim_scale_spin.setRange(0.5, 8.0)
        self._lightn_anim_scale_spin.setSingleStep(0.5)
        self._lightn_anim_scale_spin.setDecimals(1)
        self._lightn_anim_scale_spin.setSuffix(" ×")
        self._lightn_anim_scale_spin.setFixedWidth(80)
        self._lightn_anim_scale_spin.setToolTip(tr("tip.lightn.scale"))
        h_scale.addWidget(self._lightn_anim_scale_spin)
        h_scale.addStretch()
        v.addLayout(h_scale)

        h_font = QHBoxLayout()
        h_font.addWidget(QLabel(tr("set.map.font_lightning")))
        self._lightn_font_spin = QSpinBox()
        self._lightn_font_spin.setRange(5, 72)
        self._lightn_font_spin.setSuffix(" pt")
        self._lightn_font_spin.setFixedWidth(80)
        h_font.addWidget(self._lightn_font_spin)
        h_font.addStretch()
        v.addLayout(h_font)

        _section(v, tr("set.lightn.perf"))
        h3 = QHBoxLayout()
        h3.addWidget(QLabel(tr("set.lightn.interval")))
        self._lightn_rate_spin = QSpinBox()
        self._lightn_rate_spin.setRange(100, 5000)
        self._lightn_rate_spin.setSingleStep(100)
        self._lightn_rate_spin.setFixedWidth(80)
        self._lightn_rate_spin.setToolTip(tr("tip.lightn.rate"))
        h3.addWidget(self._lightn_rate_spin)
        h3.addStretch()
        v.addLayout(h3)

        v.addStretch()
        return w

    # ── Tab: Meldingen ────────────────────────────────────────────────────────
    def _tab_alerts(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(12, 8, 12, 8)
        v.setSpacing(4)

        _section(v, tr("sec.k_storm"))

        h = QHBoxLayout()
        self._k_en = QCheckBox(tr("k_en_cb"))
        v.addWidget(self._k_en)

        h2 = QHBoxLayout()
        h2.addWidget(QLabel(tr("k_thr_lbl")))
        self._k_spin = QSpinBox()
        self._k_spin.setRange(0, 9); self._k_spin.setFixedWidth(60)
        h2.addWidget(self._k_spin)
        h2.addStretch()
        v.addLayout(h2)

        note_k = QLabel(tr("k_note"))
        note_k.setStyleSheet(f"color: {TEXT_DIM}; font-size: 7pt;")
        note_k.setWordWrap(True)
        v.addWidget(note_k)

        _section(v, tr("sec.xray"))

        self._xflare_en = QCheckBox(tr("xflare_en_cb"))
        v.addWidget(self._xflare_en)

        _section(v, tr("sec.bandcond"))

        self._band_en = QCheckBox(tr("band_en_cb"))
        v.addWidget(self._band_en)

        h3 = QHBoxLayout()
        h3.addWidget(QLabel(tr("band_thr_lbl")))
        self._band_spin = QSpinBox()
        self._band_spin.setRange(0, 100); self._band_spin.setFixedWidth(60)
        h3.addWidget(self._band_spin)
        h3.addStretch()
        v.addLayout(h3)

        _section(v, tr("set.alerts.fifo"))
        h4 = QHBoxLayout()
        h4.addWidget(QLabel(tr("set.alerts.fifo_max")))
        self._alert_max_spin = QSpinBox()
        self._alert_max_spin.setRange(5, 500)
        self._alert_max_spin.setValue(50)
        self._alert_max_spin.setFixedWidth(70)
        self._alert_max_spin.setToolTip(tr("tip.alert.max"))
        h4.addWidget(self._alert_max_spin)
        h4.addStretch()
        v.addLayout(h4)

        _section(v, tr("set.alerts.sat"))
        self._sat_ping_cb = QCheckBox(tr("set.alerts.sat_ping_en"))
        self._sat_ping_cb.setToolTip(tr("tip.sat.ping"))
        v.addWidget(self._sat_ping_cb)

        v.addStretch()
        return w

    # ── Tab: CAT ──────────────────────────────────────────────────────────────
    def _tab_cat(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(12, 8, 12, 8)
        v.setSpacing(4)
        f8 = QFont("Segoe UI", 8)

        def row(lbl_txt, widget, width=130):
            h = QHBoxLayout()
            l = QLabel(lbl_txt); l.setFixedWidth(width)
            h.addWidget(l)
            h.addWidget(widget)
            h.addStretch()
            v.addLayout(h)

        _section(v, tr("sec.cat"))

        self._cat_en = QCheckBox(tr("cat.enable_cb"))
        self._cat_en.setToolTip(tr("tip.cat.en"))
        v.addWidget(self._cat_en)

        self._cat_monitor_btn = QPushButton(tr("set.cat.terminal"))
        self._cat_monitor_btn.setObjectName("ok")
        self._cat_monitor_btn.setFont(f8)
        self._cat_monitor_btn.setToolTip(tr("cat.monitor_tip"))
        self._cat_monitor_btn.clicked.connect(self._open_cat_monitor_from_settings)
        v.addWidget(self._cat_monitor_btn)

        _section(v, tr("sec.connection"))

        port_row = QHBoxLayout()
        port_lbl = QLabel(tr("cat.port_lbl")); port_lbl.setFixedWidth(130)
        self._cat_port = QComboBox()
        self._cat_port.setEditable(True)
        self._cat_port.setFont(QFont("Consolas", 8))
        self._cat_port.setMinimumWidth(160)
        self._cat_port.lineEdit().setPlaceholderText("COM3  /  /dev/ttyUSB0")
        btn_scan = QPushButton("↺")
        btn_scan.setFixedWidth(28)
        btn_scan.setToolTip(tr("tip.port.scan"))
        btn_scan.setFont(QFont("Segoe UI", 9))
        btn_scan.clicked.connect(self._scan_cat_ports)
        port_row.addWidget(port_lbl)
        port_row.addWidget(self._cat_port, 1)
        port_row.addWidget(btn_scan)
        v.addLayout(port_row)
        self._scan_cat_ports()

        self._cat_baud = QComboBox()
        for b in [300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]:
            self._cat_baud.addItem(str(b), b)
        row(tr("cat.baud_lbl"), self._cat_baud)

        self._cat_bits = QComboBox()
        for b in [7, 8]:
            self._cat_bits.addItem(str(b), b)
        row(tr("cat.bits_lbl"), self._cat_bits)

        self._cat_parity = QComboBox()
        # Data = interne waarde (voor cat_interface), display = vertaald
        for internal, tr_key in [("Geen", "cat.parity.none"),
                                  ("Even", "cat.parity.even"),
                                  ("Odd",  "cat.parity.odd")]:
            self._cat_parity.addItem(tr(tr_key), internal)
        row(tr("cat.parity_lbl"), self._cat_parity)

        self._cat_stop = QComboBox()
        self._cat_stop.addItems(["1", "2"])
        row(tr("cat.stop_lbl"), self._cat_stop)

        self._cat_rtscts = QCheckBox(tr("cat.rtscts"))
        v.addWidget(self._cat_rtscts)
        self._cat_dtr = QCheckBox(tr("cat.dtr"))
        v.addWidget(self._cat_dtr)
        self._cat_rts = QCheckBox(tr("cat.rts"))
        v.addWidget(self._cat_rts)

        _section(v, tr("sec.radio_type"))

        self._cat_type = QComboBox()
        self._cat_type.addItems(CatInterface.RADIO_TYPES)
        row(tr("cat.type_lbl"), self._cat_type)

        self._cat_civ = QSpinBox()
        self._cat_civ.setRange(0, 255)
        self._cat_civ.setDisplayIntegerBase(16)
        self._cat_civ.setPrefix("0x")
        self._cat_civ.setFixedWidth(80)
        self._cat_civ.setToolTip(tr("tip.civ"))
        row(tr("cat.civ_lbl"), self._cat_civ)

        def _update_civ_vis():
            show = "Icom" in self._cat_type.currentText()
            self._cat_civ.setEnabled(show)
        self._cat_type.currentTextChanged.connect(_update_civ_vis)
        _update_civ_vis()

        _section(v, tr("sec.preset"))
        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel(tr("cat.preset_lbl")))
        _none = tr("cat.parity.none")
        for label, rtype, baud, bits, par, stop in [
            ("FT-950",  "Yaesu (FT-950/2000/DX/3000/5000)", 38400, 8, _none, "2"),
            ("FT-817",  "Yaesu (FT-817/857/897)",           9600,  8, _none, "1"),
            ("TS-590",  "Kenwood / Elecraft",               9600,  8, _none, "1"),
            ("K3/KX3",  "Kenwood / Elecraft",               38400, 8, _none, "1"),
        ]:
            b = QPushButton(label)
            b.setFont(f8)
            b.setToolTip(f"{rtype}  ·  {baud} baud  {bits}{par[0]}1")
            b.clicked.connect(
                lambda _=0, rt=rtype, bd=baud, bi=bits, pa=par, st=stop:
                    self._apply_cat_preset(rt, bd, bi, pa, st))
            preset_row.addWidget(b)
        preset_row.addStretch()
        v.addLayout(preset_row)

        _section(v, tr("sec.test"))

        btn_row = QHBoxLayout()
        self._cat_test_btn = QPushButton(tr("btn.test_conn"))
        self._cat_test_btn.setFont(f8)
        self._cat_status_lbl = QLabel("")
        self._cat_status_lbl.setFont(f8)
        btn_row.addWidget(self._cat_test_btn)
        btn_row.addWidget(self._cat_status_lbl)
        btn_row.addStretch()
        v.addLayout(btn_row)

        def _test_connection():
            tmp_cfg = self._collect_cfg()
            existing = get_instance()
            if existing and existing.connected:
                existing.disconnect()
            cat = CatInterface(tmp_cfg)
            ok, err = cat.connect()
            if not ok:
                friendly = _friendly_serial_error(err)
                self._cat_status_lbl.setText(f"✘  {friendly}")
                self._cat_status_lbl.setStyleSheet(_STYLE_STATUS_ERR)
                return
            # Identificeer de radio via ID;
            id_ok, id_resp = cat.identify()
            cat.disconnect()
            if id_ok:
                # ID0310 = FT-950, andere waarden voor andere rigs
                rig = _RADIO_ID_MAP.get(id_resp, id_resp)
                self._cat_status_lbl.setText(tr("cat.status.ok", rig=rig))
                self._cat_status_lbl.setStyleSheet(_STYLE_STATUS_OK)
            else:
                self._cat_status_lbl.setText(tr("cat.status.open"))
                self._cat_status_lbl.setStyleSheet("color: #FFA726; font-size: 8pt;")

        self._cat_test_btn.clicked.connect(_test_connection)

        if not serial_available():
            note = QLabel(tr("cat.no_pyserial"))
            note.setStyleSheet(_STYLE_ERR_DIM)
            v.addWidget(note)

        v.addStretch()
        return w

    def _apply_cat_preset(self, radio_type: str, baud: int, bits: int,
                          parity: str, stopbits: str):
        """Vul CAT-instellingen in met bekende waarden voor dit radiotype."""
        _set_combo(self._cat_type, radio_type, CatInterface.RADIO_TYPES[0])
        _set_combo_data(self._cat_baud, baud, 9600)
        _set_combo_data(self._cat_bits, bits, 8)
        _set_combo_data(self._cat_parity, parity, "Geen")
        _set_combo(self._cat_stop, stopbits, "1")
        self._live(0)

    def _scan_cat_ports(self):
        """Vul de poort-combobox met beschikbare seriële poorten."""
        current = self._cat_port.currentText().strip()
        self._cat_port.blockSignals(True)
        self._cat_port.clear()

        ports = _list_serial_ports()
        for port, desc in ports:
            label = f"{port}  —  {desc}" if desc else port
            self._cat_port.addItem(label, port)

        # Herstel eerder geselecteerde poort
        found = False
        if current:
            for i in range(self._cat_port.count()):
                if self._cat_port.itemData(i) == current or \
                        self._cat_port.itemText(i).startswith(current):
                    self._cat_port.setCurrentIndex(i)
                    found = True
                    break
            if not found:
                self._cat_port.setEditText(current)

        self._cat_port.blockSignals(False)
        # Statuslabel bijwerken
        n = len(ports)
        if hasattr(self, "_cat_status_lbl"):
            if n == 0:
                self._cat_status_lbl.setText(tr("cat.no_ports"))
                self._cat_status_lbl.setStyleSheet(_STYLE_STATUS_ERR)
            else:
                self._cat_status_lbl.setText(f"{n} poort{'en' if n > 1 else ''} gevonden")
                self._cat_status_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 8pt;")

    # ── Tab: Resources ────────────────────────────────────────────────────────
    def _tab_resources(self) -> QWidget:
        from .resources_tab import ResourceManagerTab
        return ResourceManagerTab(self)

    # ── Tab: Over ─────────────────────────────────────────────────────────────
    def _tab_about(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(12, 8, 12, 8)
        v.setSpacing(4)

        f8 = QFont("Segoe UI", 8)

        _section(v, tr("sec.version"))
        for txt in [tr("set.about.app_line"), tr("set.about.dev_line")]:
            lbl = QLabel(txt)
            lbl.setFont(f8)
            v.addWidget(lbl)

        _section(v, tr("sec.deps"))

        _req_str = "[required]" if tr("set.tab.about.lbl") == "📦  About" else "[vereist]"
        _opt_str = "[optional]" if tr("set.tab.about.lbl") == "📦  About" else "[optioneel]"
        _copy_str = "← copy" if tr("set.tab.about.lbl") == "📦  About" else "← kopieer"
        DEPS = [
            ("PySide6",          _req_str, "pip install PySide6"),
            ("websocket-client", _opt_str, "pip install websocket-client"),
            ("pyserial",         _opt_str, "pip install pyserial"),
            ("timezonefinder",   _opt_str, "pip install timezonefinder"),
        ]
        for pkg, kind, cmd in DEPS:
            ok  = _check_dep(pkg)
            row = QHBoxLayout()
            row.setSpacing(6)

            status = QLabel("✔" if ok else "✘")
            status.setFont(f8)
            status.setFixedWidth(16)
            status.setStyleSheet(f"color: {'#4CAF50' if ok else '#EF5350'};")
            row.addWidget(status)

            lbl = QLabel(f"{pkg}  {kind}")
            lbl.setFont(f8)
            row.addWidget(lbl)

            if not ok:
                btn = QPushButton(cmd)
                btn.setFont(QFont("Consolas", 8))
                btn.setToolTip(tr("tip.copy"))
                btn.clicked.connect(lambda _, c=cmd: _copy_to_clipboard(c))
                row.addWidget(btn)
                hint = QLabel(_copy_str)
                hint.setFont(f8)
                row.addWidget(hint)

            row.addStretch()
            v.addLayout(row)

        _section(v, tr("sec.files"))
        from .startup import file_status
        f7 = QFont("Consolas", 7)
        for info in file_status():
            row = QHBoxLayout(); row.setSpacing(4)
            ok  = info["exists"]
            dot = QLabel("✔" if ok else "✘")
            dot.setFont(f8); dot.setFixedWidth(14)
            dot.setStyleSheet(f"color: {'#4CAF50' if ok else '#EF5350'};")
            row.addWidget(dot)
            name_lbl = QLabel(info["name"])
            name_lbl.setFont(f7)
            name_lbl.setToolTip(info["path"])
            row.addWidget(name_lbl)
            size_lbl = QLabel(f"{info['size_kb']} KB" if ok else f"—  [{info['label']}]")
            size_lbl.setFont(f7)
            size_lbl.setStyleSheet(f"color: {'#606870' if ok else '#EF5350'};")
            row.addWidget(size_lbl)
            row.addStretch()
            v.addLayout(row)

        _section(v, tr("sec.options"))
        self._splash_about = QCheckBox(tr("about.splash"))
        self._splash_about.setFont(f8)
        v.addWidget(self._splash_about)

        _section(v, tr("set.lang_section"))
        lang_row = QHBoxLayout()
        from PySide6.QtWidgets import QRadioButton, QButtonGroup
        self._lang_nl = QRadioButton("Nederlands")
        self._lang_en = QRadioButton("English")
        self._lang_nl.setFont(f8)
        self._lang_en.setFont(f8)
        self._lang_group = QButtonGroup(self)
        self._lang_group.addButton(self._lang_nl, 0)
        self._lang_group.addButton(self._lang_en, 1)
        lang_row.addWidget(self._lang_nl)
        lang_row.addWidget(self._lang_en)
        lang_row.addStretch()
        v.addLayout(lang_row)
        lang_note = QLabel(tr("about.lang_note"))
        lang_note.setFont(f8)
        lang_note.setStyleSheet(f"color: {TEXT_DIM}; font-style: italic;")
        lang_note.setWordWrap(True)
        v.addWidget(lang_note)
        self._lang_nl.toggled.connect(lambda: self._live(0))

        v.addStretch()
        return w

    # ── Tab: Layout ───────────────────────────────────────────────────────────
    def _tab_layout(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(12, 8, 12, 8)
        v.setSpacing(6)
        f8 = QFont("Segoe UI", 8)

        # ── Snap-raster ───────────────────────────────────────────────────
        _section(v, tr("sec.raster"))

        snap_row = QHBoxLayout()
        snap_lbl = QLabel(tr("set.layout.snap"))
        snap_lbl.setFont(f8)
        snap_lbl.setFixedWidth(160)
        self._snap_cb = QComboBox()
        self._snap_cb.setFont(f8)
        for val in _GRIDS:
            self._snap_cb.addItem(f"{val} px", val)
        snap_row.addWidget(snap_lbl)
        snap_row.addWidget(self._snap_cb)
        snap_row.addStretch()
        v.addLayout(snap_row)

        # ── Standaard layout ──────────────────────────────────────────────
        _section(v, tr("sec.default_layout"))

        br = QHBoxLayout()
        btn_save_def = QPushButton(tr("btn.save_default"))
        btn_reset    = QPushButton(tr("btn.reset_default"))
        btn_reset.setObjectName("danger")
        br.addWidget(btn_save_def)
        br.addWidget(btn_reset)
        br.addStretch()
        v.addLayout(br)

        note_def = QLabel(
            "\"Als standaard\" slaat de huidige paneel-posities op.\n"
            "\"Reset\" herstelt panelen naar die opgeslagen standaard (of fabriek).")
        note_def.setFont(f8)
        note_def.setStyleSheet(f"color: {TEXT_DIM};")
        note_def.setWordWrap(True)
        v.addWidget(note_def)

        # ── Benoemde profielen ────────────────────────────────────────────
        _section(v, tr("sec.profiles"))

        new_row = QHBoxLayout()
        self._profile_name = QLineEdit()
        self._profile_name.setPlaceholderText("Naam voor nieuw profiel…")
        self._profile_name.setFont(f8)
        btn_new = QPushButton(tr("btn.save_profile"))
        btn_new.setFont(f8)
        new_row.addWidget(self._profile_name, 1)
        new_row.addWidget(btn_new)
        v.addLayout(new_row)

        # Scrollbare profielenlijst
        self._profiles_scroll = QScrollArea()
        self._profiles_scroll.setWidgetResizable(True)
        self._profiles_scroll.setFrameShape(QScrollArea.NoFrame)
        self._profiles_scroll.setMinimumHeight(100)
        v.addWidget(self._profiles_scroll, 1)

        # Verbindingen
        btn_save_def.clicked.connect(self._save_as_default)
        btn_reset.clicked.connect(self._reset_to_default)
        btn_new.clicked.connect(self._save_new_profile)

        self._refresh_profiles()
        return w

    def _fit_to_tabs(self):
        """Pas breedte aan zodat alle tab-labels zichtbaar zijn."""
        bar_w = self._tabs.tabBar().sizeHint().width()
        needed = bar_w + 60
        if self.width() < needed:
            self.resize(needed, self.height())
        self.setMinimumWidth(needed)

    def _refresh_profiles(self):
        """Vervang de profielenlijst door een nieuw opgebouwde widget (ProfielManager)."""
        f8  = QFont("Segoe UI", 8)
        f8b = QFont("Segoe UI", 8); f8b.setBold(True)

        # Maak elke keer een nieuwe container (geen deleteLater-problemen)
        container = QWidget()
        container.setStyleSheet(f"background: {BG_PANEL};")
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(4, 4, 4, 4)
        vbox.setSpacing(4)

        profiles = ProfileManager.list_named_profiles()

        if not profiles:
            lbl = QLabel(tr("no_profiles"))
            lbl.setFont(f8)
            lbl.setStyleSheet(f"color: {TEXT_DIM};")
            vbox.addWidget(lbl)
        else:
            for name in profiles:
                row_widget = QWidget()
                row_widget.setStyleSheet(
                    f"QWidget {{ background: {BG_SURFACE}; border-radius: 2px; }}")
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(8, 3, 4, 3)
                row_layout.setSpacing(4)

                lbl = QLabel(name)
                lbl.setFont(f8b)
                lbl.setStyleSheet(f"color: {TEXT_H1}; background: transparent;")
                row_layout.addWidget(lbl, 1)

                for btn_txt, clr, action in [
                    (tr("btn.load"),   "#66BB6A", lambda _=0, n=name: self._load_profile(n)),
                    ("Overschrijven", ACCENT,    lambda _=0, n=name: self._overwrite_profile(n)),
                    ("Verwijderen",   "#EF5350", lambda _=0, n=name: self._delete_profile(n)),
                ]:
                    b = QPushButton(btn_txt)
                    b.setFont(f8)
                    b.setStyleSheet(
                        f"QPushButton {{ background: {BG_PANEL}; color: {clr};"
                        f" border: 1px solid {BORDER}; padding: 2px 8px; border-radius: 2px; }}"
                        f"QPushButton:hover {{ background: #32373F; }}")
                    b.clicked.connect(action)
                    row_layout.addWidget(b)

                vbox.addWidget(row_widget)

        vbox.addStretch()
        self._profiles_scroll.setWidget(container)

    # ── Profiel-acties (config + layout) ──────────────────────────────────
    def _get_current_config_dict(self) -> dict:
        """Converteer huidge AppConfig naar dict."""
        return asdict(self._cfg)

    def _get_current_layout_dict(self) -> dict:
        """Lees huidge panel-geometrie + zichtbaarheid."""
        layout = {}
        for pid, p in self._panels.items():
            g = p.geometry()
            layout[pid] = [g.x(), g.y(), g.width(), g.height(),
                           p.is_panel_visible()]
        if self._mainwin:
            layout["__window__"] = [
                self._mainwin.x(), self._mainwin.y(),
                self._mainwin.width(), self._mainwin.height()
            ]
        return layout

    # ── Layout-acties ─────────────────────────────────────────────────────
    def _current_layout_dict(self) -> dict:
        """Lees huidge panel-geometrie + zichtbaarheid (legacy compat)."""
        return self._get_current_layout_dict()

    def _apply_layout_dict(self, layout: dict):
        """Pas een opgeslagen layout toe op panelen én venster."""
        # Venstergrootte herstellen
        if "__window__" in layout and self._mainwin and len(layout["__window__"]) >= 4:
            wx, wy, ww, wh = layout["__window__"][:4]
            self._mainwin.setGeometry(int(wx), int(wy), int(ww), int(wh))
        # Panelen
        for pid, p in self._panels.items():
            if pid in layout and len(layout[pid]) >= 5:
                x, y, ww, hh, vis = layout[pid][:5]
                p.setGeometry(int(x), int(y), int(ww), int(hh))
                if vis:
                    p.show_panel()
                else:
                    p.hide_panel()

    def _save_as_default(self):
        """Sla huidge instellingen + layout op als default-profiel."""
        config_dict = self._get_current_config_dict()
        layout_dict = self._get_current_layout_dict()
        ProfileManager.set_default_profile(config_dict, layout_dict)
        self._status_lbl.setText(tr("set.saved_default"))
        self._status_lbl.setStyleSheet(_STYLE_STATUS_OK)
        self._status_timer.start(2500)

    def _reset_to_default(self):
        """Laad default-profiel (config + layout)."""
        result = ProfileManager.reset_to_default()
        if result:
            config_dict, layout_dict = result
            # Laad config
            self._apply_config_dict(config_dict)
            # Laad layout
            self._apply_layout_dict(layout_dict)
            self._status_lbl.setText("✓  Standaard-instellingen hersteld")
            self._status_lbl.setStyleSheet(_STYLE_STATUS_OK)
            self._status_timer.start(2500)
        else:
            self._status_lbl.setText("✗  Geen standaard-profiel gevonden")
            self._status_lbl.setStyleSheet(_STYLE_STATUS_ERR)
            self._status_timer.start(3000)

    def _save_new_profile(self):
        """Sla huidge instellingen + layout op als nieuw profiel."""
        name = self._profile_name.text().strip()
        if not name:
            return
        if name.startswith("__"):
            name = name.lstrip("_")

        config_dict = self._get_current_config_dict()
        layout_dict = self._get_current_layout_dict()

        if ProfileManager.save_profile(name, config_dict, layout_dict):
            self._profile_name.clear()
            self._refresh_profiles()
            self._status_lbl.setText(f"[OK]  Profiel '{name}' opgeslagen")
            self._status_lbl.setStyleSheet(_STYLE_STATUS_OK)
            self._status_timer.start(2500)
        else:
            self._status_lbl.setText(f"✗  Profiel '{name}' kon niet opgeslagen worden")
            self._status_lbl.setStyleSheet(_STYLE_STATUS_ERR)
            self._status_timer.start(3000)

    def _load_profile(self, name: str):
        """Laad profiel (config + layout)."""
        profile = ProfileManager.get_profile(name)
        if profile:
            # Laad config
            self._apply_config_dict(profile.config)
            # Laad layout
            self._apply_layout_dict(profile.layout)
            self._status_lbl.setText(f"✓  Profiel '{name}' geladen")
            self._status_lbl.setStyleSheet(_STYLE_STATUS_OK)
            self._status_timer.start(2500)
        else:
            self._status_lbl.setText(f"✗  Profiel '{name}' niet gevonden")
            self._status_lbl.setStyleSheet(_STYLE_STATUS_ERR)
            self._status_timer.start(3000)

    def _overwrite_profile(self, name: str):
        """Overschrijf bestaand profiel met huidge instellingen."""
        config_dict = self._get_current_config_dict()
        layout_dict = self._get_current_layout_dict()

        if ProfileManager.update_profile(name, config_dict, layout_dict):
            self._status_lbl.setText(f"✓  Profiel '{name}' overschreven")
            self._status_lbl.setStyleSheet(_STYLE_STATUS_OK)
            self._status_timer.start(2500)
        else:
            self._status_lbl.setText(f"✗  Profiel '{name}' kon niet overschreven worden")
            self._status_lbl.setStyleSheet(_STYLE_STATUS_ERR)
            self._status_timer.start(3000)

    def _delete_profile(self, name: str):
        """Verwijder profiel."""
        from PySide6.QtWidgets import QMessageBox
        if QMessageBox.question(
                self, "Profiel verwijderen",
                f"Profiel '{name}' verwijderen?",
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            if ProfileManager.delete_profile(name):
                self._refresh_profiles()
            else:
                self._status_lbl.setText(f"✗  Profiel '{name}' kon niet verwijderd worden")
                self._status_lbl.setStyleSheet(_STYLE_STATUS_ERR)
                self._status_timer.start(3000)

    def _apply_config_dict(self, config_dict: dict):
        """Pas config-dict toe op alle UI-controls (vanuit profiel)."""
        self._loading = True
        c = config_dict  # config als dict met str-keys

        def get_val(key, default=None):
            """Haal waarde uit dict met fallback."""
            return c.get(key, default)

        # Station
        self._call_edit.setText(get_val("callsign", ""))
        self._loc_edit.setText(get_val("qth_locator", "JO22"))
        self._lat_spin.blockSignals(True)
        self._lon_spin.blockSignals(True)
        self._lat_spin.setValue(float(get_val("qth_lat", 52.0)))
        self._lon_spin.setValue(float(get_val("qth_lon", 5.0)))
        self._lat_spin.blockSignals(False)
        self._lon_spin.blockSignals(False)
        _set_combo(self._mode_cb,  get_val("mode", "SSB"),    _MODES[0])
        _set_combo(self._power_cb, get_val("power", "100W"),   _POWERS[4])
        _set_combo(self._ant_cb,   get_val("antenna", "Dipole ~2dBi"), _ANTENNAS[0])
        self._day_auto_cb.setChecked(get_val("band_day_auto", True))

        # Kaart
        self._cb_night.setChecked(get_val("show_night", True))
        self._cb_grayline.setChecked(get_val("show_grayline", True))
        self._cb_aurora.setChecked(get_val("show_aurora", True))
        self._cb_sun.setChecked(get_val("show_sun", True))
        self._cb_moon.setChecked(get_val("show_moon", True))
        self._cb_lightn.setChecked(get_val("show_lightning", True))
        self._cb_lightn_en.setChecked(get_val("show_lightning", True))
        self._cb_dxspots.setChecked(get_val("show_dx_spots", True))
        self._cb_locator.setChecked(get_val("show_locator", False))
        _set_combo_data(self._snap_cb, get_val("snap_grid", 10), _GRIDS[2])
        _set_combo_data(self._grat_step_cb, get_val("grat_step", 30), 30)
        self._font_spin.setValue(int(get_val("overlay_font_size", 8)))
        self._maid_font_spin.setValue(int(get_val("maidenhead_font_size", 8)))
        self._sat_font_spin.setValue(int(get_val("sat_font_size", 8)))
        self._sat_path_width_spin.setValue(float(get_val("sat_path_width", 1.2)))
        self._callsign_font_spin.setValue(int(get_val("callsign_overlay_font_size", 7)))
        self._dx_map_font_spin.setValue(int(get_val("dx_map_font_size", 7)))
        self._dx_font_spin.setValue(int(get_val("dx_font_size", 8)))
        self._sun_size_spin.setValue(int(get_val("sun_icon_size", 24)))
        self._moon_size_spin.setValue(int(get_val("moon_icon_size", 20)))

        # Bliksem
        self._fade_spin.setValue(int(get_val("lightning_fade", 600)))
        self._cb_lightn_en.setChecked(get_val("show_lightning", True))
        self._lightn_radius_spin.setValue(int(get_val("lightning_radius", 500)))
        self._lightn_rate_spin.setValue(int(get_val("lightning_rate", 500)))
        self._lightn_beep_cb.setChecked(get_val("lightning_beep", False))
        self._lightn_beep_r_spin.setValue(int(get_val("lightning_beep_r", 0)))
        self._lightn_beep_pitch_spin.setValue(int(get_val("lightning_beep_pitch", 2800)))
        self._lightn_beep_duration_spin.setValue(int(get_val("lightning_beep_duration", 5)))
        self._lightn_anim_scale_spin.setValue(float(get_val("lightning_anim_scale", 2.0)))
        self._lightn_font_spin.setValue(int(get_val("lightning_font_size", 7)))
        self._lightn_pitch_spin.setValue(int(get_val("lightning_alert_pitch", 5000)))
        self._lightn_duration_spin.setValue(int(get_val("lightning_alert_duration", 10)))

        # Meldingen
        self._k_en.setChecked(get_val("k_alert_en", True))
        self._k_spin.setValue(int(get_val("k_alert", 4)))
        self._xflare_en.setChecked(get_val("xflare_alert_en", True))
        self._band_en.setChecked(get_val("band_alert_en", True))
        self._band_spin.setValue(int(get_val("band_alert", 40)))
        self._alert_max_spin.setValue(int(get_val("alert_max", 50)))
        self._sat_ping_cb.setChecked(get_val("sat_zone_ping", True))

        # Splash & taal
        self._splash_about.setChecked(get_val("show_splash", True))
        lang = get_val("language", "nl")
        (self._lang_en if lang == "en" else self._lang_nl).setChecked(True)

        # CAT
        self._cat_en.setChecked(get_val("cat_enabled", False))
        _set_cat_port(self._cat_port, get_val("cat_port", ""))
        _set_combo_data(self._cat_baud,   get_val("cat_baud", 4800), 4800)
        _set_combo_data(self._cat_bits,   get_val("cat_databits", 8), 8)
        _set_combo_data(self._cat_parity, get_val("cat_parity", "Geen"), "Geen")
        _set_combo(self._cat_stop,   get_val("cat_stopbits", "1"), "1")
        self._cat_rtscts.setChecked(get_val("cat_rtscts", False))
        self._cat_dtr.setChecked(get_val("cat_dtr", False))
        self._cat_rts.setChecked(get_val("cat_rts", False))
        saved_type = get_val("cat_radio_type", "")
        if saved_type == "Yaesu":
            saved_type = CatInterface.RADIO_TYPES[0]
        _set_combo(self._cat_type, saved_type, CatInterface.RADIO_TYPES[0])
        self._cat_civ.setValue(int(get_val("cat_civ_addr", 0x58)))

        self._loading = False
        # Verbind alle controls na laden
        self._connect_live_controls()

        # Update AppConfig object van UI-values en sla op
        self._cfg = self._collect_cfg()
        self._save_cfg()

    # ── Lightning connection status ────────────────────────────────────────────
    def _update_lightn_status(self, enabled: bool):
        """Update Lightning connection status when Enable is toggled."""
        if not enabled:
            self._lightn_status.setText("○ Disabled")
            self._lightn_status.setStyleSheet(f"color: {TEXT_DIM};")
            return

        # Show connecting status
        self._lightn_status.setText("● Connecting...")
        self._lightn_status.setStyleSheet("color: #C8A84B;")

        # Start connection test in background
        import threading
        import urllib.request

        def test_connection():
            try:
                # Test connectivity to Blitzortung website
                req = urllib.request.Request(
                    "https://www.blitzortung.org/",
                    method="HEAD",
                    headers={"User-Agent": "HAMIOS/5.4"}
                )
                with urllib.request.urlopen(req, timeout=5) as r:
                    return r.status < 400
            except Exception:
                return False

        def run_test():
            success = test_connection()
            if success:
                self._lightn_status.setText("✓ Connected")
                self._lightn_status.setStyleSheet(_STYLE_OK_NO_SIZE)
            else:
                self._lightn_status.setText("✗ Connection failed")
                self._lightn_status.setStyleSheet(_STYLE_ERR_NO_SIZE)

        threading.Thread(target=run_test, daemon=True).start()

    # ── Config laden/opslaan ──────────────────────────────────────────────────
    def _load_cfg(self):
        self._loading = True   # blokkeert _live() tijdens initialisatie
        c = self._cfg

        # Station
        self._call_edit.setText(c.callsign)
        self._loc_edit.setText(c.qth_locator)
        self._lat_spin.blockSignals(True)
        self._lon_spin.blockSignals(True)
        self._lat_spin.setValue(c.qth_lat)
        self._lon_spin.setValue(c.qth_lon)
        self._lat_spin.blockSignals(False)
        self._lon_spin.blockSignals(False)
        _set_combo(self._mode_cb,  c.mode,    _MODES[0])
        _set_combo(self._power_cb, c.power,   _POWERS[4])
        _set_combo(self._ant_cb,   c.antenna, _ANTENNAS[0])
        self._day_auto_cb.setChecked(getattr(c, "band_day_auto", True))

        # Kaart
        self._cb_night.setChecked(c.show_night)
        self._cb_grayline.setChecked(c.show_grayline)
        self._cb_aurora.setChecked(c.show_aurora)
        self._cb_sun.setChecked(c.show_sun)
        self._cb_moon.setChecked(c.show_moon)
        self._cb_lightn.setChecked(c.show_lightning)
        self._cb_lightn_en.setChecked(c.show_lightning)
        self._cb_dxspots.setChecked(c.show_dx_spots)
        self._cb_locator.setChecked(getattr(c, "show_locator", False))
        _set_combo_data(self._snap_cb, c.snap_grid, _GRIDS[2])
        _set_combo_data(self._grat_step_cb, getattr(c, "grat_step", 30), 30)
        self._font_spin.setValue(c.overlay_font_size)
        self._maid_font_spin.setValue(getattr(c, "maidenhead_font_size", 8))
        self._sat_font_spin.setValue(getattr(c, "sat_font_size", 8))
        self._sat_path_width_spin.setValue(getattr(c, "sat_path_width", 1.2))
        self._callsign_font_spin.setValue(getattr(c, "callsign_overlay_font_size", 7))
        self._dx_map_font_spin.setValue(getattr(c, "dx_map_font_size", 7))
        self._dx_font_spin.setValue(getattr(c, "dx_font_size", 8))
        self._sun_size_spin.setValue(getattr(c, "sun_icon_size", 24))
        self._moon_size_spin.setValue(getattr(c, "moon_icon_size", 20))

        # Bliksem
        self._fade_spin.setValue(c.lightning_fade)
        self._cb_lightn_en.setChecked(getattr(c, "show_lightning", True))
        self._lightn_radius_spin.setValue(getattr(c, "lightning_radius", 500))
        self._lightn_rate_spin.setValue(getattr(c, "lightning_rate", 500))
        self._lightn_beep_cb.setChecked(getattr(c, "lightning_beep", False))
        self._lightn_beep_r_spin.setValue(getattr(c, "lightning_beep_r", 0))
        self._lightn_beep_pitch_spin.setValue(getattr(c, "lightning_beep_pitch", 2800))
        self._lightn_beep_duration_spin.setValue(getattr(c, "lightning_beep_duration", 5))
        self._lightn_anim_scale_spin.setValue(getattr(c, "lightning_anim_scale", 2.0))
        self._lightn_font_spin.setValue(getattr(c, "lightning_font_size", 7))
        self._lightn_pitch_spin.setValue(getattr(c, "lightning_alert_pitch", 5000))
        self._lightn_duration_spin.setValue(getattr(c, "lightning_alert_duration", 10))

        # Meldingen
        self._k_en.setChecked(c.k_alert_en)
        self._k_spin.setValue(c.k_alert)
        self._xflare_en.setChecked(c.xflare_alert_en)
        self._band_en.setChecked(c.band_alert_en)
        self._band_spin.setValue(c.band_alert)
        self._alert_max_spin.setValue(getattr(c, "alert_max", 50))
        self._sat_ping_cb.setChecked(getattr(c, "sat_zone_ping", True))

        # Splash screen — alleen in About tab
        self._splash_about.setChecked(c.show_splash)
        lang = getattr(c, "language", "nl")
        (self._lang_en if lang == "en" else self._lang_nl).setChecked(True)

        # CAT
        self._cat_en.setChecked(getattr(c, "cat_enabled", False))
        _set_cat_port(self._cat_port, getattr(c, "cat_port", ""))
        _set_combo_data(self._cat_baud,   getattr(c, "cat_baud",     9600), 9600)
        _set_combo_data(self._cat_bits,   getattr(c, "cat_databits", 8),    8)
        _set_combo_data(self._cat_parity, getattr(c, "cat_parity", "Geen"), "Geen")
        _set_combo(self._cat_stop,   getattr(c, "cat_stopbits", "1"),   "1")
        self._cat_rtscts.setChecked(getattr(c, "cat_rtscts", False))
        self._cat_dtr.setChecked(getattr(c, "cat_dtr", False))
        self._cat_rts.setChecked(getattr(c, "cat_rts", False))
        # Migreer oude "Yaesu" waarde naar nieuwe naam
        saved_type = getattr(c, "cat_radio_type", "")
        if saved_type == "Yaesu":
            saved_type = CatInterface.RADIO_TYPES[0]
        _set_combo(self._cat_type, saved_type, CatInterface.RADIO_TYPES[0])
        self._cat_civ.setValue(int(getattr(c, "cat_civ_addr", 0x58)))

        self._loading = False
        # Verbind alle controls na laden (voorkomt trigger tijdens init)
        self._connect_live_controls()

    def _collect_cfg(self) -> AppConfig:
        import dataclasses
        c = self._cfg
        # Gebruik dataclasses.replace zodat alle niet-UI-velden bewaard blijven
        return dataclasses.replace(c,
            callsign          = self._call_edit.text().strip().upper(),
            qth_lat           = self._lat_spin.value(),
            qth_lon           = self._lon_spin.value(),
            qth_locator       = self._loc_edit.text().strip().upper(),
            mode              = self._mode_cb.currentText(),
            power             = self._power_cb.currentText(),
            antenna           = self._ant_cb.currentText(),
            band_day_auto     = self._day_auto_cb.isChecked(),
            show_night        = self._cb_night.isChecked(),
            show_grayline     = self._cb_grayline.isChecked(),
            show_aurora       = self._cb_aurora.isChecked(),
            show_sun          = self._cb_sun.isChecked(),
            show_moon         = self._cb_moon.isChecked(),
            show_lightning    = self._cb_lightn_en.isChecked(),
            show_dx_spots     = self._cb_dxspots.isChecked(),
            show_locator      = self._cb_locator.isChecked(),
            lightning_fade      = self._fade_spin.value(),
            lightning_radius    = self._lightn_radius_spin.value(),
            lightning_rate      = self._lightn_rate_spin.value(),
            lightning_beep      = self._lightn_beep_cb.isChecked(),
            lightning_beep_r    = self._lightn_beep_r_spin.value(),
            lightning_beep_pitch = self._lightn_beep_pitch_spin.value(),
            lightning_beep_duration = self._lightn_beep_duration_spin.value(),
            lightning_alert_pitch = self._lightn_pitch_spin.value(),
            lightning_alert_duration = self._lightn_duration_spin.value(),
            lightning_anim_scale= self._lightn_anim_scale_spin.value(),
            lightning_font_size = self._lightn_font_spin.value(),
            snap_grid         = self._snap_cb.currentData(),
            grat_step         = self._grat_step_cb.currentData(),
            overlay_font_size     = self._font_spin.value(),
            maidenhead_font_size  = self._maid_font_spin.value(),
            sat_font_size     = self._sat_font_spin.value(),
            sat_path_width    = self._sat_path_width_spin.value(),
            callsign_overlay_font_size = self._callsign_font_spin.value(),
            dx_map_font_size  = self._dx_map_font_spin.value(),
            dx_font_size      = self._dx_font_spin.value(),
            sun_icon_size     = self._sun_size_spin.value(),
            moon_icon_size    = self._moon_size_spin.value(),
            show_splash       = self._splash_about.isChecked(),
            language          = "en" if self._lang_en.isChecked() else "nl",
            k_alert           = self._k_spin.value(),
            k_alert_en        = self._k_en.isChecked(),
            xflare_alert_en   = self._xflare_en.isChecked(),
            band_alert        = self._band_spin.value(),
            band_alert_en     = self._band_en.isChecked(),
            alert_max         = self._alert_max_spin.value(),
            sat_zone_ping     = self._sat_ping_cb.isChecked(),
            cat_enabled       = self._cat_en.isChecked(),
            cat_port          = _get_cat_port(self._cat_port),
            cat_baud          = self._cat_baud.currentData() or 4800,
            cat_databits      = self._cat_bits.currentData() or 8,
            cat_parity        = self._cat_parity.currentData() or "Geen",
            cat_stopbits      = self._cat_stop.currentText(),
            cat_rtscts        = self._cat_rtscts.isChecked(),
            cat_dtr           = self._cat_dtr.isChecked(),
            cat_rts           = self._cat_rts.isChecked(),
            cat_radio_type    = self._cat_type.currentText(),
            cat_civ_addr      = self._cat_civ.value(),
        )
        # Velden die via panel-signals bewaard worden (niet hier overschrijven):
        # dx_own_continent, dx_heatmap, band_mode, band_power, band_day_auto,
        # sat_fp, sat_back_h, sat_fwd_h, sat_selected, sat_path, sat_visible

    def _save_cfg(self):
        """Sla huidige config op naar bestand."""
        save_config(self._cfg)

    # ── Acties ────────────────────────────────────────────────────────────────
    def _locator_to_latlon(self):
        result = locator_to_latlon(self._loc_edit.text())
        if result:
            self._lat_spin.blockSignals(True)
            self._lon_spin.blockSignals(True)
            self._lat_spin.setValue(result[0])
            self._lon_spin.setValue(result[1])
            self._lat_spin.blockSignals(False)
            self._lon_spin.blockSignals(False)

    def _latlon_to_locator(self):
        loc = latlon_to_locator(self._lat_spin.value(), self._lon_spin.value())
        self._loc_edit.blockSignals(True)
        self._loc_edit.setText(loc)
        self._loc_edit.blockSignals(False)

    def _reset_layout(self):
        from PySide6.QtWidgets import QMessageBox
        if QMessageBox.question(
                self, "Layout resetten",
                "Alle panels terugzetten naar standaard positie?",
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            parent = self.parent()
            if parent and hasattr(parent, '_reset_layout'):
                parent._reset_layout()

    # ── Live-toepassen ────────────────────────────────────────────────────────
    def _live(self, debounce_ms: int = 0):
        """Activeer directe toepassing (met optionele debounce voor zware ops)."""
        if self._loading:
            return
        if debounce_ms > 0:
            self._debounce.start(debounce_ms)
        else:
            self._debounce.stop()
            self._do_apply()

    def _do_apply(self):
        self._cfg = self._collect_cfg()
        self.applied.emit(self._cfg)

    def _play_pitch_preview(self, pitch: int, duration: int) -> None:
        """Play preview sound when pitch/duration spinboxes change."""
        try:
            import winsound
            winsound.Beep(pitch, duration)
        except Exception:
            pass

    def _connect_live_controls(self):
        """Verbind alle controls voor live toepassing na _load_cfg."""
        # Checkboxen en combo's: direct
        for cb in [self._cb_night, self._cb_grayline, self._cb_aurora,
                   self._cb_sun, self._cb_moon, self._cb_lightn,
                   self._cb_dxspots, self._cb_locator,
                   self._splash_about, self._k_en,
                   self._xflare_en, self._band_en,
                   self._day_auto_cb,
                   self._cat_en, self._cat_rtscts, self._cat_dtr, self._cat_rts,
                   self._cb_lightn_en, self._lightn_beep_cb, self._sat_ping_cb]:
            cb.toggled.connect(lambda: self._live(0))
        # Synchroniseer de twee bliksem-checkboxes (Kaart ↔ Bliksem tab)
        self._cb_lightn.toggled.connect(
            lambda v: self._cb_lightn_en.setChecked(v)
            if self._cb_lightn_en.isChecked() != v else None)
        self._cb_lightn_en.toggled.connect(
            lambda v: self._cb_lightn.setChecked(v)
            if self._cb_lightn.isChecked() != v else None)
        # Panel checkboxes moved to header panel chooser dialog
        for combo in [self._mode_cb, self._power_cb, self._ant_cb, self._snap_cb,
                      self._cat_baud, self._cat_bits, self._cat_parity,
                      self._cat_stop, self._cat_type]:
            combo.currentIndexChanged.connect(lambda: self._live(0))
        # Tekstvelden: bij verlaten
        for le in [self._call_edit, self._loc_edit]:
            le.editingFinished.connect(lambda: self._live(0))
        # cat_port is een editable combobox — gebruik lineEdit signal
        if hasattr(self, "_cat_port") and self._cat_port.lineEdit():
            self._cat_port.lineEdit().editingFinished.connect(lambda: self._live(0))
        self._cat_port.currentIndexChanged.connect(lambda: self._live(0))
        # Spinboxen: 400ms debounce
        for spin in [self._lat_spin, self._lon_spin, self._k_spin,
                     self._band_spin, self._alert_max_spin, self._fade_spin,
                     self._lightn_radius_spin, self._lightn_rate_spin,
                     self._lightn_beep_r_spin, self._lightn_anim_scale_spin,
                     self._font_spin, self._maid_font_spin, self._sat_font_spin,
                     self._sat_path_width_spin,
                     self._callsign_font_spin,
                     self._dx_map_font_spin, self._dx_font_spin,
                     self._sun_size_spin, self._moon_size_spin,
                     self._cat_civ]:
            spin.valueChanged.connect(lambda: self._live(400))
        self._grat_step_cb.currentIndexChanged.connect(lambda: self._live(0))

        # Dynamic preview for lightning sound pitch/duration
        # Alert zone sounds
        self._lightn_pitch_spin.valueChanged.connect(
            lambda: self._play_pitch_preview(
                self._lightn_pitch_spin.value(),
                self._lightn_duration_spin.value()
            )
        )
        self._lightn_duration_spin.valueChanged.connect(
            lambda: self._play_pitch_preview(
                self._lightn_pitch_spin.value(),
                self._lightn_duration_spin.value()
            )
        )
        # Normal zone sounds
        self._lightn_beep_pitch_spin.valueChanged.connect(
            lambda: self._play_pitch_preview(
                self._lightn_beep_pitch_spin.value(),
                self._lightn_beep_duration_spin.value()
            )
        )
        self._lightn_beep_duration_spin.valueChanged.connect(
            lambda: self._play_pitch_preview(
                self._lightn_beep_pitch_spin.value(),
                self._lightn_beep_duration_spin.value()
            )
        )

    def _open_cat_monitor_from_settings(self):
        """Open CAT monitor venster vanuit de instellingen."""
        from .cat_interface import get_instance
        from .cat_monitor import CatMonitorWindow
        cat = get_instance()
        if cat is None:
            return
        if not hasattr(self, "_cat_mon_win") or self._cat_mon_win is None \
                or not self._cat_mon_win.isVisible():
            self._cat_mon_win = CatMonitorWindow(cat)
            self._cat_mon_win.show()
        else:
            self._cat_mon_win.raise_()
            self._cat_mon_win.activateWindow()

    def _on_ok(self):
        self._do_apply()
        self.accept()

    def _on_cancel(self):
        # Herstel originele instellingen
        if self._original_cfg:
            self.applied.emit(self._original_cfg)
        self.reject()

    def current_config(self) -> AppConfig:
        return self._cfg


# ── Hulpfuncties ──────────────────────────────────────────────────────────────

def _set_combo(cb: QComboBox, value: str, default: str):
    idx = cb.findText(value)
    cb.setCurrentIndex(idx if idx >= 0 else cb.findText(default))


def _set_combo_data(cb: QComboBox, value, default):
    for i in range(cb.count()):
        if cb.itemData(i) == value:
            cb.setCurrentIndex(i)
            return
    cb.setCurrentIndex(0)


# Yaesu/Kenwood radio-ID codes (ID; antwoord zonder puntkomma)
_RADIO_ID_MAP = {
    "ID0310": "Yaesu FT-950",
    "ID0650": "Yaesu FT-2000",
    "ID0670": "Yaesu FTDX-5000",
    "ID0680": "Yaesu FTDX-3000",
    "ID0920": "Yaesu FTDX-101",
    "ID019":  "Kenwood TS-590S",
    "ID021":  "Kenwood TS-590SG",
    "ID018":  "Kenwood TS-480",
    "ID023":  "Kenwood TS-890S",
}


def _friendly_serial_error(msg: str) -> str:
    """Vertaal een pyserial-foutmelding naar een begrijpelijke Nederlandse tekst."""
    m = msg.lower()
    if "permissionerror" in m or "access is denied" in m or "[errno 13]" in m or "error(13" in m:
        return "Toegang geweigerd — poort al in gebruik door ander programma"
    if "filenotfounderror" in m or "cannot find the file" in m or "no such file" in m:
        return "Poort niet gevonden — controleer de poortnaam"
    if "seriaalexception" in m or "serialexception" in m:
        return f"Serieel fout: {msg}"
    if "timed out" in m or "timeout" in m:
        return "Time-out — geen reactie van radio"
    return msg


def _get_cat_port(cb: QComboBox) -> str:
    """Lees de geselecteerde/ingetypte poort uit een editable QComboBox."""
    txt = cb.currentText().strip()
    # Als het item een beschrijving heeft ("COM3  —  USB Serial"), gebruik alleen het poortdeel
    if "  —  " in txt:
        txt = txt.split("  —  ")[0].strip()
    # Gebruik itemData als het beschikbaar is (=pure poortnaam)
    data = cb.currentData()
    if data and isinstance(data, str):
        return data.strip()
    return txt


def _set_cat_port(cb: QComboBox, port: str):
    """Stel de poort in op de editable combobox; zoek eerst in de lijst."""
    if not port:
        return
    for i in range(cb.count()):
        if cb.itemData(i) == port or cb.itemText(i).startswith(port + "  "):
            cb.setCurrentIndex(i)
            return
    cb.setEditText(port)


def _list_serial_ports() -> list[tuple[str, str]]:
    """Geef lijst van (port, beschrijving) voor alle beschikbare seriële poorten."""
    try:
        from serial.tools import list_ports
        return [(p.device, p.description or "") for p in sorted(
            list_ports.comports(), key=lambda p: p.device)]
    except ImportError:
        pass
    # Fallback als pyserial niet beschikbaar: scan Windows COM-poorten via registry
    import sys
    if sys.platform == "win32":
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"HARDWARE\DEVICEMAP\SERIALCOMM")
            ports = []
            i = 0
            while True:
                try:
                    _, val, _ = winreg.EnumValue(key, i)
                    ports.append((val, ""))
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
            return sorted(ports)
        except Exception:
            pass
    return []


_IMPORT_MAP = {"pyserial": "serial", "websocket-client": "websocket", "timezonefinder": "timezonefinder"}


def _check_dep(pkg: str) -> bool:
    import_name = _IMPORT_MAP.get(pkg, pkg.replace("-", "_"))
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def _copy_to_clipboard(text: str):
    try:
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
    except Exception:
        pass
