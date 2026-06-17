"""
HAMIOS v5 — Real-time kaartlagen (PySide6 QGraphicsItem)

Lagen:
  LightningLayer  z=5   Blitzortung WebSocket, fade-animatie
  SatelliteLayer  z=4   Orbitpaden + posities (geen externe library)
  DXSpotsLayer    z=6   DX cluster spots met bandkleur
"""

import datetime
import json
import math
import os
import re
import threading
import time
import urllib.request

from PySide6.QtCore import QObject, QRectF, QPointF, QTimer, Signal, Qt, QThread
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QFont
from PySide6.QtWidgets import QGraphicsItem

# Kaartafmetingen (moet overeenkomen met mapview.py)
MAP_W, MAP_H = 4096, 2048


def _play_tick():
    """Geigerteller-tick: één korte puls."""
    try:
        import winsound
        winsound.Beep(2800, 5)
    except Exception:
        pass


def _play_sat_enter():
    """Één hoge ping: satelliet komt QTH-zone binnen."""
    try:
        import winsound
        winsound.Beep(1400, 180)
    except Exception:
        pass


def _play_sat_exit():
    """Één lage ping: satelliet verlaat QTH-zone."""
    try:
        import winsound
        winsound.Beep(600, 180)
    except Exception:
        pass


class _SatSignaller(QObject):
    zone_changed = Signal(str, bool)   # (naam, in_zone)

from ._appdir import APP_DIR as _HERE
_TLE_CACHE = os.path.join(_HERE, "config", "hamios_tle.json")

TLE_GROUPS = {
    "Amateur": {
        "primary": "https://celestrak.org/NORAD/elements/gp.php?GROUP=amateur&FORMAT=tle",
        "fallback": "https://www.amsat.org/tle/dailytle.txt",
    },
    "ISS": {
        "primary": "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=tle",
        "fallback": "https://www.amsat.org/tle/dailytle.txt",
    },
    "Weather": "https://celestrak.org/NORAD/elements/gp.php?GROUP=weather&FORMAT=tle",
    "CubeSat": "https://celestrak.org/NORAD/elements/gp.php?GROUP=cubesat&FORMAT=tle",
}


def _xy(lat: float, lon: float) -> QPointF:
    return QPointF((lon + 180) / 360 * MAP_W, (90 - lat) / 180 * MAP_H)


# ── TLE hulpfuncties ──────────────────────────────────────────────────────────

def parse_tle_text(text: str) -> list[tuple[str, str, str]]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    sats, i = [], 0
    while i + 2 < len(lines):
        name, l1, l2 = lines[i], lines[i+1], lines[i+2]
        if l1.startswith("1 ") and l2.startswith("2 "):
            sats.append((name, l1, l2))
            i += 3
        else:
            i += 1
    return sats


def load_tle_cache() -> dict:
    try:
        if os.path.exists(_TLE_CACHE):
            with open(_TLE_CACHE, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_tle_cache(data: dict):
    try:
        with open(_TLE_CACHE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:
        pass


def fetch_tle_group(url_or_config) -> list[tuple[str, str, str]]:
    """Fetch TLE group from primary URL, fallback to backup if available."""
    # Handle both string URLs (legacy) and dict with primary/fallback
    is_iss_group = False
    if isinstance(url_or_config, dict):
        urls = [url_or_config.get("primary"), url_or_config.get("fallback")]
        # Check if this is ISS group based on primary URL
        is_iss_group = "CATNR=25544" in str(urls[0])
    else:
        urls = [url_or_config]

    for url in urls:
        if not url:
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "HAMIOS/5.4"})
            with urllib.request.urlopen(req, timeout=15) as r:
                text = r.read().decode("utf-8", errors="replace")
                sats = parse_tle_text(text)
                if sats:
                    # If this is ISS group and we got results from AMSAT fallback,
                    # filter to only ISS (NORAD catalog number 25544)
                    if is_iss_group and url == url_or_config.get("fallback"):
                        sats = [s for s in sats if "ISS" in s[0]]
                    if sats:
                        return sats
        except Exception:
            continue

    return []


class TleFetchThread(QThread):
    """Download alle TLE-groepen van CelesTrak en sla op als cache."""
    progress = Signal(str)   # groepsnaam die nu geladen wordt
    done     = Signal(dict)  # volledige cache na afronden

    def run(self):
        cache = {}
        for group, url in TLE_GROUPS.items():
            self.progress.emit(group)
            sats = fetch_tle_group(url)
            if sats:
                cache[group] = [[n, l1, l2] for n, l1, l2 in sats]

        # If any data was fetched, save it
        if cache:
            save_tle_cache(cache)
        else:
            # If all fetches failed, load cached data
            cache = load_tle_cache()

        self.done.emit(cache)


# ── Orbital mechanics (geen externe library nodig) ────────────────────────────

def _sgp4_latlon(line1: str, line2: str,
                 offset_min: float = 0.0) -> tuple[float, float, float] | None:
    """Vereenvoudigde TLE-propagator. Nauwkeurigheid ~50 km (voldoende voor kaart)."""
    try:
        ep  = line1[18:32].strip()
        yr2 = int(ep[:2])
        yr  = 2000 + yr2 if yr2 < 57 else 1900 + yr2
        epoch = (datetime.datetime(yr, 1, 1, tzinfo=datetime.timezone.utc)
                 + datetime.timedelta(days=float(ep[2:]) - 1))

        incl = math.radians(float(line2[8:16]))
        raan = math.radians(float(line2[17:25]))
        ecc  = float("0." + line2[26:33])
        argp = math.radians(float(line2[34:42]))
        M0   = math.radians(float(line2[43:51]))
        n    = float(line2[52:63])          # omwentelingen/dag

        now   = datetime.datetime.now(datetime.timezone.utc)
        t_min = (now - epoch).total_seconds() / 60.0 + offset_min
        n_rm  = n * 2 * math.pi / (24 * 60)
        n_rs  = n * 2 * math.pi / 86400
        a     = (398600.4418 / n_rs**2) ** (1/3)
        M     = (M0 + n_rm * t_min) % (2 * math.pi)

        E = M
        for _ in range(10):
            E = M + ecc * math.sin(E)

        cosE = math.cos(E)
        nu   = math.atan2(math.sqrt(1 - ecc**2) * math.sin(E), cosE - ecc)
        r    = a * (1 - ecc * cosE)
        xp, yp = r * math.cos(nu), r * math.sin(nu)

        cr, sr = math.cos(raan), math.sin(raan)
        co, so = math.cos(argp), math.sin(argp)
        ci, si = math.cos(incl), math.sin(incl)
        x_eci = (cr*co - sr*so*ci)*xp + (-cr*so - sr*co*ci)*yp
        y_eci = (sr*co + cr*so*ci)*xp + (-sr*so + cr*co*ci)*yp
        z_eci =          si*so    *xp +          si*co    *yp

        J2000 = datetime.datetime(2000, 1, 1, 12, tzinfo=datetime.timezone.utc)
        jd    = (now - J2000).total_seconds() / 86400 + offset_min / 1440.0
        g     = math.radians((280.46061837 + 360.98564736629 * jd) % 360)
        xe    =  x_eci * math.cos(g) + y_eci * math.sin(g)
        ye    = -x_eci * math.sin(g) + y_eci * math.cos(g)
        ze    =  z_eci

        lat = math.degrees(math.asin(max(-1.0, min(1.0, ze / r))))
        lon = math.degrees(math.atan2(ye, xe))
        return lat, lon, r - 6371.0
    except Exception:
        return None


def _calc_sat_path(line1: str, line2: str,
                   back_min: int = 60, fwd_min: int = 720,
                   step: float = 0.5) -> tuple[list, list]:
    """Past-paden (1 min stap) en toekomst (step min). None = antimeridiaanbreuk."""
    def segment(offsets):
        pts, prev = [], None
        for off in offsets:
            r = _sgp4_latlon(line1, line2, off)
            if r is None:
                continue
            lat, lon, _ = r
            if prev is not None and abs(lon - prev) > 180:
                pts.append(None)
            pts.append((lat, lon))
            prev = lon
        return pts

    past = segment([-i for i in range(back_min, 0, -1)])
    fwd  = segment([i * step for i in range(0, int(fwd_min / step) + 1)])
    return past, fwd


# ── Blitzortung parser ────────────────────────────────────────────────────────

