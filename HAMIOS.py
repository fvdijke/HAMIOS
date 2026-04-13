"""
HAMIOS v2.0
by Frank van Dijke

HAM radio propagation en DX tool met donkere GUI.
Features: solar/ionosfeer data (SFI, SSN, A/K-index),
          HF band betrouwbaarheid (MUF/LUF model, mode/vermogen/antenne),
          instellingen in INI-bestand.

Dependencies:
  pip install pillow

─────────────────────────────────────────────────────────────────────
Change Log (2.0)
─────────────────────────────────────────────────────────────────────

· 2026-04-13 09:15 CEST — Fix solarwind fetch: NOAA SWPC retourneert lijst van dicts
               ipv een dict; sleutelnamen zijn 'proton_speed' en 'bz_gsm'.
· 2026-04-13 09:08 CEST — Zoomen en pannen van de wereldkaart: muiswiel zoom
               (1×–8×, cursor-gecentreerd), click+drag pant, rechter muisklik
               reset zoom/pan (of wist groot-cirkel als zoom=1). Alle overlays
               (nacht, zon, maan, ITU, locator, aurora, CS, groot-cirkel) worden
               correct getekend op de virtuele VW×VH kaart en gecropped naar
               de viewport. Cache invalide bij zoom-wijziging.
· 2026-04-13 09:01 CEST — Callsign-prefix laag op wereldkaart: checkbox "CS" in
               kaart-header toont ~110 DXCC-entiteiten als gele stip + prefix-
               label (PA, G, DL, JA, W, VK enz.). Laag opgeslagen in INI.
· 2026-04-12 17:33 CEST — Tooltips verbeterd: _Tooltip krijgt 350ms vertraging voor
               tonen, schermrand-detectie (tooltip klapt om als hij buiten scherm
               valt), wraplength 380px voor lange tekst, 1px rand voor betere
               zichtbaarheid. Hover-tooltip op Bandopenings-schema (band, uur,
               kwaliteit, FT8-freq, modi). Hover-tooltip op Band Verloop
               (tijdstip + alle band%-waarden gesorteerd op kwaliteit).
· 2026-04-12 17:30 CEST — Alle panelen voorzien van 'bijgewerkt HH:MM' timestamp:
               Wereldkaart, HF Betrouwbaarheid, Band Verloop, Bandopenings-schema,
               DX Spots (tijd toegevoegd aan statusregel) en Advies.
               Solar/Ionosfeer had al een bijgewerkt-label.
· 2026-04-12 17:20 CEST — Solarwind toegevoegd aan Solar/Ionosfeer paneel:
               snelheid (km/s) en Bz (nT) opgehaald van NOAA SWPC. Bz negatief
               kleurt oranje (≤−10 nT) of rood (≤−20 nT). Tooltips voor beide
               velden toegevoegd.

"""

import configparser
import csv
import json
import math
import os
import sys
import tkinter as tk
try:
    import pystray
    _TRAY_OK = True
except ImportError:
    _TRAY_OK = False
from tkinter import font as tkfont
import threading
import datetime
import urllib.request
import xml.etree.ElementTree as ET
try:
    from PIL import Image, ImageDraw, ImageTk
    _PIL_OK = True
except ImportError:
    _PIL_OK = False

# ── Paden ──────────────────────────────────────────────────────────────────────
APP_DIR       = (os.path.dirname(sys.executable)
                 if getattr(sys, "frozen", False)
                 else os.path.dirname(os.path.abspath(__file__)))
SETTINGS_FILE = os.path.join(APP_DIR, "HAMIOS.ini")
HIST_FILE     = os.path.join(APP_DIR, "HAMIOS_history.csv")
# Equirectangulaire NASA-kaart (2048×1024 = exact 2:1 → coördinaten kloppen)
MAP_FILE      = os.path.join(APP_DIR, "worldmap_eq.jpg")
MAP_URL       = ("https://eoimages.gsfc.nasa.gov/images/imagerecords/"
                 "57000/57752/land_shallow_topo_2048.jpg")

# ── Thema ──────────────────────────────────────────────────────────────────────
BG_ROOT    = "#1A1C1F"
BG_PANEL   = "#22252A"
BG_SURFACE = "#2A2E35"
BG_HOVER   = "#32373F"
ACCENT     = "#C8A84B"
TEXT_H1    = "#F0E6C8"
TEXT_BODY  = "#B0B8C4"
TEXT_DIM   = "#606870"
BORDER     = "#383E47"

# ── Kaart kleuren ──────────────────────────────────────────────────────────────
MAP_OCEAN  = (27,  58,  92)    # donkerblauw
MAP_LAND   = (45,  96, 128)    # blauw-grijs
MAP_COAST  = (60, 122, 160)    # kustlijn
MAP_NIGHT  = (0,    8,  20, 150)  # nacht-overlay (RGBA)
MAP_GRID   = (30,  62,  95)    # graticule
MAP_SUN    = (255, 215,   0)   # zon
MAP_MOON   = (200, 200, 200)   # maan
MAP_QTH    = ( 80, 180, 255)   # eigen positie (helder blauw)

# ── ITU regio-grenzen (lat, lon) ──────────────────────────────────────────────
# Lijn B: westgrens R1 / oostgrens R2
_ITU_B = [
    (90, -10), (72, -10), (40, -50), (30, -20), (0, -20), (-90, -20),
]

# Lijn A (zuidelijk deel): Kaukasus → Turkije → Irak/Iran → Perzische Golf →
# Oman → Arabische Zee → 11N/55E → 11N/59E → Z-pool/59E
# Dit gedeelte scheidt het Arabisch schiereiland (R1) van Azië (R3)
_ITU_A = [
    (55, 55),                   # Aansluiting met Rusland-arm bij Oeral
    (47, 43), (45, 39),         # Kaukasus / Krasnodar
    (41, 40),                   # Turkse Zwarte Zeekust
    (39, 40), (38, 42),         # Oost-Turkije
    (37, 44),                   # Turkije/Irak/Iran driehoek
    (35, 46), (33, 47),         # Irak/Iran grens
    (31, 47), (30, 48),         # Zuid-Irak/Koeweit
    (29, 49), (27, 53),         # Perzische Golf / Qatar
    (25, 57), (23, 59),         # VAE → Noord-Oman
    (21, 60),                   # Oost-Oman
    (18, 60), (15, 58),         # Arabische Zee
    (13, 57), (11, 55),         # 11N/55E
    (11, 59),                   # langs 11N naar 59E
    (-90, 59),                  # Z-pool langs 59E
]

# Lijn A (noordelijk deel / Rusland-arm): Oeral → zuidgrens Rusland oost →
# Kazachstaan/Mongolië/China grens → Russisch Verre Oosten kust
# Rusland (boven deze lijn) is volledig R1
_ITU_A_RUS = [
    (90, 55),                   # N-pool langs 55E
    (55, 55),                   # 55N/Oeral (knoop met zuidelijk deel)
    (53, 60), (52, 73),         # Kazachstaan/W-Siberisch grens
    (51, 82), (52, 87),         # Altai-regio
    (52, 98), (50, 107),        # Tuva / Mongolisch grens
    (50, 118), (49, 127),       # Mongolisch / Mandsjoerij grens
    (47, 130), (46, 134),       # Amoer-rivier (Rusland/China)
    (43, 131),                  # Vladivostok
]

# Lijn C: Pacific grens R2 / R3
# N-pool/170W -> 60N/170W -> stap oost -> 60N/120W -> Z-pool/120W
_ITU_C = [
    (90, -170), (60, -170), (60, -120), (-90, -120),
]




def _ll_to_xy(lat: float, lon: float, W: int, H: int) -> tuple:
    """Breedtegraad/lengtegraad → canvas-coördinaten (equirectangular)."""
    x = int((lon + 180) / 360 * W)
    y = int((90 - lat) / 180 * H)
    return x, y


def _subsolar_point() -> tuple:
    """Geeft (lat, lon) terug van het punt direct onder de zon."""
    now = datetime.datetime.now(datetime.timezone.utc)
    doy = now.timetuple().tm_yday
    decl = -23.45 * math.cos(math.radians(360 / 365 * (doy + 10)))
    ut   = now.hour + now.minute / 60 + now.second / 3600
    lon  = -(ut - 12) * 15
    lon  = ((lon + 180) % 360) - 180
    return decl, lon


def _is_daytime_at_qth(lat: float, lon: float) -> bool:
    """True als de zon boven de horizon staat op de opgegeven QTH-positie."""
    sun_lat, sun_lon = _subsolar_point()
    lat_r     = math.radians(lat)
    sun_lat_r = math.radians(sun_lat)
    dlon_r    = math.radians(lon - sun_lon)
    cos_angle = (math.sin(lat_r)   * math.sin(sun_lat_r) +
                 math.cos(lat_r)   * math.cos(sun_lat_r) * math.cos(dlon_r))
    return cos_angle > 0


def _submoon_point() -> tuple:
    """Geeft (lat, lon) terug van het punt direct onder de maan (vereenvoudigd)."""
    now  = datetime.datetime.now(datetime.timezone.utc)
    J2K  = datetime.datetime(2000, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    d    = (now - J2K).total_seconds() / 86400
    L    = math.radians((218.316 + 13.176396 * d) % 360)
    M    = math.radians((134.963 + 13.064993 * d) % 360)
    F    = math.radians((93.272  + 13.229350 * d) % 360)
    lam  = L + math.radians(6.289 * math.sin(M))
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


def _night_mask(sun_lat: float, sun_lon: float, W: int, H: int) -> "Image":
    """Nachtmasker op volledige resolutie met zachte terminator-overgang.

    Optimalisatie: cos(lon − sun_lon) wordt één keer per kolom voorberekend,
    zodat de binnenste lus alleen een vermenigvuldiging en optelling bevat.
    De overgangszone (±SOFT graden) vervaagt van doorzichtig naar volledig nacht.
    """
    SOFT    = 0.06          # breedte zachte overgang in cos-eenheden (~3–4°)
    NR, NG, NB, NA = MAP_NIGHT

    slr     = math.radians(sun_lat)
    slon    = math.radians(sun_lon)
    sin_sun = math.sin(slr)
    cos_sun = math.cos(slr)

    # Voorberekende cos(lon − sun_lon) per kolom — trig verdwijnt uit de lus
    cos_dlon = [math.cos(math.radians(x * 360 / W - 180) - slon)
                for x in range(W)]

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px  = img.load()

    for y in range(H):
        lat_r      = math.radians(90 - y * 180 / H)
        k          = sin_sun * math.sin(lat_r)
        cos_lat_k  = cos_sun * math.cos(lat_r)

        for x in range(W):
            ca = k + cos_lat_k * cos_dlon[x]
            if ca < -SOFT:
                px[x, y] = (NR, NG, NB, NA)
            elif ca < SOFT:
                # Zachte overgang: lineair van 0 → NA
                alpha = int(NA * (SOFT - ca) / (2 * SOFT))
                px[x, y] = (NR, NG, NB, alpha)

    return img


def _graylijn_mask(sun_lat: float, sun_lon: float, W: int, H: int) -> "Image":
    """Goudgele band langs de terminator (graylijn, ~9° breed = ±~1000 km)."""
    HALF  = 0.155          # cos-eenheden breedte halve band (~9°)
    GR, GG, GB = 255, 200, 60   # amber/goud

    slr     = math.radians(sun_lat)
    slon    = math.radians(sun_lon)
    sin_sun = math.sin(slr)
    cos_sun = math.cos(slr)
    cos_dlon = [math.cos(math.radians(x * 360 / W - 180) - slon)
                for x in range(W)]

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px  = img.load()
    for y in range(H):
        lat_r     = math.radians(90 - y * 180 / H)
        k         = sin_sun * math.sin(lat_r)
        cos_lat_k = cos_sun * math.cos(lat_r)
        for x in range(W):
            ca = abs(k + cos_lat_k * cos_dlon[x])
            if ca < HALF:
                alpha = int(110 * (1 - ca / HALF))
                px[x, y] = (GR, GG, GB, alpha)
    return img


def _great_circle_pts(lat1, lon1, lat2, lon2, n=180):
    """Geef lijst van (lat, lon) langs de groot-cirkel van punt 1 naar punt 2."""
    lat1r, lon1r = math.radians(lat1), math.radians(lon1)
    lat2r, lon2r = math.radians(lat2), math.radians(lon2)
    d = math.acos(max(-1.0, min(1.0,
        math.sin(lat1r)*math.sin(lat2r) +
        math.cos(lat1r)*math.cos(lat2r)*math.cos(lon2r - lon1r))))
    if d < 1e-9:
        return [(lat1, lon1)]
    pts = []
    for i in range(n + 1):
        f = i / n
        A = math.sin((1 - f) * d) / math.sin(d)
        B = math.sin(f * d)       / math.sin(d)
        x = A*math.cos(lat1r)*math.cos(lon1r) + B*math.cos(lat2r)*math.cos(lon2r)
        y = A*math.cos(lat1r)*math.sin(lon1r) + B*math.cos(lat2r)*math.sin(lon2r)
        z = A*math.sin(lat1r)                  + B*math.sin(lat2r)
        pts.append((math.degrees(math.atan2(z, math.sqrt(x*x + y*y))),
                    math.degrees(math.atan2(y, x))))
    return pts


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2)**2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2)**2)
    return 2 * R * math.asin(math.sqrt(a))


def _bearing_deg(lat1, lon1, lat2, lon2) -> float:
    lat1r, lat2r = math.radians(lat1), math.radians(lat2)
    dlon = math.radians(lon2 - lon1)
    x = math.sin(dlon) * math.cos(lat2r)
    y = (math.cos(lat1r) * math.sin(lat2r) -
         math.sin(lat1r) * math.cos(lat2r) * math.cos(dlon))
    return (math.degrees(math.atan2(x, y)) + 360) % 360


# ── Font helper (gecached — elke combinatie wordt slechts één keer aangemaakt) ──
_FONT_CACHE: dict = {}

def _font(size=10, weight="normal"):
    key = (size, weight)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = tkfont.Font(family="Segoe UI", size=size, weight=weight)
    return _FONT_CACHE[key]

# ── Instellingen ───────────────────────────────────────────────────────────────
def _load_settings() -> dict:
    cfg = configparser.ConfigParser()
    cfg.read(SETTINGS_FILE, encoding="utf-8")
    hist_sel_raw = cfg.get("Graph", "selected_bands", fallback="")
    return {
        "lat":           cfg.getfloat  ("QTH",   "lat",            fallback=52.0),
        "lon":           cfg.getfloat  ("QTH",   "lon",            fallback=5.1),
        "refresh":       cfg.get       ("App",   "refresh",        fallback="1 min"),
        "mode":          cfg.get       ("App",   "mode",           fallback="SSB"),
        "power":         cfg.get       ("App",   "power",          fallback="100W"),
        "antenna":       cfg.get       ("App",   "antenna",        fallback="Isotropic 0dBi"),
        "dst":           cfg.getboolean("App",   "dst",            fallback=True),
        "show_tips":     cfg.getboolean("App",   "show_tips",      fallback=True),
        "show_sun":      cfg.getboolean("Map",   "show_sun",       fallback=True),
        "show_moon":     cfg.getboolean("Map",   "show_moon",      fallback=True),
        "show_locator":  cfg.getboolean("Map",   "show_locator",   fallback=False),
        "show_graylijn": cfg.getboolean("Map",   "show_graylijn",  fallback=True),
        "show_iaru":     cfg.getboolean("Map",   "show_iaru",      fallback=False),
        "show_cs":       cfg.getboolean("Map",   "show_cs",        fallback=False),
        "hist_range":    cfg.get       ("Graph", "hist_range",     fallback="Uren"),
        "hist_sel":      set(hist_sel_raw.split(",")) - {""} if hist_sel_raw else set(),
        "k_alert":       cfg.getint   ("Alerts","k_alert",        fallback=4),
    }

def _save_settings(lat: float, lon: float, refresh: str,
                   mode: str = "SSB", power: str = "100W",
                   antenna: str = "Isotropic 0dBi",
                   dst: bool = True, show_tips: bool = True,
                   show_sun: bool = True, show_moon: bool = True,
                   show_locator: bool = False,
                   show_graylijn: bool = True,
                   show_iaru: bool = False,
                   show_cs: bool = False,
                   hist_range: str = "Uren",
                   hist_sel: set = None,
                   k_alert: int = 4) -> None:
    cfg = configparser.ConfigParser()
    cfg["QTH"]   = {"lat": str(lat), "lon": str(lon)}
    cfg["App"]   = {"refresh": refresh, "mode": mode, "power": power,
                    "antenna": antenna, "dst": str(dst),
                    "show_tips": str(show_tips)}
    cfg["Map"]   = {"show_sun": str(show_sun), "show_moon": str(show_moon),
                    "show_locator": str(show_locator),
                    "show_graylijn": str(show_graylijn),
                    "show_iaru": str(show_iaru),
                    "show_cs": str(show_cs)}
    cfg["Graph"]  = {"hist_range": hist_range,
                     "selected_bands": ",".join(sorted(hist_sel)) if hist_sel else ""}
    cfg["Alerts"] = {"k_alert": str(k_alert)}
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)

# ── Solar data ophalen ─────────────────────────────────────────────────────────
SOLAR_URL    = "https://www.hamqsl.com/solarxml.php"
SW_SPEED_URL = "https://services.swpc.noaa.gov/products/summary/solar-wind-speed.json"
SW_MAG_URL   = "https://services.swpc.noaa.gov/products/summary/solar-wind-mag-field.json"

