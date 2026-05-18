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
_TLE_CACHE = os.path.join(_HERE, "hamios_tle.json")

TLE_GROUPS = {
    "Amateur": "https://celestrak.org/NORAD/elements/gp.php?GROUP=amateur&FORMAT=tle",
    "ISS":     "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=tle",
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


def fetch_tle_group(url: str) -> list[tuple[str, str, str]]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "HAMIOS/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return parse_tle_text(r.read().decode("utf-8", errors="replace"))
    except Exception:
        return []


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

    def set_enabled(self, on: bool):
        """Start of stop de WebSocket-verbinding én maak de overlay zichtbaar/onzichtbaar."""
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
        self.setVisible(False)

    def set_qth(self, lat: float, lon: float):
        self._qth_lat = lat
        self._qth_lon = lon
        self.update()

    def set_radius_km(self, km: int):
        self._radius_km = km
        self.setVisible(km > 0)
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
        painter.setFont(QFont("Segoe UI", 7))
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
                _draw_path(painter, past, QPen(color.darker(160), 0.8, Qt.DashLine))
                _draw_path(painter, fwd,  QPen(color, 1.2))

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

# Compact DXCC prefix → (lat, lon)
_DXCC: dict[str, tuple[float, float]] = {
    # Noord-Amerika
    "W":   (38.0, -97.0), "K":   (38.0, -97.0), "N":   (38.0, -97.0),
    "AA":  (38.0, -97.0), "AB":  (38.0, -97.0), "AC":  (38.0, -97.0),
    "AD":  (38.0, -97.0), "AE":  (38.0, -97.0), "AF":  (38.0, -97.0),
    "AG":  (38.0, -97.0), "AH":  (38.0, -97.0), "AI":  (38.0, -97.0),
    "AJ":  (38.0, -97.0), "AK":  (38.0, -97.0),
    "VE":  (56.0, -96.0), "VA":  (56.0, -96.0),
    "KH6": (20.5,-157.0), "KL":  (64.0,-152.0),
    "XE":  (23.0,-102.0),
    # Zuid-Amerika
    "PY":  (-15.0, -50.0), "PU": (-15.0, -50.0), "PP": (-15.0, -50.0),
    "LU":  (-34.0, -64.0), "CE": (-30.0, -71.0), "OA": (-10.0, -75.0),
    "HC":  ( -1.8, -78.0), "YV": (  8.0, -66.0), "CX": (-32.8, -56.0),
    "ZP":  (-23.0, -58.0), "CP": (-16.0, -64.0),
    # West-Europa
    "DL":  (52.0, 10.0), "F":  (46.0,  2.0), "G":  (52.0,  -2.0),
    "GW":  (52.0, -4.0), "GM": (57.0, -4.0), "GI": (54.5,  -6.5),
    "I":   (42.0, 12.0), "IT9":(37.5, 14.0), "IS": (40.0,   9.0),
    "SP":  (52.0, 21.0), "SQ": (52.0, 21.0),
    "OM":  (48.7, 19.0), "OK": (50.0, 15.0), "HA": (47.0,  19.0),
    "OH":  (64.0, 26.0), "SM": (62.0, 17.0), "LA": (62.0,  10.0),
    "OZ":  (56.0, 10.0), "PA": (52.3,  5.3), "ON": (50.5,   4.5),
    "HB":  (47.0,  8.0), "OE": (47.5, 14.5),
    "EA":  (40.0, -4.0), "EA8":(28.3,-14.0),
    "CT":  (39.5, -8.0), "CS": (39.5, -8.0),
    "YO":  (46.0, 25.0), "LZ": (43.0, 25.0), "SV": (38.0,  23.0),
    "SV9": (35.3, 25.0), "TA": (39.0, 35.0),
    "TF":  (65.0,-19.0), "EI": (53.0, -8.0),
    "YU":  (44.0, 21.0), "9A": (45.0, 16.0), "S5": (46.0,  15.0),
    "YL":  (57.0, 25.0), "LY": (56.0, 24.0), "ES": (59.0,  25.0),
    "5B":  (35.0, 33.0), "9H": (35.9, 14.5),
    # Rusland
    "UA":  (55.0, 60.0), "RA":  (55.0, 60.0), "RZ": (55.0, 60.0),
    "R":   (55.0, 60.0), "UA9": (60.0, 90.0), "UA0":(60.0,130.0),
    # Midden-Oosten
    "4X":  (31.5, 34.8), "4Z": (31.5, 34.8),
    "A9":  (26.0, 50.5), "A4": (23.0, 57.0), "A6": (24.5, 54.5),
    "HZ":  (25.0, 45.0), "JY": (31.0, 36.0), "EP": (32.0, 53.0),
    "AP":  (30.0, 70.0),
    # Azië
    "JA":  (36.0,138.0), "HL": (37.0,127.0), "DS": (37.0,127.0),
    "BY":  (35.0,104.0), "BA": (35.0,104.0), "BD": (35.0,104.0),
    "BG":  (35.0,104.0),
    "VR":  (22.3,114.2), "BV": (23.5,121.0),
    "9V":  ( 1.3,103.8), "VU": (20.0, 77.0),
    "HS":  (13.0,101.0), "DU": (13.0,122.0),
    "YB":  (-5.0,120.0), "YC": (-5.0,120.0),
    # Oceanië
    "VK":  (-25.0,135.0), "ZL": (-40.0,175.0),
    "FK":  (-21.0,165.0), "FO": (-18.0,-149.0),
    "KH0": (15.2, 145.7), "H44":(-9.0, 160.0),
    # Afrika
    "ZS":  (-30.0, 25.0), "ZR": (-30.0, 25.0), "ZU": (-30.0, 25.0),
    "V5":  (-22.0, 17.0), "A2": (-22.0, 24.0), "Z2": (-20.0, 30.0),
    "5H":  ( -6.0, 35.0), "5Z": (  1.0, 38.0), "5X": (  1.3, 32.0),
    "ET":  (  9.0, 38.7), "SU": ( 26.0, 30.0),
    "CN":  ( 32.0, -6.0), "7X": ( 28.0,  2.0), "TS": (34.0, 9.0),
    "5A":  ( 27.0, 17.0), "3B8":(-20.2, 57.5),
    # Eilanden
    "ZD8": ( -7.9,-14.4), "VP9":(32.3,-64.8),
    "VP8": (-51.7,-57.8), "3DA":(-26.3, 31.5),
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
    _URL = "https://dxwatch.com/dxsd1/s.php?s=0&r=30&cdxc=0"

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
        self._spots: list = []
        self._lock = threading.Lock()
        self._signals = _DXSignals()
        self.spots_updated = self._signals.spots_updated
        self._fetch_thread = None
        self._label_font_size: int = 7

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

    def _on_spots(self, spots: list):
        """spots = [{time, dx, freq_khz, band, spotter, comment}, ...]"""
        map_spots = []
        for s in spots:
            call    = s.get("dx", "")
            freq    = s.get("freq_khz", 0.0)
            spotter = s.get("spotter", "")
            dx_loc  = _call_to_latlon(call)
            de_loc  = _call_to_latlon(spotter)
            if dx_loc:
                map_spots.append((
                    dx_loc[0], dx_loc[1], call, freq,
                    de_loc[0] if de_loc else None,
                    de_loc[1] if de_loc else None,
                ))
        with self._lock:
            self._spots = map_spots
        self._signals.spots_updated.emit(spots)  # ruwe dicts voor tabel
        self.update()

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, MAP_W, MAP_H)

    def paint(self, painter: QPainter, option, widget=None):
        with self._lock:
            spots = list(self._spots)

        painter.setRenderHint(QPainter.Antialiasing)
        font = QFont("Segoe UI", self._label_font_size)
        painter.setFont(font)

        for lat, lon, call, freq, de_lat, de_lon in spots:
            color = _band_color(freq)
            pt    = _xy(lat, lon)

            # Verbindingslijn spotter → DX (gestippeld)
            if de_lat is not None:
                de_pt = _xy(de_lat, de_lon)
                painter.setPen(QPen(color.darker(180), 0.5, Qt.DotLine))
                painter.setBrush(Qt.NoBrush)
                painter.drawLine(de_pt, pt)

            # DX station stip — 5px, wit randje voor zichtbaarheid op donkere kaart
            painter.setPen(QPen(QColor(255, 255, 255, 120), 1))
            painter.setBrush(QBrush(color))
            painter.drawEllipse(pt, 5, 5)

            # Callsign label
            painter.setPen(color.lighter(160))
            painter.drawText(pt + QPointF(7, 4), call[:9])
