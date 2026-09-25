"""HAMIOS v5 — Propagatie-advies (P2).

Combineert het centrale propagatiemodel (propagation.py, gekalibreerd op de
gemeten ionosfeer) met wat er NU werkelijk gehoord wordt (WSPR, DX-cluster,
PSKReporter) en met ruimteweer-gebeurtenissen (NOAA R/S/G-schalen, schokgolf,
Bz), tot concrete, gerangschikte aanbevelingen:

    band → mode → richting → tijdvenster   (+ onderbouwing: model / waargenomen)

Pure logica zonder Qt-widgets; het paneel (PropAdvWidget) vertaalt de sleutels
en parameters naar tekst. Alle tijden in UTC (datetime met tzinfo).
"""

from __future__ import annotations

import datetime as _dt
import math
from dataclasses import dataclass, field

from . import propagation as P

LOCAL_KM   = 1500        # "eigen regio" rond de QTH
OBS_STRONG = 8           # zoveel spots op een pad = volledig bevestigd
STEP_MIN   = 30          # resolutie van tijdvensters en tijdlijn
HORIZON_H  = 12

# Banden (kHz-bereik) voor het indelen van spots
BAND_KHZ = [
    ("160m", 1800, 2000), ("80m", 3500, 4000), ("60m", 5250, 5450),
    ("40m", 7000, 7300), ("30m", 10100, 10150), ("20m", 14000, 14350),
    ("17m", 18068, 18168), ("15m", 21000, 21450), ("12m", 24890, 24990),
    ("10m", 28000, 29700), ("6m", 50000, 54000),
]
_BAND_ORDER = [b for b, _, _ in BAND_KHZ]

# Werkfrequenties (kHz) per mode — digitaal = FT8, anders gangbaar segment
FREQ_KHZ = {
    "FT8": {"160m": 1840, "80m": 3573, "60m": 5357, "40m": 7074, "30m": 10136,
            "20m": 14074, "17m": 18100, "15m": 21074, "12m": 24915, "10m": 28074, "6m": 50313},
    "FT4": {"80m": 3575, "40m": 7047.5, "30m": 10140, "20m": 14080, "17m": 18104,
            "15m": 21140, "12m": 24919, "10m": 28180, "6m": 50318},
    "CW":  {"160m": 1830, "80m": 3530, "60m": 5354, "40m": 7030, "30m": 10116,
            "20m": 14030, "17m": 18080, "15m": 21030, "12m": 24900, "10m": 28030, "6m": 50090},
    "SSB": {"160m": 1850, "80m": 3700, "60m": 5360, "40m": 7150, "30m": 10136,
            "20m": 14250, "17m": 18130, "15m": 21300, "12m": 24950, "10m": 28450, "6m": 50150},
}
_DIGITAL = {"FT8", "FT4", "WSPR", "PSK31", "RTTY", "JS8"}


# Grote meteorenzwermen (IMO-kalender): (id, maand, piekdag, ZHR, ± dagen actief)
# Arietiden en zeta-Perseïden zijn dagzwermen: alleen via radio (meteorscatter).
METEOR_SHOWERS = [
    ("QUA", 1, 3, 110, 1), ("LYR", 4, 22, 18, 1), ("ETA", 5, 6, 50, 2),
    ("ARI", 6, 7, 30, 3), ("ZPE", 6, 9, 20, 2), ("SDA", 7, 30, 25, 2),
    ("PER", 8, 12, 100, 2), ("DRA", 10, 8, 10, 1), ("ORI", 10, 21, 20, 2),
    ("LEO", 11, 17, 15, 1), ("GEM", 12, 14, 150, 2), ("URS", 12, 22, 10, 1),
]


def active_meteor_shower(day: _dt.date):
    """(id, piekdatum, ZHR) van de actieve zwerm met de hoogste ZHR, of None."""
    best = None
    for sid, m, d, zhr, win in METEOR_SHOWERS:
        for yr in (day.year - 1, day.year, day.year + 1):
            try:
                peak = _dt.date(yr, m, d)
            except ValueError:
                continue
            if abs((day - peak).days) <= win and (best is None or zhr > best[2]):
                best = (sid, peak, zhr)
    return best