def _parse_blitzortung(msg) -> tuple[float | None, float | None]:
    if isinstance(msg, bytes):
        msg = msg.decode("utf-8", errors="replace")

    # Methode 1: standaard JSON
    try:
        d = json.loads(msg)
        lat = d.get("lat") or d.get("y")
        lon = d.get("lon") or d.get("x")
        if lat is not None and lon is not None:
            return float(lat), float(lon)
    except Exception:
        pass

    # Methode 2: positionale floats (≥3 decimalen)
    nums = re.findall(r'([+-]?\d{1,3}\.\d{3,})', msg)
    if len(nums) >= 2:
        lat, lon = float(nums[0]), float(nums[1])
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return lat, lon

    # Methode 3: regex op lat/lon sleutels
    lm = re.search(r'"lat[^\d\-+]*([+-]?\d+\.\d+)', msg)
    xm = re.search(r'"lon[^\d\-+]*([+-]?\d+\.\d+)', msg)
    if lm and xm:
        return float(lm.group(1)), float(xm.group(1))

    return None, None


# ── Lightning Worker ──────────────────────────────────────────────────────────

class LightningWorker(QObject):
    """Achtergrond WebSocket-client voor Blitzortung (websocket-client library)."""
    strike  = Signal(float, float)   # lat, lon
    status  = Signal(str)            # "live" | "disc" | "no_lib"

    _URL = "wss://ws1.blitzortung.org:443/"

    def __init__(self):
        super().__init__()
        self._running = False
        self._ws      = None   # actieve WebSocketApp-instantie

    def start(self):
        self._running = True
        threading.Thread(target=self._run, daemon=True, name="blitz-ws").start()

    def stop(self):
        """Stop de worker: sluit de actieve WebSocket zodat run_forever() direct terugkeert."""
        self._running = False
        ws = self._ws
        if ws is not None:
            try:
                ws.close()
            except Exception:
                pass
        self._ws = None

    def _run(self):
        try:
            import websocket
        except ImportError:
            self.status.emit("no_lib")
            return

        while self._running:
            try:
                ws = websocket.WebSocketApp(
                    self._URL,
                    on_open=lambda w: (w.send('{"a": 111}'), self.status.emit("live")),
                    on_message=lambda w, m: self._on_msg(m),
                    on_close=lambda w, c, t: self.status.emit("disc"),
                )
                self._ws = ws
                ws.run_forever(reconnect=5)
                self._ws = None
            except Exception:
                self._ws = None
                if self._running:
                    time.sleep(10)

    def _on_msg(self, msg):
        lat, lon = _parse_blitzortung(msg)
        if lat is not None:
            self.strike.emit(lat, lon)


# ── Lightning Layer ───────────────────────────────────────────────────────────

class LightningLayer(QGraphicsItem):
    """Real-time Blitzortung inslagen met fade-animatie."""

    def __init__(self):
        super().__init__()
        self.setZValue(5)
        self._strikes: list = []   # (x, y, t_mono)
        self._flashes: list  = []  # (x, y, t_mono)  korte ring
        self._lock = threading.Lock()
        self.fade_seconds = 600
        self._anim_scale = 2.0    # schaal voor ring en stip (default 2.0 voor MAP_W=4096)
        self._font_size = 7       # lettergrootte labels (pt)
        self._cfg = None   # AppConfig — voor piepje-instellingen

        self._worker = LightningWorker()
        self._worker.strike.connect(self._on_strike)
        self._worker.start()

        # Opruim-timer: verwijdert verouderde inslagen (instelbaar interval)
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(500)

        # Animatie-timer: 20 fps voor vloeiende ring-expansie
        # Stopt zichzelf als er geen actieve ringen zijn (CPU-vriendelijk)
        self._anim_timer = QTimer()
        self._anim_timer.timeout.connect(self._anim_tick)
        self._anim_timer.start(50)

    @property
    def status_signal(self) -> Signal:
        return self._worker.status

    def set_overlay_visible(self, on: bool):
        """Toon of verberg de overlay — worker blijft draaien (gebruikt door Overlay-knop)."""
        self.setVisible(on)

    def set_enabled(self, on: bool):
        """Start of stop de WebSocket-verbinding én overlay (gebruikt door Instellingen)."""
        self.setVisible(on)
        if on:
            if not self._worker._running:
                self._worker.start()
            if not self._anim_timer.isActive():
                self._anim_timer.start(50)
        else:
            self._worker.stop()
            with self._lock:
                self._strikes.clear()
                self._flashes.clear()
            self.update()
            self._worker.status.emit("disabled")
            self._anim_timer.stop()

    def set_cfg(self, cfg):
        self._cfg = cfg

    def set_fade_seconds(self, secs: int):
        self.fade_seconds = max(30, int(secs))

    def set_anim_scale(self, scale: float):
        """Schaal voor ring-diameter en stip-grootte (1.0 = origineel, 2.0 = dubbel)."""
        self._anim_scale = max(0.5, min(8.0, float(scale)))

    def set_font_size(self, size: int):
        """Stel lettergrootte in voor labels op kaart."""
        self._font_size = max(5, min(72, int(size)))

    def _on_strike(self, lat: float, lon: float):
        pt  = _xy(lat, lon)
        now = time.monotonic()
        with self._lock:
            self._strikes.append((pt.x(), pt.y(), now))
            self._flashes.append((pt.x(), pt.y(), now))
            if len(self._strikes) > 5000:
                self._strikes = self._strikes[-5000:]
        # Piepje afspelen indien ingesteld
        cfg = self._cfg
        if cfg and getattr(cfg, "lightning_beep", False):
            beep_r = int(getattr(cfg, "lightning_beep_r", 0))
            if beep_r > 0:
                # Controleer afstand tot QTH
                try:
                    import math
                    R = 6371.0
                    qlat = math.radians(cfg.qth_lat)
                    qlon = math.radians(cfg.qth_lon)
                    slat = math.radians(lat)
                    slon = math.radians(lon)
                    dlat = slat - qlat; dlon = slon - qlon
                    a = math.sin(dlat/2)**2 + math.cos(qlat)*math.cos(slat)*math.sin(dlon/2)**2
                    km = 2 * R * math.asin(min(1.0, math.sqrt(a)))
                    if km > beep_r:
                        return
                except Exception:
                    return
            threading.Thread(target=_play_tick, daemon=True).start()

    def _anim_tick(self):
        """20 fps tick — alleen actief redraw als er verse ringen zijn."""
        now = time.monotonic()
        with self._lock:
            has_flashes = bool(self._flashes) and (now - self._flashes[-1][2] < 10)
        if has_flashes:
            self.update()

    def _tick(self):
        """Opruim-timer: verwijdert verouderde inslagen + traag fade-update."""
        now = time.monotonic()
        with self._lock:
            self._strikes = [(x, y, t) for x, y, t in self._strikes
                             if now - t < self.fade_seconds]
            self._flashes = [(x, y, t) for x, y, t in self._flashes
                             if now - t < 4.0]
        self.update()

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, MAP_W, MAP_H)

    def paint(self, painter: QPainter, option, widget=None):
        now = time.monotonic()
        with self._lock:
            strikes = list(self._strikes)
            flashes = list(self._flashes)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        sc = self._anim_scale
        for x, y, t in strikes:
            age = now - t
            f   = max(0.0, 1.0 - age / self.fade_seconds)
            if age < 60:
                r, g, b = 255, 255, int(180 + 75*f)
            elif age < 300:
                r, g, b = 255, int(150 + 105*f), 30
            else:
                r, g, b = int(150 + 105*f), int(60 + 60*f), 0
            r, g, b = int(r*f), int(g*f), int(b*f)
            sz = max(1.0, (1.5 + 2.5*f) * sc)
            painter.setBrush(QBrush(QColor(r, g, b, int(220*f))))
            painter.drawEllipse(QPointF(x, y), sz, sz)

        # Uitdijende ringen — helder wit → geel → oranje, lineaire fade
        _RING_DUR = 5.0   # 5 seconden zodat ringen goed zichtbaar blijven
        painter.setBrush(Qt.NoBrush)
        for x, y, t in flashes:
            age = now - t
            if age >= _RING_DUR:
                continue

            # ── Korte centrale flits (eerste 0.3s) ───────────────────────────
            if age < 0.3:
                ff = 1.0 - age / 0.3
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(255, 255, 255, int(240 * ff))))
                painter.drawEllipse(QPointF(x, y), 6 * sc * ff, 6 * sc * ff)
                painter.setBrush(Qt.NoBrush)

            # ── Ring 1: primaire ring (snel, heller) ──────────────────────────
            f1  = max(0.0, 1.0 - age / _RING_DUR)           # lineaire fade
            sz1 = (8 + age * 22) * sc
            lw1 = max(1.5, 3.5 * f1 * sc)
            r1  = int(255 * min(1.0, age * 4))               # wit → geel aan het begin
            g1  = int(200 * f1)
            c1  = QColor(255, g1, r1 // 4, int(230 * f1))
            painter.setPen(QPen(c1, lw1))
            painter.drawEllipse(QPointF(x, y), sz1, sz1)

            # ── Ring 2: vertraagde ring (0.5s later, iets groter) ────────────
            age2 = age - 0.5
            if 0.0 <= age2 < _RING_DUR:
                f2  = max(0.0, 1.0 - age2 / _RING_DUR)
                sz2 = (8 + age2 * 22) * sc
                lw2 = max(1.0, 2.0 * f2 * sc)
                c2  = QColor(255, int(140 * f2), 0, int(160 * f2))
                painter.setPen(QPen(c2, lw2))
                painter.drawEllipse(QPointF(x, y), sz2, sz2)


# ── Lightning Radius Layer ────────────────────────────────────────────────────

class LightningRadiusLayer(QGraphicsItem):
    """Transparante cirkel op de kaart om het QTH.

    color_rgb  : (R, G, B) tuple — kleur van de rand en vulling
    label      : korte tekst achter het km-getal (bijv. '⚡' of '🔔')
    """

    def __init__(self, color_rgb=(255, 80, 80), label: str = ""):
        super().__init__()
        self.setZValue(4.5)
        self._qth_lat   = 52.0
        self._qth_lon   = 5.0
        self._radius_km = 0
        self._r, self._g, self._b = color_rgb
        self._label     = label
        self._font_size = 7
        self.setVisible(False)

    def set_qth(self, lat: float, lon: float):
        self._qth_lat = lat
        self._qth_lon = lon
        self.update()

    def set_radius_km(self, km: int):
        self._radius_km = km
        self.setVisible(km > 0)
        self.update()

    def set_font_size(self, size: int):
        """Stel lettergrootte in voor label."""
        self._font_size = max(5, min(72, int(size)))
        self.update()

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, MAP_W, MAP_H)

    def paint(self, painter: QPainter, option, widget=None):
        if self._radius_km <= 0:
            return

        N   = 90
        rho = self._radius_km / 6371.0
        lat_r = math.radians(self._qth_lat)
        lon_r = math.radians(self._qth_lon)

        from PySide6.QtGui import QPolygonF
        poly = []
        for i in range(N):
            az   = 2 * math.pi * i / N
            glat = math.asin(max(-1.0, min(1.0,
                math.sin(lat_r) * math.cos(rho) +
                math.cos(lat_r) * math.sin(rho) * math.cos(az))))
            glon = lon_r + math.atan2(
                math.sin(az) * math.sin(rho) * math.cos(lat_r),
                math.cos(rho) - math.sin(lat_r) * math.sin(glat))
            x = (math.degrees(glon) + 180) / 360 * MAP_W
            y = (90 - math.degrees(glat)) / 180 * MAP_H
            poly.append(QPointF(x, y))

        r, g, b = self._r, self._g, self._b
        painter.setPen(QPen(QColor(r, g, b, 190), 1.5, Qt.DashLine))
        painter.setBrush(QBrush(QColor(r, g, b, 18)))
        painter.drawPolygon(QPolygonF(poly))

        # Label boven de cirkel
        top_lat = math.degrees(math.asin(min(1.0,
            math.sin(lat_r) * math.cos(rho) + math.cos(lat_r) * math.sin(rho))))
        cx     = (self._qth_lon + 180) / 360 * MAP_W
        cy_top = (90 - top_lat) / 180 * MAP_H - 7
        painter.setPen(QColor(r, g, b, 210))
        painter.setFont(QFont("Segoe UI", self._font_size))
        lbl = f"{self._radius_km} km {self._label}".strip()
        painter.drawText(QPointF(cx + 4, cy_top), lbl)


