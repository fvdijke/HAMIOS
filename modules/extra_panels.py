"""
HAMIOS — extra panelen

IonosondeWidget  — gemeten ionosfeer (KC2G/GIRO): dichtstbijzijnde stations
SatPassesWidget  — overkomsten van de gevolgde satellieten + melding vooraf
"""

from __future__ import annotations

import datetime as _dt

from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QAbstractItemView, QHeaderView, QLabel,
                               QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from .i18n import tr
from .propagation import (BANDS, ENGINE, IONO_MAX_AGE_S, _dist_km, model_fof2,
                          model_m3000)
from .theme import ACCENT, BG_PANEL, BG_SURFACE, TEXT_BODY, TEXT_DIM, TEXT_H1

_GREEN, _AMBER, _RED = "#66BB6A", "#FFA726", "#EF5350"
_HF = [(b, f) for b, f in BANDS if b != "6m"]


def _table(headers: list[str], stretch: int = 0) -> QTableWidget:
    t = QTableWidget(0, len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.verticalHeader().setVisible(False)
    t.setEditTriggers(QAbstractItemView.NoEditTriggers)
    t.setSelectionMode(QAbstractItemView.NoSelection)
    t.setFocusPolicy(Qt.NoFocus)
    t.setWordWrap(False)
    t.setShowGrid(False)
    t.setAlternatingRowColors(True)
    h = t.horizontalHeader()
    h.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    h.setSectionResizeMode(QHeaderView.ResizeToContents)
    h.setSectionResizeMode(stretch, QHeaderView.Stretch)
    h.setMinimumSectionSize(28)
    t.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    t.verticalHeader().setDefaultSectionSize(20)
    t.setStyleSheet(
        f"QTableWidget {{ background: {BG_PANEL}; alternate-background-color: {BG_SURFACE};"
        f" color: {TEXT_BODY}; border: none; font-size: 8pt; }}"
        f"QHeaderView::section {{ background: {BG_SURFACE}; color: {ACCENT}; border: none;"
        f" padding: 2px 6px; font-size: 8pt; font-weight: bold; }}")
    return t


def _item(text: str, color: str | None = None, bold: bool = False,
          align=Qt.AlignLeft) -> QTableWidgetItem:
    it = QTableWidgetItem(text)
    it.setTextAlignment(align | Qt.AlignVCenter)
    if color:
        it.setForeground(QColor(color))
    if bold:
        f = it.font()
        f.setBold(True)
        it.setFont(f)
    return it


def _highest_band(limit_mhz: float) -> str | None:
    """Hoogste HF-band onder de grens (met 10 % marge)."""
    ok = [b for b, f in _HF if f <= limit_mhz * 0.9]
    return ok[-1] if ok else None


# ── Ionosondes ────────────────────────────────────────────────────────────────

class IonosondeWidget(QWidget):
    """Gemeten ionosfeer rond de QTH: foF2, MUF(3000) en foEs van de
    dichtstbijzijnde digisondes (GIRO via prop.kc2g.com). De ★-regel is het
    station waarmee het propagatiemodel gekalibreerd wordt."""

    MAX_ROWS = 12

    def __init__(self, cfg=None, parent=None):
        super().__init__(parent)
        self._cfg = cfg
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 4, 6, 4)
        lay.setSpacing(4)
        self._summary = QLabel(tr("iono.waiting"))
        self._summary.setTextFormat(Qt.RichText)
        self._summary.setWordWrap(True)
        self._summary.setStyleSheet(f"color: {TEXT_BODY}; font-size: 8pt;")
        lay.addWidget(self._summary)
        self._table = _table([tr("iono.col.station"), tr("iono.col.km"), "foF2",
                              "MUF", "foEs", tr("iono.col.age")])
        self._table.setToolTip(tr("iono.table_tip"))
        lay.addWidget(self._table, 1)
        self._summary.setToolTip(tr("iono.source"))
        ENGINE.updated.connect(self.refresh)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(60_000)
        self.refresh()

    def set_cfg(self, cfg):
        self._cfg = cfg
        self.refresh()

    def _qth(self) -> tuple[float, float]:
        c = self._cfg
        return (c.qth_lat, c.qth_lon) if c else (52.0, 5.0)

    def resizeEvent(self, event):
        """Smal paneel: foEs en leeftijd verbergen (verouderde rijen blijven
        herkenbaar aan de gedimde kleur) zodat de stationsnaam past."""
        super().resizeEvent(event)
        w = self.width()
        self._table.setColumnHidden(4, w < 380)
        self._table.setColumnHidden(5, w < 320)

    def refresh(self):
        lat, lon = self._qth()
        now = _dt.datetime.now(_dt.timezone.utc)
        stations = ENGINE.ionosondes()
        if not stations:
            self._summary.setText(tr("iono.waiting"))
            self._table.setRowCount(0)
            return
        rows = sorted(((_dist_km(lat, lon, s.lat, s.lon), s) for s in stations),
                      key=lambda r: r[0])[:self.MAX_ROWS]
        used = ENGINE.nearest_ionosonde(lat, lon, now)
        self._summary.setText(self._summary_html(used, lat, lon, now))

        t = self._table
        t.setRowCount(len(rows))
        for r, (km, s) in enumerate(rows):
            age_min = s.age_s(now) / 60
            stale = s.age_s(now) > IONO_MAX_AGE_S
            dim = TEXT_DIM if stale else None
            star = s is used
            t.setItem(r, 0, _item(("★ " if star else "") + s.name.split(",")[0],
                                  ACCENT if star else (dim or TEXT_H1), bold=star))
            t.setItem(r, 1, _item(f"{km:.0f}", dim, align=Qt.AlignRight))
            t.setItem(r, 2, _item(f"{s.fof2:.1f}", dim, align=Qt.AlignRight))
            t.setItem(r, 3, _item(f"{s.mufd:.1f}" if s.mufd else "—", dim, align=Qt.AlignRight))
            es_col = (_AMBER if s.foes and s.foes >= 5 else None) if not stale else dim
            t.setItem(r, 4, _item(f"{s.foes:.1f}" if s.foes else "—", es_col, align=Qt.AlignRight))
            age_txt = tr("iono.age_min", n=int(age_min)) if age_min < 120 else \
                tr("iono.age_h", n=int(age_min / 60))
            t.setItem(r, 5, _item(age_txt, _RED if stale else TEXT_DIM))

    def _summary_html(self, s, lat, lon, now) -> str:
        if s is None:
            return tr("iono.none_near")
        km = _dist_km(lat, lon, s.lat, s.lon)
        head = (f"<b style='color:{ACCENT}'>{tr('iono.local')}</b> "
                f"<span style='color:{TEXT_DIM}'>{s.name} · {km:.0f} km · "
                f"{tr('iono.age_min', n=int(s.age_s(now) / 60))}</span>")
        nvis = _highest_band(s.fof2)
        lines = [head,
                 tr("iono.nvis", fof2=f"{s.fof2:.1f}",
                    band=nvis or tr("iono.no_band"))]
        if s.mufd:
            dx = _highest_band(s.mufd)
            lines.append(tr("iono.dx", muf=f"{s.mufd:.1f}", band=dx or tr("iono.no_band")))
        # Meting vs model: hoe wijkt de ionosfeer nu af van het gemiddelde?
        f_mod = model_fof2(s.lat, s.lon, s.time, ENGINE.ssn, ENGINE.k)
        if s.mufd:
            ratio = s.mufd / (f_mod * model_m3000(s.lat, s.lon, s.time))
        else:
            ratio = s.fof2 / f_mod
        pct = int(round((ratio - 1) * 100))
        col = _GREEN if pct >= 5 else _RED if pct <= -10 else TEXT_BODY
        lines.append(tr("iono.vs_model", pct=f"<b style='color:{col}'>{pct:+d} %</b>"))
        if s.foes and s.foes >= 5:
            lines.append(f"<span style='color:{_AMBER}'>{tr('iono.es', foes=f'{s.foes:.1f}')}</span>")
        return "<br>".join(lines)


