"""
HAMIOS v5 — Sprint 5 panel-widgets

BandRelWidget    — HF band-betrouwbaarheid (SFI/K-gebaseerd)
BandCondWidget   — Dag/nacht bandcondities (HamQSL XML)
StormFcWidget    — 3-daagse stormprognose (NOAA)
BandSchedWidget  — Bandopenings-schema (24u rooster)
BandHistChart    — Band SFI historiek (QPainter)
SolarHistChart   — Solar historiek SFI + Kp (QPainter)
LightningPanel   — Bliksemstatus + fade-instelling
AlertsWidget     — NOAA ruimteweer-meldingen
DXSpotsTable     — Live DX spots tabel
(PropAdvWidget   — zie advice_panel.py)
"""

import datetime as _dt

from PySide6.QtCore import Qt, QTimer, QPointF, Signal
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QPainterPath
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QScrollArea, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QCheckBox, QComboBox,
    QPushButton, QStackedWidget
)


class NumericTableItem(QTableWidgetItem):
    """Table item that sorts numerically instead of alphabetically."""
    def __init__(self, text: str, numeric_value=0):
        super().__init__(text)
        self._numeric_value = numeric_value

    def __lt__(self, other):
        if isinstance(other, NumericTableItem):
            return self._numeric_value < other._numeric_value
        return super().__lt__(other)

from .theme import (
    ACCENT, BG_PANEL, BG_SURFACE, BG_ROOT,
    TEXT_H1, TEXT_BODY, TEXT_DIM, BORDER
)
from . import history as _hist_csv
from .i18n import tr, language_changed
from .propagation import (ENGINE as _PROP, is_day as _prop_is_day,
                          representative_time as _prop_rep_time)



# ── Propagatie-model ──────────────────────────────────────────────────────────

# ── Bandtabellen (v4-equivalent) ──────────────────────────────────────────────

_BANDS_HF = [
    ("160m",  1.810), ("80m",  3.500), ("60m",  5.352),
    ("40m",   7.000), ("30m", 10.100), ("20m", 14.000),
    ("17m",  18.068), ("15m", 21.000), ("12m", 24.890),
    ("10m",  28.000), ("6m",  50.000),
]

_BAND_COLORS_HF = {
    "160m": "#9575CD", "80m":  "#5C6BC0", "60m": "#42A5F5",
    "40m":  "#26C6DA", "30m":  "#26A69A", "20m": "#66BB6A",
    "17m":  "#D4E157", "15m":  "#FFCA28", "12m": "#FFA726",
    "10m":  "#EF5350", "6m":   "#EC407A",
}

_BAND_FT8_FREQ = {
    "160m": "1.840", "80m": "3.573", "60m": "5.357",
    "40m": "7.074",  "30m": "10.136","20m": "14.074",
    "17m": "18.100", "15m": "21.074","12m": "24.915",
    "10m": "28.074", "6m":  "50.313",
}

# Kiesbare frequenties per band — voor CAT-popup (mode → MHz)
_BAND_FREQ_OPTIONS: dict[str, list[tuple[str, float]]] = {
    "160m": [("CW",   1.810), ("SSB",  1.840), ("FT8",  1.840), ("WSPR", 1.8366)],
    "80m":  [("CW",   3.500), ("SSB",  3.600), ("FT8",  3.573), ("WSPR", 3.5686)],
    "60m":  [("USB",  5.352), ("FT8",  5.357)],
    "40m":  [("CW",   7.000), ("SSB",  7.100), ("FT8",  7.074), ("WSPR", 7.0386)],
    "30m":  [("CW",  10.100), ("FT8", 10.136), ("WSPR",10.1387)],
    "20m":  [("CW",  14.000), ("SSB", 14.225), ("FT8", 14.074), ("WSPR",14.0956)],
    "17m":  [("CW",  18.068), ("SSB", 18.130), ("FT8", 18.100), ("WSPR",18.1046)],
    "15m":  [("CW",  21.000), ("SSB", 21.200), ("FT8", 21.074), ("WSPR",21.0946)],
    "12m":  [("CW",  24.890), ("SSB", 24.940), ("FT8", 24.915), ("WSPR",24.9246)],
    "10m":  [("CW",  28.000), ("SSB", 28.400), ("FT8", 28.074), ("WSPR",28.1246)],
    "6m":   [("CW",  50.090), ("SSB", 50.150), ("FT8", 50.313), ("WSPR",50.293)],
}


# ── CAT-hulpfuncties voor alle panelen ────────────────────────────────────────

def _cat_check() -> tuple:
    """Geeft (cat_instance, foutmelding_of_None) terug."""
    from .cat_interface import get_instance
    cat = get_instance()
    if cat is None:
        return None, tr("cat.not_configured")
    if not cat.connected:
        return cat, tr("cat.not_connected")
    return cat, None


_CAT_DIGITAL = {"FT8", "FT4", "WSPR", "JS8", "JS8CALL", "PSK31", "DATA", "DIGI"}


def _cat_mode_for(mode: str | None, hz: int, cfg) -> str | None:
    """Werkmode (FT8, SSB, CW …) → radiomode (USB, LSB, CW, PKT-U …).
    Digitaal → de datamode uit de instellingen; SSB → LSB onder 10 MHz."""
    if not mode:
        return None
    m = mode.upper()
    if m in _CAT_DIGITAL:
        return (getattr(cfg, "cat_data_mode", "USB") or "USB").upper()
    if m == "SSB":
        return "LSB" if hz < 10_000_000 else "USB"
    return m


def _cat_send(hz: int, mode: str | None = None) -> tuple[bool, str]:
    """Stuur frequentie (en optioneel modus) naar radio via CAT."""
    cat, err = _cat_check()
    if err:
        return False, err
    ok, msg = cat.set_freq_hz(hz)
    if not ok:
        return False, msg
    radio_mode = _cat_mode_for(mode, hz, getattr(cat, "_cfg", None))
    if radio_mode:
        cat.set_mode(radio_mode)
    shown = f"{mode} ({radio_mode})" if mode and radio_mode and radio_mode != mode.upper() else (mode or "")
    return True, f"{hz/1000:.3f} kHz  {shown}".strip()


def _show_band_freq_menu(band: str, widget, callback) -> None:
    """Toon popup-menu met kiesbare frequenties voor een band.
    callback(hz: int, mode: str) wordt aangeroepen bij selectie.
    """
    from PySide6.QtWidgets import QMenu
    from PySide6.QtGui import QCursor
    options = _BAND_FREQ_OPTIONS.get(band, [])
    if not options:
        return
    if len(options) == 1:
        mode, mhz = options[0]
        callback(int(mhz * 1_000_000), mode)
        return
    menu = QMenu(widget)
    menu.setStyleSheet(
        "QMenu { background: #2A2D32; border: 1px solid #404850; }"
        "QMenu::item { padding: 4px 20px; color: #C8C8D0; font-size: 8pt; }"
        "QMenu::item:selected { background: #32373F; }")
    for mode, mhz in options:
        act = menu.addAction(f"{mode:8s}  {mhz:.4f} MHz")
        act.setData((int(mhz * 1_000_000), mode))
    chosen = menu.exec(QCursor.pos())
    if chosen and chosen.data():
        hz, mode = chosen.data()
        callback(hz, mode)