# ── Satellite Layer ───────────────────────────────────────────────────────────

_SAT_COLORS = [
    QColor(255, 200,   0),   # goud
    QColor(100, 220, 255),   # cyaan
    QColor(100, 255, 100),   # groen
    QColor(255, 140,   0),   # oranje
    QColor(220, 100, 255),   # paars
    QColor(255, 100, 100),   # rood
]


class SatelliteLayer(QGraphicsItem):
    """Satelliet-posities, orbitpaden en footprints. TLE via set_tle()."""

    _R_EARTH = 6371.0

    def __init__(self):
        super().__init__()
        self.setZValue(4)
        self._tle:       dict[str, tuple[str, str]] = {}
        self._selected:  set[str] = set()
        self._path_sel:  set[str] = set()
        self._fp_sel:    set[str] = set()
        self._back_h: int = 1
        self._fwd_h:  int = 12
        self._path_width: float = 1.2
        self._qth_lat: float = 52.0
        self._qth_lon: float = 5.0
        self._overlay_font_size: int = 8
        self._positions: dict[str, tuple] = {}
        self._paths:     dict[str, tuple] = {}
        self._ping_enabled: bool = True
        self._sig = _SatSignaller()
        self._lock      = threading.Lock()
        self._calc_lock = threading.Lock()

        self._pos_timer  = QTimer()
        self._pos_timer.timeout.connect(lambda: threading.Thread(
            target=self._calc_positions, daemon=True).start())
        self._pos_timer.start(10_000)

        self._path_timer = QTimer()
        self._path_timer.timeout.connect(lambda: threading.Thread(
            target=self._calc_paths, daemon=True).start())
        self._path_timer.start(60_000)

    def set_tle(self, tle: dict[str, tuple[str, str]]):
        with self._lock:
            self._tle = dict(tle)
        threading.Thread(target=self._calc_positions, daemon=True).start()
        threading.Thread(target=self._calc_paths, daemon=True).start()

    def set_selected(self, names: set[str]):
        with self._lock:
            self._selected = set(names)
        threading.Thread(target=self._calc_positions, daemon=True).start()

    def set_path_selected(self, names: set[str]):
        with self._lock:
            self._path_sel = set(names)
        threading.Thread(target=self._calc_paths, daemon=True).start()

    def set_fp_selected(self, names: set[str]):
        with self._lock:
            self._fp_sel = set(names)
        self.update()

    def set_qth(self, lat: float, lon: float):
        with self._lock:
            self._qth_lat = lat
            self._qth_lon = lon
        self.update()

    @property
    def zone_changed(self) -> Signal:
        return self._sig.zone_changed

    def set_ping_enabled(self, on: bool):
        self._ping_enabled = on

    def set_overlay_font_size(self, size: int):
        self._overlay_font_size = max(6, size)
        self.update()

    def set_path_hours(self, back_h: int, fwd_h: int):
        self._back_h = max(0, back_h)
        self._fwd_h  = max(0, fwd_h)
        threading.Thread(target=self._calc_paths, daemon=True).start()

    def set_path_width(self, width: float):
        self._path_width = max(0.3, float(width))
        self.update()

    def _calc_positions(self):
        if not self._calc_lock.acquire(blocking=False):
            return   # al bezig in een andere thread — sla over
        try:
            with self._lock:
                sel = set(self._selected)
                tle = dict(self._tle)
            pos = {}
            for name in sel:
                if name in tle:
                    r = _sgp4_latlon(*tle[name])
                    if r:
                        pos[name] = r
            with self._lock:
                self._positions = pos
            self.update()
        finally:
            self._calc_lock.release()

    def _calc_paths(self):
        with self._lock:
            sel    = set(self._path_sel)
            tle    = dict(self._tle)
            back_h = self._back_h
            fwd_h  = self._fwd_h
        paths = {}
        for name in sel:
            if name in tle:
                paths[name] = _calc_sat_path(
                    *tle[name],
                    back_min=back_h * 60,   # 0 = geen verleden-pad
                    fwd_min=fwd_h  * 60)    # 0 = geen toekomst-pad
        with self._lock:
            self._paths = paths
        self.update()

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, MAP_W, MAP_H)

    def paint(self, painter: QPainter, option, widget=None):
        with self._lock:
            pos   = dict(self._positions)
            paths = dict(self._paths)
            names = sorted(self._selected)
            fp_sel = set(self._fp_sel)

        painter.setRenderHint(QPainter.Antialiasing)
        font = QFont("Segoe UI", self._overlay_font_size)
        painter.setFont(font)

        for i, name in enumerate(names):
            color = _SAT_COLORS[i % len(_SAT_COLORS)]

            # Footprint
            if name in fp_sel and name in pos:
                lat, lon, alt = pos[name]
                if alt > 0:
                    rho_deg = math.degrees(
                        math.acos(min(1.0, self._R_EARTH / (self._R_EARTH + alt))))
                    with self._lock:
                        qth_lat = self._qth_lat
                        qth_lon = self._qth_lon
                    _draw_footprint(painter, lat, lon, rho_deg, qth_lat, qth_lon)

            # Orbitpaden
            if name in paths:
                past, fwd = paths[name]
                pw = self._path_width
                _draw_path(painter, past, QPen(color.darker(160), pw * 0.67, Qt.DashLine))
                _draw_path(painter, fwd,  QPen(color, pw))

            # Satelliet-icoon en label
            if name in pos:
                lat, lon, _ = pos[name]
                pt = _xy(lat, lon)
                painter.setRenderHint(QPainter.Antialiasing)
                _draw_sat_icon(painter, pt, color)
                # Label gecentreerd onder het icoon
                short = name.split("(")[0].strip()[:16]
                lbl_font = QFont("Segoe UI", self._overlay_font_size)
                lbl_font.setBold(True)
                painter.setFont(lbl_font)
                fm     = painter.fontMetrics()
                tw     = fm.horizontalAdvance(short)
                lbl_x  = pt.x() - tw / 2          # horizontaal gecentreerd
                lbl_y  = pt.y() + 8 + self._overlay_font_size  # schaal met fontgrootte
                # Schaduw
                painter.setPen(QColor(0, 0, 0, 180))
                painter.drawText(QPointF(lbl_x + 1, lbl_y + 1), short)
                # Tekst
                painter.setPen(color.lighter(150))
                painter.drawText(QPointF(lbl_x, lbl_y), short)


