"""
HAMIOS — Model tegen werkelijkheid: hoe vaak klopt het propagatiemodel?

Elke echte waarneming (WSPR-spot rond de QTH, PSKReporter-melding met één kant
in de eigen regio) is een pad dat op dat moment open wás. Per waarneming
wordt bekeken welke kans het model op dat pad gaf. Per band en per uur:

  gehoord      aantal waarnemingen (paden ≥ 1000 km)
  model eens   deel daarvan waarvoor het model ≥ 50 % gaf
  gem. kans    gemiddelde modelkans op de gehoorde paden
  open, stil   uren waarin het model de band naar minstens één DX-regio open
               gaf, terwijl er op die band niets gehoord werd (terwijl er op
               andere banden wél waarnemingen waren — anders zegt stilte niets)

Opgeslagen in config/hamios_verify.json (30 dagen), zodat de cijfers over
herstarts heen doorlopen.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import threading

from ._appdir import APP_DIR

VERIFY_FILE = os.path.join(APP_DIR, "config", "hamios_verify.json")
KEEP_DAYS = 30
MIN_KM = 1000
OPEN_PCT = 50
LOCAL_KM = 500
BANDS = ["160m", "80m", "60m", "40m", "30m", "20m", "17m", "15m", "12m", "10m", "6m"]


def _hour_key(t: _dt.datetime) -> str:
    return t.astimezone(_dt.timezone.utc).strftime("%Y-%m-%dT%H")


class Verifier:
    """Verzamelt waarnemingen en vergelijkt ze met het model."""

    def __init__(self, path: str = VERIFY_FILE, engine=None):
        from .propagation import ENGINE
        self._eng = engine or ENGINE
        self._path = path
        self._lock = threading.Lock()
        self._seen: set = set()                 # dubbele waarnemingen overslaan
        self.hours: dict = {}                   # uur → {band: {...}}
        self._load()

    # ── opslag ──────────────────────────────────────────────────────────────
    def _load(self):
        try:
            with open(self._path, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and isinstance(data.get("hours"), dict):
                self.hours = data["hours"]
        except (OSError, ValueError):
            self.hours = {}

    def save(self):
        cutoff = _hour_key(_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(days=KEEP_DAYS))
        with self._lock:
            self.hours = {h: v for h, v in self.hours.items() if h >= cutoff}
            data = {"hours": self.hours}
        try:
            os.makedirs(os.path.dirname(self._path), exist_ok=True)
            tmp = self._path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f)
            os.replace(tmp, self._path)
        except OSError:
            pass

    # ── waarnemingen ────────────────────────────────────────────────────────
    def _bucket(self, hour: str, t: _dt.datetime, qth, snr_db: float) -> dict:
        """Uur-bucket; bij aanmaken eenmalig: welke banden het model 'open' gaf."""
        b = self.hours.get(hour)
        if b is None:
            from .propagation import DX_REGIONS, _dist_km
            open_any = {band: False for band in BANDS}
            for _name, rlat, rlon in DX_REGIONS:
                if _dist_km(qth[0], qth[1], rlat, rlon) < 1500:
                    continue
                pct = self._eng.path_band_pct(qth[0], qth[1], rlat, rlon, t, snr_db)
                for band in BANDS:
                    if pct.get(band, 0) >= OPEN_PCT:
                        open_any[band] = True
            b = {band: {"n": 0, "agree": 0, "pct": 0, "open": open_any[band]} for band in BANDS}
            self.hours[hour] = b
        return b

    def add(self, key, t: _dt.datetime, band: str, far: tuple, qth, snr_db: float = 0.0):
        """Eén waarneming: pad QTH → far op `band`, gehoord op tijdstip t."""
        from .propagation import _dist_km
        if band not in BANDS or key in self._seen:
            return
        if _dist_km(qth[0], qth[1], far[0], far[1]) < MIN_KM:
            return
        self._seen.add(key)
        if len(self._seen) > 50_000:
            self._seen.clear()
        pct = self._eng.path_band_pct(qth[0], qth[1], far[0], far[1], t, snr_db).get(band, 0)
        with self._lock:
            b = self._bucket(_hour_key(t), t, qth, snr_db)[band]
            b["n"] += 1
            b["pct"] += int(pct)
            if pct >= OPEN_PCT:
                b["agree"] += 1

    def add_wspr(self, records: list, qth, snr_db: float = 0.0):
        from .layers import _maidenhead_to_latlon
        for r in records or []:
            far = _maidenhead_to_latlon(r.get("grid", ""))
            try:
                t = _dt.datetime.fromisoformat(r.get("time", ""))
            except (TypeError, ValueError):
                continue
            if far is None:
                continue
            key = ("W", r.get("tx_call"), r.get("rx_call"), r.get("band"), r.get("time"))
            self.add(key, t, r.get("band", ""), far, qth, snr_db)

    def add_psk(self, reports: list, qth, snr_db: float = 0.0):
        """PSKReporter-paden waarvan één kant binnen LOCAL_KM van de QTH ligt."""
        from .advisor import band_of
        from .propagation import _dist_km
        now = _dt.datetime.now(_dt.timezone.utc)
        for rep in reports or []:
            try:
                tx, rx, khz = tuple(rep[0]), tuple(rep[1]), float(rep[2])
            except (IndexError, TypeError, ValueError):
                continue
            near_tx = _dist_km(qth[0], qth[1], *tx) <= LOCAL_KM
            near_rx = _dist_km(qth[0], qth[1], *rx) <= LOCAL_KM
            if near_tx == near_rx:
                continue
            far = rx if near_tx else tx
            band = band_of(khz) or ""
            key = ("P", rep[5] if len(rep) > 5 else "", rep[6] if len(rep) > 6 else "",
                   band, now.strftime("%Y%m%d%H") + str(int(now.minute) // 15))
            self.add(key, now, band, far, qth, snr_db)

    # ── uitkomst ────────────────────────────────────────────────────────────
    def stats(self, days: int = 7) -> dict:
        """{band: {'n', 'agree_pct', 'mean_pct', 'open_hours', 'open_silent_pct'}}
        + '_total': {'n', 'agree_pct', 'hours'}."""
        cutoff = _hour_key(_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(days=days))
        with self._lock:
            hours = {h: v for h, v in self.hours.items() if h >= cutoff}
        out = {}
        tot_n = tot_agree = 0
        active = [v for v in hours.values() if sum(b["n"] for b in v.values()) > 0]
        for band in BANDS:
            n = sum(v[band]["n"] for v in hours.values() if band in v)
            agree = sum(v[band]["agree"] for v in hours.values() if band in v)
            pct = sum(v[band]["pct"] for v in hours.values() if band in v)
            open_h = [v for v in active if v.get(band, {}).get("open")]
            silent = sum(1 for v in open_h if v[band]["n"] == 0)
            out[band] = {"n": n, "agree_pct": round(100 * agree / n) if n else None,
                         "mean_pct": round(pct / n) if n else None,
                         "open_hours": len(open_h),
                         "open_silent_pct": round(100 * silent / len(open_h)) if open_h else None}
            tot_n += n
            tot_agree += agree
        out["_total"] = {"n": tot_n, "agree_pct": round(100 * tot_agree / tot_n) if tot_n else None,
                         "hours": len(active)}
        return out


# ── Paneel ────────────────────────────────────────────────────────────────────

def _make_widget_class():
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

    from .extra_panels import _item, _table
    from .i18n import tr
    from .theme import TEXT_DIM, TEXT_H1

    def _col(v, good, bad, reverse=False):
        if v is None:
            return TEXT_DIM
        ok = v <= good if reverse else v >= good
        poor = v >= bad if reverse else v <= bad
        return "#66BB6A" if ok else "#EF5350" if poor else "#FFA726"

    class VerifyWidget(QWidget):
        """Paneel 'Model vs werkelijkheid'."""

        def __init__(self, verifier: Verifier, parent=None):
            super().__init__(parent)
            self._v = verifier
            lay = QVBoxLayout(self)
            lay.setContentsMargins(6, 4, 6, 4)
            lay.setSpacing(4)
            top = QHBoxLayout()
            self._sum = QLabel("")
            self._sum.setWordWrap(True)
            self._sum.setTextFormat(Qt.RichText)
            self._sum.setStyleSheet("font-size: 8pt;")
            top.addWidget(self._sum, 1)
            self._days = QComboBox()
            for d in (1, 7, 30):
                self._days.addItem(tr("verify.days", n=d), d)
            self._days.setCurrentIndex(1)
            self._days.currentIndexChanged.connect(self.refresh)
            top.addWidget(self._days)
            lay.addLayout(top)
            self._tbl = _table([tr("verify.col.band"), tr("verify.col.heard"),
                                tr("verify.col.agree"), tr("verify.col.mean"),
                                tr("verify.col.silent")])
            self._tbl.setToolTip(tr("verify.table_tip"))
            lay.addWidget(self._tbl, 1)
            note = QLabel(tr("verify.note"))
            note.setWordWrap(True)
            note.setStyleSheet(f"color: {TEXT_DIM}; font-size: 7pt;")
            lay.addWidget(note)
            self._timer = QTimer(self)
            self._timer.timeout.connect(self.refresh)
            self._timer.start(5 * 60_000)
            self.refresh()

        def refresh(self):
            st = self._v.stats(int(self._days.currentData() or 7))
            tot = st.pop("_total")
            if not tot["n"]:
                self._sum.setText(tr("verify.empty"))
            else:
                a = tot["agree_pct"]
                self._sum.setText(tr("verify.summary", n=tot["n"], h=tot["hours"],
                                     pct=f"<b style='color:{_col(a, 70, 40)}'>{a}%</b>"))
            rows = [(b, d) for b, d in st.items() if d["n"] or d["open_hours"]]
            self._tbl.setRowCount(len(rows))
            for i, (band, d) in enumerate(rows):
                fmt = lambda v: "—" if v is None else f"{v}%"   # noqa: E731
                self._tbl.setItem(i, 0, _item(band, TEXT_H1, bold=True))
                self._tbl.setItem(i, 1, _item(str(d["n"]), align=Qt.AlignRight))
                self._tbl.setItem(i, 2, _item(fmt(d["agree_pct"]), _col(d["agree_pct"], 70, 40),
                                              align=Qt.AlignRight))
                self._tbl.setItem(i, 3, _item(fmt(d["mean_pct"]), align=Qt.AlignRight))
                self._tbl.setItem(i, 4, _item(
                    fmt(d["open_silent_pct"]) + (f"  ({d['open_hours']} {tr('lightn.per_hour')})" if d["open_hours"] else ""),
                    _col(d["open_silent_pct"], 30, 70, reverse=True), align=Qt.AlignRight))

    return VerifyWidget


def VerifyWidget(verifier, parent=None):          # noqa: N802 — fabriek (Qt pas laden bij gebruik)
    return _make_widget_class()(verifier, parent)
