"""
HAMIOS — Padvoorspelling: "wanneer kan ik daar werken?"

Kans per band voor de komende 24 uur op het pad QTH → doel, met hetzelfde
padmodel als de aanbevelingen (propagation.path_detail: controlepunten op het
pad, het zwakste punt telt). Het doel volgt de kaart: een klik op de kaart,
een aanbeveling of een melding in 'Mijn signaal'. Of typ een locator
(JO21DN) of een roepnaam (land via cty.dat).
"""

from __future__ import annotations

import datetime as _dt

from PySide6.QtCore import QPointF, QRect, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit, QPushButton, QToolTip,
                               QVBoxLayout, QWidget)

from .i18n import tr
from .theme import ACCENT, BG_PANEL, TEXT_DIM

BANDS = ["160m", "80m", "60m", "40m", "30m", "20m", "17m", "15m", "12m", "10m", "6m"]
HOURS = 24
OPEN_PCT = 50


def _cell_colour(pct: int) -> QColor:
    # Zelfde kleuren als 'Bandopeningen 24u'
    if pct >= 60:
        return QColor("#2E7D32")
    if pct >= 30:
        return QColor("#F9A825")
    if pct >= 1:
        return QColor("#B71C1C")
    return QColor("#1A1C1F")


def forecast(qth, target, snr_db: float = 0.0, start: _dt.datetime | None = None,
             engine=None) -> tuple[list, list]:
    """([lokale uurstart], {band: [pct per uur]}) voor het pad qth → target."""
    from .propagation import ENGINE
    eng = engine or ENGINE
    start = start or _dt.datetime.now().replace(minute=0, second=0, microsecond=0)
    hours = [start + _dt.timedelta(hours=h) for h in range(HOURS)]
    grid = {b: [] for b in BANDS}
    for t in hours:
        # midden van het uur, in UTC
        pct = eng.path_band_pct(qth[0], qth[1], target[0], target[1],
                                (t + _dt.timedelta(minutes=30)).astimezone(_dt.timezone.utc),
                                snr_db)
        for b in BANDS:
            grid[b].append(int(pct.get(b, 0)))
    return hours, grid


def best_windows(hours: list, grid: dict, top: int = 3) -> list[tuple]:
    """Beste aaneengesloten open vensters: [(band, begin, eind, max %)], beste eerst."""
    out = []
    for b in BANDS:
        row, i = grid.get(b, []), 0
        while i < len(row):
            if row[i] >= OPEN_PCT:
                j = i
                while j + 1 < len(row) and row[j + 1] >= OPEN_PCT:
                    j += 1
                out.append((b, hours[i], hours[j] + _dt.timedelta(hours=1), max(row[i:j + 1])))
                i = j + 1
            else:
                i += 1
    # Hoogste kans eerst; bij gelijke kans de hoogste band (minder absorptie, meer DX)
    out.sort(key=lambda w: (-w[3], -BANDS.index(w[0]), -(w[2] - w[1]).total_seconds()))
    return out[:top]


def resolve_target(text: str):
    """Locator (4/6 tekens) of roepnaam → (lat, lon, label), of None."""
    from .settings_dialog import locator_to_latlon
    t = (text or "").strip().upper()
    if not t:
        return None
    if len(t) in (4, 6) and t[:2].isalpha() and t[2:4].isdigit():
        pos = locator_to_latlon(t)
        if pos:
            return pos[0], pos[1], t
    from .cty import lookup
    ent = lookup(t)
    if ent is not None:
        return ent.lat, ent.lon, f"{t} ({ent.name})"
    return None


