"""HAMIOS v5 — Header balk (PySide6) — gelijk aan v4 stijl"""
import datetime

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFrame, QSpinBox
from PySide6.QtCore import QTimer, Signal
from PySide6.QtGui import QColor, QPalette

from .theme import ACCENT, BG_PANEL, TEXT_H1, TEXT_DIM, HDR_H, BG_SURFACE, BORDER
from .i18n import tr


class HeaderBar(QWidget):
    """Amber-geaccentueerde header — v4 stijl."""

    refresh_interval_changed = Signal(int)   # minuten (0 = uit)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("header")
        self.setFixedHeight(HDR_H)
        self.setAutoFillBackground(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(3)   # kleine ruimte tussen knoppen

        # Amber accent-balk links (4 px)
        bar = QFrame()
        bar.setFixedWidth(4)
        bar.setStyleSheet(f"background: {ACCENT};")
        layout.addWidget(bar)

        # Titel
        title = QLabel("📡  HF Propagation & Atmosphere Monitor")
        title.setObjectName("title")
        title.setStyleSheet(
            f"color: {ACCENT}; font-size: 13pt; font-weight: bold; padding: 0 10px;")
        layout.addWidget(title)

        # OFFLINE indicator (verborgen tot netfout)
        self._offline_lbl = QLabel("⚠ OFFLINE")
        self._offline_lbl.setStyleSheet(
            f"color: #EF5350; font-weight: bold; font-size: 9pt; padding: 0 6px;")
        self._offline_lbl.hide()
        layout.addWidget(self._offline_lbl)

        # Onweer-nabijheid waarschuwing (aparte label, onafhankelijk van OFFLINE)
        self._lightning_lbl = QLabel("")
        self._lightning_lbl.setStyleSheet(
            f"color: #EF5350; font-weight: bold; font-size: 9pt; padding: 0 6px;")
        self._lightning_lbl.hide()
        layout.addWidget(self._lightning_lbl)

        # Puls-timer voor de onweer-waarschuwing
        self._pulse_bright = True
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._pulse_lightning_lbl)
        self._pulse_timer.setInterval(600)

        # Linker knoppen
        self._btn_sat     = self._btn(tr("hdr.satellite"),   amber=True)
        self._btn_spy     = self._btn(tr("hdr.spystations"), amber=True)
        self._btn_eibi    = self._btn(tr("hdr.eibi"),        amber=True)
        self._btn_ft8     = self._btn(tr("hdr.ft8"),         amber=True)
        self._btn_overlay = self._btn(tr("hdr.overlays"),    amber=True)
        self._btn_overlay.setToolTip(tr("hdr.overlays.tip"))
        self._btn_panels = self._btn(tr("hdr.panels"),       amber=True)
        self._btn_panels.setToolTip(tr("hdr.panels"))
        self._btn_tools = self._btn("📡 Antenna", amber=True)
        self._btn_tools.setToolTip("HAM Antenna Designer")
        self._btn_exit     = self._btn(tr("app.close"), bg="#5A1010", hover="#8B1A1A")
        self._btn_settings = self._btn(tr("hdr.settings"), amber=True)

        # Refresh-interval spinbox + countdown
        _lbl_ref = QLabel("↻")
        _lbl_ref.setStyleSheet(f"color: {ACCENT}; font-size: 11pt; padding: 0 2px;")
        self._spin_refresh = QSpinBox()
        self._spin_refresh.setRange(0, 60)
        self._spin_refresh.setValue(5)
        self._spin_refresh.setSpecialValueText(tr("hdr.refresh.off"))
        self._spin_refresh.setFixedWidth(44)
        self._spin_refresh.setToolTip(tr("hdr.refresh.tip"))
        self._spin_refresh.valueChanged.connect(
            lambda v: self.refresh_interval_changed.emit(v))

        self._countdown_lbl = QLabel("")
        self._countdown_lbl.setStyleSheet(
            f"color: {ACCENT}; font-size: 9pt; padding: 0 4px;")
        self._countdown_lbl.setToolTip(tr("hdr.countdown.tip"))

        self._next_refresh_at: float = 0.0
        self._local_tz = _tz_from_latlon(52.0, 5.0)   # default NL; update via set_qth()

        for b in [self._btn_sat, self._btn_spy, self._btn_eibi,
                  self._btn_ft8, self._btn_overlay, self._btn_panels, self._btn_tools]:
            layout.addWidget(b)

        # Radio frequentie display
        layout.addWidget(self._make_sep())
        self._freq_lbl = QLabel(tr("hdr.cat.disconnected"))
        self._freq_lbl.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 9pt; font-family: Consolas;"
            f" padding: 0 8px;")
        layout.addWidget(self._freq_lbl)

        layout.addStretch(1)

        # Onweer-waarschuwing — gecentreerd via gelijke stretches aan beide kanten
        layout.addWidget(self._lightning_lbl)

        layout.addStretch(1)

        # Refresh-interval spinbox + countdown — rechts van de stretch
        layout.addWidget(_lbl_ref)
        layout.addWidget(self._spin_refresh)
        layout.addWidget(self._countdown_lbl)
        layout.addWidget(self._make_sep())

        # ── Rechter kant: FS | Exit | Help | sep | UTC | sep | Lokaal ──────────
        self._btn_min  = self._btn("─",                amber=True)
        self._btn_fs   = self._btn("⛶",              amber=True)
        self._btn_help = self._btn(tr("hdr.help"),   amber=True)

        self._lbl_local = QLabel("--:--:--")
        self._lbl_local.setStyleSheet(
            f"color: {TEXT_H1}; font-size: 10pt; font-weight: bold; padding: 0 8px;")

        self._lbl_utc = QLabel("UTC  --")
        self._lbl_utc.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 9pt; padding: 0 8px;")

        # Volgorde rechts → links: FS | MIN | ⚙ | Exit | ? | sep | UTC | sep | Local
        layout.addWidget(self._lbl_local)
        layout.addWidget(self._make_sep())
        layout.addWidget(self._lbl_utc)
        layout.addWidget(self._make_sep())
        layout.addWidget(self._btn_settings)   # ⚙ voor Help
        layout.addWidget(self._btn_help)        # Help
        layout.addWidget(self._btn_exit)
        layout.addWidget(self._btn_min)
        layout.addWidget(self._btn_fs)

        # Achtergrond via palette
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor(BG_PANEL))
        self.setPalette(pal)

        # Klok-timer
        self._clock = QTimer(self)
        self._clock.timeout.connect(self._tick)
        self._clock.start(1000)
        self._tick()

    # ── helpers ───────────────────────────────────────────────────────────────
    def _btn(self, text: str, amber: bool = False,
             bg: str = None, hover: str = None) -> QPushButton:
        b = QPushButton(text)
        _bg  = bg    or BG_SURFACE
        _hbg = hover or "#32373F"
        _clr = ACCENT if amber else TEXT_H1
        b.setStyleSheet(
            f"QPushButton {{ background: {_bg}; color: {_clr}; border: none;"
            f" padding: 2px 10px; }}"
            f"QPushButton:hover {{ background: {_hbg}; }}")
        return b

    def _make_sep(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet(f"color: {BORDER};")
        sep.setFixedWidth(1)
        sep.setContentsMargins(4, 6, 4, 6)
        return sep

    def set_next_refresh(self, epoch_secs: float):
        """Stel in wanneer de volgende verversing plaatsvindt (0 = Uit)."""
        self._next_refresh_at = epoch_secs
        if epoch_secs == 0.0:
            self._countdown_lbl.setText("Uit")
            self._countdown_lbl.setStyleSheet(
                f"color: {TEXT_DIM}; font-size: 9pt; padding: 0 4px;")

    def _tick(self):
        utc   = datetime.datetime.now(datetime.timezone.utc)
        local = utc.astimezone(self._local_tz)
        # Countdown bijwerken
        if self._next_refresh_at > 0:
            import time as _time
            remaining = max(0, self._next_refresh_at - _time.monotonic())
            m, s = divmod(int(remaining), 60)
            self._countdown_lbl.setText(f"{m}:{s:02d}")
            self._countdown_lbl.setStyleSheet(
                f"color: {ACCENT}; font-size: 9pt; padding: 0 4px;")
        elif self._next_refresh_at == 0.0:
            pass   # "Uit" is al gezet door set_next_refresh
        else:
            self._countdown_lbl.setText("")
        zone = local.strftime('%Z') or local.strftime('UTC%z')
        self._lbl_local.setText(f"{zone}  {local.strftime('%H:%M:%S')}")
        self._lbl_utc.setText(
            f"UTC  {utc.strftime('%Y-%m-%d')}  {utc.strftime('%H:%M:%S')}")

    def set_qth(self, lat: float, lon: float):
        """Update lokale tijdzone op basis van QTH-coördinaten."""
        self._local_tz = _tz_from_latlon(lat, lon)

    def set_offline(self, offline: bool):
        """Toon/verberg OFFLINE indicator."""
        self._offline_lbl.setVisible(offline)

    def set_lightning_warning(self, text: str | None):
        """Toon (tekst) of verberg (None) de onweer-nabijheid waarschuwing."""
        if text:
            self._lightning_lbl.setText(text)
            self._lightning_lbl.show()
            if not self._pulse_timer.isActive():
                self._pulse_timer.start()
        else:
            self._pulse_timer.stop()
            self._lightning_lbl.hide()

    def _pulse_lightning_lbl(self):
        """Wissel de label-kleur voor een licht pulseffect."""
        self._pulse_bright = not self._pulse_bright
        clr = "#EF5350" if self._pulse_bright else "#FF8A80"
        self._lightning_lbl.setStyleSheet(
            f"color: {clr}; font-weight: bold; font-size: 9pt; padding: 0 6px;")

    # ── publieke interface ─────────────────────────────────────────────────────
    def set_radio_freq(self, freq_hz):
        """
        Toon radio-frequentie in de header.
          None      → 'Radio niet verbonden'  (grijs)
          -1        → 'Radio offline'         (oranje — poort open, geen respons)
          0         → 'Verbonden  —'          (amber, freq onbekend)
          int > 0   → '14.225,000 kHz'        (amber vet)
        """
        if freq_hz is None:
            self._freq_lbl.setText(tr("hdr.cat.disconnected"))
            self._freq_lbl.setStyleSheet(
                f"color: {TEXT_DIM}; font-size: 9pt; font-family: Consolas;"
                f" padding: 0 8px;")
        elif freq_hz == -1:
            self._freq_lbl.setText(tr("hdr.cat.offline"))
            self._freq_lbl.setStyleSheet(
                f"color: #FFA726; font-size: 9pt; font-family: Consolas;"
                f" padding: 0 8px;")
        elif freq_hz == 0:
            self._freq_lbl.setText(tr("hdr.cat.connected"))
            self._freq_lbl.setStyleSheet(
                f"color: {ACCENT}; font-size: 9pt; font-family: Consolas;"
                f" padding: 0 8px;")
        else:
            khz = freq_hz / 1000.0
            txt = f"{khz:,.3f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            self._freq_lbl.setText(f"{txt} kHz")
            self._freq_lbl.setStyleSheet(
                f"color: {ACCENT}; font-size: 10pt; font-weight: bold;"
                f" font-family: Consolas; padding: 0 8px;")

    def retranslate(self):
        """Herlaad alle knop- en tooltip-teksten na taalwisseling."""
        self._btn_sat.setText(tr("hdr.satellite"))
        self._btn_spy.setText(tr("hdr.spystations"))
        self._btn_eibi.setText(tr("hdr.eibi"))
        self._btn_ft8.setText(tr("hdr.ft8"))
        self._btn_overlay.setText(tr("hdr.overlays"))
        self._btn_overlay.setToolTip(tr("hdr.overlays.tip"))
        self._btn_panels.setText(tr("hdr.panels"))
        self._btn_panels.setToolTip(tr("hdr.panels"))
        self._btn_exit.setText(tr("app.close"))
        self._btn_settings.setText(tr("hdr.settings"))
        self._btn_help.setText(tr("hdr.help"))
        self._spin_refresh.setSpecialValueText(tr("hdr.refresh.off"))
        self._spin_refresh.setToolTip(tr("hdr.refresh.tip"))
        self._countdown_lbl.setToolTip(tr("hdr.countdown.tip"))

    def set_cat_connected(self, connected: bool):
        """Pas kleur van frequentie-label aan op basis van CAT-verbindingsstatus."""
        if not connected and self._freq_lbl.text() == "Radio niet verbonden":
            self._freq_lbl.setStyleSheet(
                f"color: {TEXT_DIM}; font-size: 9pt; font-family: Consolas; padding: 0 8px;")

    @property
    def btn_exit(self):       return self._btn_exit
    @property
    def btn_settings(self):   return self._btn_settings
    @property
    def btn_sat(self):        return self._btn_sat
    @property
    def btn_spy(self):        return self._btn_spy
    @property
    def btn_eibi(self):       return self._btn_eibi
    @property
    def btn_ft8(self):        return self._btn_ft8
    @property
    def btn_tools(self):      return self._btn_tools
    @property
    def btn_overlay(self):    return self._btn_overlay
    @property
    def btn_panels(self):     return self._btn_panels
    @property
    def btn_help(self):       return self._btn_help
    @property
    def spin_refresh(self):   return self._spin_refresh
    @property
    def btn_minimize(self):   return self._btn_min
    @property
    def btn_fullscreen(self): return self._btn_fs


def _tz_from_latlon(lat: float, lon: float):
    """Bepaal tijdzone vanuit QTH-coördinaten.

    Probeert timezonefinder; valt terug op de OS-systeemtijdzone.
    """
    try:
        from timezonefinder import TimezoneFinder
        import zoneinfo
        tz_name = TimezoneFinder().timezone_at(lat=lat, lng=lon)
        if tz_name:
            return zoneinfo.ZoneInfo(tz_name)
    except ImportError:
        pass
    return datetime.datetime.now().astimezone().tzinfo
