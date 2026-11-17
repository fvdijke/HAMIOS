"""
HAMIOS — Azimutale kaart (azimutaal-equidistant rond de eigen QTH).

Elke rechte lijn vanuit het midden is een grootcirkel: de richting op de kaart
is de antennerichting, de afstand tot het midden de echte afstand. Ringen per
5000 km; de rand is het antipode van de QTH (20 000 km).

- Aanwijzen: richting (kort/lang pad), afstand en land (cty.dat).
- Klik: padvoorspelling en kaartpad naar dat punt; met een rotor ingesteld
  draait de antenne mee (Instellingen → CAT → Rotor).
- DX-spots van het cluster staan als stippen op de kaart.
"""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt, QThread, Signal
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPen
from PySide6.QtWidgets import QLabel, QToolTip, QVBoxLayout, QWidget

from .i18n import tr
from .theme import ACCENT, BG_PANEL, TEXT_DIM

EARTH_HALF_KM = 20015.1         # halve omtrek: afstand tot het antipode
RENDER_PX = 640


def project(lat0, lon0, lat, lon) -> tuple[float, float]:
    """(lat, lon) → (x, y) in eenheden van de kaartstraal (−1…1), noord boven."""
    p0, p = math.radians(lat0), math.radians(lat)
    dl = math.radians(lon - lon0)
    cos_c = math.sin(p0) * math.sin(p) + math.cos(p0) * math.cos(p) * math.cos(dl)
    c = math.acos(max(-1.0, min(1.0, cos_c)))
    if c < 1e-12:
        return 0.0, 0.0
    az = math.atan2(math.sin(dl) * math.cos(p),
                    math.cos(p0) * math.sin(p) - math.sin(p0) * math.cos(p) * math.cos(dl))
    r = c / math.pi
    return r * math.sin(az), -r * math.cos(az)


def unproject(lat0, lon0, x, y) -> tuple[float, float] | None:
    """Omgekeerde van project(); None buiten de schijf."""
    r = math.hypot(x, y)
    if r > 1.0:
        return None
    c = r * math.pi
    az = math.atan2(x, -y)
    p0 = math.radians(lat0)
    lat = math.asin(max(-1.0, min(1.0, math.cos(c) * math.sin(p0)
                                  + math.sin(c) * math.cos(p0) * math.cos(az))))
    lon = math.radians(lon0) + math.atan2(math.sin(az) * math.sin(c) * math.cos(p0),
                                          math.cos(c) - math.sin(p0) * math.sin(lat))
    return math.degrees(lat), ((math.degrees(lon) + 180) % 360) - 180


def render(src: QImage, lat0: float, lon0: float, size: int = RENDER_PX) -> QImage:
    """Equirectangulaire kaart → azimutaal-equidistant beeld (size × size)."""
    src = src.convertToFormat(QImage.Format_RGB32)
    sw, sh = src.width(), src.height()
    out = QImage(size, size, QImage.Format_ARGB32)
    out.fill(Qt.transparent)
    try:
        import numpy as np
        ptr = src.constBits()
        sarr = np.frombuffer(ptr, dtype=np.uint32, count=sw * sh).reshape(sh, sw)
        g = (np.arange(size) + 0.5) / size * 2 - 1
        xs, ys = np.meshgrid(g, g)
        r = np.hypot(xs, ys)
        inside = r <= 1.0
        c = np.clip(r, 0, 1) * np.pi
        az = np.arctan2(xs, -ys)
        p0 = math.radians(lat0)
        lat = np.arcsin(np.clip(np.cos(c) * math.sin(p0)
                                + np.sin(c) * math.cos(p0) * np.cos(az), -1, 1))
        lon = math.radians(lon0) + np.arctan2(np.sin(az) * np.sin(c) * math.cos(p0),
                                              np.cos(c) - math.sin(p0) * np.sin(lat))
        u = ((np.degrees(lon) + 180) % 360) / 360 * (sw - 1)
        v = (90 - np.degrees(lat)) / 180 * (sh - 1)
        pix = sarr[v.astype(np.int32).clip(0, sh - 1), u.astype(np.int32).clip(0, sw - 1)]
        pix = np.where(inside, pix | 0xFF000000, 0).astype(np.uint32)
        buf = pix.tobytes()
        out = QImage(buf, size, size, size * 4, QImage.Format_ARGB32).copy()
    except ImportError:
        for py in range(size):
            for px in range(size):
                ll = unproject(lat0, lon0, (px + 0.5) / size * 2 - 1, (py + 0.5) / size * 2 - 1)
                if ll is None:
                    continue
                u = int((ll[1] + 180) / 360 * (sw - 1))
                v = int((90 - ll[0]) / 180 * (sh - 1))
                out.setPixel(px, py, src.pixel(u, v) | 0xFF000000)
    return out


