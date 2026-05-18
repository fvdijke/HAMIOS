"""
HAMIOS v5 Sprint 2 — Kaart-paneel (PySide6 + QGraphicsView)

Hardware-accelerated wereldkaart via QGraphicsScene.
Lagen (z-volgorde):
  0  BaseMapItem       — NASA equirectangulaire kaart
  1  NightOverlayItem  — dag/nacht terminator
  2  GraylineItem      — grayline (~1000 km band)
  3  AuroraItem        — K-index gebaseerde aurora-ovaal
  4  SatelliteLayer    — satelliet-posities + paden
  5  LightningLayer    — Blitzortung inslagen (real-time)
  6  DXSpotsLayer      — DX cluster spots
  7  OverlayItems      — QTH-marker, GC-pad
"""

import math
import os
import datetime
import threading

from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsItem,
    QGraphicsPixmapItem, QGraphicsEllipseItem,
    QGraphicsLineItem, QWidget, QVBoxLayout, QLabel
)
from PySide6.QtCore import (
    Qt, QRectF, QPointF, QTimer, Signal, QObject, QThread
)
from PySide6.QtGui import (
    QPixmap, QPainter, QColor, QPen, QBrush, QTransform,
    QImage, QFont, QPainterPath
)

from .theme import ACCENT, TEXT_DIM, BG_ROOT
from . import layers as _layers

# Kaartbestand (gedeeld met v4)
from ._appdir import APP_DIR as _HERE
MAP_FILE = os.path.join(_HERE, "worldmap_eq.jpg")

# Map dimensions (equirectangular, 2:1)
MAP_W = 2048
MAP_H = 1024


# ── Coördinaat-helpers ────────────────────────────────────────────────────────

def latlon_to_scene(lat: float, lon: float,
                    w: float = MAP_W, h: float = MAP_H) -> QPointF:
    """Geografische coördinaten → scene-pixel."""
    x = (lon + 180) / 360 * w
    y = (90 - lat) / 180 * h
    return QPointF(x, y)


def scene_to_latlon(x: float, y: float,
                    w: float = MAP_W, h: float = MAP_H) -> tuple[float, float]:
    """Scene-pixel → (lat, lon)."""
    lon = x / w * 360 - 180
    lat = 90 - y / h * 180
    return lat, lon


# ── Overlay items ─────────────────────────────────────────────────────────────

class GraticuleItem(QGraphicsItem):
    """Lat/lon rooster elke 30°, met graadlabels. z=0.5"""

    def __init__(self):
        super().__init__()
        self.setZValue(0.5)
        self._font_size = 8

    def set_font_size(self, size: int):
        self._font_size = max(6, size)
        self.update()

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, MAP_W, MAP_H)

    def paint(self, painter: QPainter, option, widget=None):
        pen = QPen(QColor(80, 120, 170, 180), 1.0)
        lbl = QColor(180, 200, 220, 220)
        f   = QFont("Segoe UI", self._font_size)
        painter.setFont(f)
        painter.setRenderHint(QPainter.Antialiasing, False)
        for lat in range(-60, 90, 30):
            y = (90 - lat) / 180 * MAP_H
            painter.setPen(pen)
            painter.drawLine(QPointF(0, y), QPointF(MAP_W, y))
            painter.setPen(lbl)
            painter.drawText(QPointF(3, y - 1), f"{lat:+d}°")
        for lon in range(-150, 181, 30):
            x = (lon + 180) / 360 * MAP_W
            painter.setPen(pen)
            painter.drawLine(QPointF(x, 0), QPointF(x, MAP_H))
            if lon < 150:
                painter.setPen(lbl)
                painter.drawText(QPointF(x + 2, 11), f"{lon:+d}°")