def _qth_in_footprint(sat_lat: float, sat_lon: float,
                      rho_deg: float,
                      qth_lat: float, qth_lon: float) -> bool:
    """True als het QTH binnen de voetafdruk van de satelliet valt."""
    sl = math.radians(sat_lat); ql = math.radians(qth_lat)
    dlon = math.radians(qth_lon - sat_lon)
    cos_d = math.sin(sl)*math.sin(ql) + math.cos(sl)*math.cos(ql)*math.cos(dlon)
    return math.degrees(math.acos(max(-1.0, min(1.0, cos_d)))) < rho_deg


def _draw_sat_icon(painter: QPainter, pt: QPointF, color: QColor):
    """Teken een satelliet-icoon: romp + zonnepanelen + antenne."""
    px, py = pt.x(), pt.y()

    # ── Zonnepanelen (links en rechts van de romp) ────────────────────────────
    pw, ph = 14, 5   # paneel breedte, hoogte
    bw, bh =  9, 9   # romp breedte, hoogte
    panel_clr = QColor(
        min(255, int(color.red()   * 0.7 + 40)),
        min(255, int(color.green() * 0.7 + 40)),
        min(255, int(color.blue()  * 0.7 + 80)),
    )
    painter.setPen(QPen(Qt.black, 0.5))
    painter.setBrush(QBrush(panel_clr))
    # Links
    painter.drawRect(QRectF(px - bw / 2 - pw, py - ph / 2, pw, ph))
    # Rechts
    painter.drawRect(QRectF(px + bw / 2, py - ph / 2, pw, ph))

    # Verbindingsstangen
    painter.setPen(QPen(color.darker(140), 1.0))
    painter.drawLine(QPointF(px - bw / 2 - pw / 2, py),
                     QPointF(px + bw / 2 + pw / 2, py))

    # ── Romp ──────────────────────────────────────────────────────────────────
    painter.setPen(QPen(Qt.black, 0.8))
    painter.setBrush(QBrush(color))
    painter.drawRect(QRectF(px - bw / 2, py - bh / 2, bw, bh))

    # Romp-detail: klein venster
    win_clr = QColor(min(255, color.red() + 60),
                     min(255, color.green() + 60),
                     min(255, color.blue() + 60), 200)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QBrush(win_clr))
    painter.drawRect(QRectF(px - 1.5, py - 1.5, 3, 3))

    # ── Antenne (omhoog) ──────────────────────────────────────────────────────
    painter.setPen(QPen(color.lighter(160), 1.0))
    painter.drawLine(QPointF(px, py - bh / 2), QPointF(px, py - bh / 2 - 6))
    painter.setBrush(QBrush(color.lighter(150)))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(QPointF(px, py - bh / 2 - 7), 2, 2)


def _draw_footprint(painter: QPainter, sat_lat: float, sat_lon: float,
                    rho_deg: float, qth_lat: float, qth_lon: float):
    """Teken satelliet-footprint — algoritme conform v4.0.2.

    Stap 1: polaire kap (kleine rechthoek bij de pool-tip) EERST.
    Stap 2: volledig polygoon erover heen (3× voor antimeridian).
    Bij poolpassage: geen rand op polygoon (zoals v4).
    Geel = QTH buiten bereik, Groen = QTH zichtbaar.
    """
    from PySide6.QtGui import QPolygonF

    in_range = _qth_in_footprint(sat_lat, sat_lon, rho_deg, qth_lat, qth_lon)
    c_fill = QColor(50, 220, 50,  80) if in_range else QColor(255, 220, 0,  60)
    c_line = QColor(50, 220, 50, 200) if in_range else QColor(255, 200, 0, 180)

    # ── v4.0.2-formules voor polaire kap ──────────────────────────────────────
    dist_north = 90.0 - sat_lat   # hoekafstand naar noordpool
    dist_south = 90.0 + sat_lat   # hoekafstand naar zuidpool
    has_polar  = False

    # ── Polygoon — azimuth-parameterisatie (normaal geval) ───────────────────
    N = 72
    sat_lat_r = math.radians(sat_lat)
    sat_lon_r = math.radians(sat_lon)
    rho       = math.radians(rho_deg)

    pts = []
    for i in range(N):
        az     = 2 * math.pi * i / N
        glat_r = math.asin(max(-1.0, min(1.0,
                    math.sin(sat_lat_r) * math.cos(rho) +
                    math.cos(sat_lat_r) * math.sin(rho) * math.cos(az))))
        glon_r = sat_lon_r + math.atan2(
                    math.sin(az) * math.sin(rho) * math.cos(sat_lat_r),
                    math.cos(rho) - math.sin(sat_lat_r) * math.sin(glat_r))
        glat = math.degrees(glat_r)
        glon = math.degrees(glon_r)
        while glon - sat_lon >  180: glon -= 360
        while glon - sat_lon < -180: glon += 360
        pts.append(QPointF((glon + 180) / 360 * MAP_W,
                            (90 - glat) / 180 * MAP_H))

    from PySide6.QtGui import QPainterPath as _QPP

    painter.setPen(Qt.NoPen)
    painter.setBrush(QBrush(c_fill))

    if dist_north < rho_deg or dist_south < rho_deg:
        # ── Poolgeval: azimuth-polygoon + poolkap via QPainterPath.united() ───
        # Probleem: bij az≈0° geeft atan2(0,negatief)=±π → ±180° lengtegraad-
        # sprong → horizontale/diagonale lijnfout.
        # Oplossing conform v4: poolkap-rechthoek ∪ alle drie dx-polygonen in
        # één enkel pad (geen meervoudige alpha-compositing).
        # De kaplijn wordt 8 px extra uitgebreid zodat punten net onder lat_full
        # (met iets afwijkende lengtegraad) volledig worden bedekt.
        north_pole = (dist_north < rho_deg)
        has_polar  = True

        if north_pole:
            lat_full = 180.0 - rho_deg - sat_lat
        else:
            lat_full = rho_deg - 180.0 - sat_lat
        yf = max(0.0, min(float(MAP_H) - 1,
                          (90.0 - lat_full) / 180.0 * MAP_H))

        MARGIN = 10   # px marge om near-pool punten met foute lengtegraad te dekken

        combined = _QPP()
        if north_pole:
            combined.addRect(QRectF(-2, -2, MAP_W + 4, yf + MARGIN))
        else:
            combined.addRect(QRectF(-2, yf - MARGIN, MAP_W + 4, MAP_H + 4))

        from PySide6.QtGui import QPolygonF as _QPolyF
        for dx in (-MAP_W, 0, MAP_W):
            sub = _QPP()
            sub.addPolygon(_QPolyF(
                [QPointF(p.x() + dx, p.y()) for p in pts]))
            sub.closeSubpath()
            combined = combined.united(sub)

        painter.setPen(QPen(c_line, 1.0))
        painter.drawPath(combined)
        painter.setPen(Qt.NoPen)

    else:
        # Normaal geval: alleen polygoon met rand
        painter.setPen(QPen(c_line, 1.5))
        for dx in (-MAP_W, 0, MAP_W):
            painter.drawPolygon(
                QPolygonF([QPointF(p.x() + dx, p.y()) for p in pts]))