class _RenderThread(QThread):
    done = Signal(QImage, float, float)

    def __init__(self, path, lat, lon, parent=None):
        super().__init__(parent)
        self._args = (path, lat, lon)

    def run(self):
        path, lat, lon = self._args
        src = QImage(path)
        if src.isNull():
            return
        self.done.emit(render(src, lat, lon), lat, lon)


class _Canvas(QWidget):
    clicked = Signal(float, float, float)          # lat, lon, azimut

    def __init__(self, parent=None):
        super().__init__(parent)
        self._img: QImage | None = None
        self._qth = (52.0, 5.0)
        self._spots: list = []                      # (lat, lon, call, kHz)
        self._target = None                         # (lat, lon)
        self._heading: float | None = None          # laatst gevraagde rotorrichting
        self.setMouseTracking(True)
        self.setMinimumSize(200, 200)

    def _disk(self) -> QRectF:
        s = min(self.width(), self.height()) - 36
        return QRectF((self.width() - s) / 2, (self.height() - s) / 2, s, s)

    def _to_px(self, lat, lon) -> QPointF:
        d = self._disk()
        x, y = project(self._qth[0], self._qth[1], lat, lon)
        return QPointF(d.center().x() + x * d.width() / 2, d.center().y() + y * d.height() / 2)

    def _to_ll(self, pos: QPointF):
        d = self._disk()
        x = (pos.x() - d.center().x()) / (d.width() / 2)
        y = (pos.y() - d.center().y()) / (d.height() / 2)
        return unproject(self._qth[0], self._qth[1], x, y)

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(BG_PANEL))
        d = self._disk()
        if self._img is not None:
            p.drawImage(d, self._img)
        else:
            p.setPen(QColor(TEXT_DIM))
            p.drawText(self.rect(), Qt.AlignCenter, tr("az.rendering"))
        c, R = d.center(), d.width() / 2
        # Afstandsringen en richtingslijnen
        p.setFont(QFont("Segoe UI", 7))
        ring = QPen(QColor(200, 168, 75, 110), 1, Qt.DashLine)
        for km in (5000, 10000, 15000):
            rr = R * km / EARTH_HALF_KM
            p.setPen(ring)
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(c, rr, rr)
            p.setPen(QColor(200, 168, 75, 170))
            p.drawText(QPointF(c.x() + 3, c.y() - rr - 2), f"{km // 1000}k km")
        p.setPen(QPen(QColor(200, 168, 75, 70), 1))
        for a in range(0, 360, 30):
            rad = math.radians(a)
            p.drawLine(c, QPointF(c.x() + R * math.sin(rad), c.y() - R * math.cos(rad)))
        p.setPen(QPen(QColor(ACCENT), 1.5))
        p.drawEllipse(c, R, R)
        lab = {0: "N", 90: "E", 180: "S", 270: "W"}
        p.setPen(QColor(ACCENT))
        for a in range(0, 360, 30):
            rad = math.radians(a)
            pt = QPointF(c.x() + (R + 11) * math.sin(rad), c.y() - (R + 11) * math.cos(rad))
            p.drawText(QRectF(pt.x() - 14, pt.y() - 7, 28, 14), Qt.AlignCenter,
                       lab.get(a, f"{a}"))
        # DX-spots
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(79, 195, 247, 200))
        for lat, lon, _call, _khz in self._spots:
            p.drawEllipse(self._to_px(lat, lon), 3, 3)
        # Doel + richting (grootcirkel = rechte lijn)
        if self._target is not None:
            tp = self._to_px(*self._target)
            p.setPen(QPen(QColor(ACCENT), 2, Qt.DashLine))
            p.drawLine(c, tp)
            p.setBrush(QColor(ACCENT))
            p.setPen(QPen(QColor(0, 0, 0), 1))
            p.drawEllipse(tp, 5, 5)
        if self._heading is not None:
            rad = math.radians(self._heading)
            p.setPen(QPen(QColor("#66BB6A"), 3))
            p.drawLine(c, QPointF(c.x() + R * 0.25 * math.sin(rad), c.y() - R * 0.25 * math.cos(rad)))
        p.setBrush(QColor(ACCENT))
        p.setPen(QPen(QColor(0, 0, 0), 1))
        p.drawEllipse(c, 4, 4)

    def mouseMoveEvent(self, e):
        from .propagation import _dist_km, bearing_deg
        ll = self._to_ll(e.position())
        if ll is None:
            QToolTip.hideText()
            return
        az = bearing_deg(self._qth[0], self._qth[1], *ll)
        km = _dist_km(self._qth[0], self._qth[1], *ll)
        near = min(self._spots, default=None,
                   key=lambda s: (s[0] - ll[0]) ** 2 + (s[1] - ll[1]) ** 2)
        extra = ""
        if near is not None and abs(near[0] - ll[0]) < 3 and abs(near[1] - ll[1]) < 3:
            extra = f"<br>{near[2]} · {near[3]:.1f} kHz"
        QToolTip.showText(e.globalPosition().toPoint(),
                          tr("az.tip", az=f"{az:.0f}", lp=f"{(az + 180) % 360:.0f}",
                             km=f"{km:,.0f}".replace(",", "."),
                             pos=f"{ll[0]:+.1f}°, {ll[1]:+.1f}°") + extra, self)

    def mouseReleaseEvent(self, e):
        from .propagation import bearing_deg
        if e.button() != Qt.LeftButton:
            return
        ll = self._to_ll(e.position())
        if ll is None:
            return
        self._target = ll
        self.update()
        self.clicked.emit(ll[0], ll[1], bearing_deg(self._qth[0], self._qth[1], *ll))