def band_of(freq_khz: float) -> str | None:
    for name, lo, hi in BAND_KHZ:
        if lo <= freq_khz <= hi:
            return name
    return None


def _dist(a, b) -> float:
    return P._dist_km(a[0], a[1], b[0], b[1])


def region_of(point, qth) -> str:
    """'local' binnen LOCAL_KM van de QTH, anders de dichtstbijzijnde DX-regio."""
    if _dist(point, qth) < LOCAL_KM:
        return "local"
    return min(P.DX_REGIONS, key=lambda r: _dist(point, (r[1], r[2])))[0]


# ── Uitvoer ───────────────────────────────────────────────────────────────────

@dataclass
class Rec:
    region: str
    band: str
    mode: str
    freq_khz: float
    pct: int                       # modelkans op dit pad (%)
    eff: int                       # effectieve kans (%): model + waarnemingen
    obs: int                       # waarnemingen op dit pad (laatste ~30 min)
    confidence: str                # 'confirmed' | 'observed' | 'model'
    until: _dt.datetime | None     # open tot (None = heel de horizon open)
    score: float
    lat: float
    lon: float
    dist_km: int
    # Onderbouwing (voor de tooltip-uitleg)
    band_mhz: float = 0.0          # middenfrequentie van de band
    path_muf: float = 0.0          # laagste MUF op de controlepunten van het pad
    path_luf: float = 0.0          # hoogste LUF op de controlepunten
    hops: int = 1                  # aantal F2-sprongen (~3500 km per sprong)
    cp_day: tuple = ()             # dag (True) / nacht per controlepunt
    sources: dict = field(default_factory=dict)   # {'WSPR': n, 'DX': n, 'PSK': n}
    absorption: float = 0.0        # gemeten D-laag-absorptie op het pad (D-RAP, MHz)


@dataclass
class Event:
    level: str                     # 'red' | 'amber' | 'green' | 'info'
    icon: str
    key: str                       # i18n-sleutel
    params: dict = field(default_factory=dict)


@dataclass
class TimelineItem:
    time: _dt.datetime
    icon: str
    key: str
    params: dict = field(default_factory=dict)


@dataclass
class Advice:
    level: int                     # 0 slecht · 1 matig · 2 goed · 3 uitstekend
    recs: list
    events: list
    timeline: list
    trends: dict                   # band → +1 / 0 / −1 (komend uur)
    es: dict
    muf: float
    source: str                    # 'model' of naam ionosonde
    obs_total: int
    is_day: bool
    good: int = 0                  # aantal sterke paden (voor uitleg oordeel)
    level_raw: int = 0             # oordeel vóór correctie voor gebeurtenissen
    obs_by_source: dict = field(default_factory=dict)


# ── Waarnemingen ──────────────────────────────────────────────────────────────

def collect_observations(qth, wspr=(), dx=(), psk=()) -> dict:
    """{(regio, band): aantal} + {'_es': [(band, km)]} uit spots waarvan één kant
    in de eigen regio ligt. Formaten:
      wspr: records van WSPRFeed (dict met band, grid, distance, direction)
      dx:   (dx_lat, dx_lon, call, freq_khz, de_lat, de_lon, spotter)
      psk:  ((tx_lat, tx_lon), (rx_lat, rx_lon), freq_khz, snr, mode, tx, rx)
    """
    from .layers import _maidenhead_to_latlon
    counts: dict = {}
    by_src: dict = {}                # (regio, band) → {'WSPR': n, 'DX': n, 'PSK': n}
    es: list = []

    def add(far, band, path_km, src):
        if band is None:
            return
        reg = region_of(far, qth)
        if reg != "local":
            counts[(reg, band)] = counts.get((reg, band), 0) + 1
            d = by_src.setdefault((reg, band), {})
            d[src] = d.get(src, 0) + 1
        if band in ("10m", "6m") and 500 <= path_km <= 2300:
            es.append((band, int(path_km)))

    for r in wspr:
        far = _maidenhead_to_latlon(r.get("grid", ""))
        if far:
            add(far, r.get("band"), r.get("distance") or _dist(far, qth), "WSPR")

    def pair(a, b, freq, src):
        if a is None or b is None or None in a or None in b:
            return
        band = band_of(freq)
        near_a, near_b = _dist(a, qth) < LOCAL_KM, _dist(b, qth) < LOCAL_KM
        if near_a and not near_b:
            add(b, band, _dist(a, b), src)
        elif near_b and not near_a:
            add(a, band, _dist(a, b), src)
        elif near_a and near_b:
            add(b, band, _dist(a, b), src)      # alleen voor Es (korte sprong)

    for s in dx:
        try:
            pair((s[4], s[5]), (s[0], s[1]), float(s[3]), "DX")
        except (IndexError, TypeError, ValueError):
            continue
    for r in psk:
        try:
            pair(tuple(r[1]), tuple(r[0]), float(r[2]), "PSK")
        except (IndexError, TypeError, ValueError):
            continue
    counts["_es"] = es
    counts["_src"] = by_src
    return counts