def _fetch_solar() -> dict:
    try:
        with urllib.request.urlopen(SOLAR_URL, timeout=8) as r:
            xml = r.read()
        root = ET.fromstring(xml)
        sd = root.find(".//solardata")
        if sd is None:
            return {}
        data = {
            "sfi":           sd.findtext("solarflux", "—").strip(),
            "ssn":           sd.findtext("sunspots",  "—").strip(),
            "a_index":       sd.findtext("aindex",    "—").strip(),
            "k_index":       sd.findtext("kindex",    "—").strip(),
            "xray":          sd.findtext("xray",      "—").strip(),
            "updated":       sd.findtext("updated",   "—").strip(),
            "muf":           sd.findtext("muf",       "—").strip(),
            "band_80m_day":  _band_cond(sd, "80m-40m",  "day"),
            "band_20m_day":  _band_cond(sd, "30m-20m",  "day"),
            "band_17m_day":  _band_cond(sd, "17m-15m",  "day"),
            "band_10m_day":  _band_cond(sd, "12m-10m",  "day"),
            "band_80m_ngt":  _band_cond(sd, "80m-40m",  "night"),
            "band_20m_ngt":  _band_cond(sd, "30m-20m",  "night"),
            "band_17m_ngt":  _band_cond(sd, "17m-15m",  "night"),
            "band_10m_ngt":  _band_cond(sd, "12m-10m",  "night"),
        }
        # ── Solarwind (NOAA SWPC) ──────────────────────────────────────────────
        # Beide endpoints retourneren een lijst van dicts: [{...}, ...]
        try:
            with urllib.request.urlopen(SW_SPEED_URL, timeout=6) as r:
                sw_speed_data = json.loads(r.read())
            entry = sw_speed_data[0] if isinstance(sw_speed_data, list) and sw_speed_data else {}
            spd = entry.get("proton_speed")
            data["sw_speed"] = f"{float(spd):.0f}" if spd is not None else "—"
        except Exception:
            data["sw_speed"] = "—"
        try:
            with urllib.request.urlopen(SW_MAG_URL, timeout=6) as r:
                sw_mag_data = json.loads(r.read())
            entry = sw_mag_data[0] if isinstance(sw_mag_data, list) and sw_mag_data else {}
            bz = entry.get("bz_gsm")
            data["sw_bz"] = f"{float(bz):.1f}" if bz is not None else "—"
        except Exception:
            data["sw_bz"] = "—"
        return data
    except Exception as e:
        return {"error": str(e)}


def _band_cond(sd, band: str, time_of_day: str) -> str:
    for item in sd.findall("calculatedconditions/band"):
        if item.get("name") == band and item.get("time") == time_of_day:
            return (item.text or "—").strip()
    return "—"


# ── Callsign-prefix locaties (DXCC-entiteiten) ───────────────────────────────
# (prefix, lat, lon)  — approximate centroid of entity
_CS_PREFIXES: list[tuple[str, float, float]] = [
    # Europa
    ("PA",  52.3,   5.3), ("G",   52.0,  -1.5), ("DL",  51.0,  10.0),
    ("F",   46.0,   2.0), ("I",   42.5,  12.5), ("EA",  40.0,  -4.0),
    ("SP",  52.0,  20.0), ("OZ",  56.0,  10.0), ("SM",  60.0,  15.0),
    ("OH",  64.0,  26.0), ("LA",  64.0,  11.0), ("OE",  47.5,  13.5),
    ("HB9", 47.0,   8.0), ("ON",  50.5,   4.5), ("LX",  49.7,   6.2),
    ("EI",  53.0,  -8.0), ("HA",  47.0,  19.0), ("OK",  49.8,  15.5),
    ("OM",  48.7,  19.5), ("S5",  46.1,  14.9), ("9A",  45.0,  16.0),
    ("YO",  45.5,  24.5), ("LZ",  42.7,  25.5), ("SV",  39.0,  22.0),
    ("YU",  44.0,  21.0), ("CT",  39.5,  -8.0), ("GI",  54.6,  -6.5),
    ("GM",  57.0,  -4.0), ("GW",  52.4,  -3.7), ("GJ",  49.2,  -2.1),
    ("IS0", 40.0,   9.0), ("IT9", 37.6,  14.0), ("5B",  35.0,  33.0),
    ("TK",  42.0,   9.0), ("3A",  43.7,   7.4), ("HV",  41.9,  12.4),
    # Oost-Europa / CIS
    ("UA",  56.0,  38.0), ("UR",  49.0,  32.0), ("EW",  53.5,  28.0),
    ("ES",  59.0,  25.0), ("YL",  57.0,  25.0), ("LY",  55.5,  24.0),
    ("ER",  47.0,  29.0), ("4L",  42.0,  44.0), ("EK",  40.2,  44.5),
    ("4J",  40.4,  47.8), ("UF",  42.0,  43.5),
    # Midden-Oosten
    ("TA",  39.0,  35.0), ("4X",  31.5,  35.0), ("OD",  33.9,  35.5),
    ("YK",  35.0,  38.3), ("JY",  31.0,  36.5), ("A4",  21.0,  57.0),
    ("A6",  23.5,  54.0), ("A9",  26.0,  50.5), ("9K",  29.3,  47.7),
    ("HZ",  24.0,  45.0), ("7Z",  24.0,  45.0), ("YI",  33.0,  44.0),
    # Azië
    ("UA9", 60.0, 100.0), ("UN",  48.0,  68.0), ("EX",  41.0,  74.0),
    ("EY",  38.5,  71.0), ("EZ",  40.0,  58.0), ("UK",  41.0,  64.0),
    ("EP",  32.0,  53.0), ("AP",  30.0,  70.0), ("VU",  22.0,  78.0),
    ("S2",  23.7,  90.4), ("9N",  28.0,  84.0), ("XV",  16.0, 108.0),
    ("XU",  12.6, 104.9), ("XW",  18.0, 103.0), ("HS",  15.0, 101.0),
    ("9M2",  4.0, 109.0), ("9V",   1.4, 103.8), ("YB",  -5.0, 120.0),
    ("DU",  12.0, 123.0), ("BV",  23.5, 121.0), ("BY",  35.0, 105.0),
    ("HL",  37.0, 127.5), ("JA",  36.0, 138.0), ("JT",  47.0, 106.0),
    ("VR",  22.3, 114.2), ("VS6", 22.3, 114.2),
    # Afrika
    ("ZS", -29.0,  25.0), ("ZE", -20.0,  30.0), ("9J",  -14.0,  28.0),
    ("5H",  -6.0,  35.0), ("5Z",   1.0,  38.0), ("ET",   9.0,  38.5),
    ("ST",  16.0,  32.0), ("SU",  27.0,  30.0), ("CN",  32.0,  -6.0),
    ("EA8", 28.0, -15.5), ("7X",  28.0,   3.0), ("3V",  33.8,   9.5),
    ("IG9", 35.6,  12.7), ("TU",   6.0,  -5.0), ("9G",   8.0,  -2.0),
    ("5N",  10.0,   8.0), ("TZ",  13.0,  -2.0), ("6W",  14.0, -14.0),
    # Noord-Amerika
    ("W",   38.0, -97.0), ("VE",  57.0, -96.0), ("XE",  23.0,-102.0),
    ("KP4", 18.2, -66.4), ("KH6", 20.7,-156.0), ("KL7", 64.0,-153.0),
    # Midden-Amerika / Caraïben
    ("TI",  10.0, -84.0), ("HP",   8.5, -80.0), ("YN",  12.8, -85.2),
    ("HR",  14.8, -86.8), ("TG",  15.5, -90.3), ("V3",  17.2, -88.7),
    ("HH",  19.0, -72.3), ("HI",  19.0, -70.2), ("6Y",  18.2, -77.5),
    ("VP9", 32.3, -64.7), ("ZF",  19.3, -81.4),
    # Zuid-Amerika
    ("PY", -10.0, -55.0), ("LU", -34.0, -64.0), ("CE", -30.0, -71.0),
    ("CP", -17.0, -65.0), ("OA", -10.0, -75.0), ("PZ",   4.0, -56.0),
    ("9Y",  10.5, -61.2), ("8R",   5.0, -59.0), ("HC",  -1.8, -78.2),
    # Oceanië
    ("VK",  -25.0, 134.0), ("ZL", -41.0, 174.0), ("KH0",  15.2, 145.7),
    ("YJ",  -17.7, 168.3), ("T2",  -8.5, 179.2), ("A3",  -21.2,-175.2),
    ("ZK",  -21.2,-175.2), ("E5",  -21.2,-159.8),
]

# ── HF/VHF/UHF band definities ────────────────────────────────────────────────
# (naam, startfrequentie MHz, hf=True voor ionosfeer-propagatiemodel)
_BANDS = [
    ("160m",    1.810, True),
    ("80m",     3.500, True),
    ("60m",    5.352, True),   # geregionaliseerde band (regionaal, licentie-afhankelijk)
    ("40m",     7.000, True),
    ("30m",    10.100, True),
    ("20m",    14.000, True),
    ("17m",    18.068, True),
    ("15m",    21.000, True),
    ("12m",    24.890, True),
    ("10m",    28.000, True),
    ("6m",     50.000, True),
    ("4m",     70.000, False),  # VHF — geen ionosfeer
    ("2m",    144.000, False),
    ("70cm",  430.000, False),
    ("23cm", 1240.000, False),
]

_BAND_FT8 = {
    "160m":  "1.840",
    "80m":   "3.573",
    "60m":  "5.357",
    "40m":   "7.074",
    "30m":   "10.136",
    "20m":   "14.074",
    "17m":   "18.100",
    "15m":   "21.074",
    "12m":   "24.915",
    "10m":   "28.074",
    "6m":    "50.313",
    "4m":    "70.154",
    "2m":    "144.174",
    "70cm":  "432.065",
    "23cm":  "—",
}

_BAND_MODES = {
    "160m":  "CW / FT8",
    "80m":   "CW / FT8",
    "60m":  "USB / FT8",
    "40m":   "SSB / FT8",
    "30m":   "CW / FT8",
    "20m":   "SSB / FT8",
    "17m":   "SSB / FT8",
    "15m":   "SSB / FT8",
    "12m":   "SSB / FT8",
    "10m":   "SSB / FT8",
    "6m":    "Es / FT8",
    "4m":    "Es / SSB",
    "2m":    "SSB / FM",
    "70cm":  "FM / DMR",
    "23cm":  "FM / ATV",
}

# N = Novice (NL Basis) toegestaan, F = alleen Full (HAREC) licentie
_BAND_LICENSE = {
    "160m": "NF", "80m":  "NF", "60m": "F",  "40m":  "NF",
    "30m":  "F",  "20m":  "NF", "17m":  "F",  "15m":  "F",
    "12m":  "F",  "10m":  "NF", "6m":   "F",  "4m":   "F",
    "2m":   "NF", "70cm": "NF", "23cm": "F",
}

_MODE_DB  = {"SSB": 0, "CW": 10, "FT8": 25, "AM": -6}
_POWER_DB = {"5W": -13, "10W": -10, "25W": -6, "50W": -3,
             "100W": 0, "500W": 7, "1kW": 10}
_ANT_DB = {
    "Isotropic 0dBi":   0,
    "Magnetische loop":  0,
    "Vertikaal":         0,
    "Groundplane":       0,
    "Inverted V":        1,
    "Dipole ~2dBi":      2,
    "EFHW":              2,
    "OCFD":              2,
    "J-pole":            2,
    "Long wire":         2,
    "Delta loop ~3dBi":  3,
    "Quad ~8dBi":        8,
    "Yagi ~7dBi":        7,
    "Beam ~10dBi":      10,
}

_REFRESH_OPTIONS = {
    "Uit": 0, "30s": 30, "1 min": 60, "5 min": 300,
    "10 min": 600, "30 min": 1800, "1 uur": 3600,
}

_HIST_KEEP_DAYS  = 90   # hoeveel dagen geschiedenis bewaren
_HIST_BAND_COLS  = [name for name, _, _ in _BANDS]
_HIST_SOLAR_COLS = ["sfi", "ssn", "k_index", "a_index"]
_HIST_COLS       = ["timestamp"] + _HIST_BAND_COLS + _HIST_SOLAR_COLS

# Kleur per band in de historiekgrafiek
_BAND_COLORS = {
    "160m": "#9575CD", "80m":  "#5C6BC0", "60m": "#42A5F5",
    "40m":  "#26C6DA", "30m":  "#26A69A", "20m":  "#66BB6A",
    "17m":  "#D4E157", "15m":  "#FFCA28", "12m":  "#FFA726",
    "10m":  "#EF5350", "6m":   "#EC407A",
}


def _calc_propagation(sfi: float, ssn: float, k_index: float,
                      qth_lat: float = 52.0,
                      snr_bonus_db: float = 0.0, daytime: bool = True) -> tuple:
    foF2 = 4.0 + (sfi - 70) * 0.065 + ssn * 0.012

    # Breedtegraad-correctie: F2-ionisatie neemt af naar de polen toe
    # Van 25° equatorwaarts: geen correctie; bij 90°: ~30% reductie
    lat_fac = 1.0 - max(0.0, (abs(qth_lat) - 25) / 65) * 0.30
    foF2 *= lat_fac

    if not daytime:
        foF2 *= 0.55
    foF2 = max(1.5, min(foF2, 16.0))
    muf = foF2 * 3.8

    base_luf = 3.5 + k_index * 0.8

    # Aurorale absorptie boven 45° breedtegraad: hogere K-index = meer LUF-stijging
    if abs(qth_lat) > 45:
        auroral = 1.0 + (abs(qth_lat) - 45) / 25 * k_index * 0.20
        base_luf *= auroral

    if not daytime:
        base_luf = max(0.5, base_luf * 0.4)
    luf = base_luf / (10 ** (snr_bonus_db / 20.0))
    luf = max(0.5, luf)

    band_pct = []
    for name, freq, is_hf in _BANDS:
        if not is_hf:
            # VHF/UHF: geen ionosfeer — toon als "—" (pct=-1 = speciaal geval)
            band_pct.append((name, freq, -1))
            continue
        if freq > muf:
            pct = 0
        elif freq < luf:
            pct = max(0, int(30 * (freq / luf)))
        else:
            ratio = (freq - luf) / max(0.1, muf - luf)
            peak  = 1.0 - abs(ratio - 0.55) * 1.4
            pct   = max(5, min(100, int(peak * 100)))
        band_pct.append((name, freq, pct))

    return band_pct, round(muf, 1), round(luf, 1)


# ── DX Cluster ────────────────────────────────────────────────────────────────
DX_CLUSTER_URL    = "https://dxwatch.com/dxsd1/s.php?s=0&r=30&cdxc=0"
DX_REFRESH_SECS   = 120   # elke 2 minuten

# HF-band grenzen in kHz voor spot-filtering
_BAND_RANGES_KHZ = [
    ("160m",  1800,  2000),
    ("80m",   3500,  4000),
    ("60m",   5351,  5367),
    ("40m",   7000,  7300),
    ("30m",  10100, 10150),
    ("20m",  14000, 14350),
    ("17m",  18068, 18168),
    ("15m",  21000, 21450),
    ("12m",  24890, 24990),
    ("10m",  28000, 29700),
    ("6m",   50000, 54000),
]

def _freq_khz_to_band(freq_khz: float) -> str:
    for name, lo, hi in _BAND_RANGES_KHZ:
        if lo <= freq_khz <= hi:
            return name
    return ""


def _qth_continent(lat: float, lon: float) -> str:
    """Bepaal continent op basis van lat/lon (eenvoudige bounding-box methode)."""
    if lat > 34 and -30 <= lon <= 50:
        return "EU"
    if lat > 10 and -170 <= lon <= -30:
        return "NA"
    if lat <= 10 and -82 <= lon <= -34:
        return "SA"
    if -38 <= lat <= 38 and -20 <= lon <= 55:
        return "AF"
    if lat >= -12 and 25 <= lon <= 180:
        return "AS"
    return "OC"


def _callsign_continent(cs: str) -> str:
    """Bepaal continent o.b.v. callsign prefix (2-teken lookup)."""
    cs = cs.upper().split("/")[0]
    p2 = cs[:2]
    _EU = {"OE","OH","OK","OM","ON","OZ","PA","PB","PC","PD","PE","PF","PG","PH",
           "SM","SP","SQ","SV","SX","HA","HB","LX","LY","LZ","LA","EA","EB","EC",
           "ER","ES","EU","EV","EW","UA","UB","UC","UD","UE","UF","UG","UR","US",
           "UT","UU","UV","UW","UX","UY","UZ","RA","RB","RC","RD","RE","RF","RG",
           "RH","RI","RJ","RK","RL","RM","RN","RO","RP","RQ","RR","RS","RT","RU",
           "RV","RW","RX","RY","RZ","DL","DK","DA","DB","DC","DD","DE","DF","DG",
           "DH","DI","DJ","DM","DN","DO","DP","DQ","DR","YL","YO","YT","YU","Z3",
           "ZA","TF","T7","T9","TA","TB","TC","TK","S5","HV","IS","IT","IU","3A",
           "EK","CS","CT","CU","F","G","I","M"}
    _NA = {"VE","VY","KH","KL","XE","XF","XG","YN","HH","HI","HP","HR","HT","HQ",
           "TI","V3","VP9"}
    _SA = {"CE","CP","CX","HC","HJ","HK","LU","LV","LW","PY","PP","PQ","PR","PS",
           "PT","PU","PV","PW","PX","YV","YW","ZP","ZY","ZZ"}
    _AS = {"JA","JD","HL","DS","DT","VU","VT","BY","BA","BD","BG","BH","BI","BJ",
           "UN","UO","UP","UQ","4J","4K","4L","AP","9N","9V","HS","XW","XZ","7Z",
           "HZ","A4","A6","A7","A9","OD","YI","YK","4X","4Z","EP","EQ"}
    _OC = {"VK","ZL","ZM","ZK","YB","YC","YD","YE","YF","YG","YH","DU","DV","DW",
           "DX","DY","DZ","V6","V7","T8"}
    if p2 in _EU or cs[0] in "FGIM": return "EU"
    if p2 in _NA or cs[0] in "KNW":  return "NA"
    if p2 in _SA:                     return "SA"
    if p2 in _AS or cs[0] == "J":    return "AS"
    if p2 in _OC:                     return "OC"
    return ""