class AzimuthalWidget(QWidget):
    """Paneel 'Azimutale kaart'."""

    target_picked = Signal(float, float, str)   # → kaartpad + padvoorspelling
    _rotor_msg = Signal(str)                     # rotorresultaat (uit achtergrondthread)

    def __init__(self, cfg=None, map_file: str = "", parent=None):
        super().__init__(parent)
        self._cfg = cfg
        self._map_file = map_file
        self._thread = None
        self._rendered_for = None
        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.setSpacing(2)
        self._canvas = _Canvas()
        self._canvas.clicked.connect(self._on_click)
        lay.addWidget(self._canvas, 1)
        self._status = QLabel(tr("az.hint"))
        self._status.setWordWrap(True)
        self._status.setStyleSheet(f"color: {TEXT_DIM}; font-size: 8pt;")
        lay.addWidget(self._status)
        self._rotor_msg.connect(self._status.setText)
        self.set_cfg(cfg)

    def set_cfg(self, cfg):
        self._cfg = cfg
        if cfg is None:
            return
        qth = (round(cfg.qth_lat, 3), round(cfg.qth_lon, 3))
        self._canvas._qth = qth
        if qth != self._rendered_for and self._thread is None:
            th = _RenderThread(self._map_file, *qth, parent=self)
            th.done.connect(self._on_rendered)
            th.finished.connect(th.deleteLater)
            th.finished.connect(lambda: setattr(self, "_thread", None))
            self._thread = th
            th.start()
        self._canvas.update()

    def _on_rendered(self, img: QImage, lat: float, lon: float):
        self._rendered_for = (lat, lon)
        self._canvas._img = img
        self._canvas.update()
        if self._cfg and (round(self._cfg.qth_lat, 3), round(self._cfg.qth_lon, 3)) != (lat, lon):
            self.set_cfg(self._cfg)         # QTH tijdens het renderen gewijzigd

    def set_spots(self, raw_spots: list):
        """Ruwe DX-spots uit de kaartlaag: (dx_lat, dx_lon, call, kHz, …)."""
        self._canvas._spots = [(s[0], s[1], s[2], float(s[3] or 0)) for s in raw_spots or []]
        self._canvas.update()

    def set_target(self, lat: float, lon: float, _label: str = ""):
        self._canvas._target = (lat, lon)
        self._canvas.update()

    def _on_click(self, lat: float, lon: float, az: float):
        from . import rotor
        from .sat_passes import compass
        self.target_picked.emit(lat, lon, "")
        self._canvas._heading = az
        self._canvas.update()
        if rotor.turn(self._cfg, az, done=self._rotor_done):
            self._status.setText(tr("az.turning", az=f"{az:.0f}", dir=compass(az)))
        else:
            self._status.setText(tr("az.no_rotor", az=f"{az:.0f}", dir=compass(az)))

    def _rotor_done(self, ok: bool, msg: str):
        # Achtergrondthread → signaal (komt via de Qt-wachtrij in de GUI-thread)
        self._rotor_msg.emit(tr("az.turned") if ok else tr("az.rotor_err", err=msg))
