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
from PySide6.QtCore import Qt, QRect, QSize, QTimer, QObject, Signal
from PySide6.QtGui import QColor, QPalette


class _FreqBridge(QObject):
    """Thread-safe brug: achtergrond-poll → GUI-signaal."""
    freq_changed = Signal(object)   # int (Hz) of None

from .theme import BG_ROOT, BG_PANEL, QSS
from . import theme as _theme
from .i18n import tr, set_language, get_language, language_changed
from .header import HeaderBar
from .panel import FloatingPanel
from .mapview import MapView
from .charts import NoaaDataManager, KpChart, BzChart, XrayChart, SolarParamsWidget
from .panels5 import (
    BandRelWidget, BandCondWidget, StormFcWidget, BandSchedWidget,
    BandHistChart, SolarHistChart, LightningPanel, AlertsWidget,
    DXSpotsTable, PropAdvWidget, MUFWidget, WSPRTableWidget,
)
from .config import AppConfig, load_config, save_config
from .profiel_manager import ProfileManager
from .settings_dialog import SettingsDialog
from .sat_dialog import SatelliteDialog
from . import history as _history
from .spy_dialog import SpyStationsDialog
from .eibi_dialog import EibiDialog
from .ft8_dialog import Ft8Dialog
from .help_dialog import HelpDialog
from .antenna_calculator.antenna_calculator import AntennaCalculator
from . import cat_interface as _cat_mod

# Pad naar layouts-bestand (gedeeld met v4)
from ._appdir import APP_DIR as _HERE
_LAYOUTS_FILE = os.path.join(_HERE, "config", "hamios_layouts.json")  # legacy + panels
_CONFIG_FILE  = os.path.join(_HERE, "config", "hamios_config.json")