class _CatBar(QWidget):
    """Smal statusbalkje onderaan een paneel voor CAT-feedback.
    Verbergt zichzelf automatisch na 4 seconden.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        from PySide6.QtWidgets import QHBoxLayout, QLabel
        from PySide6.QtCore import QTimer
        lay = QHBoxLayout(self)
        lay.setContentsMargins(4, 1, 4, 1)
        self._lbl = QLabel("")
        self._lbl.setStyleSheet("font-size: 8pt;")
        lay.addWidget(self._lbl)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)
        self.hide()

    def show_msg(self, text: str, ok: bool):
        clr = "#4CAF50" if ok else "#EF5350"
        self._lbl.setText(text)
        self._lbl.setStyleSheet(f"color: {clr}; font-size: 8pt;")
        self.show()
        self._timer.start(4000)

_BAND_MODES_TBL = {
    "160m": "CW/FT8",  "80m": "CW/FT8",  "60m": "USB/FT8",
    "40m":  "SSB/FT8", "30m": "CW/FT8",  "20m": "SSB/FT8",
    "17m":  "SSB/FT8", "15m": "SSB/FT8", "12m": "SSB/FT8",
    "10m":  "SSB/FT8", "6m":  "Es/FT8",
}


# ── Propagatie: één centraal model (propagation.py) ──────────────────────────
# Alle panelen en het advies gebruiken dezelfde cijfers, gekalibreerd op de
# dichtstbijzijnde gemeten ionosonde. (Vervangt _calc_propagation_v4 en
# _reliability, die elkaar en de werkelijkheid tegenspraken.)

def _station_snr(cfg) -> int:
    """Station-marge in dB t.o.v. SSB/100 W/isotroop (mode + vermogen + antenne)."""
    if not cfg:
        return 0
    return (_MODE_DB.get(cfg.mode, 0) + _POWER_DB.get(cfg.power, 0) +
            _ANT_DB.get(getattr(cfg, "antenna", ""), 0))


def _qth(cfg) -> tuple[float, float]:
    return (cfg.qth_lat, cfg.qth_lon) if cfg else (52.0, 5.0)


def _prop_now(cfg, t=None, day: bool | None = None):
    """Propagatie op de QTH. day=True/False → representatief dag-/nachtmoment."""
    lat, lon = _qth(cfg)
    if day is not None:
        t = _prop_rep_time(lat, lon, day)
    return _PROP.conditions(lat, lon, t, _station_snr(cfg))


def _band_pct_list(c) -> list:
    """Conditions → [(band, MHz, pct)] voor de grafieken."""
    return [(n, f, c.band_pct.get(n, 0)) for n, f in _BANDS_HF]


def _prop_source_tip(c) -> str:
    """Tooltip: waar komen MUF/LUF vandaan (gemeten ionosonde of model)."""
    if c.measured is not None and c.cal_weight > 0.05:
        return tr("prop.src.measured", name=c.measured.name,
                  age=int(c.measured.age_s() // 60), w=int(round(c.cal_weight * 100)))
    return tr("prop.src.model")



def _rel_color(rel: float) -> QColor:
    if rel >= 0.7: return QColor("#4CAF50")
    if rel >= 0.4: return QColor("#FFC107")
    if rel >= 0.15: return QColor("#FF9800")
    return QColor("#555A60")


# ── BandRelWidget ─────────────────────────────────────────────────────────────

class _BandChart(QWidget):
    """Bandbalken voor 'Banden nu': kans nu (balk + %), beoordeling overdag en
    's nachts, trend komend uur, frequentie/mode/FT8. Op een smal paneel vallen
    de minst belangrijke kolommen weg (eerst FT8, dan MHz, dan mode)."""

    BAR_H   = 22
    BAR_PAD = 4
    HDR_H   = 16
    LBL_W   = 46
    MIN_BAR = 90
    # (sleutel, breedte) — volgorde op het scherm
    _COLS = [("pct", 36), ("day", 48), ("night", 48), ("trend", 16),
             ("freq", 52), ("mode", 72), ("ft8", 50)]
    _DROP = ("ft8", "freq", "mode", "trend")        # wegvallen bij krapte

    def __init__(self, parent=None):
        super().__init__(parent)
        self._band_pct: list = []
        self._extra: dict = {}           # band → (dag %, nacht %, trend −1/0/1)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)
        self._band_click_cb = None   # callback(band_name)
        n = len(_BANDS_HF)
        self.setMinimumHeight(self.HDR_H + n * (self.BAR_H + self.BAR_PAD) + self.BAR_PAD)

    def set_band_click_callback(self, cb):
        self._band_click_cb = cb

    def _row_at(self, y: float) -> int:
        return int((y - self.HDR_H) / (self.BAR_H + self.BAR_PAD))

    def mousePressEvent(self, event):
        if not self._band_pct or not self._band_click_cb:
            return
        row = self._row_at(event.position().y())
        if 0 <= row < len(self._band_pct):
            self._band_click_cb(self._band_pct[row][0])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        from PySide6.QtWidgets import QToolTip
        row = self._row_at(event.position().y())
        if not (0 <= row < len(self._band_pct)):
            QToolTip.hideText()
            return
        name, freq, pct = self._band_pct[row]
        d, n, t = self._extra.get(name, (None, None, 0))
        info = _BAND_INFO.get(name, ("", ""))
        lines = [f"<b>{name}</b> — {info[0]}", info[1], "",
                 tr("bandnow.tip.now", pct=pct)]
        if d is not None:
            lines.append(tr("bandnow.tip.daynight", day=_pct_to_cond(d)[0], dp=d,
                            night=_pct_to_cond(n)[0], np=n))
        lines.append(tr({1: "bandnow.tip.up", -1: "bandnow.tip.down"}.get(t, "bandnow.tip.flat")))
        lines += ["", f"<i>{tr('bandnow.tip.click')}</i>"]
        QToolTip.showText(event.globalPosition().toPoint(), "<br>".join(lines), self)

    def set_data(self, band_pct: list, extra: dict | None = None):
        self._band_pct = band_pct
        if extra is not None:
            self._extra = extra
        self.update()

    def _layout(self, W: int) -> tuple[list, int]:
        """Zichtbare kolommen en balkbreedte voor paneelbreedte W."""
        cols = list(self._COLS)
        for key in self._DROP:
            if W - self.LBL_W - 12 - sum(w for _, w in cols) >= self.MIN_BAR:
                break
            cols = [c for c in cols if c[0] != key]
        bar_max = max(40, W - self.LBL_W - 12 - sum(w for _, w in cols))
        return cols, bar_max

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)
        W, H = self.width(), self.height()
        p.fillRect(0, 0, W, H, QColor(BG_PANEL))

        if not self._band_pct:
            return

        cols, bar_max = self._layout(W)
        bar_x = self.LBL_W + 4
        xs, x = {}, bar_x + bar_max
        for key, w in cols:
            xs[key] = (x, w)
            x += w

        f7b = QFont("Segoe UI", 7); f7b.setBold(True)
        f7  = QFont("Segoe UI", 7)
        f8b = QFont("Segoe UI", 8); f8b.setBold(True)

        # Kolomhoofden
        heads = {"pct": "%", "day": tr("band.day"), "night": tr("band.night"),
                 "trend": "", "freq": "MHz", "mode": tr("bandnow.col.mode"), "ft8": "FT8"}
        p.setFont(f7b)
        p.setPen(QColor(ACCENT))
        for key, (cx, cw) in xs.items():
            p.drawText(cx, 0, cw, self.HDR_H, Qt.AlignCenter, heads[key])

        for i, (name, freq, pct) in enumerate(self._band_pct):
            y   = self.HDR_H + self.BAR_PAD + i * (self.BAR_H + self.BAR_PAD)
            clr = QColor(_BAND_COLORS_HF.get(name, TEXT_DIM))

            # Bandnaam
            p.setFont(f8b)
            p.setPen(clr)
            p.drawText(0, y, self.LBL_W - 2, self.BAR_H,
                       Qt.AlignRight | Qt.AlignVCenter, name)

            # Balk achtergrond
            p.setPen(QPen(QColor(BORDER), 1))
            p.setBrush(QBrush(QColor(BG_SURFACE)))
            p.drawRect(bar_x, y + 1, bar_max, self.BAR_H - 2)

            if pct == 0:
                p.setFont(f7)
                p.setPen(QColor(TEXT_DIM))
                p.drawText(bar_x, y + 1, bar_max, self.BAR_H - 2,
                           Qt.AlignCenter, tr("band.closed"))
            else:
                fill_w = max(2, int((bar_max - 2) * pct / 100))
                r, g, b = clr.red(), clr.green(), clr.blue()
                slices = min(self.BAR_H - 4, 6)
                for sl in range(slices):
                    fac = 1.0 - (sl / slices) * 0.50
                    sc  = QColor(min(255, int(r*fac)), min(255, int(g*fac)), min(255, int(b*fac)))
                    sy1 = y + 2 + sl * (self.BAR_H - 4) // slices
                    sy2 = y + 2 + (sl + 1) * (self.BAR_H - 4) // slices
                    p.setPen(Qt.NoPen)
                    p.setBrush(QBrush(sc))
                    p.drawRect(bar_x + 1, sy1, fill_w, sy2 - sy1)
                hl = QColor(min(255, int(r*1.5)), min(255, int(g*1.5)), min(255, int(b*1.5)))
                p.setPen(QPen(hl, 1))
                p.drawLine(bar_x + 2, y + 2, bar_x + fill_w, y + 2)

            d, n, t = self._extra.get(name, (None, None, 0))
            for key, (cx, cw) in xs.items():
                if key == "pct":
                    p.setFont(f7b); p.setPen(QColor(TEXT_H1 if pct else TEXT_DIM))
                    p.drawText(cx, y, cw, self.BAR_H, Qt.AlignCenter, f"{pct}%")
                elif key in ("day", "night"):
                    v = d if key == "day" else n
                    if v is not None:
                        txt, c = _pct_to_cond(v)
                        p.setFont(f7b); p.setPen(QColor(c))
                        p.drawText(cx, y, cw, self.BAR_H, Qt.AlignCenter, txt)
                elif key == "trend" and t:
                    p.setFont(f7b)
                    p.setPen(QColor("#4CAF50" if t > 0 else "#EF5350"))
                    p.drawText(cx, y, cw, self.BAR_H, Qt.AlignCenter, "▲" if t > 0 else "▼")
                elif key == "freq":
                    p.setFont(f7); p.setPen(QColor(TEXT_DIM))
                    p.drawText(cx, y, cw, self.BAR_H, Qt.AlignCenter, f"{freq:.3f}")
                elif key == "mode":
                    p.setFont(f7); p.setPen(QColor(TEXT_DIM))
                    p.drawText(cx, y, cw, self.BAR_H, Qt.AlignCenter, _BAND_MODES_TBL.get(name, ""))
                elif key == "ft8":
                    p.setFont(f7); p.setPen(QColor(TEXT_DIM))
                    p.drawText(cx, y, cw, self.BAR_H, Qt.AlignCenter, _BAND_FT8_FREQ.get(name, "—"))


class BandRelWidget(QWidget):
    """HF Band Betrouwbaarheid — v4 stijl met controls, MUF/LUF en gradient-balken."""

    settings_changed = Signal()   # emitteert bij mode/power/dag-wijziging

    def __init__(self, cfg=None, parent=None):
        super().__init__(parent)
        self._cfg = cfg
        self._sfi = 100.0
        self._ssn = 50.0
        self._k   = 2.0
        self._day = True

        v = QVBoxLayout(self)
        v.setContentsMargins(6, 4, 6, 4)
        v.setSpacing(3)

        # ── Info-rij (MUF / LUF / SNR) ────────────────────────────────────
        info = QHBoxLayout()
        info.setSpacing(16)
        f8b = QFont("Segoe UI", 8); f8b.setBold(True)
        self._muf_lbl = QLabel("MUF: —"); self._muf_lbl.setFont(f8b)
        self._muf_lbl.setStyleSheet(f"color: {TEXT_H1};")
        self._luf_lbl = QLabel("LUF: —"); self._luf_lbl.setFont(f8b)
        self._luf_lbl.setStyleSheet(f"color: {TEXT_H1};")
        self._snr_lbl = QLabel("0 dB");   self._snr_lbl.setFont(f8b)
        self._snr_lbl.setStyleSheet(f"color: {ACCENT};")
        info.addWidget(self._muf_lbl)
        info.addWidget(self._luf_lbl)
        info.addWidget(self._snr_lbl)
        info.addStretch()
        v.addLayout(info)

        # ── Balk-grafiek ─────────────────────────────────────────────────
        self._chart = _BandChart()
        self._chart.set_band_click_callback(self._on_band_click)
        v.addWidget(self._chart, 1)

        self._cat_bar = _CatBar()
        v.addWidget(self._cat_bar)

        if cfg:
            self._recalc()

    def _on_band_click(self, band: str):
        _show_band_freq_menu(band, self, self._send_band)

    def _send_band(self, hz: int, mode: str):
        ok, msg = _cat_send(hz, mode)
        self._cat_bar.show_msg(
            f"📟  {hz/1e6:.4f} MHz  {mode}" if ok else f"📟  {msg}", ok)

    def set_cfg(self, cfg):
        self._cfg = cfg
        self._recalc()

    @staticmethod
    def _is_day_at_qth(qth_lat: float, qth_lon: float) -> bool:
        """Dag/nacht via werkelijke zonsstand op de QTH (centraal model)."""
        return _prop_is_day(qth_lat, qth_lon)


    def set_data(self, solar: dict):
        try:
            self._sfi = float(str(solar.get("sfi", 100)).replace("—", "100") or "100")
            self._ssn = float(str(solar.get("ssn",  50)).replace("—",  "50") or "50")
            self._k   = float(str(solar.get("k_index", 2)).replace("—", "2")  or "2")
        except (ValueError, TypeError):
            pass
        self._recalc()

    def _recalc(self):
        day_auto = getattr(self._cfg, "band_day_auto", True) if self._cfg else True
        # Automatisch: nu. Handmatig dag/nacht: representatief moment daarvan.
        c = _prop_now(self._cfg) if day_auto else _prop_now(self._cfg, day=self._day)
        if day_auto:
            self._day = c.is_day
        snr = _station_snr(self._cfg)
        # Samengevoegd uit het oude paneel 'Bandcondities': beoordeling overdag
        # en 's nachts, plus de trend voor het komende uur
        pd = _prop_now(self._cfg, day=True).band_pct
        pn = _prop_now(self._cfg, day=False).band_pct
        lat, lon = _qth(self._cfg)
        nxt = _PROP.conditions(lat, lon, c.time + _dt.timedelta(hours=1), snr).band_pct
        extra = {}
        for b, _f in _BANDS_HF:
            dlt = nxt.get(b, 0) - c.band_pct.get(b, 0)
            extra[b] = (pd.get(b, 0), pn.get(b, 0), 1 if dlt >= 10 else (-1 if dlt <= -10 else 0))
        self._chart.set_data(_band_pct_list(c), extra)
        self._muf_lbl.setText(f"MUF: {c.muf} MHz")
        self._luf_lbl.setText(f"LUF: {c.luf} MHz")
        tip = _prop_source_tip(c)
        self._muf_lbl.setToolTip(tip)
        self._luf_lbl.setToolTip(tip)
        dn = tr("band.day") if self._day else tr("band.night")
        self._snr_lbl.setText(f"{snr:+d} dB  ·  {dn}")


# ── BandCondWidget ────────────────────────────────────────────────────────────

def _band_info():
    return {
        "160m": ("1.8–2.0 MHz", tr("bandt.160m")),
        "80m":  ("3.5–4.0 MHz", tr("bandt.80m")),
        "60m":  ("5 MHz",       tr("bandt.60m")),
        "40m":  ("7 MHz",       tr("bandt.40m")),
        "30m":  ("10 MHz",      tr("bandt.30m")),
        "20m":  ("14 MHz",      tr("bandt.20m")),
        "17m":  ("18 MHz",      tr("bandt.17m")),
        "15m":  ("21 MHz",      tr("bandt.15m")),
        "12m":  ("24 MHz",      tr("bandt.12m")),
        "10m":  ("28–30 MHz",   tr("bandt.10m")),
        "6m":   ("50 MHz",      tr("bandt.6m")),
}


def _pct_to_cond(pct: int) -> tuple[str, str]:
    if pct >= 60: return tr("band.good"),    "#4CAF50"
    if pct >= 30: return tr("band.fair"),    "#FFC107"
    if pct >= 1:  return tr("band.poor"),    "#F44336"
    return               tr("band.closed"),  TEXT_DIM

_BAND_INFO = _band_info()


# ── StormFcWidget ─────────────────────────────────────────────────────────────

class _OutlookStrip(QWidget):
    """27-dagen-vooruitzicht (NOAA): per dag max Kp (kleur) + zonneflux (balkje).
    Vandaag omkaderd; tooltip per dag. Voor het plannen van contests/DX."""

    def __init__(self):
        super().__init__()
        self._rows: list = []            # [(date, flux, A, Kp), …]
        self.setMinimumHeight(46)
        self.setMouseTracking(True)

    def set_rows(self, rows: list):
        self._rows = list(rows)
        self.setToolTip(self._summary())
        self.update()

    def _summary(self) -> str:
        if not self._rows:
            return ""
        calm = [r for r in self._rows if r[3] <= 2]
        best = sorted(calm, key=lambda r: -r[1])[:3]
        days = ", ".join(f"{r[0].day}-{r[0].month}" for r in sorted(best))
        return tr("outlook.tip", days=days or "—")

    def _geom(self):
        n = max(1, len(self._rows))
        cw = max(3, (self.width() - 4) // n)
        return n, cw

    def paintEvent(self, event):
        p = QPainter(self)
        W, H = self.width(), self.height()
        p.fillRect(0, 0, W, H, QColor(BG_PANEL))
        if not self._rows:
            return
        n, cw = self._geom()
        lab_h, kp_h = 11, 12
        bar_top, bar_bot = lab_h + kp_h + 3, H - 1
        fmin = min(r[1] for r in self._rows) - 5
        fmax = max(r[1] for r in self._rows) + 5
        today = _dt.date.today()
        p.setFont(QFont("Segoe UI", 6))
        for i, (d, flux, a, kp) in enumerate(self._rows):
            x = 2 + i * cw
            c = ("#EF5350" if kp >= 6 else "#FFA726" if kp == 5
                 else "#FFF176" if kp == 4 else "#2E7D32")
            p.fillRect(x, lab_h, cw - 1, kp_h, QColor(c))
            h = int((bar_bot - bar_top) * (flux - fmin) / max(1, fmax - fmin))
            p.fillRect(x, bar_bot - h, cw - 1, h, QColor(ACCENT).darker(130))
            if d.weekday() == 0 or i == 0:
                p.setPen(QColor(TEXT_DIM))
                p.drawText(x, 0, 30, lab_h, Qt.AlignLeft | Qt.AlignVCenter, f"{d.day}-{d.month}")
            if d == today:
                p.setPen(QPen(QColor(ACCENT), 1))
                p.setBrush(Qt.NoBrush)
                p.drawRect(x - 1, lab_h - 1, cw, H - lab_h)

    def mouseMoveEvent(self, event):
        from PySide6.QtWidgets import QToolTip
        if not self._rows:
            return
        n, cw = self._geom()
        i = int((event.position().x() - 2) // cw)
        if 0 <= i < n:
            d, flux, a, kp = self._rows[i]
            QToolTip.showText(event.globalPosition().toPoint(),
                              tr("outlook.day", date=f"{d.day}-{d.month}-{d.year}",
                                 flux=flux, a=a, kp=kp) + "<br><br>" + self._summary(), self)


class StormFcWidget(QWidget):
    """3-daagse NOAA stormprognose + 27-dagen-vooruitzicht."""

    # (tr-key, data-key, Kp-bereik, tooltip)
    _LEVELS = [
        ("storm.active",    "active",   "Kp 3–4",
         "storm.tip.active"),
        ("storm.minor",  "minor",    "Kp 5",
         "storm.tip.minor"),
        ("storm.moderate",  "moderate", "Kp 6",
         "storm.tip.moderate"),
        ("storm.severe",  "severe",   "Kp 7",
         "storm.tip.severe"),
        ("storm.extreme", "extreme",  "Kp ≥8",
         "storm.tip.extreme"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        language_changed.connect(self.retranslate)

    def retranslate(self, _=None):
        """Update alle labels na taalwisseling."""
        self._sub_lbl.setText(tr("storm.subtitle"))
        if hasattr(self, "_outlook_lbl"):
            self._outlook_lbl.setText(tr("outlook.title"))
            self._outlook.set_rows(self._outlook._rows)
        for i, key in enumerate(["storm.col.act","storm.col.d1","storm.col.d2","storm.col.d3"]):
            self._hdr_lbls[i].setText(tr(key))
        for i, (trkey, _key, kp, _tip) in enumerate(self._LEVELS):
            self._row_lbls[i].setText(
                f"{tr(trkey)}  <small style='color:#555;'>{kp}</small>")
        self._legend_lbl.setText(
            f'<span style="color:{TEXT_DIM};">{tr("storm.legend.low")}</span>'
            f'&nbsp;&nbsp;'
            f'<span style="color:#FFF176;">{tr("storm.legend.fair")}</span>'
            f'&nbsp;&nbsp;'
            f'<span style="color:#FFA726;">{tr("storm.legend.high")}</span>'
            f'&nbsp;&nbsp;'
            f'<span style="color:#EF5350;">{tr("storm.legend.crit")}</span>')

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(6, 4, 6, 4)
        outer.setSpacing(2)

        self._sub_lbl = QLabel(tr("storm.subtitle"))
        self._sub_lbl.setFont(QFont("Segoe UI", 6))
        self._sub_lbl.setStyleSheet(f"color: {TEXT_DIM}; background: transparent;")
        self._sub_lbl.setAlignment(Qt.AlignCenter)
        outer.addWidget(self._sub_lbl)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(3)
        outer.addLayout(grid)

        f7  = QFont("Segoe UI", 7)
        f7b = QFont("Segoe UI", 7); f7b.setBold(True)

        self._hdr_lbls = []
        for col, key in enumerate(["storm.col.act","storm.col.d1","storm.col.d2","storm.col.d3"]):
            lbl = QLabel(tr(key))
            lbl.setFont(f7b)
            lbl.setStyleSheet(f"color: {TEXT_DIM};")
            lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, 0, col)
            self._hdr_lbls.append(lbl)

        self._cells: dict[tuple, QLabel] = {}
        self._row_lbls = []
        for row, (trkey, key, kp, tip) in enumerate(self._LEVELS, start=1):
            tip = tr(tip)
            lbl = QLabel(f"{tr(trkey)}  <small style='color:#555;'>{kp}</small>")
            lbl.setTextFormat(Qt.RichText)
            lbl.setFont(f7)
            lbl.setStyleSheet(f"color: {TEXT_DIM};")
            lbl.setToolTip(tip)
            grid.addWidget(lbl, row, 0)
            self._row_lbls.append(lbl)
            for day in range(3):
                cell = QLabel("—")
                cell.setFont(f7b)
                cell.setAlignment(Qt.AlignCenter)
                cell.setToolTip(tip)
                grid.addWidget(cell, row, day + 1)
                self._cells[(key, day)] = cell

        legend_row = len(self._LEVELS) + 1
        self._legend_lbl = QLabel()
        self._legend_lbl.setFont(QFont("Segoe UI", 6))
        self._legend_lbl.setAlignment(Qt.AlignCenter)
        self._legend_lbl.setStyleSheet("background: transparent;")
        grid.addWidget(self._legend_lbl, legend_row, 0, 1, 4)

        # 27-dagen-vooruitzicht
        self._outlook_lbl = QLabel(tr("outlook.title"))
        self._outlook_lbl.setFont(QFont("Segoe UI", 7, QFont.Bold))
        self._outlook_lbl.setStyleSheet(f"color: {ACCENT}; background: transparent;")
        outer.addWidget(self._outlook_lbl)
        self._outlook = _OutlookStrip()
        outer.addWidget(self._outlook)
        # Vul initieel via retranslate
        self.retranslate()

    def set_outlook(self, rows: list):
        self._outlook.set_rows(rows)

    def set_data(self, storm: dict):
        for _trkey, key, _kp, _tip in self._LEVELS:
            vals = storm.get(key, [0, 0, 0])
            for day, val in enumerate(vals[:3]):
                cell = self._cells.get((key, day))
                if cell:
                    cell.setText(f"{val}%")
                    if val >= 50:   c = "#EF5350"
                    elif val >= 25: c = "#FFA726"
                    elif val >= 10: c = "#FFF176"
                    else:           c = TEXT_DIM
                    cell.setStyleSheet(
                        f"color: {c}; font-weight: bold; font-size: 7pt;")


# ── BandSchedWidget ───────────────────────────────────────────────────────────

class BandSchedWidget(QWidget):
    """24u band-openings heatmap — v4 stijl met propagatieberekening per uur."""

    def __init__(self, cfg=None, parent=None):
        super().__init__(parent)
        self._cfg  = cfg
        self._solar: dict = {}
        self._grid: list  = []   # [band_idx][hour] = pct
        self._now_h = 0
        self._layout_info: dict = {}
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setMinimumHeight(130)
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)
        # CAT statusbalk is een aparte widget boven dit widget (wordt door mainwindow/parent beheerd)
        # Gebruik een overlay-label rechtsonder
        self._cat_lbl = QLabel("", self)
        self._cat_lbl.setStyleSheet(
            "background: rgba(26,28,34,200); color: #4CAF50; font-size: 8pt; padding: 2px 6px;")
        self._cat_lbl.hide()
        self._cat_timer = QTimer(self)
        self._cat_timer.setSingleShot(True)
        self._cat_timer.timeout.connect(self._cat_lbl.hide)

    def _show_cat_msg(self, text: str, ok: bool):
        clr = "#4CAF50" if ok else "#EF5350"
        self._cat_lbl.setStyleSheet(
            f"background: rgba(26,28,34,200); color: {clr}; font-size: 8pt; padding: 2px 6px;")
        self._cat_lbl.setText(text)
        self._cat_lbl.adjustSize()
        self._cat_lbl.move(self.width() - self._cat_lbl.width() - 4,
                           self.height() - self._cat_lbl.height() - 2)
        self._cat_lbl.show(); self._cat_lbl.raise_()
        self._cat_timer.start(4000)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._cat_lbl.isVisible():
            self._cat_lbl.move(self.width() - self._cat_lbl.width() - 4,
                               self.height() - self._cat_lbl.height() - 2)

    def set_cfg(self, cfg):
        self._cfg = cfg
        self._recalc()
        self.update()

    def set_data(self, solar: dict):
        self._solar = solar
        self._recalc()
        self.update()

    def _recalc(self):
        """24 uur vooruit vanaf het huidige lokale uur (doorlopend), één
        modelberekening per uur: kans per band + MUF/LUF."""
        snr = _station_snr(self._cfg)
        qth_lat, qth_lon = _qth(self._cfg)
        start = _dt.datetime.now().replace(minute=0, second=0, microsecond=0)
        self._hours = [start + _dt.timedelta(hours=h) for h in range(24)]
        conds = [_PROP.conditions(qth_lat, qth_lon, t.astimezone(_dt.timezone.utc), snr)
                 for t in self._hours]
        self._grid = [[c.band_pct.get(bname, 0) for c in conds] for bname, _ in _BANDS_HF]
        self._muf = [c.muf for c in conds]
        self._luf = [c.luf for c in conds]
        self._day = [c.is_day for c in conds]
        self._now_h = 0

    # ── tekenen ──────────────────────────────────────────────────────────────
    _MUF_BANDS = (("40m", 7.0), ("20m", 14.0), ("15m", 21.0), ("10m", 28.0))

    def paintEvent(self, event):
        p = QPainter(self)
        W, H = self.width(), self.height()
        p.fillRect(0, 0, W, H, QColor(BG_PANEL))

        if not self._grid:
            p.setPen(QColor(TEXT_DIM))
            p.setFont(QFont("Segoe UI", 9))
            p.drawText(0, 0, W, H, Qt.AlignCenter, tr("app.loading"))
            return

        N_H = 24
        N_B = len(_BANDS_HF)
        PL, PR, PT, GAP, PB = 40, 4, 16, 8, 4
        muf_h = max(50, int((H - PT - GAP - PB) * 0.34))
        heat_h = H - PT - GAP - PB - muf_h
        cell_w = max(1, (W - PL - PR) // N_H)
        cell_h = max(1, heat_h // N_B)
        heat_bottom = PT + N_B * cell_h
        muf_top = heat_bottom + GAP
        muf_bottom = H - PB

        f7 = QFont("Segoe UI", 7)
        p.setFont(f7)

        # Uur-labels (lokale tijd; elke 3 uur) + nacht-arcering boven
        for h in range(N_H):
            cx = PL + h * cell_w
            if not self._day[h]:
                p.fillRect(cx, PT - 3, cell_w, 2, QColor(70, 90, 140))
            if h % 3 == 0:
                p.setPen(QColor(TEXT_DIM))
                p.drawText(cx + cell_w // 2 - 10, 0, 20, PT - 4, Qt.AlignCenter,
                           f"{self._hours[h].hour:02d}")

        # Heatmap: banden × uren
        for bi, (bname, _) in enumerate(_BANDS_HF):
            cy = PT + bi * cell_h
            p.setPen(QColor(_BAND_COLORS_HF.get(bname, TEXT_DIM)))
            p.drawText(0, cy, PL - 3, cell_h, Qt.AlignRight | Qt.AlignVCenter, bname)
            for h in range(N_H):
                pct = self._grid[bi][h]
                if   pct >= 60: fill = QColor("#2E7D32")
                elif pct >= 30: fill = QColor("#F9A825")
                elif pct >= 1:  fill = QColor("#B71C1C")
                else:           fill = QColor("#1A1C1F")
                p.fillRect(PL + h * cell_w, cy, cell_w - 1, cell_h - 1, fill)

        # MUF/LUF-curve op dezelfde uuras
        ymax = max(30.0, max(self._muf) + 2)
        ymax = float(int((ymax + 4.99) // 5) * 5)

        def yv(mhz):
            return muf_bottom - (muf_bottom - muf_top) * min(1.0, mhz / ymax)

        p.fillRect(PL, muf_top, N_H * cell_w, muf_bottom - muf_top, QColor(BG_SURFACE))
        p.setPen(QPen(QColor(BORDER), 1, Qt.DotLine))
        for bname, mhz in self._MUF_BANDS:
            if mhz < ymax:
                y = int(yv(mhz))
                p.setPen(QPen(QColor(_BAND_COLORS_HF.get(bname, TEXT_DIM)).darker(160), 1, Qt.DotLine))
                p.drawLine(PL, y, PL + N_H * cell_w, y)
                p.setPen(QColor(_BAND_COLORS_HF.get(bname, TEXT_DIM)))
                p.drawText(0, y - 6, PL - 3, 12, Qt.AlignRight | Qt.AlignVCenter, bname)
        p.setPen(QColor(TEXT_DIM))
        p.drawText(0, muf_top, PL - 3, 12, Qt.AlignRight | Qt.AlignTop, f"{ymax:.0f}")
        muf_pts = [QPointF(PL + h * cell_w + cell_w / 2, yv(self._muf[h])) for h in range(N_H)]
        luf_pts = [QPointF(PL + h * cell_w + cell_w / 2, yv(self._luf[h])) for h in range(N_H)]
        band = QPainterPath(muf_pts[0])
        for pt in muf_pts[1:]:
            band.lineTo(pt)
        for pt in reversed(luf_pts):
            band.lineTo(pt)
        band.closeSubpath()
        p.setRenderHint(QPainter.Antialiasing, True)
        p.fillPath(band, QColor(200, 168, 75, 40))
        p.setPen(QPen(QColor(ACCENT), 2))
        p.drawPolyline(muf_pts)
        p.setPen(QPen(QColor(TEXT_DIM), 1.2, Qt.DashLine))
        p.drawPolyline(luf_pts)
        p.setRenderHint(QPainter.Antialiasing, False)
        p.setPen(QColor(ACCENT))
        p.drawText(PL + 3, muf_top + 1, 60, 12, Qt.AlignLeft | Qt.AlignTop, "MUF")
        p.setPen(QColor(TEXT_DIM))
        p.drawText(PL + 36, muf_top + 1, 60, 12, Qt.AlignLeft | Qt.AlignTop, "LUF")

        # Huidig uur (eerste kolom) — amber omkadering over heatmap én curve
        p.setPen(QPen(QColor(ACCENT), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRect(PL, PT, cell_w - 1, muf_bottom - PT - 1)

        self._layout_info = dict(pl=PL, pt=PT, cw=cell_w, ch=cell_h, nb=N_B, nh=N_H,
                                 heat_bottom=heat_bottom, muf_top=muf_top,
                                 muf_bottom=muf_bottom)

    # ── interactie ───────────────────────────────────────────────────────────
    def _cell(self, pos):
        lay = self._layout_info
        if not lay or not self._grid:
            return None, None, None
        col = (pos.x() - lay["pl"]) // lay["cw"]
        if not (0 <= col < lay["nh"]):
            return None, None, None
        if lay["pt"] <= pos.y() < lay["heat_bottom"]:
            return "heat", col, (pos.y() - lay["pt"]) // lay["ch"]
        if lay["muf_top"] <= pos.y() <= lay["muf_bottom"]:
            return "muf", col, None
        return None, None, None

    def mousePressEvent(self, event):
        area, col, row = self._cell(event.position().toPoint())
        if area == "heat" and 0 <= row < len(_BANDS_HF):
            bname = _BANDS_HF[row][0]
            _show_band_freq_menu(bname, self,
                lambda hz, mode: self._send_to_cat(hz, mode))
        super().mousePressEvent(event)

    def _send_to_cat(self, hz: int, mode: str):
        ok, msg = _cat_send(hz, mode)
        self._show_cat_msg(
            f"📟  {hz/1e6:.4f} MHz  {mode}" if ok else f"📟  {msg}", ok)

    def mouseMoveEvent(self, event):
        from PySide6.QtWidgets import QToolTip
        area, col, row = self._cell(event.position().toPoint())
        if area is None:
            QToolTip.hideText()
            return
        t0 = self._hours[col]
        span = f"{t0:%H:%M}–{(t0 + _dt.timedelta(hours=1)):%H:%M}"
        dn = tr("band.day") if self._day[col] else tr("band.night")
        if area == "heat" and 0 <= row < len(_BANDS_HF):
            bname, bfreq = _BANDS_HF[row]
            pct = self._grid[row][col]
            kwal = _pct_to_cond(pct)[0]
            tip = tr("sched.tip.heat", band=bname, span=span, dn=dn, pct=pct, cond=kwal,
                     mhz=f"{bfreq:.3f}", mode=_BAND_MODES_TBL.get(bname, "—"),
                     ft8=_BAND_FT8_FREQ.get(bname, "—"))
        else:
            tip = tr("sched.tip.muf", span=span, dn=dn, muf=self._muf[col], luf=self._luf[col])
        QToolTip.showText(event.globalPosition().toPoint(), tip, self)


# ── Historiek-grafieken ───────────────────────────────────────────────────────

def _rows_to_ha(rows: list, hours: float) -> list:
    """Converteer history-rijen naar [(hours_ago, ts, bp, sol), ...] gesorteerd."""
    now = _dt.datetime.now(_dt.timezone.utc)
    out = []
    for ts, bp, sol in rows:
        ha = (now - ts).total_seconds() / 3600
        if 0 <= ha <= hours:
            out.append((ha, ts, bp, sol))
    out.sort(key=lambda x: x[0], reverse=True)  # oudste eerst (groot ha → klein ha)
    return out


def _gap_limit(data: list) -> float:
    """Grootste afstand (uren) tussen twee metingen die nog verbonden wordt.
    Groter = een gat (HAMIOS stond uit): daar geen lijn tekenen, anders lijkt
    een rechte verbindingslijn op echte data. Grens: 4× het normale
    meetinterval (mediaan), minstens 45 minuten."""
    steps = sorted(abs(a[0] - b[0]) for a, b in zip(data, data[1:]) if a[0] != b[0])
    median = steps[len(steps) // 2] if steps else 0.0
    return max(0.75, 4 * median)


class SolarHistChart(QWidget):
    """SFI + Kp historiek — leest uit HAMIOS_history.csv."""

    _SEL_H  = 14
    _RANGES = [("24h", 24), ("7d", 168), ("30d", 720), ("1j", 8760)]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hours = 24.0
        self._range_rects: list = []
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setMinimumHeight(80)
        self.setCursor(Qt.PointingHandCursor)
        t = QTimer(self)
        t.timeout.connect(self.update)
        t.start(60_000)

    def set_hours(self, h: float):
        self._hours = h
        self.update()

    def set_data(self, solar: dict):
        self.update()

    def mousePressEvent(self, event):
        px, py = event.position().x(), event.position().y()
        for hours, (rx, ry, rw, rh) in self._range_rects:
            if rx <= px <= rx + rw and ry <= py <= ry + rh:
                self._hours = float(hours)
                self.update()
                return
        super().mousePressEvent(event)

    def _draw_range_selector(self, p: QPainter, W: int):
        f7 = QFont("Segoe UI", 7)
        p.setFont(f7)
        fm = p.fontMetrics()
        x = W - 4
        rects = []
        for label, hours in reversed(self._RANGES):
            tw = fm.horizontalAdvance(label) + 10
            x -= tw
            active = int(self._hours) == hours
            bg = QColor(ACCENT) if active else QColor(BG_PANEL)
            fg = QColor("#1A1D22") if active else QColor(TEXT_DIM)
            p.fillRect(x, 1, tw, self._SEL_H - 2, bg)
            p.setPen(fg)
            p.drawText(x, 1, tw, self._SEL_H - 2, Qt.AlignCenter, label)
            rects.append((hours, (x, 1, tw, self._SEL_H - 2)))
            x -= 2
        self._range_rects = rects

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()
        p.fillRect(0, 0, W, H, QColor(BG_SURFACE))

        self._draw_range_selector(p, W)

        rows = _hist_csv.get_range(self._hours)
        data = _rows_to_ha(rows, self._hours)

        PL, PR  = 30, 30   # rechts = K-as
        PT      = self._SEL_H + 2
        PB      = 12
        gW = W - PL - PR
        gH = H - PT - PB
        f6 = QFont("Segoe UI", 6)
        p.setFont(f6)

        if not data:
            p.setPen(QColor(TEXT_DIM))
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(0, PT, W, H - PT, Qt.AlignCenter,
                       tr("shist.no_data"))
            return

        # Auto-scale SFI: ±10% marge rondom het databereik
        sfis = [sol.get("sfi", 0) for _, _, _, sol in data if sol.get("sfi", 0) > 0]
        sfi_min = max(0,   min(sfis) - 10) if sfis else 50
        sfi_max = max(150, max(sfis) + 10) if sfis else 200
        sfi_range = max(1, sfi_max - sfi_min)

        def sfi_y(v):
            return PT + int(gH * (1.0 - (max(sfi_min, min(sfi_max, v)) - sfi_min) / sfi_range))
        def kp_y(v):
            return PT + int(gH * (1.0 - max(0.0, min(9.0, v)) / 9.0))
        def ha_x(ha):
            return PL + int(gW * (1.0 - ha / self._hours))

        # Rasterlijnen + SFI-labels
        for ref in [sfi_min + sfi_range * f for f in (0.25, 0.5, 0.75)]:
            yr = sfi_y(ref)
            p.setPen(QPen(QColor(BORDER), 1, Qt.DashLine))
            p.drawLine(PL, yr, W - PR, yr)
            p.setPen(QColor(TEXT_DIM))
            p.drawText(0, yr - 5, PL - 2, 10,
                       Qt.AlignRight | Qt.AlignVCenter, f"{int(ref)}")

        # K-index achtergrond-balken
        p.setPen(Qt.NoPen)
        for ha, ts, bp, sol in data:
            k = sol.get("k_index", 0)
            if k >= 3:
                x = ha_x(ha)
                alpha = int(min(120, k * 14))
                p.fillRect(x - 1, PT, 3, gH, QColor(200, 80, 50, alpha))

        gap = _gap_limit(data)

        # SFI-lijn (oranje) — onderbroken bij gaten in de data
        prev = None
        p.setPen(QPen(QColor("#FFA726"), 1.5))
        for ha, ts, bp, sol in reversed(data):
            sfi = sol.get("sfi", 0)
            if sfi <= 0:
                prev = None; continue
            x, y = ha_x(ha), sfi_y(sfi)
            if prev and abs(prev[2] - ha) <= gap:
                p.drawLine(prev[0], prev[1], x, y)
            prev = (x, y, ha)

        # K-index lijn (rood, rechts-as)
        prev = None
        p.setPen(QPen(QColor("#EF5350"), 1.0))
        for ha, ts, bp, sol in reversed(data):
            k = sol.get("k_index", 0)
            x, y = ha_x(ha), kp_y(k)
            if prev and abs(prev[2] - ha) <= gap:
                p.drawLine(prev[0], prev[1], x, y)
            prev = (x, y, ha)

        # Rechts: K-as labels (0, 3, 5, 9)
        p.setPen(QColor("#EF5350"))
        for kv in (0, 3, 5, 9):
            yk = kp_y(kv)
            p.drawText(W - PR + 2, yk - 5, PR - 4, 10,
                       Qt.AlignLeft | Qt.AlignVCenter, f"K{kv}")

        p.setPen(QColor(TEXT_DIM))
        p.setFont(f6)
        lbl = f"{int(self._hours)}h" if self._hours < 48 else f"{int(self._hours/24)}d"
        p.drawText(PL, H - PB + 2, 24, PB, Qt.AlignLeft, lbl)
        p.drawText(W - PR - 16, H - PB + 2, 16, PB, Qt.AlignRight, tr("sched.now"))
        p.setPen(QColor("#FFA726"))
        p.drawText(PL + 2, PT, 24, 10, Qt.AlignLeft, "SFI")


class BandHistChart(QWidget):
    """Band-betrouwbaarheid historiek per band — leest uit HAMIOS_history.csv."""

    SHOW   = ["160m","80m","60m","40m","30m","20m","17m","15m","12m","10m","6m"]
    COLORS = {
        "160m": "#7B1FA2", "80m":  "#C62828", "60m": "#E65100",
        "40m":  "#FFA000", "30m":  "#558B2F", "20m": "#4CAF50",
        "17m":  "#00897B", "15m":  "#00ACC1", "12m": "#1E88E5",
        "10m":  "#9C27B0", "6m":   "#E91E63",
    }

    # Legenda-hoogte: 2 rijen van 13px + 4px spatie = 30px
    # Tijdlabel: 12px  →  totaal onderkant: 42px
    _LEG_H  = 30   # hoogte van de legenda-strip
    _TIME_H = 12   # hoogte van "24h … nu" tijdlijn
    _SEL_H  = 14   # hoogte van de tijdbereik-selector balk

    _RANGES = [("24h", 24), ("7d", 168), ("30d", 720), ("1j", 8760)]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hours        = 24.0
        self._visible      = set(self.SHOW)   # geselecteerde banden
        self._legend_rects: list[tuple[str, tuple]] = []   # [(band, (x,y,w,h))]
        self._range_rects:  list[tuple[int, tuple]] = []   # [(hours, (x,y,w,h))]
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setMinimumHeight(110)
        self.setCursor(Qt.PointingHandCursor)
        t = QTimer(self)
        t.timeout.connect(self.update)
        t.start(60_000)

    def mousePressEvent(self, event):
        """Klik op tijdbereik-selector of legenda-item."""
        px, py = event.position().x(), event.position().y()
        for hours, (rx, ry, rw, rh) in self._range_rects:
            if rx <= px <= rx + rw and ry <= py <= ry + rh:
                self._hours = float(hours)
                self.update()
                return
        for band, (rx, ry, rw, rh) in self._legend_rects:
            if rx <= px <= rx + rw and ry <= py <= ry + rh:
                if band in self._visible:
                    self._visible.discard(band)
                else:
                    self._visible.add(band)
                self.update()
                return
        super().mousePressEvent(event)

    def set_data(self, solar: dict):
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()
        p.fillRect(0, 0, W, H, QColor(BG_SURFACE))

        # ── Tijdbereik-selector ────────────────────────────────────────────────
        self._draw_range_selector(p, W)

        rows = _hist_csv.get_range(self._hours)
        data = _rows_to_ha(rows, self._hours)

        PB_total = self._TIME_H + self._LEG_H   # ruimte onder grafiek
        PL, PR   = 30, 4
        PT       = self._SEL_H + 2              # boven de grafiek: selector-balk
        PB       = PB_total
        gW, gH   = W - PL - PR, H - PT - PB

        if not data:
            p.setPen(QColor(TEXT_DIM))
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(0, PT, W, H - PT - PB_total, Qt.AlignCenter,
                       tr("hist.no_data"))
            self._draw_legend(p, W, H)
            return

        f6 = QFont("Segoe UI", 6)
        p.setFont(f6)

        def ha_x(ha):
            return PL + int(gW * (1.0 - ha / self._hours))
        def pct_y(pct):
            return PT + int(gH * (1.0 - pct / 100))

        # Rasterlijnen
        for pct in (25, 50, 75):
            yr = pct_y(pct)
            p.setPen(QPen(QColor(BORDER), 1, Qt.DashLine))
            p.drawLine(PL, yr, W - PR, yr)
            p.setPen(QColor(TEXT_DIM))
            p.drawText(0, yr - 5, PL - 2, 10,
                       Qt.AlignRight | Qt.AlignVCenter, f"{pct}%")

        # Lijnen per band (alleen zichtbare banden), onderbroken bij gaten
        gap = _gap_limit(data)
        for band in self.SHOW:
            if band not in self._visible:
                continue
            p.setPen(QPen(QColor(self.COLORS[band]), 1.2))
            prev = None
            for ha, ts, bp, sol in reversed(data):
                pct = bp.get(band, 0)
                x, y = ha_x(ha), pct_y(pct)
                if prev and abs(prev[2] - ha) <= gap:
                    p.drawLine(prev[0], prev[1], x, y)
                prev = (x, y, ha)

        # Tijdlabels direct onder grafiek
        y_time = H - PB_total + 2
        p.setPen(QColor(TEXT_DIM))
        p.setFont(f6)
        lbl = f"{int(self._hours)}h" if self._hours < 48 else f"{int(self._hours/24)}d"
        p.drawText(PL, y_time, 24, 10, Qt.AlignLeft, lbl)
        p.drawText(W - PR - 20, y_time, 20, 10, Qt.AlignRight, tr("sched.now"))

        # Legenda onder tijdlabels
        self._draw_legend(p, W, H)

    def _draw_range_selector(self, p: QPainter, W: int):
        """Teken tijdbereik-knoppen bovenaan de grafiek."""
        f7 = QFont("Segoe UI", 7)
        p.setFont(f7)
        fm   = p.fontMetrics()
        x    = W - 4
        rects = []
        for label, hours in reversed(self._RANGES):
            tw = fm.horizontalAdvance(label) + 10
            x -= tw
            active = int(self._hours) == hours
            bg = QColor(ACCENT) if active else QColor(BG_PANEL)
            fg = QColor("#1A1D22") if active else QColor(TEXT_DIM)
            p.fillRect(x, 1, tw, self._SEL_H - 2, bg)
            p.setPen(fg)
            p.drawText(x, 1, tw, self._SEL_H - 2, Qt.AlignCenter, label)
            rects.append((hours, (x, 1, tw, self._SEL_H - 2)))
            x -= 2
        self._range_rects = rects

    def _draw_legend(self, p: QPainter, W: int, H: int):
        """Teken twee rijen met klikbare band-labels.
        Geselecteerd = volle kleur; uitgeschakeld = doorgestreept + grijs.
        """
        f7 = QFont("Segoe UI", 7)
        p.setFont(f7)

        PL    = 30
        row1  = self.SHOW[:6]
        row2  = self.SHOW[6:]
        col_w = max(32, (W - PL) // 6)
        y1    = H - self._LEG_H + 3
        y2    = H - self._LEG_H + 16
        ITEM_H = 13

        self._legend_rects = []

        for row_bands, y_base in ((row1, y1), (row2, y2)):
            for j, band in enumerate(row_bands):
                x   = PL + j * col_w
                sel = band in self._visible
                clr = QColor(self.COLORS[band]) if sel else QColor(80, 85, 90)

                # Achtergrond-hover hint voor geselecteerde items
                if sel:
                    p.fillRect(x - 1, y_base - 2, col_w - 2, ITEM_H,
                               QColor(255, 255, 255, 12))

                # Kleurlijn
                p.setPen(QPen(clr, 2))
                p.drawLine(x, y_base + 4, x + 10, y_base + 4)

                # Naam
                p.setPen(clr)
                p.drawText(x + 13, y_base - 1, col_w - 14, 12,
                           Qt.AlignLeft | Qt.AlignVCenter, band)

                # Doorstrepen als uitgeschakeld
                if not sel:
                    p.setPen(QPen(QColor(80, 85, 90), 1))
                    mid_y = y_base + 4
                    p.drawLine(x + 13, mid_y, x + col_w - 4, mid_y)

                # Sla hit-rect op voor mousePressEvent
                self._legend_rects.append(
                    (band, (x - 1, y_base - 2, col_w - 2, ITEM_H)))


# ── LightningPanel ────────────────────────────────────────────────────────────

class LightningPanel(QWidget):
    """Bliksemstatus, teller en fade-instelling."""

    settings_changed = Signal()
    qrn_alert        = Signal(str, str, str)   # (icon, text, color)

    def __init__(self, lightning_layer, cfg=None, parent=None):
        super().__init__(parent)
        self._layer     = lightning_layer
        self._cfg       = cfg
        self._qrn_level = 0
        self._build_ui()
        lightning_layer.status_signal.connect(self._on_status)
        language_changed.connect(self._retranslate)
        if cfg:
            self._layer.set_fade_seconds(cfg.lightning_fade)

        self._refresh = QTimer(self)
        self._refresh.timeout.connect(self._update_count)
        self._refresh.start(2000)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)

        f8 = QFont("Segoe UI", 8)
        f9b = QFont("Segoe UI", 9); f9b.setBold(True)

        # Status
        row = QHBoxLayout()
        self._status_hdr = QLabel(tr("lightn.status") + ":", font=f8,
                                   styleSheet=f"color:{TEXT_DIM};")
        row.addWidget(self._status_hdr)
        self._status_lbl = QLabel(tr("lightn.connecting"))
        self._status_lbl.setFont(f9b)
        self._status_lbl.setStyleSheet(f"color:{TEXT_DIM};")
        row.addWidget(self._status_lbl)
        row.addStretch()
        layout.addLayout(row)

        # Teller
        row2 = QHBoxLayout()
        self._count_hdr = QLabel(tr("lightn.discharges") + ":", font=f8,
                                  styleSheet=f"color:{TEXT_DIM};")
        row2.addWidget(self._count_hdr)
        self._count_lbl = QLabel("0")
        self._count_lbl.setFont(f9b)
        self._count_lbl.setStyleSheet(f"color:{TEXT_H1};")
        row2.addWidget(self._count_lbl)
        self._count_period_lbl = QLabel("")
        self._count_period_lbl.setFont(f8)
        self._count_period_lbl.setStyleSheet(f"color:{TEXT_DIM};")
        row2.addWidget(self._count_period_lbl)
        row2.addStretch()
        layout.addLayout(row2)

        # QRN-advies
        self._qrn_lbl = QLabel("")
        self._qrn_lbl.setFont(f8)
        self._qrn_lbl.setWordWrap(True)
        self._qrn_lbl.setStyleSheet(f"color:{TEXT_DIM};")
        layout.addWidget(self._qrn_lbl)

        # Dichtstbijzijnde inslag
        self._near_lbl = QLabel("")
        self._near_lbl.setFont(f8)
        self._near_lbl.setStyleSheet(f"color:{TEXT_DIM};")
        layout.addWidget(self._near_lbl)

        layout.addStretch()

    def _retranslate(self, _=None):
        self._status_hdr.setText(tr("lightn.status") + ":")
        self._count_hdr.setText(tr("lightn.discharges") + ":")

    def _on_status(self, status: str):
        msgs = {
            "live":     (tr("lightn.connected"),     "#4CAF50"),
            "disc":     (tr("lightn.disconnected"),  "#EF5350"),
            "no_lib":   (tr("lightn.no_lib"),        "#FFA726"),
            "disabled": (tr("lightn.disabled"),      TEXT_DIM),
        }
        txt, clr = msgs.get(status, ("…", TEXT_DIM))
        self._status_lbl.setText(txt)
        self._status_lbl.setStyleSheet(
            f"color:{clr}; font-weight:bold; font-size:9pt;")
        if status == "disabled":
            self._count_lbl.setText("—")
            self._count_period_lbl.setText("")

    # QRN wordt berekend over inslagen binnen deze straal van het QTH
    _QRN_RADIUS_KM = 2000

    def _update_count(self):
        # Filter naar inslagen nabij QTH (QRN is lokaal fenomeen); afstanden
        # komen uit de cache van de bliksemlaag (per inslag één keer berekend)
        strikes = self._layer.strikes_km()
        if self._cfg:
            n = sum(1 for *_, km in strikes if km is not None and km <= self._QRN_RADIUS_KM)
        else:
            n = len(strikes)
        self._count_lbl.setText(str(n))
        # Toon de periode (fade-duur) naast het getal
        secs = int(self._layer.fade_seconds)
        if secs < 60:
            period = f"/{secs}s"
        elif secs < 3600:
            period = f"/{secs//60}m"
        else:
            period = f"/{secs//3600}u"
        self._count_period_lbl.setText(period)

        # QRN-niveau + advies
        if n == 0:
            lvl, qrn, qrn_clr = 0, tr("lightn.qrn.none"),                         TEXT_DIM
        elif n < 10:
            lvl, qrn, qrn_clr = 1, tr("qrn.low"),    "#4CAF50"
        elif n < 50:
            lvl, qrn, qrn_clr = 2, tr("qrn.medium"), "#FFA726"
        elif n < 200:
            lvl, qrn, qrn_clr = 3, tr("qrn.high"),   "#FF7043"
        else:
            lvl, qrn, qrn_clr = 4, tr("qrn.severe"),  "#EF5350"
        radius_lbl = f" ({n} inslagen ≤{self._QRN_RADIUS_KM//1000}Mm)" if n > 0 else ""
        self._qrn_lbl.setText(f"QRN: {qrn}{radius_lbl}")
        self._qrn_lbl.setStyleSheet(f"color:{qrn_clr}; font-size:8pt;")

        # Stuur naar meldingen-paneel als niveau stijgt
        if lvl > self._qrn_level and lvl >= 2:
            self.qrn_alert.emit("⚡", f"QRN: {qrn}", qrn_clr)
        self._qrn_level = lvl

        # Dichtstbijzijnde inslag (volledige set; afstanden uit de cache)
        kms = [km for *_, km in strikes if km is not None]
        if self._cfg and kms:
            try:
                min_km = min(kms)
                if min_km is not None:
                    self._near_lbl.setText(f"{tr('lightn.nearest')}: {min_km:.0f} {tr('lightn.km')}")
                    clr = "#EF5350" if min_km < 100 else "#FFA726" if min_km < 300 else TEXT_DIM
                    self._near_lbl.setStyleSheet(f"color:{clr}; font-size:8pt;")
                else:
                    self._near_lbl.setText("")
            except Exception:
                pass
        else:
            self._near_lbl.setText("")

    def set_cfg(self, cfg):
        self._cfg = cfg
        self._layer.set_fade_seconds(cfg.lightning_fade)
        rate = int(getattr(cfg, "lightning_rate", 500))
        self._refresh.setInterval(max(100, rate))


# ── AlertsWidget ──────────────────────────────────────────────────────────────

class AlertsWidget(QWidget):
    """Meldingen-paneel: gefilterde ruimteweer-alerts + satelliet in QTH-zone.
    Wis-knop verwijdert alle meldingen."""

    def __init__(self, cfg=None, parent=None):
        super().__init__(parent)
        self._cfg          = cfg
        self._solar_data:  dict  = {}
        self._sat_zone:    list  = []
        self._cleared      = False
        # Persistente meldingenlijst met tijdstempel (nieuwste boven)
        # items: (ts_float, icon, text, color, detail)
        self._alert_log: list = []

        # Dynamische verversing — tijdstempels bijhouden onafhankelijk van solar-refresh
        self._dyn_timer = QTimer(self)
        self._dyn_timer.timeout.connect(self._rebuild)
        self._dyn_timer.start(30_000)   # elke 30 seconden

        v = QVBoxLayout(self)
        v.setContentsMargins(4, 4, 4, 4)
        v.setSpacing(3)

        # Wis-knop
        f8 = QFont("Segoe UI", 8)
        top = QHBoxLayout()
        self._count_lbl = QLabel(tr("alerts.count", n=0))
        self._count_lbl.setFont(f8)
        self._count_lbl.setStyleSheet(f"color: {TEXT_DIM};")
        top.addWidget(self._count_lbl)
        top.addStretch()
        btn_wis = QPushButton(tr("alerts.clear")); btn_wis.setObjectName("danger")
        btn_wis.setFont(f8)
        btn_wis.clicked.connect(self._clear)
        top.addWidget(btn_wis)
        v.addLayout(top)

        # Scrollbare lijst
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(f"QScrollArea {{ border: none; }}")
        v.addWidget(self._scroll, 1)

    def set_cfg(self, cfg):
        self._cfg = cfg
        self._rebuild()

    def set_data(self, alerts: list):
        """NOAA alerts — worden NIET meer getoond (raw NOAA tekst ongewenst)."""
        # Bewaar voor eventueel intern gebruik maar toon niet

    def set_solar_data(self, solar: dict):
        """Solar data bijwerken — alleen echte drempel-alerts tonen."""
        cfg = self._cfg
        # Controleer of K of X-flare de drempel OVERSCHRIJDT
        new_k_alert = False
        new_x_alert = False
        try:
            k = float(str(solar.get("k_index", "0")).replace("—", "0") or "0")
            threshold = getattr(cfg, "k_alert", 4) if cfg else 4
            k_en = getattr(cfg, "k_alert_en", True) if cfg else True
            if k_en and k >= threshold:
                # Alleen resetten als K waarde veranderd is t.o.v. vorige
                # Hele K-stappen vergelijken: de NOAA-waarde verandert per
                # minuut; kleine schommelingen mogen een gewiste melding niet terugzetten
                prev_k = float(str(self._solar_data.get("k_index", "0")).replace("—","0") or "0")
                if round(k) != round(prev_k):
                    new_k_alert = True
        except (ValueError, TypeError):
            pass
        try:
            xray = str(solar.get("xray", ""))
            x_en = getattr(cfg, "xflare_alert_en", True) if cfg else True
            if x_en and xray[:1].upper() in ("M", "X"):
                prev_x = str(self._solar_data.get("xray", ""))
                if xray != prev_x:
                    new_x_alert = True
        except (ValueError, TypeError):
            pass
        self._solar_data = solar
        # Alleen _cleared resetten als er écht iets nieuws is
        if new_k_alert or new_x_alert:
            self._cleared = False
        self._rebuild()

    def set_sat_zone(self, names: list):
        """Lijst van satellieten zichtbaar van QTH (naam incl. elevatie)."""
        prev = set(self._sat_zone)
        self._sat_zone = names
        new_entries = set(names) - prev
        if new_entries:
            self._cleared = False
            # Ping-geluid voor elke nieuw binnengekomen satelliet
            if getattr(self._cfg, "sat_zone_ping", True):
                import threading
                from .sound import play_sat_ping
                threading.Thread(target=play_sat_ping, daemon=True).start()
        self._rebuild()

    def add_alert(self, icon: str, text: str, color: str, detail: str = ""):
        """Voeg een melding toe vanuit externe bronnen (bijv. PropAdvWidget)."""
        import time as _t
        self._alert_log.insert(0, (_t.time(), icon, text, color, detail))
        max_n = int(getattr(self._cfg, "alert_max", 50)) if self._cfg else 50
        self._alert_log = self._alert_log[:max_n]
        self._rebuild()

    def _clear(self):
        self._sat_zone    = []
        self._solar_data  = {}
        self._alert_log   = []
        self._cleared     = True
        self._rebuild()

    def _rebuild(self):
        """Bouw de meldingenlijst op basis van instellingen."""
        items: list[tuple] = []  # (kleur_hex, icon, tekst, detail)
        cfg = self._cfg
        data = self._solar_data

        # ── Altijd: status K-index en X-straling ──────────────────────────────
        try:
            k = float(str(data.get("k_index", "—")).replace("—", "0") or "0")
            k_clr = ("#EF5350" if k >= 7 else "#FFA726" if k >= 5
                     else "#FFF176" if k >= 3 else "#4FC3F7")
            xray  = str(data.get("xray", "—"))
            items.append((k_clr, "🧲", tr("alert.k_status", k=f"{k:.0f}", xray=xray), "", ""))
        except (ValueError, TypeError):
            pass

        # ── K-storm drempel-alert ─────────────────────────────────────────────
        if not cfg or getattr(cfg, "k_alert_en", True):
            threshold = getattr(cfg, "k_alert", 4) if cfg else 4
            try:
                k = float(str(data.get("k_index", "0")).replace("—", "0") or "0")
            except (ValueError, TypeError):
                k = 0.0
            if k >= threshold:
                clr = "#EF5350" if k >= 7 else "#FFA726"
                items.append((clr, "🚨",
                    tr("alert.k_storm", k=f"{k:.0f}", thr=threshold),
                    tr("alert.k_storm_detail"), ""))

        # ── X-flare alert ─────────────────────────────────────────────────────
        if not cfg or getattr(cfg, "xflare_alert_en", True):
            xray = str(data.get("xray", ""))
            if xray and xray[0].upper() in ("M", "X"):
                clr = "#EF5350" if xray[0].upper() == "X" else "#FFA726"
                items.append((clr, "☢", tr("alert.xflare", xray=xray), "", ""))

        # ── Satellieten in QTH-zone ────────────────────────────────────────────
        for entry in self._sat_zone:
            items.append(("#4CAF50", "🛰", tr("alert.sat_qth", name=entry), "", ""))

        # ── Externe meldingen (analyse, enz.) uit _alert_log ──────────────────
        import time as _t
        now = _t.time()
        for ts, icon, text, color, detail in self._alert_log:
            age  = now - ts
            mins = int(age / 60)
            secs = int(age % 60)
            if mins > 0:
                tstr = tr("alert.min_ago", m=mins)
            else:
                tstr = tr("alert.sec_ago", s=secs)
            items.append((color, icon, text, detail or "", tstr))

        # ── Bouw widgets ──────────────────────────────────────────────────────
        container = QWidget()
        container.setStyleSheet(f"background: {BG_PANEL};")
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(3)

        f8 = QFont("Segoe UI", 8)
        f7 = QFont("Segoe UI", 7)

        if not items:
            lbl = QLabel(tr("alerts.none_active"))
            lbl.setFont(f8)
            lbl.setStyleSheet(f"color: {TEXT_DIM};")
            lbl.setAlignment(Qt.AlignCenter)
            vbox.addWidget(lbl)
        else:
            for clr, icon, text, detail, tstr in items:
                frame = QFrame()
                frame.setStyleSheet(
                    f"QFrame {{ background:{BG_SURFACE}; }}")
                fl = QVBoxLayout(frame)
                fl.setContentsMargins(6, 3, 4, 3)
                fl.setSpacing(1)
                # Tekst + tijdstempel op één rij
                top_row = QHBoxLayout()
                lbl_m = QLabel(f"{icon}  {text}")
                lbl_m.setFont(f8)
                lbl_m.setStyleSheet(f"color: {clr};")
                lbl_m.setWordWrap(True)
                top_row.addWidget(lbl_m, 1)
                if tstr:
                    lbl_ts = QLabel(tstr)
                    lbl_ts.setFont(f7)
                    lbl_ts.setStyleSheet(f"color: {TEXT_DIM};")
                    lbl_ts.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    top_row.addWidget(lbl_ts)
                fl.addLayout(top_row)
                if detail:
                    lbl_d = QLabel(detail)
                    lbl_d.setFont(f7)
                    lbl_d.setStyleSheet(f"color: {TEXT_DIM};")
                    fl.addWidget(lbl_d)
                vbox.addWidget(frame)

        vbox.addStretch()
        self._scroll.setWidget(container)
        n = len(items)
        self._count_lbl.setText(tr("alerts.count1" if n == 1 else "alerts.count", n=n))


# ── DXSpotsTable ──────────────────────────────────────────────────────────────

# ── Continent-helpers ─────────────────────────────────────────────────────────

# Compacte prefix→continent tabel
_DXCC_CONT: dict[str, str] = {
    "W":"NA","K":"NA","N":"NA","AA":"NA","AB":"NA","AC":"NA","AD":"NA",
    "AE":"NA","AF":"NA","AG":"NA","AH":"NA","AI":"NA","AJ":"NA","AK":"NA",
    "VE":"NA","VA":"NA","KH6":"NA","KL":"NA","XE":"NA","CO":"NA","HI":"NA",
    "PY":"SA","LU":"SA","CE":"SA","OA":"SA","HC":"SA","YV":"SA","CX":"SA",
    "DL":"EU","F":"EU","G":"EU","GW":"EU","GM":"EU","GI":"EU","I":"EU",
    "SP":"EU","OM":"EU","OK":"EU","HA":"EU","OH":"EU","SM":"EU","LA":"EU",
    "OZ":"EU","PA":"EU","ON":"EU","HB":"EU","OE":"EU","EA":"EU","CT":"EU",
    "YO":"EU","LZ":"EU","SV":"EU","TA":"EU","TF":"EU","EI":"EU","YU":"EU",
    "9A":"EU","S5":"EU","YL":"EU","LY":"EU","ES":"EU","5B":"EU","9H":"EU",
    "UA":"EU","RA":"EU","RZ":"EU","R":"EU",
    "JA":"AS","HL":"AS","DS":"AS","BY":"AS","BA":"AS","VR":"AS","BV":"AS",
    "9V":"AS","VU":"AS","HS":"AS","DU":"AS","YB":"AS","UA9":"AS","UA0":"AS",
    "4X":"AS","4Z":"AS","A9":"AS","A4":"AS","A6":"AS","HZ":"AS","EP":"AS",
    "AP":"AS","JY":"AS",
    "VK":"OC","ZL":"OC","FK":"OC","FO":"OC","KH0":"OC","H44":"OC",
    "ZS":"AF","V5":"AF","A2":"AF","Z2":"AF","5H":"AF","5Z":"AF","ET":"AF",
    "SU":"AF","CN":"AF","7X":"AF","TS":"AF","5A":"AF","3B8":"AF",
}

def _qth_to_continent(lat: float, lon: float) -> str:
    if   lat > 35 and -25 < lon < 65:   return "EU"
    elif lat > 0  and -170 < lon < -30: return "NA"
    elif lat < 0  and -90  < lon < -30: return "SA"
    elif lat > 0  and 60   < lon < 150: return "AS"
    elif lat < 0  and 100  < lon < 180: return "OC"
    elif -40 < lat < 38 and 10 < lon < 55: return "AF"
    return "??"

def _callsign_continent(call: str) -> str:
    call = call.upper().split("/")[0]
    for n in range(min(len(call), 3), 0, -1):
        if call[:n] in _DXCC_CONT:
            return _DXCC_CONT[call[:n]]
    return "??"


# ── DX Heatmap widget ──────────────────────────────────────────────────────────

class _DXHeatmapWidget(QWidget):
    """Band × UTC-uur heatmap van spot-activiteit (laatste 24u)."""

    _BANDS = ["160m","80m","40m","20m","17m","15m","12m","10m","6m"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._history: list = []
        self.setAttribute(Qt.WA_OpaquePaintEvent)

    def set_data(self, history: list):
        self._history = history
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        W, H = self.width(), self.height()
        p.fillRect(0, 0, W, H, QColor(BG_PANEL))

        BANDS = self._BANDS
        HOURS = 24
        ML, MR, MT, MB = 38, 4, 4, 18
        cw = max(1, (W - ML - MR) // HOURS)
        ch = max(1, (H - MT - MB) // len(BANDS))

        counts: dict = {}
        for ts, band in self._history:
            h = ts.hour
            counts[(band, h)] = counts.get((band, h), 0) + 1

        max_c = max(counts.values(), default=1)
        f7 = QFont("Segoe UI", 7)
        p.setFont(f7)

        for bi, band in enumerate(BANDS):
            cy = MT + bi * ch
            clr = QColor(_BAND_COLORS_HF.get(band, TEXT_DIM))
            p.setPen(clr)
            p.drawText(0, cy, ML - 3, ch,
                       Qt.AlignRight | Qt.AlignVCenter, band)
            for h in range(HOURS):
                n   = counts.get((band, h), 0)
                frac = n / max_c
                if frac > 0:
                    r = int(clr.red()   * frac + 26 * (1 - frac))
                    g = int(clr.green() * frac + 26 * (1 - frac))
                    b = int(clr.blue()  * frac + 26 * (1 - frac))
                    fill = QColor(r, g, b)
                else:
                    fill = QColor("#1A1C1F")
                p.fillRect(ML + h * cw, cy, cw - 1, ch - 1, fill)

        # Uur-labels
        p.setPen(QColor(TEXT_DIM))
        for h in range(0, HOURS, 3):
            lx = ML + h * cw + cw // 2
            p.drawText(lx - 8, H - MB + 2, 16, MB - 2,
                       Qt.AlignCenter, f"{h:02d}")

        # Huidig uur markering
        cur_h = _dt.datetime.now(_dt.timezone.utc).hour
        p.setPen(QPen(QColor(ACCENT), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRect(ML + cur_h * cw, MT, cw - 1, len(BANDS) * ch - 1)


# ── DXSpotsTable ──────────────────────────────────────────────────────────────

class DXSpotsTable(QWidget):
    """Live DX spots paneel — v4 stijl met filter, status en heatmap."""

    settings_changed = Signal()

    def __init__(self, cfg=None, parent=None):
        super().__init__(parent)
        self._cfg          = cfg
        self._all_spots:  list = []
        self._filtered:   list = []
        self._history:    list = []
        self._dx_font_sz: int  = getattr(cfg, "dx_font_size", 9) if cfg else 9
        self._build_ui()
        language_changed.connect(self._retranslate)
        if cfg:
            self._own_cb.setChecked(getattr(cfg, "dx_own_continent", False))
            if getattr(cfg, "dx_heatmap", False):
                self._heatmap_btn.setChecked(True)

    def set_cfg(self, cfg):
        self._cfg = cfg
        self._own_cb.setChecked(getattr(cfg, "dx_own_continent", False))
        font_size = getattr(cfg, "dx_font_size", 9)
        self._set_font_size(font_size)
        self._apply_filter()

    def set_font_size(self, size: int):
        self._set_font_size(size)

    def _retranslate(self, _=None):
        self._table.setHorizontalHeaderLabels(
            [tr("dx.col.utc"), tr("dx.col.band"), tr("dx.col.mhz"),
             tr("dx.col.dx"), tr("dx.col.spotter"), tr("dx.col.comment")])
        self._own_cb.setText(tr("dx.filter.continent"))
        self._heatmap_btn.setText(tr("dx.heatmap"))

    def _set_font_size(self, size: int):
        self._dx_font_sz = max(6, size)
        fmono = QFont("Consolas", self._dx_font_sz)
        self._table.setFont(fmono)
        self._table.verticalHeader().setDefaultSectionSize(max(14, self._dx_font_sz + 6))
        self._fit_columns(fmono)
        self._update_table()   # herteken met nieuwe fontgrootte

    # Kolombreedtes in tekens (monospace): UTC, band, MHz, DX, spotter; commentaar rekt
    _COL_CHARS = (5, 4, 7, 10, 10)

    def _fit_columns(self, font: QFont):
        """Kolombreedtes op de tekenbreedte van het gebruikte lettertype, zodat
        bijv. de UTC-tijd bij elke lettergrootte volledig past."""
        from PySide6.QtGui import QFontMetrics
        cw = QFontMetrics(font).horizontalAdvance("0")
        for i, n in enumerate(self._COL_CHARS):
            self._table.setColumnWidth(i, int(cw * n + 14))

    def _build_ui(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(4, 4, 4, 4)
        v.setSpacing(3)

        f8 = QFont("Segoe UI", 8)

        # ── Bedieningsrij ────────────────────────────────────────────────────
        ctrl = QHBoxLayout()
        ctrl.setSpacing(6)
        self._own_cb = QCheckBox(tr("dx.filter.continent"))
        self._own_cb.setFont(f8)
        self._own_cb.toggled.connect(self._apply_filter)
        ctrl.addWidget(self._own_cb)

        self._heatmap_btn = QPushButton(tr("dx.heatmap"))
        self._heatmap_btn.setFont(f8)
        self._heatmap_btn.setCheckable(True)
        self._heatmap_btn.toggled.connect(self._toggle_heatmap)
        ctrl.addWidget(self._heatmap_btn)

        ctrl.addStretch()
        self._status_lbl = QLabel(tr("app.loading"))
        self._status_lbl.setFont(f8)
        self._status_lbl.setStyleSheet(f"color: {TEXT_DIM};")
        ctrl.addWidget(self._status_lbl)
        v.addLayout(ctrl)

        # ── Stacked: tabel / heatmap ──────────────────────────────────────
        self._stack = QStackedWidget()

        # Tabel
        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels(
            [tr("dx.col.utc"), tr("dx.col.band"), tr("dx.col.mhz"),
             tr("dx.col.dx"), tr("dx.col.spotter"), tr("dx.col.comment")])
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(False)
        fmono = QFont("Consolas", 8)
        self._table.setFont(fmono)
        hdr = self._table.horizontalHeader()
        hdr.setFont(QFont("Segoe UI", 7))
        for i in range(5):
            hdr.setSectionResizeMode(i, QHeaderView.Fixed)
        hdr.setSectionResizeMode(5, QHeaderView.Stretch)
        self._fit_columns(fmono)
        self._table.verticalHeader().setDefaultSectionSize(16)
        self._table.cellClicked.connect(self._on_row_clicked)
        self._table.setStyleSheet(f"""
            QTableWidget {{
                background: {BG_SURFACE}; color: {TEXT_BODY};
                border: none;
            }}
            QHeaderView::section {{
                background: {BG_PANEL}; color: {ACCENT};
                border: none; padding: 1px 3px;
                font-size: 7pt; font-weight: bold;
            }}
            QTableWidget::item:alternate {{ background: {BG_ROOT}; }}
            QTableWidget::item:selected  {{ background: #2A4060; }}
        """)
        self._stack.addWidget(self._table)

        # Heatmap
        self._heatmap = _DXHeatmapWidget()
        self._stack.addWidget(self._heatmap)

        v.addWidget(self._stack, 1)

        # CAT-statusbalk onderaan
        self._cat_bar = _CatBar()
        v.addWidget(self._cat_bar)

    def _on_row_clicked(self, row: int, col: int):
        """Klik op DX-spot rij → stuur frequentie naar CAT."""
        if row >= len(self._filtered):
            return
        spot = self._filtered[row]
        freq_khz = spot.get("freq_khz", 0.0)
        if not freq_khz:
            return
        hz   = int(freq_khz * 1000)
        # Bepaal modus op basis van band (SSB standaard voor DX)
        mode = "SSB"
        ok, msg = _cat_send(hz, mode)
        self._cat_bar.show_msg(
            f"📟  {freq_khz/1000:.3f} MHz  {mode}" if ok else f"📟  {msg}", ok)

    def set_data(self, spots: list):
        """spots = [{time, dx, freq_khz, band, spotter, comment}, ...]"""
        self._all_spots = spots
        # Bijhouden voor heatmap (24u buffer)
        now    = _dt.datetime.now(_dt.timezone.utc)
        cutoff = now - _dt.timedelta(hours=24)
        new    = [(now, s.get("band", "")) for s in spots if s.get("band")]
        self._history = (
            [(t, b) for t, b in self._history if t >= cutoff] + new)
        self._heatmap.set_data(self._history)
        self._apply_filter()

    def _apply_filter(self):
        spots = self._all_spots
        if self._own_cb.isChecked() and self._cfg:
            my = _qth_to_continent(self._cfg.qth_lat, self._cfg.qth_lon)
            spots = [s for s in spots
                     if _callsign_continent(s.get("spotter", "")) == my]
        self._filtered = spots
        if self._cfg:
            self._cfg.dx_own_continent = self._own_cb.isChecked()
        self._update_table()
        self._update_status()
        self.settings_changed.emit()

    def _update_status(self):
        n     = len(self._filtered)
        total = len(self._all_spots)
        ts    = _dt.datetime.now().strftime("%H:%M")
        filt  = tr("dx.own_cont_short") if self._own_cb.isChecked() else ""
        self._status_lbl.setText(
            f"{n}/{total} spots{filt}  {ts}" if total else tr("dx.no_spots", ts=ts))

    def _toggle_heatmap(self, on: bool):
        self._stack.setCurrentIndex(1 if on else 0)
        self._heatmap_btn.setStyleSheet(
            f"color: {ACCENT}; background: #32373F;" if on else "")
        if self._cfg:
            self._cfg.dx_heatmap = on
        self.settings_changed.emit()

    def _update_table(self):
        self._table.setRowCount(0)
        fmono = QFont("Consolas", self._dx_font_sz)
        for spot in self._filtered:
            freq    = spot.get("freq_khz", 0.0)
            call    = spot.get("dx",       "")
            spotter = spot.get("spotter",  "")
            tstr    = spot.get("time",     "—")
            band    = spot.get("band",     _freq_to_band(freq))
            comment = spot.get("comment",  "")
            clr     = QColor(_band_color_name(freq))

            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setRowHeight(row, 16)

            for col, (val, fg, align) in enumerate([
                (tstr,                          TEXT_DIM,  Qt.AlignCenter),
                (band,                          None,      Qt.AlignCenter),
                (f"{freq/1000:.3f}" if freq else "—",
                                                TEXT_BODY, Qt.AlignRight | Qt.AlignVCenter),
                (call[:12],                     None,      Qt.AlignLeft  | Qt.AlignVCenter),
                (spotter[:10],                  TEXT_DIM,  Qt.AlignLeft  | Qt.AlignVCenter),
                (comment[:30],                  TEXT_DIM,  Qt.AlignLeft  | Qt.AlignVCenter),
            ]):
                item = QTableWidgetItem(val)
                item.setTextAlignment(align)
                item.setFont(fmono)
                if fg:
                    item.setForeground(QColor(fg))
                elif col in (1, 3):   # band en DX in bandkleur
                    item.setForeground(clr)
                self._table.setItem(row, col, item)


def _freq_to_band(freq_khz: float) -> str:
    if freq_khz < 2100:  return "160m"
    if freq_khz < 5000:  return "80m"
    if freq_khz < 7500:  return "40m"
    if freq_khz < 11000: return "30m"
    if freq_khz < 15500: return "20m"
    if freq_khz < 19000: return "17m"
    if freq_khz < 22000: return "15m"
    if freq_khz < 26000: return "12m"
    if freq_khz < 32000: return "10m"
    return "6m+"


def _band_color_name(freq_khz: float) -> str:
    if freq_khz < 2100:  return "#CE93D8"
    if freq_khz < 5000:  return "#EF5350"
    if freq_khz < 7500:  return "#FFA726"
    if freq_khz < 15500: return "#4CAF50"
    if freq_khz < 22000: return "#00BCD4"
    if freq_khz < 32000: return "#42A5F5"
    return "#AB47BC"


# ── PropAdvWidget ─────────────────────────────────────────────────────────────

_MODE_DB  = {"SSB": 0, "CW": 10, "FT8": 25, "FT4": 22, "WSPR": 35, "AM": -6,
             "PSK31": 12, "RTTY": 5, "FM": -3}
_POWER_DB = {"5W": -13, "10W": -10, "25W": -6, "50W": -3,
             "100W": 0, "200W": 3, "400W": 6, "1kW": 10, "1.5kW": 12}
_ANT_DB   = {
    "Isotropic 0dBi":   0,
    "Magnetic loop":    0,
    "Ground loop":      1,
    "Vertical":         0,
    "Groundplane":      0,
    "Inverted V":       1,
    "Dipole ~2dBi":     2,
    "EFHW":             2,
    "OCFD":             2,
    "J-pole":           2,
    "Long wire":        2,
    "Delta loop ~3dBi": 3,
    "Quad ~8dBi":       8,
    "Yagi ~7dBi":       7,
    "Beam ~10dBi":     10,
    "Stack 2×Yagi":    13,
}


def _set_cb_text(cb: "QComboBox", text: str):
    """Stel combobox in op text; valt terug op index 0 als niet gevonden."""
    idx = cb.findText(text)
    cb.setCurrentIndex(idx if idx >= 0 else 0)


# PropAdvWidget is verhuisd naar advice_panel.py (P2: advies op basis van
# centraal model + waarnemingen + ruimteweer-gebeurtenissen).


# ── WSPR ──────────────────────────────────────────────────────────────────────

class WSPRTableWidget(QWidget):
    """Live WSPR QSO records table with real-time updates."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._wspr_feed = None
        self._records = []

        vlay = QVBoxLayout(self)
        vlay.setContentsMargins(4, 4, 4, 4)
        vlay.setSpacing(2)

        # Status label
        self._status_lbl = QLabel(tr("app.loading"))
        self._status_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 8pt;")
        vlay.addWidget(self._status_lbl)

        # Table with sortable columns
        self._table = QTableWidget()
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels([
            tr("wspr.call"),
            tr("wspr.grid"),
            tr("wspr.freq"),
            tr("wspr.snr"),
            tr("wspr.distance"),
            tr("wspr.path"),
            tr("wspr.time_utc"),
        ])
        # Enable sorting by clicking column headers
        self._table.setSortingEnabled(True)
        self._table.sortItems(6, Qt.DescendingOrder)  # Sort by UTC time (descending)
        self._table.setStyleSheet(
            f"QTableWidget {{ background: {BG_PANEL}; color: {TEXT_BODY}; }}"
            f"QHeaderView::section {{ background: {BG_SURFACE}; color: {TEXT_H1}; "
            f"padding: 4px; font-size: 8pt; }}"
        )
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        # Eén regel per spot; kolommen passen zich aan de inhoud aan
        self._table.setWordWrap(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.resizeColumnsToContents()
        self._table.verticalHeader().setVisible(False)
        # Set header alignment to left
        self._table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        vlay.addWidget(self._table)

    def set_wspr_feed(self, feed):
        """Connect to WSPR feed for live updates."""
        self._wspr_feed = feed
        self._last_ok = None
        if feed:
            feed.data_updated.connect(self._on_wspr_data)
            feed.error_occurred.connect(self._on_wspr_error)

    def _on_wspr_data(self, records):
        """Update table with new WSPR data."""
        self._records = records
        self._last_ok = _dt.datetime.now()
        self._update_table()

    def _on_wspr_error(self, msg: str):
        """Storing: laatste echte data blijft staan, status meldt 'offline'."""
        since = (f" — {tr('wspr.last_update')}: {self._last_ok.strftime('%H:%M')}"
                 if self._last_ok else "")
        self._status_lbl.setText(f"⚠ {tr('wspr.offline')}{since}")
        self._status_lbl.setToolTip(msg)
        self._status_lbl.setStyleSheet("color: #FFA726; font-size: 8pt;")

    def _update_table(self):
        """Populate table with WSPR records."""
        # Sorteren uit tijdens vullen — anders husselt Qt de rijen door elkaar
        self._table.setSortingEnabled(False)
        self._table.setRowCount(0)
        self._status_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 8pt;")
        self._status_lbl.setToolTip(tr("wspr.note"))

        if not self._records:
            self._status_lbl.setText(tr("wspr.none_region"))
            self._table.setSortingEnabled(True)
            return

        n_out = sum(1 for r in self._records if r.get("direction") == "out")
        self._status_lbl.setText(
            f"{len(self._records)} {tr('wspr.records')}  ·  → {n_out}  ← "
            f"{len(self._records) - n_out}  "
            f"({tr('wspr.last_update')}: {_dt.datetime.now().strftime('%H:%M')})"
        )

        for row, record in enumerate(self._records[:100]):  # Limit to 100 rows
            self._table.insertRow(row)

            # Verre station, met richting: → eigen regio gehoord, ← gehoord in eigen regio
            arrow = "→" if record.get("direction") == "out" else "←"
            call_item = QTableWidgetItem(f"{arrow} {record.get('call_sign', '?')}")
            call_item.setForeground(QColor(ACCENT))
            call_item.setToolTip(
                f"{record.get('tx_call', '?')} ({record.get('tx_grid', '?')}) → "
                f"{record.get('rx_call', '?')} ({record.get('rx_grid', '?')})  ·  "
                f"{record.get('band', '')}  ·  {record.get('power', '')}")
            self._table.setItem(row, 0, call_item)

            # Locator van het verre station
            grid_item = QTableWidgetItem(record.get("grid", "?"))
            self._table.setItem(row, 1, grid_item)

            # Frequency
            freq = record.get("frequency", 0)
            freq_item = NumericTableItem(f"{freq:.4f}" if freq else "?", float(freq) if freq else 0)
            self._table.setItem(row, 2, freq_item)

            # SNR
            snr = record.get("snr", 0)
            snr_item = NumericTableItem(f"{snr:+d}" if snr else "?", int(snr) if snr else 0)
            snr_color = QColor("#4CAF50") if snr >= -10 else QColor("#FFA726") if snr >= -20 else QColor("#EF5350")
            snr_item.setForeground(snr_color)
            self._table.setItem(row, 3, snr_item)

            # Distance
            distance = record.get("distance", 0)
            dist_item = NumericTableItem(f"{distance} km", int(distance) if distance else 0)
            self._table.setItem(row, 4, dist_item)

            # Azimuth
            azimuth = record.get("azimuth", 0)
            az_item = NumericTableItem(f"{azimuth}°", int(azimuth) if azimuth else 0)
            self._table.setItem(row, 5, az_item)

            # Time
            time_str = record.get("time", "")
            time_sort_val = record.get("time", "")
            if time_str:
                try:
                    ts = _dt.datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                    time_str = ts.strftime("%H:%M:%S")
                    time_sort_val = ts.timestamp()
                except (ValueError, AttributeError):
                    time_sort_val = 0
            time_item = NumericTableItem(time_str, float(time_sort_val) if isinstance(time_sort_val, (int, float)) else 0)
            time_item.setForeground(QColor(TEXT_DIM))
            self._table.setItem(row, 6, time_item)

        self._table.setSortingEnabled(True)
        self._table.resizeColumnsToContents()
        self._table.resizeRowsToContents()

    def set_font_size(self, pt: int) -> None:
        """Set font size for table and adjust column widths accordingly."""
        # Update table font
        font = self._table.font()
        font.setPointSize(pt)
        self._table.setFont(font)

        # Update status label font
        status_font = self._status_lbl.font()
        status_font.setPointSize(pt - 1)  # Status label slightly smaller
        self._status_lbl.setFont(status_font)

        # Update stylesheet to include proper font sizes
        self._table.setStyleSheet(
            f"QTableWidget {{ background: {BG_PANEL}; color: {TEXT_BODY}; font-size: {pt}pt; }}"
            f"QHeaderView::section {{ background: {BG_SURFACE}; color: {TEXT_H1}; "
            f"padding: 4px; font-size: {pt}pt; }}"
        )

        # Ensure header alignment is preserved (left-aligned)
        self._table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self._table.resizeColumnsToContents()
        self._table.resizeRowsToContents()
