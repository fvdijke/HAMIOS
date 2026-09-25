"""
HAMIOS — Satellietbanen en overkomsten (passes)

Baanmodel: Kepler met de seculiere J2-storing (precessie van de klimmende knoop
en het perigeum) en de eerste afgeleide van de gemiddelde beweging uit de TLE.
Voor LEO-satellieten ~km-nauwkeurig binnen een dag; overkomsttijden op
±1 minuut — ruim voldoende voor een overzicht en een melding vooraf.

Kijkhoeken (azimut/elevatie) worden topocentrisch berekend vanaf de QTH.
"""

from __future__ import annotations

import datetime as _dt
import math
from dataclasses import dataclass
from functools import lru_cache

MU      = 398600.4418        # km³/s²
RE_J2   = 6378.137           # km (equatoriaal, voor J2)
J2      = 1.08262668e-3
R_EARTH = 6371.0             # km (bol, voor lat/lon zoals op de kaart)
_J2000  = _dt.datetime(2000, 1, 1, 12, tzinfo=_dt.timezone.utc)


@dataclass(frozen=True)
class _Elements:
    epoch: _dt.datetime
    incl: float
    raan: float
    ecc: float
    argp: float
    m0: float
    n: float                 # rad/min
    ndot: float              # rad/min² (½·n̈ uit de TLE, al ×2)
    raan_dot: float          # rad/min
    argp_dot: float          # rad/min
    rev_per_day: float


@lru_cache(maxsize=512)
def _elements(line1: str, line2: str) -> _Elements:
    ep = line1[18:32].strip()
    yr2 = int(ep[:2])
    yr = 2000 + yr2 if yr2 < 57 else 1900 + yr2
    epoch = (_dt.datetime(yr, 1, 1, tzinfo=_dt.timezone.utc)
             + _dt.timedelta(days=float(ep[2:]) - 1))
    incl = math.radians(float(line2[8:16]))
    raan = math.radians(float(line2[17:25]))
    ecc = float("0." + line2[26:33].strip())
    argp = math.radians(float(line2[34:42]))
    m0 = math.radians(float(line2[43:51]))
    rev = float(line2[52:63])
    try:
        ndot_rev = float(line1[33:43])           # ṅ/2 in omw/dag²
    except ValueError:
        ndot_rev = 0.0
    n = rev * 2 * math.pi / 1440.0               # rad/min
    a = (MU / (n / 60) ** 2) ** (1 / 3)
    p = a * (1 - ecc * ecc)
    k = 1.5 * J2 * (RE_J2 / p) ** 2 * n
    return _Elements(
        epoch=epoch, incl=incl, raan=raan, ecc=ecc, argp=argp, m0=m0, n=n,
        ndot=ndot_rev * 2 * math.pi / (1440.0 ** 2),
        raan_dot=-k * math.cos(incl),
        argp_dot=k * (2 - 2.5 * math.sin(incl) ** 2),
        rev_per_day=rev)


def sat_ecef(line1: str, line2: str, t: _dt.datetime) -> tuple[float, float, float]:
    """Positie (km) in aardvaste coördinaten op tijdstip t (UTC)."""
    el = _elements(line1, line2)
    dt_min = (t - el.epoch).total_seconds() / 60.0
    M = (el.m0 + el.n * dt_min + el.ndot * dt_min * dt_min) % (2 * math.pi)
    E = M
    for _ in range(8):
        E = M + el.ecc * math.sin(E)
    n_rs = (el.n + 2 * el.ndot * dt_min) / 60
    a = (MU / n_rs ** 2) ** (1 / 3)
    cos_e = math.cos(E)
    nu = math.atan2(math.sqrt(1 - el.ecc ** 2) * math.sin(E), cos_e - el.ecc)
    r = a * (1 - el.ecc * cos_e)
    xp, yp = r * math.cos(nu), r * math.sin(nu)
    raan = el.raan + el.raan_dot * dt_min
    argp = el.argp + el.argp_dot * dt_min
    cr, sr = math.cos(raan), math.sin(raan)
    co, so = math.cos(argp), math.sin(argp)
    ci, si = math.cos(el.incl), math.sin(el.incl)
    x = (cr * co - sr * so * ci) * xp + (-cr * so - sr * co * ci) * yp
    y = (sr * co + cr * so * ci) * xp + (-sr * so + cr * co * ci) * yp
    z = si * so * xp + si * co * yp
    d = (t - _J2000).total_seconds() / 86400
    g = math.radians((280.46061837 + 360.98564736629 * d) % 360)
    cg, sg = math.cos(g), math.sin(g)
    return x * cg + y * sg, -x * sg + y * cg, z


def subpoint(line1: str, line2: str, t: _dt.datetime) -> tuple[float, float, float]:
    """(breedte, lengte, hoogte km) van het subsatellietpunt."""
    x, y, z = sat_ecef(line1, line2, t)
    r = math.sqrt(x * x + y * y + z * z)
    return (math.degrees(math.asin(max(-1.0, min(1.0, z / r)))),
            math.degrees(math.atan2(y, x)), r - R_EARTH)


