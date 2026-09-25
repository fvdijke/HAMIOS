"""
HAMIOS v5 — Grafiek-widgets (PySide6 QPainter)

Widgets:
  KpChart          — Kp-index 48u staafdiagram
  BzChart          — Bz zonnewind 24u lijn + vlak
  XrayChart        — GOES X-straling 24u log-schaal
  SolarParamsWidget — Actuele solar-parameters (SFI, SSN, Kp, Bz, wind)

Data-manager:
  NoaaDataManager  — centrale fetcher, distribueert via signals
"""

import datetime
import gzip
import json
import math
import os
import threading
import time
import urllib.request
import xml.etree.ElementTree as ET

from PySide6.QtCore import Qt, QTimer, QThread, Signal, QObject, QPointF
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QPolygonF
)
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QLabel
)

from .theme import BG_SURFACE, TEXT_DIM, TEXT_H1, BORDER
from .i18n import tr

# ── NOAA / HamQSL endpoints ───────────────────────────────────────────────────

_SOLAR_XML  = "https://www.hamqsl.com/solarxml.php"
_SW_SPEED   = "https://services.swpc.noaa.gov/products/summary/solar-wind-speed.json"
_SW_MAG     = "https://services.swpc.noaa.gov/products/summary/solar-wind-mag-field.json"
# NOAA heeft products/solar-wind/ (mag-1-day, plasma-1-day) opgeheven (HTTP 404).
# Vervanging: real-time solar wind per minuut, 24 u (gzip ~100–160 KB).
_RTSW_MAG   = "https://services.swpc.noaa.gov/json/rtsw/rtsw_mag_1m.json"
_RTSW_WIND  = "https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json"
# Officiële NOAA-schalen R (radio blackout), S (stralingsstorm), G (geomagn.)
_SCALES_URL = "https://services.swpc.noaa.gov/products/noaa-scales.json"
# D-RAP: hoogste frequentie die door D-laag-absorptie verzwakt wordt (per lat/lon)
_DRAP_URL    = "https://services.swpc.noaa.gov/text/drap_global_frequencies.txt"
# OVATION: kans op aurora per graad (voor de kaart)
_OVATION_URL = "https://services.swpc.noaa.gov/json/ovation_aurora_latest.json"
# 27-dagen-vooruitzicht (flux, A-index, max Kp per dag)
_OUTLOOK_URL = "https://services.swpc.noaa.gov/text/27-day-outlook.txt"
_KP_URL     = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
_KP_1M_URL  = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
_XRAY_URL   = "https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json"
_STORM_URL  = "https://services.swpc.noaa.gov/text/3-day-geomag-forecast.txt"
_ALERTS_URL = "https://services.swpc.noaa.gov/products/alerts.json"

_UA = {"User-Agent": "HAMIOS/5.7", "Accept-Encoding": "gzip"}

# ── Minimale leeftijd per bron ────────────────────────────────────────────────
# Niet elke bron verandert even vaak. Een verversingsronde (standaard elke
# 5 min) downloadt een bron alleen als de bewaarde versie ouder is dan hieronder;
# anders wordt de bewaarde data opnieuw verwerkt (grafieken schuiven gewoon door).
# Bronnen die niet in de lijst staan: elke ronde.
_MAX_AGE_S = {
    _SOLAR_XML:   30 * 60,      # HamQSL: SFI dagelijks, K per 3 u
    _KP_URL:      60 * 60,      # officiële Kp per 3 u (48u-grafiek)
    _XRAY_URL:    10 * 60,      # 24u-reeks per minuut — 10 min is ruim genoeg
    _RTSW_MAG:    10 * 60,      # Bz 24u (per minuut, ~160 KB)
    _RTSW_WIND:   10 * 60,      # dichtheid + snelheidssprong (~100 KB)
    _SCALES_URL:  15 * 60,      # NOAA R/S/G — wijzigt alleen bij gebeurtenissen
    _ALERTS_URL:  15 * 60,      # meldingen — bij uitgifte
    _STORM_URL:   3 * 60 * 60,  # 3-daagse prognose — 2× per dag uitgegeven
    _OVATION_URL: 15 * 60,      # aurora-kaart (~150 KB) — per ~5 min, 15 min volstaat
    _OUTLOOK_URL: 12 * 60 * 60, # 27-dagen-vooruitzicht — 1× per week uitgegeven
    # _DRAP_URL: 2 KB, per minuut bijgewerkt → elke ronde
    # _KP_1M_URL, _SW_SPEED, _SW_MAG: klein en per minuut → elke ronde
}
_cache: dict = {}             # url → (monotonic-tijd, data)
_cache_lock = threading.Lock()


def _cached(url: str):
    """Bewaarde data als die nog jong genoeg is, anders None."""
    max_age = _MAX_AGE_S.get(url)
    if not max_age:
        return None
    with _cache_lock:
        hit = _cache.get(url)
    if hit and time.monotonic() - hit[0] < max_age:
        return hit[1]
    return None


def _store(url: str, data):
    if data is not None and url in _MAX_AGE_S:
        with _cache_lock:
            _cache[url] = (time.monotonic(), data)


