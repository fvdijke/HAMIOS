"""HAMIOS v5 — Eén propagatiemodel voor de hele applicatie.

Vervangt de drie losse modellen (bandpanelen, advies-venster, MUF-paneel) die
elkaar en de werkelijkheid tegenspraken.

Werking
  1. Gemeten ionosfeer eerst: de dichtstbijzijnde actuele ionosonde
     (KC2G / GIRO, ≤ 90 min oud, ≤ 2000 km) kalibreert het model.
     Voor 'nu' telt de meting volledig; voor latere uren neemt de invloed
     geleidelijk af (halveringstijd ~8 u) en valt de voorspelling terug op
     het model.
  2. Model: foF2 uit zonnevlekgetal en zonsstand (met ~1 u ionosferische
     vertraging), MUF(3000) = foF2 × M(3000); LUF uit D-laag-absorptie
     (zonsstand, SFI) plus aurora-absorptie op hoge breedte bij hoge K.
  3. Kans per band: de MUF is een mediaan — op de MUF is een band ~50 % van
     de dagen open, op 0,85×MUF ~90 %. Aan de onderkant bepaalt de LUF
     (verschoven door mode/vermogen/antenne) de kans.

Gebruik
    from .propagation import ENGINE
    c = ENGINE.conditions(lat, lon, snr_db=snr)          # nu
    c.muf, c.luf, c.band_pct["20m"], c.is_day, c.source
    hours = ENGINE.hourly(lat, lon, hours=24, start=...)  # voorspelling
"""

from __future__ import annotations

import datetime as _dt
import json
import math
import threading
import urllib.request
from dataclasses import dataclass, field
from functools import lru_cache

from PySide6.QtCore import QObject, QThread, Signal

# Banden — gelijk aan panels5._BANDS_HF (naam, MHz)
BANDS = [
    ("160m",  1.810), ("80m",  3.500), ("60m",  5.352),
    ("40m",   7.000), ("30m", 10.100), ("20m", 14.000),
    ("17m",  18.068), ("15m", 21.000), ("12m", 24.890),
    ("10m",  28.000), ("6m",  50.000),
]

KC2G_URL        = "https://prop.kc2g.com/api/stations.json"
IONO_POLL_S     = 15 * 60          # KC2G ververst ~elke 15 min
IONO_MAX_AGE_S  = 90 * 60
IONO_MAX_DIST   = 2000.0           # km
CAL_HALF_LIFE_H = 8.0
_UA = "HAMIOS/5.8 (+https://hamios.space; propagation monitor)"


# ── Zonsstand ─────────────────────────────────────────────────────────────────

def _utc(t: _dt.datetime | None) -> _dt.datetime:
    if t is None:
        return _dt.datetime.now(_dt.timezone.utc)
    return t if t.tzinfo else t.replace(tzinfo=_dt.timezone.utc)


def sun_position(t: _dt.datetime | None = None) -> tuple[float, float, float]:
    """Zonpositie volgens de NOAA-zonnecalculator (Meeus; ~0,01°):
    (declinatie °, lengte van het subsolaire punt °, tijdvereffening min).
    Eén bron voor kaart (nacht, grayline, zonmarker) en propagatiemodel.
    Gecachet per seconde (de zon verschuift 0,004°/s): het model vraagt per
    berekening meerdere keren hetzelfde moment op."""
    return _sun_position_at(round(_utc(t).timestamp()))