def _draw_path(painter: QPainter, pts: list, pen: QPen):
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)
    prev = None
    for pt in pts:
        if pt is None:
            prev = None
            continue
        cur = _xy(*pt)
        if prev is not None:
            painter.drawLine(prev, cur)
        prev = cur


# ── DX Spots Layer ────────────────────────────────────────────────────────────

# Uitgebreide DXCC prefix → (lat, lon)  — dekt >300 entiteiten
_DXCC: dict[str, tuple[float, float]] = {
    # ── USA / Canada / Noord-Amerika ──────────────────────────────────────────
    "W":   ( 38.0, -97.0), "K":   ( 38.0, -97.0), "N":   ( 38.0, -97.0),
    "AA":  ( 38.0, -97.0), "AB":  ( 38.0, -97.0), "AC":  ( 38.0, -97.0),
    "AD":  ( 38.0, -97.0), "AE":  ( 38.0, -97.0), "AF":  ( 38.0, -97.0),
    "AG":  ( 38.0, -97.0), "AH":  ( 38.0, -97.0), "AI":  ( 38.0, -97.0),
    "AJ":  ( 38.0, -97.0), "AK":  ( 38.0, -97.0),
    "WH2": ( 13.5, 144.8), "WH0": ( 15.2, 145.7), "KH2": ( 13.5, 144.8),
    "KH0": ( 15.2, 145.7), "KH6": ( 20.5,-157.0), "KH8": (-14.3,-170.7),
    "KP2": ( 17.7, -64.8), "KP4": ( 18.2, -66.5),
    "KL":  ( 64.0,-152.0),
    "VE":  ( 56.0, -96.0), "VA":  ( 56.0, -96.0), "VO":  ( 53.0, -60.0),
    "VY":  ( 63.0,-136.0),
    "XE":  ( 23.0,-102.0), "XF":  ( 23.0,-102.0),
    "TG":  ( 15.5, -90.3), "TI":  (  9.9, -84.1), "HP":  (  8.9, -79.5),
    "YN":  ( 12.9, -85.6), "HR":  ( 15.0, -86.5), "HH":  ( 19.0, -72.3),
    "HI":  ( 19.0, -70.7), "J3":  ( 12.1, -61.7), "J6":  ( 14.0, -61.0),
    "J7":  ( 15.3, -61.4), "VP2E":( 17.1, -61.8), "VP2M":( 16.7, -62.2),
    "VP2V":( 18.4, -64.6), "VP5": ( 21.8, -71.9),
    "CO":  ( 22.0, -80.0), "CM":  ( 22.0, -80.0),
    "ZF":  ( 19.3, -81.4), "V3":  ( 17.2, -88.8),
    # ── Zuid-Amerika ──────────────────────────────────────────────────────────
    "PY":  (-15.0, -50.0), "PU":  (-15.0, -50.0), "PP":  (-15.0, -50.0),
    "PQ":  (-15.0, -50.0), "PR":  (-15.0, -50.0), "PS":  (-15.0, -50.0),
    "PT":  (-15.0, -50.0), "PV":  (-15.0, -50.0), "PW":  (-15.0, -50.0),
    "LU":  (-34.0, -64.0), "CE":  (-30.0, -71.0),
    "OA":  (-10.0, -75.0), "OB":  (-10.0, -75.0),
    "HC":  ( -1.8, -78.0), "YV":  (  8.0, -66.0), "YW":  (  8.0, -66.0),
    "CX":  (-32.8, -56.0), "ZP":  (-23.0, -58.0), "CP":  (-16.0, -64.0),
    "HK":  (  4.0, -74.0), "GY":  (  5.0, -59.0), "8R":  (  5.0, -59.0),
    "9Y":  ( 10.5, -61.3), "9Z":  ( 10.5, -61.3),
    "FY":  (  4.0, -53.0), "PZ":  (  4.0, -56.0),
    "VP8": (-51.7, -57.8),
    # ── West-Europa ───────────────────────────────────────────────────────────
    "G":   ( 52.0,  -2.0), "GW":  ( 52.0,  -4.0), "GM":  ( 57.0,  -4.0),
    "GI":  ( 54.5,  -6.5), "GU":  ( 49.5,  -2.4), "GJ":  ( 49.2,  -2.1),
    "EI":  ( 53.0,  -8.0), "TF":  ( 65.0, -19.0),
    "F":   ( 46.0,   2.0), "TK":  ( 42.0,   9.0),
    "DL":  ( 52.0,  10.0), "DJ":  ( 52.0,  10.0), "DK":  ( 52.0,  10.0),
    "DA":  ( 52.0,  10.0), "DB":  ( 52.0,  10.0), "DC":  ( 52.0,  10.0),
    "DD":  ( 52.0,  10.0), "DE":  ( 52.0,  10.0), "DF":  ( 52.0,  10.0),
    "DG":  ( 52.0,  10.0), "DH":  ( 52.0,  10.0), "DI":  ( 52.0,  10.0),
    "PA":  ( 52.3,   5.3), "PB":  ( 52.3,   5.3), "PC":  ( 52.3,   5.3),
    "PD":  ( 52.3,   5.3), "PE":  ( 52.3,   5.3), "PF":  ( 52.3,   5.3),
    "PG":  ( 52.3,   5.3), "PH":  ( 52.3,   5.3), "PI":  ( 52.3,   5.3),
    "ON":  ( 50.5,   4.5), "OT":  ( 50.5,   4.5),
    "LX":  ( 49.8,   6.1), "HB":  ( 47.0,   8.0), "HB0": ( 47.1,   9.5),
    "OE":  ( 47.5,  14.5),
    "I":   ( 42.0,  12.0), "IT9": ( 37.5,  14.0), "IS":  ( 40.0,   9.0),
    "IG9": ( 35.5,  12.6),
    "EA":  ( 40.0,  -4.0), "EA6": ( 39.6,   3.0), "EA8": ( 28.3, -14.0),
    "EA9": ( 35.9,  -5.3),
    "CT":  ( 39.5,  -8.0), "CS":  ( 39.5,  -8.0), "CR":  ( 39.5,  -8.0),
    "SM":  ( 62.0,  17.0), "SK":  ( 62.0,  17.0), "SL":  ( 62.0,  17.0),
    "SE":  ( 62.0,  17.0), "SF":  ( 62.0,  17.0), "SG":  ( 62.0,  17.0),
    "SH":  ( 62.0,  17.0), "SI":  ( 62.0,  17.0),
    "LA":  ( 62.0,  10.0), "LB":  ( 62.0,  10.0),
    "OZ":  ( 56.0,  10.0), "OY":  ( 62.0,  -7.0), "OX":  ( 72.0, -25.0),
    "OH":  ( 64.0,  26.0), "OF":  ( 64.0,  26.0), "OG":  ( 64.0,  26.0),
    "OH0": ( 60.2,  20.0),
    "SP":  ( 52.0,  21.0), "SQ":  ( 52.0,  21.0), "SR":  ( 52.0,  21.0),
    "OK":  ( 50.0,  15.0), "OL":  ( 50.0,  15.0),
    "OM":  ( 48.7,  19.0),
    "HA":  ( 47.0,  19.0), "HG":  ( 47.0,  19.0),
    "YO":  ( 46.0,  25.0), "YP":  ( 46.0,  25.0), "YQ":  ( 46.0,  25.0),
    "YR":  ( 46.0,  25.0),
    "LZ":  ( 43.0,  25.0),
    "SV":  ( 38.0,  23.0), "SW":  ( 38.0,  23.0), "SX":  ( 38.0,  23.0),
    "SY":  ( 38.0,  23.0), "SZ":  ( 38.0,  23.0),
    "SV5": ( 36.2,  27.9), "SV9": ( 35.3,  25.0),
    "5B":  ( 35.0,  33.0), "C4":  ( 35.0,  33.0),
    "9H":  ( 35.9,  14.5),
    "YU":  ( 44.0,  21.0), "YT":  ( 44.0,  21.0), "YZ":  ( 44.0,  21.0),
    "9A":  ( 45.0,  16.0),
    "S5":  ( 46.0,  15.0),
    "T9":  ( 44.0,  17.5), "E7":  ( 44.0,  17.5),
    "4O":  ( 42.8,  19.5),
    "Z3":  ( 41.6,  21.7), "Z32": ( 41.6,  21.7),
    "LY":  ( 56.0,  24.0),
    "YL":  ( 57.0,  25.0),
    "ES":  ( 59.0,  25.0),
    # ── Oost-Europa / Centraal-Azië ───────────────────────────────────────────
    "UA":  ( 55.0,  40.0), "RA":  ( 55.0,  40.0), "RZ":  ( 55.0,  40.0),
    "R":   ( 55.0,  40.0), "RK":  ( 55.0,  40.0), "RL":  ( 55.0,  40.0),
    "RM":  ( 55.0,  40.0), "RN":  ( 55.0,  40.0), "RO":  ( 55.0,  40.0),
    "RP":  ( 55.0,  40.0), "RQ":  ( 55.0,  40.0), "RT":  ( 55.0,  40.0),
    "RU":  ( 55.0,  40.0), "RV":  ( 55.0,  40.0), "RW":  ( 55.0,  40.0),
    "RX":  ( 55.0,  40.0), "RY":  ( 55.0,  40.0),
    "UA9": ( 60.0,  90.0), "UA0": ( 60.0, 130.0),
    "UR":  ( 49.0,  32.0), "US":  ( 49.0,  32.0), "UT":  ( 49.0,  32.0),
    "UU":  ( 49.0,  32.0), "UV":  ( 49.0,  32.0), "UW":  ( 49.0,  32.0),
    "UX":  ( 49.0,  32.0), "UY":  ( 49.0,  32.0), "UZ":  ( 49.0,  32.0),
    "EW":  ( 53.5,  28.0),
    "EU":  ( 53.5,  28.0),
    "EK":  ( 40.0,  45.0),
    "4J":  ( 40.4,  49.8), "4K":  ( 40.4,  49.8),
    "EX":  ( 41.0,  75.0), "EY":  ( 38.5,  71.0), "EZ":  ( 38.0,  58.0),
    "UK":  ( 41.0,  64.0), "UJ":  ( 41.0,  64.0),
    "UN":  ( 50.0,  70.0), "UO":  ( 50.0,  70.0),
    "TA":  ( 39.0,  35.0), "TC":  ( 39.0,  35.0),
    "4L":  ( 42.0,  43.5),
    # ── Midden-Oosten ─────────────────────────────────────────────────────────
    "4X":  ( 31.5,  34.8), "4Z":  ( 31.5,  34.8),
    "OD":  ( 33.8,  35.5),
    "YK":  ( 34.8,  38.5),
    "A4":  ( 23.0,  57.0), "A6":  ( 24.5,  54.5), "A7":  ( 25.3,  51.5),
    "A9":  ( 26.0,  50.5), "A8":  (  6.3, -10.8),
    "HZ":  ( 25.0,  45.0),
    "JY":  ( 31.0,  36.0),
    "EP":  ( 32.0,  53.0),
    "YA":  ( 34.5,  69.2),
    "AP":  ( 30.0,  70.0),
    # ── Azië ──────────────────────────────────────────────────────────────────
    "JA":  ( 36.0, 138.0), "7J":  ( 36.0, 138.0),
    "HL":  ( 37.0, 127.0), "DS":  ( 37.0, 127.0), "6K":  ( 37.0, 127.0),
    "BY":  ( 35.0, 104.0), "BA":  ( 35.0, 104.0), "BD":  ( 35.0, 104.0),
    "BE":  ( 35.0, 104.0), "BG":  ( 35.0, 104.0), "BH":  ( 35.0, 104.0),
    "BI":  ( 35.0, 104.0), "BJ":  ( 35.0, 104.0),
    "VR":  ( 22.3, 114.2), "BV":  ( 23.5, 121.0),
    "XU":  ( 12.5, 105.0), "XV":  ( 16.0, 106.0), "3W":  ( 16.0, 106.0),
    "XW":  ( 18.0, 103.0),
    "HS":  ( 13.0, 101.0), "E2":  ( 13.0, 101.0),
    "DU":  ( 13.0, 122.0), "DX":  ( 13.0, 122.0),
    "YB":  ( -5.0, 120.0), "YC":  ( -5.0, 120.0), "YD":  ( -5.0, 120.0),
    "YE":  ( -5.0, 120.0), "YF":  ( -5.0, 120.0), "YG":  ( -5.0, 120.0),
    "YH":  ( -5.0, 120.0),
    "9V":  (  1.3, 103.8),
    "VU":  ( 20.0,  77.0), "AT":  ( 20.0,  77.0), "AU":  ( 20.0,  77.0),
    "AW":  ( 20.0,  77.0),
    "9N":  ( 28.0,  84.0), "9M2": (  4.0, 110.0), "9M8": (  2.0, 113.0),
    "9M6": (  6.0, 116.0), "9W":  (  4.0, 110.0),
    "S2":  ( 24.0,  90.0),
    "4S":  (  7.9,  80.7),
    "8Q":  (  4.2,  73.5),
    "VQ9": (-7.3,  72.4),
    "VK9": (-10.5, 105.7),
    # ── Oceanië ───────────────────────────────────────────────────────────────
    "VK":  (-25.0, 135.0),
    "ZL":  (-40.0, 175.0), "ZL7": (-44.0,-176.5), "ZL8": (-29.1,-177.9),
    "ZL9": (-52.5, 169.1),
    "FK":  (-21.0, 165.0),
    "FO":  (-18.0,-149.0), "FO/A":(-9.0,-140.0),
    "KH0": ( 15.2, 145.7),
    "T2":  ( -8.0, 178.0), "T30": (  3.4, 172.1),
    "T31": (  2.0,-157.5), "T32": (  1.9,-157.5),
    "H44": ( -9.0, 160.0), "H40": ( -9.0, 158.0),
    "YJ":  (-17.7, 168.3), "A3":  (-20.0,-175.0),
    "3D2": (-18.1, 179.0),
    "V7":  (  7.1, 171.4), "KX6": (  7.1, 171.4),
    # ── Afrika ────────────────────────────────────────────────────────────────
    "ZS":  (-30.0,  25.0), "ZR":  (-30.0,  25.0), "ZT":  (-30.0,  25.0),
    "ZU":  (-30.0,  25.0),
    "V5":  (-22.0,  17.0), "A2":  (-22.0,  24.0), "Z2":  (-20.0,  30.0),
    "7P":  (-29.5,  28.2), "8P":  ( 13.2, -59.6),
    "5H":  ( -6.0,  35.0), "5Z":  (  1.0,  38.0), "5X":  (  1.3,  32.0),
    "ET":  (  9.0,  38.7), "6O":  ( 10.0,  49.0),
    "SU":  ( 26.0,  30.0),
    "CN":  ( 32.0,  -6.0), "7X":  ( 28.0,   2.0), "TS":  ( 34.0,   9.0),
    "5A":  ( 27.0,  17.0),
    "ST":  ( 15.6,  32.5),
    "EL":  (  6.3, -10.8), "D4":  ( 16.0, -24.0), "6W":  ( 14.7, -17.4),
    "TU":  (  7.5,  -5.5), "TY":  (  9.3,   2.3), "TZ":  ( 17.3,  -4.0),
    "TJ":  (  4.0,  12.4), "TR":  ( -1.0,  11.8), "TN":  ( -4.3,  15.3),
    "5R":  (-20.0,  47.0), "FR":  (-21.1,  55.5),
    "3B8": (-20.2,  57.5), "3B6": (-10.4,  40.0), "3B7": ( -9.8,  50.7),
    "3B9": (-19.7,  63.4),
    "VQ9": ( -7.3,  72.4),
    "9J":  (-15.0,  30.0), "9I":  (-15.0,  30.0),
    "ZD7": (-15.9,  -5.7), "ZD8": ( -7.9, -14.4), "ZD9": (-37.1, -12.3),
    "9L":  (  8.5, -13.3), "9G":  (  7.9,  -1.1),
    "D2":  (-12.0,  18.0), "D3":  (-12.0,  18.0),
    "C5":  ( 13.5, -15.5), "C3":  ( 42.6,   1.5),
    "J5":  ( 12.0, -15.0), "3C":  (  1.7,   9.0),
    "7Q":  (-13.0,  34.0), "7O":  ( 15.5,  48.0),
    "C9":  (-18.0,  35.0), "CR7": (-18.0,  35.0),
    "5V":  (  8.7,   1.2), "6Y":  ( 18.2, -77.3),
    "T5":  (  2.0,  45.3), "6V":  ( 14.7, -17.4),
}



