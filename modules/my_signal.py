"""
HAMIOS — "Waar word ik gehoord?"

Haalt op waar het eigen signaal (roepnaam uit Instellingen) het afgelopen uur
ontvangen is:
  • PSKReporter — FT8/FT4/CW/… ontvangstmeldingen (senderCallsign = eigen call)
  • wspr.live   — WSPR-spots van de eigen baken (tx_sign = eigen call)

Per band: aantal ontvangers, verste afstand en beste SNR; daaronder de
afzonderlijke meldingen. Een klik op een regel toont het pad op de kaart.
Ververst elke 5 minuten (PSKReporter vraagt om niet vaker te bevragen).
"""

from __future__ import annotations

import datetime as _dt
import json
import urllib.parse
import urllib.request

from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from .extra_panels import _item, _table
from .i18n import tr
from .theme import TEXT_BODY, TEXT_DIM, TEXT_H1
from .version import USER_AGENT

POLL_MS = 5 * 60_000
WINDOW_S = 3600
_PSK_URL = ("https://pskreporter.info/cgi-bin/pskquery5.pl?encap=0&callback=_&statistics=0"
            "&noactive=1&nolocator=1&rronly=1&appcontact=HAMIOS5"
            "&flowStartSeconds=-{win}&senderCallsign={call}")
_WSPR_URL = "https://db1.wspr.live/?query="


def _clean_call(call: str) -> str:
    """Alleen letters, cijfers en '/': de roepnaam komt in een URL en een query."""
    return "".join(ch for ch in (call or "").upper() if ch.isalnum() or ch == "/")[:20]