@lru_cache(maxsize=4096)
def _sun_position_at(ts: int) -> tuple[float, float, float]:
    t = _dt.datetime.fromtimestamp(ts, _dt.timezone.utc)
    T = (ts / 86400 + 2440587.5 - 2451545.0) / 36525
    L0 = (280.46646 + T * (36000.76983 + 0.0003032 * T)) % 360
    M = math.radians(357.52911 + T * (35999.05029 - 0.0001537 * T))
    e = 0.016708634 - T * (0.000042037 + 0.0000001267 * T)
    C = (math.sin(M) * (1.914602 - T * (0.004817 + 0.000014 * T))
         + math.sin(2 * M) * (0.019993 - 0.000101 * T) + math.sin(3 * M) * 0.000289)
    omega = math.radians(125.04 - 1934.136 * T)
    lam = math.radians(L0 + C - 0.00569 - 0.00478 * math.sin(omega))
    eps = math.radians(23 + (26 + (21.448 - T * (46.815 + T * (0.00059 - T * 0.001813))) / 60) / 60
                       + 0.00256 * math.cos(omega))
    decl = math.degrees(math.asin(math.sin(eps) * math.sin(lam)))
    y = math.tan(eps / 2) ** 2
    l0 = math.radians(L0)
    eot = 4 * math.degrees(y * math.sin(2 * l0) - 2 * e * math.sin(M)
                           + 4 * e * y * math.sin(M) * math.cos(2 * l0)
                           - 0.5 * y * y * math.sin(4 * l0) - 1.25 * e * e * math.sin(2 * M))
    ut_h = t.hour + t.minute / 60 + t.second / 3600
    lon = -15 * (ut_h - 12 + eot / 60)
    return decl, ((lon + 180) % 360) - 180, eot


def sun_declination(t: _dt.datetime) -> float:
    return sun_position(t)[0]


def _eot_minutes(t: _dt.datetime) -> float:
    """Tijdvereffening (minuten): verschil zonnetijd en middelbare tijd."""
    return sun_position(t)[2]


def representative_time(lat: float, lon: float, day: bool,
                        ref: _dt.datetime | None = None) -> _dt.datetime:
    """UTC-tijdstip van de lokale zonne-middag (day) of -middernacht (night)
    dat het dichtst bij ref ligt — voor 'overdag / 's nachts'-overzichten."""
    ref = _utc(ref)
    noon_h = 12 - lon / 15 - _eot_minutes(ref) / 60
    t = ref.replace(hour=0, minute=0, second=0, microsecond=0) + \
        _dt.timedelta(hours=noon_h if day else noon_h + 12)
    while t - ref > _dt.timedelta(hours=12):
        t -= _dt.timedelta(days=1)
    while ref - t > _dt.timedelta(hours=12):
        t += _dt.timedelta(days=1)
    return t


def cos_zenith(lat: float, lon: float, t: _dt.datetime | None = None) -> float:
    """Cosinus van de zenithoek van de zon (1 = zon recht boven, <0 = onder)."""
    dec_d, sub_lon, _ = sun_position(t)
    ha = math.radians(lon - sub_lon)
    dec = math.radians(dec_d)
    la = math.radians(lat)
    return math.sin(la) * math.sin(dec) + math.cos(la) * math.cos(dec) * math.cos(ha)


def is_day(lat: float, lon: float, t: _dt.datetime | None = None) -> bool:
    """Dag = zon boven de horizon (incl. refractie, -0,83°)."""
    return cos_zenith(lat, lon, t) > math.sin(math.radians(-0.83))


def _noon_cos_zenith(lat: float, t: _dt.datetime) -> float:
    return math.cos(math.radians(lat - sun_declination(t)))


# ── Model ─────────────────────────────────────────────────────────────────────

def _day_shape(lat: float, lon: float, t: _dt.datetime) -> float:
    """0 (nacht) … ~1 (middag), met ~1 u ionosferische vertraging."""
    lagged = t - _dt.timedelta(hours=1)
    cz = max(0.0, cos_zenith(lat, lon, lagged))
    noon = max(0.2, _noon_cos_zenith(lat, lagged))
    return min(1.1, (cz / noon) ** 0.6)


def model_fof2(lat: float, lon: float, t: _dt.datetime,
               ssn: float, k: float) -> float:
    ssn = max(0.0, min(ssn, 250.0))
    f_noon  = 4.0 + 0.045 * ssn
    f_night = 2.2 + 0.016 * ssn
    lat_f = 1.0 - 0.25 * max(0.0, (abs(lat) - 40) / 40)
    shape = _day_shape(lat, lon, t)
    f = (f_night + (f_noon - f_night) * shape) * lat_f
    f *= 1.0 - 0.035 * max(0.0, k - 3)          # negatieve stormfase
    return max(1.0, f)


def model_m3000(lat: float, lon: float, t: _dt.datetime) -> float:
    return 2.9 + 0.3 * min(1.0, _day_shape(lat, lon, t))


