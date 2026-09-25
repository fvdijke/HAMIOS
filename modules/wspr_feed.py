"""
WSPR (Weak Signal Propagation Reporter) Live Data Feed

Haalt echte WSPR-spots op via wspr.live (publieke ClickHouse-database met alle
WSPRnet-spots). De oude wsprnet.org-API bestaat niet meer (HTTP 404).

Alleen spots die iets zeggen over propagatie vanaf de eigen QTH:
  → uitgaand: zender binnen RADIUS_KM van de QTH, elders gehoord
  ← inkomend: ontvanger binnen RADIUS_KM van de QTH, hoort een verre zender

Geen nepdata: bij een storing blijven de laatste echte spots staan en wordt
een fout gemeld. Poll-interval 5 minuten (WSPR-cyclus = 2 min; server sparen).

Usage:
    feed = WSPRFeed(qth_lat=52.0, qth_lon=5.0)
    feed.start()
    feed.stop()
"""

import json
import math
import threading
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Dict, List

from PySide6.QtCore import QThread, Signal

WSPR_LIVE_URL   = "https://db1.wspr.live/"
RADIUS_KM       = 300      # "eigen regio" rond de QTH
WINDOW_MIN      = 30       # spots van de laatste N minuten
MIN_DISTANCE_KM = 100      # lokale/zelf-spots zeggen niets over propagatie
MAX_ROWS        = 500
POLL_SECONDS    = 300
_UA = "HAMIOS/5.8 (+https://hamios.space; WSPR propagation monitor)"

# wspr.live 'band' (MHz, afgerond) → bandnaam
BAND_NAMES = {
    -1: "2200m", 0: "630m", 1: "160m", 3: "80m", 5: "60m", 7: "40m",
    10: "30m", 14: "20m", 18: "17m", 21: "15m", 24: "12m", 28: "10m",
    40: "8m", 50: "6m", 70: "4m", 144: "2m", 432: "70cm", 1296: "23cm",
}


def build_query(lat: float, lon: float) -> str:
    """ClickHouse-query: recente spots van/naar de regio rond (lat, lon)."""
    r_m = int(RADIUS_KM * 1000)
    return (
        "SELECT time, band, frequency, tx_sign, tx_loc, rx_sign, rx_loc, "
        "snr, drift, power, distance, azimuth, rx_azimuth, "
        f"greatCircleDistance(tx_lon, tx_lat, {lon:.4f}, {lat:.4f}) < {r_m} AS tx_near "
        "FROM wspr.rx "
        f"WHERE time > now() - INTERVAL {WINDOW_MIN} MINUTE "
        f"AND distance >= {MIN_DISTANCE_KM} "
        f"AND (greatCircleDistance(tx_lon, tx_lat, {lon:.4f}, {lat:.4f}) < {r_m} "
        f"OR greatCircleDistance(rx_lon, rx_lat, {lon:.4f}, {lat:.4f}) < {r_m}) "
        f"ORDER BY time DESC LIMIT {MAX_ROWS} FORMAT JSON"
    )


def parse_rows(rows: List[Dict]) -> List[Dict]:
    """wspr.live-rijen → records voor de tabel (en later het propagatie-advies)."""
    out = []
    for r in rows:
        try:
            outgoing = bool(int(r.get("tx_near", 0)))
            # Verre kant van het pad = de 'andere' station
            remote_call = r["rx_sign"] if outgoing else r["tx_sign"]
            remote_grid = r["rx_loc"]  if outgoing else r["tx_loc"]
            # Peilrichting gezien vanaf de eigen regio naar het verre station
            az = int(r["azimuth"]) if outgoing else int(r["rx_azimuth"])
            ts = datetime.strptime(r["time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            band_mhz = int(r["band"])
            out.append({
                "direction":   "out" if outgoing else "in",
                "call_sign":   remote_call,
                "grid":        remote_grid,
                "tx_call":     r["tx_sign"],
                "tx_grid":     r["tx_loc"],
                "rx_call":     r["rx_sign"],
                "rx_grid":     r["rx_loc"],
                "band":        BAND_NAMES.get(band_mhz, f"{band_mhz} MHz"),
                "frequency":   int(r["frequency"]) / 1e6,     # MHz
                "snr":         int(r["snr"]),
                "drift":       int(r["drift"]),
                "power":       f"{int(r['power'])} dBm",
                "distance":    int(r["distance"]),
                "azimuth":     az,
                "time":        ts.isoformat(),
            })
        except (KeyError, TypeError, ValueError):
            continue
    return out


class WSPRFeed(QThread):
    """WSPR live data fetcher running in background thread."""

    data_updated   = Signal(list)   # records (alleen echte data)
    error_occurred = Signal(str)    # foutmelding; laatste data blijft geldig

    def __init__(self, qth_lat: float = 52.0, qth_lon: float = 5.0, parent=None):
        super().__init__(parent)
        self.qth_lat = qth_lat
        self.qth_lon = qth_lon
        self._running = False
        self._cache: List[Dict] = []
        self._cache_lock = threading.Lock()
        self._update_interval = POLL_SECONDS
        self._wake = threading.Event()

    def set_update_interval(self, seconds: int):
        """Interval in seconden (minimaal 120 s — één WSPR-cyclus is 2 min)."""
        self._update_interval = max(120, int(seconds))

    def set_qth(self, lat: float, lon: float):
        """Nieuwe QTH → direct opnieuw ophalen."""
        if (lat, lon) != (self.qth_lat, self.qth_lon):
            self.qth_lat, self.qth_lon = lat, lon
            self._wake.set()

    def run(self):
        self._running = True
        while self._running:
            try:
                records = self._fetch()
                with self._cache_lock:
                    self._cache = records
                self.data_updated.emit(records)
            except Exception as e:
                # Géén nepdata: laatste echte data blijft staan
                self.error_occurred.emit(str(e)[:120])
            self._wake.clear()
            self._wake.wait(self._update_interval)

    def stop(self):
        self._running = False
        self._wake.set()
        self.wait(3000)

    def records(self) -> List[Dict]:
        with self._cache_lock:
            return list(self._cache)

    def _fetch(self) -> List[Dict]:
        url = WSPR_LIVE_URL + "?query=" + urllib.parse.quote(
            build_query(self.qth_lat, self.qth_lon))
        req = urllib.request.Request(url, headers={"User-Agent": _UA})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return parse_rows(data.get("data", []))

    @staticmethod
    def compute_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Great-circle distance in km."""
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp, dl = p2 - p1, math.radians(lon2 - lon1)
        a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
        return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