def _read_layouts() -> dict:
    """Lees layouts: eerst config, dan legacy JSON."""
    try:
        if os.path.exists(_CONFIG_FILE):
            with open(_CONFIG_FILE, encoding="utf-8") as f:
                d = json.load(f)
            if d.get("layouts"):
                return d["layouts"]
    except Exception:
        pass
    try:
        if os.path.exists(_LAYOUTS_FILE):
            with open(_LAYOUTS_FILE, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _write_layouts(data: dict):
    """Schrijf layouts naar config én legacy JSON."""
    try:
        cfg_data = {}
        if os.path.exists(_CONFIG_FILE):
            with open(_CONFIG_FILE, encoding="utf-8") as f:
                cfg_data = json.load(f)
        cfg_data["layouts"] = data
        with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    try:
        with open(_LAYOUTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# Standaard paneel-layout voor v5 (scherm-relatief t.o.v. desktop-canvas)
_PANEL_DEFAULTS = {
    "worldmap":   (440,  0,    740, 490, True),
    "solar":      (1190, 0,    370, 600, True),
    "band_rel":   (0,    0,    430, 600, True),
    "band_cond":  (0,    500,  200, 400, True),
    "storm_fc":   (0,    910,  200, 140, True),
    "band_sched": (440,  500,  370, 290, True),
    "band_hist":  (820,  500,  370, 290, True),
    "muf_forecast": (1200, 500, 370, 290, True),
    "solar_hist": (820,  800,  370, 120, True),
    "kp_48h":     (440,  800,  370, 270, True),
    "bz_24h":     (820,  800,  370, 200, True),
    "xray_24h":   (820, 1010,  370, 200, True),
    "lightning":  (1200, 800,  370, 300, True),
    "wspr_feed":  (440, 1100,  740, 300, True),
    "alerts":     (0,    500,  200, 280, True),
    "dx_spots":   (1200, 610,  370, 460, True),
    "prop_adv":   (0,    610,  430, 460, True),
}

_PANEL_TITLE_KEYS = {
    "worldmap":   "panel.map",
    "solar":      "panel.solar",
    "band_rel":   "panel.band_rel",
    "band_cond":  "panel.band_cond",
    "storm_fc":   "panel.storm_fc",
    "band_sched": "panel.band_sched",
    "band_hist":  "panel.band_hist",
    "muf_forecast": "panel.muf_forecast",
    "solar_hist": "panel.solar_hist",
    "kp_48h":     "panel.kp",
    "bz_24h":     "panel.bz",
    "xray_24h":   "panel.xray",
    "lightning":  "panel.lightning",
    "wspr_feed":  "wspr.title",
    "alerts":     "panel.alerts",
    "dx_spots":   "panel.dx_spots",
    "prop_adv":   "panel.prop_adv",
}

def _panel_titles():
    from .i18n import tr as _tr
    return {pid: _tr(key) for pid, key in _PANEL_TITLE_KEYS.items()}

_PANEL_TITLES = _panel_titles()


def _clamp_window(win, wx: int, wy: int, ww: int, wh: int):
    """Herstel venstergeometrie maar zorg dat het altijd op het scherm past."""
    from PySide6.QtWidgets import QApplication as _QA
    screen = _QA.primaryScreen().availableGeometry()
    # Minimale afmetingen
    ww = max(900, min(ww, screen.width()))
    wh = max(600, min(wh, screen.height()))
    # Positie: minimaal 30px van bovenkant (zodat titelbar bereikbaar is)
    wx = max(screen.x(), min(wx, screen.x() + screen.width()  - ww))
    wy = max(screen.y() + 30, min(wy, screen.y() + screen.height() - wh))
    win.setGeometry(wx, wy, ww, wh)


def _sat_elevation(sat_lat: float, sat_lon: float, alt_km: float,
                   qth_lat: float, qth_lon: float, R: float = 6371.0) -> float:
    """Bereken elevatiehoek (graden) van satelliet gezien vanuit QTH (v4-formule)."""
    import math
    sl = math.radians(sat_lat); ql = math.radians(qth_lat)
    dlon = math.radians(sat_lon - qth_lon)
    cos_d = math.sin(sl)*math.sin(ql) + math.cos(sl)*math.cos(ql)*math.cos(dlon)
    dist  = math.acos(max(-1.0, min(1.0, cos_d)))
    rho   = math.acos(min(1.0, R / (R + alt_km)))
    if math.sin(rho) < 1e-9:
        return 90.0
    return math.degrees(math.asin(min(1.0,
        (math.cos(dist) - R / (R + alt_km)) / math.sin(rho))))


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
        self.setWindowTitle("HF Propagation & Atmosphere Monitor")
        self.setMinimumSize(900, 600)
        # Initiële grootte en centrering — begrensd tot beschikbaar schermgebied
        from PySide6.QtWidgets import QApplication as _QApp
        _scr = _QApp.primaryScreen().availableGeometry()
        _w   = min(1600, _scr.width())
        _h   = min(900,  _scr.height() - 60)   # 60px vrij voor taakbalk
        self.resize(_w, _h)
        self.move(
            _scr.x() + max(0, (_scr.width()  - _w) // 2),
            _scr.y() + max(30, (_scr.height() - _h) // 2)
        )

        # Stylesheet
        # QSS + pijlen worden al gezet in HAMIOS5.py na QApplication-aanmaak
        # Voeg eventueel ontbrekende QSS toe als de app anders gestart wordt
        if not QApplication.instance().styleSheet():
            QApplication.instance().setStyleSheet(QSS)

        # Header bovenaan
        self._header = HeaderBar()
        self._header.btn_exit.clicked.connect(self.close)
        self._header.btn_fullscreen.clicked.connect(self._toggle_fullscreen)
        self._header.btn_minimize.clicked.connect(self.showMinimized)
        self._header.refresh_interval_changed.connect(self._set_refresh_interval)
        # Herstel opgeslagen interval na aanmaak _data_mgr (zie verderop)

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

        # Config laden, taal instellen en snap-grid instellen
        self._cfg = load_config()
        set_language(getattr(self._cfg, "language", "nl"))
        _theme.PANEL_GRID = self._cfg.snap_grid

        # Bijhouden van geopende header-dialogen (meerdere tegelijk mogelijk)
        self._open_dlgs: dict[str, QDialog] = {}

        # Centrale NOAA data-manager (gedeeld tussen alle chart-panels)
        self._data_mgr = NoaaDataManager(self)
        self._data_mgr.next_refresh_changed.connect(self._header.set_next_refresh)
        self._data_mgr.solar_ready.connect(self._on_solar_for_history)

        # Verwijder oude history-regels bij opstart (in achtergrond)
        import threading as _thr
        _thr.Thread(target=_history.prune, daemon=True).start()

        # Pas opgeslagen refresh-interval toe op spinner en timer
        _saved_interval = getattr(self._cfg, "refresh_interval", 5)
        self._header.spin_refresh.setValue(_saved_interval)
        self._data_mgr.set_interval(_saved_interval)

        # Panels aanmaken
        self._panels: dict[str, FloatingPanel] = {}
        self._build_panels()

        # Layout laden
        self._load_layout()

        # CAT interface aanmaken
        self._cat = _cat_mod.CatInterface(self._cfg)
        _cat_mod.set_instance(self._cat)

        # Thread-safe freq bridge: poll-thread → header label
        self._freq_bridge = _FreqBridge()
        self._freq_bridge.freq_changed.connect(self._on_cat_freq)
        self._cat._freq_callback = self._freq_bridge.freq_changed.emit

        # Auto-verbinden bij opstart als ingeschakeld
        if getattr(self._cfg, "cat_enabled", False):
            QTimer.singleShot(1500, self._cat_autoconnect)

        # Config toepassen na layout laden
        QTimer.singleShot(200, self._apply_config)

        # Ensure config directories exist after initialization
        save_config(self._cfg)

    # ── Panels ────────────────────────────────────────────────────────────────
    def _build_panels(self):
        """Maak alle panels aan als kind-widgets van _desktop."""
        for pid, title in _PANEL_TITLES.items():
            p = FloatingPanel(title, panel_id=pid, parent=self._desktop)
            p.hide()
            self._panels[pid] = p

            if pid == "worldmap":
                self._build_worldmap_panel(p)
            elif pid == "kp_48h":
                self._build_kp_panel(p)
            elif pid == "bz_24h":
                self._build_bz_panel(p)
            elif pid == "xray_24h":
                self._build_xray_panel(p)
            elif pid == "solar":
                self._build_solar_panel(p)
            elif pid == "band_rel":
                self._build_band_rel_panel(p)
            elif pid == "band_cond":
                self._build_band_cond_panel(p)
            elif pid == "storm_fc":
                self._build_storm_fc_panel(p)
            elif pid == "band_sched":
                self._build_band_sched_panel(p)
            elif pid == "band_hist":
                self._build_band_hist_panel(p)
            elif pid == "muf_forecast":
                self._build_muf_forecast_panel(p)
            elif pid == "solar_hist":
                self._build_solar_hist_panel(p)
            elif pid == "lightning":
                self._build_lightning_panel(p)
            elif pid == "wspr_feed":
                self._build_wspr_panel(p)
            elif pid == "alerts":
                self._build_alerts_panel(p)
            elif pid == "dx_spots":
                self._build_dx_spots_panel(p)
            elif pid == "prop_adv":
                self._build_prop_adv_panel(p)
            else:
                self._build_placeholder(p, pid)

    def _build_worldmap_panel(self, panel: FloatingPanel):
        """Plaatst de echte MapView in het wereldkaart-paneel."""
        from PySide6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(panel.content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._map_view = MapView()
        layout.addWidget(self._map_view)

        # Aurora K-index via solar data
        self._data_mgr.solar_ready.connect(
            lambda d: self._map_view.set_k_index(
                float(str(d.get("k_index", "2")).replace("—", "2") or "2")
            )
        )

        # Knop-koppelingen
        self._header.btn_sat.clicked.connect(self._open_sat_dialog)
        self._header.btn_spy.clicked.connect(self._open_spy_dialog)
        self._header.btn_eibi.clicked.connect(self._open_eibi_dialog)
        self._header.btn_ft8.clicked.connect(self._open_ft8_dialog)
        self._header.btn_overlay.clicked.connect(self._open_overlay_menu)
        self._header.btn_panels.clicked.connect(self._open_panel_chooser)
        self._header.btn_tools.clicked.connect(self._open_antenna_calculator_dialog)
        self._header.btn_help.clicked.connect(self._open_help)
        self._header.btn_settings.clicked.connect(self._open_settings)



    def _build_kp_panel(self, panel: FloatingPanel):
        from PySide6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(panel.content)
        layout.setContentsMargins(4, 4, 4, 4)
        chart = KpChart()
        layout.addWidget(chart)
        self._data_mgr.kp_ready.connect(chart.set_data)

    def _build_bz_panel(self, panel: FloatingPanel):
        from PySide6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(panel.content)
        layout.setContentsMargins(4, 4, 4, 4)
        chart = BzChart()
        layout.addWidget(chart)
        self._data_mgr.bz_ready.connect(chart.set_data)

    def _build_xray_panel(self, panel: FloatingPanel):
        from PySide6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(panel.content)
        layout.setContentsMargins(4, 4, 4, 4)
        chart = XrayChart()
        layout.addWidget(chart)
        self._data_mgr.xray_ready.connect(chart.set_data)

    def _build_solar_panel(self, panel: FloatingPanel):
        from PySide6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(panel.content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        solar = SolarParamsWidget()
        layout.addWidget(solar)
        layout.addStretch()
        self._data_mgr.solar_ready.connect(solar.set_data)

    # ── Sprint 5 panel builders ───────────────────────────────────────────────
    def _sprint5_layout(self, panel):
        from PySide6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(panel.content)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)
        return layout

    def _build_band_rel_panel(self, panel):
        w = BandRelWidget(cfg=self._cfg)
        self._sprint5_layout(panel).addWidget(w)
        self._data_mgr.solar_ready.connect(w.set_data)
        w.settings_changed.connect(self._on_panel_settings_changed)
        self._band_rel_widget = w

    def _build_band_cond_panel(self, panel):
        layout = self._sprint5_layout(panel)
        w = BandCondWidget(cfg=self._cfg)
        layout.addWidget(w)
        layout.addStretch()
        self._data_mgr.solar_ready.connect(w.set_data)
        self._band_cond_widget = w

    def _build_storm_fc_panel(self, panel):
        layout = self._sprint5_layout(panel)
        w = StormFcWidget()
        layout.addWidget(w)
        layout.addStretch()
        self._data_mgr.storm_ready.connect(w.set_data)

    def _build_band_sched_panel(self, panel):
        layout = self._sprint5_layout(panel)
        w = BandSchedWidget(cfg=self._cfg)
        layout.addWidget(w)
        self._data_mgr.solar_ready.connect(w.set_data)
        self._band_sched_widget = w

    def _build_band_hist_panel(self, panel):
        w = BandHistChart()
        self._sprint5_layout(panel).addWidget(w)
        self._data_mgr.solar_ready.connect(w.set_data)

    def _build_muf_forecast_panel(self, panel):
        w = MUFWidget(cfg=self._cfg)
        self._sprint5_layout(panel).addWidget(w)
        self._data_mgr.solar_ready.connect(w.set_data)
        self._muf_widget = w

    def _build_solar_hist_panel(self, panel):
        w = SolarHistChart()
        self._sprint5_layout(panel).addWidget(w)
        self._data_mgr.solar_ready.connect(w.set_data)

    def _build_lightning_panel(self, panel):
        w = LightningPanel(self._map_view._lightning, cfg=self._cfg)
        self._sprint5_layout(panel).addWidget(w)
        w.settings_changed.connect(self._on_panel_settings_changed)
        # QRN-meldingen doorsturen naar meldingen-paneel (wordt later gekoppeld)
        self._lightning_panel_widget = w

    def _build_wspr_panel(self, panel):
        from .wspr_feed import WSPRFeed
        w = WSPRTableWidget()
        self._sprint5_layout(panel).addWidget(w)
        # Start WSPR feed
        feed = WSPRFeed(self._cfg.qth_lat if self._cfg else 52.0,
                       self._cfg.qth_lon if self._cfg else 5.0)
        w.set_wspr_feed(feed)
        feed.start()
        self._wspr_feed = feed
        self._wspr_table_widget = w

    def _build_alerts_panel(self, panel):
        layout = self._sprint5_layout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        w = AlertsWidget(cfg=self._cfg)
        layout.addWidget(w)
        self._data_mgr.alerts_ready.connect(w.set_data)
        self._data_mgr.solar_ready.connect(w.set_solar_data)
        self._alerts_widget = w

        # QRN-meldingen van het onweer-paneel doorsturen
        if hasattr(self, "_lightning_panel_widget"):
            self._lightning_panel_widget.qrn_alert.connect(
                lambda icon, txt, clr: w.add_alert(icon, txt, clr, tr("alert.qrn_source")))

        # Satelliet-zone check elke 30s (referentie bewaren!)
        self._sat_zone_timer = QTimer(self)
        self._sat_zone_timer.timeout.connect(self._check_sat_zone)
        self._sat_zone_timer.start(30_000)
        QTimer.singleShot(5000, self._check_sat_zone)

        # Satelliet QTH-zone state (lazy-init in _check_sat_zone)
        self._sat_zone_prev: dict[str, bool] = {}

        # Onweer-straal controle elke 10s
        self._lightning_alert_timer = QTimer(self)
        self._lightning_alert_timer.timeout.connect(self._check_lightning_proximity)
        self._lightning_alert_timer.start(10_000)

    def _build_dx_spots_panel(self, panel):
        layout = self._sprint5_layout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        w = DXSpotsTable(cfg=self._cfg)
        layout.addWidget(w)
        self._map_view._dx_spots.spots_updated.connect(w.set_data)
        w.settings_changed.connect(self._on_panel_settings_changed)
        # Synchroniseer kaartfilter met tabelfilter bij elke wijziging
        w.settings_changed.connect(self._sync_dx_map_filter)
        self._dx_spots_widget = w
        # Initieel filter toepassen
        self._sync_dx_map_filter()

    def _build_prop_adv_panel(self, panel):
        w = PropAdvWidget(cfg=self._cfg)
        self._sprint5_layout(panel).addWidget(w)
        self._data_mgr.solar_ready.connect(w.set_data)
        w.analysis_changed.connect(self._on_analysis_changed)
        self._prop_adv_widget = w

    def _on_analysis_changed(self, changed_tips: list):
        """Stuur gewijzigde analyse-kaarten naar het meldingen-paneel."""
        if not hasattr(self, "_alerts_widget"):
            return
        for icon, text, color in changed_tips[:3]:  # max 3 tegelijk
            self._alerts_widget.add_alert(icon, text[:60], color,
                                          tr("alert.prop_changed"))

    def _on_settings_applied(self, cfg: AppConfig):
        self._cfg = cfg
        _theme.PANEL_GRID = cfg.snap_grid

        # Taal wisselen — herlaad alle paneeltitels en UI-teksten
        new_lang = getattr(cfg, "language", "nl")
        if new_lang != get_language():
            set_language(new_lang)
            self._retranslate_panels()
            self._header.retranslate()

        # Kaart en lagen
        self.set_qth(cfg.qth_lat, cfg.qth_lon)
        self._map_view.set_lightning_fade(cfg.lightning_fade)
        self._map_view.set_lightning_enabled(cfg.show_lightning)   # volledige aan/uit (verbinding)
        self._map_view.set_lightning_visible(getattr(cfg, "lightning_overlay_visible", True))  # overlay zichtbaarheid
        self._map_view.set_lightning_font_size(getattr(cfg, "lightning_font_size", 7))
        _lon = cfg.show_lightning
        self._map_view.set_lightning_radius(
            int(getattr(cfg, "lightning_beep_r", 0)) if _lon else 0)
        self._map_view.set_lightning_beep_radius(
            int(getattr(cfg, "lightning_warn_radius", 0)) if _lon else 0)
        self._map_view._lightning.set_cfg(cfg)
        self._map_view._lightning.set_anim_scale(
            getattr(cfg, "lightning_anim_scale", 2.0))
        rate = int(getattr(cfg, "lightning_rate", 500))
        self._map_view._lightning._timer.setInterval(max(100, rate))
        self._map_view.set_dx_spots_visible(cfg.show_dx_spots)
        self._map_view._night.setVisible(cfg.show_night)
        self._map_view.set_grayline_visible(cfg.show_grayline)
        self._map_view.set_aurora_visible(cfg.show_aurora)
        self._map_view.set_sun_visible(cfg.show_sun)
        self._map_view.set_moon_visible(cfg.show_moon)
        self._map_view.set_locator_visible(getattr(cfg, "show_locator", False))
        self._map_view._psk.setVisible(getattr(cfg, "show_psk", False))
        self._map_view.set_callsign_overlay_visible(getattr(cfg, "show_callsign_overlay", False))
        self._map_view.set_callsign_overlay_font_size(getattr(cfg, "callsign_overlay_font_size", 7))
        self._map_view.set_overlay_font_size(cfg.overlay_font_size)
        self._map_view.set_maidenhead_font_size(getattr(cfg, "maidenhead_font_size", 8))
        self._map_view.set_grat_step(getattr(cfg, "grat_step", 30))
        self._map_view.set_sun_size(getattr(cfg, "sun_icon_size", 24))
        self._map_view.set_moon_size(getattr(cfg, "moon_icon_size", 20))
        self._map_view.set_sat_font_size(getattr(cfg, "sat_font_size", 8))
        self._map_view.set_satellite_path_width(getattr(cfg, "sat_path_width", 1.2))
        self._map_view.set_dx_map_font_size(getattr(cfg, "dx_map_font_size", 7))

        # Sync cfg-referentie in ALLE panel-widgets die cfg bewaren
        _panel_widgets = [
            "_prop_adv_widget", "_band_rel_widget", "_band_cond_widget",
            "_dx_spots_widget", "_lightning_panel_widget", "_band_sched_widget",
            "_muf_widget", "_alerts_widget",
        ]
        for attr in _panel_widgets:
            w = getattr(self, attr, None)
            if w and hasattr(w, "set_cfg"):
                w.set_cfg(cfg)

        if hasattr(self, "_dx_spots_widget"):
            self._dx_spots_widget.set_font_size(cfg.dx_font_size)

        # WSPR Live panel font size
        if hasattr(self, "_wspr_table_widget") and self._wspr_table_widget:
            self._wspr_table_widget.set_font_size(getattr(cfg, "wspr_font_size", 9))

        # CAT: update cfg-referentie en herverbinden indien ingeschakeld
        if hasattr(self, "_cat"):
            self._cat._cfg = cfg
            self._cat._freq_callback = self._freq_bridge.freq_changed.emit
            _cat_mod.set_instance(self._cat)
            was_connected = self._cat.connected
            if getattr(cfg, "cat_enabled", False) and not self._cat.connected:
                self._cat.connect()
            elif not getattr(cfg, "cat_enabled", False) and self._cat.connected:
                self._cat.disconnect()
            self._update_cat_button()

        save_config(cfg)

    def _build_placeholder(self, panel: FloatingPanel, pid: str):
        """Tijdelijke lege content — wordt vervangen in latere sprints."""
        from PySide6.QtWidgets import QLabel, QVBoxLayout
        lbl = QLabel(f"[ {pid} ]")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(f"color: #404850; font-size: 10pt;")
        layout = QVBoxLayout(panel.content)
        layout.addWidget(lbl)

    # ── Layout opslaan/laden ──────────────────────────────────────────────────
    def _load_layout(self):
        """Laad panel-layout uit default-profiel (ProfielManager) of legacy."""
        saved = {}

        # Probeer eerst nieuwe ProfielManager
        default_profile = ProfileManager.get_default_profile()
        if default_profile and default_profile.layout:
            saved = default_profile.layout
        else:
            # Fallback: legacy systeem (hamios_config.json)
            try:
                data = _read_layouts()
                if "__default__" in data:
                    saved = data["__default__"]
            except Exception:
                pass

        # Venstergrootte herstellen
        if "__window__" in saved and len(saved["__window__"]) >= 4:
            wx, wy, ww, wh = saved["__window__"][:4]
            _clamp_window(self, int(wx), int(wy), int(ww), int(wh))

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
        # Sla op via ProfielManager (config + layout)
        from dataclasses import asdict
        config_dict = asdict(self._cfg)
        ProfileManager.set_default_profile(config_dict, layout)

        # Fallback: legacy systeem ook updaten
        try:
            data = _read_layouts()
            data["__default__"] = layout
            _write_layouts(data)
        except Exception as e:
            print(f"Layout save failed: {e}")

    # ── Config toepassen ─────────────────────────────────────────────────────
    def _apply_config(self):
        """Pas ingeladen config toe op kaart, lagen en panels."""
        c = self._cfg
        self.set_qth(c.qth_lat, c.qth_lon)
        self._map_view.set_overlay_font_size(c.overlay_font_size)
        self._map_view.set_maidenhead_font_size(getattr(c, "maidenhead_font_size", 8))
        self._map_view.set_grat_step(getattr(c, "grat_step", 30))
        self._map_view.set_sun_size(getattr(c, "sun_icon_size", 24))
        self._map_view.set_moon_size(getattr(c, "moon_icon_size", 20))
        self._map_view.set_sat_font_size(getattr(c, "sat_font_size", 8))
        self._map_view.set_satellite_path_width(getattr(c, "sat_path_width", 1.2))
        self._map_view.set_dx_map_font_size(getattr(c, "dx_map_font_size", 7))
        if hasattr(self, "_dx_spots_widget"):
            self._dx_spots_widget.set_font_size(c.dx_font_size)
        if hasattr(self, "_wspr_table_widget") and self._wspr_table_widget:
            self._wspr_table_widget.set_font_size(getattr(c, "wspr_font_size", 9))
        self._map_view.set_lightning_fade(c.lightning_fade)
        self._map_view.set_lightning_enabled(c.show_lightning)   # volledige aan/uit (verbinding)
        self._map_view.set_lightning_visible(getattr(c, "lightning_overlay_visible", True))  # overlay zichtbaarheid
        self._map_view.set_lightning_font_size(getattr(c, "lightning_font_size", 7))
        _lon = c.show_lightning
        self._map_view.set_lightning_radius(
            int(getattr(c, "lightning_beep_r", 0)) if _lon else 0)
        self._map_view.set_lightning_beep_radius(
            int(getattr(c, "lightning_warn_radius", 0)) if _lon else 0)
        self._map_view._lightning.set_cfg(c)
        self._map_view._lightning.set_anim_scale(
            getattr(c, "lightning_anim_scale", 2.0))
        self._map_view.set_dx_spots_visible(c.show_dx_spots)
        self._sync_dx_map_filter()
        self._map_view._night.setVisible(c.show_night)
        # Uren altijd instellen (ook als geen satellites geselecteerd)
        self._map_view.set_satellite_hours(
            getattr(c, "sat_back_h", 1),
            getattr(c, "sat_fwd_h",  12))
        self._map_view.set_satellite_visible(getattr(c, "sat_visible", False))
        if c.sat_selected:
            self._map_view.set_satellite_selection(set(c.sat_selected))
            self._map_view.set_satellite_paths(set(c.sat_path))
            self._map_view.set_satellite_footprints(set(getattr(c, "sat_fp", [])))
        self._map_view.set_grayline_visible(c.show_grayline)
        self._map_view.set_aurora_visible(c.show_aurora)
        self._map_view.set_sun_visible(c.show_sun)
        self._map_view.set_moon_visible(c.show_moon)
        self._map_view.set_graticule_visible(True)
        self._map_view.set_locator_visible(getattr(c, "show_locator", False))
        self._map_view._psk.setVisible(getattr(c, "show_psk", False))
        self._map_view.set_callsign_overlay_visible(getattr(c, "show_callsign_overlay", False))
        self._map_view.set_callsign_overlay_font_size(getattr(c, "callsign_overlay_font_size", 7))

    # ── Retranslate ───────────────────────────────────────────────────────────
    def _sync_dx_map_filter(self):
        """Synchroniseer het kaart-DX-filter met de tabelinstelling."""
        own_only = getattr(self._cfg, "dx_own_continent", False)
        self._map_view._dx_spots.set_continent_filter(
            own_only, self._cfg.qth_lat, self._cfg.qth_lon)

    def _retranslate_panels(self):
        """Update paneeltitels en widget-teksten na taalwisseling."""
        titles = _panel_titles()
        for pid, panel in self._panels.items():
            if pid in titles:
                panel.set_title(titles[pid])
        # language_changed signal zorgt voor directe update in verbonden widgets
        # (StormFcWidget.retranslate, HelpDialog._on_language_changed, etc.)

    # ── Instellingen-dialoog ──────────────────────────────────────────────────
    # ── Helper: toon dialoog niet-modaal, meerdere tegelijk mogelijk ────────────

    def _show_dialog(self, key: str, dlg: "QDialog"):
        """Toon dialoog niet-modaal boven het hoofdvenster.
        Bij herhaald klikken: bestaand venster naar voren brengen."""
        existing = self._open_dlgs.get(key)
        if existing and existing.isVisible():
            existing.raise_()
            existing.activateWindow()
            return
        dlg.setWindowFlag(Qt.Window, True)
        dlg.setAttribute(Qt.WA_DeleteOnClose, True)
        dlg.destroyed.connect(lambda _=None, k=key: self._open_dlgs.pop(k, None))
        self._open_dlgs[key] = dlg
        dlg.show()
        dlg.raise_()
        dlg.activateWindow()

    def _open_help(self):
        self._show_dialog("help", HelpDialog(self))

    def _open_spy_dialog(self):
        self._show_dialog("spy", SpyStationsDialog(self))

    def _open_eibi_dialog(self):
        self._show_dialog("eibi", EibiDialog(self))

    def _open_ft8_dialog(self):
        self._show_dialog("ft8", Ft8Dialog(self))

    def _open_antenna_calculator_dialog(self):
        """Open the antenna calculator."""
        calculator = AntennaCalculator(self)
        calculator.exec()

    def _open_overlay_menu(self):
        """Modeless overlay selection panel (multiple toggles, stays open)."""
        from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                                       QCheckBox, QPushButton, QLabel)
        from PySide6.QtCore import Qt, QPoint

        # Check if dialog already open
        if hasattr(self, "_overlay_dialog") and self._overlay_dialog.isVisible():
            self._overlay_dialog.raise_()
            self._overlay_dialog.activateWindow()
            return

        # Create custom dialog that closes on focus loss
        class AutoCloseDialog(QDialog):
            def focusOutEvent(self, event):
                super().focusOutEvent(event)
                self.close()

        dialog = AutoCloseDialog(self, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        dialog.setStyleSheet(
            f"QDialog {{ background: #1A1D22; border: 1px solid #404850; border-radius: 5px; }}"
            f"QCheckBox {{ color: #C8C8D0; }}"
            f"QLabel {{ color: #C8D0DC; }}"
            f"QPushButton {{ background: #C8A84B; color: #1A1D22; font-weight: bold; "
            f"border: none; border-radius: 3px; padding: 4px 12px; }}"
            f"QPushButton:hover {{ background: #E0C060; }}"
        )

        vlay = QVBoxLayout(dialog)
        vlay.setContentsMargins(12, 12, 12, 12)
        vlay.setSpacing(8)

        # Title
        title = QLabel(tr("hdr.overlays"))
        title.setStyleSheet("color: #C8A84B; font-weight: bold;")
        vlay.addWidget(title)

        # Overlay checkboxes
        overlays = [
            (tr("ov.night"),     "show_night",    lambda v: self._map_view._night.setVisible(v)),
            (tr("ov.grayline"),  "show_grayline", lambda v: self._map_view.set_grayline_visible(v)),
            (tr("ov.aurora"),    "show_aurora",   lambda v: self._map_view.set_aurora_visible(v)),
            (tr("ov.sun"),       "show_sun",      lambda v: self._map_view.set_sun_visible(v)),
            (tr("ov.moon"),      "show_moon",     lambda v: self._map_view.set_moon_visible(v)),
            (tr("ov.lightning"), "lightning_overlay_visible", lambda v: (
                self._map_view.set_lightning_visible(v),
                self._map_view.set_lightning_radius(
                    int(getattr(self._cfg, "lightning_beep_r", 0)) if v else 0),
                self._map_view.set_lightning_beep_radius(
                    int(getattr(self._cfg, "lightning_warn_radius", 0)) if v else 0),
            )),
            (tr("ov.dx_spots"),  "show_dx_spots", lambda v: self._map_view.set_dx_spots_visible(v)),
            (tr("ov.satellites"),"sat_visible",   lambda v: self._map_view.set_satellite_visible(v)),
            (tr("ov.locator"),   "show_locator",  lambda v: self._map_view.set_locator_visible(v)),
            (tr("ov.psk"),       "show_psk",      lambda v: self._map_view._psk.setVisible(v)),
            (tr("ov.callsign"),  "show_callsign_overlay",
             lambda v: self._map_view.set_callsign_overlay_visible(v)),
        ]

        for label, attr, fn in overlays:
            cb = QCheckBox(label)
            cb.setChecked(bool(getattr(self._cfg, attr, False)))
            cb.toggled.connect(
                lambda v, a=attr, f=fn: (setattr(self._cfg, a, v), f(v),
                                         save_config(self._cfg)))
            vlay.addWidget(cb)

        vlay.addSpacing(6)

        # OK button
        hlay = QHBoxLayout()
        hlay.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.setFixedWidth(80)
        ok_btn.clicked.connect(dialog.accept)
        hlay.addWidget(ok_btn)
        vlay.addLayout(hlay)

        dialog.adjustSize()

        # Position near button (top-right)
        btn = self._header.btn_overlay
        pos = btn.mapToGlobal(QPoint(btn.width() - dialog.width(), btn.height() + 4))
        dialog.move(pos)

        self._overlay_dialog = dialog
        dialog.setAttribute(Qt.WA_DeleteOnClose, False)
        dialog.show()

    def _open_panel_chooser(self):
        """Modeless panel visibility selector."""
        from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                                       QCheckBox, QPushButton, QLabel)
        from PySide6.QtCore import Qt, QPoint

        # Check if dialog already open
        if hasattr(self, "_panel_dialog") and self._panel_dialog.isVisible():
            self._panel_dialog.raise_()
            self._panel_dialog.activateWindow()
            return

        # Create custom dialog that closes on focus loss
        class AutoCloseDialog(QDialog):
            def focusOutEvent(self, event):
                super().focusOutEvent(event)
                self.close()

        dialog = AutoCloseDialog(self, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        dialog.setStyleSheet(
            f"QDialog {{ background: #1A1D22; border: 1px solid #404850; border-radius: 5px; }}"
            f"QCheckBox {{ color: #C8C8D0; }}"
            f"QLabel {{ color: #C8D0DC; }}"
            f"QPushButton {{ background: #C8A84B; color: #1A1D22; font-weight: bold; "
            f"border: none; border-radius: 3px; padding: 4px 12px; }}"
            f"QPushButton:hover {{ background: #E0C060; }}"
        )

        vlay = QVBoxLayout(dialog)
        vlay.setContentsMargins(12, 12, 12, 12)
        vlay.setSpacing(8)

        # Title
        title = QLabel("Panelen")
        title.setStyleSheet("color: #C8A84B; font-weight: bold;")
        vlay.addWidget(title)

        # Panel visibility checkboxes
        _PANEL_KEYS = [
            "worldmap", "solar", "band_rel", "band_cond", "storm_fc",
            "band_sched", "band_hist", "muf_forecast", "solar_hist", "kp_48h", "bz_24h",
            "xray_24h", "lightning", "alerts", "dx_spots", "wspr_feed", "prop_adv",
        ]

        for pid in _PANEL_KEYS:
            panel = self._panels.get(pid)
            cb = QCheckBox(tr(f"panels.{pid}"))
            cb.setChecked(panel.is_panel_visible() if panel else False)
            if panel:
                cb.toggled.connect(
                    lambda v, p=panel: (p.show_panel() if v else p.hide_panel(),
                                       save_config(self._cfg)))
            vlay.addWidget(cb)

        vlay.addSpacing(6)

        # OK button
        hlay = QHBoxLayout()
        hlay.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.setFixedWidth(80)
        ok_btn.clicked.connect(dialog.accept)
        hlay.addWidget(ok_btn)
        vlay.addLayout(hlay)

        dialog.adjustSize()

        # Position near button
        btn = self._header.btn_panels
        pos = btn.mapToGlobal(QPoint(btn.width() - dialog.width(), btn.height() + 4))
        dialog.move(pos)

        self._panel_dialog = dialog
        dialog.setAttribute(Qt.WA_DeleteOnClose, False)
        dialog.show()

    # ── CAT ───────────────────────────────────────────────────────────────────
    def _open_cat_dialog(self):
        """Open het CAT-venster (status + optionele terminal)."""
        self._open_cat_monitor()

    def _open_cat_monitor(self):
        """Open (of breng naar voren) het CAT monitor venster."""
        from .cat_monitor import CatMonitorWindow
        if not hasattr(self, "_cat_monitor") or self._cat_monitor is None \
                or not self._cat_monitor.isVisible():
            self._cat_monitor = CatMonitorWindow(self._cat)
            self._cat_monitor.show()
        else:
            self._cat_monitor.raise_()
            self._cat_monitor.activateWindow()

    def _cat_autoconnect(self):
        """Verbind bij opstart als cat_enabled=True."""
        self._cat._cfg = self._cfg
        ok, _ = self._cat.connect()
        self._update_cat_button()

    def _update_cat_button(self):
        self._header.set_cat_connected(self._cat.connected)
        if not self._cat.connected:
            self._header.set_radio_freq(None)

    def _on_cat_freq(self, freq_hz):
        """Ontvang frequentie-update van poll-thread (altijd op GUI-thread).

        freq_hz == None  → verbinding verbroken (poort dicht / exception)
        freq_hz == -1    → radio offline (poort open maar geen respons)
        freq_hz == 0     → verbonden maar freq onbekend (tijdelijk)
        freq_hz > 0      → geldige frequentie
        """
        self._header.set_radio_freq(freq_hz)
        # Verbindingsstatus: None = echt verbroken, anders = poort nog open
        self._header.set_cat_connected(freq_hz is not None)

    def _open_settings(self):
        dlg = SettingsDialog(
            self._cfg,
            panels=self._panels,
            mainwindow=self,
            parent=self)
        dlg.applied.connect(self._on_settings_applied)
        dlg.exec()

    def _on_solar_for_history(self, solar: dict):
        """Bereken bandpercentages en schrijf naar history-CSV."""
        import threading as _thr
        from .panels5 import (_calc_propagation_v4, BandRelWidget as _BRW,
                              _MODE_DB, _POWER_DB, _ANT_DB)
        try:
            sfi = float(str(solar.get("sfi",     "90")).replace("—", "90") or "90")
            ssn = float(str(solar.get("ssn",     "50")).replace("—", "50") or "50")
            k   = float(str(solar.get("k_index", "2" )).replace("—",  "2") or  "2")
        except (ValueError, TypeError):
            sfi, ssn, k = 90.0, 50.0, 2.0
        qth_lat = self._cfg.qth_lat
        qth_lon = self._cfg.qth_lon
        snr = (_MODE_DB.get(self._cfg.mode, 0) +
               _POWER_DB.get(self._cfg.power, 0) +
               _ANT_DB.get(getattr(self._cfg, "antenna", "Dipole ~2dBi"), 0))
        is_day  = _BRW._is_day_at_qth(qth_lat, qth_lon)
        bp, _, _ = _calc_propagation_v4(sfi, ssn, k, qth_lat, snr, is_day)
        band_pct = {name: pct for name, _, pct in bp}
        _thr.Thread(target=_history.append,
                    args=(band_pct, solar), daemon=True).start()

    def _set_refresh_interval(self, minutes: int):
        """Pas het data-verversinterval aan en sla op."""
        self._data_mgr.set_interval(minutes)
        self._cfg.refresh_interval = minutes
        save_config(self._cfg)

    def _on_sat_hours_live(self, back_h: int, fwd_h: int):
        """Live uren-wijziging: sla op in cfg én pas toe op de kaartlaag."""
        self._cfg.sat_back_h = back_h
        self._cfg.sat_fwd_h  = fwd_h
        self._map_view.set_satellite_hours(back_h, fwd_h)
        save_config(self._cfg)

    def _check_sat_zone(self):
        """Check welke satellieten zichtbaar zijn van het QTH, speel ping bij overgang."""
        if not hasattr(self, "_alerts_widget"):
            return
        import math, time as _time
        from .layers import _qth_in_footprint
        from .sound import play_sat_enter, play_sat_exit
        import threading as _th
        R = 6371.0
        sat = self._map_view._sat_layer
        with sat._lock:
            pos = dict(sat._positions)
            ql  = sat._qth_lat
            qn  = sat._qth_lon
        ping_en = getattr(self._cfg, "sat_zone_ping", True)

        # Lazy-init per-satelliet state (leeft op mainwindow, niet in de rekenthread)
        if not hasattr(self, "_sat_zone_prev"):
            self._sat_zone_prev: dict[str, bool] = {}

        visible = []
        now = _time.monotonic()
        for name, (lat, lon, alt) in pos.items():
            if alt <= 0:
                continue
            rho     = math.degrees(math.acos(min(1.0, R / (R + alt))))
            in_zone = _qth_in_footprint(lat, lon, rho, ql, qn)
            if in_zone:
                elev  = _sat_elevation(lat, lon, alt, ql, qn, R)
                short = name.split("(")[0].strip()[:20]
                visible.append(f"{short} ({elev:.0f}°)")

            was_in = self._sat_zone_prev.get(name)
            if was_in is None:
                # Eerste meting — state opslaan, geen ping
                self._sat_zone_prev[name] = in_zone
                continue
            if in_zone != was_in:
                self._sat_zone_prev[name] = in_zone
                short = name.split("(")[0].strip()[:20]
                # Alert
                if hasattr(self, "_alerts_widget"):
                    if in_zone:
                        self._alerts_widget.add_alert(
                            "🛰", tr("alerts.sat.enter", name=short),
                            "#4FC3F7", tr("alert.sat_zone"))
                    else:
                        self._alerts_widget.add_alert(
                            "🛰", tr("alerts.sat.exit", name=short),
                            "#7080A0", tr("alert.sat_zone"))
                # Ping — eenmalig in aparte thread
                if ping_en:
                    fn = play_sat_enter if in_zone else play_sat_exit
                    _th.Thread(target=fn, daemon=True).start()

        self._alerts_widget.set_sat_zone(visible)

    def _check_lightning_proximity(self):
        """Toon rode melding in header als onweer binnen de ingestelde straal is."""
        radius = int(getattr(self._cfg, "lightning_radius", 0))
        if radius <= 0:
            self._header.set_lightning_warning(None)
            return
        import math
        from .layers import MAP_W, MAP_H
        qlat = math.radians(self._cfg.qth_lat)
        qlon = math.radians(self._cfg.qth_lon)
        R = 6371.0
        with self._map_view._lightning._lock:
            strikes = list(self._map_view._lightning._strikes)
        if not strikes:
            self._header.set_lightning_warning(None)
            return
        min_km = None
        for x_px, y_px, _ in strikes:
            slat = math.radians(90 - y_px / MAP_H * 180)
            slon = math.radians(x_px / MAP_W * 360 - 180)
            dlat = slat - qlat; dlon = slon - qlon
            a = math.sin(dlat/2)**2 + math.cos(qlat)*math.cos(slat)*math.sin(dlon/2)**2
            km = 2 * R * math.asin(min(1.0, math.sqrt(a)))
            if min_km is None or km < min_km:
                min_km = km
        if min_km is not None and min_km <= radius:
            self._header.set_lightning_warning(
                tr("alert.lightning_hdr", km=min_km))
            if hasattr(self, "_alerts_widget"):
                import time as _t
                now_t = _t.time()
                last  = getattr(self, "_last_lightning_alert", 0)
                if now_t - last > 60:
                    self._last_lightning_alert = now_t
                    self._alerts_widget.add_alert(
                        "⚡",
                        tr("alert.lightning_msg", km=min_km),
                        "#EF5350",
                        tr("alert.lightning_det", radius=radius))
        else:
            self._header.set_lightning_warning(None)

    def _on_panel_settings_changed(self):
        """Sla config op en herbereken afhankelijke panels."""
        from .config import save_config
        save_config(self._cfg)
        # BandSchedWidget & MUFWidget herberekenen als mode/power/antenne wijzigt
        if hasattr(self, "_band_sched_widget"):
            self._band_sched_widget.set_cfg(self._cfg)
        if hasattr(self, "_muf_widget"):
            self._muf_widget.set_cfg(self._cfg)

    def _reset_layout(self):
        """Zet panels terug: eerst opgeslagen standaard, dan fabriekswaarden."""
        saved = {}
        try:
            data = _read_layouts()
            if "__default__" in data:
                saved = data["__default__"]
        except Exception:
            pass

        # Venstergrootte herstellen
        if "__window__" in saved and len(saved["__window__"]) >= 4:
            wx, wy, ww, wh = saved["__window__"][:4]
            _clamp_window(self, int(wx), int(wy), int(ww), int(wh))

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

    # ── Satelliet-dialoog ────────────────────────────────────────────────────
    def _open_sat_dialog(self):
        existing = self._open_dlgs.get("sat")
        if existing and existing.isVisible():
            existing.raise_()
            existing.activateWindow()
            return

        dlg = SatelliteDialog(
            self._cfg.sat_selected,
            self._cfg.sat_path,
            getattr(self._cfg, "sat_fp",         []),
            getattr(self._cfg, "sat_back_h",      1),
            getattr(self._cfg, "sat_fwd_h",       2),
            filter_sel=getattr(self._cfg, "sat_filter_sel", False),
            cfg=self._cfg,
            parent=self)
        dlg.selection_changed.connect(self._on_sat_selection)
        dlg.hours_changed.connect(self._on_sat_hours_live)
        dlg.live_pos_changed.connect(self._map_view.set_satellite_selection)
        dlg.live_path_changed.connect(self._map_view.set_satellite_paths)
        dlg.live_fp_changed.connect(self._map_view.set_satellite_footprints)

        def _load_tle_now():
            tle = {}
            for sats in dlg.tle_data.values():
                for row in sats:
                    if len(row) == 3:
                        tle[row[0]] = (row[1], row[2])
            if tle:
                self._map_view.update_tle(tle)

        from PySide6.QtCore import QTimer as _QT
        _QT.singleShot(200, _load_tle_now)
        dlg.accepted.connect(_load_tle_now)

        self._show_dialog("sat", dlg)

    def _on_sat_selection(self, selected: list, path: list,
                          fp: list, back_h: int, fwd_h: int):
        self._cfg.sat_selected = selected
        self._cfg.sat_path     = path
        # Extra config-velden opslaan (met fallback als ze niet bestaan)
        try:
            self._cfg.sat_fp     = fp
            self._cfg.sat_back_h = back_h
            self._cfg.sat_fwd_h  = fwd_h
        except AttributeError:
            pass
        save_config(self._cfg)
        self._map_view.set_satellite_selection(set(selected))
        self._map_view.set_satellite_paths(set(path))
        self._map_view.set_satellite_footprints(set(fp))
        self._map_view.set_satellite_hours(back_h, fwd_h)

    # ── TLE laden ─────────────────────────────────────────────────────────────
    def _ensure_tle_loaded(self):
        """Fetch TLE in background if not yet cached."""
        from .layers import TLE_GROUPS, fetch_tle_group, parse_tle_text, save_tle_cache, load_tle_cache
        import threading

        def _fetch():
            cache = load_tle_cache()
            if not cache:
                for group, url in TLE_GROUPS.items():
                    sats = fetch_tle_group(url)
                    if sats:
                        cache[group] = [[n, l1, l2] for n, l1, l2 in sats]
                save_tle_cache(cache)
            tle = {}
            for sats in cache.values():
                for row in sats:
                    tle[row[0]] = (row[1], row[2])
            if hasattr(self, "_map_view"):
                self._map_view.update_tle(tle)

        threading.Thread(target=_fetch, daemon=True).start()

    # ── Publieke interface ────────────────────────────────────────────────────
    def download_missing_maps(self) -> list:
        """Start downloads voor ontbrekende kaartbestanden."""
        return self._map_view.download_missing_maps()

    def set_qth(self, lat: float, lon: float):
        """Stel QTH-positie in op de kaart, satellietlaag en header-klok."""
        if hasattr(self, "_map_view"):
            self._map_view.set_qth(lat, lon)
            self._map_view._sat_layer.set_qth(lat, lon)
        if hasattr(self, "_header"):
            self._header.set_qth(lat, lon)

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
        save_config(self._cfg)
        # Stop achtergrond threads netjes voor Qt ze vernietigt
        self._data_mgr.stop()
        if hasattr(self, "_map_view"):
            self._map_view._lightning._worker.stop()
        if hasattr(self, "_wspr_feed"):
            self._wspr_feed.stop()
        if hasattr(self, "_cat"):
            self._cat.disconnect()
        super().closeEvent(event)