def model_luf(lat: float, lon: float, t: _dt.datetime,
              sfi: float, k: float, snr_db: float = 0.0) -> float:
    cz = max(0.0, cos_zenith(lat, lon, t))
    luf = 1.6 + 5.5 * cz ** 0.75 * (1 + 0.004 * (sfi - 70))
    luf *= 1 + 0.12 * max(0.0, k - 3) * max(0.0, (abs(lat) - 45) / 20)
    # Station-marge (mode/vermogen/antenne). D-laag-absorptie ∝ 1/f², dus
    # S dB extra marge verlaagt de LUF met √(A/(A+S)), A ≈ 20 dB absorptie
    # op de LUF — extra marge helpt op lage banden dus maar beperkt.
    s = max(-15.0, snr_db)
    luf *= math.sqrt(20.0 / (20.0 + s))
    return max(0.5, luf)


def band_probability(freq: float, muf: float, luf: float) -> float:
    """Kans (0–1) dat een band open is op 3000 km-paden."""
    p_muf = 1 / (1 + math.exp((freq / max(0.5, muf) - 1) / 0.07))
    p_luf = 1 / (1 + math.exp((luf - freq) / (0.15 * max(0.5, luf))))
    return p_muf * p_luf


# ── Ionosonde-metingen ────────────────────────────────────────────────────────

@dataclass
class Ionosonde:
    name: str
    code: str
    lat: float
    lon: float
    fof2: float
    mufd: float | None
    foes: float | None
    time: _dt.datetime

    def age_s(self, now: _dt.datetime | None = None) -> float:
        return (_utc(now) - self.time).total_seconds()


def parse_kc2g(data: list) -> list[Ionosonde]:
    out = []
    for s in data if isinstance(data, list) else []:
        try:
            st = s["station"]
            cs = s.get("cs")
            if cs is not None and cs != -1 and float(cs) < 50:
                continue                         # onbetrouwbare ionogram-interpretatie
            if s.get("fof2") is None or not s.get("time"):
                continue
            lon = float(st["longitude"])
            out.append(Ionosonde(
                name=str(st.get("name", "?")), code=str(st.get("code", "")),
                lat=float(st["latitude"]), lon=lon - 360 if lon > 180 else lon,
                fof2=float(s["fof2"]),
                mufd=float(s["mufd"]) if s.get("mufd") is not None else None,
                foes=float(s["foes"]) if s.get("foes") is not None else None,
                time=_dt.datetime.fromisoformat(s["time"][:19]).replace(
                    tzinfo=_dt.timezone.utc)))
        except (KeyError, TypeError, ValueError):
            continue
    return out


def _dist_km(lat1, lon1, lat2, lon2) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371 * 2 * math.asin(min(1.0, math.sqrt(a)))


def gc_point(lat1, lon1, lat2, lon2, frac: float) -> tuple[float, float]:
    """Punt op fractie frac (0–1) van het grootcirkelpad."""
    p1, l1, p2, l2 = map(math.radians, (lat1, lon1, lat2, lon2))
    d = 2 * math.asin(min(1.0, math.sqrt(
        math.sin((p2 - p1) / 2) ** 2 +
        math.cos(p1) * math.cos(p2) * math.sin((l2 - l1) / 2) ** 2)))
    if d < 1e-9:
        return lat1, lon1
    a = math.sin((1 - frac) * d) / math.sin(d)
    b = math.sin(frac * d) / math.sin(d)
    x = a * math.cos(p1) * math.cos(l1) + b * math.cos(p2) * math.cos(l2)
    y = a * math.cos(p1) * math.sin(l1) + b * math.cos(p2) * math.sin(l2)
    z = a * math.sin(p1) + b * math.sin(p2)
    return (math.degrees(math.atan2(z, math.hypot(x, y))),
            math.degrees(math.atan2(y, x)))


# DX-doelgebieden (label, lat, lon) — routes worden vanaf de eigen QTH berekend
DX_REGIONS = [
    ("EU",   50.0,   10.0), ("NA-E", 40.0,  -76.0), ("NA-W", 37.0, -120.0),
    ("SA",  -15.0,  -52.0), ("AF",    5.0,   20.0), ("ZS",  -28.0,   25.0),
    ("ME",   26.0,   48.0), ("VU",   21.0,   78.0), ("JA",   36.0,  138.0),
    ("VK",  -30.0,  145.0), ("ZL",  -40.0,  175.0),
]