# ── Advies ────────────────────────────────────────────────────────────────────

# Banden waar geen telefonie is toegestaan (IARU): alleen CW en digitaal
_NO_PHONE = {"30m"}


def _mode_for(cfg_mode: str, pct: int, band: str = "") -> str:
    """Eigen mode, maar zwakke paden liever digitaal; geen SSB op 30m."""
    m = (cfg_mode or "SSB").upper()
    if m in ("SSB", "AM", "FM") and band in _NO_PHONE:
        return "FT8"
    if pct >= 60 or m in _DIGITAL or m == "CW":
        return m if m in FREQ_KHZ else ("FT8" if m in _DIGITAL else m)
    return "FT8"


def _freq_for(mode: str, band: str) -> float:
    table = FREQ_KHZ.get(mode) or FREQ_KHZ["FT8"]
    return table.get(band) or FREQ_KHZ["FT8"].get(band, 0)


def _num(solar: dict, key: str, default: float = 0.0) -> float:
    try:
        return float(str(solar.get(key, default)).replace("—", str(default)) or default)
    except (TypeError, ValueError):
        return float(default)


def _open_until(eng, qth, target, band, snr, now) -> _dt.datetime | None:
    """Eerste tijdstip (30-min stappen) waarop het pad onder 50 % zakt."""
    for i in range(1, HORIZON_H * 60 // STEP_MIN + 1):
        t = now + _dt.timedelta(minutes=i * STEP_MIN)
        if eng.path_band_pct(qth[0], qth[1], target[0], target[1], t, snr).get(band, 0) < 50:
            return t
    return None


def build_advice(qth, solar: dict, snr_db: float = 0.0, cfg_mode: str = "SSB",
                 wspr=(), dx=(), psk=(), engine=None,
                 now: _dt.datetime | None = None, k_alert: float = 5) -> Advice:
    """k_alert: K-drempel uit de instellingen (dezelfde als het meldingen-paneel);
    daaronder geen geomagnetische melding, vanaf G1 (K 5) altijd."""
    eng = engine or P.ENGINE
    now = now or _dt.datetime.now(_dt.timezone.utc)
    obs = collect_observations(qth, wspr, dx, psk)
    es_spots = obs.pop("_es", [])
    obs_src = obs.pop("_src", {})
    totals: dict = {}
    for d in obs_src.values():
        for k, v in d.items():
            totals[k] = totals.get(k, 0) + v
    here = eng.conditions(qth[0], qth[1], now, snr_db, now)

    # ── Aanbevelingen: per regio de beste band ───────────────────────────────
    recs = []
    for name, rlat, rlon in P.DX_REGIONS:
        d = P._dist_km(qth[0], qth[1], rlat, rlon)
        if d < LOCAL_KM:
            continue
        detail = eng.path_detail(qth[0], qth[1], rlat, rlon, now, snr_db)
        pct = detail["pct"]
        best = None
        for band in _BAND_ORDER:
            if band == "6m" and obs.get((name, band), 0) < 3:
                continue                         # 6m F2 alleen als het echt gehoord wordt
            p, n = pct.get(band, 0), obs.get((name, band), 0)
            # Effectieve kans: waarnemingen tellen als bewijs — vanaf 3 spots is
            # het pad minstens 60 % zeker, bij OBS_STRONG spots volledig. Zo kan
            # een hoge modelwaarde de werkelijkheid nooit overstemmen.
            eff = p / 100 if n < 3 else max(p / 100, 0.6 + 0.4 * min(1.0, n / OBS_STRONG))
            if eff < 0.5:
                continue
            # Hoogste betrouwbaar open band voorkeur (minder absorptie voor DX),
            # plus een kleine bonus voor bevestiging door waarnemingen
            rank = _BAND_ORDER.index(band) / (len(_BAND_ORDER) - 1)
            score = eff * (0.8 + 0.2 * rank) + 0.1 * min(1.0, n / OBS_STRONG)
            if best is None or score > best[0]:
                best = (score, band, p, n, eff)
        if best is None:
            continue
        score, band, p, n, eff = best
        conf = "confirmed" if n >= 3 and p >= 50 else ("observed" if n >= 3 else "model")
        mode = _mode_for(cfg_mode, p, band)
        until = _open_until(eng, qth, (rlat, rlon), band, snr_db, now) if p >= 50 else None
        recs.append(Rec(region=name, band=band, mode=mode, freq_khz=_freq_for(mode, band),
                        pct=p, eff=int(round(100 * eff)), obs=n, confidence=conf, until=until,
                        score=round(score, 3), lat=rlat, lon=rlon, dist_km=int(d),
                        band_mhz=dict(P.BANDS).get(band, 0.0),
                        path_muf=round(detail["muf"], 1), path_luf=round(detail["luf"], 1),
                        hops=max(1, math.ceil(d / 3500)),
                        cp_day=tuple(c.is_day for c in detail["points"]),
                        sources=dict(obs_src.get((name, band), {})),
                        absorption=detail.get("absorption", 0.0)))
    recs.sort(key=lambda r: -r.score)
    recs = recs[:5]

    # ── Sporadic-E ────────────────────────────────────────────────────────────
    es = {"active": False, "bands": [], "foes": None, "station": None, "spots": 0}
    iono = eng.nearest_ionosonde(qth[0], qth[1], now)
    if iono is not None and iono.foes:
        es["foes"], es["station"] = round(iono.foes, 1), iono.name
        if iono.foes >= 10:
            es["bands"] = ["6m", "10m"]
        elif iono.foes >= 7:
            es["bands"] = ["10m"]
    # Korte-sprong spots (500–2300 km) op 10m/6m. Een verse, lage foEs-meting
    # (< 4 MHz) is tegenbewijs: dan zijn meer spots nodig (F2-randgevallen).
    need = 6 if (es["foes"] is not None and es["foes"] < 4) else 4
    for band in ("10m", "6m"):
        n = sum(1 for b, _ in es_spots if b == band)
        if n >= need and band not in es["bands"]:
            es["bands"].append(band)
        es["spots"] += n
    es["active"] = bool(es["bands"])

    # ── Gebeurtenissen ────────────────────────────────────────────────────────
    events = []
    R, S, G = (int(_num(solar, f"noaa_{k}")) for k in ("R", "S", "G"))
    k = _num(solar, "k_index", 2)
    bz = _num(solar, "sw_bz", 0)
    jump = _num(solar, "sw_speed_jump", 0)
    if R >= 1:
        events.append(Event("red" if R >= 2 else "amber", "☢",
                            "adv.ev.radio_blackout" if here.is_day else "adv.ev.radio_blackout_night",
                            {"n": R}))
    if S >= 1:
        events.append(Event("red" if S >= 3 else "amber", "☣", "adv.ev.radiation", {"n": S}))
    if G >= 1 or k >= 5:
        g = max(G, int(k) - 4)
        events.append(Event("red" if g >= 3 else "amber", "🧲", "adv.ev.geomag",
                            {"n": g, "k": f"{k:.0f}"}))
    elif k >= k_alert:
        # Onder stormniveau maar boven de eigen drempel: onrust (geen oordeelverlaging)
        events.append(Event("info", "🧲", "adv.ev.geomag_unsettled", {"k": f"{k:.0f}"}))
    if jump >= 100:
        events.append(Event("amber", "💥", "adv.ev.shock", {"jump": int(jump)}))
    if bz <= -10:
        events.append(Event("amber", "🧭", "adv.ev.bz_south", {"bz": f"{bz:+.0f}"}))
    if es["active"]:
        events.append(Event("green", "⚡", "adv.ev.es_active",
                            {"bands": "/".join(es["bands"]),
                             "src": (f"foEs {es['foes']} MHz ({es['station']})" if es["foes"] and es["foes"] >= 7
                                     else f"{es['spots']} spots")}))
    # Gemeten D-laag-absorptie boven de eigen regio (NOAA D-RAP)
    if here.absorption >= 3:
        events.append(Event("red" if here.absorption >= 10 else "amber", "📉",
                            "adv.ev.absorption", {"haf": f"{here.absorption:.0f}"}))
    shower = active_meteor_shower(now.date())
    if shower:
        sid, peak, zhr = shower
        events.append(Event("info", "☄", "adv.ev.meteor",
                            {"sid": sid, "peak": f"{peak.day}-{peak.month}", "zhr": zhr}))
    g_tom = int(_num(solar, "noaa_G_tomorrow"))
    if g_tom >= 1:
        events.append(Event("info", "📅", "adv.ev.g_tomorrow", {"n": g_tom}))
    r_prob = int(_num(solar, "noaa_R_minor_prob_tomorrow"))
    if r_prob >= 40:
        events.append(Event("info", "📅", "adv.ev.flare_prob", {"p": r_prob}))

    # ── Tijdlijn: grayline + banden die opengaan/sluiten (komende 12 u) ──────
    timeline = []
    steps = [now + _dt.timedelta(minutes=i * STEP_MIN)
             for i in range(HORIZON_H * 60 // STEP_MIN + 1)]
    prev_day = P.is_day(qth[0], qth[1], steps[0])
    series = [eng.conditions(qth[0], qth[1], t, snr_db, now) for t in steps]
    for t, c in zip(steps[1:], series[1:]):
        if c.is_day != prev_day:
            timeline.append(TimelineItem(t, "🌅" if c.is_day else "🌇",
                                         "adv.tl.sunrise" if c.is_day else "adv.tl.sunset"))
            prev_day = c.is_day
    for band in ("80m", "40m", "30m", "20m", "17m", "15m", "12m", "10m"):
        was = series[0].band_pct.get(band, 0) >= 50
        for t, c in zip(steps[1:], series[1:]):
            is_open = c.band_pct.get(band, 0) >= 50
            if is_open != was:
                timeline.append(TimelineItem(t, "▲" if is_open else "▼",
                                             "adv.tl.band_opens" if is_open else "adv.tl.band_closes",
                                             {"band": band}))
                break
    timeline.sort(key=lambda it: it.time)
    timeline = timeline[:6]

    # ── Trends (komend uur) ──────────────────────────────────────────────────
    nxt = series[2] if len(series) > 2 else series[-1]
    trends = {}
    for band in _BAND_ORDER:
        d = nxt.band_pct.get(band, 0) - here.band_pct.get(band, 0)
        trends[band] = 1 if d >= 10 else (-1 if d <= -10 else 0)

    # ── Eindoordeel ───────────────────────────────────────────────────────────
    good = sum(1 for r in recs if r.pct >= 70 or r.obs >= 5)
    level = 3 if good >= 4 else 2 if good >= 2 else 1 if good >= 1 else 0
    level_raw = level
    if any(e.level == "red" for e in events):
        level = min(level, 1)
    elif any(e.level == "amber" for e in events):
        level = max(0, level - 1)

    return Advice(level=level, recs=recs, events=events, timeline=timeline,
                  trends=trends, es=es, muf=here.muf, source=here.source,
                  obs_total=sum(obs.values()), is_day=here.is_day,
                  good=good, level_raw=level_raw, obs_by_source=totals)


def fmt_hhmm(t: _dt.datetime | None) -> str:
    """Lokale tijd HH:MM (afgerond op 10 min) voor weergave."""
    if t is None:
        return ""
    loc = t.astimezone()
    m = int(math.floor(loc.minute / 10) * 10)
    return f"{loc.hour:02d}:{m:02d}"