def fetch_reports(call: str, qth: tuple[float, float]) -> list[dict]:
    """Ontvangstmeldingen van het eigen signaal (laatste uur), nieuwste eerst.
    Gooit een uitzondering als beide bronnen falen."""
    from .advisor import band_of
    from .layers import _maidenhead_to_latlon
    from .propagation import _dist_km
    call = _clean_call(call)
    if not call:
        return []
    out, errors = [], 0

    # PSKReporter
    try:
        req = urllib.request.Request(_PSK_URL.format(win=WINDOW_S, call=urllib.parse.quote(call)),
                                     headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8", errors="replace"))
        for it in data.get("receptionReport", []) or []:
            pos = _maidenhead_to_latlon(str(it.get("receiverLocator", "")))
            khz = float(it.get("frequency", 0) or 0) / 1000
            if pos is None or not khz:
                continue
            out.append({
                "src": "PSK", "rx": str(it.get("receiverCallsign", "")),
                "lat": pos[0], "lon": pos[1], "km": int(_dist_km(qth[0], qth[1], *pos)),
                "band": band_of(khz) or f"{khz / 1000:.1f} MHz", "khz": khz,
                "snr": it.get("sNR"), "mode": str(it.get("mode", "")),
                "t": int(it.get("flowStartSeconds", 0) or 0)})
    except Exception:
        errors += 1

    # wspr.live (WSPR-baken)
    try:
        q = ("SELECT toUnixTimestamp(time) AS t, frequency, rx_sign, rx_loc, distance, snr "
             f"FROM wspr.rx WHERE tx_sign = '{call}' "
             f"AND time > now() - INTERVAL {WINDOW_S // 60} MINUTE "
             "ORDER BY time DESC LIMIT 300 FORMAT JSON")
        req = urllib.request.Request(_WSPR_URL + urllib.parse.quote(q),
                                     headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8", errors="replace"))
        for it in data.get("data", []) or []:
            pos = _maidenhead_to_latlon(str(it.get("rx_loc", "")))
            khz = float(it.get("frequency", 0) or 0) / 1000
            if pos is None or not khz:
                continue
            out.append({
                "src": "WSPR", "rx": str(it.get("rx_sign", "")),
                "lat": pos[0], "lon": pos[1], "km": int(it.get("distance") or 0),
                "band": band_of(khz) or f"{khz / 1000:.1f} MHz", "khz": khz,
                "snr": it.get("snr"), "mode": "WSPR", "t": int(it.get("t", 0) or 0)})
    except Exception:
        errors += 1

    if errors == 2:
        raise OSError("PSKReporter / wspr.live")
    out.sort(key=lambda r: -r["t"])
    return out


def summarize(reports: list[dict]) -> list[tuple]:
    """[(band, ontvangers, verste km, beste SNR)] — banden van laag naar hoog."""
    from .advisor import _BAND_ORDER
    per: dict = {}
    for r in reports:
        d = per.setdefault(r["band"], {"rx": set(), "km": 0, "snr": None})
        d["rx"].add(r["rx"])
        d["km"] = max(d["km"], r["km"])
        if r["snr"] is not None:
            d["snr"] = r["snr"] if d["snr"] is None else max(d["snr"], r["snr"])
    order = {b: i for i, b in enumerate(_BAND_ORDER)}
    return [(b, len(d["rx"]), d["km"], d["snr"])
            for b, d in sorted(per.items(), key=lambda kv: order.get(kv[0], 99))]


class _FetchThread(QThread):
    done = Signal(object)             # list, of None bij een fout

    def __init__(self, call, qth, parent=None):
        super().__init__(parent)
        self._args = (call, qth)

    def run(self):
        try:
            self.done.emit(fetch_reports(*self._args))
        except Exception:
            self.done.emit(None)


class MySignalWidget(QWidget):
    """Paneel 'Mijn signaal'."""

    path_requested = Signal(float, float, str)     # lat, lon, label → kaart

    def __init__(self, cfg=None, parent=None):
        super().__init__(parent)
        self._cfg = cfg
        self._reports: list = []
        self._thread = None
        self._last_call = ""
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 4, 6, 4)
        lay.setSpacing(4)
        self._status = QLabel(tr("mysig.waiting"))
        self._status.setWordWrap(True)
        self._status.setStyleSheet(f"color: {TEXT_DIM}; font-size: 8pt;")
        lay.addWidget(self._status)
        self._sum = _table([tr("mysig.col.band"), tr("mysig.col.rx"),
                            tr("mysig.col.far"), tr("mysig.col.snr")])
        self._sum.setMaximumHeight(150)
        lay.addWidget(self._sum)
        self._tbl = _table([tr("mysig.col.time"), tr("mysig.col.band"), tr("mysig.col.call"),
                            "km", "SNR", tr("mysig.col.mode")], stretch=2)
        self._tbl.setToolTip(tr("mysig.table_tip"))
        self._tbl.cellClicked.connect(self._on_row)
        lay.addWidget(self._tbl, 1)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(POLL_MS)
        QTimer.singleShot(8000, self.refresh)

    def set_cfg(self, cfg):
        self._cfg = cfg
        if _clean_call(getattr(cfg, "callsign", "")) != self._last_call:
            self.refresh()

    def refresh(self):
        call = _clean_call(getattr(self._cfg, "callsign", "") if self._cfg else "")
        self._last_call = call
        if not call:
            self._status.setText(tr("mysig.no_call"))
            self._sum.setRowCount(0)
            self._tbl.setRowCount(0)
            return
        if self._thread is not None:
            return
        qth = (self._cfg.qth_lat, self._cfg.qth_lon)
        th = _FetchThread(call, qth, self)
        th.done.connect(self._on_data)
        th.finished.connect(th.deleteLater)
        th.finished.connect(lambda: setattr(self, "_thread", None))
        self._thread = th
        self._status.setText(tr("mysig.loading", call=call))
        th.start()

    def _on_data(self, reports):
        call = self._last_call
        if reports is None:
            self._status.setText(tr("mysig.error"))
            return                       # vorige meldingen blijven staan
        self._reports = reports
        now = _dt.datetime.now().strftime("%H:%M")
        if not reports:
            self._status.setText(tr("mysig.none", call=call, t=now))
        else:
            far = max(reports, key=lambda r: r["km"])
            self._status.setText(tr("mysig.status", call=call, n=len({r["rx"] for r in reports}),
                                    far=far["km"], rx=far["rx"], t=now))
        rows = summarize(reports)
        self._sum.setRowCount(len(rows))
        for i, (band, n, km, snr) in enumerate(rows):
            self._sum.setItem(i, 0, _item(band, TEXT_H1, bold=True))
            self._sum.setItem(i, 1, _item(str(n), align=Qt.AlignRight))
            self._sum.setItem(i, 2, _item(f"{km:,} km".replace(",", "."), align=Qt.AlignRight))
            self._sum.setItem(i, 3, _item("—" if snr is None else f"{snr:+d} dB", align=Qt.AlignRight))
        shown = reports[:200]
        self._tbl.setRowCount(len(shown))
        for i, r in enumerate(shown):
            t = _dt.datetime.fromtimestamp(r["t"]).strftime("%H:%M") if r["t"] else "—"
            self._tbl.setItem(i, 0, _item(t, TEXT_DIM))
            self._tbl.setItem(i, 1, _item(r["band"]))
            self._tbl.setItem(i, 2, _item(r["rx"], TEXT_H1))
            self._tbl.setItem(i, 3, _item(str(r["km"]), align=Qt.AlignRight))
            self._tbl.setItem(i, 4, _item("—" if r["snr"] is None else f"{r['snr']:+d}",
                                          align=Qt.AlignRight))
            self._tbl.setItem(i, 5, _item(r["mode"], TEXT_BODY))

    def _on_row(self, row: int, _col: int):
        if 0 <= row < len(self._reports):
            r = self._reports[row]
            self.path_requested.emit(r["lat"], r["lon"], f"{r['rx']} · {r['band']}")

    def reports(self) -> list:
        return list(self._reports)