def _call_to_latlon(call: str) -> tuple[float, float] | None:
    call = call.upper().split("/")[0]
    for n in range(min(len(call), 4), 0, -1):
        if call[:n] in _DXCC:
            return _DXCC[call[:n]]
    return None


def _band_color(freq_khz: float) -> QColor:
    if freq_khz < 2100:  return QColor(180,   0, 200)  # 160m
    if freq_khz < 5000:  return QColor(220,  50,  50)  # 80m
    if freq_khz < 7500:  return QColor(255, 140,   0)  # 40m
    if freq_khz < 11000: return QColor(255, 220,   0)  # 30m
    if freq_khz < 15500: return QColor( 50, 200,  50)  # 20m
    if freq_khz < 19000: return QColor(100, 240, 100)  # 17m
    if freq_khz < 22000: return QColor(  0, 220, 220)  # 15m
    if freq_khz < 26000: return QColor(100, 180, 255)  # 12m
    if freq_khz < 32000: return QColor( 50, 100, 255)  # 10m
    return QColor(150, 0, 255)                          # 6m+


class _DXFetchThread(QThread):
    """Haalt DX spots op van dxwatch.com.
    Emitteert lijst van dicts: {time, dx, freq_khz, band, spotter, comment}.
    """
    spots_ready = Signal(list)

    # v4-formaat: s={id: [dx_call, freq_khz, spotter, comment, "HHMMz DD Mon", ...]}
    _URL = "https://dxwatch.com/dxsd1/s.php?s=0&r=100&cdxc=0"

    def run(self):
        try:
            import html as _html
            req = urllib.request.Request(
                self._URL, headers={"User-Agent": "HAMIOS/5.0"})
            with urllib.request.urlopen(req, timeout=12) as r:
                raw = json.loads(r.read().decode("utf-8", errors="replace"))

            s_data = raw.get("s", {})
            rows   = list(s_data.values()) if isinstance(s_data, dict) else list(s_data)
            spots  = []
            for row in rows:
                if len(row) < 2:
                    continue
                try:
                    freq_khz = float(row[1])
                except (ValueError, TypeError):
                    continue
                if freq_khz <= 0 or freq_khz > 60_000:
                    continue
                call    = str(row[0]).strip().upper()
                spotter = str(row[2]).strip().upper() if len(row) > 2 else ""
                comment = _html.unescape(str(row[3]).strip()) if len(row) > 3 else ""
                # Tijd: "1928z 10 Apr" → "19:28"
                t_raw   = str(row[4]).strip() if len(row) > 4 else ""
                d       = t_raw[:4]
                tstr    = f"{d[:2]}:{d[2:]}" if len(d) == 4 and d.isdigit() else "—"
                band    = _freq_to_band_name(freq_khz)
                spots.append({
                    "time":     tstr,
                    "dx":       call,
                    "freq_khz": freq_khz,
                    "band":     band,
                    "spotter":  spotter,
                    "comment":  comment,
                })
            spots.reverse()   # nieuwste eerst
            self.spots_ready.emit(spots)
        except Exception:
            self.spots_ready.emit([])