# ── Engine ────────────────────────────────────────────────────────────────────

@dataclass
class Conditions:
    time: _dt.datetime
    fof2: float
    muf: float
    luf: float
    is_day: bool
    band_pct: dict = field(default_factory=dict)   # naam → 0–100
    measured: Ionosonde | None = None              # gebruikte ionosonde (kalibratie)
    cal_weight: float = 0.0                        # 1 = volledig gemeten, 0 = alleen model
    absorption: float = 0.0                        # gemeten D-laag-absorptie (D-RAP, MHz)

    @property
    def source(self) -> str:
        if self.measured and self.cal_weight > 0.5:
            return self.measured.name
        return "model"


class PropagationEngine(QObject):
    """Enige bron van propagatiecijfers. Thread: GUI (setters) — lezen overal."""

    updated = Signal()

    def __init__(self):
        super().__init__()
        self.sfi, self.ssn, self.k = 90.0, 50.0, 2.0
        self._ionosondes: list[Ionosonde] = []
        self._drap: dict | None = None
        self._lock = threading.Lock()

    # ── invoer ───────────────────────────────────────────────────────────────
    def set_solar(self, solar: dict):
        def num(key, default):
            try:
                return float(str(solar.get(key, default)).replace("—", str(default)) or default)
            except (TypeError, ValueError):
                return float(default)
        new = (num("sfi", 90), num("ssn", 50), num("k_index", 2))
        if new != (self.sfi, self.ssn, self.k):
            self.sfi, self.ssn, self.k = new
            self.updated.emit()

    def set_ionosondes(self, stations: list[Ionosonde]):
        with self._lock:
            self._ionosondes = list(stations)
        self.updated.emit()

    def set_drap(self, drap: dict):
        """NOAA D-RAP (charts.parse_drap): gemeten D-laag-absorptie per lat/lon."""
        with self._lock:
            self._drap = drap
        self.updated.emit()

    def drap_haf(self, lat: float, lon: float, t: _dt.datetime | None = None) -> float:
        """Hoogste door absorptie verzwakte frequentie (MHz) op (lat, lon).
        Alleen rond het meetmoment (±90 min): een zonnevlam dooft snel uit."""
        with self._lock:
            d = self._drap
        if not d or d.get("valid") is None:
            return 0.0
        if abs((_utc(t) - d["valid"]).total_seconds()) > 90 * 60:
            return 0.0
        lats, lons = d["lats"], d["lons"]
        lo = ((lon + 180) % 360) - 180
        i = min(range(len(lats)), key=lambda k: abs(lats[k] - lat))
        j = min(range(len(lons)), key=lambda k: abs(lons[k] - lo))
        return float(d["grid"][i][j])

    def ionosondes(self) -> list[Ionosonde]:
        with self._lock:
            return list(self._ionosondes)

    def _fresh_ionosondes(self, now: _dt.datetime | None) -> list[Ionosonde]:
        """Bruikbare (niet te oude) ionosondes; per minuut gecachet — het model
        vraagt dit voor elk controlepunt op (duizenden keren per propagatiekaart)."""
        now = _utc(now)
        key = (id(self._ionosondes), int(now.timestamp() // 60))
        cache = getattr(self, "_fresh_cache", None)
        if cache and cache[0] == key:
            return cache[1]
        fresh = [s for s in self.ionosondes()
                 if -600 <= s.age_s(now) <= IONO_MAX_AGE_S]
        self._fresh_cache = (key, fresh)
        return fresh

    def nearest_ionosonde(self, lat: float, lon: float,
                          now: _dt.datetime | None = None) -> Ionosonde | None:
        best, best_d = None, IONO_MAX_DIST
        max_dlat = IONO_MAX_DIST / 111.0 + 0.5      # verder weg kan nooit binnen bereik zijn
        for s in self._fresh_ionosondes(now):
            if abs(s.lat - lat) > max_dlat:
                continue
            d = _dist_km(lat, lon, s.lat, s.lon)
            if d < best_d:
                best, best_d = s, d
        return best

    # ── uitvoer ──────────────────────────────────────────────────────────────
    def _calibration(self, lat, lon, t, now):
        """(factor foF2, factor MUF, gewicht, ionosonde) voor tijdstip t."""
        s = self.nearest_ionosonde(lat, lon, now)
        if s is None:
            return 1.0, 1.0, 0.0, None
        f_mod = model_fof2(s.lat, s.lon, s.time, self.ssn, self.k)
        cf = max(0.5, min(1.8, s.fof2 / f_mod))
        if s.mufd:
            m_mod = f_mod * model_m3000(s.lat, s.lon, s.time)
            cm = max(0.5, min(1.8, s.mufd / m_mod))
        else:
            cm = cf
        dt_h = abs((t - s.time).total_seconds()) / 3600
        w = 0.5 ** (dt_h / CAL_HALF_LIFE_H)
        return cf, cm, w, s

    def conditions(self, lat: float, lon: float, t: _dt.datetime | None = None,
                   snr_db: float = 0.0, now: _dt.datetime | None = None) -> Conditions:
        now = _utc(now)
        t = _utc(t) if t is not None else now
        cf, cm, w, s = self._calibration(lat, lon, t, now)
        fof2_m = model_fof2(lat, lon, t, self.ssn, self.k)
        fof2 = fof2_m * (1 + (cf - 1) * w)
        muf = fof2_m * model_m3000(lat, lon, t) * (1 + (cm - 1) * w)
        luf = model_luf(lat, lon, t, self.sfi, self.k, snr_db)
        # Gemeten absorptie (D-RAP): daaronder komt HF niet door, ongeacht het model
        haf = self.drap_haf(lat, lon, t)
        luf = max(luf, haf)
        pct = {name: int(round(100 * band_probability(f, muf, luf))) for name, f in BANDS}
        return Conditions(time=t, fof2=round(fof2, 2), muf=round(muf, 1),
                          luf=round(luf, 1), is_day=is_day(lat, lon, t),
                          band_pct=pct, measured=s, cal_weight=w, absorption=round(haf, 1))

    def hourly(self, lat: float, lon: float, hours: int = 24,
               start: _dt.datetime | None = None, snr_db: float = 0.0) -> list[Conditions]:
        start = _utc(start).replace(minute=0, second=0, microsecond=0) if start else \
            _utc(None).replace(minute=0, second=0, microsecond=0)
        now = _utc(None)
        return [self.conditions(lat, lon, start + _dt.timedelta(hours=h), snr_db, now)
                for h in range(hours)]

    def path_detail(self, lat1, lon1, lat2, lon2, t: _dt.datetime | None = None,
                    snr_db: float = 0.0) -> dict:
        """Pad QTH → doel. Paden ≤ 4000 km: één controlepunt (midden); langer:
        twee (¼ en ¾, elke sprong ~3000 km) — het zwakste punt bepaalt het pad.
        {'pct': {band: %}, 'muf': laagste MUF, 'luf': hoogste LUF,
         'points': [Conditions per controlepunt], 'km': afstand}"""
        d = _dist_km(lat1, lon1, lat2, lon2)
        fracs = (0.5,) if d <= 4000 else (0.25, 0.75)
        points, result = [], None
        for fr in fracs:
            plat, plon = gc_point(lat1, lon1, lat2, lon2, fr)
            c = self.conditions(plat, plon, t, snr_db)
            if d < 3000:
                # Korte sprong: steilere invalshoek → lagere MUF (dode zone).
                # MUF(d) ≈ foF2 · √(1 + (d / 2h)²), h ≈ 300 km, begrensd op MUF(3000)
                muf_d = min(c.muf, c.fof2 * math.sqrt(1 + (d / 600.0) ** 2))
                if muf_d < c.muf:
                    c.muf = round(muf_d, 1)
                    c.band_pct = {name: int(round(100 * band_probability(f, muf_d, c.luf)))
                                  for name, f in BANDS}
            points.append(c)
            pct = c.band_pct
            result = pct if result is None else {b: min(v, pct[b]) for b, v in result.items()}
        return {"pct": result or {}, "km": d, "points": points,
                "muf": min(c.muf for c in points), "luf": max(c.luf for c in points),
                "absorption": max(c.absorption for c in points)}

    def path_band_pct(self, lat1, lon1, lat2, lon2, t: _dt.datetime | None = None,
                      snr_db: float = 0.0) -> dict:
        """Kans per band op het pad QTH → doel (zie path_detail)."""
        return self.path_detail(lat1, lon1, lat2, lon2, t, snr_db)["pct"]

    def band_map(self, lat: float, lon: float, band: str, t: _dt.datetime | None = None,
                 snr_db: float = 0.0, step: int = 3) -> tuple[bytes, int, int]:
        """Propagatiekaart: kans (%) per cel van step° dat `band` het pad QTH → cel
        draagt, als grijswaarden (pct × 2,55; rij 0 = noord, kolom 0 = −180°,
        celmiddens). Zelfde padmodel als de aanbevelingen (path_detail); licht
        vervaagd (1-2-1) zodat de overgangen na het opschalen vloeiend zijn."""
        t = _utc(t)                       # één tijdstip voor de hele kaart
        w, h = 360 // step, 180 // step
        g = [0.0] * (w * h)
        for y in range(h):
            clat = 90 - (y + 0.5) * step
            for x in range(w):
                clon = -180 + (x + 0.5) * step
                g[y * w + x] = self.path_band_pct(lat, lon, clat, clon, t, snr_db).get(band, 0)
        tmp = [0.0] * (w * h)
        for y in range(h):
            b = y * w
            for x in range(w):
                tmp[b + x] = (g[b + x - 1 if x else b + w - 1] + 2 * g[b + x]
                              + g[b + (x + 1) % w]) / 4
        out = bytearray(w * h)
        for y in range(h):
            up, dn = max(0, y - 1) * w, min(h - 1, y + 1) * w
            for x in range(w):
                v = (tmp[up + x] + 2 * tmp[y * w + x] + tmp[dn + x]) / 4
                out[y * w + x] = min(255, int(v * 2.55 + 0.5))
        return bytes(out), w, h

    def dx_routes(self, lat: float, lon: float, snr_db: float = 0.0,
                  t: _dt.datetime | None = None, min_pct: int = 50,
                  min_km: float = 1500) -> list[tuple[str, int, list]]:
        """Open DX-routes vanaf de QTH: [(regio, afstand_km, [(band, pct), …])],
        banden van hoog naar laag (hoogste open band = minste absorptie),
        gesorteerd op beste kans."""
        freq = dict(BANDS)
        routes = []
        for name, rlat, rlon in DX_REGIONS:
            d = _dist_km(lat, lon, rlat, rlon)
            if d < min_km:
                continue                           # eigen continent
            pct = self.path_band_pct(lat, lon, rlat, rlon, t, snr_db)
            open_b = sorted(((b, p) for b, p in pct.items() if p >= min_pct and b != "6m"),
                            key=lambda bp: -freq[bp[0]])
            if open_b:
                routes.append((name, int(d), open_b[:2]))
        routes.sort(key=lambda r: -max(p for _, p in r[2]))
        return routes


ENGINE = PropagationEngine()


# ── Ionosonde-feed (KC2G) ─────────────────────────────────────────────────────

class IonosondeFeed(QThread):
    """Haalt elke 15 min de KC2G-stationslijst op. Bij een fout blijven de
    vorige metingen staan (ze verouderen vanzelf na 90 min → model)."""

    stations_ready = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False
        self._wake = threading.Event()

    def run(self):
        self._running = True
        while self._running:
            try:
                req = urllib.request.Request(KC2G_URL, headers={"User-Agent": _UA})
                with urllib.request.urlopen(req, timeout=20) as r:
                    stations = parse_kc2g(json.loads(r.read().decode("utf-8")))
                if stations:
                    self.stations_ready.emit(stations)
            except Exception as e:
                self.error_occurred.emit(str(e)[:120])
            self._wake.wait(IONO_POLL_S)

    def stop(self):
        self._running = False
        self._wake.set()
        self.wait(3000)