class MaidenheadItem(QGraphicsItem):
    """Maidenhead locatorraster 20°×10° met 2-letter labels. z=0.6"""

    def __init__(self):
        super().__init__()
        self.setZValue(0.6)
        self._font_size = 8

    def set_font_size(self, size: int):
        self._font_size = max(6, size)
        self.update()

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, MAP_W, MAP_H)

    def paint(self, painter: QPainter, option, widget=None):
        grid_clr = QColor(100, 160, 220, 140)
        lbl_clr  = QColor(160, 210, 255, 200)
        pen = QPen(grid_clr, 0.8, Qt.DashLine)
        painter.setPen(pen)
        f = QFont("Segoe UI", self._font_size)
        painter.setFont(f)

        # Verticale lijnen elke 20° lon
        for lon_i in range(19):
            gx = lon_i * 20 / 360 * MAP_W
            painter.setPen(pen)
            painter.drawLine(QPointF(gx, 0), QPointF(gx, MAP_H))

        # Horizontale lijnen elke 10° lat
        for lat_i in range(19):
            gy = lat_i * 10 / 180 * MAP_H
            painter.setPen(pen)
            painter.drawLine(QPointF(0, gy), QPointF(MAP_W, gy))

        # Labels midden van elk veld
        for lon_i in range(18):
            for lat_i in range(18):
                lon_c = -180 + lon_i * 20 + 10
                lat_c =   90 - (lat_i * 10 + 5)
                cx = (lon_c + 180) / 360 * MAP_W
                cy = (90 - lat_c) / 180 * MAP_H
                lbl = chr(ord('A') + lon_i) + chr(ord('A') + (17 - lat_i))
                painter.setPen(lbl_clr)
                painter.drawText(
                    QRectF(cx - 14, cy - 7, 28, 14),
                    Qt.AlignCenter, lbl)


class GraylineItem(QGraphicsItem):
    """Graylijn-band (~1000 km schemering). z=2"""

    def __init__(self):
        super().__init__()
        self.setZValue(2)
        self._image: QImage | None = None

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, MAP_W, MAP_H)

    def paint(self, painter: QPainter, option, widget=None):
        if self._image:
            painter.drawImage(0, 0, self._image)


