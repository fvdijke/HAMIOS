"""HAMIOS v5 — Propagatie-advies paneel (P2).

Toont de uitkomst van advisor.build_advice():
  1. eindoordeel + onderbouwing (MUF, bron, aantal waarnemingen)
  2. gebeurtenissen (zonnevlam, storm, schokgolf, Es …)
  3. aanbevelingen: band → mode/frequentie → richting → tijdvenster,
     met modelkans en waarnemingen — klik = afstemmen via CAT + pad op kaart
  4. komende uren (grayline, banden die opengaan/sluiten)
  5. trends komend uur

Wordt één keer opgebouwd en daarna alleen bijgewerkt (vaste rijen).
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QScrollArea,
                               QToolTip, QVBoxLayout, QWidget)

from . import advisor as _adv
from . import advice_explain as _x
from .i18n import tr, language_changed
from .theme import ACCENT, BG_PANEL, BG_SURFACE, TEXT_BODY, TEXT_DIM

_LEVEL_CLR = {0: "#EF5350", 1: "#FFA726", 2: "#8BC34A", 3: "#4CAF50"}
_EVENT_CLR = {"red": "#EF5350", "amber": "#FFA726", "green": "#66BB6A", "info": "#4FC3F7"}
_BAND_CLR = {
    "160m": "#9575CD", "80m": "#5C6BC0", "60m": "#42A5F5", "40m": "#26C6DA",
    "30m": "#26A69A", "20m": "#66BB6A", "17m": "#D4E157", "15m": "#FFCA28",
    "12m": "#FFA726", "10m": "#EF5350", "6m": "#EC407A",
}
_MAX_RECS, _MAX_EVENTS, _MAX_TL = 5, 5, 6
# Meldingen die alleen het advies kent → ook naar het meldingen-paneel.
# K-storm en zonnevlammen (R) bewaakt het meldingen-paneel zelf met de drempels
# uit de instellingen — die niet doorsturen, anders verschijnen ze dubbel.
_FORWARD = {"adv.ev.radiation", "adv.ev.shock", "adv.ev.bz_south", "adv.ev.es_active"}


def _region(code: str) -> str:
    return tr(f"region.{code}")


class _PctBar(QWidget):
    """Balkje 0–100 %: lengte = effectieve kans (model + waarnemingen), kleur =
    band. Een wit streepje markeert de kale modelkans als die daarvan afwijkt."""

    def __init__(self):
        super().__init__()
        self._eff, self._model, self._clr = 0, 0, QColor(ACCENT)
        self.setFixedSize(46, 8)

    def set_value(self, eff: int, model: int, clr: str):
        self._eff = max(0, min(100, eff))
        self._model = max(0, min(100, model))
        self._clr = QColor(clr)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        w, h = self.width(), self.height()
        p.fillRect(self.rect(), QColor(BG_PANEL))
        p.fillRect(0, 0, int(w * self._eff / 100), h, self._clr)
        if abs(self._eff - self._model) >= 5:
            x = min(w - 2, int(w * self._model / 100))
            p.fillRect(x, 0, 2, h, QColor(255, 255, 255, 220))


class _RecRow(QFrame):
    """Eén aanbeveling; klikbaar."""

    clicked = Signal(object)

    def __init__(self):
        super().__init__()
        self._rec = None
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("recrow")
        self.setStyleSheet(
            f"QFrame#recrow {{ background: {BG_SURFACE}; border-radius: 3px; }}"
            f"QFrame#recrow:hover {{ border: 1px solid {ACCENT}; }}")
        h = QHBoxLayout(self)
        h.setContentsMargins(6, 3, 6, 3)
        h.setSpacing(8)
        f8, f8b = QFont("Segoe UI", 8), QFont("Segoe UI", 9)
        f8b.setBold(True)
        self._band = QLabel(); self._band.setFont(f8b); self._band.setFixedWidth(38)
        self._freq = QLabel(); self._freq.setFont(f8); self._freq.setFixedWidth(92)
        self._dest = QLabel(); self._dest.setFont(f8)
        self._bar = _PctBar()
        self._when = QLabel(); self._when.setFont(f8); self._when.setFixedWidth(70)
        self._evid = QLabel(); self._evid.setFont(f8); self._evid.setFixedWidth(150)
        for lb in (self._band, self._freq, self._dest, self._when, self._evid):
            lb.setStyleSheet("background: transparent;")
        h.addWidget(self._band)
        h.addWidget(self._freq)
        h.addWidget(self._dest, 1)
        h.addWidget(self._bar)
        h.addWidget(self._when)
        h.addWidget(self._evid)

    def set_rec(self, r, station: str = "", snr_db: float = 0.0):
        self._rec = r
        clr = _BAND_CLR.get(r.band, ACCENT)
        self._band.setText(r.band)
        self._band.setStyleSheet(f"color: {clr}; background: transparent;")
        self._freq.setText(f"{r.mode}  {r.freq_khz / 1000:.3f}")
        self._freq.setStyleSheet(f"color: {TEXT_BODY}; background: transparent;")
        self._dest.setText(f"→ {_region(r.region)}")
        self._dest.setStyleSheet(f"color: {TEXT_BODY}; background: transparent;")
        self._bar.set_value(r.eff, r.pct, clr)
        self._bar.setToolTip(tr("adv.bar_tip", eff=r.eff, p=r.pct, n=r.obs))
        self._when.setText(tr("adv.until", t=_adv.fmt_hhmm(r.until)) if r.until
                           else (tr("adv.open_long") if r.pct >= 50 else ""))
        self._when.setStyleSheet(f"color: {TEXT_DIM}; background: transparent;")
        if r.confidence == "confirmed":
            ev, ec = tr("adv.conf.confirmed", n=r.obs), "#4CAF50"
        elif r.confidence == "observed":
            ev, ec = tr("adv.conf.observed", n=r.obs, p=r.pct), "#4FC3F7"
        else:
            ev, ec = tr("adv.conf.model", p=r.pct), TEXT_DIM
        self._evid.setText(ev)
        self._evid.setStyleSheet(f"color: {ec}; background: transparent;")
        self.setToolTip(_x.rec_tooltip(r, _region(r.region), station, snr_db,
                                       _adv.fmt_hhmm(r.until) if r.until else ""))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._rec is not None:
            self.clicked.emit(self._rec)
        super().mousePressEvent(event)


class _GuideLabel(QLabel):
    """'ⓘ Zo lees je dit' — leeswijzer als tooltip; klik houdt hem in beeld."""

    def __init__(self):
        super().__init__(tr("adv.guide.btn"))
        self.setCursor(Qt.WhatsThisCursor)
        self.setStyleSheet(f"color: {ACCENT}; background: transparent;")
        self.setToolTip(_x.reading_guide())

    def retranslate(self):
        self.setText(tr("adv.guide.btn"))
        self.setToolTip(_x.reading_guide())

    def mousePressEvent(self, event):
        QToolTip.showText(event.globalPosition().toPoint(), self.toolTip(), self,
                          self.rect(), 60000)
        super().mousePressEvent(event)


class PropAdvWidget(QWidget):
    """Propagatie-advies: oordeel, gebeurtenissen, aanbevelingen, tijdlijn."""

    # Nieuwe gebeurtenissen → meldingen-paneel: [(icoon, tekst, kleur)]
    analysis_changed = Signal(list)
    # Klik op aanbeveling → (lat, lon, frequentie kHz, mode, kaartlabel)
    recommendation_clicked = Signal(float, float, float, str, str)

    def __init__(self, cfg=None, parent=None):
        super().__init__(parent)
        self._cfg = cfg
        self._solar: dict = {}
        self._wspr: list = []
        self._dx: list = []
        self._psk: list = []
        self._last_events: set = set()
        self._advice = None
        self._build_ui()
        # Invoer komt uit meerdere bronnen: bundel herberekeningen
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(600)
        self._timer.timeout.connect(self._rebuild)
        # Tijdvensters en tijdlijn schuiven mee met de klok
        self._tick = QTimer(self)
        self._tick.timeout.connect(self._rebuild)
        self._tick.start(10 * 60 * 1000)
        language_changed.connect(self.retranslate)

    # ── opbouw (één keer) ────────────────────────────────────────────────────
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background: {BG_PANEL}; border: none; }}")
        outer.addWidget(scroll)
        body = QWidget()
        body.setStyleSheet(f"background: {BG_PANEL};")
        scroll.setWidget(body)
        v = QVBoxLayout(body)
        v.setContentsMargins(6, 4, 6, 4)
        v.setSpacing(4)

        f11b = QFont("Segoe UI", 11); f11b.setBold(True)
        f8, f8b = QFont("Segoe UI", 8), QFont("Segoe UI", 8)
        f8b.setBold(True)

        self._verdict = QLabel(tr("app.loading"))
        self._verdict.setFont(f11b)
        self._verdict.setWordWrap(True)
        v.addWidget(self._verdict)
        self._sub = QLabel("")
        self._sub.setFont(f8)
        self._sub.setStyleSheet(f"color: {TEXT_DIM};")
        v.addWidget(self._sub)

        self._event_lbls = []
        for _ in range(_MAX_EVENTS):
            lb = QLabel()
            lb.setFont(f8)
            lb.setWordWrap(True)
            lb.hide()
            v.addWidget(lb)
            self._event_lbls.append(lb)

        self._recs_title = QLabel(tr("adv.sec.recs"))
        self._recs_title.setFont(f8b)
        self._recs_title.setStyleSheet(f"color: {ACCENT};")
        self._guide = _GuideLabel()
        self._guide.setFont(f8)
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.addWidget(self._recs_title)
        title_row.addStretch()
        title_row.addWidget(self._guide)
        v.addLayout(title_row)
        self._rows = []
        for _ in range(_MAX_RECS):
            row = _RecRow()
            row.clicked.connect(self._on_rec_clicked)
            row.hide()
            v.addWidget(row)
            self._rows.append(row)
        self._no_recs = QLabel(tr("adv.sec.none"))
        self._no_recs.setFont(f8)
        self._no_recs.setStyleSheet(f"color: {TEXT_DIM};")
        self._no_recs.hide()
        v.addWidget(self._no_recs)

        self._tl_title = QLabel(tr("adv.sec.timeline"))
        self._tl_title.setFont(f8b)
        self._tl_title.setStyleSheet(f"color: {ACCENT};")
        v.addWidget(self._tl_title)
        self._tl_lbls = []
        for _ in range(_MAX_TL):
            lb = QLabel()
            lb.setFont(f8)
            lb.setStyleSheet(f"color: {TEXT_BODY};")
            lb.hide()
            v.addWidget(lb)
            self._tl_lbls.append(lb)

        self._cat_lbl = QLabel("")
        self._cat_lbl.setFont(f8)
        self._cat_lbl.hide()
        v.addWidget(self._cat_lbl)
        self._cat_timer = QTimer(self)
        self._cat_timer.setSingleShot(True)
        self._cat_timer.timeout.connect(self._cat_lbl.hide)

        self._trend = QLabel("")
        self._trend.setFont(f8)
        self._trend.setWordWrap(True)
        self._trend.setStyleSheet(f"color: {TEXT_DIM};")
        v.addWidget(self._trend)
        v.addStretch()

    # ── invoer ───────────────────────────────────────────────────────────────
    def set_cfg(self, cfg):
        self._cfg = cfg
        self._timer.start()

    def set_data(self, solar: dict):
        self._solar = solar
        self._timer.start()

    def set_wspr(self, records: list):
        self._wspr = list(records or [])
        self._timer.start()

    def set_dx(self, raw_spots: list):
        self._dx = list(raw_spots or [])
        self._timer.start()

    def set_psk(self, reports: list):
        self._psk = list(reports or [])
        self._timer.start()

    def retranslate(self):
        self._guide.retranslate()
        self._recs_title.setText(tr("adv.sec.recs"))
        self._tl_title.setText(tr("adv.sec.timeline"))
        self._no_recs.setText(tr("adv.sec.none"))
        self._rebuild()

    # ── berekenen + tonen ────────────────────────────────────────────────────
    def _snr(self) -> float:
        from .panels5 import _station_snr
        return _station_snr(self._cfg)

    def _rebuild(self):
        cfg = self._cfg
        qth = (cfg.qth_lat, cfg.qth_lon) if cfg else (52.0, 5.0)
        try:
            k_alert = (float(getattr(cfg, "k_alert", 4))
                       if cfg is not None and getattr(cfg, "k_alert_en", True) else 99)
            adv = _adv.build_advice(qth, self._solar, snr_db=self._snr(),
                                    cfg_mode=getattr(cfg, "mode", "SSB") if cfg else "SSB",
                                    wspr=self._wspr, dx=self._dx, psk=self._psk,
                                    k_alert=k_alert)
        except Exception as e:                          # nooit het paneel laten crashen
            self._verdict.setText(f"⚠ {e}")
            return
        self._advice = adv
        self._show(adv)

    def _show(self, adv):
        lvl_txt = tr(f"adv.level.{adv.level}")
        clr = _LEVEL_CLR[adv.level]
        if adv.recs:
            r = adv.recs[0]
            self._verdict.setText(tr("adv.verdict", level=lvl_txt, band=r.band,
                                     region=_region(r.region)))
        else:
            self._verdict.setText(tr("adv.verdict_none", level=lvl_txt))
        self._verdict.setStyleSheet(f"color: {clr};")
        src = tr("adv.src.model") if adv.source == "model" else adv.source
        self._sub.setText(tr("adv.sub", muf=adv.muf, src=src, n=adv.obs_total))
        red_amber = [tr(e.key, **e.params) for e in adv.events if e.level in ("red", "amber")]
        self._verdict.setToolTip(_x.verdict_tooltip(adv, red_amber))
        self._sub.setToolTip(_x.sub_tooltip(adv, self._iono_age_min()))

        # Gebeurtenissen (nieuwe ook naar het meldingen-paneel)
        new_events = []
        for lb, ev in zip(self._event_lbls, adv.events + [None] * _MAX_EVENTS):
            if ev is None:
                lb.hide()
                continue
            params = dict(ev.params)
            if "sid" in params:
                params["name"] = tr(f"meteor.{params['sid']}")
            text = tr(ev.key, **params)
            c = _EVENT_CLR.get(ev.level, TEXT_BODY)
            lb.setText(f"{ev.icon}  {text}")
            lb.setToolTip(_x.event_tooltip(ev))
            lb.setStyleSheet(f"color: {c}; background: {BG_SURFACE}; border-left: 3px solid {c};"
                             f" padding: 3px 6px; border-radius: 2px;")
            lb.show()
            sig = (ev.key, tuple(sorted(ev.params.items())))
            if sig not in self._last_events and ev.key in _FORWARD:
                new_events.append((ev.icon, text, c))
        self._last_events = {(e.key, tuple(sorted(e.params.items()))) for e in adv.events}
        if new_events:
            self.analysis_changed.emit(new_events)

        # Aanbevelingen
        for row, rec in zip(self._rows, adv.recs + [None] * _MAX_RECS):
            if rec is None:
                row.hide()
            else:
                row.set_rec(rec, self._station_desc(), self._snr())
                row.show()
        self._no_recs.setVisible(not adv.recs)

        # Tijdlijn
        self._tl_title.setVisible(bool(adv.timeline))
        for lb, it in zip(self._tl_lbls, adv.timeline + [None] * _MAX_TL):
            if it is None:
                lb.hide()
            else:
                lb.setText(f"{_adv.fmt_hhmm(it.time)}   {it.icon}  {tr(it.key, **it.params)}")
                lb.setToolTip(_x.timeline_tooltip(it))
                lb.show()

        # Trends + Es
        up = [b for b, t in adv.trends.items() if t > 0]
        down = [b for b, t in adv.trends.items() if t < 0]
        parts = []
        if up or down:
            parts.append(tr("adv.trends") + "  " + "  ".join(
                [f"▲{b}" for b in up] + [f"▼{b}" for b in down]))
        if adv.es.get("foes") is not None:
            parts.append(tr("adv.es_line", foes=adv.es["foes"], station=adv.es["station"]))
        self._trend.setText("   ·   ".join(parts))
        self._trend.setToolTip(_x.trend_tooltip())

    def show_cat_result(self, ok: bool | None, text: str):
        """Korte terugmelding na klik op een aanbeveling.
        ok=True afgestemd · False CAT-fout · None alleen pad (geen CAT)."""
        clr = "#4CAF50" if ok else ("#EF5350" if ok is False else TEXT_DIM)
        self._cat_lbl.setText(f"{'📟' if ok is not None else '🗺'}  {text}")
        self._cat_lbl.setStyleSheet(f"color: {clr};")
        self._cat_lbl.show()
        self._cat_timer.start(5000)

    def _station_desc(self) -> str:
        c = self._cfg
        if not c:
            return "SSB · 100W"
        return " · ".join(str(x) for x in (getattr(c, "mode", ""), getattr(c, "power", ""),
                                           getattr(c, "antenna", "")) if x)

    def _iono_age_min(self):
        from .propagation import ENGINE
        c = self._cfg
        qth = (c.qth_lat, c.qth_lon) if c else (52.0, 5.0)
        s = ENGINE.nearest_ionosonde(*qth)
        return int(s.age_s() // 60) if s else None

    def _on_rec_clicked(self, rec):
        label = f"{rec.band} → {_region(rec.region)} · {rec.dist_km:,} km".replace(",", ".")
        self.recommendation_clicked.emit(float(rec.lat), float(rec.lon),
                                         float(rec.freq_khz), rec.mode, label)