def _download(url: str, timeout: float) -> bytes:
    req = urllib.request.Request(url, headers=_UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
        if r.headers.get("Content-Encoding", "").lower() == "gzip":
            body = gzip.decompress(body)
        return body


def _get_json(url: str, timeout: float = 10):
    """JSON ophalen (gzip scheelt 5–10×); binnen de minimale leeftijd uit cache.
    Bij een mislukte download: laatst bewaarde versie (ook als die ouder is)."""
    hit = _cached(url)
    if hit is not None:
        return hit
    try:
        data = json.loads(_download(url, timeout).decode())
        _store(url, data)
        return data
    except Exception:
        with _cache_lock:
            old = _cache.get(url)
        return old[1] if old else None


def _rtsw_active(rows) -> list:
    """RTSW-rijen van de actieve satelliet, oud → nieuw."""
    if not isinstance(rows, list):
        return []
    act = [r for r in rows if isinstance(r, dict) and r.get("active")]
    act.sort(key=lambda r: str(r.get("time_tag", "")))
    return act


def _parse_ts(tag: str) -> datetime.datetime | None:
    try:
        return datetime.datetime.strptime(str(tag)[:19].replace("T", " "),
                                          "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=datetime.timezone.utc)
    except ValueError:
        return None


def speed_jump(rows: list) -> int:
    """Sprong in zonnewindsnelheid (km/s): mediaan laatste 10 min minus mediaan
    30–60 min eerder. > ~100 km/s wijst op een schokgolf (CME-aankomst)."""
    now = datetime.datetime.now(datetime.timezone.utc)
    recent, before = [], []
    for r in rows:
        v, ts = r.get("proton_speed"), _parse_ts(r.get("time_tag", ""))
        if v is None or ts is None:
            continue
        age = (now - ts).total_seconds() / 60
        if age <= 10:
            recent.append(float(v))
        elif 30 <= age <= 60:
            before.append(float(v))
    if len(recent) < 3 or len(before) < 5:
        return 0
    med = lambda xs: sorted(xs)[len(xs) // 2]   # noqa: E731
    return int(round(med(recent) - med(before)))


def parse_drap(text: str) -> dict | None:
    """drap_global_frequencies.txt → {'lats', 'lons', 'grid' (MHz), 'valid' (UTC),
    'xray_msg', 'proton_msg', 'recovery'} of None."""
    lats, grid, lons = [], [], None
    meta = {}
    valid = None
    for line in text.splitlines():
        st = line.strip()
        if st.startswith("#"):
            body = st.lstrip("#").strip()
            if body.startswith("Product Valid At"):
                try:
                    valid = datetime.datetime.strptime(
                        body.split(":", 1)[1].strip()[:16], "%Y-%m-%d %H:%M").replace(
                        tzinfo=datetime.timezone.utc)
                except ValueError:
                    pass
            for key, name in (("X-RAY Message", "xray_msg"), ("Proton Message", "proton_msg"),
                              ("Estimated Recovery Time", "recovery")):
                if body.startswith(key):
                    meta[name] = body.split(":", 1)[1].strip()
            continue
        if "|" in st:
            lat_s, vals = st.split("|", 1)
            try:
                lats.append(float(lat_s))
                grid.append([float(v) for v in vals.split()])
            except ValueError:
                continue
        elif lons is None and st and not st.startswith("-" * 5):
            try:
                lons = [float(v) for v in st.split()]
            except ValueError:
                lons = None
    if not lats or not lons or any(len(r) != len(lons) for r in grid):
        return None
    return {"lats": lats, "lons": lons, "grid": grid, "valid": valid, **meta}


def parse_outlook(text: str) -> list:
    """27-day-outlook.txt → [(datetime.date, flux, A, Kp_max), …]."""
    out = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 6 and parts[0].isdigit():
            try:
                d = datetime.datetime.strptime(" ".join(parts[:3]), "%Y %b %d").date()
                out.append((d, int(parts[3]), int(parts[4]), int(parts[5])))
            except ValueError:
                continue
    return out


def ovation_rgba(data) -> bytes | None:
    """OVATION-coördinaten [lon 0–359, lat −90–90, kans %] → RGBA-bytes voor een
    360×181-beeld (kolom 0 = −180°, rij 0 = +90°). Groen → geel → rood, doorzichtig
    onder 4 %."""
    try:
        coords = data["coordinates"]
    except (KeyError, TypeError):
        return None
    W, H = 360, 181
    buf = bytearray(W * H * 4)
    for lon, lat, prob in coords:
        # |lat| < 25°: geen aurora — en de OVATION-data bevat op 0° een naad
        # (rij met kans 4 % waar de halfronden samenkomen) die anders als lijn
        # over de evenaar zichtbaar is
        if prob < 4 or abs(lat) < 25:
            continue
        x = (int(lon) + 180) % 360
        y = 90 - int(lat)
        if not (0 <= y < H):
            continue
        p = min(100, int(prob))
        if p < 30:
            r, g, b = 60, 220, 90
        elif p < 60:
            r, g, b = 230, 220, 60
        else:
            r, g, b = 240, 80, 40
        a = min(190, 40 + p * 3)
        i = (y * W + x) * 4
        buf[i:i + 4] = bytes((r, g, b, a))
    return bytes(buf)


def parse_scales(data) -> dict:
    """noaa-scales.json → {noaa_R, noaa_S, noaa_G (nu, 0–5), noaa_G_tomorrow,
    noaa_R_minor_prob_tomorrow (%)}."""
    out = {}
    try:
        now, tom = data.get("0", {}), data.get("1", {})
        for k in ("R", "S", "G"):
            out[f"noaa_{k}"] = int((now.get(k) or {}).get("Scale") or 0)
        out["noaa_G_tomorrow"] = int((tom.get("G") or {}).get("Scale") or 0)
        out["noaa_R_minor_prob_tomorrow"] = int((tom.get("R") or {}).get("MinorProb") or 0)
    except (AttributeError, TypeError, ValueError):
        pass
    return out


def _get_raw(url: str) -> bytes | None:
    """Ruwe bytes ophalen; zelfde cache-regels als _get_json."""
    hit = _cached(url)
    if hit is not None:
        return hit
    try:
        body = _download(url, 10)
        _store(url, body)
        return body
    except Exception:
        with _cache_lock:
            old = _cache.get(url)
        return old[1] if old else None


# ── Achtergrond data-fetcher ──────────────────────────────────────────────────

class _FetchThread(QThread):
    """Voert één fetch-ronde uit en emitteert resultaten."""
    solar_ready  = Signal(dict)
    kp_ready     = Signal(list)
    bz_ready     = Signal(list)
    xray_ready   = Signal(list)
    storm_ready  = Signal(dict)   # {day0..2: {active, minor, mod, sev, extreme}}
    alerts_ready = Signal(list)   # [{severity, message, issued}, ...]
    drap_ready    = Signal(dict)    # parse_drap()
    aurora_ready  = Signal(object)  # (rgba-bytes 360×181, waarnemingstijd-str)
    outlook_ready = Signal(list)    # parse_outlook()

    def run(self):
        self._fetch_solar()
        self._fetch_kp()
        self._fetch_bz()
        self._fetch_xray()
        self._fetch_storm()
        self._fetch_alerts()
        self._fetch_drap()
        self._fetch_ovation()
        self._fetch_outlook()

    # ── P3: absorptie, aurora, 27-dagen ──────────────────────────────────────
    def _fetch_drap(self):
        raw = _get_raw(_DRAP_URL)
        if raw:
            d = parse_drap(raw.decode("utf-8", errors="replace"))
            if d:
                self.drap_ready.emit(d)

    def _fetch_ovation(self):
        data = _get_json(_OVATION_URL, timeout=20)
        rgba = ovation_rgba(data) if isinstance(data, dict) else None
        if rgba:
            self.aurora_ready.emit((rgba, str(data.get("Observation Time", ""))))

    def _fetch_outlook(self):
        raw = _get_raw(_OUTLOOK_URL)
        if raw:
            rows = parse_outlook(raw.decode("utf-8", errors="replace"))
            if rows:
                self.outlook_ready.emit(rows)

    # ── Solar params ──────────────────────────────────────────────────────────
    def _fetch_solar(self):
        data: dict = {}
        raw = _get_raw(_SOLAR_XML)
        if raw:
            try:
                root = ET.fromstring(raw)
                sd = root.find(".//solardata")
                if sd is not None:
                    data = {
                        "sfi":       sd.findtext("solarflux", "—").strip(),
                        "ssn":       sd.findtext("sunspots",  "—").strip(),
                        "a_index":   sd.findtext("aindex",    "—").strip(),
                        "k_index":   sd.findtext("kindex",    "—").strip(),
                        "xray":      sd.findtext("xray",      "—").strip(),
                        "updated":   sd.findtext("updated",   "—").strip(),
                    }
                    # Bandcondities uit <calculatedconditions>
                    for key, bname, tstr in [
                        ("band_80m_day", "80m-40m", "day"),
                        ("band_20m_day", "30m-20m", "day"),
                        ("band_17m_day", "17m-15m", "day"),
                        ("band_10m_day", "12m-10m", "day"),
                        ("band_80m_ngt", "80m-40m", "night"),
                        ("band_20m_ngt", "30m-20m", "night"),
                        ("band_17m_ngt", "17m-15m", "night"),
                        ("band_10m_ngt", "12m-10m", "night"),
                    ]:
                        for b in sd.findall("calculatedconditions/band"):
                            if b.get("name") == bname and b.get("time") == tstr:
                                data[key] = (b.text or "—").strip()
                                break
                        else:
                            data.setdefault(key, "—")
            except Exception:
                pass

        # K-index: NOAA geschatte planetaire Kp (per minuut) — dezelfde bron als
        # de Kp-grafiek en actueler dan de 3-uurswaarde van HamQSL (= terugval)
        kp1m = _get_json(_KP_1M_URL)
        if isinstance(kp1m, list) and kp1m:
            try:
                data["k_index"] = f"{float(kp1m[-1]['estimated_kp']):.1f}"
                data["k_source"] = "NOAA"
            except (KeyError, TypeError, ValueError):
                pass

        # Solar wind speed
        sw = _get_json(_SW_SPEED)
        if isinstance(sw, list) and sw:
            e = sw[0]
            v = e.get("proton_speed")
            data["sw_speed"] = f"{float(v):.0f}" if v is not None else "—"
        else:
            data["sw_speed"] = "—"

        # Bz current
        mag = _get_json(_SW_MAG)
        if isinstance(mag, list) and mag:
            e = mag[0]
            bz = e.get("bz_gsm")
            data["sw_bz"] = f"{float(bz):+.1f}" if bz is not None else "—"
        else:
            data["sw_bz"] = "—"

        # Zonnewind: dichtheid + snelheidssprong (schokgolf) uit RTSW per minuut
        wind = _rtsw_active(_get_json(_RTSW_WIND, timeout=20))
        data["sw_density"] = "—"
        for row in reversed(wind):
            if row.get("proton_density") is not None:
                data["sw_density"] = f"{float(row['proton_density']):.1f}"
                break
        data["sw_speed_jump"] = speed_jump(wind)

        # Officiële NOAA-schalen (R/S/G) — gebeurtenissen voor het advies
        scales = _get_json(_SCALES_URL)
        if isinstance(scales, dict):
            data.update(parse_scales(scales))

        if data:
            self.solar_ready.emit(data)

    # ── Kp 48h ────────────────────────────────────────────────────────────────
    def _fetch_kp(self):
        rows = _get_json(_KP_URL)
        if not rows:
            return
        now = datetime.datetime.now(datetime.timezone.utc)
        pts = []
        for row in rows:
            try:
                if isinstance(row, dict):
                    ts_str = str(row.get("time_tag", ""))
                    kp = float(row.get("Kp") or row.get("kp") or 0)
                elif isinstance(row, list) and len(row) >= 2:
                    if str(row[0]).lower().startswith("time"):
                        continue
                    ts_str, kp = str(row[0]), float(row[1])
                else:
                    continue
                ts = datetime.datetime.strptime(
                    ts_str[:19].replace("T", " "), "%Y-%m-%d %H:%M:%S"
                ).replace(tzinfo=datetime.timezone.utc)
                ha = (now - ts).total_seconds() / 3600
                if ha <= 48:
                    pts.append((ha, kp))
            except Exception:
                continue
        pts.reverse()
        self.kp_ready.emit(pts)

    # ── Bz 24h ────────────────────────────────────────────────────────────────
    def _fetch_bz(self):
        rows = _rtsw_active(_get_json(_RTSW_MAG, timeout=20))
        if not rows:
            return
        now = datetime.datetime.now(datetime.timezone.utc)
        pts = []
        for row in rows:
            bz, ts = row.get("bz_gsm"), _parse_ts(row.get("time_tag", ""))
            if bz is None or ts is None:
                continue
            ha = (now - ts).total_seconds() / 3600
            if ha <= 24:
                pts.append((ha, float(bz)))
        pts.sort(key=lambda p: p[0])         # nieuwste eerst (uren geleden oplopend), zoals voorheen
        if len(pts) > 240:
            step = len(pts) // 240
            pts = pts[::step]
        self.bz_ready.emit(pts)

    # ── Storm forecast ────────────────────────────────────────────────────────
    def _fetch_storm(self):
        """NOAA 3-day geomag forecast. Formaat: 'Minor storm  15/35/35'"""
        import re as _re
        raw = _get_raw(_STORM_URL)
        if not raw:
            return
        text = raw.decode("utf-8", errors="replace")
        result: dict = {}
        # v4-formule: zoek regelnaam + slash-gescheiden getallen
        _LEVELS = [
            ("active",   r"Active"),
            ("minor",    r"Minor storm"),
            ("moderate", r"Moderate storm"),
            ("severe",   r"Strong-Extreme storm"),
        ]
        for key, pat in _LEVELS:
            m = _re.search(pat + r'\s+([\d/]+)', text, _re.IGNORECASE)
            if m:
                try:
                    vals = [int(v.strip()) for v in m.group(1).split('/')]
                    if len(vals) >= 3:
                        result[key] = vals[:3]
                except (ValueError, TypeError):
                    pass
        if result:
            self.storm_ready.emit(result)

    # ── NOAA alerts ──────────────────────────────────────────────────────────
    def _fetch_alerts(self):
        data = _get_json(_ALERTS_URL)
        if not isinstance(data, list):
            return
        alerts = []
        for item in data[:20]:  # max 20 meest recente
            msg = str(item.get("message", ""))
            issued = str(item.get("issue_datetime", ""))[:16]
            product = str(item.get("product_id", ""))
            # Bepaal ernst op basis van product_id
            sev = ("high"   if any(x in product for x in ("X-RAY", "WATCH", "WARNING"))
                   else "medium" if "ALERT" in product
                   else "low")
            # Eerste regel van message als samenvatting
            summary = msg.split("\n")[2].strip() if "\n" in msg else msg[:80]
            alerts.append({"severity": sev, "summary": summary, "issued": issued,
                           "message": msg})
        self.alerts_ready.emit(alerts)

    # ── X-ray 24h ─────────────────────────────────────────────────────────────
    def _fetch_xray(self):
        rows = _get_json(_XRAY_URL)
        if not rows:
            return
        now = datetime.datetime.now(datetime.timezone.utc)
        pts = []
        for row in rows:
            try:
                if row.get("energy", "") != "0.1-0.8nm":
                    continue
                ts = datetime.datetime.strptime(
                    str(row["time_tag"])[:19].replace("T", " "), "%Y-%m-%d %H:%M:%S"
                ).replace(tzinfo=datetime.timezone.utc)
                flux = float(row.get("flux") or 0)
                if flux <= 0:
                    continue
                ha = (now - ts).total_seconds() / 3600
                if ha <= 24:
                    pts.append((ha, flux))
            except Exception:
                continue
        pts.reverse()
        if len(pts) > 120:
            step = len(pts) // 120
            pts = pts[::step]
        self.xray_ready.emit(pts)


class NoaaDataManager(QObject):
    """Centrale data-manager. Maak één instantie aan en deel de signals."""
    solar_ready  = Signal(dict)
    kp_ready     = Signal(list)
    bz_ready     = Signal(list)
    xray_ready   = Signal(list)
    storm_ready  = Signal(dict)
    alerts_ready         = Signal(list)
    drap_ready           = Signal(dict)
    aurora_ready         = Signal(object)
    outlook_ready        = Signal(list)
    next_refresh_changed = Signal(float)   # monotonic-tijdstip volgende refresh

    def __init__(self, parent=None):
        super().__init__(parent)
        self._busy   = False
        self._thread = None
        self._timer  = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(5 * 60 * 1000)
        QTimer.singleShot(1000, self.refresh)

    def stop(self):
        self._timer.stop()

    def set_interval(self, minutes: int):
        """Pas het refresh-interval aan (0 = stop)."""
        self._timer.stop()
        if minutes > 0:
            self._timer.start(minutes * 60 * 1000)
            self.refresh()
        else:
            # Interval 0 = Uit: emit 0 zodat countdown "Uit" toont
            self.next_refresh_changed.emit(0.0)

    def refresh(self):
        if self._busy:
            return
        self._busy = True
        import time as _t
        self.next_refresh_changed.emit(
            _t.monotonic() + self._timer.interval() / 1000.0)
        t = _FetchThread()
        t.solar_ready.connect(self.solar_ready)
        t.kp_ready.connect(self.kp_ready)
        t.bz_ready.connect(self.bz_ready)
        t.xray_ready.connect(self.xray_ready)
        t.storm_ready.connect(self.storm_ready)
        t.alerts_ready.connect(self.alerts_ready)
        t.drap_ready.connect(self.drap_ready)
        t.aurora_ready.connect(self.aurora_ready)
        t.outlook_ready.connect(self.outlook_ready)
        t.finished.connect(self._on_fetch_done)
        t.finished.connect(t.deleteLater)
        self._thread = t
        t.start()

    def _on_fetch_done(self):
        self._busy   = False
        self._thread = None


# ── Kleuren hulpfuncties ──────────────────────────────────────────────────────

def _kp_color(kp: float) -> QColor:
    if kp >= 7: return QColor("#EF5350")
    if kp >= 5: return QColor("#FFA726")
    if kp >= 3: return QColor("#FFF176")
    return QColor("#4FC3F7")


def _xray_class(flux: float) -> tuple[str, QColor]:
    if flux >= 1e-4: return f"X{flux/1e-4:.1f}", QColor("#EF5350")
    if flux >= 1e-5: return f"M{flux/1e-5:.1f}", QColor("#FFA726")
    if flux >= 1e-6: return f"C{flux/1e-6:.1f}", QColor("#FFF176")
    if flux >= 1e-7: return f"B{flux/1e-7:.1f}", QColor("#4FC3F7")
    return f"A{flux/1e-8:.1f}", QColor(TEXT_DIM)


# ── Geschiedenis-opslag ───────────────────────────────────────────────────────

from ._appdir import APP_DIR as _HERE
_HISTORY_FILE = os.path.join(_HERE, "config", "hamios_history.json")


class HistoryStore:
    """Tijdreeks SFI + Kp, bewaard in JSON (max 30 dagen)."""

    MAX_SECONDS = 30 * 86400

    def __init__(self):
        self._data: list = []  # [[timestamp, sfi, k_index], ...]
        self._lock = threading.Lock()
        self._load()

    def _load(self):
        try:
            if os.path.exists(_HISTORY_FILE):
                with open(_HISTORY_FILE, encoding="utf-8") as f:
                    self._data = json.load(f)
        except Exception:
            self._data = []

    def append(self, sfi: float, k_index: float):
        now = time.time()
        cutoff = now - self.MAX_SECONDS
        with self._lock:
            self._data.append([now, sfi, k_index])
            self._data = [d for d in self._data if d[0] >= cutoff]
        threading.Thread(target=self._save, daemon=True).start()

    def _save(self):
        with self._lock:
            data = list(self._data)
        try:
            with open(_HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception:
            pass

    def get_hours(self, hours: float) -> list[tuple[float, float, float]]:
        """→ [(hours_ago, sfi, k_index), ...] oudste eerst."""
        now = time.time()
        cutoff = now - hours * 3600
        with self._lock:
            raw = [d for d in self._data if d[0] >= cutoff]
        return [((now - d[0]) / 3600, d[1], d[2]) for d in raw]


# Singleton instantie
history = HistoryStore()


# ── KpChart ───────────────────────────────────────────────────────────────────

class KpChart(QWidget):
    """Kp-index staafdiagram, 48 uur."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pts: list = []
        self.setMinimumHeight(60)
        self.setAttribute(Qt.WA_OpaquePaintEvent)

    def set_data(self, pts: list):
        self._pts = pts
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)
        W, H = self.width(), self.height()

        p.fillRect(0, 0, W, H, QColor(BG_SURFACE))

        if not self._pts:
            p.setPen(QColor(TEXT_DIM))
            p.setFont(QFont("Segoe UI", 9))
            p.drawText(0, 0, W, H, Qt.AlignCenter, "—")
            return

        PL, PR, PT, PB = 22, 4, 6, 16
        gW, gH = W - PL - PR, H - PT - PB
        KM = 9.0
        f6 = QFont("Segoe UI", 6)
        f7b = QFont("Segoe UI", 7)
        f7b.setBold(True)
        p.setFont(f6)

        # Gridlijnen
        for kp_r, lbl in [(0,"0"),(3,"3"),(5,"5"),(7,"7"),(9,"9")]:
            yr = PT + int(gH * (1.0 - kp_r / KM))
            p.setPen(QPen(QColor(BORDER), 1, Qt.DashLine))
            p.drawLine(PL, yr, W - PR, yr)
            p.setPen(QColor(TEXT_DIM))
            p.drawText(0, yr - 5, PL - 2, 10, Qt.AlignRight | Qt.AlignVCenter, lbl)

        # Stormdrempel (Kp ≥ 5) — oranje stippellijn
        y5 = PT + int(gH * (1.0 - 5.0 / KM))
        p.setPen(QPen(QColor("#FFA726"), 1, Qt.DotLine))
        p.drawLine(PL, y5, W - PR, y5)

        # Staven
        n = len(self._pts)
        bw = max(2, gW // max(n, 1))
        for ha, kp in self._pts:
            xr = PL + int(gW * (1.0 - ha / 48))
            xl = max(PL, xr - bw + 1)
            bh = int(gH * min(kp, KM) / KM)
            if bh > 0:
                p.fillRect(xl, PT + gH - bh, xr - xl, bh, _kp_color(kp))

        # Tijdlabels
        p.setPen(QColor(TEXT_DIM))
        p.setFont(f6)
        p.drawText(PL, H - PB + 2, 24, PB, Qt.AlignLeft,  "48h")
        p.drawText(W - PR - 24, H - PB + 2, 24, PB, Qt.AlignRight, tr("sched.now"))

        # Huidige Kp waarde
        if self._pts:
            last_kp = self._pts[-1][1]
            p.setFont(f7b)
            p.setPen(_kp_color(last_kp))
            p.drawText(W - PR - 32, PT, 32, 14, Qt.AlignRight, f"{last_kp:.1f}")


# ── BzChart ───────────────────────────────────────────────────────────────────

class BzChart(QWidget):
    """Bz zonnewind 24u: lijn + gekleurde vlak-fill."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pts: list = []
        self._bz_range = 40.0
        self.setMinimumHeight(60)
        self.setAttribute(Qt.WA_OpaquePaintEvent)

    def set_data(self, pts: list):
        self._pts = pts
        self.update()

    def set_range(self, nT: float):
        self._bz_range = max(10.0, nT)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()
        p.fillRect(0, 0, W, H, QColor(BG_SURFACE))

        if not self._pts:
            p.setPen(QColor(TEXT_DIM))
            p.setFont(QFont("Segoe UI", 9))
            p.drawText(0, 0, W, H, Qt.AlignCenter, "—")
            return

        BM = self._bz_range
        PL, PR, PT, PB = 30, 6, 6, 16
        gW, gH = W - PL - PR, H - PT - PB
        f6 = QFont("Segoe UI", 6)
        p.setFont(f6)

        def bz_y(bz):
            return PT + gH / 2 - (max(-BM, min(BM, bz)) / BM) * (gH / 2)

        def ha_x(ha):
            return PL + gW * (1.0 - min(ha, 24) / 24)

        y0 = bz_y(0)

        # Tijdgrid (6, 12, 18h)
        for h in (6, 12, 18):
            xg = ha_x(h)
            p.setPen(QPen(QColor("#404850"), 1, Qt.DashLine))
            p.drawLine(int(xg), PT, int(xg), H - PB)

        # Horizontale gridlijnen
        for bz_r in (-BM/2, 0, BM/2):
            yr = bz_y(bz_r)
            is_zero = bz_r == 0
            p.setPen(QPen(QColor("#505860" if is_zero else "#404850"), 1,
                          Qt.SolidLine if is_zero else Qt.DashLine))
            p.drawLine(PL, int(yr), W - PR, int(yr))

        # Y-as labels
        for bz_r in (-BM/2, 0, BM/2):
            yr = bz_y(bz_r)
            p.setPen(QColor(TEXT_DIM))
            p.drawText(0, int(yr) - 5, PL - 2, 10,
                       Qt.AlignRight | Qt.AlignVCenter,
                       f"{int(bz_r):+d}" if bz_r != 0 else "0")

        # Geordend: oudste eerst
        ordered = sorted(self._pts, key=lambda pt: pt[0], reverse=True)
        xy = [(ha_x(ha), bz_y(bz), bz) for ha, bz in ordered]
        if not xy:
            return

        first_x, last_x = xy[0][0], xy[-1][0]

        # Vlak-fill: positief (noord, blauw) en negatief (zuid, rood)
        pos_pts = [QPointF(first_x, y0)]
        neg_pts = [QPointF(first_x, y0)]
        for x, y, bz in xy:
            if bz >= 0:
                pos_pts.append(QPointF(x, y))
            else:
                neg_pts.append(QPointF(x, y))
        pos_pts.append(QPointF(last_x, y0))
        neg_pts.append(QPointF(last_x, y0))

        p.setPen(Qt.NoPen)
        if len(pos_pts) >= 3:
            p.setBrush(QBrush(QColor(26, 58, 74, 160)))
            p.drawPolygon(QPolygonF(pos_pts))
        if len(neg_pts) >= 3:
            p.setBrush(QBrush(QColor(74, 26, 26, 160)))
            p.drawPolygon(QPolygonF(neg_pts))

        # Bz-lijn (blauw > 0, rood < 0)
        prev = None
        for x, y, bz in xy:
            clr = QColor("#4FC3F7") if bz >= 0 else QColor("#EF5350")
            if prev is not None:
                p.setPen(QPen(clr, 1.2))
                p.drawLine(QPointF(*prev), QPointF(x, y))
            prev = (x, y)

        # Labels
        p.setFont(f6)
        p.setPen(QColor(TEXT_DIM))
        p.drawText(PL, H - PB + 2, 24, PB, Qt.AlignLeft,   "24h")
        p.drawText(PL + gW//2 - 12, H - PB + 2, 24, PB, Qt.AlignCenter, "12h")
        p.drawText(W - PR - 24, H - PB + 2, 24, PB, Qt.AlignRight,  tr("sched.now"))

        # Huidige Bz waarde
        if ordered:
            last_bz = ordered[-1][1]
            clr = QColor("#4FC3F7") if last_bz >= 0 else QColor("#EF5350")
            f7b = QFont("Segoe UI", 7); f7b.setBold(True)
            p.setFont(f7b)
            p.setPen(clr)
            p.drawText(W - PR - 40, PT, 40, 14, Qt.AlignRight, f"{last_bz:+.1f} nT")


# ── XrayChart ────────────────────────────────────────────────────────────────

class XrayChart(QWidget):
    """GOES X-straling 24u op log-schaal."""

    _LOG_MIN = -8.5
    _LOG_MAX = -3.5
    _CLASSES = [("A", -8, TEXT_DIM), ("B", -7, "#4FC3F7"),
                ("C", -6, "#66BB6A"), ("M", -5, "#FFA726"), ("X", -4, "#EF5350")]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pts: list = []
        self.setMinimumHeight(60)
        self.setAttribute(Qt.WA_OpaquePaintEvent)

    def set_data(self, pts: list):
        self._pts = pts
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()
        p.fillRect(0, 0, W, H, QColor(BG_SURFACE))

        if not self._pts:
            p.setPen(QColor(TEXT_DIM))
            p.setFont(QFont("Segoe UI", 9))
            p.drawText(0, 0, W, H, Qt.AlignCenter, "—")
            return

        PL, PR, PT, PB = 18, 4, 4, 12
        gW, gH = W - PL - PR, H - PT - PB
        LN, LX = self._LOG_MIN, self._LOG_MAX
        f6 = QFont("Segoe UI", 6)
        p.setFont(f6)

        def flux_y(f):
            lf = max(LN, min(LX, math.log10(f) if f > 0 else LN))
            return PT + int(gH * (1.0 - (lf - LN) / (LX - LN)))

        def ha_x(ha):
            return PL + int(gW * (1.0 - min(ha, 24) / 24))

        # Klasse-gridlijnen
        for cls, lv, col in self._CLASSES:
            yr = PT + int(gH * (1.0 - (lv - LN) / (LX - LN)))
            if PT <= yr <= PT + gH:
                p.setPen(QPen(QColor(BORDER), 1, Qt.DashLine))
                p.drawLine(PL, yr, W - PR, yr)
                p.setPen(QColor(col))
                p.drawText(0, yr - 5, PL - 1, 10,
                           Qt.AlignRight | Qt.AlignVCenter, cls)

        # Lijn
        prev = None
        for ha, flux in self._pts:
            x, y = ha_x(ha), flux_y(flux)
            lf = math.log10(flux) if flux > 0 else LN
            clr = (QColor("#EF5350") if lf >= -5 else
                   QColor("#FFA726") if lf >= -6 else QColor("#66BB6A"))
            if prev and abs(x - prev[0]) < 30:
                p.setPen(QPen(clr, 1.2))
                p.drawLine(prev[0], prev[1], x, y)
            prev = (x, y)

        # Labels
        p.setFont(f6)
        p.setPen(QColor(TEXT_DIM))
        p.drawText(PL, H - PB + 2, 24, PB, Qt.AlignLeft,  "24h")
        p.drawText(W - PR - 24, H - PB + 2, 24, PB, Qt.AlignRight, tr("sched.now"))

        # Huidige klasse
        if self._pts:
            last_flux = self._pts[-1][1]
            cls_str, cls_col = _xray_class(last_flux)
            f7b = QFont("Segoe UI", 7); f7b.setBold(True)
            p.setFont(f7b); p.setPen(cls_col)
            p.drawText(W - PR - 36, PT, 36, 14, Qt.AlignRight, cls_str)


# ── SolarParamsWidget ────────────────────────────────────────────────────────

class SolarParamsWidget(QWidget):
    """Actuele solar-parameters (SFI, SSN, Kp, Bz, solar wind)."""

    # (label, data_key, eenheid, volledige_naam, tooltip, hint_fn)
    _ROWS = [
        ("SFI",        "sfi",        "SFU",    tr("solar.sfi.full"),
         "Solar Flux Index — maat voor ionisatie. Hoog = betere HF-condities.",
         lambda v: (tr("solar.hint.low"),   "#4FC3F7") if v < 100 else
                   (tr("solar.hint.fair"),  "#FFF176") if v < 150 else
                   (tr("solar.hint.high"),  "#FFA726") if v < 200 else
                   (tr("solar.hint.high"),  "#EF5350")),
        ("SSN",        "ssn",        "",       tr("solar.ssn.full"),
         "Zonnevlek-getal (Sunspot Number).",
         lambda v: ("min.",              TEXT_DIM)  if v < 20  else
                   (tr("solar.hint.low"),  "#4FC3F7") if v < 80  else
                   (tr("solar.hint.fair"), "#FFF176") if v < 150 else
                   (tr("solar.hint.high"), "#FFA726")),
        ("K-index",    "k_index",    "(0–9)",  tr("solar.k.full"),
         "Planetaire K-index — geomagnetische activiteit.",
         lambda v: (tr("solar.hint.calm"),   "#4FC3F7") if v < 3 else
                   (tr("solar.hint.active"), "#FFF176") if v < 5 else
                   (tr("solar.hint.storm"),  "#FFA726") if v < 7 else
                   (tr("solar.hint.severe"), "#EF5350")),
        ("A-index",    "a_index",    "",       tr("solar.a.full"),
         "Dagelijks geomagnetisch gemiddelde.",
         lambda v: (tr("solar.hint.calm"),    "#4FC3F7") if v < 15 else
                   (tr("solar.hint.active"),  "#FFF176") if v < 30 else
                   (tr("solar.hint.stormig"), "#FFA726") if v < 50 else
                   (tr("solar.hint.ernstig"), "#EF5350")),
        ("X-straling", "xray",       "",       tr("solar.xray.full"),
         "GOES X-ray klasse. M/X = zonnevlam.",
         None),
        ("SW snelheid","sw_speed",   "km/s",   tr("solar.vsw.full"),
         "Snelheid van de zonnewind.",
         lambda v: ("normaal","#4FC3F7") if v < 500 else
                   ("verhoogd","#FFA726") if v < 700 else
                   ("snel",   "#EF5350")),
        ("SW dichth.", "sw_density", "p/cm³",  tr("solar.nsw.full"),
         "Dichtheid van de zonnewind (protonen/cm3).",
         lambda v: (tr("solar.hint.low"),   "#4FC3F7") if v < 5  else
                   ("normaal","TEXT_H1") if v < 15 else
                   (tr("solar.hint.high"),  "#FFA726")),
        ("Bz (GSM)",   "sw_bz",      "nT",     tr("solar.bz.full"),
         "IMF Bz-component. Negatief = verhoogd stormsrisico.",
         lambda v: (tr("solar.hint.pos"),      "#4FC3F7") if v >= 0 else
                   (tr("solar.hint.neg"),      "#FF8A65") if v > -10 else
                   (tr("solar.hint.storm_ex"), "#EF5350")),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._labels: dict[str, QLabel] = {}
        self._build_ui()

    def _build_ui(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setVerticalSpacing(2)
        layout.setHorizontalSpacing(8)

        f_lbl  = QFont("Segoe UI", 8)
        f_val  = QFont("Segoe UI", 9); f_val.setBold(True)
        f_unit = QFont("Segoe UI", 7)
        f_hint = QFont("Segoe UI", 7)

        self._hint_labels: dict[str, QLabel] = {}

        for row, (name, key, unit, full_name, tooltip, _) in enumerate(self._ROWS):
            # Kolom 0: parameternaam
            lbl = QLabel(name + ":")
            lbl.setFont(f_lbl)
            lbl.setStyleSheet(f"color: {TEXT_DIM};")
            lbl.setToolTip(tooltip)
            layout.addWidget(lbl, row, 0)

            # Kolom 1: waarde (vet)
            val = QLabel("—")
            val.setFont(f_val)
            val.setStyleSheet(f"color: {TEXT_H1};")
            layout.addWidget(val, row, 1)
            self._labels[key] = val

            # Kolom 2: eenheid (klein, grijs)
            unit_lbl = QLabel(unit)
            unit_lbl.setFont(f_unit)
            unit_lbl.setStyleSheet(f"color: {TEXT_DIM};")
            layout.addWidget(unit_lbl, row, 2)

            # Kolom 3: dynamische duiding (klein, gekleurde tekst)
            hint_lbl = QLabel("")
            hint_lbl.setFont(f_hint)
            hint_lbl.setStyleSheet(f"color: {TEXT_DIM};")
            layout.addWidget(hint_lbl, row, 3)
            self._hint_labels[key] = hint_lbl

            # Kolom 4: volledige naam van de parameter
            full_lbl = QLabel(full_name)
            full_lbl.setFont(f_unit)
            full_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-style: italic;")
            full_lbl.setToolTip(tooltip)
            layout.addWidget(full_lbl, row, 4)

        layout.setColumnStretch(1, 0)
        layout.setColumnStretch(3, 0)
        layout.setColumnStretch(4, 1)


    def set_data(self, data: dict):
        for name, key, unit, full_name, tooltip, hint_fn in self._ROWS:
            raw = data.get(key, "—")
            val = str(raw)
            val_lbl  = self._labels.get(key)
            hint_lbl = self._hint_labels.get(key)
            if val_lbl:
                val_lbl.setText(val)
                val_lbl.setStyleSheet(f"color: {self._value_color(key, val)};")
            if hint_lbl and hint_fn:
                try:
                    v = float(str(val).replace("+", "").replace("—", "nan"))
                    if not math.isnan(v):
                        result = hint_fn(v)
                        if result:
                            hint_lbl.setText(result[0])
                            clr = result[1] if result[1] != "TEXT_H1" else TEXT_H1
                            hint_lbl.setStyleSheet(f"color: {clr}; font-size: 7pt;")
                        else:
                            hint_lbl.setText("")
                    else:
                        hint_lbl.setText("")
                except (ValueError, TypeError):
                    hint_lbl.setText("")


    @staticmethod
    def _value_color(key: str, val: str) -> str:
        try:
            v = float(val.replace("+", "").replace("—", "nan"))
            if math.isnan(v):
                return TEXT_DIM
        except ValueError:
            if val.startswith("X"):  return "#EF5350"
            if val.startswith("M"):  return "#FFA726"
            if val.startswith("C"):  return "#FFF176"
            return TEXT_H1

        if key == "k_index":
            if v >= 7: return "#EF5350"
            if v >= 5: return "#FFA726"
            if v >= 3: return "#FFF176"
            return "#4FC3F7"
        if key == "sw_bz":
            if v <= -20: return "#EF5350"
            if v < 0:    return "#FF8A65"
            return "#4FC3F7"
        if key == "sfi":
            if v >= 200: return "#EF5350"
            if v >= 150: return "#FFA726"
            if v >= 100: return "#FFF176"
            return TEXT_H1
        if key == "a_index":
            if v >= 50: return "#EF5350"
            if v >= 30: return "#FFA726"
            return TEXT_H1
        return TEXT_H1