def _fetch_dx_spots() -> list:
    """Haal DX spots op van dxwatch.com (JSON-feed).

    API-formaat s = {id: [dx_call, freq_khz, spotter, comment,
                           "HHMMz DD Mon", ?, ?, flag], ...}
    Geeft alleen HF-spots terug als lijst van dicts.
    """
    try:
        import html as _html
        req = urllib.request.Request(
            DX_CLUSTER_URL, headers={"User-Agent": "HAMIOS/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            raw = json.loads(r.read().decode("utf-8", errors="replace"))
        s_data = raw.get("s", {})
        rows = list(s_data.values()) if isinstance(s_data, dict) else list(s_data)
        spots = []
        for row in rows:
            if len(row) < 2:
                continue
            try:
                freq_khz = float(row[1])
            except (ValueError, TypeError):
                continue
            band = _freq_khz_to_band(freq_khz)
            if not band:
                continue
            # Tijd: "1928z 10 Apr" → "19:28"
            time_raw = str(row[4]).strip() if len(row) > 4 else ""
            digits   = time_raw[:4]
            time_str = f"{digits[:2]}:{digits[2:]}" if len(digits) == 4 and digits.isdigit() else "—"
            spotter  = str(row[2]).strip().upper() if len(row) > 2 else ""
            spots.append({
                "time":     time_str,
                "dx":       str(row[0]).strip().upper(),
                "freq_mhz": f"{freq_khz / 1000:.3f}",
                "band":     band,
                "spotter":  spotter,
                "comment":  _html.unescape(str(row[3]).strip()) if len(row) > 3 else "",
                "sp_cont":  _callsign_continent(spotter),
            })
        spots.reverse()   # nieuwste eerst (hoogste ID = recentst)
        return spots
    except Exception:
        return []


# ── Kaart downloaden ──────────────────────────────────────────────────────────
def _fetch_basemap(callback=None) -> None:
    """Download NASA equirectangulaire kaart naar MAP_FILE (achtergrond-thread)."""
    if os.path.exists(MAP_FILE):
        if callback:
            callback()
        return
    try:
        req = urllib.request.Request(MAP_URL,
              headers={"User-Agent": "HAMIOS/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
        with open(MAP_FILE, "wb") as f:
            f.write(data)
    except Exception:
        pass
    if callback:
        callback()


# ── Geschiedenis (CSV) ────────────────────────────────────────────────────────
def _load_history() -> list:
    """Laad CSV-geschiedenis; regels ouder dan _HIST_KEEP_DAYS worden overgeslagen.
    Geeft lijst van (ts, bp_dict, solar_dict) terug.
    """
    if not os.path.exists(HIST_FILE):
        return []
    cutoff = (datetime.datetime.now(datetime.timezone.utc)
              - datetime.timedelta(days=_HIST_KEEP_DAYS))
    rows = []
    try:
        with open(HIST_FILE, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    ts = datetime.datetime.fromisoformat(row["timestamp"])
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=datetime.timezone.utc)
                    if ts < cutoff:
                        continue
                    bp = {name: int(row.get(name, 0)) for name, _, _ in _BANDS}
                    sol = {k: float(row[k]) for k in _HIST_SOLAR_COLS if k in row}
                    rows.append((ts, bp, sol))
                except (ValueError, KeyError):
                    continue
    except Exception:
        pass
    return rows


def _append_history(ts: datetime.datetime, bp: dict, solar: dict) -> None:
    """Voeg één datapunt toe aan de CSV (schrijft header als het bestand nieuw is)."""
    write_header = not os.path.exists(HIST_FILE)
    try:
        with open(HIST_FILE, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if write_header:
                w.writerow(_HIST_COLS)
            band_vals  = [bp.get(name, 0) for name, _, _ in _BANDS]
            solar_vals = [solar.get(k, 0) for k in _HIST_SOLAR_COLS]
            w.writerow([ts.isoformat()] + band_vals + solar_vals)
    except Exception:
        pass


def _prune_history() -> None:
    """Herschrijf CSV zonder regels ouder dan _HIST_KEEP_DAYS (éénmalig bij start)."""
    rows = _load_history()
    try:
        with open(HIST_FILE, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(_HIST_COLS)
            for ts, bp, sol in rows:
                band_vals  = [bp.get(name, 0) for name, _, _ in _BANDS]
                solar_vals = [sol.get(k, 0) for k in _HIST_SOLAR_COLS]
                w.writerow([ts.isoformat()] + band_vals + solar_vals)
    except Exception:
        pass


# ── Tooltip ────────────────────────────────────────────────────────────────────
class _Tooltip:
    """Klein popup-venster dat verschijnt bij mouse-over.

    content kan zijn:
      str  → vrije tekst; eerste regel = vette titel, '─…' regels = scheidingslijn
      list → rijen:  (tekst, None)  = titelbalk (bold, volle breedte)
                     None           = scheidingslijn
                     (label, waarde) = uitgelijnde twee-koloms rij

    De tooltip verschijnt na _DELAY_MS ms vertraging en repositioneert zich
    automatisch als hij buiten het scherm zou vallen.
    """
    _DELAY_MS  = 350    # ms vertraging voor tonen
    _WRAP_PX   = 380    # maximale tekstbreedte in string-modus

    def __init__(self, widget: tk.Widget):
        self._widget  = widget
        self._win: tk.Toplevel | None = None
        self._after_id = None
        self._pending: tuple | None = None   # (x, y, content)

    def show(self, x: int, y: int, content):
        # Annuleer eventueel lopende vertraging
        if self._after_id is not None:
            try:
                self._widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        self._pending = (x, y, content)
        self._after_id = self._widget.after(self._DELAY_MS, self._do_show)

    def _do_show(self):
        self._after_id = None
        if self._pending is None:
            return
        x, y, content = self._pending
        self._pending = None

        if self._win:
            self._win.destroy()
        self._win = tw = tk.Toplevel(self._widget)
        tw.wm_overrideredirect(True)
        tw.configure(bg=BORDER)

        outer = tk.Frame(tw, bg=BG_SURFACE, padx=10, pady=8)
        outer.pack(padx=1, pady=1)   # 1px BORDER zichtbaar rondom

        def _f(sz=9, bold=False):
            return tkfont.Font(family="Segoe UI", size=sz,
                               weight="bold" if bold else "normal")

        if isinstance(content, list):
            for ri, item in enumerate(content):
                if item is None:
                    tk.Frame(outer, bg=BORDER, height=1).grid(
                        row=ri, column=0, columnspan=2,
                        sticky='ew', pady=(4, 4))
                elif item[1] is None:
                    tk.Label(outer, text=item[0], font=_f(9, bold=True),
                             bg=BG_SURFACE, fg=ACCENT).grid(
                        row=ri, column=0, columnspan=2, sticky='w', pady=(0, 2))
                else:
                    tk.Label(outer, text=item[0], font=_f(9),
                             bg=BG_SURFACE, fg=TEXT_DIM, anchor='w').grid(
                        row=ri, column=0, sticky='w', padx=(0, 16))
                    tk.Label(outer, text=item[1], font=_f(9, bold=True),
                             bg=BG_SURFACE, fg=TEXT_H1, anchor='w').grid(
                        row=ri, column=1, sticky='w')
        else:
            lines = content.split('\n')
            for ri, line in enumerate(lines):
                if line.startswith('─'):
                    tk.Frame(outer, bg=BORDER, height=1).grid(
                        row=ri, column=0, sticky='ew', pady=(3, 3))
                    outer.columnconfigure(0, weight=1)
                else:
                    is_title = ri == 0
                    tk.Label(outer, text=line, justify='left',
                             wraplength=self._WRAP_PX,
                             font=_f(9, bold=is_title),
                             bg=BG_SURFACE,
                             fg=ACCENT if is_title else TEXT_BODY,
                             anchor='w').grid(row=ri, column=0, sticky='w',
                                             pady=(0, 1))

        # Positie: eerst plaatsen, dan schermrand checken
        tw.update_idletasks()
        tw_w = tw.winfo_reqwidth()
        tw_h = tw.winfo_reqheight()
        scr_w = tw.winfo_screenwidth()
        scr_h = tw.winfo_screenheight()
        tip_x = x + 16
        tip_y = y + 12
        if tip_x + tw_w > scr_w - 8:
            tip_x = x - tw_w - 8
        if tip_y + tw_h > scr_h - 40:
            tip_y = y - tw_h - 8
        tw.wm_geometry(f"+{max(0, tip_x)}+{max(0, tip_y)}")

    def hide(self):
        # Annuleer vertraagd tonen
        if self._after_id is not None:
            try:
                self._widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        self._pending = None
        if self._win:
            self._win.destroy()
            self._win = None


# ── Hoofd-GUI ──────────────────────────────────────────────────────────────────
class HAMIOSApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("HAMIOS v2.0")
        self.root.configure(bg=BG_ROOT)
        self.root.minsize(800, 500)

        self._solar_data: dict = {}
        self._solar_after_id = None
        self._clock_after_id = None

        s = _load_settings()
        self._qth_lat = s["lat"]
        self._qth_lon = s["lon"]

        self._mode_var    = tk.StringVar(value=s["mode"])
        self._power_var   = tk.StringVar(value=s["power"])
        self._ant_var     = tk.StringVar(value=s["antenna"])
        self._day_var     = tk.BooleanVar(value=True)
        self._refresh_var = tk.StringVar(value=s["refresh"])
        self._last_band_pct = [(n, f, 0) for n, f, _ in _BANDS]
        _prune_history()
        self._history:    list = _load_history()
        self._hist_range_var = tk.StringVar(value=s["hist_range"])
        self._hist_sel: set  = s["hist_sel"]
        self._show_tips_var  = tk.BooleanVar(value=s["show_tips"])
        self._show_sun_var      = tk.BooleanVar(value=s["show_sun"])
        self._show_moon_var     = tk.BooleanVar(value=s["show_moon"])
        self._show_locator_var  = tk.BooleanVar(value=s["show_locator"])
        self._show_graylijn_var = tk.BooleanVar(value=s["show_graylijn"])
        self._show_iaru_var     = tk.BooleanVar(value=s["show_iaru"])
        self._show_cs_var       = tk.BooleanVar(value=s["show_cs"])
        self._gc_dest: tuple | None = None   # (lat, lon) groot-cirkel bestemming
        self._map_zoom:       float = 1.0   # zoom-factor (1.0 = volledig)
        self._map_cx:         float = 0.0   # viewport-middelpunt lon
        self._map_cy:         float = 0.0   # viewport-middelpunt lat
        self._map_crop_left:  int   = 0     # crop-offset voor inverse transform
        self._map_crop_top:   int   = 0
        self._map_drag_start: tuple | None = None   # (x, y, cx, cy) bij drag-start
        self._map_drag_moved: bool  = False
        self._dst_var           = tk.BooleanVar(value=s["dst"])
        self._next_refresh_at: datetime.datetime | None = None
        self._k_alert_var       = tk.IntVar(value=s["k_alert"])
        self._prev_band_open: dict = {}   # name → bool, voor band-opening detectie
        self._prev_k_above: bool   = False
        self._tray_icon             = None
        self._last_xflare: str      = ""   # voor dedup van X-flare tray-notificatie
        self._xflare_var            = tk.StringVar(value="")
        self._dx_all_spots: list    = []   # ruwe spots van dxwatch
        self._dx_after_id           = None
        self._dx_next_at: datetime.datetime | None = None
        self._dx_own_cont_var       = tk.BooleanVar(value=True)

        self._build_ui()
        # Herstel legenda-selectie visueel na opbouw UI
        if self._hist_sel:
            for bname, (lbl_d, lbl_n) in self._leg_widgets.items():
                color  = _BAND_COLORS.get(bname, TEXT_DIM)
                active = bname in self._hist_sel
                lbl_d.config(fg=color     if active else TEXT_DIM)
                lbl_n.config(fg=TEXT_BODY if active else TEXT_DIM,
                             font=_font(8, "bold") if active else _font(8))
        self._center_window(1400, 960)
        self._tick_clock()
        self._start_tray()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        threading.Thread(target=self._refresh_solar, daemon=True).start()
        threading.Thread(target=self._refresh_dx, daemon=True).start()
        threading.Thread(
            target=_fetch_basemap,
            kwargs={"callback": lambda: self.root.after(0, self._redraw_map)},
            daemon=True,
        ).start()

    # ── Klok ──────────────────────────────────────────────────────────────────
    def _tick_clock(self):
        utc   = datetime.datetime.now(datetime.timezone.utc)
        local = datetime.datetime.now()          # OS-lokale tijd (Windows beheert DST)
        zone  = "CEST" if self._dst_var.get() else "CET"
        self._local_var.set(f"{zone}  {local.strftime('%H:%M:%S')}")
        self._utc_var.set(f"UTC  {utc.strftime('%Y-%m-%d   %H:%M:%S')}")

        # Countdown tot volgende refresh
        if self._next_refresh_at:
            remaining = (self._next_refresh_at - utc).total_seconds()
            if remaining > 0:
                m, s = divmod(int(remaining), 60)
                self._countdown_var.set(f"↻ {m}:{s:02d}")
            else:
                self._countdown_var.set("↻ …")
        else:
            self._countdown_var.set("")

        # Countdown DX refresh
        if hasattr(self, "_dx_countdown_var") and self._dx_next_at:
            rem = (self._dx_next_at - utc).total_seconds()
            if rem > 0:
                m2, s2 = divmod(int(rem), 60)
                self._dx_countdown_var.set(f"↻ {m2}:{s2:02d}")
            else:
                self._dx_countdown_var.set("↻ …")

        self._clock_after_id = self.root.after(1000, self._tick_clock)

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.root, bg=BG_PANEL, height=42)
        hdr.pack(fill=tk.X)
        tk.Frame(hdr, bg=ACCENT, width=4).pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(hdr, text="📡  HAMIOS v2.0",
                 font=_font(13, "bold"), bg=BG_PANEL, fg=ACCENT,
                 pady=8).pack(side=tk.LEFT, padx=10)
        # Tijden rechts (UTC + lokaal)
        self._utc_var   = tk.StringVar()
        self._local_var = tk.StringVar()
        tk.Label(hdr, textvariable=self._utc_var,
                 font=_font(10), bg=BG_PANEL, fg=TEXT_DIM).pack(side=tk.RIGHT, padx=(0, 14))
        tk.Frame(hdr, bg=BORDER, width=1).pack(side=tk.RIGHT, fill=tk.Y, pady=8)
        tk.Label(hdr, textvariable=self._local_var,
                 font=_font(10, "bold"), bg=BG_PANEL, fg=TEXT_H1).pack(side=tk.RIGHT, padx=(0, 10))

        # Checkboxes
        tk.Checkbutton(hdr, text="Zomertijd", variable=self._dst_var,
                       command=self._save_cur_settings,
                       bg=BG_PANEL, fg=TEXT_DIM, selectcolor=BG_SURFACE,
                       activebackground=BG_PANEL, activeforeground=TEXT_BODY,
                       font=_font(9)).pack(side=tk.RIGHT, padx=(0, 8))
        tk.Checkbutton(hdr, text="Tooltips", variable=self._show_tips_var,
                       bg=BG_PANEL, fg=TEXT_DIM, selectcolor=BG_SURFACE,
                       activebackground=BG_PANEL, activeforeground=TEXT_BODY,
                       font=_font(9)).pack(side=tk.RIGHT, padx=(0, 4))

        # Interval keuze in header
        mb = tk.Menubutton(hdr, textvariable=self._refresh_var,
                           font=_font(9), bg=BG_SURFACE, fg=TEXT_H1,
                           relief=tk.FLAT, activebackground=BG_HOVER,
                           activeforeground=TEXT_H1, width=6,
                           anchor='w', padx=6, pady=3, cursor="hand2")
        interval_menu = tk.Menu(mb, tearoff=False, bg=BG_SURFACE, fg=TEXT_H1,
                                activebackground=ACCENT, activeforeground=BG_ROOT,
                                font=_font(9))
        for opt in _REFRESH_OPTIONS:
            interval_menu.add_command(label=opt,
                                      command=lambda v=opt: self._on_interval_change(v))
        mb["menu"] = interval_menu
        mb.pack(side=tk.RIGHT, padx=(0, 6))
        self._countdown_var = tk.StringVar(value="")
        tk.Label(hdr, textvariable=self._countdown_var,
                 font=_font(9), bg=BG_PANEL, fg=ACCENT).pack(side=tk.RIGHT, padx=(0, 6))
        tk.Label(hdr, text="Auto:", font=_font(9), bg=BG_PANEL,
                 fg=TEXT_DIM).pack(side=tk.RIGHT, padx=(0, 2))

        # Hoofd body — 3 kolommen: Kaart | Panelen | Solar  +  onderaan DX + Advies
        body = tk.Frame(self.root, bg=BG_ROOT)
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 4))

        # Bovenste rij: Kaart | Hist/Schema/Prop | Solar
        top_row = tk.Frame(body, bg=BG_ROOT)
        top_row.pack(fill=tk.BOTH, expand=True)

        # Solar rechts (eerst pack zodat hij niet wordt verdrongen)
        solar_col = tk.Frame(top_row, bg=BG_PANEL, width=210)
        solar_col.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        solar_col.pack_propagate(False)

        tk.Frame(solar_col, bg=ACCENT, height=2).pack(fill=tk.X)
        tk.Label(solar_col, text="☀  Solar / Ionosfeer",
                 font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT,
                 pady=8).pack(anchor='w', padx=10)

        self._solar_frame = tk.Frame(solar_col, bg=BG_PANEL)
        self._solar_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        _SOLAR_TIPS = {
            "sfi":     ("Solar Flux Index (SFI)",
                        "Maat voor de radioactiviteit van de zon op 10,7 cm.\n"
                        "< 80: laag  |  80–120: matig  |  > 150: hoog\n"
                        "Hogere SFI → betere ionisatie → hogere MUF."),
            "ssn":     ("Sunspot Number (SSN)",
                        "Aantal zonneplekken. Hoog SSN correleert met hogere SFI\n"
                        "en betere HF-propagatie, vooral op de hogere banden."),
            "a_index": ("A-index (dagelijks)",
                        "Dagelijkse maat voor geomagnetische activiteit (0–400).\n"
                        "< 10: rustig  |  10–29: onrustig  |  ≥ 30: storm\n"
                        "Hoge waarden verstoren de ionosfeer (verhoogde LUF)."),
            "k_index": ("K-index (3-uurs)",
                        "3-uurs geomagnetische activiteit (0–9).\n"
                        "0–2: rustig  |  3–4: onrustig  |  5+: storm\n"
                        "Direct effect op HF-absorptie en poolroutes."),
            "xray":    ("X-ray flux (GOES)",
                        "Röntgenflux van de zon. Klasse A/B/C/M/X.\n"
                        "X-flares kunnen de ionosfeer op dag-zijde plotseling\n"
                        "blokkeren (SWF – Short Wave Fadeout)."),
            "muf":     ("Maximum Usable Frequency (MUF)",
                        "Hoogste frequentie die op een bepaald pad weerkaatst\n"
                        "wordt door de F2-laag. Banden boven de MUF zijn dicht.\n"
                        "Berekend via foF2 × oblique factor 3,8."),
            "sw_speed": ("Solarwindsnelheid (km/s)",
                         "Snelheid van de solarwind gemeten door DSCOVR/ACE (NOAA).\n"
                         "< 400: rustig  |  400–600: verhoogd  |  > 600: stormachtig\n"
                         "Hogere snelheid kan geomagnetische activiteit verhogen."),
            "sw_bz":    ("Bz — interplanetair magneetveld (nT)",
                         "Noordwaartse (positief) of zuidwaartse (negatief) component\n"
                         "van het interplanetair magneetveld (IMF).\n"
                         "Bz < −10 nT: kans op geomagnetische storm neemt sterk toe.\n"
                         "Negatieve Bz koppelt aan het aardveld → verhoogde K-index."),
        }

        def _bind_tip(widget, key):
            tt = _Tooltip(widget)
            title, body = _SOLAR_TIPS.get(key, ("", ""))
            text = f"{title}\n{'─' * len(title)}\n{body}" if title else ""
            widget.bind("<Enter>", lambda e, t=tt, tx=text:
                        t.show(e.widget.winfo_rootx() + e.x,
                               e.widget.winfo_rooty() + e.y, tx)
                        if tx and self._show_tips_var.get() else None)
            widget.bind("<Leave>", lambda *_, t=tt: t.hide())

        self._solar_vars     = {}
        self._solar_val_lbls = {}   # key → Label widget (voor kleur-updates)
        for key, label in [
            ("sfi",      "Solar Flux (SFI)"),
            ("ssn",      "Sunspot Nr (SSN)"),
            ("a_index",  "A-index"),
            ("xray",     "X-ray"),
            ("muf",      "MUF (MHz)"),
            ("sw_speed", "Solarwind (km/s)"),
            ("sw_bz",    "Bz (nT)"),
            ("k_index",  "K-index"),
        ]:
            row = tk.Frame(self._solar_frame, bg=BG_PANEL)
            row.pack(fill=tk.X, pady=2)
            lbl = tk.Label(row, text=label + ":", font=_font(9), bg=BG_PANEL,
                           fg=TEXT_DIM, anchor='w', width=16, cursor="question_arrow")
            lbl.pack(side=tk.LEFT)
            _bind_tip(lbl, key)
            var = tk.StringVar(value="—")
            self._solar_vars[key] = var
            val_lbl = tk.Label(row, textvariable=var, font=_font(9, "bold"),
                               bg=BG_PANEL, fg=TEXT_H1, anchor='w', cursor="question_arrow")
            val_lbl.pack(side=tk.LEFT)
            _bind_tip(val_lbl, key)
            self._solar_val_lbls[key] = val_lbl

        # Melding K ≥ — onder alle solar-waarden
        alert_row = tk.Frame(self._solar_frame, bg=BG_PANEL)
        alert_row.pack(fill=tk.X, pady=(0, 2))
        tk.Label(alert_row, text="Melding K ≥", font=_font(8), bg=BG_PANEL,
                 fg=TEXT_DIM, anchor='w', width=16).pack(side=tk.LEFT)
        tk.Spinbox(alert_row, from_=1, to=9, width=2,
                   textvariable=self._k_alert_var,
                   command=self._save_cur_settings,
                   bg=BG_SURFACE, fg=TEXT_H1, buttonbackground=BG_SURFACE,
                   relief=tk.FLAT, font=_font(9)).pack(side=tk.LEFT, padx=(4, 0))

        tk.Frame(self._solar_frame, bg=BORDER, height=1).pack(fill=tk.X, pady=6)

        hdr_row = tk.Frame(self._solar_frame, bg=BG_PANEL)
        hdr_row.pack(fill=tk.X)
        for txt, w in [("Band", 6), ("Dag", 6), ("Nacht", 6)]:
            tk.Label(hdr_row, text=txt, font=_font(9, "bold"), bg=BG_PANEL,
                     fg=ACCENT, width=w, anchor='w').pack(side=tk.LEFT)

        self._band_cond_labels: dict = {}   # band → (day_lbl, ngt_lbl, is_hf)
        for name, _, is_hf in _BANDS:
            row = tk.Frame(self._solar_frame, bg=BG_PANEL)
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=name, font=_font(8), bg=BG_PANEL,
                     fg=TEXT_DIM, width=6, anchor='w').pack(side=tk.LEFT)
            day_lbl = tk.Label(row, text="—", font=_font(8, "bold"),
                               bg=BG_PANEL, fg=TEXT_DIM, width=6, anchor='w')
            day_lbl.pack(side=tk.LEFT)
            ngt_lbl = tk.Label(row, text="—", font=_font(8, "bold"),
                               bg=BG_PANEL, fg=TEXT_DIM, width=6, anchor='w')
            ngt_lbl.pack(side=tk.LEFT)
            self._band_cond_labels[name] = (day_lbl, ngt_lbl, is_hf)

        tk.Frame(self._solar_frame, bg=BORDER, height=1).pack(fill=tk.X, pady=6)
        self._updated_var = tk.StringVar(value="")
        tk.Label(self._solar_frame, textvariable=self._updated_var,
                 font=_font(8), bg=BG_PANEL, fg=TEXT_DIM,
                 wraplength=200, justify='left').pack(anchor='w')

        # X-flare waarschuwing
        self._xflare_lbl = tk.Label(self._solar_frame, textvariable=self._xflare_var,
                                    font=_font(8, "bold"), bg=BG_PANEL, fg="#FF7043",
                                    wraplength=200, justify='left')
        self._xflare_lbl.pack(anchor='w', pady=(4, 0))

        # ── Gecombineerde linker+midden zone ──────────────────────────────────
        combined = tk.Frame(top_row, bg=BG_ROOT)
        combined.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Sub-rij: Kaart+Hist+DX links (vaste breedte) | Prop+Schema rechts (expand)
        sub_row = tk.Frame(combined, bg=BG_ROOT)
        sub_row.pack(fill=tk.BOTH, expand=True)

        # Linkerkolom: Kaart bovenaan (2:1 op 480px → 240px hoog), dan Hist, dan DX
        left_sub = tk.Frame(sub_row, bg=BG_ROOT, width=480)
        left_sub.pack(side=tk.LEFT, fill=tk.Y)
        left_sub.pack_propagate(False)
        self._build_map_panel(left_sub)
        self._build_hist_panel(left_sub)
        self._build_dx_panel(left_sub)

        right_sub = tk.Frame(sub_row, bg=BG_ROOT)
        right_sub.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        self._build_prop_panel(right_sub)
        self._build_schedule_panel(right_sub)  # Schema onder HF Betrouwbaarheid

        # Advies: volledige breedte onderin body (over alle kolommen inclusief Solar)
        self._build_advice_panel(body)

    # ── Wereldkaart panel ─────────────────────────────────────────────────────
    def _build_map_panel(self, parent):
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.X, pady=(0, 0))
        tk.Frame(outer, bg=ACCENT, height=2).pack(fill=tk.X)

        map_hdr = tk.Frame(outer, bg=BG_PANEL)
        map_hdr.pack(fill=tk.X)
        tk.Label(map_hdr, text="🌍  Wereldkaart",
                 font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT,
                 pady=4).pack(side=tk.LEFT, padx=10)

        def _cb(text, var):
            def _on_toggle():
                self._save_cur_settings()
                self._draw_map()
            tk.Checkbutton(map_hdr, text=text, variable=var,
                           command=_on_toggle,
                           bg=BG_PANEL, fg=TEXT_DIM, selectcolor=BG_SURFACE,
                           activebackground=BG_PANEL, activeforeground=TEXT_BODY,
                           font=_font(9)).pack(side=tk.RIGHT, padx=(0, 8))

        _cb("Locator",  self._show_locator_var)
        _cb("CS",       self._show_cs_var)
        _cb("ITU",      self._show_iaru_var)
        _cb("Graylijn", self._show_graylijn_var)
        _cb("Maan",     self._show_moon_var)
        _cb("Zon",      self._show_sun_var)

        # QTH lat/lon invoer
        def _apply_qth(*_):
            try:
                lat = float(self._qth_lat_var.get().replace(",", "."))
                lon = float(self._qth_lon_var.get().replace(",", "."))
                lat = max(-90.0,  min(90.0,  lat))
                lon = max(-180.0, min(180.0, lon))
                self._qth_lat = lat
                self._qth_lon = lon
                self._qth_lat_var.set(f"{lat:.2f}")
                self._qth_lon_var.set(f"{lon:.2f}")
                self._save_cur_settings()
                self._draw_map()
                self._recalc_prop()
            except ValueError:
                pass

        self._qth_lat_var = tk.StringVar(value=f"{self._qth_lat:.2f}")
        self._qth_lon_var = tk.StringVar(value=f"{self._qth_lon:.2f}")

        qth_row = tk.Frame(map_hdr, bg=BG_PANEL)
        qth_row.pack(side=tk.LEFT, padx=(16, 0))
        tk.Label(qth_row, text="QTH  Lat:", font=_font(9), bg=BG_PANEL,
                 fg=TEXT_DIM).pack(side=tk.LEFT)
        lat_e = tk.Entry(qth_row, textvariable=self._qth_lat_var, width=7,
                         bg=BG_SURFACE, fg=TEXT_H1, insertbackground=TEXT_H1,
                         relief=tk.FLAT, font=_font(9))
        lat_e.pack(side=tk.LEFT, padx=(2, 6))
        lat_e.bind("<Return>",    _apply_qth)
        lat_e.bind("<FocusOut>",  _apply_qth)

        tk.Label(qth_row, text="Lon:", font=_font(9), bg=BG_PANEL,
                 fg=TEXT_DIM).pack(side=tk.LEFT)
        lon_e = tk.Entry(qth_row, textvariable=self._qth_lon_var, width=8,
                         bg=BG_SURFACE, fg=TEXT_H1, insertbackground=TEXT_H1,
                         relief=tk.FLAT, font=_font(9))
        lon_e.pack(side=tk.LEFT, padx=(2, 0))
        lon_e.bind("<Return>",   _apply_qth)
        lon_e.bind("<FocusOut>", _apply_qth)

        self._map_updated_var = tk.StringVar(value="")
        tk.Label(map_hdr, textvariable=self._map_updated_var,
                 font=_font(8), bg=BG_PANEL, fg=TEXT_DIM).pack(side=tk.LEFT, padx=(14, 0))

        self._map_canvas = tk.Canvas(outer, height=200, bg="#1B3A5C",
                                     bd=0, highlightthickness=0)
        self._map_canvas.pack(fill=tk.X)
        self._map_photo = None
        self._map_canvas.bind("<Configure>",      self._on_map_resize)
        self._map_canvas.bind("<Button-1>",       self._on_map_btn1_press)
        self._map_canvas.bind("<B1-Motion>",      self._on_map_drag)
        self._map_canvas.bind("<ButtonRelease-1>", self._on_map_btn1_release)
        self._map_canvas.bind("<Button-3>",       self._on_map_clear)
        self._map_canvas.bind("<MouseWheel>",     self._on_map_scroll)   # Windows
        self._map_canvas.bind("<Button-4>",       self._on_map_scroll)   # Linux
        self._map_canvas.bind("<Button-5>",       self._on_map_scroll)   # Linux

        # Info-label voor groot-cirkel (rechtsonder in canvas)
        self._gc_info_var = tk.StringVar(value="")
        tk.Label(outer, textvariable=self._gc_info_var,
                 font=_font(9), bg=BG_PANEL, fg=ACCENT,
                 anchor='w').pack(fill=tk.X, padx=10, pady=(0, 4))

    def _on_map_resize(self, event):
        """Handhaaf exacte 2:1 verhouding (equirectangulair)."""
        new_h = max(80, event.width // 2)
        if self._map_canvas.winfo_height() != new_h:
            self._map_canvas.config(height=new_h)
        self._draw_map()

    def _redraw_map(self):
        """Cache ongeldig maken en kaart opnieuw tekenen (na download)."""
        self._map_zoom = 1.0
        self._map_cx   = 0.0
        self._map_cy   = 0.0
        self._map_base_size = None
        self._draw_map()

    def _viewport_to_latlon(self, vx: int, vy: int) -> tuple[float, float]:
        """Viewport pixel → (lat, lon) met zoom/pan."""
        W  = self._map_canvas.winfo_width()  or 960
        H  = self._map_canvas.winfo_height() or 400
        VW = int(W * max(1.0, self._map_zoom))
        VH = int(H * max(1.0, self._map_zoom))
        wx  = self._map_crop_left + vx
        wy  = self._map_crop_top  + vy
        lon = wx / VW * 360 - 180
        lat = 90 - wy / VH * 180
        return lat, lon

    def _on_map_click(self, vx: int, vy: int):
        """Groot-cirkel bestemming instellen na een klik (geen drag)."""
        lat, lon = self._viewport_to_latlon(vx, vy)
        self._gc_dest = (lat, lon)
        dist = _haversine_km(self._qth_lat, self._qth_lon, lat, lon)
        hdg  = _bearing_deg(self._qth_lat, self._qth_lon, lat, lon)
        self._gc_info_var.set(
            f"→  {lat:+.1f}°, {lon:+.1f}°  |  Afstand: {dist:,.0f} km  "
            f"|  Richting: {hdg:.0f}°  (klik rechts om te wissen)")
        self._draw_map()

    def _on_map_btn1_press(self, event):
        """Muisknop-1 ingedrukt: start drag."""
        self._map_drag_start  = (event.x, event.y, self._map_cx, self._map_cy)
        self._map_drag_moved  = False

    def _on_map_drag(self, event):
        """Muis bewogen met knop-1: pan de kaart."""
        if self._map_drag_start is None:
            return
        sx, sy, ocx, ocy = self._map_drag_start
        dx = event.x - sx
        dy = event.y - sy
        if abs(dx) > 3 or abs(dy) > 3:
            self._map_drag_moved = True
        if not self._map_drag_moved:
            return
        W  = self._map_canvas.winfo_width()  or 960
        H  = self._map_canvas.winfo_height() or 400
        zoom      = max(1.0, self._map_zoom)
        d_lon     = -dx / W * (360 / zoom)
        d_lat     =  dy / H * (180 / zoom)
        half_lon  = 180 / zoom
        half_lat  =  90 / zoom
        self._map_cx = max(-180 + half_lon, min(180 - half_lon, ocx + d_lon))
        self._map_cy = max(-90  + half_lat, min( 90 - half_lat, ocy + d_lat))
        self._draw_map()

    def _on_map_btn1_release(self, event):
        """Muisknop-1 losgelaten: klik (geen drag) → groot-cirkel."""
        if not self._map_drag_moved:
            self._on_map_click(event.x, event.y)
        self._map_drag_start = None
        self._map_drag_moved = False

    def _on_map_scroll(self, event):
        """Muiswiel: zoom in/uit op cursorpositie."""
        if event.num == 4 or event.delta > 0:
            factor = 1.25
        else:
            factor = 1 / 1.25
        W    = self._map_canvas.winfo_width()  or 960
        H    = self._map_canvas.winfo_height() or 400
        old_zoom = max(1.0, self._map_zoom)
        new_zoom = max(1.0, min(8.0, old_zoom * factor))
        if new_zoom == old_zoom:
            return
        # Bepaal lat/lon onder cursor vóór zoom
        VW_old   = int(W * old_zoom)
        VH_old   = int(H * old_zoom)
        wx_old   = self._map_crop_left + event.x
        wy_old   = self._map_crop_top  + event.y
        lon_cur  = wx_old / VW_old * 360 - 180
        lat_cur  = 90 - wy_old / VH_old * 180
        # Nieuw center zodat cursor dezelfde lat/lon wijst
        VW_new   = int(W * new_zoom)
        VH_new   = int(H * new_zoom)
        new_cl   = (lon_cur + 180) / 360 * VW_new - event.x
        new_ct   = (90 - lat_cur)  / 180 * VH_new - event.y
        new_cx   = (new_cl + W / 2) / VW_new * 360 - 180
        new_cy   = 90 - (new_ct + H / 2) / VH_new * 180
        half_lon = 180 / new_zoom
        half_lat =  90 / new_zoom
        self._map_zoom = new_zoom
        self._map_cx   = max(-180 + half_lon, min(180 - half_lon, new_cx))
        self._map_cy   = max(-90  + half_lat, min( 90 - half_lat, new_cy))
        # Invalideer cache alleen als zoom-niveau de VW×VH dimensies wijzigt
        self._map_base_size = None
        self._draw_map()

    def _on_map_clear(self, *_):
        """Rechter muisklik: reset zoom/pan of verwijder groot-cirkel."""
        if self._map_zoom > 1.01:
            self._map_zoom = 1.0
            self._map_cx   = 0.0
            self._map_cy   = 0.0
            self._map_base_size = None
            self._draw_map()
        else:
            self._gc_dest = None
            self._gc_info_var.set("")
            self._draw_map()

    def _draw_map(self):
        c = self._map_canvas
        W = c.winfo_width()  or 960
        H = c.winfo_height() or 400
        # Virtuele wereld-afmetingen (groter bij zoom)
        zoom = max(1.0, self._map_zoom)
        VW   = int(W * zoom)
        VH   = int(H * zoom)

        if not _PIL_OK:
            c.delete("all")
            c.create_rectangle(0, 0, W, H, fill="#1B3A5C", outline="")
            c.create_text(W // 2, H // 2,
                          text="pip install pillow  voor kaartweergave",
                          fill=TEXT_DIM, font=("Segoe UI", 9))
            return

        # ── Basiskaart (gecached bij grootte-wijziging) ───────────────────────
        cache_key = (VW, VH)
        if getattr(self, "_map_base_size", None) != cache_key:
            if os.path.exists(MAP_FILE):
                # NASA equirectangulaire kaart (2048×1024 = exact 2:1)
                src = Image.open(MAP_FILE).convert("RGB").resize(
                    (VW, VH), Image.LANCZOS)
                # NASA-topo: oceaan = blauw dominant, land = groen/bruin/wit
                src.putdata([
                    MAP_OCEAN if (b > r + 15 and b > g) else MAP_LAND
                    for r, g, b in src.getdata()
                ])
            else:
                # Fallback: oceaan-achtergrond tijdens download
                src = Image.new("RGB", (VW, VH), MAP_OCEAN)
                ImageDraw.Draw(src).text(
                    (6, 4), "⬇ NASA-kaart wordt gedownload…", fill=MAP_GRID)

            # Graticule + graden-labels
            d   = ImageDraw.Draw(src)
            LBL = (180, 200, 220)   # contrasterende lichtblauwe kleur
            for lat in range(-60, 90, 30):
                gy = int((90 - lat) / 180 * VH)
                d.line([(0, gy), (VW, gy)], fill=MAP_GRID, width=1)
                d.text((3, gy + 2), f"{lat:+d}°", fill=LBL)
            for lon in range(-150, 180, 30):
                gx = int((lon + 180) / 360 * VW)
                d.line([(gx, 0), (gx, VH)], fill=MAP_GRID, width=1)
                d.text((gx + 2, 2), f"{lon:+d}°", fill=LBL)

            self._map_base_img  = src
            self._map_base_size = cache_key

        img  = self._map_base_img.copy()

        # ── Nacht overlay ────────────────────────────────────────────────────
        sun_lat, sun_lon = _subsolar_point()
        night = _night_mask(sun_lat, sun_lon, VW, VH)
        img   = img.convert("RGBA")
        img   = Image.alpha_composite(img, night)
        img   = img.convert("RGB")
        draw  = ImageDraw.Draw(img)

        # ── Zon ──────────────────────────────────────────────────────────────
        if self._show_sun_var.get():
            sx, sy = _ll_to_xy(sun_lat, sun_lon, VW, VH)
            draw.ellipse([(sx - 7, sy - 7), (sx + 7, sy + 7)],
                         fill=MAP_SUN, outline=(200, 160, 0), width=1)

        # ── Maan ─────────────────────────────────────────────────────────────
        if self._show_moon_var.get():
            moon_lat, moon_lon = _submoon_point()
            mx, my = _ll_to_xy(moon_lat, moon_lon, VW, VH)
            draw.ellipse([(mx - 5, my - 5), (mx + 5, my + 5)],
                         fill=MAP_MOON, outline=(150, 150, 150), width=1)

        # ── Graylijn ─────────────────────────────────────────────────────────
        if self._show_graylijn_var.get():
            gray = _graylijn_mask(sun_lat, sun_lon, VW, VH)
            img  = Image.alpha_composite(img.convert("RGBA"), gray).convert("RGB")
            draw = ImageDraw.Draw(img)

        # ── ITU regio-overlay (correcte R1/R2/R3 grenzen) ───────────────────
        if self._show_iaru_var.get():
            itu_img = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
            id_     = ImageDraw.Draw(itu_img)
            AF, AL  = 55, 220   # alpha vulling / grenslijn  (55≈22% dekking)
            # Kleuren conform referentieplaatje: R1=geel, R2=roze, R3=groen
            C_R1 = (210, 190,  70, AF)
            C_R2 = (210,  80,  80, AF)
            C_R3 = ( 60, 170,  80, AF)

            def _px(pts):
                return [_ll_to_xy(la, lo, VW, VH) for la, lo in pts]

            # ── Gevulde regio-polygonen ───────────────────────────────────
            # R3 Pacific west (kaartrand -180 tot Lijn-C)
            id_.polygon(_px([
                (90,-180),(90,-170),(60,-170),(60,-120),(-90,-120),(-90,-180)
            ]), fill=C_R3)

            # R2 Amerika: Lijn-C → Lijn-B → Z-pool
            id_.polygon(_px([
                (90,-170),(90,-10),(72,-10),(40,-50),(30,-20),(0,-20),
                (-90,-20),(-90,-120),(60,-120),(60,-170)
            ]), fill=C_R2)

            # R1 hoofd: Lijn-B → Z-pool → Lijn-A omgekeerd → Oeral-knoop
            # (Europa, Afrika, Arabisch schiereiland, Turkije)
            id_.polygon(_px([
                (90,-10),(72,-10),(40,-50),(30,-20),(0,-20),(-90,-20),
                (-90,59),
                (11,59),(11,55),
                (13,57),(15,58),(18,60),
                (21,60),(23,59),(25,57),
                (27,53),(29,49),
                (30,48),(31,47),(33,47),(35,46),
                (37,44),(38,42),(39,40),
                (41,40),(45,39),(47,43),
                (55,55),(90,55)
            ]), fill=C_R1)

            # R3 oost (Azië-Pacific): Lijn-A zuidelijk → 180°E
            id_.polygon(_px([
                (55,55),(47,43),
                (45,39),(41,40),
                (39,40),(38,42),(37,44),
                (35,46),(33,47),(31,47),(30,48),
                (29,49),(27,53),(25,57),
                (23,59),(21,60),(18,60),
                (15,58),(13,57),(11,55),
                (11,59),
                (-90,59),(-90,180),(90,180),(90,55)
            ]), fill=C_R3)

            # R1 Rusland-patch: heel Rusland (boven Kazachstaan/Mongolië/China
            # grens ~50-55N) is R1 — overtekent R3 oost voor Siberisch gebied
            id_.polygon(_px([
                (55, 55),
                (53, 60),(52, 73),(51, 82),(52, 87),
                (52, 98),(50,107),(50,118),(49,127),
                (47,130),(46,134),(43,131),
                (45,136),(50,141),(55,141),
                (59,151),(63,163),(67,178),
                (90,180),(90,55),
            ]), fill=C_R1)

            # ── Grenslijnen ───────────────────────────────────────────────
            for pts, clr, w in [
                (_ITU_B,     (255, 200,  80, AL), 2),   # R1/R2
                (_ITU_A,     ( 80, 220, 100, AL), 2),   # R1/R3 Arabisch deel
                (_ITU_A_RUS, ( 80, 220, 100, AL), 2),   # R1/R3 Rusland-arm
                (_ITU_C,     (160, 220, 160, AL), 1),   # R2/R3 Pacific
            ]:
                px = _px(pts)
                for j in range(len(px) - 1):
                    id_.line([px[j], px[j+1]], fill=clr, width=w)

            # ── Labels (volledige naam) ────────────────────────────────────
            for txt, la, lo in [
                ("Regio 2", 35, -100),
                ("Regio 1", 35,   15),
                ("Regio 3", 35,  115),
            ]:
                x_l, y_l = _ll_to_xy(la, lo, VW, VH)
                if 0 <= x_l < VW and 0 <= y_l < VH:
                    id_.text((x_l - 22, y_l - 5), txt, fill=(230,230,230,210))

            img  = Image.alpha_composite(img.convert("RGBA"), itu_img).convert("RGB")
            draw = ImageDraw.Draw(img)

        # ── Maidenhead locatorraster ─────────────────────────────────────────
        if self._show_locator_var.get():
            LOC_GRID = (100, 160, 220, 180)   # lichtblauw, semi-transparant
            LOC_LBL  = (160, 210, 255, 200)
            loc_img  = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
            ld       = ImageDraw.Draw(loc_img)
            # Grote velden: 20° breed × 10° hoog
            for fi in range(19):          # 18 velden in lon-richting
                gx = int(fi * 20 / 360 * VW)
                ld.line([(gx, 0), (gx, VH)], fill=LOC_GRID, width=1)
            for fi in range(19):          # 18 velden in lat-richting
                gy = int(fi * 10 / 180 * VH)
                ld.line([(0, gy), (VW, gy)], fill=LOC_GRID, width=1)
            # Labels (2-letter locator) in het midden van elk groot veld
            for lon_i in range(18):
                for lat_i in range(18):
                    lon_c = -180 + lon_i * 20 + 10
                    lat_c =  -90 + lat_i * 10 +  5
                    lbl   = chr(ord('A') + lon_i) + chr(ord('A') + lat_i)
                    cx_l, cy_l = _ll_to_xy(lat_c, lon_c, VW, VH)
                    ld.text((cx_l - 8, cy_l - 5), lbl, fill=LOC_LBL)
            img = Image.alpha_composite(img.convert("RGBA"), loc_img).convert("RGB")
            draw = ImageDraw.Draw(img)

        # ── Auroraal absorptie-ovaal (K≥4) ───────────────────────────────────
        try:
            k_val = float(self._solar_data.get("k_index", "0").replace("—", "0"))
        except (ValueError, TypeError, AttributeError):
            k_val = 0.0
        if k_val >= 4:
            # Equatorwaartse grens van het auroraal ovaal ≈ 75 − K×2.5 graden
            aurora_lat = max(50.0, 75.0 - k_val * 2.5)
            aurora_img = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
            ad = ImageDraw.Draw(aurora_img)
            # Trek een horizontale band als proxy voor het ovaal (beide hemisferen)
            thickness = max(4, int(k_val * 1.5))
            alpha = min(200, int(80 + k_val * 15))
            for sign in (1, -1):
                lat_c = sign * aurora_lat
                _, y_c = _ll_to_xy(lat_c, 0, VW, VH)
                y_top = max(0, y_c - thickness)
                y_bot = min(VH, y_c + thickness)
                # Rood/oranje ovaal
                ad.rectangle([(0, y_top), (VW, y_bot)],
                              fill=(220, 80, 20, alpha))
            img = Image.alpha_composite(img.convert("RGBA"), aurora_img).convert("RGB")
            draw = ImageDraw.Draw(img)

        # ── Groot-cirkel pad ─────────────────────────────────────────────────
        if self._gc_dest:
            dlat, dlon = self._gc_dest
            pts = _great_circle_pts(self._qth_lat, self._qth_lon, dlat, dlon)
            gc_img = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
            gd     = ImageDraw.Draw(gc_img)
            xy     = [_ll_to_xy(la, lo, VW, VH) for la, lo in pts]
            # Splits op anti-meridian (|Δx| > VW/2) om wraparound te vermijden
            seg_start = 0
            for i in range(1, len(xy)):
                if abs(xy[i][0] - xy[i-1][0]) > VW // 2:
                    if i - seg_start > 1:
                        gd.line(xy[seg_start:i], fill=(255, 220, 50, 220), width=2)
                    seg_start = i
            if len(xy) - seg_start > 1:
                gd.line(xy[seg_start:], fill=(255, 220, 50, 220), width=2)
            # Bestemmingsmarkering
            dx, dy = _ll_to_xy(dlat, dlon, VW, VH)
            gd.ellipse([(dx-5, dy-5), (dx+5, dy+5)], fill=(255, 220, 50, 220))
            img  = Image.alpha_composite(img.convert("RGBA"), gc_img).convert("RGB")
            draw = ImageDraw.Draw(img)

        # ── Callsign-prefix labels ────────────────────────────────────────────
        if self._show_cs_var.get() and _PIL_OK:
            CS_DOT  = (255, 230, 120, 230)   # geel, opaque
            CS_TXT  = (255, 230, 120, 210)
            cs_img  = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
            cd      = ImageDraw.Draw(cs_img)
            for prefix, lat, lon in _CS_PREFIXES:
                px, py = _ll_to_xy(lat, lon, VW, VH)
                # Klein stipje op de positie
                cd.ellipse([(px - 2, py - 2), (px + 2, py + 2)], fill=CS_DOT)
                # Prefix-tekst net rechts/boven het stipje
                cd.text((px + 4, py - 6), prefix, fill=CS_TXT)
            img  = Image.alpha_composite(img.convert("RGBA"), cs_img).convert("RGB")
            draw = ImageDraw.Draw(img)

        # ── QTH marker (alleen kruisje) ───────────────────────────────────────
        qx, qy = _ll_to_xy(self._qth_lat, self._qth_lon, VW, VH)
        draw.line([(qx - 10, qy), (qx + 10, qy)], fill=MAP_QTH, width=2)
        draw.line([(qx, qy - 10), (qx, qy + 10)], fill=MAP_QTH, width=2)

        # ── Crop naar viewport (bij zoom > 1) ────────────────────────────────
        if zoom > 1.0:
            world_cx = int((self._map_cx + 180) / 360 * VW)
            world_cy = int((90 - self._map_cy) / 180 * VH)
            crop_l   = max(0, min(VW - W, world_cx - W // 2))
            crop_t   = max(0, min(VH - H, world_cy - H // 2))
            img      = img.crop((crop_l, crop_t, crop_l + W, crop_t + H))
        else:
            crop_l, crop_t = 0, 0
        self._map_crop_left = crop_l
        self._map_crop_top  = crop_t

        # ── Tonen ────────────────────────────────────────────────────────────
        self._map_photo = ImageTk.PhotoImage(img)
        c.delete("all")
        c.create_image(0, 0, anchor='nw', image=self._map_photo)
        if hasattr(self, "_map_updated_var"):
            self._map_updated_var.set(datetime.datetime.now().strftime("%H:%M"))

    # ── HF Propagatie panel ───────────────────────────────────────────────────
    def _build_prop_panel(self, parent):
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.X, pady=(6, 0))

        tk.Frame(outer, bg=ACCENT, height=2).pack(fill=tk.X)
        prop_hdr = tk.Frame(outer, bg=BG_PANEL)
        prop_hdr.pack(fill=tk.X, padx=10, pady=(6, 0))
        tk.Label(prop_hdr, text="📶  HF Band Betrouwbaarheid",
                 font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT).pack(side=tk.LEFT)
        self._prop_updated_var = tk.StringVar(value="")
        tk.Label(prop_hdr, textvariable=self._prop_updated_var,
                 font=_font(8), bg=BG_PANEL, fg=TEXT_DIM).pack(side=tk.RIGHT)

        ctrl = tk.Frame(outer, bg=BG_PANEL)
        ctrl.pack(fill=tk.X, padx=10, pady=(0, 4))

        def _menubutton(par, var, options, label, width=12):
            tk.Label(par, text=label, font=_font(9), bg=BG_PANEL,
                     fg=TEXT_DIM).pack(side=tk.LEFT, padx=(0, 2))
            mb2 = tk.Menubutton(par, textvariable=var, font=_font(9),
                                bg=BG_SURFACE, fg=TEXT_H1, relief=tk.FLAT,
                                activebackground=BG_HOVER, activeforeground=TEXT_H1,
                                width=width, anchor='w', padx=6, pady=3, cursor="hand2")
            menu2 = tk.Menu(mb2, tearoff=False, bg=BG_SURFACE, fg=TEXT_H1,
                            activebackground=ACCENT, activeforeground=BG_ROOT,
                            font=_font(9))
            for opt in options:
                menu2.add_command(label=opt,
                                  command=lambda v=opt: (var.set(v), self._recalc_prop()))
            mb2["menu"] = menu2
            mb2.pack(side=tk.LEFT, padx=(0, 12))

        _menubutton(ctrl, self._mode_var,  list(_MODE_DB.keys()),  "Mode:",     width=5)
        _menubutton(ctrl, self._power_var, list(_POWER_DB.keys()), "Vermogen:", width=5)
        _menubutton(ctrl, self._ant_var,   list(_ANT_DB.keys()),   "Antenne:",  width=18)

        tk.Checkbutton(ctrl, text="Dag (auto)", variable=self._day_var,
                       command=self._recalc_prop,
                       bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                       activebackground=BG_PANEL, font=_font(9)).pack(side=tk.LEFT, padx=(4, 0))

        info = tk.Frame(outer, bg=BG_PANEL)
        info.pack(fill=tk.X, padx=10, pady=(0, 4))
        self._muf_var = tk.StringVar(value="MUF: —")
        self._luf_var = tk.StringVar(value="LUF: —")
        self._db_var  = tk.StringVar(value="0 dB")
        for var, fg in [(self._muf_var, TEXT_H1), (self._luf_var, TEXT_H1),
                        (self._db_var, ACCENT)]:
            tk.Label(info, textvariable=var, font=_font(9, "bold"),
                     bg=BG_PANEL, fg=fg).pack(side=tk.LEFT, padx=(0, 18))

        BAR_H    = 16
        BAR_PAD  = 2
        HDR_H    = 16
        canvas_h = HDR_H + len(_BANDS) * (BAR_H + BAR_PAD) + BAR_PAD + 2
        self._prop_canvas = tk.Canvas(outer, height=canvas_h, bg=BG_PANEL,
                                      bd=0, highlightthickness=0)
        self._prop_canvas.pack(fill=tk.X, padx=10, pady=(0, 8))
        self._prop_canvas.bind("<Configure>",
                               lambda *_: self._draw_prop_bars(self._last_band_pct))
        self._bar_rows: list = []   # (y_top, y_bot, tooltip_text)
        self._tooltip  = _Tooltip(self._prop_canvas)
        self._prop_canvas.bind("<Motion>", self._on_bar_motion)
        self._prop_canvas.bind("<Leave>",  lambda *_: self._tooltip.hide())

    def _draw_prop_bars(self, band_pct):
        self._last_band_pct = band_pct
        c = self._prop_canvas
        c.delete("all")
        self._bar_rows = []

        W       = c.winfo_width() or 700
        BAR_H   = 16
        BAR_PAD = 2
        HDR_H   = 16
        LABEL_W = 40
        LIC_W   = 20
        PCT_W   = 36
        MODES_W = 84
        FREQ_W  = 60
        FT8_W   = 62
        BAR_X   = LABEL_W + LIC_W + 4
        BAR_MAX = max(40, W - BAR_X - PCT_W - FREQ_W - MODES_W - FT8_W - 10)

        # Kolomhoofden
        def _hdr(x, w, txt):
            c.create_text(x + w // 2, HDR_H // 2, text=txt,
                          font=("Segoe UI", 8, "bold"), fill=ACCENT, anchor='center')

        _hdr(BAR_X,                                    BAR_MAX, "")
        _hdr(BAR_X + BAR_MAX,                          PCT_W,   "%")
        _hdr(BAR_X + BAR_MAX + PCT_W,                  FREQ_W,  "Start")
        _hdr(BAR_X + BAR_MAX + PCT_W + FREQ_W,         MODES_W, "Mode")
        _hdr(BAR_X + BAR_MAX + PCT_W + FREQ_W + MODES_W, FT8_W, "FT8")

        for i, entry in enumerate(band_pct):
            name, freq, pct = entry[0], entry[1], entry[2]
            y = HDR_H + BAR_PAD + i * (BAR_H + BAR_PAD)

            # Bandnaam
            c.create_text(LABEL_W - 2, y + BAR_H // 2,
                          text=name, font=("Segoe UI", 9),
                          fill=TEXT_DIM, anchor='e')

            # Licentie (N/F)
            lic = _BAND_LICENSE.get(name, "")
            c.create_text(LABEL_W + LIC_W - 2, y + BAR_H // 2,
                          text=lic, font=("Segoe UI", 7),
                          fill=TEXT_DIM, anchor='e')

            freq_str = f"{freq:.3f} MHz" if freq < 1000 else f"{freq/1000:.3f} GHz"

            if pct == -1:
                # VHF/UHF: geen HF-propagatiemodel
                c.create_rectangle(BAR_X, y, BAR_X + BAR_MAX, y + BAR_H,
                                   fill=BG_SURFACE, outline=BORDER, width=1)
                c.create_text(BAR_X + BAR_MAX // 2, y + BAR_H // 2,
                              text="LOS / Tropo", font=("Segoe UI", 8),
                              fill=TEXT_DIM, anchor='center')
                tip = [
                    (f"{name}  ·  {freq_str}", None),
                    None,
                    ("Type:",        "VHF / UHF"),
                    ("Propagatie:",  "Lijn-van-zicht / Troposfeer"),
                    ("Modi:",        _BAND_MODES.get(name, "—")),
                    ("FT8:",         _BAND_FT8.get(name, "—") + " MHz"),
                ]
            elif pct == 0:
                # Band volledig gesloten — zelfde stijl als LOS/Tropo
                c.create_rectangle(BAR_X, y, BAR_X + BAR_MAX, y + BAR_H,
                                   fill=BG_SURFACE, outline=BORDER, width=1)
                c.create_text(BAR_X + BAR_MAX // 2, y + BAR_H // 2,
                              text="Gesloten", font=("Segoe UI", 8),
                              fill=TEXT_DIM, anchor='center')
                c.create_text(BAR_X + BAR_MAX + PCT_W // 2, y + BAR_H // 2,
                              text="0%", font=("Segoe UI", 9, "bold"),
                              fill=TEXT_DIM, anchor='center')
                tip = [
                    (f"{name}  ·  {freq_str}", None),
                    None,
                    ("Status:",  "Gesloten"),
                    ("Reden:",   "Boven MUF of onder LUF"),
                    ("Modi:",    _BAND_MODES.get(name, "—")),
                    ("FT8:",     _BAND_FT8.get(name, "—") + " MHz"),
                ]
            else:
                # HF: kleurenbalk
                c.create_rectangle(BAR_X, y, BAR_X + BAR_MAX, y + BAR_H,
                                   fill=BG_SURFACE, outline=BORDER, width=1)
                color = "#4CAF50" if pct >= 60 else ("#FFC107" if pct >= 30 else "#F44336")
                cond  = "Goed" if pct >= 60 else ("Redelijk" if pct >= 30 else "Arm")
                fill_w = int(BAR_MAX * pct / 100)
                if fill_w > 2:
                    c.create_rectangle(BAR_X + 1, y + 1, BAR_X + fill_w, y + BAR_H - 1,
                                       fill=color, outline="")
                c.create_text(BAR_X + BAR_MAX + PCT_W // 2, y + BAR_H // 2,
                              text=f"{pct}%", font=("Segoe UI", 9, "bold"),
                              fill=TEXT_H1, anchor='center')
                tip = [
                    (f"{name}  ·  {freq_str}", None),
                    None,
                    ("Betrouwbaarheid:", f"{pct}%  –  {cond}"),
                    ("Modi:",            _BAND_MODES.get(name, "—")),
                    ("FT8:",             _BAND_FT8.get(name, "—") + " MHz"),
                ]

            # Frequentie (kort, rechts van balk)
            c.create_text(BAR_X + BAR_MAX + PCT_W + FREQ_W // 2, y + BAR_H // 2,
                          text=freq_str.split()[0], font=("Segoe UI", 8),
                          fill=TEXT_DIM, anchor='center')

            # Modi
            c.create_text(BAR_X + BAR_MAX + PCT_W + FREQ_W + MODES_W // 2, y + BAR_H // 2,
                          text=_BAND_MODES.get(name, ""), font=("Segoe UI", 8),
                          fill=TEXT_DIM, anchor='center')

            # FT8 frequentie
            ft8 = _BAND_FT8.get(name, "—")
            c.create_text(BAR_X + BAR_MAX + PCT_W + FREQ_W + MODES_W + FT8_W // 2,
                          y + BAR_H // 2,
                          text=ft8, font=("Segoe UI", 8),
                          fill=ACCENT if ft8 != "—" else TEXT_DIM, anchor='center')

            self._bar_rows.append((y, y + BAR_H, tip))

    def _on_bar_motion(self, event: tk.Event):
        if not self._show_tips_var.get():
            self._tooltip.hide()
            return
        for y0, y1, tip in self._bar_rows:
            if y0 <= event.y <= y1:
                rx = self._prop_canvas.winfo_rootx() + event.x
                ry = self._prop_canvas.winfo_rooty() + event.y
                self._tooltip.show(rx, ry, tip)
                return
        self._tooltip.hide()

    # ── Historiek panel ───────────────────────────────────────────────────────
    def _build_hist_panel(self, parent):
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.X, pady=(6, 0))

        tk.Frame(outer, bg=ACCENT, height=2).pack(fill=tk.X)

        hdr = tk.Frame(outer, bg=BG_PANEL)
        hdr.pack(fill=tk.X, padx=10, pady=(4, 2))
        tk.Label(hdr, text="📈  Band Verloop",
                 font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT).pack(side=tk.LEFT)

        for opt in ("Uren", "Dagen", "Weken", "Maanden"):
            tk.Radiobutton(hdr, text=opt, variable=self._hist_range_var,
                           value=opt, command=lambda: (self._save_cur_settings(), self._draw_hist_graph()),
                           bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                           activebackground=BG_PANEL, activeforeground=TEXT_H1,
                           font=_font(9)).pack(side=tk.LEFT, padx=(8, 0))

        # Toggle: Banden vs Solar-indices
        self._hist_mode_var = tk.StringVar(value="Banden")
        for opt in ("Banden", "Solar"):
            tk.Radiobutton(hdr, text=opt, variable=self._hist_mode_var,
                           value=opt, command=self._draw_hist_graph,
                           bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                           activebackground=BG_PANEL, activeforeground=TEXT_H1,
                           font=_font(9)).pack(side=tk.RIGHT, padx=(0, 6))

        self._hist_updated_var = tk.StringVar(value="")
        tk.Label(hdr, textvariable=self._hist_updated_var,
                 font=_font(8), bg=BG_PANEL, fg=TEXT_DIM).pack(side=tk.RIGHT, padx=(0, 10))

        self._hist_canvas = tk.Canvas(outer, height=120, bg=BG_PANEL,
                                      bd=0, highlightthickness=0)
        self._hist_canvas.pack(fill=tk.X, padx=10, pady=(0, 6))
        self._hist_canvas.bind("<Configure>", lambda *_: self._draw_hist_graph())
        self._hist_tooltip = _Tooltip(self._hist_canvas)
        self._hist_layout: dict = {}
        self._hist_canvas.bind("<Motion>", self._on_hist_motion)
        self._hist_canvas.bind("<Leave>",  lambda *_: self._hist_tooltip.hide())

        # Klikbare legenda (alleen in band-modus zichtbaar)
        self._leg_frame = tk.Frame(outer, bg=BG_PANEL)
        self._leg_frame.pack(fill=tk.X, padx=10, pady=(0, 6))
        self._leg_widgets: dict = {}   # name → (dash_lbl, name_lbl)
        for name, _, is_hf in _BANDS:
            if not is_hf:
                continue
            color  = _BAND_COLORS.get(name, TEXT_DIM)
            lbl_d  = tk.Label(self._leg_frame, text="━", fg=color, bg=BG_PANEL,
                              font=_font(9, "bold"), cursor="hand2")
            lbl_d.pack(side=tk.LEFT)
            lbl_n  = tk.Label(self._leg_frame, text=name, fg=TEXT_DIM, bg=BG_PANEL,
                              font=_font(8), cursor="hand2")
            lbl_n.pack(side=tk.LEFT, padx=(0, 6))
            self._leg_widgets[name] = (lbl_d, lbl_n)
            for w in (lbl_d, lbl_n):
                w.bind("<Button-1>", lambda _, n=name: self._toggle_band(n))

    def _toggle_band(self, name: str):
        if name in self._hist_sel:
            self._hist_sel.discard(name)
        else:
            self._hist_sel.add(name)
        # Legenda visueel bijwerken
        for bname, (lbl_d, lbl_n) in self._leg_widgets.items():
            color   = _BAND_COLORS.get(bname, TEXT_DIM)
            active  = (not self._hist_sel) or (bname in self._hist_sel)
            lbl_d.config(fg=color    if active else TEXT_DIM)
            lbl_n.config(fg=TEXT_BODY if active else TEXT_DIM,
                         font=_font(8, "bold") if bname in self._hist_sel else _font(8))
        self._save_cur_settings()
        self._draw_hist_graph()

    def _draw_hist_graph(self):
        if not hasattr(self, "_hist_canvas"):
            return
        c = self._hist_canvas
        c.delete("all")
        W = c.winfo_width() or 700
        H = c.winfo_height() or 140

        _RANGE = {
            "Uren":    datetime.timedelta(hours=24),
            "Dagen":   datetime.timedelta(days=7),
            "Weken":   datetime.timedelta(weeks=4),
            "Maanden": datetime.timedelta(days=365),
        }
        now   = datetime.datetime.now(datetime.timezone.utc)
        delta = _RANGE.get(self._hist_range_var.get(), datetime.timedelta(hours=24))
        t_min = now - delta

        data = [(t, bp, sol) for t, bp, sol in self._history if t >= t_min]

        PAD_L, PAD_R, PAD_T, PAD_B = 36, 8, 8, 18
        gw = W - PAD_L - PAD_R
        gh = H - PAD_T - PAD_B

        solar_mode = getattr(self, "_hist_mode_var", None) and self._hist_mode_var.get() == "Solar"

        if solar_mode:
            # Toon solar-indices grafiek
            _SOLAR_SERIES = [
                ("sfi",     "#FFC107",  300, "SFI"),
                ("k_index", "#EF5350",    9, "K"),
                ("a_index", "#FF7043",  400, "A"),
                ("ssn",     "#66BB6A",  300, "SSN"),
            ]
            # Y-labels (0 en max per serie — gebruik tweede serie als voorbeeld)
            for i in range(5):
                frac = i / 4
                gy   = PAD_T + gh - int(gh * frac)
                c.create_line(PAD_L, gy, W - PAD_R, gy, fill=BORDER, dash=(2, 4))
            c.create_text(PAD_L - 3, PAD_T,      text="max", fill=TEXT_DIM, font=("Segoe UI", 7), anchor='e')
            c.create_text(PAD_L - 3, PAD_T + gh, text="0",   fill=TEXT_DIM, font=("Segoe UI", 7), anchor='e')

            if len(data) < 2:
                c.create_text(W // 2, PAD_T + gh // 2,
                              text="Nog geen historische data beschikbaar",
                              fill=TEXT_DIM, font=("Segoe UI", 9), anchor='center')
                return

            t0 = t_min.timestamp()
            t1 = now.timestamp()
            dt = max(1.0, t1 - t0)

            for key, color, max_val, short in _SOLAR_SERIES:
                pts = []
                for ts, bp, sol in data:
                    val = sol.get(key, 0)
                    frac = min(1.0, val / max_val)
                    tx = PAD_L + int(gw * (ts.timestamp() - t0) / dt)
                    ty = PAD_T + gh - int(gh * frac)
                    pts.append((tx, ty))
                for j in range(len(pts) - 1):
                    c.create_line(pts[j][0], pts[j][1],
                                  pts[j + 1][0], pts[j + 1][1],
                                  fill=color, width=1)
            # Legenda
            lx = PAD_L
            for key, color, max_val, short in _SOLAR_SERIES:
                c.create_line(lx, PAD_T + gh + 10, lx + 12, PAD_T + gh + 10, fill=color, width=2)
                c.create_text(lx + 14, PAD_T + gh + 10, text=short, fill=TEXT_DIM,
                               font=("Segoe UI", 7), anchor='w')
                lx += 38
            return

        # ── Banden modus ──────────────────────────────────────────────────────
        # Y-raster
        for pct in (0, 25, 50, 75, 100):
            gy = PAD_T + gh - int(gh * pct / 100)
            c.create_line(PAD_L, gy, W - PAD_R, gy,
                          fill=BORDER, dash=(2, 4))
            c.create_text(PAD_L - 3, gy, text=str(pct),
                          fill=TEXT_DIM, font=("Segoe UI", 7), anchor='e')

        if len(data) < 2:
            c.create_text(W // 2, PAD_T + gh // 2,
                          text="Nog geen historische data beschikbaar",
                          fill=TEXT_DIM, font=("Segoe UI", 9), anchor='center')
            self._hist_layout = {}
            return

        t0 = t_min.timestamp()
        t1 = now.timestamp()
        dt = max(1.0, t1 - t0)

        for name, _, is_hf in _BANDS:
            if not is_hf:
                continue
            # Toon alleen geselecteerde banden; leeg = alle banden
            if self._hist_sel and name not in self._hist_sel:
                continue
            color = _BAND_COLORS.get(name, TEXT_DIM)
            pts = []
            for ts, bp, sol in data:
                pct = bp.get(name, 0)
                if pct < 0:
                    pct = 0
                tx = PAD_L + int(gw * (ts.timestamp() - t0) / dt)
                ty = PAD_T + gh - int(gh * pct / 100)
                pts.append((tx, ty))
            for j in range(len(pts) - 1):
                c.create_line(pts[j][0], pts[j][1],
                              pts[j + 1][0], pts[j + 1][1],
                              fill=color, width=1)

        # Layout opslaan voor hover-tooltip
        self._hist_layout = {
            "mode": "Banden", "t0": t0, "dt": dt,
            "pad_l": PAD_L, "gw": gw, "data": data,
        }
        if hasattr(self, "_hist_updated_var"):
            self._hist_updated_var.set(datetime.datetime.now().strftime("%H:%M"))

    # ── Bandopenings-schema (heatmap) ─────────────────────────────────────────
    def _build_schedule_panel(self, parent):
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.BOTH, expand=True, pady=(6, 0))
        tk.Frame(outer, bg=ACCENT, height=2).pack(fill=tk.X)

        hdr = tk.Frame(outer, bg=BG_PANEL)
        hdr.pack(fill=tk.X, padx=10, pady=(4, 2))
        tk.Label(hdr, text="🕐  Bandopenings-schema (lokale tijd, vandaag)",
                 font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT).pack(side=tk.LEFT)
        self._sched_updated_var = tk.StringVar(value="")
        tk.Label(hdr, textvariable=self._sched_updated_var,
                 font=_font(8), bg=BG_PANEL, fg=TEXT_DIM).pack(side=tk.RIGHT)

        self._sched_canvas = tk.Canvas(outer, bg=BG_PANEL,
                                       bd=0, highlightthickness=0)
        self._sched_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 6))
        self._sched_canvas.bind("<Configure>", lambda *_: self._draw_schedule())
        self._sched_tooltip = _Tooltip(self._sched_canvas)
        self._sched_layout: dict = {}   # grid-layout voor hover
        self._sched_canvas.bind("<Motion>", self._on_sched_motion)
        self._sched_canvas.bind("<Leave>",  lambda *_: self._sched_tooltip.hide())

    def _draw_schedule(self):
        if not hasattr(self, "_sched_canvas"):
            return
        c = self._sched_canvas
        c.delete("all")
        W = c.winfo_width() or 700
        H = c.winfo_height() or 130

        data = self._solar_data
        try:
            sfi     = float(data.get("sfi",     "90").replace("—", "90"))
            ssn     = float(data.get("ssn",     "50").replace("—", "50"))
            k_index = float(data.get("k_index", "2" ).replace("—", "2"))
        except (ValueError, TypeError):
            sfi, ssn, k_index = 90.0, 50.0, 2.0
        snr_db = (_MODE_DB.get(self._mode_var.get(), 0) +
                  _POWER_DB.get(self._power_var.get(), 0) +
                  _ANT_DB.get(self._ant_var.get(), 0))

        hf_bands = [(name, freq) for name, freq, is_hf in _BANDS if is_hf]
        n_bands  = len(hf_bands)
        n_hours  = 24

        PAD_L, PAD_R, PAD_T, PAD_B = 40, 4, 16, 4
        cell_w = max(1, (W - PAD_L - PAD_R) // n_hours)
        cell_h = max(1, (H - PAD_T - PAD_B) // n_bands)

        # UTC-offset op basis van DST-instelling (CET=+1, CEST=+2)
        utc_offset = 2 if self._dst_var.get() else 1
        now_utc    = datetime.datetime.now(datetime.timezone.utc)
        now_local_h = (now_utc.hour + utc_offset) % 24

        # Actuele zonpositie eenmalig berekenen
        sun_lat, sun_lon = _subsolar_point()
        lat_r     = math.radians(self._qth_lat)
        sun_lat_r = math.radians(sun_lat)

        # ── Uur-labels bovenaan (lokale tijd) ────────────────────────────
        for local_h in range(0, n_hours, 3):
            lx = PAD_L + local_h * cell_w + cell_w // 2
            c.create_text(lx, PAD_T - 4, text=f"{local_h:02d}",
                          fill=TEXT_DIM, font=("Segoe UI", 7), anchor='s')

        # ── Bereken propagatie per uur en per band ────────────────────────
        # grid_data[bi][h] = pct  (voor hover-tooltip)
        grid_data: list[list[int]] = [[0] * n_hours for _ in range(n_bands)]

        for bi, (bname, _) in enumerate(hf_bands):
            cy = PAD_T + bi * cell_h
            # Bandnaam links
            c.create_text(PAD_L - 3, cy + cell_h // 2, text=bname,
                          fill=TEXT_DIM, font=("Segoe UI", 7), anchor='e')
            for local_h in range(n_hours):
                # Lokale tijd → UTC
                utc_h    = (local_h - utc_offset) % 24
                # Zon-lon voor dit UTC-uur: zon beweegt westenwaarts 15°/uur
                offset_h  = utc_h - now_utc.hour
                sun_lon_h = sun_lon - offset_h * 15
                sun_lon_h = ((sun_lon_h + 180) % 360) - 180
                dlon_r    = math.radians(self._qth_lon - sun_lon_h)
                cos_angle = (math.sin(lat_r) * math.sin(sun_lat_r) +
                             math.cos(lat_r) * math.cos(sun_lat_r) * math.cos(dlon_r))
                is_day_h  = cos_angle > 0

                bp, _, _ = _calc_propagation(sfi, ssn, k_index,
                                             qth_lat=self._qth_lat,
                                             snr_bonus_db=float(snr_db),
                                             daytime=is_day_h)
                pct_map = {n: p for n, _, p in bp}
                pct = max(0, pct_map.get(bname, 0))
                grid_data[bi][local_h] = pct

                # Kleur op basis van kwaliteit
                if pct >= 60:
                    fill = "#2E7D32"   # donkergroen
                elif pct >= 30:
                    fill = "#F9A825"   # amber
                elif pct >= 1:
                    fill = "#B71C1C"   # donkerrood
                else:
                    fill = "#1A1C1F"   # gesloten (bijna zwart)

                cx = PAD_L + local_h * cell_w
                c.create_rectangle(cx, cy, cx + cell_w - 1, cy + cell_h - 1,
                                   fill=fill, outline="")

        # Markeer huidig lokaal uur
        lx = PAD_L + now_local_h * cell_w
        c.create_rectangle(lx, PAD_T, lx + cell_w - 1, PAD_T + n_bands * cell_h - 1,
                           outline=ACCENT, width=1)

        # Sla grid-layout op voor hover-tooltip
        self._sched_layout = {
            "pad_l": PAD_L, "pad_t": PAD_T,
            "cell_w": cell_w, "cell_h": cell_h,
            "n_bands": n_bands, "n_hours": n_hours,
            "band_names": [b for b, _ in hf_bands],
            "grid": grid_data,
            "utc_offset": utc_offset,
        }
        if hasattr(self, "_sched_updated_var"):
            self._sched_updated_var.set(datetime.datetime.now().strftime("%H:%M"))

    def _on_hist_motion(self, event: tk.Event):
        if not self._show_tips_var.get() or not self._hist_layout:
            self._hist_tooltip.hide()
            return
        lay = self._hist_layout
        data = lay.get("data", [])
        if len(data) < 2:
            self._hist_tooltip.hide()
            return
        # Bereken dichtstbijzijnde datapunt op basis van X-positie
        x_frac   = (event.x - lay["pad_l"]) / max(1.0, lay["gw"])
        target_t = lay["t0"] + x_frac * lay["dt"]
        ts, bp, _ = min(data, key=lambda d: abs(d[0].timestamp() - target_t))
        local_ts = ts.astimezone().strftime("%d %b %H:%M")
        tip = [(f"Band Verloop  —  {local_ts}", None), None]
        # HF-banden gesorteerd op openingspercentage
        hf = [(n, max(0, bp.get(n, 0))) for n, _, hf in _BANDS if hf]
        hf.sort(key=lambda x: -x[1])
        for bname, pct in hf:
            if self._hist_sel and bname not in self._hist_sel:
                continue
            tip.append((f"{bname}:", f"{pct}%"))
        if len(tip) <= 2:
            self._hist_tooltip.hide()
            return
        rx = self._hist_canvas.winfo_rootx() + event.x
        ry = self._hist_canvas.winfo_rooty() + event.y
        self._hist_tooltip.show(rx, ry, tip)

    def _on_sched_motion(self, event: tk.Event):
        if not self._show_tips_var.get() or not self._sched_layout:
            self._sched_tooltip.hide()
            return
        lay = self._sched_layout
        col = (event.x - lay["pad_l"]) // lay["cell_w"]
        row = (event.y - lay["pad_t"]) // lay["cell_h"]
        if col < 0 or col >= lay["n_hours"] or row < 0 or row >= lay["n_bands"]:
            self._sched_tooltip.hide()
            return
        pct       = lay["grid"][row][col]
        bname     = lay["band_names"][row]
        local_h   = col
        local_str = f"{local_h:02d}:00–{(local_h + 1) % 24:02d}:00"
        if pct >= 60:
            kwal = "Goed"
        elif pct >= 30:
            kwal = "Fair"
        elif pct >= 1:
            kwal = "Zwak"
        else:
            kwal = "Gesloten"
        tip = [
            (f"{bname}  —  {local_str} (lokaal)", None),
            None,
            ("Kwaliteit:",      kwal),
            ("Betrouwbaarheid:", f"{pct}%"),
            ("FT8:",             _BAND_FT8.get(bname, "—") + " MHz"),
            ("Modi:",            _BAND_MODES.get(bname, "—")),
        ]
        rx = self._sched_canvas.winfo_rootx() + event.x
        ry = self._sched_canvas.winfo_rooty() + event.y
        self._sched_tooltip.show(rx, ry, tip)

    # ── DX Spots panel ───────────────────────────────────────────────────────
    def _build_dx_panel(self, parent):
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.X, pady=(6, 0))
        tk.Frame(outer, bg=ACCENT, height=2).pack(fill=tk.X)

        hdr = tk.Frame(outer, bg=BG_PANEL)
        hdr.pack(fill=tk.X, padx=10, pady=(4, 2))
        tk.Label(hdr, text="📡  Live DX Spots (HF)",
                 font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT).pack(side=tk.LEFT)
        tk.Checkbutton(hdr, text="Eigen continent", variable=self._dx_own_cont_var,
                       command=self._filter_dx_spots,
                       bg=BG_PANEL, fg=TEXT_DIM, selectcolor=BG_SURFACE,
                       activebackground=BG_PANEL, activeforeground=TEXT_BODY,
                       font=_font(9)).pack(side=tk.RIGHT, padx=(0, 4))

        status_row = tk.Frame(outer, bg=BG_PANEL)
        status_row.pack(fill=tk.X, padx=10)
        self._dx_status_var    = tk.StringVar(value="Laden…")
        self._dx_countdown_var = tk.StringVar(value="")
        tk.Label(status_row, textvariable=self._dx_status_var,
                 font=_font(8), bg=BG_PANEL, fg=TEXT_DIM).pack(side=tk.LEFT)
        tk.Label(status_row, textvariable=self._dx_countdown_var,
                 font=_font(8), bg=BG_PANEL, fg=ACCENT).pack(side=tk.RIGHT)

        dx_wrap = tk.Frame(outer, bg=BG_PANEL)
        dx_wrap.pack(fill=tk.X, padx=10, pady=(2, 6))
        self._dx_canvas = tk.Canvas(dx_wrap, height=280, bg=BG_PANEL,
                                    bd=0, highlightthickness=0)
        dx_sb = tk.Scrollbar(dx_wrap, orient=tk.VERTICAL,
                             command=self._dx_canvas.yview,
                             bg=BG_SURFACE, troughcolor=BG_ROOT, width=8)
        self._dx_canvas.configure(yscrollcommand=dx_sb.set)
        dx_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._dx_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._dx_canvas.bind("<Configure>", lambda *_: self._draw_dx_panel())
        self._dx_canvas.bind("<MouseWheel>",
            lambda e: self._dx_canvas.yview_scroll(
                -1 if e.delta > 0 else 1, "units"))

    def _filter_dx_spots(self):
        spots = self._dx_all_spots
        if self._dx_own_cont_var.get():
            my = _qth_continent(self._qth_lat, self._qth_lon)
            spots = [s for s in spots if s.get("sp_cont") == my]
        self._dx_filtered = spots
        self._draw_dx_panel()
        n     = len(spots)
        filt  = " · eigen continent" if self._dx_own_cont_var.get() else ""
        total = len(self._dx_all_spots)
        ts    = datetime.datetime.now().strftime("%H:%M")
        self._dx_status_var.set(
            f"{n} van {total} spots  (HF{filt})  ·  {ts}" if total else f"Geen spots beschikbaar  ·  {ts}")

    def _draw_dx_panel(self):
        if not hasattr(self, "_dx_canvas"):
            return
        c = self._dx_canvas
        c.delete("all")
        W = c.winfo_width() or 700
        H = c.winfo_height() or 196

        spots = getattr(self, "_dx_filtered", [])
        ROW_H = 16
        C_UTC  = 38;  C_BAND = 38;  C_DX = 84
        C_FREQ = 68;  C_SPOT = 74
        C_CMT  = max(40, W - C_UTC - C_BAND - C_DX - C_FREQ - C_SPOT - 12)

        # Kolomkoppen
        for txt, x in [("UTC",     4),
                       ("Band",    4 + C_UTC),
                       ("DX",      4 + C_UTC + C_BAND),
                       ("MHz",     4 + C_UTC + C_BAND + C_DX),
                       ("Spotter", 4 + C_UTC + C_BAND + C_DX + C_FREQ),
                       ("Comment", 4 + C_UTC + C_BAND + C_DX + C_FREQ + C_SPOT)]:
            c.create_text(x, 2, text=txt, fill=ACCENT,
                          font=("Consolas", 8, "bold"), anchor='nw')
        c.create_line(0, ROW_H + 2, W, ROW_H + 2, fill=BORDER)

        if not spots:
            c.create_text(W // 2, H // 2,
                          text="Geen HF-spots beschikbaar",
                          fill=TEXT_DIM, font=("Segoe UI", 9), anchor='center')
            c.configure(scrollregion=(0, 0, W, H))
            return

        max_ch = max(4, C_CMT // 6)
        for i, s in enumerate(spots):
            y = ROW_H + 4 + i * ROW_H
            if i % 2 == 0:
                c.create_rectangle(0, y - 1, W, y + ROW_H - 1,
                                   fill=BG_SURFACE, outline="")
            band  = s["band"]
            color = _BAND_COLORS.get(band, TEXT_DIM)
            x = 4
            c.create_text(x, y, text=s["time"],         fill=TEXT_DIM,  font=("Consolas", 8), anchor='nw'); x += C_UTC
            c.create_text(x, y, text=band,              fill=color,     font=("Consolas", 8, "bold"), anchor='nw'); x += C_BAND
            c.create_text(x, y, text=s["dx"][:11],      fill=TEXT_H1,   font=("Consolas", 8), anchor='nw'); x += C_DX
            c.create_text(x, y, text=s["freq_mhz"],     fill=TEXT_BODY, font=("Consolas", 8), anchor='nw'); x += C_FREQ
            c.create_text(x, y, text=s["spotter"][:10], fill=TEXT_DIM,  font=("Consolas", 8), anchor='nw'); x += C_SPOT
            c.create_text(x, y, text=s.get("comment", "")[:max_ch],
                          fill=TEXT_DIM, font=("Consolas", 8), anchor='nw')
        total_h = ROW_H + 4 + len(spots) * ROW_H
        c.configure(scrollregion=(0, 0, W, total_h))

    def _refresh_dx(self):
        spots = _fetch_dx_spots()
        self.root.after(0, lambda: self._on_dx_spots(spots))

    def _on_dx_spots(self, spots: list):
        self._dx_all_spots = spots
        self._filter_dx_spots()
        self._schedule_dx()

    def _schedule_dx(self):
        self._dx_next_at  = (datetime.datetime.now(datetime.timezone.utc)
                             + datetime.timedelta(seconds=DX_REFRESH_SECS))
        self._dx_after_id = self.root.after(
            DX_REFRESH_SECS * 1000,
            lambda: threading.Thread(target=self._refresh_dx, daemon=True).start()
        )

    # ── Advies panel ─────────────────────────────────────────────────────────
    def _build_advice_panel(self, parent):
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.X, pady=(6, 0))
        tk.Frame(outer, bg=ACCENT, height=2).pack(fill=tk.X)
        adv_hdr = tk.Frame(outer, bg=BG_PANEL)
        adv_hdr.pack(fill=tk.X, padx=10, pady=(4, 0))
        tk.Label(adv_hdr, text="💡  Propagatie-analyse & Advies",
                 font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT).pack(side=tk.LEFT)
        self._advice_updated_var = tk.StringVar(value="")
        tk.Label(adv_hdr, textvariable=self._advice_updated_var,
                 font=_font(8), bg=BG_PANEL, fg=TEXT_DIM).pack(side=tk.RIGHT)
        self._advice_frame = tk.Frame(outer, bg=BG_PANEL)
        self._advice_frame.pack(fill=tk.X, padx=10, pady=(0, 8))

    def _update_advice(self):
        if not hasattr(self, "_advice_frame"):
            return
        for w in self._advice_frame.winfo_children():
            w.destroy()

        data = self._solar_data
        try:
            sfi     = float(data.get("sfi",     "90").replace("—", "90"))
            ssn     = float(data.get("ssn",     "50").replace("—", "50"))
            k_index = float(data.get("k_index", "2" ).replace("—", "2"))
            a_index = float(data.get("a_index", "5" ).replace("—", "5"))
        except (ValueError, TypeError):
            sfi, ssn, k_index, a_index = 90.0, 50.0, 2.0, 5.0

        xray    = data.get("xray", "")
        sw_spd  = data.get("sw_speed", "—")
        sw_bz   = data.get("sw_bz",    "—")
        is_day  = self._day_var.get()
        bp      = {n: p for n, _, p in self._last_band_pct if p >= 0}
        hf_open = sorted([(n, p) for n, p in bp.items() if p > 0], key=lambda x: -x[1])

        tips: list[tuple[str, str, str]] = []   # (icon, tekst, kleur)

        # ── 1. Beste banden ───────────────────────────────────────────────
        if hf_open:
            best = hf_open[:5]
            bstr = "  ·  ".join(f"{n} {p}%" for n, p in best)
            extra = f"  ({len(hf_open)} banden open)" if len(hf_open) > 5 else ""
            tips.append(("📡", f"Beste banden nu:  {bstr}{extra}", "#4CAF50"))
        else:
            tips.append(("📡", "Alle HF-banden zijn momenteel gesloten.", TEXT_DIM))

        # ── 2. Geomagnetische condities (K + A) ────────────────────────────
        a_kwal = ("rustig" if a_index < 10 else
                  "onrustig" if a_index < 30 else
                  "storm" if a_index < 100 else "ernstige storm")
        if k_index >= 7:
            tips.append(("🚨", f"Zware geomagnetische storm  K={int(k_index)}, A={int(a_index)} ({a_kwal}) — "
                                "HF vrijwel onbruikbaar, auroraal absorptie op alle routes. "
                                "Wacht op herstel (normaal binnen 12–24u).", "#F44336"))
        elif k_index >= 5:
            tips.append(("⚠️", f"Geomagnetische storm  K={int(k_index)}, A={int(a_index)} ({a_kwal}) — "
                                "poolroutes geblokkeerd, 40m/80m meest betrouwbaar. "
                                "Hoge banden en DX sterk verstoord.", "#F44336"))
        elif k_index >= 3:
            tips.append(("⚡", f"Verhoogde geo-activiteit  K={int(k_index)}, A={int(a_index)} ({a_kwal}) — "
                                "lagere banden stabieler; vermijd trans-polair DX. "
                                "Overweeg 40m/80m voor betrouwbare verbindingen.", "#FFC107"))
        else:
            tips.append(("✅", f"Rustige geo-condities  K={int(k_index)}, A={int(a_index)} — "
                                "optimaal voor alle routes incl. poolpaden en DX.", "#4CAF50"))

        # ── 3. Zonactiviteit / zonnecyclus ─────────────────────────────────
        if sfi >= 200:
            tips.append(("🌟", f"Exceptionele zonactiviteit  SFI={int(sfi)}, SSN={int(ssn)} — "
                                "zonnecyclus-maximum. 10m/12m/15m open voor wereldwijd DX; "
                                "kans op Es-versterking en TEP.", ACCENT))
        elif sfi >= 150:
            tips.append(("☀️", f"Hoge zonactiviteit  SFI={int(sfi)}, SSN={int(ssn)} — "
                                "uitstekend voor 10m t/m 17m DX. F2-propagatie sterk; "
                                "MUF hoog, lange skips mogelijk.", ACCENT))
        elif sfi >= 100:
            tips.append(("🌤", f"Goede zonactiviteit  SFI={int(sfi)}, SSN={int(ssn)} — "
                                "20m en 17m zijn primaire DX-banden; 15m kan open zijn. "
                                "Verwacht betrouwbare F2-propagatie overdag.", ACCENT))
        elif sfi >= 80:
            tips.append(("🌥", f"Matige zonactiviteit  SFI={int(sfi)}, SSN={int(ssn)} — "
                                "20m/40m meest betrouwbaar. Hoge banden onzeker; "
                                "80m goed voor regionaal verkeer.", TEXT_BODY))
        else:
            tips.append(("🌧", f"Lage zonactiviteit  SFI={int(sfi)}, SSN={int(ssn)} — "
                                "40m en 80m bieden meeste kans op verbindingen. "
                                "Banden ≥15m grotendeels dicht; 160m voor nacht-DX.", TEXT_DIM))

        # ── 4. Solarwind en Bz ─────────────────────────────────────────────
        try:
            spd = float(sw_spd)
            bz  = float(sw_bz)
            if spd > 700 or bz <= -20:
                tips.append(("🌪", f"Stormachtige solarwind  v={int(spd)} km/s, Bz={bz:+.1f} nT — "
                                    "verhoogde kans op CME-impact; K-index kan snel stijgen. "
                                    "Monitor condities actief.", "#F44336"))
            elif spd > 500 or bz <= -10:
                tips.append(("💨", f"Verhoogde solarwind  v={int(spd)} km/s, Bz={bz:+.1f} nT — "
                                    "Bz negatief koppelt aan aardveld → K-stijging mogelijk. "
                                    "Lagere banden aanhouden.", "#FFC107"))
            elif bz > 5:
                tips.append(("🛡", f"Rustige solarwind  v={int(spd)} km/s, Bz={bz:+.1f} nT — "
                                   "positieve Bz beschermt aardveld. Stabiele condities.", "#4CAF50"))
            else:
                tips.append(("💫", f"Normale solarwind  v={int(spd)} km/s, Bz={bz:+.1f} nT — "
                                   "geen direct effect op propagatie verwacht.", TEXT_BODY))
        except (ValueError, TypeError):
            pass   # solarwind nog niet beschikbaar

        # ── 5. X-ray / flares ─────────────────────────────────────────────
        xclass = xray[:1].upper() if xray else ""
        if xclass in ("X",):
            tips.append(("☢", f"X-flare gedetecteerd  ({xray}) — Short Wave Fadeout (SWF) "
                               "mogelijk op dag-zijde; HF tijdelijk geblokkeerd. "
                               "Herstel verwacht binnen 15–60 min.", "#F44336"))
        elif xclass == "M":
            tips.append(("⚡", f"M-flare actief  ({xray}) — lichte SWF mogelijk op lagere HF. "
                               "Verhoogde kans op Proton Event (PCA) bij M5+.", "#FFC107"))
        # C en lager: geen melding nodig

        # ── 6. Ionosfeer / MUF / LUF ──────────────────────────────────────
        try:
            muf = float(data.get("muf", "0").replace("—", "0"))
            if muf > 0:
                if muf >= 28:
                    muf_txt = f"MUF={muf:.1f} MHz — 10m t/m 20m alle open; F2-laag optimaal"
                elif muf >= 14:
                    muf_txt = f"MUF={muf:.1f} MHz — 20m open; banden > {muf:.0f} MHz dicht"
                elif muf >= 7:
                    muf_txt = f"MUF={muf:.1f} MHz — alleen 40m–80m bruikbaar"
                else:
                    muf_txt = f"MUF={muf:.1f} MHz — ionosfeer zwak; alleen 80m/160m"
                luf_est = 3.5 + k_index * 0.8
                tips.append(("📶", f"Ionosfeer: {muf_txt}. "
                                   f"Geschatte LUF ≈ {luf_est:.1f} MHz "
                                   f"({'verhoogd door K-index' if k_index >= 3 else 'normaal'}).",
                             TEXT_BODY))
        except (ValueError, TypeError):
            pass

        # ── 7. Dag/nacht + transitievensters ──────────────────────────────
        utc_h = datetime.datetime.now(datetime.timezone.utc).hour
        tz_off = 2 if self._dst_var.get() else 1
        lok_h  = (utc_h + tz_off) % 24
        if is_day:
            if 6 <= lok_h < 10:
                tips.append(("🌅", f"Ochtend ({lok_h:02d}:xx lokaal) — F2-laag bouwt op; "
                                   "20m wordt snel bruikbaar. Grey-line kansen voor DX-paden "
                                   "richting Amerika en Azië.", TEXT_BODY))
            elif 10 <= lok_h < 16:
                tips.append(("🌞", f"Middag ({lok_h:02d}:xx lokaal) — F2 op maximale hoogte; "
                                   "beste window voor 15m/17m/20m DX. "
                                   "Probeer SSB of FT8 voor trans-Atlantische verbindingen.", TEXT_BODY))
            else:
                tips.append(("🌇", f"Namiddag ({lok_h:02d}:xx lokaal) — Grey-line nadert; "
                                   "uitstekend voor DX richting Azië en Pacific. "
                                   "15m en 17m vaak prachtig in deze uren.", TEXT_BODY))
        else:
            if 22 <= lok_h or lok_h < 2:
                tips.append(("🌃", f"Vroege nacht ({lok_h:02d}:xx lokaal) — 40m en 80m open "
                                   "voor regionaal Europa-verkeer. F2-laag daalt; "
                                   "LUF stijgt op korte paden.", TEXT_BODY))
            elif 2 <= lok_h < 6:
                tips.append(("🌌", f"Nacht ({lok_h:02d}:xx lokaal) — 160m en 80m actief voor "
                                   "trans-Atlantisch DX. 40m goed voor Noord-Amerika. "
                                   "FT8 op lage banden voor DX-afstanden > 5000 km.", TEXT_BODY))
            else:
                tips.append(("🌄", f"Voor de ochtend ({lok_h:02d}:xx lokaal) — Grey-line "
                                   "nadert; 80m/40m DX-window naar Azië/Pacific. "
                                   "20m begint te openen richting Amerika.", TEXT_BODY))

        # ── 8. Modus / vermogen advies ────────────────────────────────────
        mode  = self._mode_var.get()
        power = self._power_var.get()
        snr_db = (_MODE_DB.get(mode, 0) + _POWER_DB.get(power, 0) +
                  _ANT_DB.get(self._ant_var.get(), 0))
        if hf_open:
            best_pct = hf_open[0][1]
            if best_pct < 30 and mode == "SSB":
                tips.append(("🔧", f"Modus-advies: condities zwak ({best_pct}% op {hf_open[0][0]}) — "
                                   "overweeg FT8 (+25 dB winst t.o.v. SSB) of CW (+10 dB). "
                                   f"Huidig SNR-budget: {snr_db:+d} dB.", "#FFC107"))
            elif best_pct >= 60 and snr_db < -5:
                tips.append(("🔧", f"Modus-advies: goede condities ({best_pct}% op {hf_open[0][0]}) — "
                                   f"SSB goed bruikbaar. SNR-budget {snr_db:+d} dB; "
                                   "verhoog vermogen of verbeter antenne voor meer bereik.", TEXT_BODY))
            else:
                tips.append(("🔧", f"Modus-advies: {mode} passend bij huidig {best_pct}% op {hf_open[0][0]}. "
                                   f"SNR-budget: {snr_db:+d} dB. "
                                   "FT8 geeft altijd +25 dB extra marge.", TEXT_BODY))

        # ── 9. Absorptie & poolroutes ─────────────────────────────────────
        lat = abs(self._qth_lat)
        if lat > 50 and k_index >= 4:
            tips.append(("🧲", f"Auroraal absorptie verhoogd (K={int(k_index)}, QTH {lat:.0f}°) — "
                               "trans-polaire paden (Europa→Canada, Europa→Japan via pool) "
                               "sterk verzwakt. Gebruik equatoriale routes via 20m/17m.", "#FFC107"))
        elif lat > 45 and k_index >= 3:
            tips.append(("🧲", f"Lichte absorptie mogelijk (K={int(k_index)}, QTH {lat:.0f}°) — "
                               "poolpaden kunnen sporadisch verstoord zijn. "
                               "Monitor 40m voor bruikbaarheid.", TEXT_BODY))

        # ── 10. Algehele beoordeling ──────────────────────────────────────
        score = 0
        if sfi >= 150: score += 3
        elif sfi >= 100: score += 2
        elif sfi >= 80: score += 1
        if k_index <= 2: score += 2
        elif k_index <= 4: score += 1
        if hf_open and hf_open[0][1] >= 60: score += 2
        elif hf_open: score += 1
        try:
            if float(sw_bz) < -10: score -= 1
        except (ValueError, TypeError):
            pass
        overall = ("Uitstekend 🏆" if score >= 6 else
                   "Goed ✅" if score >= 4 else
                   "Matig ⚡" if score >= 2 else
                   "Slecht ⚠️")
        overall_clr = ("#4CAF50" if score >= 6 else
                       "#8BC34A" if score >= 4 else
                       "#FFC107" if score >= 2 else "#F44336")
        open_cnt = len(hf_open)
        tips.append(("📊", f"Algehele propagatie-score: {overall}  "
                           f"(SFI {int(sfi)} · K {int(k_index)} · {open_cnt} banden open). "
                           f"{'Dag' if is_day else 'Nacht'}condities, QTH {self._qth_lat:.1f}°N.",
                     overall_clr))

        # ── Weergave: 3 kolommen ──────────────────────────────────────────
        COLS = 3
        for c in range(COLS):
            self._advice_frame.columnconfigure(c, weight=1)
        for i, (icon, tekst, kleur) in enumerate(tips):
            col = i % COLS
            row = i // COLS
            cell = tk.Frame(self._advice_frame, bg=BG_SURFACE, padx=8, pady=5)
            cell.grid(row=row, column=col, sticky='nsew',
                      padx=(0, 5 if col < COLS - 1 else 0), pady=(0, 4))
            tk.Label(cell, text=f"{icon}  {tekst}", font=_font(9),
                     bg=BG_SURFACE, fg=kleur,
                     anchor='nw', wraplength=300, justify='left').pack(fill=tk.X)
        if hasattr(self, "_advice_updated_var"):
            self._advice_updated_var.set(datetime.datetime.now().strftime("%H:%M"))

    def _update_band_cond_panel(self, band_pct_day, band_pct_ngt):
        def _cond(pct):
            if pct == -1:  return "LOS",    TEXT_DIM
            if pct >= 60:  return "Goed",   "#4CAF50"
            if pct >= 30:  return "Fair",   "#FFC107"
            if pct >= 1:   return "Arm",    "#F44336"
            return               "Dicht",  TEXT_DIM

        pct_day = {name: pct for name, _, pct in band_pct_day}
        pct_ngt = {name: pct for name, _, pct in band_pct_ngt}
        for name, (day_lbl, ngt_lbl, is_hf) in self._band_cond_labels.items():
            default = -1 if not is_hf else 0
            dt, dc = _cond(pct_day.get(name, default))
            nt, nc = _cond(pct_ngt.get(name, default))
            day_lbl.config(text=dt, fg=dc)
            ngt_lbl.config(text=nt, fg=nc)

    def _recalc_prop(self, *_, auto_daynight: bool = False):
        data = self._solar_data
        try:
            sfi     = float(data.get("sfi",     "90").replace("—", "90"))
            ssn     = float(data.get("ssn",     "50").replace("—", "50"))
            k_index = float(data.get("k_index", "2" ).replace("—", "2"))
        except (ValueError, TypeError):
            sfi, ssn, k_index = 90.0, 50.0, 2.0

        # Dag/nacht: bij automatische refresh op QTH-positie bepalen
        if auto_daynight:
            is_day = _is_daytime_at_qth(self._qth_lat, self._qth_lon)
            self._day_var.set(is_day)
        else:
            is_day = self._day_var.get()

        snr_db = (_MODE_DB.get(self._mode_var.get(), 0) +
                  _POWER_DB.get(self._power_var.get(), 0) +
                  _ANT_DB.get(self._ant_var.get(), 0))
        self._db_var.set(f"Totaal: {snr_db:+d} dB")
        self._save_cur_settings()

        band_pct, muf, luf = _calc_propagation(
            sfi, ssn, k_index,
            qth_lat=self._qth_lat,
            snr_bonus_db=float(snr_db),
            daytime=is_day
        )
        self._muf_var.set(f"MUF: {muf} MHz")
        self._luf_var.set(f"LUF: {luf} MHz")
        self._draw_prop_bars(band_pct)

        # Bandconditie panel: altijd zowel dag als nacht berekenen
        bpd, _, _ = _calc_propagation(sfi, ssn, k_index, qth_lat=self._qth_lat,
                                       snr_bonus_db=float(snr_db), daytime=True)
        bpn, _, _ = _calc_propagation(sfi, ssn, k_index, qth_lat=self._qth_lat,
                                       snr_bonus_db=float(snr_db), daytime=False)
        self._update_band_cond_panel(bpd, bpn)

        # Geschiedenis bijhouden
        now = datetime.datetime.now(datetime.timezone.utc)
        bp  = {n: p for n, _, p in band_pct}
        try:
            a_val = float(data.get("a_index", "0").replace("—", "0"))
        except (ValueError, TypeError):
            a_val = 0.0
        sol = {"sfi": sfi, "ssn": ssn, "k_index": k_index, "a_index": a_val}
        self._history.append((now, bp, sol))
        _append_history(now, bp, sol)
        self._draw_hist_graph()
        self._draw_schedule()
        self._update_advice()
        self._check_alerts(bp, k_index)
        if hasattr(self, "_prop_updated_var"):
            self._prop_updated_var.set(datetime.datetime.now().strftime("%H:%M"))

    # ── Instellingen opslaan ──────────────────────────────────────────────────
    def _save_cur_settings(self):
        _save_settings(self._qth_lat, self._qth_lon,
                       self._refresh_var.get(),
                       self._mode_var.get(),
                       self._power_var.get(),
                       self._ant_var.get(),
                       self._dst_var.get(),
                       self._show_tips_var.get(),
                       self._show_sun_var.get(),
                       self._show_moon_var.get(),
                       self._show_locator_var.get(),
                       self._show_graylijn_var.get(),
                       self._show_iaru_var.get(),
                       self._show_cs_var.get(),
                       self._hist_range_var.get(),
                       self._hist_sel,
                       self._k_alert_var.get())

    # ── Refresh interval ──────────────────────────────────────────────────────
    # ── Systeem-tray ─────────────────────────────────────────────────────────
    def _start_tray(self):
        if not _TRAY_OK:
            return
        # Bouw tray-icoon vanuit PIL (hergebruik hamios.ico of genereer inline)
        ico_path = os.path.join(APP_DIR, "hamios.ico")
        if os.path.exists(ico_path):
            tray_img = Image.open(ico_path).resize((64, 64)).convert("RGBA")
        else:
            tray_img = Image.new("RGBA", (64, 64), (26, 28, 31, 255))
        menu = pystray.Menu(
            pystray.MenuItem("HAMIOS tonen", self._tray_show, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Afsluiten", self._tray_quit),
        )
        self._tray_icon = pystray.Icon("HAMIOS", tray_img, "HAMIOS v2.0", menu)
        threading.Thread(target=self._tray_icon.run, daemon=True).start()

    def _tray_show(self, icon=None, item=None):
        self.root.after(0, lambda: (self.root.deiconify(), self.root.lift()))

    def _tray_quit(self, icon=None, item=None):
        if self._tray_icon:
            self._tray_icon.stop()
        self.root.after(0, self.root.destroy)

    def _on_close(self):
        """Venster sluiten → minimaliseren naar tray (of afsluiten als geen tray)."""
        if _TRAY_OK and self._tray_icon:
            self.root.withdraw()
        else:
            self.root.destroy()

    def _check_alerts(self, bp: dict, k_index: float):
        """Stuur tray-notificaties bij band-opening of K-index drempel-overschrijding."""
        threshold = self._k_alert_var.get()

        # ── K-index drempel ──────────────────────────────────────────────
        k_above = k_index >= threshold
        if k_above and not self._prev_k_above:
            self._tray_notify(
                "⚠️ Geomagnetische storm",
                f"K-index is gestegen naar {int(k_index)} (drempel: {threshold}). "
                "HF-propagatie kan verstoord zijn.")
        self._prev_k_above = k_above

        # ── Band-opening detectie ────────────────────────────────────────
        newly_open = []
        for name, pct in bp.items():
            was_open = self._prev_band_open.get(name, False)
            is_open  = pct >= 20
            if is_open and not was_open:
                newly_open.append(f"{name} ({pct}%)")
            self._prev_band_open[name] = is_open

        if newly_open:
            bands_str = ",  ".join(newly_open)
            self._tray_notify("📡 Band geopend", f"{bands_str} is nu open.")

    def _tray_notify(self, title: str, message: str):
        """Stuur een tray-notificatie (alleen als tray actief is)."""
        if _TRAY_OK and self._tray_icon:
            try:
                self._tray_icon.notify(message, title)
            except Exception:
                pass

    def _on_interval_change(self, choice):
        self._refresh_var.set(choice)
        self._save_cur_settings()
        if self._solar_after_id:
            self.root.after_cancel(self._solar_after_id)
            self._solar_after_id = None
        self._schedule_solar()

    # ── Solar data ────────────────────────────────────────────────────────────
    def _refresh_solar(self):
        data = _fetch_solar()
        self.root.after(0, lambda: self._update_solar(data))

    def _schedule_solar(self):
        interval_s = _REFRESH_OPTIONS.get(self._refresh_var.get(), 0)
        if interval_s > 0:
            self._next_refresh_at = (datetime.datetime.now(datetime.timezone.utc)
                                     + datetime.timedelta(seconds=interval_s))
            self._solar_after_id = self.root.after(
                interval_s * 1000,
                lambda: threading.Thread(target=self._refresh_solar, daemon=True).start()
            )
        else:
            self._next_refresh_at = None

    def _update_solar(self, data: dict):
        self._solar_data = data
        if "error" in data:
            self._updated_var.set(f"Fout: {data['error']}")
            self._schedule_solar()
            return

        for key, var in self._solar_vars.items():
            var.set(data.get(key, "—"))

        # K-index: alleen getal, kleur op drempelwaarde
        try:
            k = int(data.get("k_index", 0))
            self._solar_vars["k_index"].set(str(k))
            if k >= 5:
                k_color = "#EF5350"   # rood
            elif k >= 3:
                k_color = "#FFA726"   # oranje
            else:
                k_color = TEXT_H1
            if hasattr(self, "_solar_val_lbls"):
                self._solar_val_lbls["k_index"].config(fg=k_color)
        except (ValueError, TypeError):
            pass

        for key, var in self._solar_vars.items():
            if key.startswith("band_"):
                var.set(data.get(key, "—"))

        # Bz-kleur: negatief = geoeffectief (oranje/rood)
        try:
            bz_str = data.get("sw_bz", "—")
            bz_val = float(bz_str)
            if bz_val <= -20:
                bz_color = "#EF5350"   # rood — sterke zuidwaartse component
            elif bz_val <= -10:
                bz_color = "#FFA726"   # oranje — geoeffectief
            else:
                bz_color = TEXT_H1
            if hasattr(self, "_solar_val_lbls") and "sw_bz" in self._solar_val_lbls:
                self._solar_val_lbls["sw_bz"].config(fg=bz_color)
        except (ValueError, TypeError):
            pass

        # Bijgewerkt: toon QTH-lokale tijd
        local_now = datetime.datetime.now().strftime("%H:%M")
        self._updated_var.set(f"Bijgewerkt: {local_now}")

        # ── X-flare detectie ──────────────────────────────────────────────────
        self._check_xflare(data.get("xray", ""))

        self._recalc_prop(auto_daynight=True)
        self.root.after(0, self._draw_map)
        self._schedule_solar()

    def _check_xflare(self, xray: str):
        """Detecteer M/X-flare in het xray-veld en toon SWF-waarschuwing."""
        import re
        xray = (xray or "").strip().upper()
        # Verwijder label suffix als het aanwezig is (bijv. "M5.2" of "X1.3")
        m = re.match(r'^([MX])(\d+(?:\.\d+)?)', xray)
        if m:
            cls   = m.group(1)
            level = float(m.group(2))
            if cls == "X" or (cls == "M" and level >= 1.0):
                dur_min = 60 if cls == "X" else 30
                msg = (f"☢  SWF-waarschuwing: {xray}-flare gedetecteerd. "
                       f"HF dag-zijde verstoord (~{dur_min} min).")
                self._xflare_var.set(msg)
                self._xflare_lbl.config(fg="#FF7043")
                # Tray-notificatie (alleen als dit een nieuwe flare is)
                if xray != self._last_xflare:
                    self._tray_notify(
                        f"☢ {xray}-flare",
                        f"Short Wave Fadeout verwacht (~{dur_min} min). "
                        "HF op dag-zijde tijdelijk verstoord.")
                    self._last_xflare = xray
                return
        self._xflare_var.set("")
        self._last_xflare = ""

    # ── Venster centreren ─────────────────────────────────────────────────────
    def _center_window(self, min_w: int, min_h: int):
        # update() zodat canvas-widgets correct gemeten worden (resize-events vuren)
        self.root.update()
        scr_w = self.root.winfo_screenwidth()
        scr_h = self.root.winfo_screenheight()
        usable_h = scr_h - 60   # reserveer ruimte voor taakbalk
        usable_w = scr_w - 60
        # Gebruik tkinter-berekende benodigde grootte als die groter is
        req_w = self.root.winfo_reqwidth()
        req_h = self.root.winfo_reqheight()
        w = max(min_w, req_w if req_w > 100 else min_w)
        h = max(min_h, req_h if req_h > 100 else min_h)
        # Hard begrenzen aan beschikbaar schermgebied
        w = min(w, usable_w)
        h = min(h, usable_h)
        x = max(0, (scr_w - w) // 2)
        y = max(0, (scr_h - h) // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        # Stel minsize in zodat verkleinen niet onder bruikbare grens gaat
        self.root.minsize(min(900, usable_w), min(600, usable_h))


# ── Entrypoint ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import signal
    import traceback as _tb

    root = tk.Tk()

    # Ctrl+C via OS-signaal → netjes afsluiten via event-loop
    signal.signal(signal.SIGINT, lambda *_: root.after(0, root.destroy))

    # Onderdruk de lelijke tkinter-traceback bij KeyboardInterrupt in callbacks
    def _cb_exception(exc_type, exc_val, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            root.after(0, root.destroy)
            return
        _tb.print_exception(exc_type, exc_val, exc_tb)

    root.report_callback_exception = _cb_exception

    app = HAMIOSApp(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