# ── Satelliet-overkomsten ─────────────────────────────────────────────────────

class _PassThread(QThread):
    done = Signal(list, object)          # [SatPass], berekend-op

    def __init__(self, tles: dict, lat: float, lon: float, parent=None):
        super().__init__(parent)
        self._args = (tles, lat, lon)

    def run(self):
        from .sat_passes import predict_passes
        now = _dt.datetime.now(_dt.timezone.utc)
        tles, lat, lon = self._args
        try:
            passes = predict_passes(tles, lat, lon, now, hours=24)
        except Exception:
            passes = []
        self.done.emit(passes, now)


class SatPassesWidget(QWidget):
    """Overkomsten (24 uur) van de satellieten die op de kaart gevolgd worden.
    Een lopende overkomst staat groen met LOS-aftelling. Vijf minuten vóór een
    overkomst (max. elevatie ≥ drempel) volgt een melding via pass_soon."""

    pass_soon = Signal(str, int, float, str)        # naam, minuten, max elev, richting
    ALERT_MIN = 5
    MAX_ROWS = 40
    MIN_SHOW_EL = 2.0          # scherende overkomsten (< 2°) zijn onbruikbaar

    def __init__(self, cfg=None, parent=None):
        super().__init__(parent)
        self._cfg = cfg
        self._source = None                 # callable → (tles, lat, lon)
        self._passes: list = []
        self._sig = None
        self._thread: _PassThread | None = None
        self._alerted: set = set()
        self._last_calc: _dt.datetime | None = None
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 4, 6, 4)
        lay.setSpacing(4)
        self._status = QLabel(tr("pass.waiting"))
        self._status.setWordWrap(True)
        self._status.setStyleSheet(f"color: {TEXT_DIM}; font-size: 8pt;")
        lay.addWidget(self._status)
        self._table = _table([tr("pass.col.sat"), tr("pass.col.aos"), tr("pass.col.when"),
                              tr("pass.col.dur"), tr("pass.col.max"), tr("pass.col.dir")],
                             stretch=5)
        self._table.setToolTip(tr("pass.table_tip"))
        lay.addWidget(self._table, 1)
        self._tick_timer = QTimer(self)
        self._tick_timer.timeout.connect(self._tick)
        self._tick_timer.start(5_000)

    def set_cfg(self, cfg):
        self._cfg = cfg
        self._tick()

    def set_source(self, fn):
        """fn() → ({naam: (regel1, regel2)} van de gevolgde satellieten, lat, lon)."""
        self._source = fn
        QTimer.singleShot(2000, self._tick)

    # ── berekenen ────────────────────────────────────────────────────────────
    def _tick(self):
        if self._source is None:
            return
        try:
            tles, lat, lon = self._source()
        except Exception:
            return
        sig = (tuple(sorted((n, l[1][:30]) for n, l in tles.items())),
               round(lat, 3), round(lon, 3))
        now = _dt.datetime.now(_dt.timezone.utc)
        stale = self._last_calc is None or (now - self._last_calc).total_seconds() > 1800
        if (sig != self._sig or stale) and self._thread is None:
            self._sig = sig
            if not tles:
                self._passes = []
                self._status.setText(tr("pass.none_selected"))
                self._table.setRowCount(0)
                return
            th = _PassThread(tles, lat, lon, self)
            th.done.connect(self._on_passes)
            th.finished.connect(th.deleteLater)
            self._thread = th
            th.start()
        self._render(now)
        self._check_alerts(now)

    def _on_passes(self, passes: list, calc_time):
        self._thread = None
        self._passes = passes
        self._last_calc = calc_time
        self._render(_dt.datetime.now(_dt.timezone.utc))

    # ── tonen ────────────────────────────────────────────────────────────────
    def _min_el(self) -> float:
        return float(getattr(self._cfg, "sat_pass_min_el", 10))

    def _render(self, now: _dt.datetime):
        from .sat_passes import compass
        passes = [p for p in self._passes
                  if p.los > now and p.max_el >= self.MIN_SHOW_EL][:self.MAX_ROWS]
        n_sats = len(self._sig[0]) if self._sig else 0
        if self._sig and not self._sig[0]:
            return
        if self._last_calc is None:
            self._status.setText(tr("pass.calculating"))
            return
        self._status.setText(tr("pass.status", n=n_sats, count=len(passes)))
        t = self._table
        t.setRowCount(len(passes))
        min_el = self._min_el()
        for r, p in enumerate(passes):
            live = p.aos <= now < p.los
            low = p.max_el < min_el
            base = TEXT_DIM if low and not live else None
            name = p.name.split("(")[0].strip()[:18]
            t.setItem(r, 0, _item(name, _GREEN if live else (base or TEXT_H1), bold=live))
            t.setItem(r, 1, _item(p.aos.astimezone().strftime("%H:%M"), base))
            if live:
                left = int((p.los - now).total_seconds())
                when = tr("pass.live", t=f"{left // 60}:{left % 60:02d}")
                col = _GREEN
            else:
                mins = int((p.aos - now).total_seconds() // 60)
                when = tr("pass.in_min", n=mins) if mins < 60 else \
                    tr("pass.in_h", h=mins // 60, m=f"{mins % 60:02d}")
                col = _AMBER if mins < self.ALERT_MIN and not low else base
            t.setItem(r, 2, _item(when, col, bold=live))
            d = int(p.duration_s)
            t.setItem(r, 3, _item(f"{d // 60}:{d % 60:02d}", base, align=Qt.AlignRight))
            el_col = _GREEN if p.max_el >= 45 else _AMBER if p.max_el >= 20 else TEXT_DIM
            t.setItem(r, 4, _item(f"{p.max_el:.0f}°", el_col, align=Qt.AlignRight))
            t.setItem(r, 5, _item(f"{compass(p.az_aos)} → {compass(p.az_los)}", base))

    def _check_alerts(self, now: _dt.datetime):
        if not getattr(self._cfg, "sat_pass_alert", True):
            return
        from .sat_passes import compass
        min_el = self._min_el()
        for p in self._passes:
            key = (p.name, p.aos.replace(second=0, microsecond=0))
            secs = (p.aos - now).total_seconds()
            if 0 < secs <= self.ALERT_MIN * 60 and p.max_el >= min_el and key not in self._alerted:
                self._alerted.add(key)
                self.pass_soon.emit(p.name.split("(")[0].strip()[:20],
                                    max(1, int(round(secs / 60))), p.max_el,
                                    f"{compass(p.az_aos)} → {compass(p.az_los)}")