class _Grid(QWidget):
    """Banden × 24 uur, in dezelfde stijl als 'Bandopeningen 24u'."""

    PL, PT = 40, 16

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hours: list = []
        self._grid: dict = {}
        self.setMinimumHeight(140)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_OpaquePaintEvent)

    def set_data(self, hours, grid):
        self._hours, self._grid = hours, grid
        self.update()

    def _geom(self):
        cw = max(1, (self.width() - self.PL - 4) // HOURS)
        ch = max(1, (self.height() - self.PT - 4) // len(BANDS))
        return cw, ch

    def paintEvent(self, _e):
        from .panels5 import _BAND_COLORS_HF
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(BG_PANEL))
        if not self._hours:
            p.setPen(QColor(TEXT_DIM))
            p.drawText(self.rect(), Qt.AlignCenter, tr("pathfc.pick"))
            return
        cw, ch = self._geom()
        p.setFont(QFont("Segoe UI", 7))
        for h, t in enumerate(self._hours):
            if h % 3 == 0:
                p.setPen(QColor(TEXT_DIM))
                p.drawText(QRect(self.PL + h * cw + cw // 2 - 10, 0, 20, self.PT - 3),
                           Qt.AlignCenter, f"{t.hour:02d}")
        for bi, b in enumerate(BANDS):
            y = self.PT + bi * ch
            p.setPen(QColor(_BAND_COLORS_HF.get(b, TEXT_DIM)))
            p.drawText(QRect(0, y, self.PL - 3, ch), Qt.AlignRight | Qt.AlignVCenter, b)
            for h, pct in enumerate(self._grid.get(b, [])):
                p.fillRect(self.PL + h * cw, y, cw - 1, ch - 1, _cell_colour(pct))
        p.setPen(QColor(ACCENT))
        p.drawRect(self.PL, self.PT, cw - 1, len(BANDS) * ch - 1)

    def mouseMoveEvent(self, e):
        if not self._hours:
            return
        cw, ch = self._geom()
        pos: QPointF = e.position()
        h = int((pos.x() - self.PL) // cw)
        bi = int((pos.y() - self.PT) // ch)
        if 0 <= h < HOURS and 0 <= bi < len(BANDS):
            t = self._hours[h]
            QToolTip.showText(e.globalPosition().toPoint(),
                              tr("pathfc.tip", band=BANDS[bi], span=f"{t:%H:%M}–{t + _dt.timedelta(hours=1):%H:%M}",
                                 pct=self._grid[BANDS[bi]][h]), self)
        else:
            QToolTip.hideText()


class PathForecastWidget(QWidget):
    """Paneel 'Padvoorspelling'."""

    show_on_map = Signal(float, float, str)

    def __init__(self, cfg=None, parent=None):
        super().__init__(parent)
        self._cfg = cfg
        self._target = None            # (lat, lon, label)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 4, 6, 4)
        lay.setSpacing(4)
        row = QHBoxLayout()
        self._edit = QLineEdit()
        self._edit.setPlaceholderText(tr("pathfc.placeholder"))
        self._edit.returnPressed.connect(self._on_entry)
        row.addWidget(self._edit, 1)
        go = QPushButton(tr("pathfc.go"))
        go.clicked.connect(self._on_entry)
        row.addWidget(go)
        lay.addLayout(row)
        self._head = QLabel(tr("pathfc.pick"))
        self._head.setWordWrap(True)
        self._head.setTextFormat(Qt.RichText)
        self._head.setStyleSheet("font-size: 8pt;")
        lay.addWidget(self._head)
        self._grid = _Grid()
        lay.addWidget(self._grid, 1)
        self._best = QLabel("")
        self._best.setWordWrap(True)
        self._best.setStyleSheet(f"color: {TEXT_DIM}; font-size: 8pt;")
        lay.addWidget(self._best)
        self._timer = QTimer(self)                # het uur schuift door
        self._timer.timeout.connect(self.recalc)
        self._timer.start(10 * 60_000)

    def set_cfg(self, cfg):
        self._cfg = cfg
        self.recalc()

    def set_target(self, lat: float, lon: float, label: str = ""):
        self._target = (lat, lon, label)
        self.recalc()

    def _on_entry(self):
        res = resolve_target(self._edit.text())
        if res is None:
            self._head.setText(f"<span style='color:#EF5350'>{tr('pathfc.unknown')}</span>")
            return
        self.show_on_map.emit(*res)            # kaart tekent het pad en zet het doel
        self.set_target(*res)

    def recalc(self):
        if self._target is None or self._cfg is None:
            return
        from .panels5 import _station_snr
        from .propagation import _dist_km, bearing_deg
        from .sat_passes import compass
        lat, lon, label = self._target
        qth = (self._cfg.qth_lat, self._cfg.qth_lon)
        km = _dist_km(qth[0], qth[1], lat, lon)
        az = bearing_deg(qth[0], qth[1], lat, lon)
        hours, grid = forecast(qth, (lat, lon), _station_snr(self._cfg))
        self._grid.set_data(hours, grid)
        name = label or f"{lat:+.1f}°, {lon:+.1f}°"
        self._head.setText(tr("pathfc.head", name=name, km=f"{km:,.0f}".replace(",", "."),
                              az=f"{az:.0f}", dir=compass(az), lp=f"{(az + 180) % 360:.0f}"))
        wins = best_windows(hours, grid)
        if wins:
            parts = [f"{b} " + (tr("pathfc.allday") if (t1 - t0) >= _dt.timedelta(hours=HOURS)
                                else f"{t0:%H:%M}–{t1:%H:%M}") + f" ({mx}%)"
                     for b, t0, t1, mx in wins]
            self._best.setText(tr("pathfc.best", wins="  ·  ".join(parts)))
        else:
            self._best.setText(tr("pathfc.none"))