class SunMarkerItem(QGraphicsItem):
    """Gele zon-markering op de geocentrische zonpositie. z=3.5"""

    def __init__(self):
        super().__init__()
        self.setZValue(3.5)
        self._update_position()

    def _update_position(self):
        lat, lon = _subsolar_point()
        pt = latlon_to_scene(lat, lon)
        self.setPos(pt)

    def boundingRect(self) -> QRectF:
        return QRectF(-12, -12, 24, 24)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        # Stralen
        pen = QPen(QColor(255, 215, 0, 180), 1.2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        for angle in range(0, 360, 45):
            r = math.radians(angle)
            cx, cy = math.cos(r), math.sin(r)
            painter.drawLine(QPointF(8*cx, 8*cy), QPointF(11*cx, 11*cy))
        # Zon-cirkel
        painter.setBrush(QBrush(QColor(255, 215, 0)))
        painter.setPen(QPen(QColor(200, 160, 0), 1))
        painter.drawEllipse(QPointF(0, 0), 6, 6)


class MoonMarkerItem(QGraphicsItem):
    """Maan-markering met maanfase-icoon en QTH-zichtbaarheid. z=3.7"""

    _ICON_SIZE = 22

    def __init__(self):
        super().__init__()
        self.setZValue(3.7)
        self._icon: QImage | None = None
        self._elevation: float = 0.0   # graden boven/onder horizon t.o.v. QTH
        self._qth_lat: float = 52.0
        self._qth_lon: float = 5.0
        self._update_position()

    def set_qth(self, lat: float, lon: float):
        self._qth_lat = lat
        self._qth_lon = lon
        self._update_position()

    def _update_position(self):
        lat, lon = _submoon_point()
        self.setPos(latlon_to_scene(lat, lon))
        phase = _moon_phase_deg()
        self._icon = _render_moon_icon(self._ICON_SIZE, phase)
        self._elevation = _moon_elevation(self._qth_lat, self._qth_lon)
        tip = (f"Maan  fase {int((phase % 360) / 360 * 100)}%  "
               f"{'▲' if self._elevation >= 0 else '▼'} {abs(self._elevation):.0f}°"
               f" {'boven' if self._elevation >= 0 else 'onder'} horizon")
        self.setToolTip(tip)
        self.update()

    def boundingRect(self) -> QRectF:
        s = self._ICON_SIZE
        return QRectF(-s / 2 - 2, -s / 2 - 2, s + 4, s + 4)

    def paint(self, painter: QPainter, option, widget=None):
        if not self._icon:
            return
        s = self._ICON_SIZE
        painter.setRenderHint(QPainter.Antialiasing)

        above = self._elevation >= 0

        # Boven horizon: helder; onder horizon: getemperd
        if above:
            painter.setOpacity(1.0)
        else:
            painter.setOpacity(0.35)
        painter.drawImage(QPointF(-s / 2, -s / 2), self._icon)
        painter.setOpacity(1.0)

        # Kleine indicator: ▲ of ▼ rechtsonder het icoon
        elev_abs = abs(self._elevation)
        clr = QColor(180, 220, 255, 200) if above else QColor(100, 110, 130, 200)
        painter.setPen(clr)
        painter.setFont(QFont("Segoe UI", 5))
        arrow = "▲" if above else "▼"
        painter.drawText(QRectF(s // 2 - 8, s // 2 - 8, 10, 10),
                         Qt.AlignCenter, arrow)


class AuroraItem(QGraphicsItem):
    """Aurora-ovaal gebaseerd op K-index (geomagnetische dipool-model). z=3"""

    # Geomagnetische dipool-polen (IGRF-2025)
    _POLES = [(80.65, -72.65), (-80.65, 107.35)]

    def __init__(self):
        super().__init__()
        self.setZValue(3)
        self._k = 2.0

    def set_k_index(self, k: float):
        self._k = max(0.0, min(9.0, k))
        self.update()

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, MAP_W, MAP_H)

    def paint(self, painter: QPainter, option, widget=None):
        k = self._k
        if k < 3:
            color = QColor(60, 200, 60)
        elif k < 6:
            color = QColor(255, 200, 0)
        else:
            color = QColor(220, 60, 20)

        alpha  = min(210, int(110 + k * 11))
        lw     = max(1.5, 1.5 + k * 0.5)
        theta  = math.radians(23.0 + k * 2.5)
        N      = 180

        painter.setRenderHint(QPainter.Antialiasing)

        for pole_lat, pole_lon in self._POLES:
            phi_p = math.radians(pole_lat)
            lam_p = math.radians(pole_lon)
            pts   = []
            for i in range(N + 1):
                psi     = 2 * math.pi * i / N
                geo_lat = math.asin(
                    math.sin(phi_p) * math.cos(theta) +
                    math.cos(phi_p) * math.sin(theta) * math.cos(psi))
                geo_lon = lam_p + math.atan2(
                    math.sin(theta) * math.sin(psi),
                    math.cos(phi_p) * math.cos(theta) -
                    math.sin(phi_p) * math.sin(theta) * math.cos(psi))
                lat_d = math.degrees(geo_lat)
                lon_d = math.degrees(geo_lon)
                while lon_d >  180: lon_d -= 360
                while lon_d < -180: lon_d += 360
                pts.append(latlon_to_scene(lat_d, lon_d))

            # Teken in segmenten (breuk bij antimeridian)
            pen = QPen(QColor(color.red(), color.green(), color.blue(), alpha), lw)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            prev = None
            for pt in pts:
                if prev and abs(pt.x() - prev.x()) < MAP_W * 0.3:
                    painter.drawLine(prev, pt)
                prev = pt


class NightOverlayItem(QGraphicsItem):
    """Dag/nacht terminator als semi-transparant overlay."""

    def __init__(self):
        super().__init__()
        self.setZValue(1)
        self._image: QImage | None = None
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations, False)

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, MAP_W, MAP_H)

    def paint(self, painter: QPainter, option, widget=None):
        if self._image:
            painter.drawImage(0, 0, self._image)

    def update_night(self):
        """Herteken de nacht-overlay op basis van huidige zonpositie."""
        sun_lat, sun_lon = _subsolar_point()
        img = QImage(MAP_W, MAP_H, QImage.Format_ARGB32)
        img.fill(Qt.transparent)

        sun_lat_r = math.radians(sun_lat)
        for ix in range(0, MAP_W, 2):   # stap 2 voor snelheid
            lon = ix / MAP_W * 360 - 180
            dlon = math.radians(lon - sun_lon)
            for iy in range(0, MAP_H, 2):
                lat = 90 - iy / MAP_H * 180
                lat_r = math.radians(lat)
                cos_a = (math.sin(lat_r) * math.sin(sun_lat_r) +
                         math.cos(lat_r) * math.cos(sun_lat_r) * math.cos(dlon))
                if cos_a < 0:
                    depth = min(1.0, -cos_a * 3)
                    alpha = int(140 * depth)
                    img.setPixelColor(ix, iy, QColor(0, 8, 20, alpha))
                    if ix + 1 < MAP_W:
                        img.setPixelColor(ix + 1, iy, QColor(0, 8, 20, alpha))
                    if iy + 1 < MAP_H:
                        img.setPixelColor(ix, iy + 1, QColor(0, 8, 20, alpha))
                    if ix + 1 < MAP_W and iy + 1 < MAP_H:
                        img.setPixelColor(ix + 1, iy + 1, QColor(0, 8, 20, alpha))

        self._image = img
        self.update()


