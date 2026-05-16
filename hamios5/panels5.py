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
PropAdvWidget    — Propagatie-advies tekst
"""

import datetime as _dt
import math
import time as _time

from PySide6.QtCore import Qt, QTimer, QPointF, QRectF, Signal
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QScrollArea, QTableWidget, QTableWidgetItem,
    QHeaderView, QSpinBox, QSizePolicy, QAbstractItemView,
    QCheckBox, QComboBox, QPushButton, QStackedWidget
)

from .theme import (
    ACCENT, BG_PANEL, BG_SURFACE, BG_ROOT,
    TEXT_H1, TEXT_BODY, TEXT_DIM, BORDER
)
from .charts import history as _hist
from . import history as _hist_csv

# ── Propagatie-model ──────────────────────────────────────────────────────────

# ── Bandtabellen (v4-equivalent) ──────────────────────────────────────────────

_BANDS = [
    ("160m",  1.8,  50,   60),
    ("80m",   3.5,  50,   50),
    ("40m",   7.0,  60,   55),
    ("30m",  10.1,  65,   70),
    ("20m",  14.0,  70,   80),
    ("17m",  18.1,  85,  100),
    ("15m",  21.0, 100,  120),
    ("12m",  24.9, 125,  150),
    ("10m",  28.0, 145,  170),
    ("6m",   50.0, 185,  220),
]

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

_BAND_MODES_TBL = {
    "160m": "CW/FT8",  "80m": "CW/FT8",  "60m": "USB/FT8",
    "40m":  "SSB/FT8", "30m": "CW/FT8",  "20m": "SSB/FT8",
    "17m":  "SSB/FT8", "15m": "SSB/FT8", "12m": "SSB/FT8",
    "10m":  "SSB/FT8", "6m":  "Es/FT8",
}


def _calc_propagation_v4(sfi: float, ssn: float, k_index: float,
                          qth_lat: float = 52.0, snr_db: float = 0.0,
                          daytime: bool = True) -> tuple:
    """Port van v4 propagatiemodel. Geeft (band_pct, muf, luf)."""
    foF2 = 4.0 + (sfi - 70) * 0.065 + ssn * 0.012
    lat_fac = 1.0 - max(0.0, (abs(qth_lat) - 25) / 65) * 0.30
    foF2 *= lat_fac
    if not daytime:
        foF2 *= 0.55
    foF2 = max(1.5, min(foF2, 16.0))
    muf = foF2 * 3.8

    base_luf = 3.5 + k_index * 0.8
    if abs(qth_lat) > 45:
        base_luf *= 1.0 + (abs(qth_lat) - 45) / 25 * k_index * 0.20
    if not daytime:
        base_luf = max(0.5, base_luf * 0.4)
    luf = max(0.5, base_luf / (10 ** (snr_db / 20.0)))

    band_pct = []
    for name, freq in _BANDS_HF:
        if freq > muf:
            pct = 0
        elif freq < luf:
            pct = max(0, int(30 * freq / luf))
        else:
            ratio = (freq - luf) / max(0.1, muf - luf)
            peak  = 1.0 - abs(ratio - 0.55) * 1.4
            pct   = max(5, min(100, int(peak * 100)))
        band_pct.append((name, freq, pct))

    return band_pct, round(muf, 1), round(luf, 1)


def _reliability(sfi: float, k_index: float, day: bool = True) -> list[float]:
    """Eenvoudige 0–1 betrouwbaarheid per band (voor BandSchedWidget e.d.)."""
    k_factor = max(0.0, 1.0 - k_index * 0.11)
    result = []
    for _, _, sfi_day, sfi_ngt in _BANDS:
        threshold = sfi_day if day else sfi_ngt
        result.append(min(1.0, max(0.0, (sfi - threshold + 30) / 60)) * k_factor)
    return result



def _rel_color(rel: float) -> QColor:
    if rel >= 0.7: return QColor("#4CAF50")
    if rel >= 0.4: return QColor("#FFC107")
    if rel >= 0.15: return QColor("#FF9800")
    return QColor("#555A60")


# ── BandRelWidget ─────────────────────────────────────────────────────────────

class _BandChart(QWidget):
    """QPainter-gebaseerde bandbetrouwbaarheid balk (v4 stijl)."""

    BAR_H   = 22
    BAR_PAD = 4
    HDR_H   = 16
    LBL_W   = 46
    PCT_W   = 36
    FREQ_W  = 52
    MODE_W  = 72
    FT8_W   = 50

    def __init__(self, parent=None):
        super().__init__(parent)
        self._band_pct: list = []
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        n = len(_BANDS_HF)
        self.setMinimumHeight(self.HDR_H + n * (self.BAR_H + self.BAR_PAD) + self.BAR_PAD)

    def set_data(self, band_pct: list):
        self._band_pct = band_pct
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)
        W, H = self.width(), self.height()
        p.fillRect(0, 0, W, H, QColor(BG_PANEL))

        if not self._band_pct:
            return

        fixed = self.PCT_W + self.FREQ_W + self.MODE_W + self.FT8_W
        bar_max = max(40, W - self.LBL_W - fixed - 12)
        bar_x   = self.LBL_W + 4

        f7b = QFont("Segoe UI", 7); f7b.setBold(True)
        f7  = QFont("Segoe UI", 7)
        f8b = QFont("Segoe UI", 8); f8b.setBold(True)

        # Kolomhoofden
        p.setFont(f7b)
        for x, w, txt in [
            (bar_x + bar_max,                    self.PCT_W,  "%"),
            (bar_x + bar_max + self.PCT_W,        self.FREQ_W, "MHz"),
            (bar_x + bar_max + self.PCT_W + self.FREQ_W,        self.MODE_W, "Modus"),
            (bar_x + bar_max + self.PCT_W + self.FREQ_W + self.MODE_W, self.FT8_W,  "FT8"),
        ]:
            p.setPen(QColor(ACCENT))
            p.drawText(x, 0, w, self.HDR_H, Qt.AlignCenter, txt)

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
                           Qt.AlignCenter, "gesloten")
                p.setFont(f7b)
                p.drawText(bar_x + bar_max, y, self.PCT_W, self.BAR_H,
                           Qt.AlignCenter, "0%")
            else:
                fill_w = max(2, int((bar_max - 2) * pct / 100))
                # Gradient balk
                r, g, b = clr.red(), clr.green(), clr.blue()
                slices = min(self.BAR_H - 4, 6)
                for s in range(slices):
                    fac = 1.0 - (s / slices) * 0.50
                    sc  = QColor(min(255, int(r*fac)), min(255, int(g*fac)), min(255, int(b*fac)))
                    sy1 = y + 2 + s * (self.BAR_H - 4) // slices
                    sy2 = y + 2 + (s + 1) * (self.BAR_H - 4) // slices
                    p.setPen(Qt.NoPen)
                    p.setBrush(QBrush(sc))
                    p.drawRect(bar_x + 1, sy1, fill_w, sy2 - sy1)
                # Glans-lijn
                hl = QColor(min(255, int(r*1.5)), min(255, int(g*1.5)), min(255, int(b*1.5)))
                p.setPen(QPen(hl, 1))
                p.drawLine(bar_x + 2, y + 2, bar_x + fill_w, y + 2)

                p.setFont(f7b)
                p.setPen(QColor(TEXT_H1))
                p.drawText(bar_x + bar_max, y, self.PCT_W, self.BAR_H,
                           Qt.AlignCenter, f"{pct}%")

            # Freq
            p.setFont(f7)
            p.setPen(QColor(TEXT_DIM))
            p.drawText(bar_x + bar_max + self.PCT_W, y, self.FREQ_W, self.BAR_H,
                       Qt.AlignCenter, f"{freq:.3f}")

            # Modus
            p.drawText(bar_x + bar_max + self.PCT_W + self.FREQ_W, y,
                       self.MODE_W, self.BAR_H,
                       Qt.AlignCenter, _BAND_MODES_TBL.get(name, ""))

            # FT8
            p.drawText(bar_x + bar_max + self.PCT_W + self.FREQ_W + self.MODE_W, y,
                       self.FT8_W, self.BAR_H,
                       Qt.AlignCenter, _BAND_FT8_FREQ.get(name, "—"))


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

        f8 = QFont("Segoe UI", 8)

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
        v.addWidget(self._chart, 1)

        if cfg:
            self._recalc()

    def set_cfg(self, cfg):
        self._cfg = cfg
        self._recalc()

    @staticmethod
    def _is_day_at_qth(qth_lat: float, qth_lon: float) -> bool:
        """Bepaal dag/nacht via werkelijke zonpositie (zelfde als BandSchedWidget)."""
        import datetime as _dt, math as _m
        now = _dt.datetime.now(_dt.timezone.utc)
        doy  = now.timetuple().tm_yday
        decl = -23.45 * _m.cos(_m.radians(360 / 365 * (doy + 10)))
        ut   = now.hour + now.minute / 60 + now.second / 3600
        sun_lon = -(ut - 12) * 15
        sun_lon = ((sun_lon + 180) % 360) - 180
        lat_r  = _m.radians(qth_lat)
        slat_r = _m.radians(decl)
        dlon_r = _m.radians(qth_lon - sun_lon)
        cos_a  = (_m.sin(lat_r) * _m.sin(slat_r) +
                  _m.cos(lat_r) * _m.cos(slat_r) * _m.cos(dlon_r))
        return cos_a > 0


    def set_data(self, solar: dict):
        try:
            self._sfi = float(str(solar.get("sfi", 100)).replace("—", "100") or "100")
            self._ssn = float(str(solar.get("ssn",  50)).replace("—",  "50") or "50")
            self._k   = float(str(solar.get("k_index", 2)).replace("—", "2")  or "2")
        except (ValueError, TypeError):
            pass
        self._recalc()

    def _recalc(self):
        qth_lat = self._cfg.qth_lat if self._cfg else 52.0
        qth_lon = self._cfg.qth_lon if self._cfg else 5.0
        day_auto = getattr(self._cfg, "band_day_auto", True) if self._cfg else True
        if day_auto:
            self._day = self._is_day_at_qth(qth_lat, qth_lon)
        mode    = self._cfg.mode    if self._cfg else "SSB"
        power   = self._cfg.power   if self._cfg else "100W"
        antenna = getattr(self._cfg, "antenna", "Dipole ~2dBi") if self._cfg else "Dipole ~2dBi"
        snr = (_MODE_DB.get(mode, 0) + _POWER_DB.get(power, 0) + _ANT_DB.get(antenna, 0))
        lat = self._cfg.qth_lat if self._cfg else 52.0
        band_pct, muf, luf = _calc_propagation_v4(
            self._sfi, self._ssn, self._k, lat, snr, self._day)
        self._chart.set_data(band_pct)
        self._muf_lbl.setText(f"MUF: {muf} MHz")
        self._luf_lbl.setText(f"LUF: {luf} MHz")
        dn = "Dag" if self._day else "Nacht"
        self._snr_lbl.setText(f"{snr:+d} dB  ·  {dn}")


# ── BandCondWidget ────────────────────────────────────────────────────────────

_BAND_INFO = {
    "160m": ("1.8–2.0 MHz — Nachtsband",
             "Werkt 's nachts via F2-laag. Overdag sterk geabsorbeerd.\n"
             "Goed voor regionale DX bij laag K-index."),
    "80m":  ("3.5–4.0 MHz — Avond/nacht",
             "Nachtsband, ook vroege ochtend. Skip ~200-2000 km.\nGevoelig voor K-index."),
    "60m":  ("5 MHz — Noodband",
             "Beperkte banden per regio. Dag/nacht bruikbaar bij gemiddelde SFI."),
    "40m":  ("7 MHz — Dagelijks betrouwbaar",
             "Beste dag-DX band bij lage SFI. Nachts lange skip. MUF ±10-14 MHz."),
    "30m":  ("10 MHz — WARC-band",
             "CW/digi only. Bijna altijd open. Overdag regionaal, 's nachts DX."),
    "20m":  ("14 MHz — Hoofd-DX band",
             "Meest betrouwbare DX-band. Open bij SFI>80.\nDag: F2-propagatie wereldwijd."),
    "17m":  ("18 MHz — WARC DX-band",
             "Uitstekend voor DX bij hoge SFI.\nGevoeliger voor storm dan 20m."),
    "15m":  ("21 MHz — Zonnecyclus band",
             "Open bij hoge SFI (>100).\nBeste propagatie rond middaguur lokaal."),
    "12m":  ("24 MHz — WARC hoge band",
             "Vereist SFI>110.\nTrans-equatoriaal en F2 bij zonnemaxima."),
    "10m":  ("28–30 MHz — Ionosfeer afhankelijk",
             "Gesloten bij laag SFI. Spectaculair open bij SFI>150.\nEs-opens mogelijk."),
    "6m":   ("50 MHz — Magic band",
             "Normaal gesloten via ionosfeer.\nSporadisch-E (mei-aug) geeft verrassende DX."),
}


def _pct_to_cond(pct: int) -> tuple[str, str]:
    if pct >= 60: return "Goed",     "#4CAF50"
    if pct >= 30: return "Matig",    "#FFC107"
    if pct >= 1:  return "Slecht",   "#F44336"
    return               "Gesloten", TEXT_DIM


class BandCondWidget(QWidget):
    """Dag/nacht bandcondities — v4 stijl met propagatiemodel per band."""

    def __init__(self, cfg=None, parent=None):
        super().__init__(parent)
        self._cfg   = cfg
        self._solar: dict = {}
        self._day_lbls: dict[str, QLabel] = {}
        self._ngt_lbls: dict[str, QLabel] = {}
        self._build_ui()

    def set_cfg(self, cfg):
        self._cfg = cfg
        self._recalc()

    def _build_ui(self):
        grid = QGridLayout(self)
        grid.setContentsMargins(8, 6, 8, 4)
        grid.setSpacing(2)

        f8b = QFont("Segoe UI", 8); f8b.setBold(True)

        for col, txt in enumerate(["Band", "Dag", "Nacht"]):
            lbl = QLabel(txt)
            lbl.setFont(f8b)
            lbl.setStyleSheet(f"color: {ACCENT};")
            lbl.setAlignment(Qt.AlignCenter if col > 0 else Qt.AlignLeft)
            grid.addWidget(lbl, 0, col)

        for row, (bname, _) in enumerate(_BANDS_HF, start=1):
            name_lbl = QLabel(bname)
            name_lbl.setFont(f8b)
            name_lbl.setStyleSheet(
                f"color: {_BAND_COLORS_HF.get(bname, TEXT_DIM)};")
            if bname in _BAND_INFO:
                title, body = _BAND_INFO[bname]
                name_lbl.setToolTip(
                    f"<b>{title}</b><br>{body.replace(chr(10), '<br>')}")
            grid.addWidget(name_lbl, row, 0)

            day_lbl = QLabel("—")
            day_lbl.setFont(f8b)
            day_lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(day_lbl, row, 1)
            self._day_lbls[bname] = day_lbl

            ngt_lbl = QLabel("—")
            ngt_lbl.setFont(f8b)
            ngt_lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(ngt_lbl, row, 2)
            self._ngt_lbls[bname] = ngt_lbl

        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)

    def set_data(self, solar: dict):
        self._solar = solar
        self._recalc()

    def _recalc(self):
        data = self._solar
        try:
            sfi = float(str(data.get("sfi", "90")).replace("—", "90") or "90")
            ssn = float(str(data.get("ssn", "50")).replace("—", "50") or "50")
            k   = float(str(data.get("k_index", "2")).replace("—", "2")  or "2")
        except (ValueError, TypeError):
            sfi, ssn, k = 90.0, 50.0, 2.0

        snr     = 0
        qth_lat = 52.0
        if self._cfg:
            snr     = (_MODE_DB.get(self._cfg.mode,    0) +
                       _POWER_DB.get(self._cfg.power,  0) +
                       _ANT_DB.get(self._cfg.antenna,  0))
            qth_lat = self._cfg.qth_lat

        bpd, _, _ = _calc_propagation_v4(sfi, ssn, k, qth_lat, snr, True)
        bpn, _, _ = _calc_propagation_v4(sfi, ssn, k, qth_lat, snr, False)
        pct_day   = {n: p for n, _, p in bpd}
        pct_ngt   = {n: p for n, _, p in bpn}

        for bname, _ in _BANDS_HF:
            dt, dc = _pct_to_cond(pct_day.get(bname, 0))
            nt, nc = _pct_to_cond(pct_ngt.get(bname, 0))
            if bname in self._day_lbls:
                self._day_lbls[bname].setText(dt)
                self._day_lbls[bname].setStyleSheet(
                    f"color: {dc}; font-weight: bold; font-size: 8pt;")
            if bname in self._ngt_lbls:
                self._ngt_lbls[bname].setText(nt)
                self._ngt_lbls[bname].setStyleSheet(
                    f"color: {nc}; font-weight: bold; font-size: 8pt;")


# ── StormFcWidget ─────────────────────────────────────────────────────────────

class StormFcWidget(QWidget):
    """3-daagse NOAA stormprognose."""

    _LEVELS = [
        ("Actief",    "active"),
        ("G1 Minor",  "minor"),
        ("G2 Moder.", "moderate"),
        ("G3 Erg",    "severe"),
        ("G4+ Extr.", "extreme"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        grid = QGridLayout(self)
        grid.setContentsMargins(6, 4, 6, 4)
        grid.setSpacing(3)

        f7  = QFont("Segoe UI", 7)
        f7b = QFont("Segoe UI", 7); f7b.setBold(True)

        for col, txt in enumerate(["", "Dag 1", "Dag 2", "Dag 3"]):
            lbl = QLabel(txt)
            lbl.setFont(f7b)
            lbl.setStyleSheet(f"color: {TEXT_DIM};")
            lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, 0, col)

        self._cells: dict[tuple, QLabel] = {}
        for row, (name, key) in enumerate(self._LEVELS, start=1):
            lbl = QLabel(name)
            lbl.setFont(f7)
            lbl.setStyleSheet(f"color: {TEXT_DIM};")
            grid.addWidget(lbl, row, 0)
            for day in range(3):
                cell = QLabel("—")
                cell.setFont(f7b)
                cell.setAlignment(Qt.AlignCenter)
                grid.addWidget(cell, row, day + 1)
                self._cells[(key, day)] = cell

    def set_data(self, storm: dict):
        # _LEVELS = [(label, key)] — gebruik key (index 1) voor dict-opzoeking
        for _label, key in self._LEVELS:
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

def _subsolar_h(offset_h: float) -> tuple[float, float]:
    """Gecorrigeerde zonpositie voor offset_h uur ten opzichte van nu."""
    import datetime as _dt
    now = _dt.datetime.now(_dt.timezone.utc)
    doy  = now.timetuple().tm_yday
    decl = -23.45 * math.cos(math.radians(360 / 365 * (doy + 10)))
    ut   = now.hour + now.minute / 60 + now.second / 3600 + offset_h
    lon  = -(ut - 12) * 15
    lon  = ((lon + 180) % 360) - 180
    return decl, lon


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

    def set_cfg(self, cfg):
        self._cfg = cfg
        self._recalc()
        self.update()

    def set_cfg(self, cfg):
        self._cfg = cfg
        self._recalc()
        self.update()

    def set_data(self, solar: dict):
        self._solar = solar
        self._recalc()
        self.update()

    def _recalc(self):
        import datetime as _dt
        data = self._solar
        try:
            sfi = float(str(data.get("sfi", "90")).replace("—", "90") or "90")
            ssn = float(str(data.get("ssn", "50")).replace("—", "50") or "50")
            k   = float(str(data.get("k_index", "2")).replace("—",  "2") or "2")
        except (ValueError, TypeError):
            sfi, ssn, k = 90.0, 50.0, 2.0

        snr     = 0
        qth_lat = 52.0
        qth_lon = 5.0
        if self._cfg:
            snr     = (_MODE_DB.get(self._cfg.mode,    0) +
                       _POWER_DB.get(self._cfg.power,  0) +
                       _ANT_DB.get(self._cfg.antenna,  0))
            qth_lat = self._cfg.qth_lat
            qth_lon = self._cfg.qth_lon

        now_utc = _dt.datetime.now(_dt.timezone.utc)
        now_loc = _dt.datetime.now()
        # UTC-offset (uren)
        utc_off = round((now_loc.replace(tzinfo=None) -
                         now_utc.replace(tzinfo=None)).total_seconds() / 3600)
        self._now_h   = now_loc.hour
        self._utc_off = utc_off

        lat_r = math.radians(qth_lat)
        # Huidige zonpositie
        sun_lat, sun_lon = _subsolar_h(0)
        sun_lat_r = math.radians(sun_lat)

        self._grid = []
        for bname, _ in _BANDS_HF:
            row = []
            for loc_h in range(24):
                utc_h    = (loc_h - utc_off) % 24
                off_h    = utc_h - now_utc.hour
                # Corrigeer zonlongitude voor dit uur (zon beweegt 15°/uur)
                sl_h     = sun_lon - off_h * 15
                sl_h     = ((sl_h + 180) % 360) - 180
                dlon_r   = math.radians(qth_lon - sl_h)
                cos_ang  = (math.sin(lat_r) * math.sin(sun_lat_r) +
                            math.cos(lat_r) * math.cos(sun_lat_r) * math.cos(dlon_r))
                is_day   = cos_ang > 0

                bp, _, _ = _calc_propagation_v4(sfi, ssn, k, qth_lat, snr, is_day)
                pct      = max(0, {n: p for n, _, p in bp}.get(bname, 0))
                row.append(pct)
            self._grid.append(row)

    def paintEvent(self, event):
        p = QPainter(self)
        W, H = self.width(), self.height()
        p.fillRect(0, 0, W, H, QColor(BG_PANEL))

        if not self._grid:
            p.setPen(QColor(TEXT_DIM))
            p.setFont(QFont("Segoe UI", 9))
            p.drawText(0, 0, W, H, Qt.AlignCenter, "Wacht op solar data…")
            return

        N_H = 24
        N_B = len(_BANDS_HF)
        PL, PR, PT, PB = 40, 4, 16, 4
        cell_w = max(1, (W - PL - PR) // N_H)
        cell_h = max(1, (H - PT - PB) // N_B)

        f7 = QFont("Segoe UI", 7)
        p.setFont(f7)

        # Uur-labels (elke 3 uur, lokale tijd)
        p.setPen(QColor(TEXT_DIM))
        for h in range(0, N_H, 3):
            lx = PL + h * cell_w + cell_w // 2
            p.drawText(lx - 8, 0, 16, PT - 2, Qt.AlignCenter, f"{h:02d}")

        # Grid: banden × uren
        for bi, (bname, _) in enumerate(_BANDS_HF):
            cy = PT + bi * cell_h
            # Bandnaam in bandkleur
            p.setPen(QColor(_BAND_COLORS_HF.get(bname, TEXT_DIM)))
            p.drawText(0, cy, PL - 3, cell_h,
                       Qt.AlignRight | Qt.AlignVCenter, bname)

            for h in range(N_H):
                pct = self._grid[bi][h]
                if   pct >= 60: fill = QColor("#2E7D32")
                elif pct >= 30: fill = QColor("#F9A825")
                elif pct >= 1:  fill = QColor("#B71C1C")
                else:           fill = QColor("#1A1C1F")
                cx = PL + h * cell_w
                p.fillRect(cx, cy, cell_w - 1, cell_h - 1, fill)

        # Huidig uur — amber omkadering
        lx = PL + self._now_h * cell_w
        p.setPen(QPen(QColor(ACCENT), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRect(lx, PT, cell_w - 1, N_B * cell_h - 1)

        # Sla layout op voor tooltip
        self._layout_info = dict(pl=PL, pt=PT, cw=cell_w, ch=cell_h,
                                 nb=N_B, nh=N_H)

    def mouseMoveEvent(self, event):
        lay = self._layout_info
        if not lay or not self._grid:
            return
        col = (event.position().toPoint().x() - lay["pl"]) // lay["cw"]
        row = (event.position().toPoint().y() - lay["pt"]) // lay["ch"]
        if 0 <= col < lay["nh"] and 0 <= row < lay["nb"]:
            bname, bfreq = _BANDS_HF[row]
            pct  = self._grid[row][col]
            kwal = ("Goed" if pct >= 60 else "Matig" if pct >= 30
                    else "Slecht" if pct >= 1 else "Gesloten")
            tip  = (f"{bname}  —  {col:02d}:00–{(col+1)%24:02d}:00 lokaal\n"
                    f"Betrouwbaarheid: {pct}%  ({kwal})\n"
                    f"Frequentie: {bfreq:.3f} MHz\n"
                    f"Modus: {_BAND_MODES_TBL.get(bname, '—')}\n"
                    f"FT8: {_BAND_FT8_FREQ.get(bname, '—')} MHz")
            from PySide6.QtWidgets import QToolTip
            QToolTip.showText(event.globalPosition().toPoint(), tip, self)
        else:
            from PySide6.QtWidgets import QToolTip
            QToolTip.hideText()


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


class SolarHistChart(QWidget):
    """SFI + Kp historiek — leest uit HAMIOS_history.csv."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hours = 24.0
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setMinimumHeight(80)
        t = QTimer(self)
        t.timeout.connect(self.update)
        t.start(60_000)

    def set_hours(self, h: float):
        self._hours = h
        self.update()

    def set_data(self, solar: dict):
        self.update()   # data wordt beheerd door mainwindow._on_solar_for_history

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()
        p.fillRect(0, 0, W, H, QColor(BG_SURFACE))

        rows = _hist_csv.get_range(self._hours)
        data = _rows_to_ha(rows, self._hours)

        PL, PR, PT, PB = 30, 4, 4, 12
        gW = W - PL - PR
        gH = H - PT - PB
        f6 = QFont("Segoe UI", 6)
        p.setFont(f6)

        if not data:
            p.setPen(QColor(TEXT_DIM))
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(0, 0, W, H, Qt.AlignCenter,
                       "Geen historiekdata — vult na eerste refresh")
            return

        def sfi_y(v):
            return PT + int(gH * (1.0 - (max(50, min(300, v)) - 50) / 250))
        def ha_x(ha):
            return PL + int(gW * (1.0 - ha / self._hours))

        for sfi_r in (100, 150, 200):
            yr = sfi_y(sfi_r)
            p.setPen(QPen(QColor(BORDER), 1, Qt.DashLine))
            p.drawLine(PL, yr, W - PR, yr)
            p.setPen(QColor(TEXT_DIM))
            p.drawText(0, yr - 5, PL - 2, 10,
                       Qt.AlignRight | Qt.AlignVCenter, str(sfi_r))

        p.setPen(Qt.NoPen)
        for ha, ts, bp, sol in data:
            k = sol.get("k_index", 0)
            if k >= 5:
                x = ha_x(ha)
                p.fillRect(x - 1, PT, 3, gH,
                           QColor(200, 50, 50, int(min(100, k * 15))))

        prev = None
        for ha, ts, bp, sol in reversed(data):   # oudste → nieuwste
            sfi = sol.get("sfi", 0)
            x, y = ha_x(ha), sfi_y(sfi)
            if prev:
                p.setPen(QPen(QColor("#FFA726"), 1.5))
                p.drawLine(prev[0], prev[1], x, y)
            prev = (x, y)

        p.setPen(QColor(TEXT_DIM))
        p.setFont(f6)
        lbl = f"{int(self._hours)}h" if self._hours < 48 else f"{int(self._hours/24)}d"
        p.drawText(PL, H - PB + 2, 24, PB, Qt.AlignLeft, lbl)
        p.drawText(W - PR - 24, H - PB + 2, 24, PB, Qt.AlignRight, "nu")
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

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hours        = 24.0
        self._visible      = set(self.SHOW)   # geselecteerde banden
        self._legend_rects: list[tuple[str, tuple]] = []   # [(band, (x,y,w,h))]
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setMinimumHeight(110)
        self.setCursor(Qt.PointingHandCursor)
        t = QTimer(self)
        t.timeout.connect(self.update)
        t.start(60_000)

    def mousePressEvent(self, event):
        """Klik op legenda-item → band aan/uit zetten."""
        px, py = event.position().x(), event.position().y()
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

        rows = _hist_csv.get_range(self._hours)
        data = _rows_to_ha(rows, self._hours)

        PB_total = self._TIME_H + self._LEG_H   # ruimte onder grafiek
        PL, PR, PT, PB = 30, 4, 4, PB_total
        gW, gH = W - PL - PR, H - PT - PB

        if not data:
            p.setPen(QColor(TEXT_DIM))
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(0, 0, W, H - PB_total, Qt.AlignCenter,
                       "Geen historiekdata — vult na eerste refresh")
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

        # Lijnen per band (alleen zichtbare banden)
        for band in self.SHOW:
            if band not in self._visible:
                continue
            prev = None
            for ha, ts, bp, sol in reversed(data):
                pct = bp.get(band, 0)
                x, y = ha_x(ha), pct_y(pct)
                if prev:
                    p.setPen(QPen(QColor(self.COLORS[band]), 1.2))
                    p.drawLine(prev[0], prev[1], x, y)
                prev = (x, y)

        # Tijdlabels direct onder grafiek
        y_time = H - PB_total + 2
        p.setPen(QColor(TEXT_DIM))
        p.setFont(f6)
        lbl = f"{int(self._hours)}h" if self._hours < 48 else f"{int(self._hours/24)}d"
        p.drawText(PL, y_time, 24, 10, Qt.AlignLeft, lbl)
        p.drawText(W - PR - 20, y_time, 20, 10, Qt.AlignRight, "nu")

        # Legenda onder tijdlabels
        self._draw_legend(p, W, H)

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
        self._qrn_level = 0   # vorige QRN-niveau (0=geen, 1=laag, 2=matig, 3=hoog, 4=zwaar)
        self._build_ui()
        lightning_layer.status_signal.connect(self._on_status)
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
        row.addWidget(QLabel("Status:", font=f8,
                              styleSheet=f"color:{TEXT_DIM};"))
        self._status_lbl = QLabel("Verbinden…")
        self._status_lbl.setFont(f9b)
        self._status_lbl.setStyleSheet(f"color:{TEXT_DIM};")
        row.addWidget(self._status_lbl)
        row.addStretch()
        layout.addLayout(row)

        # Teller
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Inslagen:", font=f8,
                               styleSheet=f"color:{TEXT_DIM};"))
        self._count_lbl = QLabel("0")
        self._count_lbl.setFont(f9b)
        self._count_lbl.setStyleSheet(f"color:{TEXT_H1};")
        row2.addWidget(self._count_lbl)
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

    def _on_status(self, status: str):
        msgs = {
            "live":     ("Live",                   "#4CAF50"),
            "disc":     ("Verbroken",              "#EF5350"),
            "no_lib":   ("Geen websocket-client",  "#FFA726"),
            "disabled": ("Uitgeschakeld",          TEXT_DIM),
        }
        txt, clr = msgs.get(status, ("…", TEXT_DIM))
        self._status_lbl.setText(txt)
        self._status_lbl.setStyleSheet(
            f"color:{clr}; font-weight:bold; font-size:9pt;")
        if status == "disabled":
            self._count_lbl.setText("—")

    # QRN wordt berekend over inslagen binnen deze straal van het QTH
    _QRN_RADIUS_KM = 2000

    def _update_count(self):
        import time, math
        now = time.monotonic()
        with self._layer._lock:
            strikes = list(self._layer._strikes)

        # Filter naar inslagen nabij QTH (QRN is lokaal fenomeen)
        cfg = self._cfg
        if cfg:
            from .layers import MAP_W, MAP_H
            qlat = math.radians(cfg.qth_lat)
            qlon = math.radians(cfg.qth_lon)
            R    = 6371.0
            local = []
            for x_px, y_px, t in strikes:
                slat = math.radians(90 - y_px / MAP_H * 180)
                slon = math.radians(x_px / MAP_W * 360 - 180)
                dlat = slat - qlat; dlon = slon - qlon
                a  = math.sin(dlat/2)**2 + math.cos(qlat)*math.cos(slat)*math.sin(dlon/2)**2
                km = 2 * R * math.asin(min(1.0, math.sqrt(a)))
                if km <= self._QRN_RADIUS_KM:
                    local.append((x_px, y_px, t))
            n = len(local)
            # Gebruik lokale lijst ook voor dichtste inslag
            strikes_for_near = local
        else:
            n = len(strikes)
            strikes_for_near = strikes
        self._count_lbl.setText(str(n))

        # QRN-niveau + advies
        if n == 0:
            lvl, qrn, qrn_clr = 0, "Geen activiteit",                         TEXT_DIM
        elif n < 10:
            lvl, qrn, qrn_clr = 1, "Lage activiteit — weinig QRN verwacht",   "#4CAF50"
        elif n < 50:
            lvl, qrn, qrn_clr = 2, "Matige activiteit — enige QRN op LF/MF/160m", "#FFA726"
        elif n < 200:
            lvl, qrn, qrn_clr = 3, "Hoge activiteit — QRN op 160m/80m/40m",  "#FF7043"
        else:
            lvl, qrn, qrn_clr = 4, "Zware storm — sterke QRN op alle lage banden!", "#EF5350"
        radius_lbl = f" ({n} inslagen ≤{self._QRN_RADIUS_KM//1000}Mm)" if n > 0 else ""
        self._qrn_lbl.setText(f"QRN: {qrn}{radius_lbl}")
        self._qrn_lbl.setStyleSheet(f"color:{qrn_clr}; font-size:8pt;")

        # Stuur naar meldingen-paneel als niveau stijgt
        if lvl > self._qrn_level and lvl >= 2:
            self.qrn_alert.emit("⚡", f"QRN: {qrn}", qrn_clr)
        self._qrn_level = lvl

        # Dichtstbijzijnde inslag (gebruik volledige set voor absolute minimum)
        if cfg and strikes:
            try:
                qlat = math.radians(cfg.qth_lat)
                qlon = math.radians(cfg.qth_lon)
                R    = 6371.0
                from .layers import MAP_W, MAP_H
                min_km = None
                for x_px, y_px, _ in strikes:
                    slat = math.radians(90 - y_px / MAP_H * 180)
                    slon = math.radians(x_px / MAP_W * 360 - 180)
                    dlat = slat - qlat; dlon = slon - qlon
                    a  = (math.sin(dlat/2)**2 +
                          math.cos(qlat)*math.cos(slat)*math.sin(dlon/2)**2)
                    km = 2 * R * math.asin(min(1.0, math.sqrt(a)))
                    if min_km is None or km < min_km:
                        min_km = km
                if min_km is not None:
                    self._near_lbl.setText(f"Dichtste inslag: {min_km:.0f} km")
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
        self._count_lbl = QLabel("0 meldingen")
        self._count_lbl.setFont(f8)
        self._count_lbl.setStyleSheet(f"color: {TEXT_DIM};")
        top.addWidget(self._count_lbl)
        top.addStretch()
        btn_wis = QPushButton("Wis alles")
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
        pass

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
                prev_k = float(str(self._solar_data.get("k_index", "0")).replace("—","0") or "0")
                if k != prev_k:
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
        # Alleen _cleared resetten als er nieuw satelliet is bijgekomen
        new_entries = set(names) - prev
        if new_entries:
            self._cleared = False
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
            items.append((k_clr, "🧲", f"K-index: {k:.0f}  ·  X-straling: {xray}", "", ""))
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
                    f"K-STORM  K={k:.0f} ≥ drempel {threshold}",
                    "Geomagnetische storm — poolroutes verstoord", ""))

        # ── X-flare alert ─────────────────────────────────────────────────────
        if not cfg or getattr(cfg, "xflare_alert_en", True):
            xray = str(data.get("xray", ""))
            if xray and xray[0].upper() in ("M", "X"):
                clr = "#EF5350" if xray[0].upper() == "X" else "#FFA726"
                items.append((clr, "☢", f"Zonnevlam {xray}", "", ""))

        # ── Satellieten in QTH-zone ────────────────────────────────────────────
        for entry in self._sat_zone:
            items.append(("#4CAF50", "🛰", f"{entry} boven QTH", "", ""))

        # ── Externe meldingen (analyse, enz.) uit _alert_log ──────────────────
        import time as _t
        now = _t.time()
        for ts, icon, text, color, detail in self._alert_log:
            age  = now - ts
            mins = int(age / 60)
            secs = int(age % 60)
            if mins > 0:
                tstr = f"  {mins}m geleden"
            else:
                tstr = f"  {secs}s geleden"
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
            lbl = QLabel("Geen actieve meldingen")
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
        self._count_lbl.setText(f"{n} melding{'en' if n != 1 else ''}")


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
        self._dx_font_sz: int  = getattr(cfg, "dx_font_size", 8) if cfg else 8
        self._build_ui()
        # Herstel opgeslagen staat
        if cfg:
            self._own_cb.setChecked(getattr(cfg, "dx_own_continent", False))
            if getattr(cfg, "dx_heatmap", False):
                self._heatmap_btn.setChecked(True)

    def set_cfg(self, cfg):
        self._cfg = cfg
        self._own_cb.setChecked(getattr(cfg, "dx_own_continent", False))
        font_size = getattr(cfg, "dx_font_size", 8)
        self._set_font_size(font_size)
        self._apply_filter()

    def set_font_size(self, size: int):
        self._set_font_size(size)

    def _set_font_size(self, size: int):
        self._dx_font_sz = max(6, size)
        fmono = QFont("Consolas", self._dx_font_sz)
        self._table.setFont(fmono)
        self._table.verticalHeader().setDefaultSectionSize(max(14, self._dx_font_sz + 6))
        self._update_table()   # herteken met nieuwe fontgrootte

    def _build_ui(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(4, 4, 4, 4)
        v.setSpacing(3)

        f8 = QFont("Segoe UI", 8)

        # ── Bedieningsrij ────────────────────────────────────────────────────
        ctrl = QHBoxLayout()
        ctrl.setSpacing(6)
        self._own_cb = QCheckBox("Eigen continent")
        self._own_cb.setFont(f8)
        self._own_cb.toggled.connect(self._apply_filter)
        ctrl.addWidget(self._own_cb)

        self._heatmap_btn = QPushButton("Heatmap")
        self._heatmap_btn.setFont(f8)
        self._heatmap_btn.setCheckable(True)
        self._heatmap_btn.toggled.connect(self._toggle_heatmap)
        ctrl.addWidget(self._heatmap_btn)

        ctrl.addStretch()
        self._status_lbl = QLabel("Laden…")
        self._status_lbl.setFont(f8)
        self._status_lbl.setStyleSheet(f"color: {TEXT_DIM};")
        ctrl.addWidget(self._status_lbl)
        v.addLayout(ctrl)

        # ── Stacked: tabel / heatmap ──────────────────────────────────────
        self._stack = QStackedWidget()

        # Tabel
        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels(
            ["UTC", "Band", "MHz", "DX", "Spotter", "Comment"])
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(False)
        fmono = QFont("Consolas", 8)
        self._table.setFont(fmono)
        hdr = self._table.horizontalHeader()
        hdr.setFont(QFont("Segoe UI", 7))
        for i, w in enumerate([38, 38, 58, 80, 74, -1]):
            if w > 0:
                hdr.setSectionResizeMode(i, QHeaderView.Fixed)
                self._table.setColumnWidth(i, w)
            else:
                hdr.setSectionResizeMode(i, QHeaderView.Stretch)
        self._table.verticalHeader().setDefaultSectionSize(16)
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
        filt  = " (eigen cont.)" if self._own_cb.isChecked() else ""
        self._status_lbl.setText(
            f"{n}/{total} spots{filt}  {ts}" if total else f"Geen spots  {ts}")

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


class _PulseDot(QLabel):
    """Pulserende gele stip (●) — fadeert in en uit via QTimer."""
    _ALPHAS = [255, 200, 130, 70, 40, 70, 130, 200]

    def __init__(self, parent=None):
        super().__init__("●", parent)
        self.setFont(QFont("Segoe UI", 8))
        self.setAlignment(Qt.AlignTop | Qt.AlignRight)
        self.setFixedWidth(12)
        self._phase = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(150)
        self._tick()

    def _tick(self):
        a = self._ALPHAS[self._phase % len(self._ALPHAS)]
        self.setStyleSheet(
            f"color: rgba(255,204,0,{a}); background: transparent;")
        self._phase += 1


class PropAdvWidget(QWidget):
    """Propagatie-advies in kaartjes — v4 stijl."""

    COLS   = 3
    CARD_H = 72

    analysis_changed = Signal(list)

    def __init__(self, cfg=None, parent=None):
        super().__init__(parent)
        self._cfg    = cfg
        self._solar: dict = {}
        self._hashes: dict = {}
        self._dots:   list = []    # refs naar pulserende stippen bewaren
        v = QVBoxLayout(self)
        v.setContentsMargins(4, 4, 4, 4)
        v.setSpacing(4)

        self._cards_widget = QWidget()
        self._cards_widget.setStyleSheet(f"background: {BG_PANEL};")
        self._grid = QGridLayout(self._cards_widget)
        self._grid.setSpacing(4)
        v.addWidget(self._cards_widget)
        v.addStretch()

    def set_cfg(self, cfg):
        self._cfg = cfg

    def set_data(self, solar: dict):
        self._solar = solar
        self._rebuild()

    # ── Kaarten opbouwen ─────────────────────────────────────────────────────
    def _rebuild(self):
        tips = self._build_tips()
        # Stop en wis oude pulserende stippen
        for dot in self._dots:
            dot._timer.stop()
        self._dots.clear()
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        new_hashes: dict = {}
        changed_tips: list = []
        for i, (icon, text, color) in enumerate(tips):
            col     = i % self.COLS
            row     = i // self.COLS
            changed = (self._hashes.get(i) != hash((icon, text)))
            if changed and self._hashes:
                changed_tips.append((icon, text, color))
            card, dot = self._make_card(icon, text, color, changed)
            if dot:
                self._dots.append(dot)
            self._grid.addWidget(card, row, col)
            new_hashes[i] = hash((icon, text))
        for c in range(self.COLS):
            self._grid.setColumnStretch(c, 1)
        self._hashes = new_hashes
        if changed_tips:
            self.analysis_changed.emit(changed_tips)

    def _make_card(self, icon: str, text: str,
                   color: str, changed: bool):
        """Geeft (QFrame, _PulseDot|None) terug."""
        frame = QFrame()
        frame.setMinimumHeight(self.CARD_H)
        frame.setStyleSheet(
            f"QFrame {{ background: {BG_SURFACE}; border-radius: 2px; }}")
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(6, 4, 6, 4)
        fl.setSpacing(0)

        top = QHBoxLayout()
        top.setSpacing(2)
        lbl = QLabel(f"{icon}  {text}")
        f8  = QFont("Segoe UI", 8)
        lbl.setFont(f8)
        lbl.setStyleSheet(f"color: {color}; background: transparent;")
        lbl.setWordWrap(True)
        top.addWidget(lbl, 1)

        dot_ref = None
        if changed:
            dot = _PulseDot()    # pulserende stip met eigen timer
            dot_ref = dot
            top.addWidget(dot)

        fl.addLayout(top)
        fl.addStretch()
        return frame, dot_ref

    # ── Advies genereren ──────────────────────────────────────────────────────
    def _build_tips(self) -> list[tuple[str, str, str]]:
        data = self._solar
        try:
            sfi     = float(str(data.get("sfi",     "90")).replace("—", "90") or "90")
            ssn     = float(str(data.get("ssn",     "50")).replace("—", "50") or "50")
            k_index = float(str(data.get("k_index", "2" )).replace("—", "2")  or "2")
            a_index = float(str(data.get("a_index", "5" )).replace("—", "5")  or "5")
        except (ValueError, TypeError):
            sfi, ssn, k_index, a_index = 90.0, 50.0, 2.0, 5.0

        xray   = str(data.get("xray",     ""))
        sw_spd = str(data.get("sw_speed", "—"))
        sw_bz  = str(data.get("sw_bz",    "—"))
        sw_den = str(data.get("sw_density","—"))

        import datetime as _dt
        now_utc = _dt.datetime.now(_dt.timezone.utc)
        utc_h   = now_utc.hour
        now_loc = _dt.datetime.now()
        lok_h   = now_loc.hour
        month   = now_loc.month
        is_day  = 6 <= utc_h < 20

        s_i, ss_i = int(sfi), int(ssn)
        k_i, a_i  = int(k_index), int(a_index)

        rels     = _reliability(sfi, k_index, is_day)
        band_pct = {_BANDS[i][0]: int(rels[i] * 100) for i in range(len(_BANDS))}
        hf_open  = sorted(
            [(n, p) for n, p in band_pct.items() if p > 0],
            key=lambda x: -x[1])

        tips: list[tuple[str, str, str]] = []

        # ── 1. Beste banden ──────────────────────────────────────────────────
        if hf_open:
            best = hf_open[:5]
            bstr = "  ·  ".join(f"{n} {p}%" for n, p in best)
            extra = f"  (+{len(hf_open)-5} meer)" if len(hf_open) > 5 else ""
            tips.append(("📡", f"Beste banden: {bstr}{extra}", "#4CAF50"))
        else:
            tips.append(("📡", "Geen banden significant open", TEXT_DIM))

        # ── 2. Geomagnetische condities ──────────────────────────────────────
        a_kwal = ("Rustig" if a_index < 10 else
                  "Onrustig" if a_index < 30 else
                  "Storm" if a_index < 100 else "Zware storm")
        if k_index >= 7:
            tips.append(("🚨",
                f"ZWARE STORM K={k_i} A={a_i} — HF grotendeels onbruikbaar. "
                f"Poolroutes zwaar verstoord.", "#F44336"))
        elif k_index >= 5:
            tips.append(("⚠️",
                f"Geomagnetische storm K={k_i} A={a_i} ({a_kwal}) — "
                f"40m/80m meest betrouwbaar. Polaire paden verstoord.", "#F44336"))
        elif k_index >= 3:
            tips.append(("⚡",
                f"Verhoogde activiteit K={k_i} A={a_i} ({a_kwal}) — "
                f"Lichte verstoringen op hogere banden mogelijk.", "#FFC107"))
        else:
            tips.append(("✅",
                f"Geomagnetisch rustig K={k_i} A={a_i} — "
                f"Optimale condities voor alle banden.", "#4CAF50"))

        # ── 3. Zonactiviteit ─────────────────────────────────────────────────
        if sfi >= 200:
            tips.append(("🌟",
                f"Uitzonderlijke activiteit SFI={s_i} SSN={ss_i} — Zonnecyclus maximum. "
                f"10m/12m/15m open wereldwijd. Es-versterking en TEP mogelijk.", ACCENT))
        elif sfi >= 150:
            tips.append(("☀️",
                f"Hoge activiteit SFI={s_i} SSN={ss_i} — Uitstekend voor 10m–17m DX. "
                f"F2 sterk, MUF hoog, grote skips mogelijk.", ACCENT))
        elif sfi >= 100:
            tips.append(("🌤",
                f"Goede activiteit SFI={s_i} SSN={ss_i} — 20m en 17m primaire DX-banden. "
                f"15m overdag open. Betrouwbare F2-propagatie.", ACCENT))
        elif sfi >= 80:
            tips.append(("🌥",
                f"Matige activiteit SFI={s_i} SSN={ss_i} — 20m/40m meest betrouwbaar. "
                f"Hoge banden onzeker. 80m goed voor regionaal.", TEXT_BODY))
        else:
            tips.append(("🌧",
                f"Lage activiteit SFI={s_i} SSN={ss_i} — 40m en 80m beste kansen. "
                f"Banden ≥15m grotendeels gesloten. 160m voor nacht-DX.", TEXT_DIM))

        # ── 4. Solarwind en Bz ───────────────────────────────────────────────
        try:
            spd = float(sw_spd)
            bz  = float(sw_bz)
            spd_s, bz_s = str(int(spd)), f"{bz:+.1f}"
            if spd > 700 or bz <= -20:
                tips.append(("🌪",
                    f"Stormachtige solarwind {spd_s} km/s  Bz={bz_s} nT — "
                    f"Sterke geomagnetische storing verwacht.", "#F44336"))
            elif spd > 500 or bz <= -10:
                tips.append(("💨",
                    f"Verhoogde solarwind {spd_s} km/s  Bz={bz_s} nT — "
                    f"Lichte storing mogelijk op hoge banden.", "#FFC107"))
            elif bz > 5:
                tips.append(("🛡",
                    f"Rustige solarwind {spd_s} km/s  Bz={bz_s} nT — "
                    f"Noordwaartse Bz gunstig voor propagatie.", "#4CAF50"))
            else:
                tips.append(("💫",
                    f"Normale solarwind {spd_s} km/s  Bz={bz_s} nT — "
                    f"Geen bijzonderheden.", TEXT_BODY))
        except (ValueError, TypeError):
            pass

        # ── 5. X-straling / flares ───────────────────────────────────────────
        xclass = xray[:1].upper() if xray else ""
        if xclass == "X":
            tips.append(("☢",
                f"X-flare {xray} — Sterke ionosferische storing. "
                f"HF uitval op dagzijde mogelijk. LUF sterk verhoogd.", "#F44336"))
        elif xclass == "M":
            tips.append(("⚡",
                f"M-flare {xray} — Lichte radio-blackout op dagzijde. "
                f"10m–15m verstoord. Monitor condities.", "#FFC107"))

        # ── 6. Dag/nacht en grijze lijn ──────────────────────────────────────
        h_s = f"{lok_h:02d}"
        if is_day:
            if 6 <= lok_h < 10:
                tips.append(("🌅",
                    f"Ochtend ({h_s}:xx lokaal) — F2 bouwt op. "
                    f"20m wordt snel bruikbaar. Grijze lijn kansen naar Amerika en Azië.",
                    TEXT_BODY))
            elif 10 <= lok_h < 16:
                tips.append(("🌞",
                    f"Middag ({h_s}:xx lokaal) — F2 maximaal. "
                    f"Beste venster voor 15m/17m/20m DX. Trans-Atlantische QSO's goed mogelijk.",
                    TEXT_BODY))
            else:
                tips.append(("🌇",
                    f"Namiddag ({h_s}:xx lokaal) — Grijze lijn nadert. "
                    f"Uitstekend voor DX naar Azië en Pacific. 15m en 17m vaak excellent.",
                    TEXT_BODY))
        else:
            if 22 <= lok_h or lok_h < 2:
                tips.append(("🌃",
                    f"Vroege nacht ({h_s}:xx lokaal) — 40m en 80m open voor regionaal. "
                    f"F2 daalt. LUF stijgt op korte paden.",
                    TEXT_BODY))
            elif 2 <= lok_h < 6:
                tips.append(("🌌",
                    f"Nacht ({h_s}:xx lokaal) — 160m en 80m actief voor trans-Atlantisch DX. "
                    f"40m goed voor Noord-Amerika. FT8 op lage banden voor >5000 km.",
                    TEXT_BODY))
            else:
                tips.append(("🌄",
                    f"Pre-ochtend ({h_s}:xx lokaal) — Grijze lijn nadert. "
                    f"80m/40m DX naar Azië/Pacific. 20m begint te openen naar Amerika.",
                    TEXT_BODY))

        # ── 7. Modus / vermogen advies ───────────────────────────────────────
        if self._cfg and hf_open:
            mode  = self._cfg.mode
            power = self._cfg.power
            ant   = self._cfg.antenna
            snr   = (_MODE_DB.get(mode, 0) + _POWER_DB.get(power, 0) +
                     _ANT_DB.get(ant, 0))
            bn0, bp0 = hf_open[0]   # bn0 = bandnaam, bp0 = percentage
            snr_s = f"{snr:+d}"
            if bp0 < 30 and mode == "SSB":
                tips.append(("🔧",
                    f"Band {bn0} matig ({bp0}%) — Overweeg FT8/CW voor betere kansen "
                    f"(SNR-voordeel {snr_s} dB t.o.v. SSB).", "#FFC107"))
            else:
                tips.append(("🔧",
                    f"{mode} op {bn0} ({bp0}%) met {power} — "
                    f"Effectief SNR {snr_s} dB. {ant}.", TEXT_BODY))

        # ── 8. Absorptie op hoge breedte ─────────────────────────────────────
        if self._cfg:
            lat = abs(self._cfg.qth_lat)
            if lat > 50 and k_index >= 4:
                tips.append(("🧲",
                    f"Auroraire absorptie (K={k_i}, QTH {lat:.0f}°) — "
                    f"Trans-polaire paden (EU→Canada, EU→Japan via pool) sterk gedempt. "
                    f"Gebruik equatoriale routes via 20m/17m.", "#FFC107"))
            elif lat > 45 and k_index >= 3:
                tips.append(("🧲",
                    f"Lichte absorptie mogelijk (K={k_i}, QTH {lat:.0f}°) — "
                    f"Polaire paden sporadisch verstoord. Monitor 40m.", TEXT_BODY))

        # ── 9. Sporadic-E ────────────────────────────────────────────────────
        es_score = 0
        if 5 <= month <= 8:
            es_score = 3 if month in (6, 7) else 2
        elif month in (12, 1):
            es_score = 1
        es_time = (9 <= lok_h < 14) or (17 <= lok_h < 22)
        if es_score >= 2 and es_time:
            tips.append(("⚡",
                f"Sporadic-E kans HOOG (maand {month}, {h_s}:xx) — "
                f"6m/4m/2m kunnen onverwacht openen (700–2500 km). "
                f"Monitor 50.313 MHz (FT8) en 50.150 MHz (SSB).", "#66BB6A"))
        elif es_score >= 2:
            tips.append(("⚡",
                f"Sporadic-E seizoen actief (maand {month}) — "
                f"Kans op 6m opens laag buiten piekuren (09-14u en 17-22u).", TEXT_DIM))

        # ── 10. DX-routes ────────────────────────────────────────────────────
        dx_routes = []
        if is_day:
            if 5 <= utc_h < 10 and sfi >= 100:
                dx_routes.append("EU→JA (20m/17m)")
            if 12 <= utc_h < 18 and sfi >= 80:
                dx_routes.append("EU→W (20m/15m)")
            if 8 <= utc_h < 14 and sfi >= 80:
                dx_routes.append("EU→AF (20m/17m)")
            if 14 <= utc_h < 20 and sfi >= 120:
                dx_routes.append("EU→OC (15m/10m)")
        else:
            if 22 <= utc_h or utc_h < 4:
                dx_routes.append("EU→W (40m/80m)")
            if 2 <= utc_h < 8:
                dx_routes.append("EU→JA (40m grijze lijn)")
        if dx_routes:
            tips.append(("🌍",
                f"DX-routes nu open: {'  ·  '.join(dx_routes)}", "#4FC3F7"))

        # ── 11. Algehele beoordeling ─────────────────────────────────────────
        score = 0
        if sfi >= 150: score += 3
        elif sfi >= 100: score += 2
        elif sfi >= 80: score += 1
        if k_index <= 2: score += 2
        elif k_index <= 4: score += 1
        if hf_open and hf_open[0][1] >= 60: score += 2
        elif hf_open: score += 1
        try:
            if float(sw_bz) < -10: score -= 1
        except (ValueError, TypeError):
            pass
        overall = ("Uitstekend" if score >= 6 else "Goed" if score >= 4
                   else "Matig" if score >= 2 else "Slecht")
        overall_clr = ("#4CAF50" if score >= 6 else "#8BC34A" if score >= 4
                       else "#FFC107" if score >= 2 else "#F44336")
        dn = "dag" if is_day else "nacht"
        lat_s = f"{self._cfg.qth_lat:.1f}" if self._cfg else "?"
        tips.append(("📊",
            f"Algehele beoordeling: {overall}  "
            f"(SFI {s_i} · K {k_i} · {len(hf_open)} banden open)  "
            f"{dn.capitalize()}, QTH {lat_s}°N.", overall_clr))

        return tips
