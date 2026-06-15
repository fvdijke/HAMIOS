"""
WSPR (Weak Signal Propagation Reporter) Live Data Feed

Fetches real-time QSO records from wsprnet.org API.
Thread-safe caching with configurable update interval.

Usage:
    feed = WSPRFeed(qth_lat=52.0, qth_lon=5.0)
    feed.start()
    records = feed.get_recent_qsos(hours=1)
    feed.stop()
"""

import threading
import time
import json
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from PySide6.QtCore import QThread, Signal


class WSPRFeed(QThread):
    """WSPR live data fetcher running in background thread."""

    data_updated = Signal(list)  # Emits list of QSO records
    error_occurred = Signal(str)  # Emits error message

    def __init__(self, qth_lat: float = 52.0, qth_lon: float = 5.0, parent=None):
        super().__init__(parent)
        self.qth_lat = qth_lat
        self.qth_lon = qth_lon
        self._running = False
        self._cache: List[Dict] = []
        self._cache_lock = threading.Lock()
        self._update_interval = 30  # seconds

    def set_update_interval(self, seconds: int):
        """Set update interval (minimum 30s to avoid API overload)."""
        self._update_interval = max(30, seconds)

    def run(self):
        """Main thread loop: fetch WSPR data periodically."""
        self._running = True
        while self._running:
            try:
                records = self._fetch_wspr_data()
                with self._cache_lock:
                    self._cache = records
                self.data_updated.emit(records)
            except Exception as e:
                # Fallback to mock data if API fails (for testing/offline mode)
                records = _mock_wspr_data()
                with self._cache_lock:
                    self._cache = records
                self.data_updated.emit(records)
                self.error_occurred.emit(f"WSPR offline, using mock data: {str(e)}")

            # Sleep in small chunks so stop() responds quickly
            for _ in range(self._update_interval):
                if not self._running:
                    break
                time.sleep(1)

    def stop(self):
        """Stop the background thread gracefully."""
        self._running = False
        self.wait()

    def get_recent_qsos(self, hours: int = 1) -> List[Dict]:
        """Get cached QSO records from last N hours."""
        with self._cache_lock:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
            result = []
            for record in self._cache:
                try:
                    ts = datetime.fromisoformat(record.get("time", "").replace("Z", "+00:00"))
                    if ts >= cutoff:
                        result.append(record)
                except (ValueError, AttributeError):
                    pass
            return result

    def _fetch_wspr_data(self) -> List[Dict]:
        """
        Fetch latest WSPR QSO records from wsprnet.org API.

        Returns: List of QSO dicts with keys:
            - call_sign, grid, band, frequency, snr, drift, power, reporter, rg_grid,
            - distance, azimuth, time (ISO format)
        """
        try:
            import urllib.request as urlreq
            import urllib.error as urlerror

            # wsprnet.org API endpoint (public, no auth required)
            # Returns JSON with recent QSO records
            url = "https://wsprnet.org/drupal/wsprnet/api/v2/spots"
            headers = {
                "User-Agent": "HAMIOS/5.3 (WSPR Monitor)",
                "Accept": "application/json",
            }

            req = urlreq.Request(url, headers=headers)

            # Timeout after 10s
            with urlreq.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))

                # Parse response
                # Expected format: list of spots or {"spots": [...]}
                spots = data if isinstance(data, list) else data.get("spots", [])

                # Normalize field names and add computed fields
                qsos = []
                for spot in spots[:200]:  # Limit to last 200 spots
                    qso = {
                        "call_sign": spot.get("reporter", "?"),
                        "grid": spot.get("reporter_grid", "?"),
                        "band": spot.get("band", "?"),
                        "frequency": float(spot.get("frequency", 0)),
                        "snr": int(spot.get("snr", 0)),
                        "drift": int(spot.get("drift", 0)),
                        "power": spot.get("power", "?"),
                        "tx_call": spot.get("spotting_call", "?"),
                        "tx_grid": spot.get("spotting_grid", "?"),
                        "distance": int(spot.get("distance", 0)),
                        "azimuth": int(spot.get("azimuth", 0)),
                        "time": spot.get("time", datetime.now(timezone.utc).isoformat()),
                    }
                    qsos.append(qso)

                return qsos

        except urlerror.URLError as e:
            raise Exception(f"Network error: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"JSON parse error: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error: {e}")

    @staticmethod
    def compute_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Great-circle distance in km between two QTH coords.
        (Used for filtering nearby WSPR spots)
        """
        import math

        R = 6371  # Earth radius in km
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def filter_by_distance(self, max_distance_km: int = 5000) -> List[Dict]:
        """Filter cached QSOs within N km of QTH."""
        with self._cache_lock:
            result = []
            for qso in self._cache:
                try:
                    # Distance is pre-computed by wsprnet API based on their QTH
                    # but we could recompute if needed:
                    dist = qso.get("distance", 0)
                    if dist <= max_distance_km:
                        result.append(qso)
                except (ValueError, KeyError):
                    pass
            return result


# ── Mock for testing (when API is unavailable) ───────────────────────────


def _mock_wspr_data() -> List[Dict]:
    """Generate mock WSPR data for testing (when API unavailable)."""
    import random

    calls = ["W1AW", "G4RZO", "F6FLT", "ON6YLQ", "EA1WX"]
    bands = ["160m", "80m", "40m", "20m", "15m", "10m", "6m"]

    data = []
    for i in range(50):
        call = random.choice(calls)
        band = random.choice(bands)
        freq = {
            "160m": 1.8368,
            "80m": 3.5686,
            "40m": 7.0386,
            "20m": 14.0956,
            "15m": 21.0956,
            "10m": 28.1246,
            "6m": 50.2930,
        }[band]

        data.append(
            {
                "call_sign": call,
                "grid": "JO20" if call.startswith("W") else "JO" + str(random.randint(10, 99)),
                "band": band,
                "frequency": freq + random.uniform(-0.1, 0.1),
                "snr": random.randint(-30, 0),
                "drift": random.randint(-5, 5),
                "power": f"{random.choice([0.5, 1, 2, 5, 10])}W",
                "tx_call": random.choice(["JO21AA", "JO20AA", "JN99AA"]),
                "tx_grid": "JO21AA",
                "distance": random.randint(500, 5000),
                "azimuth": random.randint(0, 360),
                "time": (
                    datetime.now(timezone.utc) - timedelta(minutes=random.randint(0, 30))
                ).isoformat(),
            }
        )

    return data