class QTHMarkerItem(QGraphicsItem):
    """Blauw kruisje voor de QTH-positie."""

    def __init__(self, lat: float = 52.0, lon: float = 5.0):
        super().__init__()
        self.setZValue(8)
        self._pos = latlon_to_scene(lat, lon)
        self.setPos(self._pos)

    def set_qth(self, lat: float, lon: float):
        self._pos = latlon_to_scene(lat, lon)
        self.setPos(self._pos)
        self.update()

    def boundingRect(self) -> QRectF:
        return QRectF(-12, -12, 24, 24)

    def paint(self, painter: QPainter, option, widget=None):
        pen = QPen(QColor(80, 180, 255), 2)
        painter.setPen(pen)
        painter.drawLine(-10, 0, 10, 0)
        painter.drawLine(0, -10, 0, 10)


# ── Achtergrond render thread (bewaard als referentie, niet meer gebruikt) ─────

class NightRenderWorker(QObject):
    finished = Signal(QImage, QImage)

    def run(self):
        sun_lat, sun_lon = _subsolar_point()
        # 64×32 = 2048 pixels — snel, gladde upscale via SmoothTransformation
        W, H = 64, 32

        night = QImage(W, H, QImage.Format_ARGB32)
        night.fill(Qt.transparent)
        gray  = QImage(W, H, QImage.Format_ARGB32)
        gray.fill(Qt.transparent)

        sun_lat_r = math.radians(sun_lat)
        cos_sun   = math.cos(sun_lat_r)
        sin_sun   = math.sin(sun_lat_r)
        GRAY_HALF = 0.155

        # setPixelColor met QColor is type-safe (vermijdt signed/unsigned overflow)
        for ix in range(W):
            lon      = ix / W * 360 - 180
            cos_dlon = math.cos(math.radians(lon - sun_lon))
            for iy in range(H):
                lat_r = math.radians(90 - iy / H * 180)
                cos_a = (math.sin(lat_r) * sin_sun +
                         math.cos(lat_r) * cos_sun * cos_dlon)

                if cos_a < 0:
                    # Nacht: donkerblauw, hoog genoeg alpha om zichtbaar te zijn op donkere kaart
                    depth = min(1.0, -cos_a * 2.5)
                    alpha = int(200 * depth)
                    night.setPixelColor(ix, iy, QColor(0, 10, 50, alpha))

                ca = abs(cos_a)
                if ca < GRAY_HALF:
                    # Grayline: goudgeel, duidelijk zichtbaar
                    a = int(130 * (1 - ca / GRAY_HALF))
                    gray.setPixelColor(ix, iy, QColor(200, 170, 50, a))

        tf = Qt.SmoothTransformation
        self.finished.emit(
            night.scaled(MAP_W, MAP_H, Qt.IgnoreAspectRatio, tf),
            gray.scaled( MAP_W, MAP_H, Qt.IgnoreAspectRatio, tf)
        )


# ── Kaart herinkleuring (v4-stijl) ───────────────────────────────────────────

class _MapColorizeThread(QThread):
    """Herinkleurt de NASA kaart naar v4-stijl (oceaan/land donkerblauw)."""
    done = Signal(QPixmap)

    _OCEAN = (27,  58,  92)   # donkerblauw
    _LAND  = (45,  96, 128)   # blauwgrijs

    def __init__(self, source: QPixmap):
        super().__init__()
        self._pix = source

    def run(self):
        img    = self._pix.toImage().convertToFormat(QImage.Format_RGB32)
        W, H   = img.width(), img.height()
        ptr    = img.bits()
        data   = bytearray(ptr)            # Format_RGB32 LE: B G R 0xFF per pixel
        OR, OG, OB = self._OCEAN
        LR, LG, LB = self._LAND
        for i in range(0, len(data), 4):
            b, g, r = data[i], data[i+1], data[i+2]
            if b > r + 15 and b > g:       # oceaan: blauw dominant
                data[i], data[i+1], data[i+2] = OB, OG, OR
            else:                           # land
                data[i], data[i+1], data[i+2] = LB, LG, LR
        result = QImage(bytes(data), W, H, W * 4, QImage.Format_RGB32)
        self.done.emit(QPixmap.fromImage(result))