def _freq_to_band_name(freq_khz: float) -> str:
    if freq_khz < 2100:  return "160m"
    if freq_khz < 5000:  return "80m"
    if freq_khz < 7500:  return "40m"
    if freq_khz < 11000: return "30m"
    if freq_khz < 15500: return "20m"
    if freq_khz < 19000: return "17m"
    if freq_khz < 22000: return "15m"
    if freq_khz < 26000: return "12m"
    if freq_khz < 32000: return "10m"
    return "6m"


class _DXSignals(QObject):
    spots_updated = Signal(list)


class DXSpotsLayer(QGraphicsItem):
    """DX cluster spots met bandkleur. Pollt DXWatch elke 2 min."""

    def __init__(self):
        super().__init__()
        self.setZValue(6)
        self._spots: list      = []
        self._raw_spots: list  = []
        self._spot_dicts: list = []
        self._own_only: bool   = False
        self._qth_lat: float  = 52.0
        self._qth_lon: float  = 5.0
        self._lock = threading.Lock()
        self._signals = _DXSignals()
        self.spots_updated = self._signals.spots_updated
        self._fetch_thread = None
        self._label_font_size: int = 7
        self._anim_phase: float = 0.0   # rijdende dash-offset voor animatie

        # Animatietimer — 20 fps, beweegt de streepjes langs de lijn
        self._anim_timer = QTimer()
        self._anim_timer.timeout.connect(self._anim_tick)
        self._anim_timer.start(50)

    def _anim_tick(self):
        self._anim_phase = (self._anim_phase + 1.2) % 18.0
        with self._lock:
            has_spots = bool(self._spots)
        if has_spots:
            self.update()

    def set_label_font_size(self, size: int):
        self._label_font_size = max(6, size)
        self.update()

        self._timer = QTimer()
        self._timer.timeout.connect(self._fetch)
        self._timer.start(120_000)
        QTimer.singleShot(4000, self._fetch)

    def _fetch(self):
        if self._fetch_thread is not None:
            return                   # vorige fetch loopt nog
        t = _DXFetchThread(None)
        t.spots_ready.connect(self._on_spots)
        t.finished.connect(self._on_fetch_done)
        t.finished.connect(t.deleteLater)
        self._fetch_thread = t       # bewaar referentie
        t.start()

    def _on_fetch_done(self):
        self._fetch_thread = None

    def set_continent_filter(self, own_only: bool,
                             qth_lat: float, qth_lon: float):
        """Pas zichtbaarheid op kaart aan op basis van continent-filter."""
        self._own_only = own_only
        self._qth_lat  = qth_lat
        self._qth_lon  = qth_lon
        self._refilter()

    def _refilter(self):
        """Herbereken zichtbare spots op kaart vanuit ruwe data."""
        from .panels5 import _callsign_continent, _qth_to_continent
        map_spots = []
        my_cont = (_qth_to_continent(self._qth_lat, self._qth_lon)
                   if self._own_only else None)
        for raw in self._raw_spots:
            dx_lat, dx_lon, call, freq, de_lat, de_lon, spotter = raw
            if my_cont and _callsign_continent(spotter) != my_cont:
                continue
            map_spots.append((dx_lat, dx_lon, call, freq, de_lat, de_lon))
        with self._lock:
            self._spots = map_spots
        self.update()

    def find_spot_near(self, scene_x: float, scene_y: float,
                       radius: float = 14.0) -> dict | None:
        """Geef de dichtstbijzijnde DX-spot terug als die binnen radius px valt."""
        best_d, best = radius * radius, None
        with self._lock:
            visible = list(self._spots)
        raw_by_call = {r[2]: r for r in self._raw_spots}
        for lat, lon, call, freq, *_ in visible:
            pt = _xy(lat, lon)
            d = (pt.x() - scene_x) ** 2 + (pt.y() - scene_y) ** 2
            if d < best_d:
                best_d, best = d, (call, freq, raw_by_call.get(call))
        if best:
            call, freq, raw = best
            info = {
                "call": call,
                "freq_khz": freq,
                "spotter": raw[6] if raw else "",
                "comment": "",
                "time": "",
            }
            # Zoek volledige data op in de dict-lijst
            for s in self._spot_dicts:
                if s.get("dx", "").upper() == call.upper():
                    info["comment"] = s.get("comment", "")
                    info["time"]    = s.get("time", "")
                    info["band"]    = s.get("band", "")
                    break
            return info
        return None

    def _on_spots(self, spots: list):
        """spots = [{time, dx, freq_khz, band, spotter, comment}, ...]"""
        self._spot_dicts = spots   # bewaar voor info-lookup bij klik
        raw = []
        for s in spots:
            call    = s.get("dx", "")
            freq    = s.get("freq_khz", 0.0)
            spotter = s.get("spotter", "")
            dx_loc  = _call_to_latlon(call)
            de_loc  = _call_to_latlon(spotter)
            if dx_loc:
                raw.append((
                    dx_loc[0], dx_loc[1], call, freq,
                    de_loc[0] if de_loc else None,
                    de_loc[1] if de_loc else None,
                    spotter,
                ))
        self._raw_spots = raw
        self._refilter()
        self._signals.spots_updated.emit(spots)  # ruwe dicts voor tabel

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, MAP_W, MAP_H)

    def paint(self, painter: QPainter, option, widget=None):
        with self._lock:
            spots = list(self._spots)

        painter.setRenderHint(QPainter.Antialiasing)
        font = QFont("Segoe UI", self._label_font_size)
        painter.setFont(font)

        phase = self._anim_phase
        for lat, lon, call, freq, de_lat, de_lon in spots:
            color = _band_color(freq)
            pt    = _xy(lat, lon)

            # ── Geanimeerde verbindingslijn spotter → DX ─────────────────────
            if de_lat is not None:
                de_pt = _xy(de_lat, de_lon)

                # Schaduwlijn voor contrast
                shadow_pen = QPen(QColor(0, 0, 0, 60), 3.5)
                shadow_pen.setCapStyle(Qt.RoundCap)
                painter.setPen(shadow_pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawLine(de_pt, pt)

                # Geanimeerde streepjes — rijden van spotter (DE) naar DX
                line_color = QColor(color.red(), color.green(), color.blue(), 200)
                line_pen = QPen(line_color, 2.2)
                line_pen.setCapStyle(Qt.RoundCap)
                line_pen.setStyle(Qt.CustomDashLine)
                line_pen.setDashPattern([5.0, 4.0])
                line_pen.setDashOffset(phase)
                painter.setPen(line_pen)
                painter.drawLine(de_pt, pt)

                # ── Spotter (DE) eindpunt — kleine open cirkel ───────────────
                painter.setPen(QPen(QColor(255, 255, 255, 180), 1.2))
                painter.setBrush(QBrush(color.darker(130)))
                painter.drawEllipse(de_pt, 3.5, 3.5)

            # ── DX station eindpunt — gevulde cirkel met halo ────────────────
            painter.setPen(QPen(QColor(255, 255, 255, 180), 1.5))
            painter.setBrush(QBrush(color))
            painter.drawEllipse(pt, 6, 6)

            # ── Callsign label ───────────────────────────────────────────────
            painter.setPen(color.lighter(170))
            painter.drawText(pt + QPointF(8, 5), call[:9])


# ── PSKReporter Layer ──────────────────────────────────────────────────────────

def _maidenhead_to_latlon(locator: str) -> tuple[float, float] | None:
    """Maidenhead locator → (lat, lon) middelpunt van het veld."""
    if not locator or len(locator) < 4:
        return None
    loc = locator.upper()
    try:
        lon = (ord(loc[0]) - ord('A')) * 20 - 180
        lat = (ord(loc[1]) - ord('A')) * 10 - 90
        lon += int(loc[2]) * 2
        lat += int(loc[3])
        if len(loc) >= 6:
            lon += (ord(loc[4]) - ord('A')) * 2 / 24
            lat += (ord(loc[5]) - ord('A')) / 24
            lon += 1 / 24     # middelpunt subsquare
            lat += 0.5 / 24
        else:
            lon += 1.0        # middelpunt square
            lat += 0.5
        return (lat, lon)
    except (ValueError, IndexError):
        return None


class _PSKFetchThread(QThread):
    """Haalt PSKReporter ontvangstmeldingen op (FT8/FT4/digital, laatste 15 min)."""
    ready = Signal(list)

    _URL = ("https://pskreporter.info/cgi-bin/pskquery5.pl"
            "?encap=0&callback=_&statistics=0&noactive=1&nolocator=1"
            "&lastseenminutes=15&rronly=1&flowstart=0&appcontact=HAMIOS5")

    def run(self):
        try:
            req = urllib.request.Request(
                self._URL, headers={"User-Agent": "HAMIOS/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                raw = r.read().decode("utf-8", errors="replace")

            # Respons: JSON-object met "receptionReport" key
            data    = json.loads(raw)
            items   = data.get("receptionReport", [])
            reports = []

            for item in items:
                tx_loc_str = item.get("senderLocator",   "")
                rx_loc_str = item.get("receiverLocator", "")
                freq_hz    = item.get("frequency", 0)
                snr        = item.get("sNR", 0)
                mode       = str(item.get("mode", ""))
                tx_call    = str(item.get("senderCallsign",   ""))
                rx_call    = str(item.get("receiverCallsign", ""))

                if not freq_hz:
                    continue

                # Maidenhead locator geeft precieze coördinaten
                tx_loc = _maidenhead_to_latlon(tx_loc_str)
                rx_loc = _maidenhead_to_latlon(rx_loc_str)

                # Fallback op DXCC-code als locator ontbreekt
                if not tx_loc:
                    tx_loc = _call_to_latlon(item.get("senderDXCCCode", tx_call))
                if not rx_loc:
                    rx_loc = _call_to_latlon(rx_call)

                if tx_loc and rx_loc:
                    reports.append((tx_loc, rx_loc, freq_hz / 1000.0,
                                    snr, mode, tx_call, rx_call))

            self.ready.emit(reports)
        except Exception:
            self.ready.emit([])


class PSKReporterLayer(QGraphicsItem):
    """PSKReporter ontvangst-lijnen — toont actuele digitale propagatiepaden."""

    def __init__(self):
        super().__init__()
        self.setZValue(5.5)   # tussen DX spots (6) en lightning (5)
        self._reports: list = []
        self._lock = threading.Lock()
        self._fetch_thread = None

        self._timer = QTimer()
        self._timer.timeout.connect(self._fetch)
        self._timer.start(5 * 60 * 1000)   # elke 5 minuten
        QTimer.singleShot(6000, self._fetch)

    def _fetch(self):
        if self._fetch_thread is not None:
            return
        t = _PSKFetchThread()
        t.ready.connect(self._on_data)
        t.finished.connect(lambda: setattr(self, "_fetch_thread", None))
        t.finished.connect(t.deleteLater)
        self._fetch_thread = t
        t.start()

    def _on_data(self, reports: list):
        with self._lock:
            self._reports = reports
        self.update()

    def find_report_near(self, scene_x: float, scene_y: float,
                         radius: float = 14.0) -> dict | None:
        """Geef het dichtstbijzijnde PSKReporter-rapport als dat binnen radius valt.
        Controleert zowel het TX-punt als het RX-punt."""
        best_d = radius * radius
        best   = None
        with self._lock:
            reports = list(self._reports)
        for tx_loc, rx_loc, freq_khz, snr, mode, tx, rx in reports:
            for loc, role in ((tx_loc, "TX"), (rx_loc, "RX")):
                pt = _xy(loc[0], loc[1])
                d  = (pt.x() - scene_x) ** 2 + (pt.y() - scene_y) ** 2
                if d < best_d:
                    best_d = d
                    best   = {
                        "tx": tx, "rx": rx,
                        "freq_khz": freq_khz, "snr": snr, "mode": mode,
                        "role": role,
                        "band": _freq_to_band_name(freq_khz),
                    }
        return best

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, MAP_W, MAP_H)

    def paint(self, painter: QPainter, option, widget=None):
        with self._lock:
            reports = list(self._reports)

        if not reports:
            return

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)

        for tx_loc, rx_loc, freq_khz, snr, mode, tx, rx in reports:
            color = _band_color(freq_khz)

            # Alpha op basis van SNR: sterkere signalen zijn helderder
            snr_norm = max(0.0, min(1.0, (snr + 30) / 50.0))
            alpha = int(25 + snr_norm * 55)    # 25–80
            lw    = 0.6 + snr_norm * 0.8       # 0.6–1.4 px

            tx_pt = _xy(tx_loc[0], tx_loc[1])
            rx_pt = _xy(rx_loc[0], rx_loc[1])

            c = QColor(color.red(), color.green(), color.blue(), alpha)
            painter.setPen(QPen(c, lw))
            painter.drawLine(tx_pt, rx_pt)

            # Kleine stip op TX-locatie
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(color.red(), color.green(),
                                           color.blue(), min(alpha + 40, 180))))
            painter.drawEllipse(tx_pt, 2.0, 2.0)
            painter.setBrush(Qt.NoBrush)
