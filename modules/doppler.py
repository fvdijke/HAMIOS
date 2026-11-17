"""
HAMIOS — Doppler bij satellieten.

Voor de gevolgde satellieten (op de kaart geselecteerd) de zenders uit de
SatNOGS-database (per NORAD-nummer, 30 dagen bewaard) met de Doppler-
gecorrigeerde frequenties van dit moment:

  downlink (ontvangen)  f · (1 − v/c)      v = naderings-/verwijdersnelheid
  uplink   (zenden)     f / (1 − v/c)      zodat de satelliet f ontvangt

v komt uit het baanmodel (sat_passes): de afstand QTH → satelliet een halve
seconde vóór en na nu. 'Afstemmen' zet de gecorrigeerde downlink via CAT op de
radio; met 'Volgen' gebeurt dat elke 2 s (alleen bij > 50 Hz verschil).
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import threading
import time
import urllib.request

from ._appdir import APP_DIR
from .version import USER_AGENT

C_KM_S = 299_792.458
TX_FILE = os.path.join(APP_DIR, "config", "hamios_transmitters.json")
TX_URL = "https://db.satnogs.org/api/transmitters/?format=json&satellite__norad_cat_id={n}"
MAX_AGE_S = 30 * 86400
_lock = threading.Lock()


def norad_of(line1: str) -> int | None:
    try:
        return int(line1[2:7])
    except (ValueError, IndexError):
        return None


def range_rate(l1: str, l2: str, lat: float, lon: float, t: _dt.datetime) -> tuple[float, float, float]:
    """(afstandsverandering km/s — positief = verwijdert, azimut °, elevatie °)."""
    from .sat_passes import look_angles, sat_ecef
    h = _dt.timedelta(seconds=0.5)
    d0 = look_angles(sat_ecef(l1, l2, t - h), lat, lon)[2]
    az, el, _ = look_angles(sat_ecef(l1, l2, t), lat, lon)
    d1 = look_angles(sat_ecef(l1, l2, t + h), lat, lon)[2]
    return d1 - d0, az, el


def downlink(f_hz: float, rr_km_s: float) -> float:
    return f_hz * (1 - rr_km_s / C_KM_S)


def uplink(f_hz: float, rr_km_s: float) -> float:
    return f_hz / (1 - rr_km_s / C_KM_S)


# ── zenderdatabase ────────────────────────────────────────────────────────────

def _load() -> dict:
    try:
        with open(TX_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save(data: dict):
    try:
        os.makedirs(os.path.dirname(TX_FILE), exist_ok=True)
        tmp = TX_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.replace(tmp, TX_FILE)
    except OSError:
        pass


def _clean(items) -> list[dict]:
    out = []
    for it in items if isinstance(items, list) else []:
        if not isinstance(it, dict) or not it.get("alive", True):
            continue
        dl = it.get("downlink_low")
        if not dl:
            continue
        out.append({"desc": str(it.get("description", ""))[:40],
                    "mode": str(it.get("mode") or ""),
                    "down": float(dl),
                    "up": float(it["uplink_low"]) if it.get("uplink_low") else None,
                    "invert": bool(it.get("invert")),
                    "status": str(it.get("status", ""))})
    out.sort(key=lambda t: (t["status"] != "active", t["down"]))
    return out


def transmitters(norad: int, allow_download: bool = True) -> list[dict]:
    """Zenders van een satelliet (bewaard; ouder dan 30 dagen → opnieuw ophalen)."""
    key = str(norad)
    with _lock:
        cache = _load()
    hit = cache.get(key)
    if hit and time.time() - hit.get("t", 0) < MAX_AGE_S:
        return hit.get("items", [])
    if not allow_download:
        return hit.get("items", []) if hit else []
    try:
        req = urllib.request.Request(TX_URL.format(n=int(norad)), headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=20) as r:
            items = _clean(json.loads(r.read().decode("utf-8", errors="replace")))
    except Exception:
        return hit.get("items", []) if hit else []
    with _lock:
        cache = _load()
        cache[key] = {"t": time.time(), "items": items}
        _save(cache)
    return items


def cat_mode(mode: str) -> str:
    m = (mode or "").upper()
    if m.startswith("CW"):
        return "CW"
    if "FM" in m or "AFSK" in m or "APRS" in m:
        return "FM"
    return "USB"


# ── Paneel ────────────────────────────────────────────────────────────────────

def DopplerWidget(cfg=None, source=None, parent=None):    # noqa: N802 — fabriek
    return _widget_class()(cfg, source, parent)


def _widget_class():
    from PySide6.QtCore import Qt, QThread, QTimer, Signal
    from PySide6.QtWidgets import (QCheckBox, QComboBox, QHBoxLayout, QLabel, QPushButton,
                                   QVBoxLayout, QWidget)

    from .extra_panels import _set_text, _table, bulk_fill
    from .i18n import tr
    from .theme import TEXT_BODY, TEXT_DIM, TEXT_H1

    class _TxThread(QThread):
        done = Signal(int, list)

        def __init__(self, norad, parent=None):
            super().__init__(parent)
            self._n = norad

        def run(self):
            self.done.emit(self._n, transmitters(self._n))

    class _Doppler(QWidget):
        def __init__(self, cfg, source, parent):
            super().__init__(parent)
            self._cfg = cfg
            self._source = source              # callable → (tles, lat, lon)
            self._tx: dict = {}                # norad → [zenders]
            self._thread = None
            self._last_tuned = None
            lay = QVBoxLayout(self)
            lay.setContentsMargins(6, 4, 6, 4)
            lay.setSpacing(4)
            row = QHBoxLayout()
            self._sat = QComboBox()
            self._sat.currentIndexChanged.connect(self._on_sat)
            row.addWidget(self._sat, 1)
            self._tune = QPushButton(tr("dop.tune"))
            self._tune.clicked.connect(lambda: self._tune_selected(force=True))
            row.addWidget(self._tune)
            self._follow = QCheckBox(tr("dop.follow"))
            row.addWidget(self._follow)
            lay.addLayout(row)
            self._status = QLabel(tr("dop.none"))
            self._status.setWordWrap(True)
            self._status.setStyleSheet(f"color: {TEXT_DIM}; font-size: 8pt;")
            lay.addWidget(self._status)
            self._tbl = _table([tr("dop.col.desc"), tr("dop.col.mode"), tr("dop.col.down"),
                                tr("dop.col.down_now"), tr("dop.col.up_now")], stretch=0)
            self._tbl.setSelectionMode(self._tbl.SelectionMode.SingleSelection)
            self._tbl.setSelectionBehavior(self._tbl.SelectionBehavior.SelectRows)
            self._tbl.setToolTip(tr("dop.table_tip"))
            lay.addWidget(self._tbl, 1)
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._tick)
            self._timer.start(1000)
            self._sats_sig = None

        def set_cfg(self, cfg):
            self._cfg = cfg

        def _sats(self) -> dict:
            try:
                tles, _lat, _lon = self._source()
                return tles
            except Exception:
                return {}

        def _sync_sats(self, tles: dict):
            sig = tuple(sorted(tles))
            if sig == self._sats_sig:
                return
            self._sats_sig = sig
            cur = self._sat.currentText()
            self._sat.blockSignals(True)
            self._sat.clear()
            for name in sig:
                self._sat.addItem(name.split("(")[0].strip()[:24], name)
            i = self._sat.findText(cur)
            self._sat.setCurrentIndex(max(0, i))
            self._sat.blockSignals(False)
            self._on_sat()

        def _on_sat(self, *_):
            name = self._sat.currentData()
            tles = self._sats()
            if not name or name not in tles:
                return
            n = norad_of(tles[name][0])
            if n is None or n in self._tx or self._thread is not None:
                return
            th = _TxThread(n, self)
            th.done.connect(self._on_tx)
            th.finished.connect(th.deleteLater)
            th.finished.connect(lambda: setattr(self, "_thread", None))
            self._thread = th
            th.start()

        def _on_tx(self, norad: int, items: list):
            self._tx[norad] = items
            self._tick()

        def _tick(self):
            if not self.isVisible():
                return
            tles = self._sats()
            self._sync_sats(tles)
            name = self._sat.currentData()
            if not name or name not in tles:
                self._status.setText(tr("dop.none"))
                self._tbl.setRowCount(0)
                return
            l1, l2 = tles[name]
            lat, lon = self._cfg.qth_lat, self._cfg.qth_lon
            now = _dt.datetime.now(_dt.timezone.utc)
            try:
                rr, az, el = range_rate(l1, l2, lat, lon, now)
            except Exception:
                return
            from .sat_passes import compass
            vis = el >= 0
            self._status.setText(tr("dop.status_up" if vis else "dop.status_down",
                                    el=f"{el:.0f}", az=f"{az:.0f}", dir=compass(az),
                                    v=f"{rr:+.2f}"))
            items = self._tx.get(norad_of(l1), None)
            if items is None:
                self._tbl.setRowCount(0)
                return
            if not items:
                self._status.setText(self._status.text() + "  ·  " + tr("dop.no_tx"))
            tb = self._tbl
            with bulk_fill(tb):
                if tb.rowCount() != len(items):
                    tb.setRowCount(len(items))
                for i, t in enumerate(items):
                    dn = downlink(t["down"], rr)
                    up = uplink(t["up"], rr) if t["up"] else None
                    col = TEXT_H1 if vis else TEXT_DIM
                    _set_text(tb, i, 0, t["desc"], col)
                    _set_text(tb, i, 1, t["mode"], TEXT_BODY)
                    _set_text(tb, i, 2, f"{t['down'] / 1e6:.4f}", TEXT_DIM, align=Qt.AlignRight)
                    _set_text(tb, i, 3, f"{dn / 1e6:.5f}", col, bold=vis, align=Qt.AlignRight)
                    _set_text(tb, i, 4, "—" if up is None else f"{up / 1e6:.5f}", col,
                              align=Qt.AlignRight)
            if self._follow.isChecked() and vis and int(time.time()) % 2 == 0:
                self._tune_selected(force=False)

        def _tune_selected(self, force: bool):
            from .panels5 import _cat_send
            tles = self._sats()
            name = self._sat.currentData()
            row = self._tbl.currentRow()
            items = self._tx.get(norad_of(tles[name][0]) if name in tles else None) or []
            if not (0 <= row < len(items)):
                if force:
                    self._status.setText(tr("dop.pick_row"))
                return
            l1, l2 = tles[name]
            rr, _az, _el = range_rate(l1, l2, self._cfg.qth_lat, self._cfg.qth_lon,
                                      _dt.datetime.now(_dt.timezone.utc))
            hz = int(round(downlink(items[row]["down"], rr) / 10) * 10)
            if not force and self._last_tuned is not None and abs(hz - self._last_tuned) < 50:
                return
            ok, msg = _cat_send(hz, cat_mode(items[row]["mode"]))
            self._last_tuned = hz if ok else None
            if force or not ok:
                self._status.setText(tr("dop.tuned", f=f"{hz / 1e6:.5f}") if ok else msg)

    return _Doppler