def look_angles(sat: tuple[float, float, float], lat: float, lon: float
                ) -> tuple[float, float, float]:
    """(azimut °, elevatie °, afstand km) van de satelliet gezien vanaf (lat, lon)."""
    la, lo = math.radians(lat), math.radians(lon)
    cla, sla, clo, slo = math.cos(la), math.sin(la), math.cos(lo), math.sin(lo)
    rx = sat[0] - R_EARTH * cla * clo
    ry = sat[1] - R_EARTH * cla * slo
    rz = sat[2] - R_EARTH * sla
    east = -slo * rx + clo * ry
    north = -sla * clo * rx - sla * slo * ry + cla * rz
    up = cla * clo * rx + cla * slo * ry + sla * rz
    return (math.degrees(math.atan2(east, north)) % 360,
            math.degrees(math.atan2(up, math.hypot(east, north))),
            math.sqrt(rx * rx + ry * ry + rz * rz))


_COMPASS = {"nl": ("N", "NO", "O", "ZO", "Z", "ZW", "W", "NW"),
            "en": ("N", "NE", "E", "SE", "S", "SW", "W", "NW")}


def compass(az: float) -> str:
    from .i18n import get_language
    names = _COMPASS.get(get_language(), _COMPASS["en"])
    return names[int((az % 360) / 45 + 0.5) % 8]


@dataclass
class SatPass:
    name: str
    aos: _dt.datetime
    los: _dt.datetime
    tca: _dt.datetime
    max_el: float
    az_aos: float
    az_los: float

    @property
    def duration_s(self) -> float:
        return (self.los - self.aos).total_seconds()


def _elev(l1, l2, lat, lon, t) -> float:
    return look_angles(sat_ecef(l1, l2, t), lat, lon)[1]


def _cross(l1, l2, lat, lon, t0, t1, rising: bool, min_el: float) -> _dt.datetime:
    """Bisectie naar het moment dat de elevatie min_el passeert (op 1 s)."""
    for _ in range(12):
        tm = t0 + (t1 - t0) / 2
        above = _elev(l1, l2, lat, lon, tm) >= min_el
        if above == rising:
            t1 = tm
        else:
            t0 = tm
        if (t1 - t0).total_seconds() <= 1:
            break
    return t1 if rising else t0


def _peak(l1, l2, lat, lon, t0, t1) -> tuple[_dt.datetime, float]:
    """Hoogste elevatie tussen t0 en t1 (ternair zoeken, op ~2 s)."""
    for _ in range(20):
        if (t1 - t0).total_seconds() <= 2:
            break
        a = t0 + (t1 - t0) / 3
        b = t1 - (t1 - t0) / 3
        if _elev(l1, l2, lat, lon, a) < _elev(l1, l2, lat, lon, b):
            t0 = a
        else:
            t1 = b
    tm = t0 + (t1 - t0) / 2
    return tm, _elev(l1, l2, lat, lon, tm)


def predict_passes(tles: dict, lat: float, lon: float,
                   start: _dt.datetime | None = None, hours: float = 24,
                   min_el: float = 0.0, step_s: int = 60) -> list[SatPass]:
    """Overkomsten van de gegeven satellieten ({naam: (regel1, regel2)}) boven de
    QTH, gesorteerd op AOS. Een overkomst die al bezig is begint bij start.
    Geostationaire/hoge banen (< 2 omwentelingen per dag) worden overgeslagen."""
    start = start or _dt.datetime.now(_dt.timezone.utc)
    step = _dt.timedelta(seconds=step_s)
    n_steps = int(hours * 3600 / step_s)
    out: list[SatPass] = []
    for name, (l1, l2) in tles.items():
        try:
            if _elements(l1, l2).rev_per_day < 2:
                continue
            prev_t, prev_up = start, _elev(l1, l2, lat, lon, start) >= min_el
            aos = start if prev_up else None
            for i in range(1, n_steps + 1):
                t = start + step * i
                up = _elev(l1, l2, lat, lon, t) >= min_el
                if up and not prev_up:
                    aos = _cross(l1, l2, lat, lon, prev_t, t, True, min_el)
                elif prev_up and not up and aos is not None:
                    los = _cross(l1, l2, lat, lon, prev_t, t, False, min_el)
                    tca, mx = _peak(l1, l2, lat, lon, aos, los)
                    out.append(SatPass(
                        name, aos, los, tca, mx,
                        look_angles(sat_ecef(l1, l2, aos), lat, lon)[0],
                        look_angles(sat_ecef(l1, l2, los), lat, lon)[0]))
                    aos = None
                prev_t, prev_up = t, up
        except (ValueError, IndexError, ZeroDivisionError):
            continue
    out.sort(key=lambda p: p.aos)
    return out