# ── Hoofd MapView ──────────────────────────────────────────────────────────────

class MapView(QGraphicsView):
    """
    Hardware-accelerated kaartweergave.
    - Zoom: scroll-wheel
    - Pan: klik + sleep
    - GC-pad: linker klik
    - Reset: rechter klik
    """

    gc_path_changed = Signal(float, float)   # lat, lon van klikpunt

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(0, 0, MAP_W, MAP_H)
        self.setScene(self._scene)

        # Hardware rendering hints
        self.setRenderHint(QPainter.Antialiasing, False)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing, True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QGraphicsView.NoFrame)
        self.setBackgroundBrush(QBrush(QColor(BG_ROOT)))
        self.setDragMode(QGraphicsView.NoDrag)

        # Layers
        self._base_map  = QGraphicsPixmapItem()
        self._base_map.setZValue(0)
        self._scene.addItem(self._base_map)

        self._night = NightOverlayItem()
        self._scene.addItem(self._night)

        self._grayline = GraylineItem()
        self._scene.addItem(self._grayline)

        self._maidenhead = MaidenheadItem()
        self._maidenhead.setVisible(False)   # standaard uit
        self._scene.addItem(self._maidenhead)

        self._graticule = GraticuleItem()
        self._scene.addItem(self._graticule)

        self._aurora = AuroraItem()
        self._scene.addItem(self._aurora)

        self._sun_marker = SunMarkerItem()
        self._scene.addItem(self._sun_marker)

        self._moon_marker = MoonMarkerItem()
        self._scene.addItem(self._moon_marker)

        self._qth_marker = QTHMarkerItem()
        self._scene.addItem(self._qth_marker)

        # Set om actieve threads in leven te houden (voorkomt QThread GC-warning)
        self._threads: set = set()

        # Real-time lagen
        self._lightning = _layers.LightningLayer()
        self._scene.addItem(self._lightning)

        # Rood = meldingsradius (header-alert), oranje = piepjesradius
        self._lightning_radius      = _layers.LightningRadiusLayer(
            color_rgb=(255, 80, 80))
        self._lightning_beep_radius = _layers.LightningRadiusLayer(
            color_rgb=(255, 165, 0))
        self._scene.addItem(self._lightning_radius)
        self._scene.addItem(self._lightning_beep_radius)

        self._sat_layer = _layers.SatelliteLayer()
        self._scene.addItem(self._sat_layer)

        self._dx_spots = _layers.DXSpotsLayer()
        self._scene.addItem(self._dx_spots)

        # TLE laden vanuit cache bij opstart
        QTimer.singleShot(500, self._load_tle_cache)

        # GC-pad
        self._gc_line: QGraphicsLineItem | None = None

        # Pan-state
        self._pan_start: QPointF | None = None
        self._pan_origin = None
        self._pan_moved = False           # onderscheid klik vs sleep

        # Kaart laden
        self._load_base_map()

        # Nacht-overlay timer (elke 30s)
        self._night_timer = QTimer(self)
        self._night_timer.timeout.connect(self._refresh_night)
        self._night_timer.start(30_000)
        self._refresh_night()

        # Fit bij start
        QTimer.singleShot(100, self._fit_map)

    # ── Kaart laden ───────────────────────────────────────────────────────────
    def _load_base_map(self):
        """Laad de NASA kaart als QPixmap en start v4-stijl herinkleuring."""
        if os.path.exists(MAP_FILE):
            pix = QPixmap(MAP_FILE).scaled(
                MAP_W, MAP_H,
                Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        else:
            pix = QPixmap(MAP_W, MAP_H)
            pix.fill(QColor(27, 58, 92))
        self._base_map.setPixmap(pix)

        # Herinkleuring naar v4-stijl in achtergrond
        t = _MapColorizeThread(pix)
        t.done.connect(self._base_map.setPixmap)
        t.done.connect(t.deleteLater)
        t.finished.connect(lambda: self._threads.discard(t))
        self._threads.add(t)
        t.start()

    # ── Nacht-overlay ─────────────────────────────────────────────────────────
    def _refresh_night(self):
        """Rendert nacht + grayline direct in hoofdthread (64×32 = <5ms)."""
        sun_lat, sun_lon = _subsolar_point()
        W, H = 64, 32

        night = QImage(W, H, QImage.Format_ARGB32)
        night.fill(Qt.transparent)
        gray  = QImage(W, H, QImage.Format_ARGB32)
        gray.fill(Qt.transparent)

        sun_lat_r = math.radians(sun_lat)
        cos_sun   = math.cos(sun_lat_r)
        sin_sun   = math.sin(sun_lat_r)
        GRAY_HALF = 0.155

        for ix in range(W):
            cos_dlon = math.cos(math.radians(ix / W * 360 - 180 - sun_lon))
            for iy in range(H):
                lat_r = math.radians(90 - iy / H * 180)
                cos_a = math.sin(lat_r)*sin_sun + math.cos(lat_r)*cos_sun*cos_dlon

                if cos_a < 0:
                    depth = min(1.0, -cos_a * 2.5)
                    night.setPixelColor(ix, iy, QColor(0, 10, 50, int(200*depth)))

                ca = abs(cos_a)
                if ca < GRAY_HALF:
                    a = int(130 * (1 - ca / GRAY_HALF))
                    gray.setPixelColor(ix, iy, QColor(200, 170, 50, a))

        tf = Qt.SmoothTransformation
        night_full = night.scaled(MAP_W, MAP_H, Qt.IgnoreAspectRatio, tf)
        gray_full  = gray.scaled( MAP_W, MAP_H, Qt.IgnoreAspectRatio, tf)

        self._night._image    = night_full
        self._night.update()
        self._grayline._image = gray_full
        self._grayline.update()
        self._sun_marker._update_position()
        self._sun_marker.update()
        self._moon_marker._update_position()

    # ── View fit/zoom ─────────────────────────────────────────────────────────
    def _fit_map(self):
        """Pas kaart aan viewport (2:1 ratio behouden)."""
        self.fitInView(QRectF(0, 0, MAP_W, MAP_H), Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._fit_map()

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)
        # Begrens zoom
        t = self.transform()
        sx = t.m11()
        if sx < 0.5:
            self.fitInView(QRectF(0, 0, MAP_W, MAP_H), Qt.KeepAspectRatio)
        elif sx > 16:
            self.scale(1 / factor, 1 / factor)

    # ── Pan en klik ──────────────────────────────────────────────────────────
    _PAN_THRESHOLD = 4   # pixels beweging voordat het een pan wordt

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._start_pan(event.position())
        elif event.button() == Qt.RightButton:
            self._reset_view()
        elif event.button() == Qt.LeftButton:
            # Altijd pan starten — GC-marker pas na release zonder beweging
            self._start_pan(event.position())
        super().mousePressEvent(event)

    def _start_pan(self, pos: QPointF):
        self._pan_start  = pos
        self._pan_origin = (self.horizontalScrollBar().value(),
                            self.verticalScrollBar().value())
        self._pan_moved  = False

    def mouseMoveEvent(self, event):
        if self._pan_start is not None and event.buttons() & Qt.LeftButton:
            delta = event.position() - self._pan_start
            if not self._pan_moved:
                if (abs(delta.x()) + abs(delta.y())) < self._PAN_THRESHOLD:
                    return super().mouseMoveEvent(event)
                self._pan_moved = True
                self.setCursor(Qt.ClosedHandCursor)
            ox, oy = self._pan_origin
            self.horizontalScrollBar().setValue(int(ox - delta.x()))
            self.verticalScrollBar().setValue(int(oy - delta.y()))
        elif self._pan_start is not None and event.buttons() & Qt.MiddleButton:
            delta = event.position() - self._pan_start
            self._pan_moved = True
            ox, oy = self._pan_origin
            self.horizontalScrollBar().setValue(int(ox - delta.x()))
            self.verticalScrollBar().setValue(int(oy - delta.y()))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._pan_start is not None:
            if not self._pan_moved:
                # Korte klik zonder sleep → GC-marker plaatsen
                scene_pt = self.mapToScene(event.position().toPoint())
                lat, lon = scene_to_latlon(scene_pt.x(), scene_pt.y())
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    self._draw_gc_marker(lat, lon)
                    self.gc_path_changed.emit(lat, lon)
            self._pan_start = None
            self._pan_moved = False
            self.setCursor(Qt.ArrowCursor)
        elif event.button() == Qt.MiddleButton:
            self._pan_start = None
            self._pan_moved = False
            self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

    def _reset_view(self):
        self._fit_map()
        if self._gc_line:
            self._scene.removeItem(self._gc_line)
            self._gc_line = None

    # ── GC-pad ────────────────────────────────────────────────────────────────
    def _draw_gc_marker(self, lat: float, lon: float):
        """Toon een kruisje op het aangeklikte punt."""
        if self._gc_line:
            self._scene.removeItem(self._gc_line)
        pt = latlon_to_scene(lat, lon)
        pen = QPen(QColor(ACCENT), 3)
        line = self._scene.addLine(pt.x()-8, pt.y(), pt.x()+8, pt.y(), pen)
        line.setZValue(9)
        self._gc_line = line

    # ── QTH ───────────────────────────────────────────────────────────────────
    def set_qth(self, lat: float, lon: float):
        self._qth_marker.set_qth(lat, lon)
        self._lightning_radius.set_qth(lat, lon)
        self._lightning_beep_radius.set_qth(lat, lon)
        self._moon_marker.set_qth(lat, lon)

    def set_lightning_radius(self, km: int):
        """Rode cirkel — header-melding drempel."""
        self._lightning_radius.set_radius_km(km)

    def set_lightning_beep_radius(self, km: int):
        """Oranje cirkel — piepjes drempel."""
        self._lightning_beep_radius.set_radius_km(km)

    # ── Laag-toggles ──────────────────────────────────────────────────────────
    def set_lightning_visible(self, on: bool):
        self._lightning.set_enabled(on)

    def set_satellite_visible(self, on: bool):
        self._sat_layer.setVisible(on)

    def set_dx_spots_visible(self, on: bool):
        self._dx_spots.setVisible(on)

    def set_lightning_fade(self, seconds: int):
        self._lightning.set_fade_seconds(seconds)

    def set_grayline_visible(self, on: bool):
        self._grayline.setVisible(on)

    def set_locator_visible(self, on: bool):
        self._maidenhead.setVisible(on)

    def set_aurora_visible(self, on: bool):
        self._aurora.setVisible(on)

    def set_graticule_visible(self, on: bool):
        self._graticule.setVisible(on)

    def set_sun_visible(self, on: bool):
        self._sun_marker.setVisible(on)

    def set_moon_visible(self, on: bool):
        self._moon_marker.setVisible(on)

    def set_k_index(self, k: float):
        self._aurora.set_k_index(k)

    def set_overlay_font_size(self, size: int):
        self._graticule.set_font_size(size)

    def set_sat_font_size(self, size: int):
        self._sat_layer.set_overlay_font_size(size)

    def set_dx_map_font_size(self, size: int):
        self._dx_spots.set_label_font_size(size)

    # ── Satelliet data ────────────────────────────────────────────────────────
    def set_satellite_selection(self, names: set):
        self._sat_layer.set_selected(names)
        self._sat_layer.setVisible(len(names) > 0)

    def set_satellite_paths(self, names: set):
        self._sat_layer.set_path_selected(names)

    def set_satellite_footprints(self, names: set):
        self._sat_layer.set_fp_selected(names)

    def set_satellite_hours(self, back_h: int, fwd_h: int):
        self._sat_layer.set_path_hours(back_h, fwd_h)

    def update_tle(self, tle: dict):
        """Laad TLE data: {name: (line1, line2)}."""
        self._sat_layer.set_tle(tle)

    @property
    def lightning_status(self):
        return self._lightning.status_signal

    # ── TLE cache laden ───────────────────────────────────────────────────────
    def _load_tle_cache(self):
        cache = _layers.load_tle_cache()
        if cache:
            tle = {}
            for sats in cache.values():
                for row in sats:
                    if len(row) == 3:
                        tle[row[0]] = (row[1], row[2])
            self._sat_layer.set_tle(tle)


# ── Hulpfuncties (gedeeld met v4) ─────────────────────────────────────────────

def _subsolar_point() -> tuple[float, float]:
    """Geocentrische positie van de zon (vereenvoudigd)."""
    now = datetime.datetime.now(datetime.timezone.utc)
    doy = now.timetuple().tm_yday
    decl = -23.45 * math.cos(math.radians(360 / 365 * (doy + 10)))
    ut = now.hour + now.minute / 60 + now.second / 3600
    lon = -(ut - 12) * 15
    lon = ((lon + 180) % 360) - 180
    return decl, lon


def _submoon_point() -> tuple[float, float]:
    """Geocentrische positie van de maan (vereenvoudigd, nauwkeurig ~0.5°)."""
    now = datetime.datetime.now(datetime.timezone.utc)
    J2K = datetime.datetime(2000, 1, 1, 12, tzinfo=datetime.timezone.utc)
    d   = (now - J2K).total_seconds() / 86400
    L   = math.radians((218.316 + 13.176396 * d) % 360)
    M   = math.radians((134.963 + 13.064993 * d) % 360)
    F   = math.radians((93.272  + 13.229350 * d) % 360)
    lam = L + math.radians(6.289 * math.sin(M))
    beta = math.radians(5.128 * math.sin(F))
    obl  = math.radians(23.439)
    lat  = math.degrees(math.asin(
        math.sin(beta) * math.cos(obl) +
        math.cos(beta) * math.sin(obl) * math.sin(lam)))
    ra   = math.degrees(math.atan2(
        math.sin(lam) * math.cos(obl) - math.tan(beta) * math.sin(obl),
        math.cos(lam)))
    ut   = now.hour + now.minute / 60 + now.second / 3600
    GMST = (6.697375 + 0.0657098242 * d + ut) % 24
    lon  = ((ra / 15 - GMST) * 15 + 180) % 360 - 180
    return lat, lon


def _moon_phase_deg() -> float:
    """Maanfase in graden: 0=nieuwe maan, 180=volle maan."""
    _, sun_lon  = _subsolar_point()
    _, moon_lon = _submoon_point()
    return (moon_lon - sun_lon + 360) % 360


def _moon_elevation(qth_lat: float, qth_lon: float) -> float:
    """Hoogte van de maan boven de horizon gezien vanaf het QTH (graden)."""
    now = datetime.datetime.now(datetime.timezone.utc)
    J2K = datetime.datetime(2000, 1, 1, 12, tzinfo=datetime.timezone.utc)
    d   = (now - J2K).total_seconds() / 86400
    # Maanpositie (dezelfde berekening als _submoon_point)
    L   = math.radians((218.316 + 13.176396 * d) % 360)
    M   = math.radians((134.963 + 13.064993 * d) % 360)
    F   = math.radians((93.272  + 13.229350 * d) % 360)
    lam = L + math.radians(6.289 * math.sin(M))
    beta = math.radians(5.128 * math.sin(F))
    obl  = math.radians(23.439)
    dec  = math.asin(
        math.sin(beta) * math.cos(obl) +
        math.cos(beta) * math.sin(obl) * math.sin(lam))
    ra   = math.degrees(math.atan2(
        math.sin(lam) * math.cos(obl) - math.tan(beta) * math.sin(obl),
        math.cos(lam)))
    # Local Hour Angle
    ut   = now.hour + now.minute / 60 + now.second / 3600
    GMST = (6.697375 + 0.0657098242 * d + ut) % 24
    LST  = (GMST + qth_lon / 15) % 24
    HA   = math.radians(((LST - ra / 15) * 15 + 360) % 360)
    # Altitude
    lat_r = math.radians(qth_lat)
    alt   = math.asin(max(-1.0, min(1.0,
        math.sin(lat_r) * math.sin(dec) +
        math.cos(lat_r) * math.cos(dec) * math.cos(HA))))
    return math.degrees(alt)


def _render_moon_icon(size: int, phase_deg: float) -> QImage:
    """Rendert een maanfase-icoon als QImage (size×size, ARGB32)."""
    phase = math.radians(phase_deg)
    img   = QImage(size, size, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    r  = size / 2 - 0.5
    cx = cy = size / 2 - 0.5
    LIT  = QColor(235, 225, 190, 240)
    DARK = QColor(28,  28,  42,  240)
    EDGE = QColor(140, 135, 110, 180)
    for py in range(size):
        for px in range(size):
            dx = px - cx
            dy = py - cy
            dist2 = dx * dx + dy * dy
            if dist2 > r * r:
                continue
            # Randpixels
            if dist2 > (r - 1) * (r - 1):
                img.setPixelColor(px, py, EDGE)
                continue
            cos_y  = math.sqrt(max(0.0, 1.0 - (dy / r) ** 2))
            x_term = math.cos(phase) * r * cos_y
            lit = (dx > x_term) if phase <= math.pi else (dx < x_term)
            img.setPixelColor(px, py, LIT if lit else DARK)
    return img
