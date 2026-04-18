"""
HAMIOS v2.3
by Frank van Dijke

HAM radio propagatie- en DX-monitor met donkere GUI.
Features: solar/ionosfeer data (SFI, SSN, A/K-index, Bz, solarwind),
          HF band betrouwbaarheid (MUF/LUF model, mode/vermogen/antenne),
          WSPR/PSKReporter spots op kaart, DX-spot markers,
          CAT-interface (Yaesu/Kenwood/Elecraft/Icom CI-V),
          6 talen (NL/EN/DE/FR/IT/ES), systeemtray, ticker.

Dependencies:
  pip install pillow
  pip install pyserial   # optioneel, voor CAT-interface
  pip install pystray    # optioneel, voor systeemtray

─────────────────────────────────────────────────────────────────────
Todo
─────────────────────────────────────────────────────────────────────

[x] WSPR/PSKReporter spots op kaart, selecteerbaar
    Haal live gemeten propagatiepaden op van wspr.rocks (WSPR) of
    pskreporter.info (FT8/FT4). Teken verbindingslijnen op de wereldkaart
    (kleur = band, dikte = SNR). Selecteerbaar via checkbox in kaart-header.
    Geeft echte gemeten propagatie i.p.v. alleen modelwaarden.

[ ] Aurora-ring overlay op kaart, selecteerbaar
    Teken de magnetische aurora-ovaal op de kaart op basis van de K-index
    (hogere K → ring schuift equatorwaarts). Gebruik de empirische formule
    van Feldstein/Holzworth. Geeft direct inzicht in geblokkeerde poolroutes.
    Kleur: groen/geel/rood afhankelijk van K-niveau.

[x] DX-spot markers op de kaart, selecteerbaar
    Teken de actieve DX-cluster spots als lijnen op de kaart: stip op de
    DX-locatie (DXCC-centroid) en lijn naar de spotter. Kleur per band.
    Toggle via "Spots"-checkbox in de kaart-header. Klikken op een stip
    toont de callsign, frequentie en comment als pop-up.

[x] CAT-interface via Yaesu CAT (serieel USB)
    Lees actieve frequentie/band uit en markeer die band visueel in het
    HF-betrouwbaarheidspaneel. Optioneel: stuur frequentie naar de radio
    via klikken op een band in het schema.

[x] CAT terminal venster: "Terminal" checkbox naast VFO-A/B label.
    Geel = verzonden (▶ FA;FB;, ▶ VS0;FA…;), Blauw = ontvangen (◀ FA…;FB…;).
    Gebruik terminal om exact te zien wat verzonden wordt naar de Yaesu
    (formaat: VS0;FA00027000000; — 11 cijfers met voorloopnullen, per FT-950 spec).
    VFO-B waarde wordt getoond naast VFO-A zodra radio reageert op FB;.


[x] Nieuw bericht aanduiding
    Zet in de analyse/advies kaart een gele stip rechts boven zodat je kan zien
    dat er bericht ververst is. Verwijder de stip bij de eerst volgende refresh tenzij
    er een nieuw bericht is.

[x] Vertaal de app
    Vertaal alle teksten in NL,UK,DE,FR, IT
    Ook de analyses, helpteksten en interface teksten.

[x] Maak de ticker selecteerbaar
    Zet een selectievakje in de header die de ticker selecteerbaar maakt.

[x] Pas grote van de analyse en advies paneel aan
    Maak het analyse en advies paneel net zo groot voor de header en de 4 rijen kaarten plus te ticker.
    Bij het opstarten moet dit paneel al de juiste grote hebben zodat, en de titel, en de 4 rijen en de ticker zichtbaar zijn.

─────────────────────────────────────────────────────────────────────
Change Log (2.3)
─────────────────────────────────────────────────────────────────────

2026-04-18  CAT terminal venster toegevoegd
    - "Terminal" checkbox naast VFO-A/B label in het propagatie-paneel
    - Togglebaar: zichtbaar als CAT ingeschakeld én Terminal aangevinkt
    - Geel (▶) = verzonden commando's (FA;FB; poll, VS0;FA…; set)
    - Blauw (◀) = ontvangen data van de radio
    - Max 200 regels (auto-trim); Consolas 8pt monospace weergave

2026-04-18  CAT bugfix + VFO-A/B display in bandpaneel
    - _yaesu_set_freq: 9→11 cijfers, VS0; prepend, DTR/RTS=False (FT-950 correctie)
    - VFO-A/B label alleen zichtbaar als CAT ingeschakeld is in Setup
    - CAT polling elke 2s via FA;FB; → VFO-A (wit) en VFO-B (blauw) markers op bandbalken
    - _cat_poll_lock voorkomt conflict tussen poll-thread en klik-naar-afstemmen
    - _cat_vfo_a_hz bijgewerkt bij klik op bandbalk

2026-04-18  Spaans (Español) toegevoegd als zesde taal
    - _LANG_NAMES en _LANG_CODES uitgebreid met "Español" / "es"
    - Alle ~130 entries in _T vertaald naar het Spaans
    - _SOLAR_TIPS_LANG uitgebreid met Spaanse tooltip-teksten

2026-04-17 12:10  CAT-interface: klik-naar-afstemmen via serieel USB (Yaesu CAT)
    - _yaesu_set_freq: stuurt VS0;FA<9 digits>; naar VFO-A (FT-950 e.a.)
    - _kenwood_set_freq: FA<11 digits>; voor Kenwood/Elecraft
    - _icom_set_freq: CI-V binair BCD, instelbaar adres
    - CAT-dialoog: radio-type dropdown + CI-V adresveld; volledig vertaald (5 talen)
    - Cursor verandert naar hand2 bij hover over bandbalken
    - Klik op een bandbalk stuurt de startfrequentie naar de radio

2026-04-17 12:35  CAT verbeteringen
    - VS0; prepend fix voor FT-950 (radio bleef in geheugen/split-modus)
    - Alle CAT-dialoogteksten vertaald in NL/EN/DE/FR/IT via _T-systeem

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
import queue as _queue
import datetime
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
try:
    from PIL import Image, ImageDraw, ImageTk
    _PIL_OK = True
except ImportError:
    _PIL_OK = False
try:
    import serial
    import serial.tools.list_ports
    _SERIAL_OK = True
except ImportError:
    _SERIAL_OK = False

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
ADV_CARD_H   = 74    # vaste hoogte per advieskaart (pixels)
ADV_CARD_GAP = 4    # verticale ruimte tussen rijen
ADV_ROWS     = 4    # zichtbare rijen bij opstarten

# ── Vaste hoogte-constanten (gebruikt voor fixed-height frames en _center_window) ──
TICKER_H      = 22   # hoogte ticker-balk
APP_HDR_H     = 42   # hoogte app-header balk

# Advies-sectie: accent (2) + header-rij pady+label (28–32px, afhankelijk van fontschaling)
# + kaartgebied + ondermarge (8). ADV_HDR_STRIP=40 geeft ~10px buffer voor fontmetrieken.
ADV_HDR_STRIP  = 40
ADV_SECTION_H  = ADV_HDR_STRIP + ADV_ROWS * (ADV_CARD_H + ADV_CARD_GAP) + 8

# Solar-paneel minimum: solar_col-header(32) + param-rijen+K-alert(214) +
#   band-tabel header+11bands(196) + sep(11) + x-flare h=3(44) + PCA h=2(32) = 529
#   → royale buffer → 700px zodat alles ruim zichtbaar is.
SOLAR_MIN_H   = 700

# Minimale venster-hoogte zodat alles zichtbaar is bij opstarten:
#   app-header + solar-paneel (bepaalt top_row hoogte) + outer-pady(6) +
#   advies-sectie + body-ondermarge(4) + ticker
MIN_WINDOW_H  = APP_HDR_H + SOLAR_MIN_H + 6 + ADV_SECTION_H + 4 + TICKER_H

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
        "show_ticker":   cfg.getboolean("App",   "show_ticker",    fallback=True),
        "language":      cfg.get       ("App",   "language",       fallback="Nederlands"),
        "show_sun":      cfg.getboolean("Map",   "show_sun",       fallback=True),
        "show_moon":     cfg.getboolean("Map",   "show_moon",      fallback=True),
        "show_locator":  cfg.getboolean("Map",   "show_locator",   fallback=False),
        "show_graylijn": cfg.getboolean("Map",   "show_graylijn",  fallback=True),
        "show_iaru":     cfg.getboolean("Map",   "show_iaru",      fallback=False),
        "show_cs":       cfg.getboolean("Map",   "show_cs",        fallback=False),
        "show_spots":    cfg.getboolean("Map",   "show_spots",     fallback=False),
        "show_wspr":     cfg.getboolean("Map",   "show_wspr",      fallback=False),
        "hist_range":    cfg.get       ("Graph", "hist_range",     fallback="Uren"),
        "hist_sel":      set(hist_sel_raw.split(",")) - {""} if hist_sel_raw else set(),
        "k_alert":       cfg.getint   ("Alerts","k_alert",        fallback=4),
        # CAT interface
        "cat_port":      cfg.get      ("CAT",   "port",           fallback=""),
        "cat_baud":      cfg.get      ("CAT",   "baud",           fallback="9600"),
        "cat_bits":      cfg.get      ("CAT",   "bits",           fallback="8"),
        "cat_parity":    cfg.get      ("CAT",   "parity",         fallback="N"),
        "cat_stopbits":  cfg.get      ("CAT",   "stopbits",       fallback="1"),
        "cat_flow":      cfg.get      ("CAT",   "flow",           fallback="Geen"),
        "cat_dtr":       cfg.getboolean("CAT",  "dtr",            fallback=False),
        "cat_rts":       cfg.getboolean("CAT",  "rts",            fallback=False),
        "cat_enabled":   cfg.getboolean("CAT",  "enabled",        fallback=False),
        "cat_radio":     cfg.get       ("CAT",  "radio",          fallback="Yaesu CAT"),
        "cat_civ_addr":  cfg.get       ("CAT",  "civ_addr",       fallback="0x70"),
    }

def _save_settings(lat: float, lon: float, refresh: str,
                   mode: str = "SSB", power: str = "100W",
                   antenna: str = "Isotropic 0dBi",
                   dst: bool = True, show_tips: bool = True,
                   show_ticker: bool = True,
                   show_sun: bool = True, show_moon: bool = True,
                   show_locator: bool = False,
                   show_graylijn: bool = True,
                   show_iaru: bool = False,
                   show_cs: bool = False,
                   show_spots: bool = False,
                   show_wspr: bool = False,
                   hist_range: str = "Uren",
                   hist_sel: set = None,
                   k_alert: int = 4,
                   language: str = "Nederlands",
                   cat_port: str = "", cat_baud: str = "9600",
                   cat_bits: str = "8", cat_parity: str = "N",
                   cat_stopbits: str = "1", cat_flow: str = "Geen",
                   cat_dtr: bool = False, cat_rts: bool = False,
                   cat_enabled: bool = False,
                   cat_radio: str = "Yaesu CAT",
                   cat_civ_addr: str = "0x70") -> None:
    cfg = configparser.ConfigParser()
    cfg["QTH"]   = {"lat": str(lat), "lon": str(lon)}
    cfg["App"]   = {"refresh": refresh, "mode": mode, "power": power,
                    "antenna": antenna, "dst": str(dst),
                    "show_tips": str(show_tips), "show_ticker": str(show_ticker),
                    "language": language}
    cfg["Map"]   = {"show_sun": str(show_sun), "show_moon": str(show_moon),
                    "show_locator": str(show_locator),
                    "show_graylijn": str(show_graylijn),
                    "show_iaru": str(show_iaru),
                    "show_cs": str(show_cs),
                    "show_spots": str(show_spots),
                    "show_wspr": str(show_wspr)}
    cfg["Graph"]  = {"hist_range": hist_range,
                     "selected_bands": ",".join(sorted(hist_sel)) if hist_sel else ""}
    cfg["Alerts"] = {"k_alert": str(k_alert)}
    cfg["CAT"]    = {"port": cat_port, "baud": cat_baud, "bits": cat_bits,
                     "parity": cat_parity, "stopbits": cat_stopbits,
                     "flow": cat_flow, "dtr": str(cat_dtr), "rts": str(cat_rts),
                     "enabled": str(cat_enabled),
                     "radio": cat_radio, "civ_addr": cat_civ_addr}
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)

# ── Solar data ophalen ─────────────────────────────────────────────────────────
SOLAR_URL    = "https://www.hamqsl.com/solarxml.php"
SW_SPEED_URL = "https://services.swpc.noaa.gov/products/summary/solar-wind-speed.json"
SW_MAG_URL   = "https://services.swpc.noaa.gov/products/summary/solar-wind-mag-field.json"
# GOES >10 MeV integraalproton flux — meest recente meting (laatste element in array)
# Formaat: [{time_tag, satellite, flux, channel}, ...] — channel "P5" = >10 MeV
PROTON_URL   = "https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json"
# GIRO/LGDC DIDBase — foF2 van Europese ionosondes
# Formaat antwoord: TSV met commentaarregels (#); kolommen: Time(UTC)  foF2  QD
IONO_URL     = ("https://lgdc.uml.edu/common/DIDBGetValues"
                "?ursiCode={code}&charName=foF2"
                "&fromDate={t_from}&toDate={t_to}")

# Europese ionosondes: (URSI-code, naam, lat, lon)
_IONO_STATIONS: list[tuple[str, str, float, float]] = [
    ("DB049", "Dourbes BE",    50.1,   4.6),
    ("JR055", "Juliusruh DE",  54.6,  13.4),
    ("EB040", "Ebro ES",       40.8,   0.5),
    ("AT138", "Athene GR",     38.0,  23.5),
    ("PQ052", "Průhonice CZ",  50.0,  14.6),
    ("RO041", "Rome IT",       41.9,  12.5),
]

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
        # ── Proton flux >10 MeV (GOES SWPC) ───────────────────────────────────
        # Primair: HamQSL XML 'protonflux' veld; backup: NOAA GOES JSON
        pf_hamqsl = sd.findtext("protonflux", "").strip()
        try:
            data["proton_flux"] = f"{float(pf_hamqsl):.2f}"
        except (ValueError, TypeError):
            # Fallback: NOAA GOES integraal-proton JSON
            try:
                with urllib.request.urlopen(PROTON_URL, timeout=6) as r:
                    pf_data = json.loads(r.read())
                # Zoek meest recente P5 (>10 MeV) of P3 entry
                pf_val = None
                if isinstance(pf_data, list):
                    # Formaat: lijst van dicts met 'channel' en 'flux'
                    # of 2D-array: [[time, p1, p2, p3, p4, p5, ...], ...]
                    for entry in reversed(pf_data):
                        if isinstance(entry, dict):
                            ch = entry.get("channel", "")
                            if ch in ("P5", "P3", ">10 MeV"):
                                v = entry.get("flux") or entry.get("observed_flux")
                                if v is not None:
                                    pf_val = float(v)
                                    break
                        elif isinstance(entry, list) and len(entry) >= 5:
                            # kolom 4 (index 3) is vaak >10 MeV in 2D array
                            try:
                                pf_val = float(entry[3])
                                break
                            except (ValueError, TypeError):
                                pass
                data["proton_flux"] = f"{pf_val:.2f}" if pf_val is not None else "—"
            except Exception:
                data["proton_flux"] = "—"
        return data
    except Exception as e:
        return {"error": str(e)}


def _band_cond(sd, band: str, time_of_day: str) -> str:
    for item in sd.findall("calculatedconditions/band"):
        if item.get("name") == band and item.get("time") == time_of_day:
            return (item.text or "—").strip()
    return "—"


# ── Ionosonde helpers ─────────────────────────────────────────────────────────
def _nearest_iono_station(lat: float, lon: float) -> tuple:
    """Geeft (ursi_code, naam, lat, lon) van de dichtstbijzijnde ionosonde."""
    best = _IONO_STATIONS[0]
    best_d = float("inf")
    for station in _IONO_STATIONS:
        dlat = station[2] - lat
        dlon = station[3] - lon
        d = dlat * dlat + dlon * dlon   # ruwe kwadratische afstand volstaat
        if d < best_d:
            best_d = d
            best = station
    return best


def _fetch_ionosonde(ursi_code: str) -> dict:
    """Haal meest recente foF2 op van de opgegeven GIRO/LGDC ionosonde.

    Geeft {'fof2': '4.50', 'time': '12:00', 'station': 'Dourbes BE'}
    of    {'fof2': '—', ...} bij fout/geen data.
    """
    station_name = next(
        (s[1] for s in _IONO_STATIONS if s[0] == ursi_code), ursi_code
    )
    try:
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        t_to    = now_utc.strftime("%Y-%m-%dT%H:%M:%S")
        t_from  = (now_utc - datetime.timedelta(hours=1, minutes=30)).strftime(
                      "%Y-%m-%dT%H:%M:%S")
        url = IONO_URL.format(code=ursi_code, t_from=t_from, t_to=t_to)
        req = urllib.request.Request(url, headers={"User-Agent": "HAMIOS/1.0"})
        with urllib.request.urlopen(req, timeout=9) as r:
            text = r.read().decode("utf-8", errors="replace")

        # TSV-respons: regels met # zijn commentaar; kolom 0 = tijd, kolom 1 = foF2
        fof2_val  = None
        time_str  = "—"
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            try:
                v = float(parts[1])
                if 1.0 <= v <= 22.0:      # sanity check: foF2 tussen 1 en 22 MHz
                    fof2_val = v
                    # Tijdstip uit ISO-formaat: "2024-01-01T12:00:00.000Z" → "12:00"
                    t_raw = parts[0]
                    t_part = t_raw.split("T")
                    time_str = t_part[1][:5] if len(t_part) > 1 else "—"
            except (ValueError, IndexError):
                pass

        if fof2_val is not None:
            return {"fof2": f"{fof2_val:.2f}", "time": time_str,
                    "station": station_name}
        return {"fof2": "—", "time": "—", "station": station_name}
    except Exception:
        return {"fof2": "—", "time": "—", "station": station_name}


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

# ── DX-spot kaartoverlay ──────────────────────────────────────────────────────
_SPOT_BAND_CLR: dict[str, str] = {
    "160m": "#FF4444", "80m": "#FF8800", "60m": "#FFDD00",
    "40m":  "#88CC00", "30m": "#00CC44", "20m": "#00BBFF",
    "17m":  "#0088FF", "15m": "#4466FF", "12m": "#9944FF",
    "10m":  "#DD44FF", "6m":  "#FF44CC",
}

def _prefix_latlon(callsign: str) -> tuple[float, float] | None:
    """Geef de DXCC-centroïde (lat, lon) voor een callsign, of None als onbekend."""
    cs = callsign.upper().lstrip("/")
    # Strip /P /M /MM suffix
    if "/" in cs:
        cs = cs.split("/")[0]
    best_lat, best_lon, best_len = None, None, 0
    for prefix, lat, lon in _CS_PREFIXES:
        if cs.startswith(prefix) and len(prefix) > best_len:
            best_lat, best_lon, best_len = lat, lon, len(prefix)
    return (best_lat, best_lon) if best_len else None

_REFRESH_OPTIONS = {
    "Uit": 0, "30s": 30, "1 min": 60, "5 min": 300,
    "10 min": 600, "30 min": 1800, "1 uur": 3600,
}

# ── Taal / Language ────────────────────────────────────────────────────────────
_LANG_NAMES = ["Nederlands", "English", "Deutsch", "Français", "Italiano", "Español"]
_LANG_CODES = {"Nederlands": "nl", "English": "en", "Deutsch": "de",
               "Français": "fr", "Italiano": "it", "Español": "es"}

_T: dict[str, dict[str, str]] = {
    # ── Header ────────────────────────────────────────────────────────────────
    "exit":        {"nl": "Afsluiten",   "en": "Exit",          "de": "Beenden",     "fr": "Quitter",       "it": "Esci",           "es": "Salir"},
    "summer_time": {"nl": "Zomertijd",   "en": "Summer time",   "de": "Sommerzeit",  "fr": "Heure d'été",   "it": "Ora legale",     "es": "Hora de verano"},
    "tooltips":    {"nl": "Tooltips",    "en": "Tooltips",      "de": "Tooltips",    "fr": "Infobulles",    "it": "Suggerimenti",   "es": "Información"},
    "ticker":      {"nl": "Ticker",      "en": "Ticker",        "de": "Laufband",    "fr": "Défilant",      "it": "Ticker",         "es": "Ticker"},
    "auto_lbl":    {"nl": "Auto:",       "en": "Auto:",         "de": "Auto:",       "fr": "Auto:",         "it": "Auto:",          "es": "Auto:"},
    "lang_lbl":    {"nl": "Taal:",       "en": "Lang:",         "de": "Sprache:",    "fr": "Langue:",       "it": "Lingua:",        "es": "Idioma:"},
    "qth_lat_lbl": {"nl": "QTH  Lat:",   "en": "QTH  Lat:",     "de": "QTH  Br:",    "fr": "QTH  Lat:",     "it": "QTH  Lat:",      "es": "QTH  Lat:"},
    "lon_lbl":     {"nl": "Lon:",        "en": "Lon:",          "de": "Lg:",         "fr": "Lon:",          "it": "Lon:",           "es": "Lon:"},
    # ── Panel titels ──────────────────────────────────────────────────────────
    "worldmap":    {"nl": "🌍  Wereldkaart",         "en": "🌍  World Map",             "de": "🌍  Weltkarte",           "fr": "🌍  Carte du monde",          "it": "🌍  Planisfero",                "es": "🌍  Mapa mundial"},
    "solar":       {"nl": "☀  Solar / Ionosfeer",    "en": "☀  Solar / Ionosphere",    "de": "☀  Solar / Ionosphäre",  "fr": "☀  Solaire / Ionosphère",    "it": "☀  Solare / Ionosfera",         "es": "☀  Solar / Ionosfera"},
    "reliability": {"nl": "📻  HF Betrouwbaarheid",  "en": "📻  HF Reliability",        "de": "📻  KW-Zuverlässigkeit", "fr": "📻  Fiabilité HF",            "it": "📻  Affidabilità HF",           "es": "📻  Fiabilidad HF"},
    "schedule":    {"nl": "📅  Bandopenings-schema", "en": "📅  Band Opening Schedule", "de": "📅  Bandöffnungsplan",   "fr": "📅  Planning des ouvertures", "it": "📅  Aperture di banda",         "es": "📅  Horario de bandas"},
    "history":     {"nl": "📈  Band Verloop",         "en": "📈  Band History",          "de": "📈  Bandverlauf",        "fr": "📈  Historique des bandes",   "it": "📈  Storico bande",             "es": "📈  Historial de bandas"},
    "dx_spots":    {"nl": "📡  DX Spots",             "en": "📡  DX Spots",              "de": "📡  DX-Spots",           "fr": "📡  DX Spots",                "it": "📡  DX Spots",                  "es": "📡  DX Spots"},
    "advice":      {"nl": "💡  Propagatie Advies",    "en": "💡  Propagation Advice",    "de": "💡  Ausbreitungshinweise","fr": "💡  Conseils de propagation", "it": "💡  Consigli propagazione",     "es": "💡  Consejos de propagación"},
    # Panel titels (uitgebreid)
    "prop_header":  {"nl": "📶  HF Band Betrouwbaarheid",                "en": "📶  HF Band Reliability",                   "de": "📶  KW-Band-Zuverlässigkeit",             "fr": "📶  Fiabilité des bandes HF",              "it": "📶  Affidabilità bande HF",          "es": "📶  Fiabilidad de bandas HF"},
    "hist_header":  {"nl": "📈  Band Verloop",                           "en": "📈  Band History",                           "de": "📈  Bandverlauf",                         "fr": "📈  Historique des bandes",                "it": "📈  Storico bande",                  "es": "📈  Historial de bandas"},
    "sched_header": {"nl": "🕐  Bandopenings-schema (lokale tijd, vandaag)", "en": "🕐  Band Opening Schedule (local time, today)", "de": "🕐  Bandöffnungsplan (Lokalzeit, heute)", "fr": "🕐  Ouvertures (heure locale, auj.)",      "it": "🕐  Aperture banda (ora locale, oggi)", "es": "🕐  Horario de bandas (hora local, hoy)"},
    "dx_header":    {"nl": "📡  Live DX Spots (HF)",                    "en": "📡  Live DX Spots (HF)",                    "de": "📡  Live DX-Spots (KW)",                 "fr": "📡  DX Spots en direct (HF)",              "it": "📡  DX Spots in diretta (HF)",       "es": "📡  DX Spots en vivo (HF)"},
    "adv_header":   {"nl": "💡  Propagatie-analyse & Advies",            "en": "💡  Propagation Analysis & Advice",         "de": "💡  Ausbreitungsanalyse & Hinweise",     "fr": "💡  Analyse & Conseils de propagation",   "it": "💡  Analisi & Consigli propagazione", "es": "💡  Análisis y consejos de propagación"},
    # ── Kaart checkboxes ──────────────────────────────────────────────────────
    "sun":         {"nl": "Zon",       "en": "Sun",        "de": "Sonne",     "fr": "Soleil",     "it": "Sole",         "es": "Sol"},
    "moon":        {"nl": "Maan",      "en": "Moon",       "de": "Mond",      "fr": "Lune",       "it": "Luna",         "es": "Luna"},
    "graylijn":    {"nl": "Graylijn",  "en": "Gray line",  "de": "Grauzone",  "fr": "Ligne grise","it": "Linea grigia",  "es": "Línea gris"},
    "locator":     {"nl": "Locator",   "en": "Locator",    "de": "Locator",   "fr": "Locator",    "it": "Locator",       "es": "Locator"},
    # ── Solar veld labels ─────────────────────────────────────────────────────
    "updated_lbl":  {"nl": "Bijgewerkt",  "en": "Updated",   "de": "Aktualisiert", "fr": "Mis à jour",  "it": "Aggiornato",  "es": "Actualizado"},
    "k_alert_lbl":  {"nl": "Melding K ≥", "en": "Alert K ≥", "de": "Alarm K ≥",   "fr": "Alerte K ≥", "it": "Avviso K ≥",  "es": "Alerta K ≥"},
    "day_hdr":      {"nl": "Dag",         "en": "Day",       "de": "Tag",          "fr": "Jour",        "it": "Giorno",      "es": "Día"},
    "night_hdr":    {"nl": "Nacht",       "en": "Night",     "de": "Nacht",        "fr": "Nuit",        "it": "Notte",       "es": "Noche"},
    "band_hdr":     {"nl": "Band",        "en": "Band",      "de": "Band",         "fr": "Bande",       "it": "Banda",       "es": "Banda"},
    # ── Prop panel labels ─────────────────────────────────────────────────────
    "mode_lbl":         {"nl": "Mode:",     "en": "Mode:",    "de": "Modus:",     "fr": "Mode:",      "it": "Modo:",             "es": "Modo:"},
    "power_lbl":        {"nl": "Vermogen:", "en": "Power:",   "de": "Leistung:",  "fr": "Puissance:", "it": "Potenza:",          "es": "Potencia:"},
    "ant_lbl":          {"nl": "Antenne:",  "en": "Antenna:", "de": "Antenne:",   "fr": "Antenne:",   "it": "Antenna:",          "es": "Antena:"},
    "day_auto":         {"nl": "Dag (auto)","en": "Day (auto)","de": "Tag (auto)","fr": "Jour (auto)","it": "Giorno (auto)",     "es": "Día (auto)"},
    "closed":           {"nl": "Gesloten",  "en": "Closed",   "de": "Geschlossen","fr": "Fermée",     "it": "Chiusa",            "es": "Cerrada"},
    "cond_good":        {"nl": "Goed",      "en": "Good",     "de": "Gut",        "fr": "Bon",        "it": "Buono",             "es": "Bueno"},
    "cond_fair":        {"nl": "Redelijk",  "en": "Fair",     "de": "Mäßig",      "fr": "Correct",    "it": "Discreto",          "es": "Regular"},
    "cond_poor":        {"nl": "Arm",       "en": "Poor",     "de": "Schlecht",   "fr": "Mauvais",    "it": "Scarso",            "es": "Malo"},
    "cond_closed":      {"nl": "Dicht",     "en": "Closed",   "de": "Geschlossen","fr": "Fermée",     "it": "Chiusa",            "es": "Cerrada"},
    "status_lbl":       {"nl": "Status:",         "en": "Status:",        "de": "Status:",      "fr": "État:",         "it": "Stato:",            "es": "Estado:"},
    "reason_lbl":       {"nl": "Reden:",           "en": "Reason:",        "de": "Grund:",       "fr": "Raison:",       "it": "Motivo:",           "es": "Motivo:"},
    "reason_muf_luf":   {"nl": "Boven MUF of onder LUF", "en": "Above MUF or below LUF", "de": "Über MUF oder unter LUF", "fr": "Au-dessus MUF ou sous LUF", "it": "Sopra MUF o sotto LUF", "es": "Por encima de MUF o por debajo de LUF"},
    "reliability_lbl":  {"nl": "Betrouwbaarheid:", "en": "Reliability:",   "de": "Zuverlässigkeit:", "fr": "Fiabilité:",  "it": "Affidabilità:",    "es": "Fiabilidad:"},
    "modes_lbl":        {"nl": "Modi:",            "en": "Modes:",         "de": "Modi:",        "fr": "Modes:",        "it": "Modi:",             "es": "Modos:"},
    "total_snr":        {"nl": "Totaal:",          "en": "Total:",         "de": "Gesamt:",      "fr": "Total:",        "it": "Totale:",           "es": "Total:"},
    "quality_lbl":      {"nl": "Kwaliteit:",       "en": "Quality:",       "de": "Qualität:",    "fr": "Qualité:",      "it": "Qualità:",          "es": "Calidad:"},
    "local_lbl":        {"nl": "lokaal",           "en": "local",          "de": "lokal",        "fr": "local",         "it": "locale",            "es": "local"},
    # ── Hist panel ────────────────────────────────────────────────────────────
    "hist_range_h": {"nl": "Uren",    "en": "Hours",   "de": "Stunden",  "fr": "Heures",   "it": "Ore",       "es": "Horas"},
    "hist_range_d": {"nl": "Dagen",   "en": "Days",    "de": "Tage",     "fr": "Jours",    "it": "Giorni",    "es": "Días"},
    "hist_range_w": {"nl": "Weken",   "en": "Weeks",   "de": "Wochen",   "fr": "Semaines", "it": "Settimane", "es": "Semanas"},
    "hist_range_m": {"nl": "Maanden", "en": "Months",  "de": "Monate",   "fr": "Mois",     "it": "Mesi",      "es": "Meses"},
    "no_hist_data": {"nl": "Nog geen historische data beschikbaar",
                     "en": "No historical data available yet",
                     "de": "Noch keine historischen Daten verfügbar",
                     "fr": "Pas encore de données historiques",
                     "it": "Nessun dato storico disponibile",
                     "es": "Aún no hay datos históricos disponibles"},
    "hist_tooltip_hdr": {"nl": "Band Verloop  —  {ts}",  "en": "Band History  —  {ts}",  "de": "Bandverlauf  —  {ts}",  "fr": "Historique  —  {ts}",  "it": "Storico  —  {ts}",  "es": "Historial de bandas  —  {ts}"},
    # ── DX panel ──────────────────────────────────────────────────────────────
    "own_cont_lbl":  {"nl": "Eigen continent",          "en": "Own continent",        "de": "Eigener Kontinent",    "fr": "Continent propre",       "it": "Continente proprio",         "es": "Continente propio"},
    "dx_loading":    {"nl": "Laden…",                   "en": "Loading…",             "de": "Laden…",               "fr": "Chargement…",            "it": "Caricamento…",               "es": "Cargando…"},
    "no_dx_spots":   {"nl": "Geen HF-spots beschikbaar","en": "No HF spots available","de": "Keine KW-Spots verfügbar","fr": "Aucun spot HF disponible","it": "Nessun spot HF disponibile", "es": "No hay spots HF disponibles"},
    "dx_of":         {"nl": "van",                      "en": "of",                   "de": "von",                  "fr": "sur",                    "it": "di",                         "es": "de"},
    "dx_own_cont_filter": {"nl": " · eigen continent",  "en": " · own continent",     "de": " · eigener Kontinent", "fr": " · continent propre",    "it": " · continente proprio",      "es": " · continente propio"},
    "no_spots_ts":   {"nl": "Geen spots beschikbaar  ·  {ts}", "en": "No spots available  ·  {ts}", "de": "Keine Spots verfügbar  ·  {ts}", "fr": "Aucun spot disponible  ·  {ts}", "it": "Nessun spot disponibile  ·  {ts}", "es": "Sin spots disponibles  ·  {ts}"},
    "dx_status_fmt": {"nl": "{n} van {total} spots  (HF{filt})  ·  {ts}", "en": "{n} of {total} spots  (HF{filt})  ·  {ts}", "de": "{n} von {total} Spots  (KW{filt})  ·  {ts}", "fr": "{n} sur {total} spots  (HF{filt})  ·  {ts}", "it": "{n} di {total} spot  (HF{filt})  ·  {ts}", "es": "{n} de {total} spots  (HF{filt})  ·  {ts}"},
    # ── Map panel ─────────────────────────────────────────────────────────────
    "map_nolib":       {"nl": "pip install pillow  voor kaartweergave",  "en": "pip install pillow  for map display",      "de": "pip install pillow  für Kartenanzeige",    "fr": "pip install pillow  pour afficher la carte", "it": "pip install pillow  per visualizzare la mappa", "es": "pip install pillow  para mostrar el mapa"},
    "map_downloading": {"nl": "⬇ NASA-kaart wordt gedownload…",         "en": "⬇ Downloading NASA map…",                 "de": "⬇ NASA-Karte wird heruntergeladen…",      "fr": "⬇ Téléchargement carte NASA…",               "it": "⬇ Download mappa NASA…",                        "es": "⬇ Descargando mapa NASA…"},
    "distance_lbl":    {"nl": "Afstand",  "en": "Distance",  "de": "Entfernung",  "fr": "Distance",   "it": "Distanza",   "es": "Distancia"},
    "direction_lbl":   {"nl": "Richting", "en": "Direction", "de": "Richtung",    "fr": "Direction",  "it": "Direzione",  "es": "Dirección"},
    "right_clk_clear": {"nl": "klik rechts om te wissen", "en": "right-click to clear", "de": "Rechtsklick zum Löschen", "fr": "clic droit pour effacer", "it": "clic destro per cancellare", "es": "clic derecho para borrar"},
    # ── Tray ──────────────────────────────────────────────────────────────────
    "tray_show": {"nl": "HAMIOS tonen",  "en": "Show HAMIOS",  "de": "HAMIOS anzeigen", "fr": "Afficher HAMIOS", "it": "Mostra HAMIOS",  "es": "Mostrar HAMIOS"},
    "tray_exit": {"nl": "Afsluiten",     "en": "Exit",         "de": "Beenden",         "fr": "Quitter",         "it": "Esci",           "es": "Salir"},
    # ── Xflare / PCA warnings ────────────────────────────────────────────────
    "xflare_warning": {"nl": "☢  SWF-waarschuwing: {xray}-flare gedetecteerd. HF dag-zijde verstoord (~{dur} min).",
                       "en": "☢  SWF warning: {xray} flare detected. HF dayside disrupted (~{dur} min).",
                       "de": "☢  SWF-Warnung: {xray}-Flare erkannt. KW-Tagseite gestört (~{dur} min).",
                       "fr": "☢  Alerte SWF: éruption {xray} détectée. HF côté jour perturbé (~{dur} min).",
                       "it": "☢  Avviso SWF: brillamento {xray} rilevato. HF lato giorno disturbato (~{dur} min).",
                       "es": "☢  Aviso SWF: destello {xray} detectado. HF lado diurno perturbado (~{dur} min)."},
    "xflare_notify_body": {"nl": "Short Wave Fadeout verwacht (~{dur} min). HF op dag-zijde tijdelijk verstoord.",
                           "en": "Short Wave Fadeout expected (~{dur} min). HF dayside temporarily disrupted.",
                           "de": "Short Wave Fadeout erwartet (~{dur} min). KW-Tagseite vorübergehend gestört.",
                           "fr": "Short Wave Fadeout attendu (~{dur} min). HF côté jour temporairement perturbé.",
                           "it": "Short Wave Fadeout atteso (~{dur} min). HF lato giorno temporaneamente disturbato.",
                           "es": "Short Wave Fadeout esperado (~{dur} min). HF lado diurno temporalmente perturbado."},
    "pca_warning": {"nl": "☢  PCA-waarschuwing S{s}: proton flux {pf:.1f} pfu — poolroutes geblokkeerd (~{dur}). 160m–40m poolpaden onbruikbaar.",
                    "en": "☢  PCA warning S{s}: proton flux {pf:.1f} pfu — polar routes blocked (~{dur}). 160m–40m polar paths unusable.",
                    "de": "☢  PCA-Warnung S{s}: Protonenfluss {pf:.1f} pfu — Polarrouten gesperrt (~{dur}). 160m–40m Polarwege unbrauchbar.",
                    "fr": "☢  Alerte PCA S{s}: flux proton {pf:.1f} pfu — routes polaires bloquées (~{dur}). 160m–40m inutilisables.",
                    "it": "☢  Avviso PCA S{s}: flusso protoni {pf:.1f} pfu — rotte polari bloccate (~{dur}). 160m–40m inutilizzabili.",
                    "es": "☢  Aviso PCA S{s}: flujo de protones {pf:.1f} pfu — rutas polares bloqueadas (~{dur}). 160m–40m rutas polares inutilizables."},
    "pca_dur_s5": {"nl": "3–7 dagen", "en": "3–7 days", "de": "3–7 Tage", "fr": "3–7 jours", "it": "3–7 giorni", "es": "3–7 días"},
    "pca_dur_s3": {"nl": "2–4 dagen", "en": "2–4 days", "de": "2–4 Tage", "fr": "2–4 jours", "it": "2–4 giorni", "es": "2–4 días"},
    "pca_dur_s1": {"nl": "1–2 dagen", "en": "1–2 days", "de": "1–2 Tage", "fr": "1–2 jours", "it": "1–2 giorni", "es": "1–2 días"},
    "pca_notify_body": {"nl": "Proton flux: {pf:.1f} pfu. Polar Cap Absorption — poolroutes geblokkeerd (~{dur}).",
                        "en": "Proton flux: {pf:.1f} pfu. Polar Cap Absorption — polar routes blocked (~{dur}).",
                        "de": "Protonenfluss: {pf:.1f} pfu. Polar Cap Absorption — Polarrouten gesperrt (~{dur}).",
                        "fr": "Flux proton: {pf:.1f} pfu. Polar Cap Absorption — routes polaires bloquées (~{dur}).",
                        "it": "Flusso protoni: {pf:.1f} pfu. Polar Cap Absorption — rotte polari bloccate (~{dur}).",
                        "es": "Flujo de protones: {pf:.1f} pfu. Polar Cap Absorption — rutas polares bloqueadas (~{dur})."},
    # ── K-alert notification ──────────────────────────────────────────────────
    "k_alert_notify_title": {"nl": "K-index {k} — geomagnetische activiteit",
                              "en": "K-index {k} — geomagnetic activity",
                              "de": "K-Index {k} — geomagnetische Aktivität",
                              "fr": "Indice K {k} — activité géomagnétique",
                              "it": "Indice K {k} — attività geomagnetica",
                              "es": "Índice K {k} — actividad geomagnética"},
    "k_alert_notify_body":  {"nl": "K={k}, A={a} — HF-propagatie verstoord. Lagere banden gebruiken.",
                              "en": "K={k}, A={a} — HF propagation disrupted. Use lower bands.",
                              "de": "K={k}, A={a} — KW-Ausbreitung gestört. Niedrige Bänder nutzen.",
                              "fr": "K={k}, A={a} — propagation HF perturbée. Utiliser les bandes basses.",
                              "it": "K={k}, A={a} — propagazione HF disturbata. Usare le bande basse.",
                              "es": "K={k}, A={a} — propagación HF perturbada. Usar bandas bajas."},
    # ── Geo-condities kwaliteitswoorden ──────────────────────────────────────
    "geo_quiet":        {"nl": "rustig",        "en": "quiet",       "de": "ruhig",        "fr": "calme",        "it": "tranquillo",     "es": "tranquilo"},
    "geo_unsettled":    {"nl": "onrustig",       "en": "unsettled",   "de": "unruhig",      "fr": "agité",        "it": "agitato",        "es": "agitado"},
    "geo_storm":        {"nl": "storm",          "en": "storm",       "de": "Sturm",        "fr": "tempête",      "it": "tempesta",       "es": "tormenta"},
    "geo_severe":       {"nl": "ernstige storm", "en": "severe storm","de": "schwerer Sturm","fr": "grave tempête","it": "grave tempesta", "es": "tormenta severa"},
    # ── Overall score labels ──────────────────────────────────────────────────
    "score_excellent":  {"nl": "Uitstekend 🏆", "en": "Excellent 🏆", "de": "Ausgezeichnet 🏆", "fr": "Excellent 🏆",   "it": "Eccellente 🏆",  "es": "Excelente 🏆"},
    "score_good":       {"nl": "Goed ✅",        "en": "Good ✅",      "de": "Gut ✅",            "fr": "Bon ✅",          "it": "Buono ✅",        "es": "Bueno ✅"},
    "score_fair":       {"nl": "Matig ⚡",       "en": "Fair ⚡",      "de": "Mäßig ⚡",          "fr": "Médiocre ⚡",     "it": "Mediocre ⚡",     "es": "Regular ⚡"},
    "score_poor":       {"nl": "Slecht ⚠️",      "en": "Poor ⚠️",     "de": "Schlecht ⚠️",       "fr": "Mauvais ⚠️",     "it": "Scarso ⚠️",      "es": "Malo ⚠️"},
    "day_label":        {"nl": "Dag",            "en": "Day",          "de": "Tag",               "fr": "Jour",           "it": "Giorno",          "es": "Día"},
    "night_label":      {"nl": "Nacht",          "en": "Night",        "de": "Nacht",             "fr": "Nuit",           "it": "Notte",           "es": "Noche"},
    # ── Trend direction ───────────────────────────────────────────────────────
    "trend_improving":    {"nl": "verbeterend",    "en": "improving",    "de": "verbessernd",    "fr": "en amélioration", "it": "in miglioramento",  "es": "mejorando"},
    "trend_worsening":    {"nl": "verslechterend", "en": "deteriorating","de": "verschlechternd","fr": "en dégradation",  "it": "in deterioramento", "es": "empeorando"},
    "avg_band_quality":   {"nl": "gemid. bandkwaliteit", "en": "avg. band quality", "de": "mittl. Bandqualität", "fr": "qual. moy. des bandes", "it": "qual. media bande", "es": "cal. prom. de bandas"},
    # ── Advice texts ──────────────────────────────────────────────────────────
    "adv_best_bands":   {"nl": "Beste banden nu:  {bstr}{extra}",
                         "en": "Best bands now:  {bstr}{extra}",
                         "de": "Beste Bänder jetzt:  {bstr}{extra}",
                         "fr": "Meilleures bandes:  {bstr}{extra}",
                         "it": "Migliori bande ora:  {bstr}{extra}",
                         "es": "Mejores bandas ahora:  {bstr}{extra}"},
    "adv_best_extra":   {"nl": "  ({n} banden open)",  "en": "  ({n} bands open)",  "de": "  ({n} Bänder offen)", "fr": "  ({n} bandes ouvertes)", "it": "  ({n} bande aperte)", "es": "  ({n} bandas abiertas)"},
    "adv_no_bands":     {"nl": "Alle HF-banden zijn momenteel gesloten.",
                         "en": "All HF bands are currently closed.",
                         "de": "Alle KW-Bänder sind derzeit geschlossen.",
                         "fr": "Toutes les bandes HF sont actuellement fermées.",
                         "it": "Tutte le bande HF sono attualmente chiuse.",
                         "es": "Todas las bandas HF están actualmente cerradas."},
    "adv_geo_severe":   {"nl": "Zware geomagnetische storm  K={k}, A={a} ({kwal}) — HF vrijwel onbruikbaar, auroraal absorptie op alle routes. Wacht op herstel (normaal binnen 12–24u).",
                         "en": "Severe geomagnetic storm  K={k}, A={a} ({kwal}) — HF almost unusable, auroral absorption on all routes. Wait for recovery (normally within 12–24h).",
                         "de": "Schwerer geomagnetischer Sturm  K={k}, A={a} ({kwal}) — KW kaum nutzbar, Polarlichtabsorption auf allen Routen. Auf Erholung warten (norm. innerhalb 12–24h).",
                         "fr": "Tempête géomagnétique sévère  K={k}, A={a} ({kwal}) — HF quasi inutilisable, absorption aurorale sur toutes les routes. Attendre la récupération (norm. 12–24h).",
                         "it": "Grave tempesta geomagnetica  K={k}, A={a} ({kwal}) — HF quasi inutilizzabile, assorbimento aurorale su tutte le rotte. Attendere il ripristino (norm. entro 12–24h).",
                         "es": "Tormenta geomagnética severa  K={k}, A={a} ({kwal}) — HF casi inutilizable, absorción auroral en todas las rutas. Esperar recuperación (normalmente en 12–24h)."},
    "adv_geo_storm":    {"nl": "Geomagnetische storm  K={k}, A={a} ({kwal}) — poolroutes geblokkeerd, 40m/80m meest betrouwbaar. Hoge banden en DX sterk verstoord.",
                         "en": "Geomagnetic storm  K={k}, A={a} ({kwal}) — polar routes blocked, 40m/80m most reliable. High bands and DX strongly disturbed.",
                         "de": "Geomagnetischer Sturm  K={k}, A={a} ({kwal}) — Polarrouten gesperrt, 40m/80m am zuverlässigsten. Hohe Bänder und DX stark gestört.",
                         "fr": "Tempête géomagnétique  K={k}, A={a} ({kwal}) — routes polaires bloquées, 40m/80m les plus fiables. Hautes bandes et DX fortement perturbés.",
                         "it": "Tempesta geomagnetica  K={k}, A={a} ({kwal}) — rotte polari bloccate, 40m/80m più affidabili. Bande alte e DX fortemente disturbati.",
                         "es": "Tormenta geomagnética  K={k}, A={a} ({kwal}) — rutas polares bloqueadas, 40m/80m más fiables. Bandas altas y DX muy perturbadas."},
    "adv_geo_elevated": {"nl": "Verhoogde geo-activiteit  K={k}, A={a} ({kwal}) — lagere banden stabieler; vermijd trans-polair DX. Overweeg 40m/80m voor betrouwbare verbindingen.",
                         "en": "Elevated geo-activity  K={k}, A={a} ({kwal}) — lower bands more stable; avoid trans-polar DX. Consider 40m/80m for reliable contacts.",
                         "de": "Erhöhte Geoaktivität  K={k}, A={a} ({kwal}) — niedrigere Bänder stabiler; Trans-Polar-DX meiden. 40m/80m für zuverlässige Verbindungen erwägen.",
                         "fr": "Activité géo élevée  K={k}, A={a} ({kwal}) — bandes basses plus stables; éviter le DX trans-polaire. Envisager 40m/80m pour des liaisons fiables.",
                         "it": "Attività geo elevata  K={k}, A={a} ({kwal}) — bande basse più stabili; evitare DX trans-polare. Considerare 40m/80m per collegamenti affidabili.",
                         "es": "Actividad geo elevada  K={k}, A={a} ({kwal}) — bandas bajas más estables; evitar DX trans-polar. Considerar 40m/80m para contactos fiables."},
    "adv_geo_quiet":    {"nl": "Rustige geo-condities  K={k}, A={a} — optimaal voor alle routes incl. poolpaden en DX.",
                         "en": "Quiet geo conditions  K={k}, A={a} — optimal for all routes incl. polar paths and DX.",
                         "de": "Ruhige Geobedingungen  K={k}, A={a} — optimal für alle Routen inkl. Polarwege und DX.",
                         "fr": "Conditions géo calmes  K={k}, A={a} — optimal pour toutes les routes incl. chemins polaires et DX.",
                         "it": "Condizioni geo tranquille  K={k}, A={a} — ottimale per tutte le rotte incl. percorsi polari e DX.",
                         "es": "Condiciones geo tranquilas  K={k}, A={a} — óptimo para todas las rutas incl. rutas polares y DX."},
    "adv_sol_exceptional": {"nl": "Exceptionele zonactiviteit  SFI={sfi}, SSN={ssn} — zonnecyclus-maximum. 10m/12m/15m open voor wereldwijd DX; kans op Es-versterking en TEP.",
                             "en": "Exceptional solar activity  SFI={sfi}, SSN={ssn} — solar cycle maximum. 10m/12m/15m open for worldwide DX; chance of Es enhancement and TEP.",
                             "de": "Außergewöhnliche Sonnenaktivität  SFI={sfi}, SSN={ssn} — Sonnenzyklusmaximum. 10m/12m/15m offen für weltweites DX; Es-Verstärkung und TEP möglich.",
                             "fr": "Activité solaire exceptionnelle  SFI={sfi}, SSN={ssn} — maximum du cycle solaire. 10m/12m/15m ouverts pour DX mondial; chance d'Es et TEP.",
                             "it": "Attività solare eccezionale  SFI={sfi}, SSN={ssn} — massimo del ciclo solare. 10m/12m/15m aperti per DX mondiale; possibilità di Es e TEP.",
                             "es": "Actividad solar excepcional  SFI={sfi}, SSN={ssn} — máximo del ciclo solar. 10m/12m/15m abiertos para DX mundial; posibilidad de Es y TEP."},
    "adv_sol_high":     {"nl": "Hoge zonactiviteit  SFI={sfi}, SSN={ssn} — uitstekend voor 10m t/m 17m DX. F2-propagatie sterk; MUF hoog, lange skips mogelijk.",
                         "en": "High solar activity  SFI={sfi}, SSN={ssn} — excellent for 10m to 17m DX. F2 propagation strong; MUF high, long skips possible.",
                         "de": "Hohe Sonnenaktivität  SFI={sfi}, SSN={ssn} — ausgezeichnet für 10m bis 17m DX. F2-Ausbreitung stark; MUF hoch, lange Sprünge möglich.",
                         "fr": "Forte activité solaire  SFI={sfi}, SSN={ssn} — excellent pour DX 10m à 17m. Propagation F2 forte; MUF élevée, longs sauts possibles.",
                         "it": "Alta attività solare  SFI={sfi}, SSN={ssn} — eccellente per DX 10m-17m. Propagazione F2 forte; MUF alta, salti lunghi possibili.",
                         "es": "Alta actividad solar  SFI={sfi}, SSN={ssn} — excelente para DX 10m a 17m. Propagación F2 fuerte; MUF alta, saltos largos posibles."},
    "adv_sol_good":     {"nl": "Goede zonactiviteit  SFI={sfi}, SSN={ssn} — 20m en 17m zijn primaire DX-banden; 15m kan open zijn. Verwacht betrouwbare F2-propagatie overdag.",
                         "en": "Good solar activity  SFI={sfi}, SSN={ssn} — 20m and 17m are primary DX bands; 15m may be open. Expect reliable F2 propagation during the day.",
                         "de": "Gute Sonnenaktivität  SFI={sfi}, SSN={ssn} — 20m und 17m sind primäre DX-Bänder; 15m kann offen sein. Zuverlässige F2-Ausbreitung tagsüber.",
                         "fr": "Bonne activité solaire  SFI={sfi}, SSN={ssn} — 20m et 17m sont les bandes DX primaires; 15m peut être ouverte. Propagation F2 fiable la journée.",
                         "it": "Buona attività solare  SFI={sfi}, SSN={ssn} — 20m e 17m sono le bande DX primarie; 15m potrebbe essere aperta. Propagazione F2 affidabile di giorno.",
                         "es": "Buena actividad solar  SFI={sfi}, SSN={ssn} — 20m y 17m son las bandas DX principales; 15m puede estar abierta. Propagación F2 fiable durante el día."},
    "adv_sol_moderate": {"nl": "Matige zonactiviteit  SFI={sfi}, SSN={ssn} — 20m/40m meest betrouwbaar. Hoge banden onzeker; 80m goed voor regionaal verkeer.",
                         "en": "Moderate solar activity  SFI={sfi}, SSN={ssn} — 20m/40m most reliable. High bands uncertain; 80m good for regional traffic.",
                         "de": "Mäßige Sonnenaktivität  SFI={sfi}, SSN={ssn} — 20m/40m am zuverlässigsten. Hohe Bänder unsicher; 80m gut für regionalen Verkehr.",
                         "fr": "Activité solaire modérée  SFI={sfi}, SSN={ssn} — 20m/40m les plus fiables. Hautes bandes incertaines; 80m bon pour trafic régional.",
                         "it": "Attività solare moderata  SFI={sfi}, SSN={ssn} — 20m/40m più affidabili. Bande alte incerte; 80m buono per traffico regionale.",
                         "es": "Actividad solar moderada  SFI={sfi}, SSN={ssn} — 20m/40m más fiables. Bandas altas inciertas; 80m buena para tráfico regional."},
    "adv_sol_low":      {"nl": "Lage zonactiviteit  SFI={sfi}, SSN={ssn} — 40m en 80m bieden meeste kans op verbindingen. Banden ≥15m grotendeels dicht; 160m voor nacht-DX.",
                         "en": "Low solar activity  SFI={sfi}, SSN={ssn} — 40m and 80m offer most chances. Bands ≥15m mostly closed; 160m for night DX.",
                         "de": "Niedrige Sonnenaktivität  SFI={sfi}, SSN={ssn} — 40m und 80m bieten die meisten Chancen. Bänder ≥15m größtenteils geschlossen; 160m für Nacht-DX.",
                         "fr": "Faible activité solaire  SFI={sfi}, SSN={ssn} — 40m et 80m offrent le plus de chances. Bandes ≥15m surtout fermées; 160m pour DX nocturne.",
                         "it": "Bassa attività solare  SFI={sfi}, SSN={ssn} — 40m e 80m offrono più possibilità. Bande ≥15m per lo più chiuse; 160m per DX notturno.",
                         "es": "Baja actividad solar  SFI={sfi}, SSN={ssn} — 40m y 80m ofrecen más posibilidades. Bandas ≥15m mayormente cerradas; 160m para DX nocturno."},
    "adv_sw_stormy":    {"nl": "Stormachtige solarwind  v={spd} km/s, Bz={bz} nT — verhoogde kans op CME-impact; K-index kan snel stijgen. Monitor condities actief.",
                         "en": "Stormy solar wind  v={spd} km/s, Bz={bz} nT — increased chance of CME impact; K-index may rise quickly. Monitor conditions actively.",
                         "de": "Stürmischer Sonnenwind  v={spd} km/s, Bz={bz} nT — erhöhte CME-Einschlagsgefahr; K-Index kann schnell steigen. Bedingungen aktiv überwachen.",
                         "fr": "Vent solaire tempétueux  v={spd} km/s, Bz={bz} nT — risque CME accru; K-index peut monter vite. Surveiller activement.",
                         "it": "Vento solare tempestoso  v={spd} km/s, Bz={bz} nT — aumento rischio CME; K-index può salire rapidamente. Monitorare le condizioni.",
                         "es": "Viento solar tormentoso  v={spd} km/s, Bz={bz} nT — mayor riesgo de impacto CME; índice K puede subir rápido. Monitorear condiciones activamente."},
    "adv_sw_elevated":  {"nl": "Verhoogde solarwind  v={spd} km/s, Bz={bz} nT — Bz negatief koppelt aan aardveld → K-stijging mogelijk. Lagere banden aanhouden.",
                         "en": "Elevated solar wind  v={spd} km/s, Bz={bz} nT — negative Bz couples to Earth's field → K-index rise possible. Stick to lower bands.",
                         "de": "Erhöhter Sonnenwind  v={spd} km/s, Bz={bz} nT — negatives Bz koppelt an Erdfeld → K-Anstieg möglich. Niedrigere Bänder bevorzugen.",
                         "fr": "Vent solaire élevé  v={spd} km/s, Bz={bz} nT — Bz négatif couplé au champ terrestre → hausse K possible. Rester sur les bandes basses.",
                         "it": "Vento solare elevato  v={spd} km/s, Bz={bz} nT — Bz negativo si accoppia al campo terrestre → possibile aumento K. Preferire le bande basse.",
                         "es": "Viento solar elevado  v={spd} km/s, Bz={bz} nT — Bz negativo se acopla al campo terrestre → posible aumento de K. Mantener bandas bajas."},
    "adv_sw_calm":      {"nl": "Rustige solarwind  v={spd} km/s, Bz={bz} nT — positieve Bz beschermt aardveld. Stabiele condities.",
                         "en": "Calm solar wind  v={spd} km/s, Bz={bz} nT — positive Bz shields Earth's field. Stable conditions.",
                         "de": "Ruhiger Sonnenwind  v={spd} km/s, Bz={bz} nT — positives Bz schützt Erdfeld. Stabile Bedingungen.",
                         "fr": "Vent solaire calme  v={spd} km/s, Bz={bz} nT — Bz positif protège le champ terrestre. Conditions stables.",
                         "it": "Vento solare calmo  v={spd} km/s, Bz={bz} nT — Bz positivo protegge il campo terrestre. Condizioni stabili.",
                         "es": "Viento solar tranquilo  v={spd} km/s, Bz={bz} nT — Bz positivo protege el campo terrestre. Condiciones estables."},
    "adv_sw_normal":    {"nl": "Normale solarwind  v={spd} km/s, Bz={bz} nT — geen direct effect op propagatie verwacht.",
                         "en": "Normal solar wind  v={spd} km/s, Bz={bz} nT — no direct effect on propagation expected.",
                         "de": "Normaler Sonnenwind  v={spd} km/s, Bz={bz} nT — kein direkter Einfluss auf die Ausbreitung erwartet.",
                         "fr": "Vent solaire normal  v={spd} km/s, Bz={bz} nT — aucun effet direct sur la propagation attendu.",
                         "it": "Vento solare normale  v={spd} km/s, Bz={bz} nT — nessun effetto diretto sulla propagazione atteso.",
                         "es": "Viento solar normal  v={spd} km/s, Bz={bz} nT — sin efecto directo en la propagación esperado."},
    "adv_pf_s5":        {"nl": "ERNSTIG proton event S5  ({pf} pfu) — Polar Cap Absorption actief. Alle poolroutes volledig geblokkeerd 3–7 dagen. Gebruik equatoriale paden (20m/17m).",
                         "en": "SEVERE proton event S5  ({pf} pfu) — Polar Cap Absorption active. All polar routes fully blocked 3–7 days. Use equatorial paths (20m/17m).",
                         "de": "SCHWERES Proton-Event S5  ({pf} pfu) — Polar Cap Absorption aktiv. Alle Polarrouten 3–7 Tage vollständig gesperrt. Äquatorialwege nutzen (20m/17m).",
                         "fr": "Événement proton GRAVE S5  ({pf} pfu) — Absorption Polaire active. Toutes les routes polaires bloquées 3–7 jours. Utiliser les chemins équatoriaux (20m/17m).",
                         "it": "Evento protonico GRAVE S5  ({pf} pfu) — Polar Cap Absorption attiva. Tutte le rotte polari bloccate 3–7 giorni. Usare percorsi equatoriali (20m/17m).",
                         "es": "Evento de protones GRAVE S5  ({pf} pfu) — Polar Cap Absorption activa. Todas las rutas polares bloqueadas 3–7 días. Usar rutas ecuatoriales (20m/17m)."},
    "adv_pf_s3":        {"nl": "Proton event S3  ({pf} pfu) — PCA actief: poolroutes (EU→JA/W via pool) geblokkeerd 2–4 dagen. 160m/80m/40m poolpaden onbruikbaar.",
                         "en": "Proton event S3  ({pf} pfu) — PCA active: polar routes (EU→JA/W via pole) blocked 2–4 days. 160m/80m/40m polar paths unusable.",
                         "de": "Proton-Event S3  ({pf} pfu) — PCA aktiv: Polarrouten (EU→JA/W via Pol) 2–4 Tage gesperrt. 160m/80m/40m Polarwege unbrauchbar.",
                         "fr": "Événement proton S3  ({pf} pfu) — PCA actif: routes polaires (EU→JA/W via pôle) bloquées 2–4 jours. 160m/80m/40m inutilisables.",
                         "it": "Evento protonico S3  ({pf} pfu) — PCA attiva: rotte polari (EU→JA/W via polo) bloccate 2–4 giorni. 160m/80m/40m percorsi polari inutilizzabili.",
                         "es": "Evento de protones S3  ({pf} pfu) — PCA activa: rutas polares (EU→JA/W via polo) bloqueadas 2–4 días. 160m/80m/40m rutas polares inutilizables."},
    "adv_pf_s1":        {"nl": "Verhoogde proton flux S1  ({pf} pfu) — PCA begint mogelijk. Monitor poolroutes op 40m. Kans op verdere escalatie bij actieve vlammenactiviteit.",
                         "en": "Elevated proton flux S1  ({pf} pfu) — PCA may begin. Monitor polar routes on 40m. Chance of further escalation with active flare activity.",
                         "de": "Erhöhter Protonenfluss S1  ({pf} pfu) — PCA kann beginnen. Polarrouten auf 40m überwachen. Chance auf weitere Eskalation bei Flares.",
                         "fr": "Flux proton élevé S1  ({pf} pfu) — PCA peut commencer. Surveiller les routes polaires sur 40m. Risque d'escalade en cas d'éruptions.",
                         "it": "Flusso protonico elevato S1  ({pf} pfu) — PCA può iniziare. Monitorare le rotte polari su 40m. Possibilità di escalation con brillamenti attivi.",
                         "es": "Flujo de protones elevado S1  ({pf} pfu) — PCA puede comenzar. Monitorear rutas polares en 40m. Posibilidad de escalada con actividad de destellos."},
    "adv_pf_normal":    {"nl": "Proton flux normaal  ({pf} pfu) — geen Polar Cap Absorption. Poolroutes niet door proton flux beïnvloed.",
                         "en": "Proton flux normal  ({pf} pfu) — no Polar Cap Absorption. Polar routes unaffected by proton flux.",
                         "de": "Protonenfluss normal  ({pf} pfu) — keine Polar Cap Absorption. Polarrouten nicht durch Protonenfluss beeinflusst.",
                         "fr": "Flux proton normal  ({pf} pfu) — pas d'absorption polaire. Routes polaires non affectées par le flux proton.",
                         "it": "Flusso protonico normale  ({pf} pfu) — nessuna Polar Cap Absorption. Rotte polari non influenzate dal flusso protonico.",
                         "es": "Flujo de protones normal  ({pf} pfu) — sin Polar Cap Absorption. Rutas polares no afectadas por flujo de protones."},
    "adv_xflare_x":     {"nl": "X-flare gedetecteerd  ({xray}) — Short Wave Fadeout (SWF) mogelijk op dag-zijde; HF tijdelijk geblokkeerd. Herstel verwacht binnen 15–60 min.",
                         "en": "X-flare detected  ({xray}) — Short Wave Fadeout (SWF) possible on dayside; HF temporarily blocked. Recovery expected within 15–60 min.",
                         "de": "X-Flare erkannt  ({xray}) — Short Wave Fadeout (SWF) auf der Tagseite möglich; KW vorübergehend blockiert. Erholung in 15–60 min erwartet.",
                         "fr": "Éruption X détectée  ({xray}) — Short Wave Fadeout (SWF) possible côté jour; HF temporairement bloqué. Rétablissement dans 15–60 min.",
                         "it": "Brillamento X rilevato  ({xray}) — Short Wave Fadeout (SWF) possibile sul lato giorno; HF temporaneamente bloccato. Ripristino entro 15–60 min.",
                         "es": "Destello X detectado  ({xray}) — Short Wave Fadeout (SWF) posible en el lado diurno; HF temporalmente bloqueado. Recuperación esperada en 15–60 min."},
    "adv_xflare_m":     {"nl": "M-flare actief  ({xray}) — lichte SWF mogelijk op lagere HF. Verhoogde kans op Proton Event (PCA) bij M5+.",
                         "en": "M-flare active  ({xray}) — minor SWF possible on lower HF. Increased chance of Proton Event (PCA) at M5+.",
                         "de": "M-Flare aktiv  ({xray}) — leichter SWF auf niedrigem KW möglich. Erhöhte Chance auf Proton-Event (PCA) bei M5+.",
                         "fr": "Éruption M active  ({xray}) — SWF léger possible sur HF bas. Risque accru d'événement proton (PCA) à M5+.",
                         "it": "Brillamento M attivo  ({xray}) — SWF lieve possibile sulle HF basse. Aumento rischio Proton Event (PCA) a M5+.",
                         "es": "Destello M activo  ({xray}) — SWF leve posible en HF bajas. Mayor riesgo de Evento de Protones (PCA) en M5+."},
    "adv_muf_28":       {"nl": "MUF={muf} MHz — 10m t/m 20m alle open; F2-laag optimaal",
                         "en": "MUF={muf} MHz — 10m through 20m all open; F2 layer optimal",
                         "de": "MUF={muf} MHz — 10m bis 20m alle offen; F2-Schicht optimal",
                         "fr": "MUF={muf} MHz — 10m à 20m toutes ouvertes; couche F2 optimale",
                         "it": "MUF={muf} MHz — da 10m a 20m tutte aperte; strato F2 ottimale",
                         "es": "MUF={muf} MHz — 10m a 20m todos abiertos; capa F2 óptima"},
    "adv_muf_14":       {"nl": "MUF={muf} MHz — 20m open; banden > {muf0} MHz dicht",
                         "en": "MUF={muf} MHz — 20m open; bands > {muf0} MHz closed",
                         "de": "MUF={muf} MHz — 20m offen; Bänder > {muf0} MHz geschlossen",
                         "fr": "MUF={muf} MHz — 20m ouverte; bandes > {muf0} MHz fermées",
                         "it": "MUF={muf} MHz — 20m aperta; bande > {muf0} MHz chiuse",
                         "es": "MUF={muf} MHz — 20m abierta; bandas > {muf0} MHz cerradas"},
    "adv_muf_7":        {"nl": "MUF={muf} MHz — alleen 40m–80m bruikbaar",
                         "en": "MUF={muf} MHz — only 40m–80m usable",
                         "de": "MUF={muf} MHz — nur 40m–80m nutzbar",
                         "fr": "MUF={muf} MHz — seulement 40m–80m utilisables",
                         "it": "MUF={muf} MHz — solo 40m–80m utilizzabili",
                         "es": "MUF={muf} MHz — solo 40m–80m utilizables"},
    "adv_muf_low":      {"nl": "MUF={muf} MHz — ionosfeer zwak; alleen 80m/160m",
                         "en": "MUF={muf} MHz — ionosphere weak; only 80m/160m",
                         "de": "MUF={muf} MHz — Ionosphäre schwach; nur 80m/160m",
                         "fr": "MUF={muf} MHz — ionosphère faible; seulement 80m/160m",
                         "it": "MUF={muf} MHz — ionosfera debole; solo 80m/160m",
                         "es": "MUF={muf} MHz — ionosfera débil; solo 80m/160m"},
    "adv_iono_fmt":     {"nl": "Ionosfeer: {muf_txt}. Geschatte LUF ≈ {luf} MHz ({luf_note}).",
                         "en": "Ionosphere: {muf_txt}. Estimated LUF ≈ {luf} MHz ({luf_note}).",
                         "de": "Ionosphäre: {muf_txt}. Geschätzte LUF ≈ {luf} MHz ({luf_note}).",
                         "fr": "Ionosphère: {muf_txt}. LUF estimée ≈ {luf} MHz ({luf_note}).",
                         "it": "Ionosfera: {muf_txt}. LUF stimata ≈ {luf} MHz ({luf_note}).",
                         "es": "Ionosfera: {muf_txt}. LUF estimada ≈ {luf} MHz ({luf_note})."},
    "adv_luf_elevated": {"nl": "verhoogd door K-index", "en": "elevated by K-index", "de": "durch K-Index erhöht", "fr": "élevée par K-index", "it": "elevata dall'indice K", "es": "elevada por índice K"},
    "adv_luf_normal":   {"nl": "normaal",               "en": "normal",              "de": "normal",               "fr": "normal",              "it": "normale",              "es": "normal"},
    "adv_morning":      {"nl": "Ochtend ({h}:xx lokaal) — F2-laag bouwt op; 20m wordt snel bruikbaar. Grey-line kansen voor DX-paden richting Amerika en Azië.",
                         "en": "Morning ({h}:xx local) — F2 layer building up; 20m becoming usable quickly. Grey-line chances for DX paths towards America and Asia.",
                         "de": "Morgen ({h}:xx lokal) — F2-Schicht baut sich auf; 20m wird schnell nutzbar. Grauzonenchancen für DX-Wege in Richtung Amerika und Asien.",
                         "fr": "Matin ({h}:xx local) — couche F2 en formation; 20m bientôt utilisable. Opportunités grey-line vers l'Amérique et l'Asie.",
                         "it": "Mattino ({h}:xx locale) — strato F2 in formazione; 20m presto utilizzabile. Opportunità grey-line verso America e Asia.",
                         "es": "Mañana ({h}:xx local) — capa F2 formándose; 20m pronto utilizable. Oportunidades grey-line para rutas DX hacia América y Asia."},
    "adv_midday":       {"nl": "Middag ({h}:xx lokaal) — F2 op maximale hoogte; beste window voor 15m/17m/20m DX. Probeer SSB of FT8 voor trans-Atlantische verbindingen.",
                         "en": "Midday ({h}:xx local) — F2 at maximum height; best window for 15m/17m/20m DX. Try SSB or FT8 for trans-Atlantic contacts.",
                         "de": "Mittag ({h}:xx lokal) — F2 auf maximaler Höhe; bestes Fenster für 15m/17m/20m DX. SSB oder FT8 für Transatlantik-Verbindungen.",
                         "fr": "Midi ({h}:xx local) — F2 à son maximum; meilleure fenêtre pour DX 15m/17m/20m. Essayer SSB ou FT8 pour liaisons transatlantiques.",
                         "it": "Mezzogiorno ({h}:xx locale) — F2 al massimo; miglior finestra per DX 15m/17m/20m. Prova SSB o FT8 per collegamenti transatlantici.",
                         "es": "Mediodía ({h}:xx local) — F2 en su máximo; mejor ventana para DX 15m/17m/20m. Probar SSB o FT8 para contactos transatlánticos."},
    "adv_afternoon":    {"nl": "Namiddag ({h}:xx lokaal) — Grey-line nadert; uitstekend voor DX richting Azië en Pacific. 15m en 17m vaak prachtig in deze uren.",
                         "en": "Afternoon ({h}:xx local) — Grey-line approaching; excellent for DX towards Asia and Pacific. 15m and 17m often excellent at this time.",
                         "de": "Nachmittag ({h}:xx lokal) — Grauzone nähert sich; ausgezeichnet für DX in Richtung Asien und Pazifik. 15m und 17m oft hervorragend.",
                         "fr": "Après-midi ({h}:xx local) — Grey-line approche; excellent pour DX vers l'Asie et le Pacifique. 15m et 17m souvent superbes.",
                         "it": "Pomeriggio ({h}:xx locale) — Grey-line in avvicinamento; eccellente per DX verso Asia e Pacifico. 15m e 17m spesso ottimi.",
                         "es": "Tarde ({h}:xx local) — Grey-line aproximándose; excelente para DX hacia Asia y Pacífico. 15m y 17m a menudo excelentes en estas horas."},
    "adv_early_night":  {"nl": "Vroege nacht ({h}:xx lokaal) — 40m en 80m open voor regionaal Europa-verkeer. F2-laag daalt; LUF stijgt op korte paden.",
                         "en": "Early night ({h}:xx local) — 40m and 80m open for regional European traffic. F2 layer falling; LUF rising on short paths.",
                         "de": "Frühe Nacht ({h}:xx lokal) — 40m und 80m offen für regionalen Europa-Verkehr. F2-Schicht sinkt; LUF steigt auf kurzen Wegen.",
                         "fr": "Début de nuit ({h}:xx local) — 40m et 80m ouverts pour trafic régional européen. Couche F2 en baisse; LUF monte sur courts trajets.",
                         "it": "Prima notte ({h}:xx locale) — 40m e 80m aperti per traffico regionale europeo. Strato F2 in discesa; LUF in aumento su percorsi brevi.",
                         "es": "Primera noche ({h}:xx local) — 40m y 80m abiertos para tráfico regional europeo. Capa F2 bajando; LUF subiendo en rutas cortas."},
    "adv_night":        {"nl": "Nacht ({h}:xx lokaal) — 160m en 80m actief voor trans-Atlantisch DX. 40m goed voor Noord-Amerika. FT8 op lage banden voor DX-afstanden > 5000 km.",
                         "en": "Night ({h}:xx local) — 160m and 80m active for trans-Atlantic DX. 40m good for North America. FT8 on low bands for DX distances > 5000 km.",
                         "de": "Nacht ({h}:xx lokal) — 160m und 80m aktiv für transatlantisches DX. 40m gut für Nordamerika. FT8 auf niedrigen Bändern für DX > 5000 km.",
                         "fr": "Nuit ({h}:xx local) — 160m et 80m actifs pour DX transatlantique. 40m bon pour l'Amérique du Nord. FT8 sur bandes basses pour DX > 5000 km.",
                         "it": "Notte ({h}:xx locale) — 160m e 80m attivi per DX transatlantico. 40m buono per il Nord America. FT8 sulle bande basse per DX > 5000 km.",
                         "es": "Noche ({h}:xx local) — 160m y 80m activos para DX transatlántico. 40m buena para América del Norte. FT8 en bandas bajas para DX > 5000 km."},
    "adv_pre_morning":  {"nl": "Voor de ochtend ({h}:xx lokaal) — Grey-line nadert; 80m/40m DX-window naar Azië/Pacific. 20m begint te openen richting Amerika.",
                         "en": "Pre-dawn ({h}:xx local) — Grey-line approaching; 80m/40m DX window towards Asia/Pacific. 20m starting to open towards America.",
                         "de": "Vor dem Morgen ({h}:xx lokal) — Grauzone nähert sich; 80m/40m DX-Fenster nach Asien/Pazifik. 20m beginnt sich in Richtung Amerika zu öffnen.",
                         "fr": "Avant l'aube ({h}:xx local) — Grey-line approche; fenêtre DX 80m/40m vers Asie/Pacifique. 20m commence à s'ouvrir vers l'Amérique.",
                         "it": "Prima dell'alba ({h}:xx locale) — Grey-line in avvicinamento; finestra DX 80m/40m verso Asia/Pacifico. 20m inizia ad aprirsi verso l'America.",
                         "es": "Antes del amanecer ({h}:xx local) — Grey-line aproximándose; ventana DX 80m/40m hacia Asia/Pacífico. 20m empieza a abrirse hacia América."},
    "adv_mode_weak":    {"nl": "Modus-advies: condities zwak ({pct}% op {band}) — overweeg FT8 (+25 dB winst t.o.v. SSB) of CW (+10 dB). Huidig SNR-budget: {snr} dB.",
                         "en": "Mode advice: conditions weak ({pct}% on {band}) — consider FT8 (+25 dB gain over SSB) or CW (+10 dB). Current SNR budget: {snr} dB.",
                         "de": "Modusempfehlung: Bedingungen schwach ({pct}% auf {band}) — FT8 (+25 dB gegenüber SSB) oder CW (+10 dB) erwägen. Aktuelles SNR-Budget: {snr} dB.",
                         "fr": "Conseil de mode: conditions faibles ({pct}% sur {band}) — envisager FT8 (+25 dB gain vs SSB) ou CW (+10 dB). Budget SNR actuel: {snr} dB.",
                         "it": "Consiglio modo: condizioni deboli ({pct}% su {band}) — considerare FT8 (+25 dB guadagno su SSB) o CW (+10 dB). Budget SNR attuale: {snr} dB.",
                         "es": "Consejo de modo: condiciones débiles ({pct}% en {band}) — considerar FT8 (+25 dB ganancia sobre SSB) o CW (+10 dB). Presupuesto SNR actual: {snr} dB."},
    "adv_mode_good":    {"nl": "Modus-advies: goede condities ({pct}% op {band}) — SSB goed bruikbaar. SNR-budget {snr} dB; verhoog vermogen of verbeter antenne voor meer bereik.",
                         "en": "Mode advice: good conditions ({pct}% on {band}) — SSB well usable. SNR budget {snr} dB; increase power or improve antenna for more range.",
                         "de": "Modusempfehlung: gute Bedingungen ({pct}% auf {band}) — SSB gut nutzbar. SNR-Budget {snr} dB; Leistung erhöhen oder Antenne verbessern.",
                         "fr": "Conseil de mode: bonnes conditions ({pct}% sur {band}) — SSB bien utilisable. Budget SNR {snr} dB; augmenter la puissance ou améliorer l'antenne.",
                         "it": "Consiglio modo: buone condizioni ({pct}% su {band}) — SSB ben utilizzabile. Budget SNR {snr} dB; aumentare potenza o migliorare antenna.",
                         "es": "Consejo de modo: buenas condiciones ({pct}% en {band}) — SSB bien utilizable. Presupuesto SNR {snr} dB; aumentar potencia o mejorar antena para más alcance."},
    "adv_mode_default": {"nl": "Modus-advies: {mode} passend bij huidig {pct}% op {band}. SNR-budget: {snr} dB. FT8 geeft altijd +25 dB extra marge.",
                         "en": "Mode advice: {mode} suitable for current {pct}% on {band}. SNR budget: {snr} dB. FT8 always gives +25 dB extra margin.",
                         "de": "Modusempfehlung: {mode} passend für aktuelle {pct}% auf {band}. SNR-Budget: {snr} dB. FT8 gibt immer +25 dB extra Marge.",
                         "fr": "Conseil de mode: {mode} adapté aux {pct}% actuels sur {band}. Budget SNR: {snr} dB. FT8 donne toujours +25 dB de marge supplémentaire.",
                         "it": "Consiglio modo: {mode} adatto all'attuale {pct}% su {band}. Budget SNR: {snr} dB. FT8 dà sempre +25 dB di margine extra.",
                         "es": "Consejo de modo: {mode} adecuado para el {pct}% actual en {band}. Presupuesto SNR: {snr} dB. FT8 siempre da +25 dB de margen extra."},
    "adv_abs_high":     {"nl": "Auroraal absorptie verhoogd (K={k}, QTH {lat}°) — trans-polaire paden (Europa→Canada, Europa→Japan via pool) sterk verzwakt. Gebruik equatoriale routes via 20m/17m.",
                         "en": "Auroral absorption elevated (K={k}, QTH {lat}°) — trans-polar paths (Europe→Canada, Europe→Japan via pole) strongly attenuated. Use equatorial routes via 20m/17m.",
                         "de": "Polare Absorption erhöht (K={k}, QTH {lat}°) — transpolare Wege (Europa→Kanada, Europa→Japan via Pol) stark gedämpft. Äquatorialrouten über 20m/17m nutzen.",
                         "fr": "Absorption aurorale élevée (K={k}, QTH {lat}°) — chemins trans-polaires (Europe→Canada, Europe→Japon via pôle) fortement atténués. Utiliser routes équatoriales via 20m/17m.",
                         "it": "Assorbimento aurorale elevato (K={k}, QTH {lat}°) — percorsi trans-polari (Europa→Canada, Europa→Giappone via polo) fortemente attenuati. Usare rotte equatoriali via 20m/17m.",
                         "es": "Absorción auroral elevada (K={k}, QTH {lat}°) — rutas trans-polares (Europa→Canadá, Europa→Japón via polo) fuertemente atenuadas. Usar rutas ecuatoriales via 20m/17m."},
    "adv_abs_low":      {"nl": "Lichte absorptie mogelijk (K={k}, QTH {lat}°) — poolpaden kunnen sporadisch verstoord zijn. Monitor 40m voor bruikbaarheid.",
                         "en": "Minor absorption possible (K={k}, QTH {lat}°) — polar paths may be sporadically disturbed. Monitor 40m for usability.",
                         "de": "Leichte Absorption möglich (K={k}, QTH {lat}°) — Polarwege können sporadisch gestört sein. 40m auf Nutzbarkeit überwachen.",
                         "fr": "Légère absorption possible (K={k}, QTH {lat}°) — chemins polaires peuvent être sporadiquement perturbés. Surveiller 40m.",
                         "it": "Assorbimento lieve possibile (K={k}, QTH {lat}°) — percorsi polari possono essere sporadicamente disturbati. Monitorare 40m.",
                         "es": "Absorción leve posible (K={k}, QTH {lat}°) — rutas polares pueden estar esporádicamente perturbadas. Monitorear 40m."},
    "adv_es_high":      {"nl": "Sporadic-E kans HOOG (maand {month}, {h}:xx lok.) — 6m/4m/2m kunnen onverwacht opengaan voor afstanden van 700–2500 km. Monitor 50.313 (FT8) en 50.150 (SSB). Typisch 15–90 min durend.",
                         "en": "Sporadic-E chance HIGH (month {month}, {h}:xx local) — 6m/4m/2m may unexpectedly open for distances of 700–2500 km. Monitor 50.313 (FT8) and 50.150 (SSB). Typically 15–90 min duration.",
                         "de": "Sporadic-E Chance HOCH (Monat {month}, {h}:xx lokal) — 6m/4m/2m können unerwartet für 700–2500 km öffnen. 50.313 (FT8) und 50.150 (SSB) überwachen. Typisch 15–90 min.",
                         "fr": "Chance Sporadic-E ÉLEVÉE (mois {month}, {h}:xx local) — 6m/4m/2m peuvent s'ouvrir inopinément sur 700–2500 km. Surveiller 50.313 (FT8) et 50.150 (SSB). Typiquement 15–90 min.",
                         "it": "Probabilità Sporadic-E ALTA (mese {month}, {h}:xx locale) — 6m/4m/2m possono aprirsi inaspettatamente per distanze 700–2500 km. Monitorare 50.313 (FT8) e 50.150 (SSB). Tipicamente 15–90 min.",
                         "es": "Probabilidad Sporadic-E ALTA (mes {month}, {h}:xx local) — 6m/4m/2m pueden abrirse inesperadamente para distancias de 700–2500 km. Monitorear 50.313 (FT8) y 50.150 (SSB). Típicamente 15–90 min de duración."},
    "adv_es_seasonal":  {"nl": "Sporadic-E seizoen actief (maand {month}) maar buiten piekuren — kans op 6m/4m opens is laag; meest actief 09–14h en 17–22h lokaal.",
                         "en": "Sporadic-E season active (month {month}) but outside peak hours — chance of 6m/4m openings low; most active 09–14h and 17–22h local.",
                         "de": "Sporadic-E-Saison aktiv (Monat {month}), aber außerhalb der Spitzenstunden — Chance auf 6m/4m-Öffnungen gering; am aktivsten 09–14h und 17–22h lokal.",
                         "fr": "Saison Sporadic-E active (mois {month}) mais hors heures de pointe — probabilité d'ouvertures 6m/4m faible; plus actif 09–14h et 17–22h local.",
                         "it": "Stagione Sporadic-E attiva (mese {month}) ma fuori dalle ore di punta — probabilità di aperture 6m/4m bassa; più attiva 09–14h e 17–22h locale.",
                         "es": "Temporada Sporadic-E activa (mes {month}) pero fuera de horas pico — probabilidad de aperturas 6m/4m baja; más activo 09–14h y 17–22h local."},
    "adv_es_winter":    {"nl": "Winter-Es mogelijk (maand {month}, {h}:xx lok.) — zeldzame maar plotselinge openingen op 6m; monitor 50.313 MHz.",
                         "en": "Winter-Es possible (month {month}, {h}:xx local) — rare but sudden openings on 6m; monitor 50.313 MHz.",
                         "de": "Winter-Es möglich (Monat {month}, {h}:xx lokal) — seltene aber plötzliche Öffnungen auf 6m; 50.313 MHz überwachen.",
                         "fr": "Es hivernal possible (mois {month}, {h}:xx local) — ouvertures rares mais soudaines sur 6m; surveiller 50.313 MHz.",
                         "it": "Es invernale possibile (mese {month}, {h}:xx locale) — aperture rare ma improvvise su 6m; monitorare 50.313 MHz.",
                         "es": "Es invernal posible (mes {month}, {h}:xx local) — aperturas raras pero repentinas en 6m; monitorear 50.313 MHz."},
    "adv_tep":          {"nl": "TEP-venster (dag {doy}, {h}:xx lok.) — trans-equatoriale propagatie mogelijk. Paden richting Centraal-Afrika en Latijns-Amerika op 50 MHz en 144 MHz kunnen open zijn. Meest kansrijk 13–17h lokaal.",
                         "en": "TEP window (day {doy}, {h}:xx local) — trans-equatorial propagation possible. Paths towards Central Africa and Latin America on 50 MHz and 144 MHz may be open. Most likely 13–17h local.",
                         "de": "TEP-Fenster (Tag {doy}, {h}:xx lokal) — trans-äquatoriale Ausbreitung möglich. Wege nach Zentralafrika und Lateinamerika auf 50 MHz und 144 MHz können offen sein. Wahrscheinlichster Zeitraum 13–17h lokal.",
                         "fr": "Fenêtre TEP (jour {doy}, {h}:xx local) — propagation trans-équatoriale possible. Chemins vers l'Afrique centrale et l'Amérique latine sur 50 MHz et 144 MHz peuvent être ouverts. Plus probable 13–17h local.",
                         "it": "Finestra TEP (giorno {doy}, {h}:xx locale) — propagazione trans-equatoriale possibile. Percorsi verso l'Africa centrale e l'America Latina su 50 MHz e 144 MHz possono essere aperti. Più probabile 13–17h locale.",
                         "es": "Ventana TEP (día {doy}, {h}:xx local) — propagación trans-ecuatorial posible. Rutas hacia África Central y América Latina en 50 MHz y 144 MHz pueden estar abiertas. Más probable 13–17h local."},
    "adv_trend_change": {"nl": "Propagatie {direction} (afgelopen {age}u): {parts}.",
                         "en": "Propagation {direction} (last {age}h): {parts}.",
                         "de": "Ausbreitung {direction} (letzte {age}h): {parts}.",
                         "fr": "Propagation {direction} (dernières {age}h): {parts}.",
                         "it": "Propagazione {direction} (ultime {age}h): {parts}.",
                         "es": "Propagación {direction} (últimas {age}h): {parts}."},
    "adv_trend_stable": {"nl": "Propagatie stabiel (laatste {age}u geen significante wijziging).",
                         "en": "Propagation stable (last {age}h no significant change).",
                         "de": "Ausbreitung stabil (letzte {age}h keine signifikante Änderung).",
                         "fr": "Propagation stable (dernières {age}h aucun changement significatif).",
                         "it": "Propagazione stabile (ultime {age}h nessun cambiamento significativo).",
                         "es": "Propagación estable (últimas {age}h sin cambio significativo)."},
    "adv_sc_max":       {"nl": "Zonnecyclus 25 MAXIMUM — SSN={ssn} (hoogtepunt verwacht 2025–2026). Optimale F2-propagatie op hoge banden; geniet van 10m–15m DX terwijl de cyclus op zijn best is.",
                         "en": "Solar Cycle 25 MAXIMUM — SSN={ssn} (peak expected 2025–2026). Optimal F2 propagation on high bands; enjoy 10m–15m DX while the cycle is at its best.",
                         "de": "Sonnenzyklus 25 MAXIMUM — SSN={ssn} (Spitze erwartet 2025–2026). Optimale F2-Ausbreitung auf hohen Bändern; 10m–15m DX genießen während der Zyklus am besten ist.",
                         "fr": "Cycle Solaire 25 MAXIMUM — SSN={ssn} (pic attendu 2025–2026). Propagation F2 optimale sur les hautes bandes; profitez du DX 10m–15m pendant que le cycle est au mieux.",
                         "it": "Ciclo Solare 25 MASSIMO — SSN={ssn} (picco atteso 2025–2026). Propagazione F2 ottimale sulle bande alte; goditi il DX 10m–15m mentre il ciclo è al massimo.",
                         "es": "Ciclo Solar 25 MÁXIMO — SSN={ssn} (pico esperado 2025–2026). Propagación F2 óptima en bandas altas; disfruta del DX 10m–15m mientras el ciclo está en su mejor momento."},
    "adv_sc_high":      {"nl": "Zonnecyclus 25 hoog/maximumfase — SSN={ssn}. Hoge banden (10m–17m) regelmatig open voor DX. Verwacht verdere toename richting cycluspiek.",
                         "en": "Solar Cycle 25 high/peak phase — SSN={ssn}. High bands (10m–17m) regularly open for DX. Expect further increase towards cycle peak.",
                         "de": "Sonnenzyklus 25 hoch/Spitzenphase — SSN={ssn}. Hohe Bänder (10m–17m) regelmäßig offen für DX. Weiterer Anstieg Richtung Zyklusspitze erwartet.",
                         "fr": "Cycle Solaire 25 phase haute/maximum — SSN={ssn}. Hautes bandes (10m–17m) régulièrement ouvertes pour DX. Augmentation attendue vers le pic du cycle.",
                         "it": "Ciclo Solare 25 fase alta/massimo — SSN={ssn}. Bande alte (10m–17m) regolarmente aperte per DX. Atteso ulteriore aumento verso il picco del ciclo.",
                         "es": "Ciclo Solar 25 fase alta/máximo — SSN={ssn}. Bandas altas (10m–17m) regularmente abiertas para DX. Se espera mayor aumento hacia el pico del ciclo."},
    "adv_sc_rising":    {"nl": "Zonnecyclus 25 opkomende fase — SSN={ssn}. Cyclus in opbouw; 20m–17m betrouwbaar, hogere banden variabel. Positieve trend verwacht.",
                         "en": "Solar Cycle 25 rising phase — SSN={ssn}. Cycle building up; 20m–17m reliable, higher bands variable. Positive trend expected.",
                         "de": "Sonnenzyklus 25 aufsteigende Phase — SSN={ssn}. Zyklus im Aufbau; 20m–17m zuverlässig, höhere Bänder variabel. Positiver Trend erwartet.",
                         "fr": "Cycle Solaire 25 phase montante — SSN={ssn}. Cycle en développement; 20m–17m fiables, hautes bandes variables. Tendance positive attendue.",
                         "it": "Ciclo Solare 25 fase ascendente — SSN={ssn}. Ciclo in costruzione; 20m–17m affidabili, bande alte variabili. Tendenza positiva attesa.",
                         "es": "Ciclo Solar 25 fase ascendente — SSN={ssn}. Ciclo en construcción; 20m–17m fiables, bandas altas variables. Tendencia positiva esperada."},
    "adv_sc_transition":{"nl": "Zonnecyclus in overgangsperiode — SSN={ssn}. Afhankelijk van trend: controleer of SSN stijgt of daalt. 20m/40m vormen ruggengraat.",
                         "en": "Solar cycle in transition — SSN={ssn}. Depending on trend: check whether SSN is rising or falling. 20m/40m form the backbone.",
                         "de": "Sonnenzyklus im Übergang — SSN={ssn}. Je nach Trend: prüfen ob SSN steigt oder fällt. 20m/40m bilden das Rückgrat.",
                         "fr": "Cycle solaire en transition — SSN={ssn}. Selon la tendance: vérifier si SSN monte ou descend. 20m/40m forment l'épine dorsale.",
                         "it": "Ciclo solare in transizione — SSN={ssn}. In base alla tendenza: verificare se SSN sale o scende. 20m/40m formano la spina dorsale.",
                         "es": "Ciclo solar en transición — SSN={ssn}. Según la tendencia: verificar si SSN sube o baja. 20m/40m forman la columna vertebral."},
    "adv_sc_low":       {"nl": "Zonnecyclus laag — SSN={ssn}. Cyclus mogelijk in minimum of vroeg stadium; 40m/80m/160m zijn de meest betrouwbare banden.",
                         "en": "Solar cycle low — SSN={ssn}. Cycle possibly at minimum or early stage; 40m/80m/160m are the most reliable bands.",
                         "de": "Sonnenzyklus tief — SSN={ssn}. Zyklus möglicherweise im Minimum oder frühen Stadium; 40m/80m/160m sind die zuverlässigsten Bänder.",
                         "fr": "Cycle solaire bas — SSN={ssn}. Cycle possiblement au minimum ou en début; 40m/80m/160m sont les bandes les plus fiables.",
                         "it": "Ciclo solare basso — SSN={ssn}. Ciclo forse al minimo o in fase iniziale; 40m/80m/160m sono le bande più affidabili.",
                         "es": "Ciclo solar bajo — SSN={ssn}. Ciclo posiblemente en mínimo o fase inicial; 40m/80m/160m son las bandas más fiables."},
    "adv_storm_recovery": {"nl": "Storm-herstelprognose: A={a}, K={k} — geschatte normaliseringstijd ≈{rh}u na piek. HF herstel verloopt van laag naar hoog (40m eerst, daarna 20m/15m). Monitor K-index voor herstel onder 3.",
                           "en": "Storm recovery forecast: A={a}, K={k} — estimated normalisation time ≈{rh}h after peak. HF recovery proceeds low-to-high (40m first, then 20m/15m). Monitor K-index for recovery below 3.",
                           "de": "Sturmerholungsprognose: A={a}, K={k} — geschätzte Normalisierungszeit ≈{rh}h nach dem Höhepunkt. KW-Erholung von unten nach oben (40m zuerst, dann 20m/15m). K-Index auf Erholung unter 3 überwachen.",
                           "fr": "Prévision de récupération: A={a}, K={k} — temps de normalisation estimé ≈{rh}h après le pic. Récupération HF du bas vers le haut (40m d'abord, puis 20m/15m). Surveiller K-index pour retour sous 3.",
                           "it": "Previsione recupero tempesta: A={a}, K={k} — tempo di normalizzazione stimato ≈{rh}h dopo il picco. Recupero HF dal basso verso l'alto (prima 40m, poi 20m/15m). Monitorare K-index per recupero sotto 3.",
                           "es": "Pronóstico de recuperación de tormenta: A={a}, K={k} — tiempo estimado de normalización ≈{rh}h tras el pico. Recuperación HF de bajo a alto (primero 40m, luego 20m/15m). Monitorear índice K para recuperación bajo 3."},
    "adv_dx_cluster":   {"nl": "DX-cluster: {n} spots actief — top continenten: {top}. ",
                         "en": "DX cluster: {n} spots active — top continents: {top}. ",
                         "de": "DX-Cluster: {n} Spots aktiv — Top-Kontinente: {top}. ",
                         "fr": "DX cluster: {n} spots actifs — principaux continents: {top}. ",
                         "it": "DX cluster: {n} spot attivi — principali continenti: {top}. ",
                         "es": "DX cluster: {n} spots activos — principales continentes: {top}. "},
    "adv_dx_oceania":   {"nl": "Oceanië ({n}×) actief → goede Oost-kans. ",
                         "en": "Oceania ({n}×) active → good East opportunity. ",
                         "de": "Ozeanien ({n}×) aktiv → gute Ostchance. ",
                         "fr": "Océanie ({n}×) active → bonne opportunité Est. ",
                         "it": "Oceania ({n}×) attiva → buona opportunità Est. ",
                         "es": "Oceanía ({n}×) activa → buena oportunidad Este. "},
    "adv_dx_asia":      {"nl": "Azië ({n}×) goed vertegenwoordigd. ",
                         "en": "Asia ({n}×) well represented. ",
                         "de": "Asien ({n}×) gut vertreten. ",
                         "fr": "Asie ({n}×) bien représentée. ",
                         "it": "Asia ({n}×) ben rappresentata. ",
                         "es": "Asia ({n}×) bien representada. "},
    "adv_dx_routes":    {"nl": "Optimale DX-routes nu: {routes}.",
                         "en": "Optimal DX routes now: {routes}.",
                         "de": "Optimale DX-Routen jetzt: {routes}.",
                         "fr": "Meilleures routes DX maintenant: {routes}.",
                         "it": "Rotte DX ottimali ora: {routes}.",
                         "es": "Rutas DX óptimas ahora: {routes}."},
    "adv_overall_score":{"nl": "Algehele propagatie-score: {overall}  (SFI {sfi} · K {k} · {open} banden open). {daynight}condities, QTH {lat}°N.",
                         "en": "Overall propagation score: {overall}  (SFI {sfi} · K {k} · {open} bands open). {daynight} conditions, QTH {lat}°N.",
                         "de": "Gesamtausbreitungswert: {overall}  (SFI {sfi} · K {k} · {open} Bänder offen). {daynight}bedingungen, QTH {lat}°N.",
                         "fr": "Score de propagation global: {overall}  (SFI {sfi} · K {k} · {open} bandes ouvertes). Conditions {daynight}, QTH {lat}°N.",
                         "it": "Punteggio propagazione globale: {overall}  (SFI {sfi} · K {k} · {open} bande aperte). Condizioni {daynight}, QTH {lat}°N.",
                         "es": "Puntuación general de propagación: {overall}  (SFI {sfi} · K {k} · {open} bandas abiertas). Condiciones {daynight}, QTH {lat}°N."},
    # ── DX routes (teksten) ───────────────────────────────────────────────────
    "dx_route_eu_ja_day":   {"nl": "EU→JA (Azië) via long path, 14–21 MHz",       "en": "EU→JA (Asia) via long path, 14–21 MHz",         "de": "EU→JA (Asien) via Long Path, 14–21 MHz",           "fr": "EU→JA (Asie) via long path, 14–21 MHz",           "it": "EU→JA (Asia) via long path, 14–21 MHz",           "es": "EU→JA (Asia) via long path, 14–21 MHz"},
    "dx_route_eu_w_day":    {"nl": "EU→W (Noord-Amerika) short path, 14–21 MHz",  "en": "EU→W (North America) short path, 14–21 MHz",   "de": "EU→W (Nordamerika) Short Path, 14–21 MHz",         "fr": "EU→W (Amérique du Nord) short path, 14–21 MHz",   "it": "EU→W (Nord America) short path, 14–21 MHz",       "es": "EU→W (América del Norte) short path, 14–21 MHz"},
    "dx_route_eu_af_day":   {"nl": "EU→Afrika short path, 14–28 MHz",             "en": "EU→Africa short path, 14–28 MHz",               "de": "EU→Afrika Short Path, 14–28 MHz",                  "fr": "EU→Afrique short path, 14–28 MHz",                "it": "EU→Africa short path, 14–28 MHz",                 "es": "EU→África short path, 14–28 MHz"},
    "dx_route_eu_oc_day":   {"nl": "EU→VK/ZL (Pacific) long path, 14–21 MHz",    "en": "EU→VK/ZL (Pacific) long path, 14–21 MHz",      "de": "EU→VK/ZL (Pazifik) Long Path, 14–21 MHz",          "fr": "EU→VK/ZL (Pacifique) long path, 14–21 MHz",       "it": "EU→VK/ZL (Pacifico) long path, 14–21 MHz",        "es": "EU→VK/ZL (Pacífico) long path, 14–21 MHz"},
    "dx_route_eu_w_night":  {"nl": "EU→W (Noord-Amerika) 40m–80m nacht-DX",      "en": "EU→W (North America) 40m–80m night DX",        "de": "EU→W (Nordamerika) 40m–80m Nacht-DX",              "fr": "EU→W (Amérique du Nord) 40m–80m DX nocturne",     "it": "EU→W (Nord America) 40m–80m DX notturno",         "es": "EU→W (América del Norte) 40m–80m DX nocturno"},
    "dx_route_eu_ja_night": {"nl": "EU→JA (Azië) 40m–20m via pool night path",   "en": "EU→JA (Asia) 40m–20m via polar night path",    "de": "EU→JA (Asien) 40m–20m via Polar Night Path",       "fr": "EU→JA (Asie) 40m–20m via chemin polaire nocturne","it": "EU→JA (Asia) 40m–20m via percorso polare notturno","es": "EU→JA (Asia) 40m–20m via ruta polar nocturna"},
    # ── CAT interface dialoog ─────────────────────────────────────────────────
    "cat_dlg_title":   {"nl": "CAT Interface Instellingen",       "en": "CAT Interface Settings",           "de": "CAT-Schnittstelleneinstellungen",  "fr": "Paramètres interface CAT",        "it": "Impostazioni interfaccia CAT",      "es": "Configuración interfaz CAT"},
    "cat_ser_port":    {"nl": "Seriële Poort",                    "en": "Serial Port",                      "de": "Serielle Schnittstelle",          "fr": "Port série",                      "it": "Porta seriale",                    "es": "Puerto serie"},
    "cat_port_lbl":    {"nl": "Poort:",                           "en": "Port:",                            "de": "Port:",                           "fr": "Port:",                           "it": "Porta:",                           "es": "Puerto:"},
    "cat_scan":        {"nl": "Scan ▾",                           "en": "Scan ▾",                           "de": "Scan ▾",                          "fr": "Scan ▾",                          "it": "Scan ▾",                           "es": "Scan ▾"},
    "cat_no_ports":    {"nl": "Geen poorten gevonden",            "en": "No ports found",                   "de": "Keine Ports gefunden",            "fr": "Aucun port trouvé",               "it": "Nessuna porta trovata",            "es": "No se encontraron puertos"},
    "cat_no_pyserial": {"nl": "pyserial niet geïnstalleerd",      "en": "pyserial not installed",           "de": "pyserial nicht installiert",      "fr": "pyserial non installé",           "it": "pyserial non installato",          "es": "pyserial no instalado"},
    "cat_ser_params":  {"nl": "Seriële Parameters",               "en": "Serial Parameters",                "de": "Serielle Parameter",              "fr": "Paramètres série",                "it": "Parametri seriali",                "es": "Parámetros serie"},
    "cat_baud_lbl":    {"nl": "Baudrate:",                        "en": "Baud rate:",                       "de": "Baudrate:",                       "fr": "Débit:",                          "it": "Baud rate:",                       "es": "Velocidad:"},
    "cat_bits_lbl":    {"nl": "Databits:",                        "en": "Data bits:",                       "de": "Datenbits:",                      "fr": "Bits de données:",                "it": "Bit di dati:",                     "es": "Bits de datos:"},
    "cat_parity_lbl":  {"nl": "Pariteit:",                        "en": "Parity:",                          "de": "Parität:",                        "fr": "Parité:",                         "it": "Parità:",                          "es": "Paridad:"},
    "cat_stops_lbl":   {"nl": "Stopbits:",                        "en": "Stop bits:",                       "de": "Stoppbits:",                      "fr": "Bits d'arrêt:",                   "it": "Bit di stop:",                     "es": "Bits de parada:"},
    "cat_hs_title":    {"nl": "Handshake & Lijnsignalen",         "en": "Handshake & Line Signals",         "de": "Handshake & Leitungssignale",     "fr": "Handshake & Signaux de ligne",    "it": "Handshake & Segnali di linea",     "es": "Handshake y señales de línea"},
    "cat_hs_lbl":      {"nl": "Handshake:",                       "en": "Handshake:",                       "de": "Handshake:",                      "fr": "Handshake:",                      "it": "Handshake:",                       "es": "Handshake:"},
    "cat_enabled_cb":  {"nl": "Ingeschakeld",                     "en": "Enabled",                          "de": "Aktiviert",                       "fr": "Activé",                          "it": "Attivato",                         "es": "Activado"},
    "cat_enable_lbl":  {"nl": "CAT interface inschakelen",        "en": "Enable CAT interface",             "de": "CAT-Schnittstelle aktivieren",    "fr": "Activer l'interface CAT",         "it": "Attiva interfaccia CAT",           "es": "Activar interfaz CAT"},
    "cat_radio_title": {"nl": "Radio type",                       "en": "Radio type",                       "de": "Funkgerätetyp",                   "fr": "Type de radio",                   "it": "Tipo di radio",                    "es": "Tipo de radio"},
    "cat_type_lbl":    {"nl": "Type:",                            "en": "Type:",                            "de": "Typ:",                            "fr": "Type:",                           "it": "Tipo:",                            "es": "Tipo:"},
    "cat_civ_lbl":     {"nl": "CI-V adres:",                      "en": "CI-V address:",                    "de": "CI-V-Adresse:",                   "fr": "Adresse CI-V:",                   "it": "Indirizzo CI-V:",                  "es": "Dirección CI-V:"},
    "cat_civ_hint":    {"nl": "hex, bv. 0x70 (IC-7300), 0x94 (IC-705)", "en": "hex, e.g. 0x70 (IC-7300), 0x94 (IC-705)", "de": "hex, z.B. 0x70 (IC-7300), 0x94 (IC-705)", "fr": "hex, ex. 0x70 (IC-7300), 0x94 (IC-705)", "it": "hex, es. 0x70 (IC-7300), 0x94 (IC-705)", "es": "hex, ej. 0x70 (IC-7300), 0x94 (IC-705)"},
    "cat_test_btn":    {"nl": "Test verbinding",                  "en": "Test connection",                  "de": "Verbindung testen",               "fr": "Tester la connexion",             "it": "Testa connessione",                "es": "Probar conexión"},
    "cat_save_btn":    {"nl": "Opslaan",                          "en": "Save",                             "de": "Speichern",                       "fr": "Enregistrer",                     "it": "Salva",                            "es": "Guardar"},
    "cat_cancel_btn":  {"nl": "Annuleren",                        "en": "Cancel",                           "de": "Abbrechen",                       "fr": "Annuler",                         "it": "Annulla",                          "es": "Cancelar"},
    "cat_st_no_ser":   {"nl": "⚠  pyserial niet geïnstalleerd  (pip install pyserial)", "en": "⚠  pyserial not installed  (pip install pyserial)", "de": "⚠  pyserial nicht installiert  (pip install pyserial)", "fr": "⚠  pyserial non installé  (pip install pyserial)", "it": "⚠  pyserial non installato  (pip install pyserial)", "es": "⚠  pyserial no instalado  (pip install pyserial)"},
    "cat_st_no_port":  {"nl": "⚠  Geen poort opgegeven.",         "en": "⚠  No port specified.",            "de": "⚠  Kein Port angegeben.",         "fr": "⚠  Aucun port spécifié.",         "it": "⚠  Nessuna porta specificata.",    "es": "⚠  No se ha especificado puerto."},
    "cat_st_ok":       {"nl": "✔  {port} geopend op {baud} baud — verbinding OK", "en": "✔  {port} opened at {baud} baud — connection OK", "de": "✔  {port} geöffnet mit {baud} Baud — Verbindung OK", "fr": "✔  {port} ouvert à {baud} bauds — connexion OK", "it": "✔  {port} aperto a {baud} baud — connessione OK", "es": "✔  {port} abierto a {baud} baudios — conexión OK"},
    "cat_par_none":    {"nl": "N – Geen",    "en": "N – None",    "de": "N – Keine",    "fr": "N – Aucune",  "it": "N – Nessuna",  "es": "N – Ninguna"},
    "cat_par_even":    {"nl": "E – Even",    "en": "E – Even",    "de": "E – Gerade",   "fr": "E – Pair",    "it": "E – Pari",     "es": "E – Par"},
    "cat_par_odd":     {"nl": "O – Oneven",  "en": "O – Odd",     "de": "O – Ungerade", "fr": "O – Impair",  "it": "O – Dispari",  "es": "O – Impar"},
    "cat_par_mark":    {"nl": "M – Mark",    "en": "M – Mark",    "de": "M – Mark",     "fr": "M – Marque",  "it": "M – Mark",     "es": "M – Mark"},
    "cat_par_space":   {"nl": "S – Space",   "en": "S – Space",   "de": "S – Space",    "fr": "S – Espace",  "it": "S – Spazio",   "es": "S – Space"},
    "cat_flow_none":   {"nl": "Geen",        "en": "None",        "de": "Keiner",       "fr": "Aucun",       "it": "Nessuno",      "es": "Ninguno"},
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

# ── WSPR/wspr.live ────────────────────────────────────────────────────────────
WSPR_REFRESH_SECS = 900   # elke 15 minuten
_WSPR_Q = (
    "SELECT tx_sign,rx_sign,tx_lat,tx_lon,rx_lat,rx_lon,band,snr "
    "FROM wspr.rx "
    "WHERE time >= now() - interval 15 minute "
    "LIMIT 300 "
    "FORMAT JSONCompact"
)
WSPR_URL = "https://db1.wspr.live/?" + urllib.parse.urlencode({"query": _WSPR_Q})

# wspr.live band-veld = MHz als integer → band-naam
_WSPR_BAND_MAP: dict[int, str] = {
    1: "160m", 3: "80m", 5: "60m", 7: "40m", 10: "30m",
    14: "20m", 18: "17m", 21: "15m", 24: "12m", 28: "10m", 50: "6m",
}

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

def _fmt_freq_hz(freq_hz: int) -> str:
    """Formatteer Hz naar ##.###.### notatie (bv. 14.200.000)."""
    mhz = freq_hz // 1_000_000
    khz = (freq_hz % 1_000_000) // 1_000
    hz  = freq_hz % 1_000
    return f"{mhz}.{khz:03d}.{hz:03d}"


def _freq_khz_to_band(freq_khz: float) -> str:
    for name, lo, hi in _BAND_RANGES_KHZ:
        if lo <= freq_khz <= hi:
            return name
    return ""


def _yaesu_set_freq(port: str, baud: int, bits: int = 8, parity: str = "N",
                    stopbits: float = 1.0, freq_hz: int = 0,
                    dtr: bool = False, rts: bool = False) -> bool:
    """Stuur VFO-A frequentie via Yaesu CAT (VS0; + FA<11 digits>;)."""
    if not _SERIAL_OK or not port:
        return False
    try:
        with serial.Serial(port=port, baudrate=baud, bytesize=bits,
                           parity=parity, stopbits=stopbits, timeout=1) as s:
            s.dtr = dtr
            s.rts = rts
            s.write(f"VS0;FA{freq_hz:011d};".encode())
        return True
    except Exception:
        return False


def _kenwood_set_freq(port: str, baud: int, bits: int = 8, parity: str = "N",
                      stopbits: float = 1.0, freq_hz: int = 0) -> bool:
    """Stuur VFO-A frequentie via Kenwood/Elecraft CAT (FA<11 digits>;)."""
    if not _SERIAL_OK or not port:
        return False
    try:
        with serial.Serial(port=port, baudrate=baud, bytesize=bits,
                           parity=parity, stopbits=stopbits, timeout=1) as s:
            s.write(f"FA{freq_hz:011d};".encode())
        return True
    except Exception:
        return False


def _icom_set_freq(port: str, baud: int, bits: int = 8, parity: str = "N",
                   stopbits: float = 1.0, freq_hz: int = 0,
                   civ_addr: int = 0x70) -> bool:
    """Stuur frequentie via Icom CI-V protocol (binair BCD, commando 0x05)."""
    if not _SERIAL_OK or not port:
        return False
    # 10 cijfers packed BCD, least-significant pair eerst
    freq_str = f"{freq_hz:010d}"
    bcd = [((int(freq_str[i]) << 4) | int(freq_str[i + 1])) for i in range(0, 10, 2)]
    msg = bytes([0xFE, 0xFE, civ_addr, 0xE0, 0x05]) + bytes(reversed(bcd)) + bytes([0xFD])
    try:
        with serial.Serial(port=port, baudrate=baud, bytesize=bits,
                           parity=parity, stopbits=stopbits, timeout=1) as s:
            s.write(msg)
        return True
    except Exception:
        return False


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


def _fetch_wspr_spots() -> list:
    """Haal recente WSPR-spots op via wspr.live (laatste 15 min, max 300).

    Geeft lijst van dicts: {tx, rx, tx_lat, tx_lon, rx_lat, rx_lon, band, snr}.
    Alleen HF-banden (1–50 MHz), spots met geldige coördinaten.
    """
    try:
        req = urllib.request.Request(WSPR_URL,
              headers={"User-Agent": "HAMIOS/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            raw = json.loads(r.read().decode("utf-8", errors="replace"))
        spots = []
        for row in raw.get("data", []):
            try:
                tx_sign, rx_sign = str(row[0]), str(row[1])
                tx_lat, tx_lon   = float(row[2]), float(row[3])
                rx_lat, rx_lon   = float(row[4]), float(row[5])
                band_mhz         = int(row[6])
                snr              = int(row[7])
            except (ValueError, TypeError, IndexError):
                continue
            band_name = _WSPR_BAND_MAP.get(band_mhz)
            if not band_name:
                continue
            # filter ongeldige coördinaten
            if not (-90 <= tx_lat <= 90 and -180 <= tx_lon <= 180 and
                    -90 <= rx_lat <= 90 and -180 <= rx_lon <= 180):
                continue
            spots.append({
                "tx": tx_sign, "rx": rx_sign,
                "tx_lat": tx_lat, "tx_lon": tx_lon,
                "rx_lat": rx_lat, "rx_lon": rx_lon,
                "band": band_name, "snr": snr,
            })
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
        self.root.title("HAMIOS v2.3")
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
        self._lang_var    = tk.StringVar(value=s["language"])
        self._last_band_pct = [(n, f, 0) for n, f, _ in _BANDS]
        _prune_history()
        self._history:    list = _load_history()
        self._hist_range_var = tk.StringVar(value=s["hist_range"])
        self._hist_sel: set  = s["hist_sel"]
        self._show_tips_var    = tk.BooleanVar(value=s["show_tips"])
        self._ticker_enabled_var = tk.BooleanVar(value=s["show_ticker"])
        self._show_sun_var      = tk.BooleanVar(value=s["show_sun"])
        self._show_moon_var     = tk.BooleanVar(value=s["show_moon"])
        self._show_locator_var  = tk.BooleanVar(value=s["show_locator"])
        self._show_graylijn_var = tk.BooleanVar(value=s["show_graylijn"])
        self._show_iaru_var     = tk.BooleanVar(value=s["show_iaru"])
        self._show_cs_var       = tk.BooleanVar(value=s["show_cs"])
        self._show_spots_var    = tk.BooleanVar(value=s["show_spots"])
        self._spot_hit_areas:   list = []   # [{x, y, r, spot}, ...] voor klik-detectie
        self._show_wspr_var     = tk.BooleanVar(value=s["show_wspr"])
        self._wspr_spots:       list = []
        self._wspr_after_id             = None
        self._qth_lat_var = tk.StringVar(value=f"{self._qth_lat:.2f}")
        self._qth_lon_var = tk.StringVar(value=f"{self._qth_lon:.2f}")
        self._tr_widgets: dict = {}   # key → widget of list van widgets voor vertalingen
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
        self._last_pca_level: int   = 0    # S-level van vorig proton event (0 = geen)
        self._last_fof2_model: float = 0.0 # model foF2 (MHz), bijgewerkt door _recalc_prop
        self._dx_all_spots: list    = []   # ruwe spots van dxwatch
        self._dx_after_id           = None
        self._dx_next_at: datetime.datetime | None = None
        self._dx_own_cont_var       = tk.BooleanVar(value=True)
        self._advice_card_hashes: dict = {}   # kaart-index → hash, voor nieuw-stip per kaartje

        # CAT interface instellingen
        self._cat_port_var     = tk.StringVar(value=s["cat_port"])
        self._cat_baud_var     = tk.StringVar(value=s["cat_baud"])
        self._cat_bits_var     = tk.StringVar(value=s["cat_bits"])
        self._cat_parity_var   = tk.StringVar(value=s["cat_parity"])
        self._cat_stopbits_var = tk.StringVar(value=s["cat_stopbits"])
        self._cat_flow_var     = tk.StringVar(value=s["cat_flow"])
        self._cat_dtr_var      = tk.BooleanVar(value=s["cat_dtr"])
        self._cat_rts_var      = tk.BooleanVar(value=s["cat_rts"])
        self._cat_enabled_var  = tk.BooleanVar(value=s["cat_enabled"])
        self._cat_radio_var    = tk.StringVar(value=s["cat_radio"])
        self._cat_civ_addr_var = tk.StringVar(value=s["cat_civ_addr"])
        self._cat_freq_var      = tk.StringVar(value="")
        self._cat_terminal_var  = tk.BooleanVar(value=False)
        self._cat_vfo_a_hz: int = 0
        self._cat_vfo_b_hz: int = 0
        self._cat_rx_queue: _queue.Queue = _queue.Queue()
        self._cat_poll_lock = threading.Lock()
        self._cat_poll_after_id = None

        self._build_ui()
        # Herstel legenda-selectie visueel na opbouw UI
        if self._hist_sel:
            for bname, (lbl_d, lbl_n) in self._leg_widgets.items():
                color  = _BAND_COLORS.get(bname, TEXT_DIM)
                active = bname in self._hist_sel
                lbl_d.config(fg=color     if active else TEXT_DIM)
                lbl_n.config(fg=TEXT_BODY if active else TEXT_DIM,
                             font=_font(8, "bold") if active else _font(8))
        self._center_window(1400)   # h_hint = MIN_WINDOW_H (default)
        self._tick_clock()
        self._start_tray()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        threading.Thread(target=self._refresh_solar, daemon=True).start()
        threading.Thread(target=self._refresh_dx, daemon=True).start()
        threading.Thread(target=self._refresh_wspr, daemon=True).start()
        self._cat_start_poll()
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

    # ── Vertalingen ───────────────────────────────────────────────────────────
    def _tr(self, key: str) -> str:
        """Geeft vertaling terug voor de actieve taal."""
        lang = _LANG_CODES.get(self._lang_var.get(), "nl")
        return _T.get(key, {}).get(lang, key)

    def _apply_translations(self):
        """Werk alle opgeslagen widget-referenties bij met de nieuwe taal."""
        for key, widgets in self._tr_widgets.items():
            text = self._tr(key)
            if not isinstance(widgets, list):
                widgets = [widgets]
            for w in widgets:
                try:
                    w.config(text=text)
                except tk.TclError:
                    pass
        # Hist-range radiobuttons (value ≠ display text)
        for rb, tr_key in getattr(self, "_hist_range_rbs", []):
            try:
                rb.config(text=self._tr(tr_key))
            except tk.TclError:
                pass
        # Refresh + advice opnieuw renderen bij taalwissel
        self._update_advice()

    def _on_lang_change(self, *_):
        self._apply_translations()
        self._save_cur_settings()

    def _apply_qth(self, *_):
        """Verwerk gewijzigde QTH lat/lon invoer."""
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

    def _quit_app(self):
        """Netjes afsluiten: tray stoppen, instellingen opslaan, venster sluiten."""
        self._cat_stop_poll()
        self._save_cur_settings()
        if self._tray_icon:
            try:
                self._tray_icon.stop()
            except Exception:
                pass
        self.root.destroy()

    # ── CAT Interface ─────────────────────────────────────────────────────────
    def _update_cat_btn_color(self):
        """Kleur CAT-knop groen als ingeschakeld, anders donkerblauw."""
        if self._cat_enabled_var.get():
            self._cat_btn.config(bg="#1B5E20", activebackground="#2E7D32")
        else:
            self._cat_btn.config(bg="#0D3B4F", activebackground="#1A6080")

    def _update_cat_freq_lbl_visibility(self):
        """Toon VFO-A/B label (en terminal toggle) alleen als CAT ingeschakeld is."""
        if hasattr(self, "_cat_info_frame"):
            if self._cat_enabled_var.get():
                self._cat_info_frame.pack(fill=tk.X, padx=12, pady=(0, 2))
            else:
                self._cat_info_frame.pack_forget()
                if hasattr(self, "_cat_terminal_frame"):
                    self._cat_terminal_frame.pack_forget()

    def _toggle_cat_terminal(self):
        """Toon of verberg het CAT terminal venster."""
        if self._cat_terminal_var.get():
            self._cat_terminal_frame.pack(fill=tk.X)
        else:
            self._cat_terminal_frame.pack_forget()

    def _cat_terminal_log(self, text: str, tag: str = "info"):
        """Voeg een regel toe aan het CAT terminal venster (main thread only)."""
        if not self._cat_terminal_var.get():
            return
        if not hasattr(self, "_cat_terminal_txt"):
            return
        w = self._cat_terminal_txt
        w.config(state=tk.NORMAL)
        w.insert(tk.END, text + "\n", tag)
        w.see(tk.END)
        lines = int(w.index(tk.END).split(".")[0])
        if lines > 210:
            w.delete("1.0", f"{lines - 200}.0")
        w.config(state=tk.DISABLED)

    def _cat_start_poll(self):
        """Start VFO polling als CAT ingeschakeld en pyserial beschikbaar."""
        self._cat_stop_poll()
        if self._cat_enabled_var.get() and _SERIAL_OK:
            self._cat_poll_after_id = self.root.after(500, self._cat_poll_tick)

    def _cat_stop_poll(self):
        if self._cat_poll_after_id is not None:
            self.root.after_cancel(self._cat_poll_after_id)
            self._cat_poll_after_id = None

    def _cat_poll_tick(self):
        """Peil VFO-A en VFO-B van de radio in een achtergrond-thread."""
        if not self._cat_enabled_var.get() or not _SERIAL_OK:
            return
        port = self._cat_port_var.get().strip()
        if not port:
            self._cat_poll_after_id = self.root.after(2000, self._cat_poll_tick)
            return

        def _do_poll():
            if not self._cat_poll_lock.acquire(blocking=False):
                return
            try:
                baud  = int(self._cat_baud_var.get())
                bits  = int(self._cat_bits_var.get())
                par   = self._cat_parity_var.get()
                stop  = float(self._cat_stopbits_var.get())
                with serial.Serial(port=port, baudrate=baud, bytesize=bits,
                                   parity=par, stopbits=stop, timeout=0.3) as s:
                    s.dtr = False
                    s.rts = False
                    s.write(b"FA;FB;")
                    raw = b""
                    for _ in range(100):
                        chunk = s.read(32)
                        if not chunk:
                            break
                        raw += chunk
                        if raw.count(b";") >= 2:
                            break
                self._cat_rx_queue.put(raw.decode("ascii", errors="ignore"))
            except Exception:
                pass
            finally:
                self._cat_poll_lock.release()

        self._cat_terminal_log("▶ FA;FB;", "tx")
        threading.Thread(target=_do_poll, daemon=True).start()
        self._cat_poll_after_id = self.root.after(100, self._cat_process_rx)

    def _cat_process_rx(self):
        """Verwerk ontvangen CAT data en plan volgende poll."""
        try:
            while True:
                raw = self._cat_rx_queue.get_nowait()
                self._cat_terminal_log(f"◀ {raw.strip()}", "rx")
                parts = [p.strip() for p in raw.split(";") if p.strip()]
                for p in parts:
                    if p.startswith("FA") and len(p) >= 13:
                        digits = "".join(c for c in p[2:] if c.isdigit())
                        if len(digits) >= 8:
                            hz = int(digits[:11].zfill(11))
                            if hz != self._cat_vfo_a_hz:
                                self._cat_vfo_a_hz = hz
                                self._cat_freq_var.set(
                                    f"VFO-A:  {_fmt_freq_hz(hz)}")
                    elif p.startswith("FB") and len(p) >= 13:
                        digits = "".join(c for c in p[2:] if c.isdigit())
                        if len(digits) >= 8:
                            hz = int(digits[:11].zfill(11))
                            if hz != self._cat_vfo_b_hz:
                                self._cat_vfo_b_hz = hz
                if self._cat_vfo_b_hz:
                    self._cat_freq_var.set(
                        f"VFO-A:  {_fmt_freq_hz(self._cat_vfo_a_hz)}"
                        f"    VFO-B:  {_fmt_freq_hz(self._cat_vfo_b_hz)}")
                if hasattr(self, "_last_band_pct") and self._last_band_pct:
                    self._draw_prop_bars(self._last_band_pct)
        except _queue.Empty:
            pass
        self._cat_poll_after_id = self.root.after(2000, self._cat_poll_tick)

    def _open_cat_dialog(self):
        """Open het CAT-interface instellingendialoogvenster."""
        tr = self._tr
        dlg = tk.Toplevel(self.root)
        dlg.title(tr("cat_dlg_title"))
        dlg.configure(bg=BG_PANEL)
        dlg.resizable(False, False)
        dlg.grab_set()   # modaal

        # Tijdelijke kopieën van instellingen (alleen opgeslagen bij OK)
        port_var     = tk.StringVar(value=self._cat_port_var.get())
        baud_var     = tk.StringVar(value=self._cat_baud_var.get())
        bits_var     = tk.StringVar(value=self._cat_bits_var.get())
        parity_var   = tk.StringVar(value=self._cat_parity_var.get())
        stop_var     = tk.StringVar(value=self._cat_stopbits_var.get())
        flow_var     = tk.StringVar(value=self._cat_flow_var.get())
        dtr_var      = tk.BooleanVar(value=self._cat_dtr_var.get())
        rts_var      = tk.BooleanVar(value=self._cat_rts_var.get())
        enabled_var   = tk.BooleanVar(value=self._cat_enabled_var.get())
        radio_var     = tk.StringVar(value=self._cat_radio_var.get())
        civ_addr_var  = tk.StringVar(value=self._cat_civ_addr_var.get())
        status_var    = tk.StringVar(value="")

        # ── Opties ──────────────────────────────────────────────────────────
        BAUDS    = ["300","1200","2400","4800","9600","19200","38400",
                    "57600","115200","230400"]
        BITS     = ["7","8"]
        PARITIES = [(tr("cat_par_none"),  "N"),
                    (tr("cat_par_even"),  "E"),
                    (tr("cat_par_odd"),   "O"),
                    (tr("cat_par_mark"),  "M"),
                    (tr("cat_par_space"), "S")]
        STOPS    = ["1","1.5","2"]
        FLOWS    = [tr("cat_flow_none"), "RTS/CTS", "XON/XOFF", "DTR/DSR"]

        PAD = {"padx": 10, "pady": 4}

        def _dropdown(parent, var, values, width=18):
            mb = tk.Menubutton(parent, textvariable=var,
                               font=_font(9), bg=BG_SURFACE, fg=TEXT_H1,
                               relief=tk.FLAT, activebackground=BG_HOVER,
                               activeforeground=TEXT_H1, width=width,
                               anchor="w", padx=6, pady=3, cursor="hand2")
            menu = tk.Menu(mb, tearoff=False, bg=BG_SURFACE, fg=TEXT_H1,
                           activebackground=ACCENT, activeforeground=BG_ROOT,
                           font=_font(9))
            if values and isinstance(values[0], tuple):
                # (label, value) tuples
                for label, val in values:
                    menu.add_command(label=label, command=lambda v=val: var.set(v))
            else:
                for v in values:
                    menu.add_command(label=v, command=lambda v=v: var.set(v))
            mb["menu"] = menu
            return mb

        # ── Sectie: Poort ────────────────────────────────────────────────────
        port_frame = tk.LabelFrame(dlg, text=f" {tr('cat_ser_port')} ",
                                   font=_font(9, "bold"), bg=BG_PANEL,
                                   fg=ACCENT, bd=1, relief=tk.GROOVE)
        port_frame.grid(row=0, column=0, columnspan=2, sticky="ew",
                        padx=12, pady=(12, 4))
        port_frame.columnconfigure(1, weight=1)

        tk.Label(port_frame, text=tr("cat_port_lbl"), font=_font(9),
                 bg=BG_PANEL, fg=TEXT_DIM, anchor="w").grid(
                 row=1, column=0, sticky="w", **PAD)

        port_entry = tk.Entry(port_frame, textvariable=port_var, width=14,
                              bg=BG_SURFACE, fg=TEXT_H1,
                              insertbackground=TEXT_H1, relief=tk.FLAT,
                              font=_font(9))
        port_entry.grid(row=1, column=1, sticky="w", padx=(10,4), pady=4)

        def _scan_ports():
            if _SERIAL_OK:
                ports = [p.device for p in serial.tools.list_ports.comports()]
                ports_sorted = sorted(ports)
            else:
                ports_sorted = []
            scan_menu.delete(0, "end")
            if ports_sorted:
                for p in ports_sorted:
                    scan_menu.add_command(label=p, command=lambda v=p: port_var.set(v))
                scan_btn.config(text="Poort ▾")
            else:
                scan_menu.add_command(label=tr("cat_no_ports") if _SERIAL_OK
                                      else tr("cat_no_pyserial"),
                                      state="disabled")
                scan_btn.config(text="Scan ▾")

        scan_btn = tk.Menubutton(port_frame, text="Scan ▾",
                                 font=_font(9), bg=BG_SURFACE, fg=TEXT_H1,
                                 relief=tk.FLAT, activebackground=BG_HOVER,
                                 activeforeground=TEXT_H1, padx=6, pady=3,
                                 cursor="hand2")
        scan_menu = tk.Menu(scan_btn, tearoff=False, bg=BG_SURFACE, fg=TEXT_H1,
                            activebackground=ACCENT, activeforeground=BG_ROOT,
                            font=_font(9))
        scan_btn["menu"] = scan_menu
        scan_btn.grid(row=1, column=2, sticky="w", padx=(0, 10), pady=4)
        scan_btn.bind("<Button-1>", lambda _: _scan_ports())

        # Pariteit-waarde omzetten voor weergave (N→"N – Geen" etc.)
        _par_label = {v: l for l, v in PARITIES}

        def _parity_display():
            return _par_label.get(parity_var.get(), parity_var.get())

        parity_disp = tk.StringVar(value=_parity_display())

        def _set_parity(code):
            parity_var.set(code)
            parity_disp.set(_par_label.get(code, code))

        # ── Sectie: Seriële parameters ───────────────────────────────────────
        ser_frame = tk.LabelFrame(dlg, text=f" {tr('cat_ser_params')} ",
                                  font=_font(9, "bold"), bg=BG_PANEL,
                                  fg=ACCENT, bd=1, relief=tk.GROOVE)
        ser_frame.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=4)
        ser_frame.columnconfigure(1, weight=1)

        tk.Label(ser_frame, text=tr("cat_baud_lbl"), font=_font(9),
                 bg=BG_PANEL, fg=TEXT_DIM, anchor="w").grid(
                 row=1, column=0, sticky="w", **PAD)
        _dropdown(ser_frame, baud_var, BAUDS, width=10).grid(
            row=1, column=1, sticky="w", **PAD)

        tk.Label(ser_frame, text=tr("cat_bits_lbl"), font=_font(9),
                 bg=BG_PANEL, fg=TEXT_DIM, anchor="w").grid(
                 row=2, column=0, sticky="w", **PAD)
        _dropdown(ser_frame, bits_var, BITS, width=10).grid(
            row=2, column=1, sticky="w", **PAD)

        tk.Label(ser_frame, text=tr("cat_parity_lbl"), font=_font(9),
                 bg=BG_PANEL, fg=TEXT_DIM, anchor="w").grid(
                 row=3, column=0, sticky="w", **PAD)
        par_mb = tk.Menubutton(ser_frame, textvariable=parity_disp,
                               font=_font(9), bg=BG_SURFACE, fg=TEXT_H1,
                               relief=tk.FLAT, activebackground=BG_HOVER,
                               activeforeground=TEXT_H1, width=12,
                               anchor="w", padx=6, pady=3, cursor="hand2")
        par_menu = tk.Menu(par_mb, tearoff=False, bg=BG_SURFACE, fg=TEXT_H1,
                           activebackground=ACCENT, activeforeground=BG_ROOT,
                           font=_font(9))
        for label, code in PARITIES:
            par_menu.add_command(label=label, command=lambda c=code: _set_parity(c))
        par_mb["menu"] = par_menu
        par_mb.grid(row=3, column=1, sticky="w", **PAD)

        tk.Label(ser_frame, text=tr("cat_stops_lbl"), font=_font(9),
                 bg=BG_PANEL, fg=TEXT_DIM, anchor="w").grid(
                 row=4, column=0, sticky="w", **PAD)
        _dropdown(ser_frame, stop_var, STOPS, width=10).grid(
            row=4, column=1, sticky="w", **PAD)

        # ── Sectie: Handshake & lijnsignalen ─────────────────────────────────
        hs_frame = tk.LabelFrame(dlg, text=f" {tr('cat_hs_title')} ",
                                 font=_font(9, "bold"), bg=BG_PANEL,
                                 fg=ACCENT, bd=1, relief=tk.GROOVE)
        hs_frame.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=4)
        hs_frame.columnconfigure(1, weight=1)

        tk.Label(hs_frame, text=tr("cat_hs_lbl"), font=_font(9),
                 bg=BG_PANEL, fg=TEXT_DIM, anchor="w").grid(
                 row=1, column=0, sticky="w", **PAD)
        _dropdown(hs_frame, flow_var, FLOWS, width=12).grid(
            row=1, column=1, sticky="w", **PAD)

        tk.Label(hs_frame, text="DTR:", font=_font(9),
                 bg=BG_PANEL, fg=TEXT_DIM, anchor="w").grid(
                 row=2, column=0, sticky="w", **PAD)
        tk.Checkbutton(hs_frame, text=tr("cat_enabled_cb"), variable=dtr_var,
                       bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                       activebackground=BG_PANEL, activeforeground=TEXT_H1,
                       font=_font(9)).grid(row=2, column=1, sticky="w", **PAD)

        tk.Label(hs_frame, text="RTS:", font=_font(9),
                 bg=BG_PANEL, fg=TEXT_DIM, anchor="w").grid(
                 row=3, column=0, sticky="w", **PAD)
        tk.Checkbutton(hs_frame, text=tr("cat_enabled_cb"), variable=rts_var,
                       bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                       activebackground=BG_PANEL, activeforeground=TEXT_H1,
                       font=_font(9)).grid(row=3, column=1, sticky="w", **PAD)

        # Spacer zodat beide frames even hoog zijn
        tk.Label(hs_frame, text="", bg=BG_PANEL).grid(row=4, column=0)

        # ── Sectie: Radio type ────────────────────────────────────────────────
        RADIO_TYPES = ["Yaesu CAT", "Kenwood / Elecraft", "Icom CI-V"]
        radio_frame = tk.LabelFrame(dlg, text=f" {tr('cat_radio_title')} ",
                                    font=_font(9, "bold"), bg=BG_PANEL,
                                    fg=ACCENT, bd=1, relief=tk.GROOVE)
        radio_frame.grid(row=2, column=0, columnspan=2, sticky="ew",
                         padx=12, pady=4)
        radio_frame.columnconfigure(1, weight=1)

        tk.Label(radio_frame, text=tr("cat_type_lbl"), font=_font(9),
                 bg=BG_PANEL, fg=TEXT_DIM, anchor="w").grid(
                 row=0, column=0, sticky="w", **PAD)
        _dropdown(radio_frame, radio_var, RADIO_TYPES, width=20).grid(
            row=0, column=1, sticky="w", padx=(10, 4), pady=4)

        civ_lbl = tk.Label(radio_frame, text=tr("cat_civ_lbl"), font=_font(9),
                           bg=BG_PANEL, fg=TEXT_DIM, anchor="w")
        civ_entry = tk.Entry(radio_frame, textvariable=civ_addr_var, width=8,
                             bg=BG_SURFACE, fg=TEXT_H1,
                             insertbackground=TEXT_H1, relief=tk.FLAT,
                             font=_font(9))
        civ_hint = tk.Label(radio_frame,
                            text=tr("cat_civ_hint"),
                            font=_font(8), bg=BG_PANEL, fg=TEXT_DIM)

        def _update_civ_visibility(*_):
            if radio_var.get() == "Icom CI-V":
                civ_lbl.grid(row=1, column=0, sticky="w", **PAD)
                civ_entry.grid(row=1, column=1, sticky="w", padx=(10, 4), pady=4)
                civ_hint.grid(row=1, column=2, sticky="w", padx=(0, 10), pady=4)
            else:
                civ_lbl.grid_remove()
                civ_entry.grid_remove()
                civ_hint.grid_remove()

        radio_var.trace_add("write", _update_civ_visibility)
        _update_civ_visibility()

        # ── Sectie: Activeren ─────────────────────────────────────────────────
        act_frame = tk.Frame(dlg, bg=BG_PANEL)
        act_frame.grid(row=3, column=0, columnspan=2, sticky="ew",
                       padx=12, pady=(4, 2))
        tk.Checkbutton(act_frame, text=tr("cat_enable_lbl"),
                       variable=enabled_var,
                       bg=BG_PANEL, fg=TEXT_H1, selectcolor=BG_SURFACE,
                       activebackground=BG_PANEL, activeforeground=TEXT_H1,
                       font=_font(9, "bold")).pack(side=tk.LEFT, padx=4)

        # ── Status & Test ────────────────────────────────────────────────────
        test_frame = tk.Frame(dlg, bg=BG_SURFACE, bd=1, relief=tk.GROOVE)
        test_frame.grid(row=4, column=0, columnspan=2, sticky="ew",
                        padx=12, pady=4)

        def _test_connection():
            if not _SERIAL_OK:
                status_var.set(tr("cat_st_no_ser"))
                status_lbl.config(fg="#FFC107")
                return
            port = port_var.get().strip()
            if not port:
                status_var.set(tr("cat_st_no_port"))
                status_lbl.config(fg="#FFC107")
                return
            try:
                baud  = int(baud_var.get())
                bits  = int(bits_var.get())
                stop  = float(stop_var.get())
                par   = parity_var.get()
                flow  = flow_var.get()
                xonxoff  = ("XON/XOFF" in flow)
                rtscts   = ("RTS/CTS"  in flow)
                dsrdtr   = ("DTR/DSR"  in flow)
                s = serial.Serial(
                    port=port, baudrate=baud, bytesize=bits,
                    parity=par, stopbits=stop,
                    xonxoff=xonxoff, rtscts=rtscts, dsrdtr=dsrdtr,
                    timeout=1
                )
                s.dtr = dtr_var.get()
                s.rts = rts_var.get()
                s.close()
                status_var.set(tr("cat_st_ok").format(port=port, baud=baud))
                status_lbl.config(fg="#4CAF50")
            except serial.SerialException as e:
                status_var.set(f"✘  {e}")
                status_lbl.config(fg="#F44336")
            except Exception as e:
                status_var.set(f"✘  {e}")
                status_lbl.config(fg="#F44336")

        test_btn = tk.Button(test_frame, text=tr("cat_test_btn"),
                             command=_test_connection,
                             font=_font(9), bg="#1A3A5C", fg=TEXT_H1,
                             activebackground="#2A5A8C", activeforeground=TEXT_H1,
                             relief=tk.FLAT, padx=10, pady=3, cursor="hand2")
        test_btn.pack(side=tk.LEFT, padx=8, pady=6)
        status_lbl = tk.Label(test_frame, textvariable=status_var,
                              font=_font(9), bg=BG_SURFACE, fg=TEXT_DIM,
                              anchor="w", wraplength=320, justify="left")
        status_lbl.pack(side=tk.LEFT, padx=(4, 8), pady=6, fill=tk.X, expand=True)

        # ── OK / Annuleren ───────────────────────────────────────────────────
        btn_frame = tk.Frame(dlg, bg=BG_PANEL)
        btn_frame.grid(row=5, column=0, columnspan=2, sticky="e",
                       padx=12, pady=(4, 12))

        def _save_and_close():
            self._cat_port_var.set(port_var.get().strip())
            self._cat_baud_var.set(baud_var.get())
            self._cat_bits_var.set(bits_var.get())
            self._cat_parity_var.set(parity_var.get())
            self._cat_stopbits_var.set(stop_var.get())
            self._cat_flow_var.set(flow_var.get())
            self._cat_dtr_var.set(dtr_var.get())
            self._cat_rts_var.set(rts_var.get())
            self._cat_enabled_var.set(enabled_var.get())
            self._cat_radio_var.set(radio_var.get())
            self._cat_civ_addr_var.set(civ_addr_var.get().strip())
            self._save_cur_settings()
            self._update_cat_btn_color()
            self._cat_start_poll()
            self._update_cat_freq_lbl_visibility()
            dlg.destroy()

        tk.Button(btn_frame, text=tr("cat_save_btn"),
                  command=_save_and_close,
                  font=_font(9), bg="#1B5E20", fg=TEXT_H1,
                  activebackground="#2E7D32", activeforeground=TEXT_H1,
                  relief=tk.FLAT, padx=14, pady=3, cursor="hand2").pack(
                  side=tk.LEFT, padx=(0, 6))
        tk.Button(btn_frame, text=tr("cat_cancel_btn"),
                  command=dlg.destroy,
                  font=_font(9), bg=BG_SURFACE, fg=TEXT_DIM,
                  activebackground=BG_HOVER, activeforeground=TEXT_H1,
                  relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(side=tk.LEFT)

        # Centreer dialoog op hoofdvenster
        dlg.update_idletasks()
        rx = self.root.winfo_x() + (self.root.winfo_width()  - dlg.winfo_reqwidth())  // 2
        ry = self.root.winfo_y() + (self.root.winfo_height() - dlg.winfo_reqheight()) // 2
        dlg.geometry(f"+{max(0,rx)}+{max(0,ry)}")

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.root, bg=BG_PANEL, height=42)
        hdr.pack(fill=tk.X)
        tk.Frame(hdr, bg=ACCENT, width=4).pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(hdr, text="📡  HAMIOS v2.3",
                 font=_font(13, "bold"), bg=BG_PANEL, fg=ACCENT,
                 pady=8).pack(side=tk.LEFT, padx=10)

        # Exit knop (links, naast titel)
        exit_btn = tk.Button(hdr, text=self._tr("exit"),
                             command=self._quit_app,
                             font=_font(9), bg="#5A1010", fg=TEXT_H1,
                             activebackground="#8B1A1A", activeforeground=TEXT_H1,
                             relief=tk.FLAT, padx=8, pady=2, cursor="hand2")
        exit_btn.pack(side=tk.LEFT, padx=(0, 6))
        self._tr_widgets["exit"] = exit_btn

        # CAT Interface knop (naast Afsluiten)
        self._cat_btn = tk.Button(hdr, text="CAT",
                                  command=self._open_cat_dialog,
                                  font=_font(9), bg="#0D3B4F", fg=TEXT_H1,
                                  activebackground="#1A6080", activeforeground=TEXT_H1,
                                  relief=tk.FLAT, padx=8, pady=2, cursor="hand2")
        self._cat_btn.pack(side=tk.LEFT, padx=(0, 10))
        self._update_cat_btn_color()

        # ── Rechter kant (right → left volgorde) ────────────────────────────
        # Tijden rechts (UTC + lokaal)
        self._utc_var   = tk.StringVar()
        self._local_var = tk.StringVar()
        tk.Label(hdr, textvariable=self._utc_var,
                 font=_font(10), bg=BG_PANEL, fg=TEXT_DIM).pack(side=tk.RIGHT, padx=(0, 14))
        tk.Frame(hdr, bg=BORDER, width=1).pack(side=tk.RIGHT, fill=tk.Y, pady=8)
        tk.Label(hdr, textvariable=self._local_var,
                 font=_font(10, "bold"), bg=BG_PANEL, fg=TEXT_H1).pack(side=tk.RIGHT, padx=(0, 10))

        # Checkboxes
        tk.Frame(hdr, bg=BORDER, width=1).pack(side=tk.RIGHT, fill=tk.Y, pady=8)
        cb_dst = tk.Checkbutton(hdr, text=self._tr("summer_time"), variable=self._dst_var,
                                command=self._save_cur_settings,
                                bg=BG_PANEL, fg=TEXT_DIM, selectcolor=BG_SURFACE,
                                activebackground=BG_PANEL, activeforeground=TEXT_BODY,
                                font=_font(9))
        cb_dst.pack(side=tk.RIGHT, padx=(0, 8))
        self._tr_widgets["summer_time"] = cb_dst
        cb_tips = tk.Checkbutton(hdr, text=self._tr("tooltips"), variable=self._show_tips_var,
                                 bg=BG_PANEL, fg=TEXT_DIM, selectcolor=BG_SURFACE,
                                 activebackground=BG_PANEL, activeforeground=TEXT_BODY,
                                 font=_font(9))
        cb_tips.pack(side=tk.RIGHT, padx=(0, 4))
        self._tr_widgets["tooltips"] = cb_tips
        cb_ticker = tk.Checkbutton(hdr, text=self._tr("ticker"),
                                   variable=self._ticker_enabled_var,
                                   command=self._toggle_ticker,
                                   bg=BG_PANEL, fg=TEXT_DIM, selectcolor=BG_SURFACE,
                                   activebackground=BG_PANEL, activeforeground=TEXT_BODY,
                                   font=_font(9))
        cb_ticker.pack(side=tk.RIGHT, padx=(0, 4))
        self._tr_widgets["ticker"] = cb_ticker

        # QTH Lat/Lon invoer
        tk.Frame(hdr, bg=BORDER, width=1).pack(side=tk.RIGHT, fill=tk.Y, pady=8)
        lon_e = tk.Entry(hdr, textvariable=self._qth_lon_var, width=8,
                         bg=BG_SURFACE, fg=TEXT_H1, insertbackground=TEXT_H1,
                         relief=tk.FLAT, font=_font(9))
        lon_e.pack(side=tk.RIGHT, padx=(2, 8))
        lon_e.bind("<Return>",   self._apply_qth)
        lon_e.bind("<FocusOut>", self._apply_qth)
        lon_lbl = tk.Label(hdr, text=self._tr("lon_lbl"), font=_font(9),
                           bg=BG_PANEL, fg=TEXT_DIM)
        lon_lbl.pack(side=tk.RIGHT)
        self._tr_widgets["lon_lbl"] = lon_lbl
        lat_e = tk.Entry(hdr, textvariable=self._qth_lat_var, width=7,
                         bg=BG_SURFACE, fg=TEXT_H1, insertbackground=TEXT_H1,
                         relief=tk.FLAT, font=_font(9))
        lat_e.pack(side=tk.RIGHT, padx=(2, 4))
        lat_e.bind("<Return>",    self._apply_qth)
        lat_e.bind("<FocusOut>",  self._apply_qth)
        qth_lbl = tk.Label(hdr, text=self._tr("qth_lat_lbl"), font=_font(9),
                           bg=BG_PANEL, fg=TEXT_DIM)
        qth_lbl.pack(side=tk.RIGHT, padx=(8, 0))
        self._tr_widgets["qth_lat_lbl"] = qth_lbl

        # Taal selector
        tk.Frame(hdr, bg=BORDER, width=1).pack(side=tk.RIGHT, fill=tk.Y, pady=8)
        lang_mb = tk.Menubutton(hdr, textvariable=self._lang_var,
                                font=_font(9), bg=BG_SURFACE, fg=TEXT_H1,
                                relief=tk.FLAT, activebackground=BG_HOVER,
                                activeforeground=TEXT_H1, width=10,
                                anchor='w', padx=6, pady=3, cursor="hand2")
        lang_menu = tk.Menu(lang_mb, tearoff=False, bg=BG_SURFACE, fg=TEXT_H1,
                            activebackground=ACCENT, activeforeground=BG_ROOT,
                            font=_font(9))
        for name in _LANG_NAMES:
            lang_menu.add_command(label=name,
                                  command=lambda v=name: (self._lang_var.set(v),
                                                          self._on_lang_change()))
        lang_mb["menu"] = lang_menu
        lang_mb.pack(side=tk.RIGHT, padx=(0, 4))
        lang_lbl = tk.Label(hdr, text=self._tr("lang_lbl"), font=_font(9),
                            bg=BG_PANEL, fg=TEXT_DIM)
        lang_lbl.pack(side=tk.RIGHT, padx=(8, 2))
        self._tr_widgets["lang_lbl"] = lang_lbl

        # Interval keuze in header
        tk.Frame(hdr, bg=BORDER, width=1).pack(side=tk.RIGHT, fill=tk.Y, pady=8)
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
        auto_lbl = tk.Label(hdr, text=self._tr("auto_lbl"), font=_font(9),
                            bg=BG_PANEL, fg=TEXT_DIM)
        auto_lbl.pack(side=tk.RIGHT, padx=(4, 2))
        self._tr_widgets["auto_lbl"] = auto_lbl

        # Ticker onderaan (pack VOOR body zodat hij aan de onderkant blijft)
        self._build_ticker()

        # Hoofd body — 3 kolommen: Kaart | Panelen | Solar  +  onderaan DX + Advies
        body = tk.Frame(self.root, bg=BG_ROOT)
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 4))

        # Bovenste rij: Kaart | Hist/Schema/Prop | Solar
        top_row = tk.Frame(body, bg=BG_ROOT)
        top_row.pack(fill=tk.BOTH, expand=True)

        # Solar rechts (eerst pack zodat hij niet wordt verdrongen)
        solar_col = tk.Frame(top_row, bg=BG_PANEL, width=210, height=SOLAR_MIN_H)
        solar_col.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        solar_col.pack_propagate(False)

        tk.Frame(solar_col, bg=ACCENT, height=2).pack(fill=tk.X)
        _solar_hdr_lbl = tk.Label(solar_col, text=self._tr("solar"),
                                  font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT,
                                  pady=8)
        _solar_hdr_lbl.pack(anchor='w', padx=10)
        self._tr_widgets["solar"] = _solar_hdr_lbl

        self._solar_frame = tk.Frame(solar_col, bg=BG_PANEL)
        self._solar_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        _SOLAR_TIPS_LANG = {
            "nl": {
                "sfi":        ("Solar Flux Index (SFI)",
                               "Maat voor de radioactiviteit van de zon op 10,7 cm.\n"
                               "< 80: laag  |  80–120: matig  |  > 150: hoog\n"
                               "Hogere SFI → betere ionisatie → hogere MUF."),
                "ssn":        ("Sunspot Number (SSN)",
                               "Aantal zonneplekken. Hoog SSN correleert met hogere SFI\n"
                               "en betere HF-propagatie, vooral op de hogere banden."),
                "a_index":    ("A-index (dagelijks)",
                               "Dagelijkse maat voor geomagnetische activiteit (0–400).\n"
                               "< 10: rustig  |  10–29: onrustig  |  ≥ 30: storm\n"
                               "Hoge waarden verstoren de ionosfeer (verhoogde LUF)."),
                "k_index":    ("K-index (3-uurs)",
                               "3-uurs geomagnetische activiteit (0–9).\n"
                               "0–2: rustig  |  3–4: onrustig  |  5+: storm\n"
                               "Direct effect op HF-absorptie en poolroutes."),
                "xray":       ("X-ray flux (GOES)",
                               "Röntgenflux van de zon. Klasse A/B/C/M/X.\n"
                               "X-flares kunnen de ionosfeer op dag-zijde plotseling\n"
                               "blokkeren (SWF – Short Wave Fadeout)."),
                "muf":        ("Maximum Usable Frequency (MUF)",
                               "Hoogste frequentie die op een bepaald pad weerkaatst\n"
                               "wordt door de F2-laag. Banden boven de MUF zijn dicht.\n"
                               "Berekend via foF2 × oblique factor 3,8."),
                "luf":        ("Lowest Usable Frequency (LUF)",
                               "Laagste frequentie die bruikbaar is door D-laag absorptie.\n"
                               "Banden onder de LUF worden te sterk geabsorbeerd.\n"
                               "Stijgt met hogere K-index en aurorale activiteit."),
                "sw_speed":   ("Solarwindsnelheid (km/s)",
                               "Snelheid van de solarwind gemeten door DSCOVR/ACE (NOAA).\n"
                               "< 400: rustig  |  400–600: verhoogd  |  > 600: stormachtig\n"
                               "Hogere snelheid kan geomagnetische activiteit verhogen."),
                "sw_bz":      ("Bz — interplanetair magneetveld (nT)",
                               "Noordwaartse (positief) of zuidwaartse (negatief) component\n"
                               "van het interplanetair magneetveld (IMF).\n"
                               "Bz < −10 nT: kans op geomagnetische storm neemt sterk toe.\n"
                               "Negatieve Bz koppelt aan het aardveld → verhoogde K-index."),
                "iono_fof2":  ("Ionosonde foF2 — gemeten vs model (MHz)",
                               "foF2 = kritische frequentie van de F2-laag (ionosonde-meting).\n"
                               "Gemeten: actuele waarde van de dichtstbijzijnde Europese\n"
                               "ionosonde (GIRO/LGDC DIDBase, interval ≈15 min).\n"
                               "Model: HAMIOS-berekening op basis van SFI en SSN.\n"
                               "Groen = goede overeenkomst  |  Oranje = matige afwijking\n"
                               "Rood = grote afwijking (storm of ongewone activiteit)."),
                "proton_flux":("Proton flux >10 MeV (pfu)",
                               "Hoog-energetische protonen van zonne-uitbarstingen.\n"
                               "< 10 pfu: normaal  |  ≥ 10: S1 (PCA mogelijk)\n"
                               "≥ 100 pfu: S3 — poolroutes geblokkeerd\n"
                               "≥ 1000 pfu: S5 — ernstige PCA, alle poolpaden dicht\n"
                               "PCA blokkeert poolroutes 1–7 dagen."),
            },
            "en": {
                "sfi":        ("Solar Flux Index (SFI)",
                               "Measure of solar radio activity at 10.7 cm.\n"
                               "< 80: low  |  80–120: moderate  |  > 150: high\n"
                               "Higher SFI → better ionisation → higher MUF."),
                "ssn":        ("Sunspot Number (SSN)",
                               "Number of sunspots. High SSN correlates with higher SFI\n"
                               "and better HF propagation, especially on higher bands."),
                "a_index":    ("A-index (daily)",
                               "Daily measure of geomagnetic activity (0–400).\n"
                               "< 10: quiet  |  10–29: unsettled  |  ≥ 30: storm\n"
                               "High values disturb the ionosphere (elevated LUF)."),
                "k_index":    ("K-index (3-hourly)",
                               "3-hourly geomagnetic activity (0–9).\n"
                               "0–2: quiet  |  3–4: unsettled  |  5+: storm\n"
                               "Direct effect on HF absorption and polar routes."),
                "xray":       ("X-ray flux (GOES)",
                               "Solar X-ray flux. Class A/B/C/M/X.\n"
                               "X-flares can suddenly block the dayside ionosphere\n"
                               "(SWF – Short Wave Fadeout)."),
                "muf":        ("Maximum Usable Frequency (MUF)",
                               "Highest frequency reflected by the F2 layer on a given path.\n"
                               "Bands above the MUF are closed.\n"
                               "Calculated via foF2 × oblique factor 3.8."),
                "luf":        ("Lowest Usable Frequency (LUF)",
                               "Lowest usable frequency due to D-layer absorption.\n"
                               "Bands below the LUF are too strongly absorbed.\n"
                               "Rises with higher K-index and auroral activity."),
                "sw_speed":   ("Solar wind speed (km/s)",
                               "Solar wind speed measured by DSCOVR/ACE (NOAA).\n"
                               "< 400: quiet  |  400–600: elevated  |  > 600: stormy\n"
                               "Higher speed can increase geomagnetic activity."),
                "sw_bz":      ("Bz — interplanetary magnetic field (nT)",
                               "Northward (positive) or southward (negative) component\n"
                               "of the interplanetary magnetic field (IMF).\n"
                               "Bz < −10 nT: geomagnetic storm risk increases strongly.\n"
                               "Negative Bz couples to Earth's field → elevated K-index."),
                "iono_fof2":  ("Ionosonde foF2 — measured vs model (MHz)",
                               "foF2 = critical frequency of the F2 layer (ionosonde measurement).\n"
                               "Measured: current value from the nearest European\n"
                               "ionosonde (GIRO/LGDC DIDBase, interval ≈15 min).\n"
                               "Model: HAMIOS calculation based on SFI and SSN.\n"
                               "Green = good match  |  Orange = moderate deviation\n"
                               "Red = large deviation (storm or unusual activity)."),
                "proton_flux":("Proton flux >10 MeV (pfu)",
                               "High-energy protons from solar eruptions.\n"
                               "< 10 pfu: normal  |  ≥ 10: S1 (PCA possible)\n"
                               "≥ 100 pfu: S3 — polar routes blocked\n"
                               "≥ 1000 pfu: S5 — severe PCA, all polar paths closed\n"
                               "PCA blocks polar routes 1–7 days."),
            },
            "de": {
                "sfi":        ("Solarfluxindex (SFI)",
                               "Maß für die Radioaktivität der Sonne bei 10,7 cm.\n"
                               "< 80: niedrig  |  80–120: mäßig  |  > 150: hoch\n"
                               "Höherer SFI → bessere Ionisation → höhere MUF."),
                "ssn":        ("Sonnenfleckenanzahl (SSN)",
                               "Anzahl der Sonnenflecken. Hohe SSN korreliert mit höherem SFI\n"
                               "und besserer KW-Ausbreitung, besonders auf hohen Bändern."),
                "a_index":    ("A-Index (täglich)",
                               "Tägliches Maß für geomagnetische Aktivität (0–400).\n"
                               "< 10: ruhig  |  10–29: unruhig  |  ≥ 30: Sturm\n"
                               "Hohe Werte stören die Ionosphäre (erhöhte LUF)."),
                "k_index":    ("K-Index (3-stündlich)",
                               "3-stündliche geomagnetische Aktivität (0–9).\n"
                               "0–2: ruhig  |  3–4: unruhig  |  5+: Sturm\n"
                               "Direkter Einfluss auf KW-Absorption und Polarrouten."),
                "xray":       ("Röntgenfluss (GOES)",
                               "Solarer Röntgenfluss. Klasse A/B/C/M/X.\n"
                               "X-Flares können die Tagseite der Ionosphäre plötzlich\n"
                               "blockieren (SWF – Short Wave Fadeout)."),
                "muf":        ("Maximal nutzbare Frequenz (MUF)",
                               "Höchste an der F2-Schicht reflektierte Frequenz.\n"
                               "Bänder oberhalb der MUF sind geschlossen.\n"
                               "Berechnet via foF2 × Schrägfaktor 3,8."),
                "luf":        ("Niedrigste nutzbare Frequenz (LUF)",
                               "Niedrigste nutzbare Frequenz durch D-Schicht-Absorption.\n"
                               "Bänder unterhalb der LUF werden zu stark absorbiert.\n"
                               "Steigt mit höherem K-Index und Polarlichtaktivität."),
                "sw_speed":   ("Sonnenwindgeschwindigkeit (km/s)",
                               "Sonnenwindgeschwindigkeit gemessen von DSCOVR/ACE (NOAA).\n"
                               "< 400: ruhig  |  400–600: erhöht  |  > 600: stürmisch\n"
                               "Höhere Geschwindigkeit kann geomagnetische Aktivität erhöhen."),
                "sw_bz":      ("Bz — Interplanetares Magnetfeld (nT)",
                               "Nordwärts (positiv) oder südwärts (negativ) Komponente\n"
                               "des interplanetaren Magnetfelds (IMF).\n"
                               "Bz < −10 nT: Geomagnetsturmrisiko steigt stark.\n"
                               "Negatives Bz koppelt an Erdfeld → erhöhter K-Index."),
                "iono_fof2":  ("Ionosonde foF2 — gemessen vs Modell (MHz)",
                               "foF2 = kritische Frequenz der F2-Schicht (Ionosonden-Messung).\n"
                               "Gemessen: aktueller Wert der nächsten europäischen\n"
                               "Ionosonde (GIRO/LGDC DIDBase, Intervall ≈15 min).\n"
                               "Modell: HAMIOS-Berechnung auf Basis von SFI und SSN.\n"
                               "Grün = gute Übereinstimmung  |  Orange = mäßige Abweichung\n"
                               "Rot = große Abweichung (Sturm oder ungewöhnliche Aktivität)."),
                "proton_flux":("Protonenfluss >10 MeV (pfu)",
                               "Hochenergetische Protonen aus Sonneneruptionen.\n"
                               "< 10 pfu: normal  |  ≥ 10: S1 (PCA möglich)\n"
                               "≥ 100 pfu: S3 — Polarrouten gesperrt\n"
                               "≥ 1000 pfu: S5 — schwere PCA, alle Polarwege geschlossen\n"
                               "PCA sperrt Polarrouten 1–7 Tage."),
            },
            "fr": {
                "sfi":        ("Indice de flux solaire (SFI)",
                               "Mesure de l'activité radio solaire à 10,7 cm.\n"
                               "< 80: faible  |  80–120: modéré  |  > 150: élevé\n"
                               "SFI plus élevé → meilleure ionisation → MUF plus haute."),
                "ssn":        ("Nombre de taches solaires (SSN)",
                               "Nombre de taches solaires. SSN élevé corrèle avec SFI plus haut\n"
                               "et meilleure propagation HF, surtout sur les bandes hautes."),
                "a_index":    ("Indice A (quotidien)",
                               "Mesure quotidienne de l'activité géomagnétique (0–400).\n"
                               "< 10: calme  |  10–29: agité  |  ≥ 30: tempête\n"
                               "Valeurs élevées perturbent l'ionosphère (LUF élevée)."),
                "k_index":    ("Indice K (3-horaire)",
                               "Activité géomagnétique sur 3 heures (0–9).\n"
                               "0–2: calme  |  3–4: agité  |  5+: tempête\n"
                               "Effet direct sur l'absorption HF et les routes polaires."),
                "xray":       ("Flux X (GOES)",
                               "Flux de rayons X solaires. Classe A/B/C/M/X.\n"
                               "Les éruptions X peuvent soudainement bloquer l'ionosphère\n"
                               "côté jour (SWF – Short Wave Fadeout)."),
                "muf":        ("Fréquence Maximale Utilisable (MUF)",
                               "Fréquence la plus haute réfléchie par la couche F2.\n"
                               "Les bandes au-dessus de la MUF sont fermées.\n"
                               "Calculée via foF2 × facteur oblique 3,8."),
                "luf":        ("Fréquence Minimale Utilisable (LUF)",
                               "Fréquence la plus basse utilisable malgré l'absorption couche D.\n"
                               "Les bandes sous la LUF sont trop absorbées.\n"
                               "Augmente avec un K-index élevé et l'activité aurorale."),
                "sw_speed":   ("Vitesse du vent solaire (km/s)",
                               "Vitesse du vent solaire mesurée par DSCOVR/ACE (NOAA).\n"
                               "< 400: calme  |  400–600: élevé  |  > 600: tempétueux\n"
                               "Une vitesse plus élevée peut augmenter l'activité géomagnétique."),
                "sw_bz":      ("Bz — champ magnétique interplanétaire (nT)",
                               "Composante vers le nord (positif) ou le sud (négatif)\n"
                               "du champ magnétique interplanétaire (IMF).\n"
                               "Bz < −10 nT: risque de tempête géomagnétique fortement accru.\n"
                               "Bz négatif se couple au champ terrestre → K-index élevé."),
                "iono_fof2":  ("Ionosonde foF2 — mesuré vs modèle (MHz)",
                               "foF2 = fréquence critique de la couche F2 (mesure ionosonde).\n"
                               "Mesuré: valeur actuelle de l'ionosonde européenne la plus proche\n"
                               "(GIRO/LGDC DIDBase, intervalle ≈15 min).\n"
                               "Modèle: calcul HAMIOS basé sur SFI et SSN.\n"
                               "Vert = bonne correspondance  |  Orange = déviation modérée\n"
                               "Rouge = grande déviation (tempête ou activité inhabituelle)."),
                "proton_flux":("Flux de protons >10 MeV (pfu)",
                               "Protons de haute énergie provenant d'éruptions solaires.\n"
                               "< 10 pfu: normal  |  ≥ 10: S1 (PCA possible)\n"
                               "≥ 100 pfu: S3 — routes polaires bloquées\n"
                               "≥ 1000 pfu: S5 — PCA sévère, tous les chemins polaires fermés\n"
                               "La PCA bloque les routes polaires 1–7 jours."),
            },
            "it": {
                "sfi":        ("Indice di flusso solare (SFI)",
                               "Misura dell'attività radio solare a 10,7 cm.\n"
                               "< 80: basso  |  80–120: moderato  |  > 150: alto\n"
                               "SFI più alto → migliore ionizzazione → MUF più alta."),
                "ssn":        ("Numero di macchie solari (SSN)",
                               "Numero di macchie solari. SSN alto correla con SFI più alto\n"
                               "e migliore propagazione HF, specialmente sulle bande alte."),
                "a_index":    ("Indice A (giornaliero)",
                               "Misura giornaliera dell'attività geomagnetica (0–400).\n"
                               "< 10: tranquillo  |  10–29: agitato  |  ≥ 30: tempesta\n"
                               "Valori alti disturbano l'ionosfera (LUF elevata)."),
                "k_index":    ("Indice K (ogni 3 ore)",
                               "Attività geomagnetica ogni 3 ore (0–9).\n"
                               "0–2: tranquillo  |  3–4: agitato  |  5+: tempesta\n"
                               "Effetto diretto sull'assorbimento HF e le rotte polari."),
                "xray":       ("Flusso X (GOES)",
                               "Flusso di raggi X solari. Classe A/B/C/M/X.\n"
                               "Le eruzioni X possono bloccare improvvisamente l'ionosfera\n"
                               "sul lato giorno (SWF – Short Wave Fadeout)."),
                "muf":        ("Frequenza Massima Utilizzabile (MUF)",
                               "Frequenza più alta riflessa dallo strato F2.\n"
                               "Le bande sopra la MUF sono chiuse.\n"
                               "Calcolata tramite foF2 × fattore obliquo 3,8."),
                "luf":        ("Frequenza Minima Utilizzabile (LUF)",
                               "Frequenza più bassa utilizzabile nonostante l'assorbimento strato D.\n"
                               "Le bande sotto la LUF sono troppo assorbite.\n"
                               "Aumenta con K-index più alto e attività aurorale."),
                "sw_speed":   ("Velocità del vento solare (km/s)",
                               "Velocità del vento solare misurata da DSCOVR/ACE (NOAA).\n"
                               "< 400: tranquillo  |  400–600: elevato  |  > 600: tempestoso\n"
                               "Velocità più alta può aumentare l'attività geomagnetica."),
                "sw_bz":      ("Bz — campo magnetico interplanetario (nT)",
                               "Componente verso nord (positivo) o sud (negativo)\n"
                               "del campo magnetico interplanetario (IMF).\n"
                               "Bz < −10 nT: rischio tempesta geomagnetica fortemente aumentato.\n"
                               "Bz negativo si accoppia al campo terrestre → K-index elevato."),
                "iono_fof2":  ("Ionosonda foF2 — misurato vs modello (MHz)",
                               "foF2 = frequenza critica dello strato F2 (misurazione ionosonda).\n"
                               "Misurato: valore attuale dell'ionosonda europea più vicina\n"
                               "(GIRO/LGDC DIDBase, intervallo ≈15 min).\n"
                               "Modello: calcolo HAMIOS basato su SFI e SSN.\n"
                               "Verde = buona corrispondenza  |  Arancione = deviazione moderata\n"
                               "Rosso = grande deviazione (tempesta o attività insolita)."),
                "proton_flux":("Flusso protonico >10 MeV (pfu)",
                               "Protoni ad alta energia da eruzioni solari.\n"
                               "< 10 pfu: normale  |  ≥ 10: S1 (PCA possibile)\n"
                               "≥ 100 pfu: S3 — rotte polari bloccate\n"
                               "≥ 1000 pfu: S5 — PCA grave, tutti i percorsi polari chiusi\n"
                               "PCA blocca le rotte polari 1–7 giorni."),
            },
            "es": {
                "sfi":        ("Índice de flujo solar (SFI)",
                               "Medida de la actividad de radio solar a 10,7 cm.\n"
                               "< 80: bajo  |  80–120: moderado  |  > 150: alto\n"
                               "SFI más alto → mejor ionización → MUF más alta."),
                "ssn":        ("Número de manchas solares (SSN)",
                               "Número de manchas solares. SSN alto correlaciona con SFI más alto\n"
                               "y mejor propagación HF, especialmente en bandas altas."),
                "a_index":    ("Índice A (diario)",
                               "Medida diaria de la actividad geomagnética (0–400).\n"
                               "< 10: tranquilo  |  10–29: agitado  |  ≥ 30: tormenta\n"
                               "Valores altos perturban la ionosfera (LUF elevada)."),
                "k_index":    ("Índice K (cada 3 horas)",
                               "Actividad geomagnética cada 3 horas (0–9).\n"
                               "0–2: tranquilo  |  3–4: agitado  |  5+: tormenta\n"
                               "Efecto directo en la absorción HF y rutas polares."),
                "xray":       ("Flujo de rayos X (GOES)",
                               "Flujo de rayos X solar. Clase A/B/C/M/X.\n"
                               "Los destellos X pueden bloquear repentinamente la ionosfera\n"
                               "del lado diurno (SWF – Short Wave Fadeout)."),
                "muf":        ("Frecuencia Máxima Utilizable (MUF)",
                               "Frecuencia más alta reflejada por la capa F2 en una ruta dada.\n"
                               "Las bandas por encima de la MUF están cerradas.\n"
                               "Calculada via foF2 × factor oblicuo 3,8."),
                "luf":        ("Frecuencia Mínima Utilizable (LUF)",
                               "Frecuencia más baja utilizable debido a la absorción de la capa D.\n"
                               "Las bandas por debajo de la LUF son demasiado absorbidas.\n"
                               "Aumenta con mayor índice K y actividad auroral."),
                "sw_speed":   ("Velocidad del viento solar (km/s)",
                               "Velocidad del viento solar medida por DSCOVR/ACE (NOAA).\n"
                               "< 400: tranquilo  |  400–600: elevado  |  > 600: tormentoso\n"
                               "Mayor velocidad puede aumentar la actividad geomagnética."),
                "sw_bz":      ("Bz — campo magnético interplanetario (nT)",
                               "Componente hacia el norte (positivo) o sur (negativo)\n"
                               "del campo magnético interplanetario (IMF).\n"
                               "Bz < −10 nT: riesgo de tormenta geomagnética aumenta fuertemente.\n"
                               "Bz negativo se acopla al campo terrestre → índice K elevado."),
                "iono_fof2":  ("Ionosonda foF2 — medido vs modelo (MHz)",
                               "foF2 = frecuencia crítica de la capa F2 (medición ionosonda).\n"
                               "Medido: valor actual de la ionosonda europea más cercana\n"
                               "(GIRO/LGDC DIDBase, intervalo ≈15 min).\n"
                               "Modelo: cálculo HAMIOS basado en SFI y SSN.\n"
                               "Verde = buena coincidencia  |  Naranja = desviación moderada\n"
                               "Rojo = gran desviación (tormenta o actividad inusual)."),
                "proton_flux":("Flujo de protones >10 MeV (pfu)",
                               "Protones de alta energía de erupciones solares.\n"
                               "< 10 pfu: normal  |  ≥ 10: S1 (PCA posible)\n"
                               "≥ 100 pfu: S3 — rutas polares bloqueadas\n"
                               "≥ 1000 pfu: S5 — PCA grave, todos los caminos polares cerrados\n"
                               "PCA bloquea rutas polares 1–7 días."),
            },
        }

        def _get_solar_tips(lang: str) -> dict:
            return _SOLAR_TIPS_LANG.get(lang, _SOLAR_TIPS_LANG["en"])

        def _bind_tip(widget, key):
            tt = _Tooltip(widget)
            lang = _LANG_CODES.get(self._lang_var.get(), "nl")
            tips_dict = _get_solar_tips(lang)
            title, body = tips_dict.get(key, ("", ""))
            text = f"{title}\n{'─' * len(title)}\n{body}" if title else ""
            widget.bind("<Enter>", lambda e, t=tt, tx=text:
                        t.show(e.widget.winfo_rootx() + e.x,
                               e.widget.winfo_rooty() + e.y, tx)
                        if tx and self._show_tips_var.get() else None)
            widget.bind("<Leave>", lambda *_, t=tt: t.hide())

        self._solar_vars     = {}
        self._solar_val_lbls = {}   # key → Label widget (voor kleur-updates)
        # Dynamisch label voor ionosonde-rij (stationsnaam wordt ingevuld na fetch)
        self._iono_station_var = tk.StringVar(value="foF2 ms/md:")
        for key, label in [
            ("sfi",         "Solar Flux (SFI)"),
            ("ssn",         "Sunspot Nr (SSN)"),
            ("a_index",     "A-index"),
            ("k_index",     "K-index"),
            ("xray",        "X-ray"),
            ("muf",         "MUF (MHz)"),
            ("luf",         "LUF (MHz)"),
            ("sw_speed",    "Solarwind (km/s)"),
            ("sw_bz",       "Bz (nT)"),
            ("proton_flux", "Proton >10MeV"),
            ("iono_fof2",   None),      # None → dynamisch label via StringVar
        ]:
            row = tk.Frame(self._solar_frame, bg=BG_PANEL)
            row.pack(fill=tk.X, pady=2)
            if label is None:
                # Ionosonde-rij: label tekst is dynamisch
                lbl = tk.Label(row, textvariable=self._iono_station_var,
                               font=_font(9), bg=BG_PANEL,
                               fg=TEXT_DIM, anchor='w', width=16, cursor="question_arrow")
            else:
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

            # Melding K ≥ direct onder K-index, waarde uitgelijnd met getallen-kolom
            if key == "k_index":
                alert_row = tk.Frame(self._solar_frame, bg=BG_PANEL)
                alert_row.pack(fill=tk.X, pady=(0, 2))
                _k_alert_lbl = tk.Label(alert_row, text=self._tr("k_alert_lbl"),
                                        font=_font(9), bg=BG_PANEL,
                                        fg=TEXT_DIM, anchor='w', width=16)
                _k_alert_lbl.pack(side=tk.LEFT)
                self._tr_widgets["k_alert_lbl"] = _k_alert_lbl
                tk.Spinbox(alert_row, from_=1, to=9, width=3,
                           textvariable=self._k_alert_var,
                           command=self._save_cur_settings,
                           bg=BG_SURFACE, fg=TEXT_H1, buttonbackground=BG_SURFACE,
                           relief=tk.FLAT, font=_font(9, "bold")).pack(side=tk.LEFT)

        # Scheidingslijn tussen params en bandentabel
        tk.Frame(self._solar_frame, bg=BORDER, height=1).pack(fill=tk.X, pady=(4, 2))

        # Bandentabel
        hdr_row = tk.Frame(self._solar_frame, bg=BG_PANEL)
        hdr_row.pack(fill=tk.X, pady=(0, 0))
        for key, w in [("band_hdr", 6), ("day_hdr", 6), ("night_hdr", 6)]:
            lbl = tk.Label(hdr_row, text=self._tr(key), font=_font(9, "bold"),
                           bg=BG_PANEL, fg=ACCENT, width=w, anchor='w')
            lbl.pack(side=tk.LEFT)
            self._tr_widgets.setdefault(key, [])
            self._tr_widgets[key] = (self._tr_widgets[key]
                                     if isinstance(self._tr_widgets[key], list)
                                     else [self._tr_widgets[key]])
            self._tr_widgets[key].append(lbl)

        self._band_cond_labels: dict = {}   # band → (day_lbl, ngt_lbl, is_hf)
        for name, _, is_hf in _BANDS:
            if not is_hf:
                continue   # VHF/UHF niet tonen in solar-panel bandtabel
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

        # Scheidingslijn + waarschuwingen direct ónder de bandentabel
        tk.Frame(self._solar_frame, bg=BORDER, height=1).pack(fill=tk.X, pady=(4, 2))

        # X-flare waarschuwing — natuurlijke hoogte (geen vaste height=)
        self._xflare_lbl = tk.Label(self._solar_frame, textvariable=self._xflare_var,
                                    font=_font(8, "bold"), bg=BG_PANEL, fg="#FF7043",
                                    wraplength=190, justify='left', anchor='nw')
        self._xflare_lbl.pack(fill=tk.X, pady=(0, 2))

        # PCA-waarschuwing (proton event — paars) — natuurlijke hoogte
        self._pca_var = tk.StringVar(value="")
        self._pca_lbl = tk.Label(self._solar_frame, textvariable=self._pca_var,
                                 font=_font(8, "bold"), bg=BG_PANEL, fg="#CE93D8",
                                 wraplength=190, justify='left', anchor='nw')
        self._pca_lbl.pack(fill=tk.X, pady=(0, 4))

        # ── Gecombineerde linker+midden zone ──────────────────────────────────
        combined = tk.Frame(top_row, bg=BG_ROOT)
        combined.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Sub-rij: Kaart+Hist+DX links (vaste breedte) | Prop+Schema rechts (expand)
        sub_row = tk.Frame(combined, bg=BG_ROOT)
        sub_row.pack(fill=tk.BOTH, expand=True)

        # Linkerkolom: Bandopenings-schema + Hist + DX (vaste breedte)
        left_sub = tk.Frame(sub_row, bg=BG_ROOT, width=480)
        left_sub.pack(side=tk.LEFT, fill=tk.Y)
        left_sub.pack_propagate(False)
        self._build_schedule_panel(left_sub)
        self._build_hist_panel(left_sub)
        self._build_dx_panel(left_sub)

        right_sub = tk.Frame(sub_row, bg=BG_ROOT)
        right_sub.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        self._build_map_panel(right_sub)
        self._build_prop_panel(right_sub)  # HF Betrouwbaarheid onder Wereldkaart

        # Advies: volledige breedte onderin body (over alle kolommen inclusief Solar)
        self._build_advice_panel(body)

    # ── Wereldkaart panel ─────────────────────────────────────────────────────
    def _build_map_panel(self, parent):
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.X, pady=(0, 0))
        tk.Frame(outer, bg=ACCENT, height=2).pack(fill=tk.X)

        map_hdr = tk.Frame(outer, bg=BG_PANEL)
        map_hdr.pack(fill=tk.X)
        map_title = tk.Label(map_hdr, text=self._tr("worldmap"),
                             font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT,
                             pady=4)
        map_title.pack(side=tk.LEFT, padx=10)
        self._tr_widgets["worldmap"] = map_title

        def _cb(tr_key, var, fallback_text=""):
            def _on_toggle():
                self._save_cur_settings()
                self._draw_map()
            cb = tk.Checkbutton(map_hdr, text=self._tr(tr_key) if tr_key else fallback_text,
                                variable=var, command=_on_toggle,
                                bg=BG_PANEL, fg=TEXT_DIM, selectcolor=BG_SURFACE,
                                activebackground=BG_PANEL, activeforeground=TEXT_BODY,
                                font=_font(9))
            cb.pack(side=tk.RIGHT, padx=(0, 8))
            if tr_key:
                self._tr_widgets.setdefault(tr_key, [])
                if isinstance(self._tr_widgets[tr_key], list):
                    self._tr_widgets[tr_key].append(cb)
                else:
                    self._tr_widgets[tr_key] = [self._tr_widgets[tr_key], cb]

        _cb("locator",  self._show_locator_var)
        _cb(None,       self._show_cs_var,       "CS")
        _cb(None,       self._show_iaru_var,      "ITU")
        _cb(None,       self._show_spots_var,    "Spots")
        _cb(None,       self._show_wspr_var,     "WSPR")
        _cb("graylijn", self._show_graylijn_var)
        _cb("moon",     self._show_moon_var)
        _cb("sun",      self._show_sun_var)

        self._map_canvas = tk.Canvas(outer, height=200, bg="#1B3A5C",
                                     bd=0, highlightthickness=0)
        self._map_canvas.pack(fill=tk.X, padx=10, pady=(2, 2))
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
        """Stel canvas hoogte in; rendering gebruikt altijd 2:1 ratio."""
        new_h = max(80, min(event.width // 2, 320))
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
        VW = int(W * max(1.0, self._map_zoom))
        VH = int(W // 2 * max(1.0, self._map_zoom))
        wx  = self._map_crop_left + vx
        wy  = self._map_crop_top  + vy
        lon = wx / VW * 360 - 180
        lat = 90 - wy / VH * 180
        return lat, lon

    def _on_map_click(self, vx: int, vy: int):
        """Klik op kaart: DX-spot popup als Spots aan staat, anders groot-cirkel."""
        # Controleer eerst of er een DX-spot stip is geraakt
        if self._show_spots_var.get():
            for hit in self._spot_hit_areas:
                if abs(vx - hit["x"]) <= hit["r"] and abs(vy - hit["y"]) <= hit["r"]:
                    s = hit["spot"]
                    self._gc_info_var.set(
                        f"📡  {s.get('dx','')}  {s.get('freq_mhz','')} MHz"
                        f"  [{s.get('band','')}]  "
                        f"spotter: {s.get('spotter','')}  —  {s.get('comment','')}"
                    )
                    return
        lat, lon = self._viewport_to_latlon(vx, vy)
        self._gc_dest = (lat, lon)
        dist = _haversine_km(self._qth_lat, self._qth_lon, lat, lon)
        hdg  = _bearing_deg(self._qth_lat, self._qth_lon, lat, lon)
        self._gc_info_var.set(
            f"→  {lat:+.1f}°, {lon:+.1f}°  |  {self._tr('distance_lbl')}: {dist:,.0f} km  "
            f"|  {self._tr('direction_lbl')}: {hdg:.0f}°  ({self._tr('right_clk_clear')})")
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
        zoom      = max(1.0, self._map_zoom)
        d_lon     = -dx / W       * (360 / zoom)
        d_lat     =  dy / (W // 2) * (180 / zoom)
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
        # Bepaal lat/lon onder cursor vóór zoom (VH altijd 2:1)
        VW_old   = int(W * old_zoom)
        VH_old   = int(W // 2 * old_zoom)
        wx_old   = self._map_crop_left + event.x
        wy_old   = self._map_crop_top  + event.y
        lon_cur  = wx_old / VW_old * 360 - 180
        lat_cur  = 90 - wy_old / VH_old * 180
        # Nieuw center zodat cursor dezelfde lat/lon wijst
        VW_new   = int(W * new_zoom)
        VH_new   = int(W // 2 * new_zoom)
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
        # Virtuele wereld-afmetingen: altijd 2:1 ongeacht canvas-hoogte
        zoom = max(1.0, self._map_zoom)
        VW   = int(W * zoom)
        VH   = int(W // 2 * zoom)

        if not _PIL_OK:
            c.delete("all")
            c.create_rectangle(0, 0, W, H, fill="#1B3A5C", outline="")
            c.create_text(W // 2, H // 2,
                          text=self._tr("map_nolib"),
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
                    (6, 4), self._tr("map_downloading"), fill=MAP_GRID)

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
            self._map_render_key = None   # basiskaart veranderd → forceer re-render

        # ── Render-cache sleutel (alles behalve pan-positie cx/cy) ───────────
        sun_lat, sun_lon = _subsolar_point()
        try:
            k_val = float(self._solar_data.get("k_index", "0").replace("—", "0"))
        except (ValueError, TypeError, AttributeError):
            k_val = 0.0

        render_key = (
            VW, VH,
            round(sun_lat, 1), round(sun_lon, 1),
            bool(self._show_sun_var.get()),
            bool(self._show_moon_var.get()),
            bool(self._show_graylijn_var.get()),
            bool(self._show_iaru_var.get()),
            bool(self._show_locator_var.get()),
            bool(self._show_cs_var.get()),
            int(k_val),
            round(self._qth_lat, 2), round(self._qth_lon, 2),
            self._gc_dest,
        )

        if getattr(self, "_map_render_key", None) != render_key:
            # ── Volledige render (alleen bij echte inhoud-wijziging) ──────────
            img  = self._map_base_img.copy()

            # Nacht overlay — masker op ¼ resolutie → 16× sneller, zacht genoeg
            NW, NH = max(1, VW // 4), max(1, VH // 4)
            night_small = _night_mask(sun_lat, sun_lon, NW, NH)
            night = night_small.resize((VW, VH), Image.BILINEAR)
            img   = Image.alpha_composite(img.convert("RGBA"), night).convert("RGB")
            draw  = ImageDraw.Draw(img)

            # ── Zon ──────────────────────────────────────────────────────────
            if self._show_sun_var.get():
                sx, sy = _ll_to_xy(sun_lat, sun_lon, VW, VH)
                draw.ellipse([(sx - 7, sy - 7), (sx + 7, sy + 7)],
                             fill=MAP_SUN, outline=(200, 160, 0), width=1)

            # ── Maan ─────────────────────────────────────────────────────────
            if self._show_moon_var.get():
                moon_lat, moon_lon = _submoon_point()
                mx, my = _ll_to_xy(moon_lat, moon_lon, VW, VH)
                draw.ellipse([(mx - 5, my - 5), (mx + 5, my + 5)],
                             fill=MAP_MOON, outline=(150, 150, 150), width=1)

            # ── Graylijn — ook op ¼ resolutie ────────────────────────────────
            if self._show_graylijn_var.get():
                gray_small = _graylijn_mask(sun_lat, sun_lon, NW, NH)
                gray = gray_small.resize((VW, VH), Image.BILINEAR)
                img  = Image.alpha_composite(img.convert("RGBA"), gray).convert("RGB")
                draw = ImageDraw.Draw(img)

            # ── ITU regio-overlay (correcte R1/R2/R3 grenzen) ────────────────
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

                # ── Gevulde regio-polygonen ───────────────────────────────
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

                # ── Grenslijnen ───────────────────────────────────────────
                for pts, clr, w in [
                    (_ITU_B,     (255, 200,  80, AL), 2),   # R1/R2
                    (_ITU_A,     ( 80, 220, 100, AL), 2),   # R1/R3 Arabisch deel
                    (_ITU_A_RUS, ( 80, 220, 100, AL), 2),   # R1/R3 Rusland-arm
                    (_ITU_C,     (160, 220, 160, AL), 1),   # R2/R3 Pacific
                ]:
                    px = _px(pts)
                    for j in range(len(px) - 1):
                        id_.line([px[j], px[j+1]], fill=clr, width=w)

                # ── Labels (volledige naam) ────────────────────────────────
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

            # ── Maidenhead locatorraster ──────────────────────────────────────
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

            # ── Auroraal absorptie-ovaal (K≥4) ───────────────────────────────
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

            # ── Groot-cirkel pad ──────────────────────────────────────────────
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

            # ── Callsign-prefix labels ────────────────────────────────────────
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

            # ── QTH marker (alleen kruisje) ───────────────────────────────────
            qx, qy = _ll_to_xy(self._qth_lat, self._qth_lon, VW, VH)
            draw.line([(qx - 10, qy), (qx + 10, qy)], fill=MAP_QTH, width=2)
            draw.line([(qx, qy - 10), (qx, qy + 10)], fill=MAP_QTH, width=2)

            # Sla volledig gerenderde afbeelding op in cache
            self._map_render_img = img
            self._map_render_key = render_key

        # ── Pan = alleen crop uit gecachede afbeelding (microseconden) ────────
        img = self._map_render_img
        if zoom > 1.0:
            world_cx = int((self._map_cx + 180) / 360 * VW)
            world_cy = int((90 - self._map_cy) / 180 * VH)
            crop_l   = max(0, min(VW - W, world_cx - W // 2))
            crop_t   = max(0, min(VH - H, world_cy - H // 2))
            img      = img.crop((crop_l, crop_t, crop_l + W, crop_t + H))
        else:
            crop_l = 0
            # VH = W//2 maar canvas H kan kleiner zijn → centreer op evenaar
            crop_t = max(0, (VH - H) // 2)
            if crop_t > 0:
                img = img.crop((0, crop_t, W, crop_t + H))
        self._map_crop_left = crop_l
        self._map_crop_top  = crop_t

        # ── Tonen ────────────────────────────────────────────────────────────
        self._map_photo = ImageTk.PhotoImage(img)
        c.delete("all")
        c.create_image(0, 0, anchor='nw', image=self._map_photo)
        self._draw_dx_spots()
        self._draw_wspr_spots()

    def _draw_dx_spots(self):
        """Teken DX-spot stippen en lijnen als canvas-items over de kaart."""
        self._spot_hit_areas = []
        if not getattr(self, "_show_spots_var", None) or not self._show_spots_var.get():
            return
        spots = getattr(self, "_dx_all_spots", [])
        if not spots:
            return
        c  = self._map_canvas
        W  = c.winfo_width()  or 960
        VW = int(W * max(1.0, self._map_zoom))
        VH = VW // 2
        cl = self._map_crop_left
        ct = self._map_crop_top

        seen: set = set()   # dedup per DX-callsign (toon max 1 stip per DX)
        for spot in spots[:80]:
            dx_pos = _prefix_latlon(spot.get("dx", ""))
            if not dx_pos:
                continue
            dx_mx, dx_my = _ll_to_xy(dx_pos[0], dx_pos[1], VW, VH)
            dx_vx = dx_mx - cl
            dx_vy = dx_my - ct
            color = _SPOT_BAND_CLR.get(spot.get("band", ""), "#AAAAAA")

            # Lijn van spotter naar DX
            sp_pos = _prefix_latlon(spot.get("spotter", ""))
            if sp_pos:
                sp_mx, sp_my = _ll_to_xy(sp_pos[0], sp_pos[1], VW, VH)
                c.create_line(sp_mx - cl, sp_my - ct, dx_vx, dx_vy,
                              fill=color, width=1, dash=(3, 3))

            # Stip op DX-locatie (één per uniek callsign)
            dx_key = spot.get("dx", "")
            if dx_key not in seen:
                seen.add(dx_key)
                r = 4
                c.create_oval(dx_vx - r, dx_vy - r, dx_vx + r, dx_vy + r,
                              fill=color, outline="white", width=1)
                self._spot_hit_areas.append(
                    {"x": dx_vx, "y": dx_vy, "r": r + 4, "spot": spot})

    def _draw_wspr_spots(self):
        """Teken WSPR-verbindingslijnen als canvas-items over de kaart."""
        if not getattr(self, "_show_wspr_var", None) or not self._show_wspr_var.get():
            return
        spots = getattr(self, "_wspr_spots", [])
        if not spots:
            return
        c  = self._map_canvas
        W  = c.winfo_width() or 960
        VW = int(W * max(1.0, self._map_zoom))
        VH = VW // 2
        cl = self._map_crop_left
        ct = self._map_crop_top

        for spot in spots:
            color = _SPOT_BAND_CLR.get(spot["band"], "#888888")
            # Lijndikte op basis van SNR: ≤-20 → 1, -20..-5 → 2, >-5 → 3
            snr = spot["snr"]
            width = 1 if snr <= -20 else (2 if snr <= -5 else 3)

            tx_x, tx_y = _ll_to_xy(spot["tx_lat"], spot["tx_lon"], VW, VH)
            rx_x, rx_y = _ll_to_xy(spot["rx_lat"], spot["rx_lon"], VW, VH)
            c.create_line(tx_x - cl, tx_y - ct, rx_x - cl, rx_y - ct,
                          fill=color, width=width)

            # Klein stipje op de ontvanger
            r = 2
            c.create_oval(rx_x - cl - r, rx_y - ct - r,
                          rx_x - cl + r, rx_y - ct + r,
                          fill=color, outline="")

    # ── HF Propagatie panel ───────────────────────────────────────────────────
    def _build_prop_panel(self, parent):
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.BOTH, expand=True, pady=(0, 0))

        tk.Frame(outer, bg=ACCENT, height=2).pack(fill=tk.X)
        prop_hdr = tk.Frame(outer, bg=BG_PANEL)
        prop_hdr.pack(fill=tk.X, padx=10, pady=(2, 0))
        _prop_title = tk.Label(prop_hdr, text=self._tr("prop_header"),
                               font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT)
        _prop_title.pack(side=tk.LEFT)
        self._tr_widgets["prop_header"] = _prop_title
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

        _menubutton(ctrl, self._mode_var,  list(_MODE_DB.keys()),  self._tr("mode_lbl"),  width=5)
        _menubutton(ctrl, self._power_var, list(_POWER_DB.keys()), self._tr("power_lbl"), width=5)
        _menubutton(ctrl, self._ant_var,   list(_ANT_DB.keys()),   self._tr("ant_lbl"),   width=18)

        _day_auto_cb = tk.Checkbutton(ctrl, text=self._tr("day_auto"),
                                      variable=self._day_var,
                                      command=self._recalc_prop,
                                      bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                                      activebackground=BG_PANEL, font=_font(9))
        _day_auto_cb.pack(side=tk.LEFT, padx=(4, 0))
        self._tr_widgets["day_auto"] = _day_auto_cb

        info = tk.Frame(outer, bg=BG_PANEL)
        info.pack(fill=tk.X, padx=10, pady=(0, 4))
        self._muf_var = tk.StringVar(value="MUF: —")
        self._luf_var = tk.StringVar(value="LUF: —")
        self._db_var  = tk.StringVar(value="0 dB")
        for var, fg in [(self._muf_var, TEXT_H1), (self._luf_var, TEXT_H1),
                        (self._db_var, ACCENT)]:
            tk.Label(info, textvariable=var, font=_font(9, "bold"),
                     bg=BG_PANEL, fg=fg).pack(side=tk.LEFT, padx=(0, 18))

        BAR_H    = 13
        BAR_PAD  = 1
        HDR_H    = 14
        _hf_count = sum(1 for _, _, is_hf in _BANDS if is_hf)
        canvas_h = HDR_H + _hf_count * (BAR_H + BAR_PAD) + BAR_PAD + 2
        self._prop_canvas = tk.Canvas(outer, height=canvas_h, bg=BG_PANEL,
                                      bd=0, highlightthickness=0)
        self._prop_canvas.pack(fill=tk.X, padx=10, pady=(0, 8))
        self._prop_canvas.bind("<Configure>",
                               lambda *_: self._draw_prop_bars(self._last_band_pct))
        self._bar_rows: list = []   # (y_top, y_bot, tooltip_text)
        self._tooltip  = _Tooltip(self._prop_canvas)
        self._prop_canvas.bind("<Motion>",   self._on_bar_motion)
        self._prop_canvas.bind("<Leave>",    self._on_bar_leave)
        self._prop_canvas.bind("<Button-1>", self._on_bar_click)

        # VFO-A/B frequentie + terminal toggle (wordt verborgen als CAT uit)
        self._cat_info_frame = tk.Frame(outer, bg=BG_PANEL)
        self._cat_freq_lbl = tk.Label(self._cat_info_frame, textvariable=self._cat_freq_var,
                                      font=_font(10, "bold"), bg=BG_PANEL,
                                      fg=ACCENT, anchor="w")
        self._cat_freq_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
        _cat_term_cb = tk.Checkbutton(self._cat_info_frame, text="Terminal",
                                      variable=self._cat_terminal_var,
                                      command=self._toggle_cat_terminal,
                                      bg=BG_PANEL, fg=TEXT_DIM,
                                      selectcolor=BG_SURFACE,
                                      activebackground=BG_PANEL,
                                      font=_font(8), cursor="hand2")
        _cat_term_cb.pack(side=tk.RIGHT, padx=(4, 0))

        # CAT terminal venster (verborgen tot checkbox aan)
        self._cat_terminal_frame = tk.Frame(outer, bg=BG_PANEL)
        _term_inner = tk.Frame(self._cat_terminal_frame, bg=BG_PANEL)
        _term_inner.pack(fill=tk.BOTH, expand=True, pady=(0, 4))
        _term_sb = tk.Scrollbar(_term_inner, orient=tk.VERTICAL,
                                bg=BG_SURFACE, troughcolor=BG_PANEL)
        self._cat_terminal_txt = tk.Text(
            _term_inner, height=5,
            bg=BG_SURFACE, fg=TEXT_BODY,
            font=("Consolas", 8),
            state=tk.DISABLED, wrap=tk.NONE,
            yscrollcommand=_term_sb.set,
            bd=0, padx=4, pady=2)
        _term_sb.config(command=self._cat_terminal_txt.yview)
        _term_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._cat_terminal_txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._cat_terminal_txt.tag_configure("tx", foreground="#FFCA28")
        self._cat_terminal_txt.tag_configure("rx", foreground="#80CFFF")
        self._cat_terminal_txt.tag_configure("info", foreground=TEXT_DIM)

        self._update_cat_freq_lbl_visibility()

    def _draw_prop_bars(self, band_pct):
        self._last_band_pct = band_pct
        c = self._prop_canvas
        c.delete("all")
        self._bar_rows = []
        self._bar_band_rows = []

        W       = c.winfo_width() or 700
        BAR_H   = 13
        BAR_PAD = 1
        HDR_H   = 14
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

        hf_pct = [(n, f, p) for n, f, p in band_pct if p != -1]
        for i, entry in enumerate(hf_pct):
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

            if pct == 0:
                # Band volledig gesloten — zelfde stijl als LOS/Tropo
                c.create_rectangle(BAR_X, y, BAR_X + BAR_MAX, y + BAR_H,
                                   fill=BG_SURFACE, outline=BORDER, width=1)
                c.create_text(BAR_X + BAR_MAX // 2, y + BAR_H // 2,
                              text=self._tr("closed"), font=("Segoe UI", 8),
                              fill=TEXT_DIM, anchor='center')
                c.create_text(BAR_X + BAR_MAX + PCT_W // 2, y + BAR_H // 2,
                              text="0%", font=("Segoe UI", 9, "bold"),
                              fill=TEXT_DIM, anchor='center')
                tip = [
                    (f"{name}  ·  {freq_str}", None),
                    None,
                    (self._tr("status_lbl"),   self._tr("closed")),
                    (self._tr("reason_lbl"),   self._tr("reason_muf_luf")),
                    (self._tr("modes_lbl"),    _BAND_MODES.get(name, "—")),
                    ("FT8:",                   _BAND_FT8.get(name, "—") + " MHz"),
                ]
            else:
                # HF: kleurenbalk
                c.create_rectangle(BAR_X, y, BAR_X + BAR_MAX, y + BAR_H,
                                   fill=BG_SURFACE, outline=BORDER, width=1)
                color = "#4CAF50" if pct >= 60 else ("#FFC107" if pct >= 30 else "#F44336")
                cond  = (self._tr("cond_good") if pct >= 60 else
                         (self._tr("cond_fair") if pct >= 30 else self._tr("cond_poor")))
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
                    (self._tr("reliability_lbl"), f"{pct}%  –  {cond}"),
                    (self._tr("modes_lbl"),        _BAND_MODES.get(name, "—")),
                    ("FT8:",                       _BAND_FT8.get(name, "—") + " MHz"),
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
            self._bar_band_rows.append((y, y + BAR_H, name, freq))

        # VFO-A / VFO-B markers (alleen als CAT ingeschakeld)
        if self._cat_enabled_var.get():
            _band_y = {r[2]: (r[0], r[1]) for r in self._bar_band_rows}
            for vfo_hz, label, color in [
                    (self._cat_vfo_a_hz, "A", "#FFFFFF"),
                    (self._cat_vfo_b_hz, "B", "#80CFFF")]:
                if not vfo_hz:
                    continue
                vfo_khz = vfo_hz / 1000
                for bname, lo, hi in _BAND_RANGES_KHZ:
                    if lo <= vfo_khz <= hi and bname in _band_y:
                        y0, y1 = _band_y[bname]
                        x = BAR_X + max(1, min(BAR_MAX - 1,
                                               int(BAR_MAX * (vfo_khz - lo) / (hi - lo))))
                        c.create_line(x, y0, x, y1, fill=color, width=2)
                        c.create_text(x, y0 - 1, text=label,
                                      font=("Segoe UI", 7, "bold"),
                                      fill=color, anchor="s")
                        break

    def _on_bar_motion(self, event: tk.Event):
        for y0, y1, _ in self._bar_rows:
            if y0 <= event.y <= y1:
                self._prop_canvas.config(cursor="hand2")
                if self._show_tips_var.get():
                    rx = self._prop_canvas.winfo_rootx() + event.x
                    ry = self._prop_canvas.winfo_rooty() + event.y
                    self._tooltip.show(rx, ry, _)
                return
        self._prop_canvas.config(cursor="")
        self._tooltip.hide()

    def _on_bar_leave(self, _event=None):
        self._prop_canvas.config(cursor="")
        self._tooltip.hide()

    def _on_bar_click(self, event: tk.Event):
        """Klik op een bandbalk → stuur startfrequentie naar radio via CAT."""
        port = self._cat_port_var.get().strip()
        if not port:
            return
        for y0, y1, _, freq_mhz in self._bar_band_rows:
            if y0 <= event.y <= y1:
                freq_hz = int(freq_mhz * 1_000_000)
                baud = int(self._cat_baud_var.get())
                bits = int(self._cat_bits_var.get())
                par  = self._cat_parity_var.get()
                stop = float(self._cat_stopbits_var.get())
                radio = self._cat_radio_var.get()
                lock = self._cat_poll_lock

                def _send(fn, args):
                    with lock:
                        fn(*args)

                if radio == "Icom CI-V":
                    try:
                        addr = int(self._cat_civ_addr_var.get(), 0)
                    except ValueError:
                        addr = 0x70
                    self._cat_terminal_log(f"▶ <CI-V set freq={freq_hz} Hz addr=0x{addr:02X}>", "tx")
                    threading.Thread(
                        target=_send,
                        args=(_icom_set_freq, (port, baud, bits, par, stop, freq_hz, addr)),
                        daemon=True,
                    ).start()
                elif radio == "Kenwood / Elecraft":
                    self._cat_terminal_log(f"▶ FA{freq_hz:011d};", "tx")
                    threading.Thread(
                        target=_send,
                        args=(_kenwood_set_freq, (port, baud, bits, par, stop, freq_hz)),
                        daemon=True,
                    ).start()
                else:  # Yaesu CAT (default)
                    self._cat_terminal_log(f"▶ VS0;FA{freq_hz:011d};", "tx")
                    threading.Thread(
                        target=_send,
                        args=(_yaesu_set_freq, (port, baud, bits, par, stop, freq_hz)),
                        daemon=True,
                    ).start()
                self._cat_vfo_a_hz = freq_hz
                self._cat_freq_var.set(f"VFO-A:  {_fmt_freq_hz(freq_hz)}")
                break

    # ── Historiek panel ───────────────────────────────────────────────────────
    def _build_hist_panel(self, parent):
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.X, pady=(6, 0))

        tk.Frame(outer, bg=ACCENT, height=2).pack(fill=tk.X)

        hdr = tk.Frame(outer, bg=BG_PANEL)
        hdr.pack(fill=tk.X, padx=10, pady=(4, 2))
        _hist_title = tk.Label(hdr, text=self._tr("hist_header"),
                               font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT)
        _hist_title.pack(side=tk.LEFT)
        self._tr_widgets["hist_header"] = _hist_title

        # Radiobuttons: value = interne NL-sleutel (opgeslagen in INI), text = vertaald
        _HIST_RANGE_KEYS = [("Uren", "hist_range_h"), ("Dagen", "hist_range_d"),
                            ("Weken", "hist_range_w"), ("Maanden", "hist_range_m")]
        self._hist_range_rbs: list = []   # [(rb_widget, tr_key), …] voor live-vertaling
        for val, tr_key in _HIST_RANGE_KEYS:
            rb = tk.Radiobutton(hdr, text=self._tr(tr_key),
                                variable=self._hist_range_var,
                                value=val,
                                command=lambda: (self._save_cur_settings(), self._draw_hist_graph()),
                                bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                                activebackground=BG_PANEL, activeforeground=TEXT_H1,
                                font=_font(9))
            rb.pack(side=tk.LEFT, padx=(8, 0))
            self._hist_range_rbs.append((rb, tr_key))

        self._hist_canvas = tk.Canvas(outer, height=75, bg=BG_PANEL,
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

        # ── Banden historiek ─────────────────────────────────────────────────────
        # Y-raster
        for pct in (0, 25, 50, 75, 100):
            gy = PAD_T + gh - int(gh * pct / 100)
            c.create_line(PAD_L, gy, W - PAD_R, gy,
                          fill=BORDER, dash=(2, 4))
            c.create_text(PAD_L - 3, gy, text=str(pct),
                          fill=TEXT_DIM, font=("Segoe UI", 7), anchor='e')

        if len(data) < 2:
            c.create_text(W // 2, PAD_T + gh // 2,
                          text=self._tr("no_hist_data"),
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
            for ts, bp, _ in data:
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

    # ── Bandopenings-schema (heatmap) ─────────────────────────────────────────
    def _build_schedule_panel(self, parent):
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.X, pady=(0, 0))
        tk.Frame(outer, bg=ACCENT, height=2).pack(fill=tk.X)

        hdr = tk.Frame(outer, bg=BG_PANEL)
        hdr.pack(fill=tk.X, padx=10, pady=(4, 2))
        _sched_title = tk.Label(hdr, text=self._tr("sched_header"),
                                font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT)
        _sched_title.pack(side=tk.LEFT)
        self._tr_widgets["sched_header"] = _sched_title
        self._sched_canvas = tk.Canvas(outer, height=180, bg=BG_PANEL,
                                       bd=0, highlightthickness=0)
        self._sched_canvas.pack(fill=tk.X, padx=10, pady=(0, 6))
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
        tip = [(self._tr("hist_tooltip_hdr").format(ts=local_ts), None), None]
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
            kwal = self._tr("cond_good")
        elif pct >= 30:
            kwal = self._tr("cond_fair")
        elif pct >= 1:
            kwal = self._tr("cond_poor")
        else:
            kwal = self._tr("cond_closed")
        tip = [
            (f"{bname}  —  {local_str} ({self._tr('local_lbl')})", None),
            None,
            (self._tr("quality_lbl"),     kwal),
            (self._tr("reliability_lbl"), f"{pct}%"),
            ("FT8:",                      _BAND_FT8.get(bname, "—") + " MHz"),
            (self._tr("modes_lbl"),       _BAND_MODES.get(bname, "—")),
        ]
        rx = self._sched_canvas.winfo_rootx() + event.x
        ry = self._sched_canvas.winfo_rooty() + event.y
        self._sched_tooltip.show(rx, ry, tip)

    # ── DX Spots panel ───────────────────────────────────────────────────────
    def _build_dx_panel(self, parent):
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.BOTH, expand=True, pady=(6, 0))
        tk.Frame(outer, bg=ACCENT, height=2).pack(fill=tk.X)

        hdr = tk.Frame(outer, bg=BG_PANEL)
        hdr.pack(fill=tk.X, padx=10, pady=(4, 2))
        _dx_title = tk.Label(hdr, text=self._tr("dx_header"),
                             font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT)
        _dx_title.pack(side=tk.LEFT)
        self._tr_widgets["dx_header"] = _dx_title
        _dx_own_cb = tk.Checkbutton(hdr, text=self._tr("own_cont_lbl"),
                                    variable=self._dx_own_cont_var,
                                    command=self._filter_dx_spots,
                                    bg=BG_PANEL, fg=TEXT_DIM, selectcolor=BG_SURFACE,
                                    activebackground=BG_PANEL, activeforeground=TEXT_BODY,
                                    font=_font(9))
        _dx_own_cb.pack(side=tk.RIGHT, padx=(0, 4))
        self._tr_widgets["own_cont_lbl"] = _dx_own_cb

        status_row = tk.Frame(outer, bg=BG_PANEL)
        status_row.pack(fill=tk.X, padx=10)
        self._dx_status_var    = tk.StringVar(value=self._tr("dx_loading"))
        self._dx_countdown_var = tk.StringVar(value="")
        tk.Label(status_row, textvariable=self._dx_status_var,
                 font=_font(8), bg=BG_PANEL, fg=TEXT_DIM).pack(side=tk.LEFT)
        tk.Label(status_row, textvariable=self._dx_countdown_var,
                 font=_font(8), bg=BG_PANEL, fg=ACCENT).pack(side=tk.RIGHT)

        dx_wrap = tk.Frame(outer, bg=BG_PANEL)
        dx_wrap.pack(fill=tk.BOTH, expand=True, padx=10, pady=(2, 6))
        self._dx_canvas = tk.Canvas(dx_wrap, height=180, bg=BG_PANEL,
                                    bd=0, highlightthickness=0)
        dx_sb = tk.Scrollbar(dx_wrap, orient=tk.VERTICAL,
                             command=self._dx_canvas.yview,
                             bg=BG_SURFACE, troughcolor=BG_ROOT, width=8)
        self._dx_canvas.configure(yscrollcommand=dx_sb.set)
        dx_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._dx_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
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
        filt  = self._tr("dx_own_cont_filter") if self._dx_own_cont_var.get() else ""
        total = len(self._dx_all_spots)
        ts    = datetime.datetime.now().strftime("%H:%M")
        if total:
            self._dx_status_var.set(
                self._tr("dx_status_fmt").format(n=n, total=total, filt=filt, ts=ts))
        else:
            self._dx_status_var.set(self._tr("no_spots_ts").format(ts=ts))

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
                          text=self._tr("no_dx_spots"),
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

    def _refresh_wspr(self):
        spots = _fetch_wspr_spots()
        self.root.after(0, lambda: self._on_wspr_spots(spots))

    def _on_wspr_spots(self, spots: list):
        self._wspr_spots = spots
        if self._show_wspr_var.get():
            self._draw_map()
        self._schedule_wspr()

    def _schedule_wspr(self):
        self._wspr_after_id = self.root.after(
            WSPR_REFRESH_SECS * 1000,
            lambda: threading.Thread(target=self._refresh_wspr, daemon=True).start()
        )

    # ── Advies panel ─────────────────────────────────────────────────────────
    def _build_advice_panel(self, parent):
        # Vaste hoogte op basis van constanten zodat winfo_reqheight() bij startup klopt
        outer = tk.Frame(parent, bg=BG_PANEL, height=ADV_SECTION_H)
        outer.pack(fill=tk.X, pady=(6, 0))
        outer.pack_propagate(False)
        tk.Frame(outer, bg=ACCENT, height=2).pack(fill=tk.X)
        adv_hdr = tk.Frame(outer, bg=BG_PANEL)
        adv_hdr.pack(fill=tk.X, padx=10, pady=(4, 0))
        _adv_title = tk.Label(adv_hdr, text=self._tr("adv_header"),
                              font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT)
        _adv_title.pack(side=tk.LEFT)
        self._tr_widgets["adv_header"] = _adv_title
        adv_h = ADV_ROWS * (ADV_CARD_H + ADV_CARD_GAP)
        adv_wrap = tk.Frame(outer, bg=BG_PANEL, height=adv_h)
        adv_wrap.pack(fill=tk.X, padx=10, pady=(0, 8))
        adv_wrap.pack_propagate(False)
        self._advice_frame = tk.Frame(adv_wrap, bg=BG_PANEL)
        self._advice_frame.pack(fill=tk.BOTH, expand=True)

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
            best  = hf_open[:5]
            bstr  = "  ·  ".join(f"{n} {p}%" for n, p in best)
            extra = self._tr("adv_best_extra").format(n=len(hf_open)) if len(hf_open) > 5 else ""
            tips.append(("📡", self._tr("adv_best_bands").format(bstr=bstr, extra=extra), "#4CAF50"))
        else:
            tips.append(("📡", self._tr("adv_no_bands"), TEXT_DIM))

        # ── 2. Geomagnetische condities (K + A) ────────────────────────────
        a_kwal = (self._tr("geo_quiet")    if a_index < 10 else
                  self._tr("geo_unsettled") if a_index < 30 else
                  self._tr("geo_storm")    if a_index < 100 else
                  self._tr("geo_severe"))
        k_i, a_i = int(k_index), int(a_index)
        if k_index >= 7:
            tips.append(("🚨", self._tr("adv_geo_severe").format(k=k_i, a=a_i, kwal=a_kwal),   "#F44336"))
        elif k_index >= 5:
            tips.append(("⚠️", self._tr("adv_geo_storm").format(k=k_i, a=a_i, kwal=a_kwal),    "#F44336"))
        elif k_index >= 3:
            tips.append(("⚡", self._tr("adv_geo_elevated").format(k=k_i, a=a_i, kwal=a_kwal), "#FFC107"))
        else:
            tips.append(("✅", self._tr("adv_geo_quiet").format(k=k_i, a=a_i),                  "#4CAF50"))

        # ── 3. Zonactiviteit / zonnecyclus ─────────────────────────────────
        s_i, ss_i = int(sfi), int(ssn)
        if sfi >= 200:
            tips.append(("🌟", self._tr("adv_sol_exceptional").format(sfi=s_i, ssn=ss_i), ACCENT))
        elif sfi >= 150:
            tips.append(("☀️", self._tr("adv_sol_high").format(sfi=s_i, ssn=ss_i),        ACCENT))
        elif sfi >= 100:
            tips.append(("🌤", self._tr("adv_sol_good").format(sfi=s_i, ssn=ss_i),        ACCENT))
        elif sfi >= 80:
            tips.append(("🌥", self._tr("adv_sol_moderate").format(sfi=s_i, ssn=ss_i),    TEXT_BODY))
        else:
            tips.append(("🌧", self._tr("adv_sol_low").format(sfi=s_i, ssn=ss_i),         TEXT_DIM))

        # ── 4. Solarwind en Bz ─────────────────────────────────────────────
        try:
            spd = float(sw_spd)
            bz  = float(sw_bz)
            spd_s = str(int(spd))
            bz_s  = f"{bz:+.1f}"
            if spd > 700 or bz <= -20:
                tips.append(("🌪", self._tr("adv_sw_stormy").format(spd=spd_s, bz=bz_s),   "#F44336"))
            elif spd > 500 or bz <= -10:
                tips.append(("💨", self._tr("adv_sw_elevated").format(spd=spd_s, bz=bz_s), "#FFC107"))
            elif bz > 5:
                tips.append(("🛡", self._tr("adv_sw_calm").format(spd=spd_s, bz=bz_s),     "#4CAF50"))
            else:
                tips.append(("💫", self._tr("adv_sw_normal").format(spd=spd_s, bz=bz_s),   TEXT_BODY))
        except (ValueError, TypeError):
            pass   # solarwind nog niet beschikbaar

        # ── 5. Proton event / PCA ─────────────────────────────────────────
        try:
            pf_adv = float(data.get("proton_flux", "0").replace("—", "0"))
        except (ValueError, TypeError):
            pf_adv = 0.0
        if pf_adv >= 1000:
            tips.append(("☢", self._tr("adv_pf_s5").format(pf=f"{pf_adv:.0f}"), "#EA80FC"))
        elif pf_adv >= 100:
            tips.append(("☢", self._tr("adv_pf_s3").format(pf=f"{pf_adv:.0f}"), "#CE93D8"))
        elif pf_adv >= 10:
            tips.append(("⚛", self._tr("adv_pf_s1").format(pf=f"{pf_adv:.1f}"), "#BA68C8"))
        else:
            tips.append(("⚛", self._tr("adv_pf_normal").format(pf=f"{pf_adv:.2f}"), TEXT_DIM))

        # ── 6. X-ray / flares ─────────────────────────────────────────────
        xclass = xray[:1].upper() if xray else ""
        if xclass == "X":
            tips.append(("☢", self._tr("adv_xflare_x").format(xray=xray), "#F44336"))
        elif xclass == "M":
            tips.append(("⚡", self._tr("adv_xflare_m").format(xray=xray), "#FFC107"))

        # ── 7. Ionosfeer / MUF / LUF ──────────────────────────────────────
        try:
            muf = float(data.get("muf", "0").replace("—", "0"))
            if muf > 0:
                if muf >= 28:
                    muf_txt = self._tr("adv_muf_28").format(muf=f"{muf:.1f}")
                elif muf >= 14:
                    muf_txt = self._tr("adv_muf_14").format(muf=f"{muf:.1f}", muf0=f"{muf:.0f}")
                elif muf >= 7:
                    muf_txt = self._tr("adv_muf_7").format(muf=f"{muf:.1f}")
                else:
                    muf_txt = self._tr("adv_muf_low").format(muf=f"{muf:.1f}")
                luf_est  = 3.5 + k_index * 0.8
                luf_note = (self._tr("adv_luf_elevated") if k_index >= 3
                            else self._tr("adv_luf_normal"))
                tips.append(("📶",
                             self._tr("adv_iono_fmt").format(
                                 muf_txt=muf_txt, luf=f"{luf_est:.1f}", luf_note=luf_note),
                             TEXT_BODY))
        except (ValueError, TypeError):
            pass

        # ── 8. Dag/nacht + transitievensters ──────────────────────────────
        utc_h = datetime.datetime.now(datetime.timezone.utc).hour
        tz_off = 2 if self._dst_var.get() else 1
        lok_h  = (utc_h + tz_off) % 24
        h_s    = f"{lok_h:02d}"
        if is_day:
            if 6 <= lok_h < 10:
                tips.append(("🌅", self._tr("adv_morning").format(h=h_s),   TEXT_BODY))
            elif 10 <= lok_h < 16:
                tips.append(("🌞", self._tr("adv_midday").format(h=h_s),    TEXT_BODY))
            else:
                tips.append(("🌇", self._tr("adv_afternoon").format(h=h_s), TEXT_BODY))
        else:
            if 22 <= lok_h or lok_h < 2:
                tips.append(("🌃", self._tr("adv_early_night").format(h=h_s),  TEXT_BODY))
            elif 2 <= lok_h < 6:
                tips.append(("🌌", self._tr("adv_night").format(h=h_s),        TEXT_BODY))
            else:
                tips.append(("🌄", self._tr("adv_pre_morning").format(h=h_s),  TEXT_BODY))

        # ── 9. Modus / vermogen advies ────────────────────────────────────
        mode   = self._mode_var.get()
        power  = self._power_var.get()
        snr_db = (_MODE_DB.get(mode, 0) + _POWER_DB.get(power, 0) +
                  _ANT_DB.get(self._ant_var.get(), 0))
        if hf_open:
            best_pct  = hf_open[0][1]
            best_band = hf_open[0][0]
            snr_s     = f"{snr_db:+d}"
            if best_pct < 30 and mode == "SSB":
                tips.append(("🔧",
                             self._tr("adv_mode_weak").format(pct=best_pct, band=best_band, snr=snr_s),
                             "#FFC107"))
            elif best_pct >= 60 and snr_db < -5:
                tips.append(("🔧",
                             self._tr("adv_mode_good").format(pct=best_pct, band=best_band, snr=snr_s),
                             TEXT_BODY))
            else:
                tips.append(("🔧",
                             self._tr("adv_mode_default").format(
                                 mode=mode, pct=best_pct, band=best_band, snr=snr_s),
                             TEXT_BODY))

        # ── 10. Absorptie & poolroutes ────────────────────────────────────
        lat = abs(self._qth_lat)
        if lat > 50 and k_index >= 4:
            tips.append(("🧲",
                         self._tr("adv_abs_high").format(k=k_i, lat=f"{lat:.0f}"),
                         "#FFC107"))
        elif lat > 45 and k_index >= 3:
            tips.append(("🧲",
                         self._tr("adv_abs_low").format(k=k_i, lat=f"{lat:.0f}"),
                         TEXT_BODY))

        # ── 11. Sporadic-E kans ───────────────────────────────────────────
        now_dt = datetime.datetime.now()
        month  = now_dt.month
        doy    = now_dt.timetuple().tm_yday
        es_score = 0
        if 5 <= month <= 8:
            es_score = 3 if month in (6, 7) else 2
        elif month in (12, 1):
            es_score = 1
        es_time_ok = (9 <= lok_h < 14) or (17 <= lok_h < 22)
        if es_score >= 2 and es_time_ok:
            tips.append(("⚡",
                         self._tr("adv_es_high").format(month=month, h=h_s),
                         "#66BB6A"))
        elif es_score >= 2:
            tips.append(("⚡",
                         self._tr("adv_es_seasonal").format(month=month),
                         TEXT_DIM))
        elif es_score == 1 and es_time_ok:
            tips.append(("⚡",
                         self._tr("adv_es_winter").format(month=month, h=h_s),
                         TEXT_DIM))
        if (75 <= doy <= 120 or 265 <= doy <= 310) and 12 <= lok_h <= 18:
            tips.append(("🌐",
                         self._tr("adv_tep").format(doy=doy, h=h_s),
                         "#4FC3F7"))

        # ── 12. Propagatie trend (historische data) ───────────────────────
        if len(self._history) >= 4:
            latest_ts, latest_bp, latest_sol = self._history[-1]
            target_ts = latest_ts - datetime.timedelta(hours=2)
            ref = None
            for ts, bp_h, sol_h in reversed(self._history[:-1]):
                if ts <= target_ts:
                    ref = (ts, bp_h, sol_h)
                    break
            if ref is None:
                ref = self._history[0]
            ref_ts, ref_bp, ref_sol = ref
            age_h = (latest_ts - ref_ts).total_seconds() / 3600

            sfi_delta  = latest_sol.get("sfi", sfi)     - ref_sol.get("sfi", sfi)
            k_delta    = latest_sol.get("k_index", k_index) - ref_sol.get("k_index", k_index)
            hf_names   = [n for n, _, hf in _BANDS if hf]
            avg_now    = sum(latest_bp.get(n, 0) for n in hf_names) / max(len(hf_names), 1)
            avg_ref    = sum(ref_bp.get(n, 0)    for n in hf_names) / max(len(hf_names), 1)
            band_delta = avg_now - avg_ref

            trend_parts = []
            if abs(sfi_delta) >= 3:
                trend_parts.append(f"SFI {sfi_delta:+.0f}")
            if abs(k_delta) >= 1:
                trend_parts.append(f"K-index {k_delta:+.0f}")
            if abs(band_delta) >= 5:
                trend_parts.append(
                    f"{self._tr('avg_band_quality')} {band_delta:+.0f}%")

            if trend_parts:
                direction = (self._tr("trend_improving") if band_delta > 0
                             else self._tr("trend_worsening"))
                trend_clr = "#66BB6A" if band_delta > 0 else "#FF7043"
                tips.append(("📈" if band_delta > 0 else "📉",
                             self._tr("adv_trend_change").format(
                                 direction=direction, age=f"{age_h:.0f}",
                                 parts="  ·  ".join(trend_parts)),
                             trend_clr))
            else:
                tips.append(("📊",
                             self._tr("adv_trend_stable").format(age=f"{age_h:.0f}"),
                             TEXT_DIM))

        # ── 13. Zonnecyclus fase ──────────────────────────────────────────
        if ssn >= 130:
            tips.append(("☀",  self._tr("adv_sc_max").format(ssn=ss_i),        ACCENT))
        elif ssn >= 90:
            tips.append(("🌤", self._tr("adv_sc_high").format(ssn=ss_i),       ACCENT))
        elif ssn >= 50:
            tips.append(("🌥", self._tr("adv_sc_rising").format(ssn=ss_i),     TEXT_BODY))
        elif ssn >= 20:
            tips.append(("🌦", self._tr("adv_sc_transition").format(ssn=ss_i), TEXT_DIM))
        else:
            tips.append(("🌧", self._tr("adv_sc_low").format(ssn=ss_i),        TEXT_DIM))

        # ── 14. Herstelprognose bij K-storm ──────────────────────────────
        if k_index >= 5:
            recovery_h = (36 if a_index >= 50 else
                          24 if a_index >= 30 else
                          12 if a_index >= 20 else 6)
            tips.append(("🕐",
                         self._tr("adv_storm_recovery").format(
                             a=a_i, k=k_i, rh=recovery_h),
                         "#FF7043"))

        # ── 15. DX-cluster activiteitsanalyse ────────────────────────────
        all_spots = getattr(self, "_dx_all_spots", [])
        if all_spots:
            cont_count: dict = {}
            for s in all_spots:
                dx_cont = s.get("dx_cont", "??")
                cont_count[dx_cont] = cont_count.get(dx_cont, 0) + 1
            top_conts = sorted(cont_count.items(), key=lambda x: -x[1])[:4]
            top_str   = "  ·  ".join(f"{c}: {n}" for c, n in top_conts)
            n_as = cont_count.get("AS", 0)
            n_oc = cont_count.get("OC", 0)
            tip_txt = self._tr("adv_dx_cluster").format(n=len(all_spots), top=top_str)
            if n_oc >= 2:
                tip_txt += self._tr("adv_dx_oceania").format(n=n_oc)
            if n_as >= 3:
                tip_txt += self._tr("adv_dx_asia").format(n=n_as)
            tips.append(("📡", tip_txt.strip(), TEXT_BODY))

        # ── 16. Beste DX-routes nu ────────────────────────────────────────
        try:
            muf_dx = float(data.get("muf", "0").replace("—", "0"))
        except (ValueError, TypeError):
            muf_dx = 0.0
        dx_routes = []
        if is_day:
            if 5 <= utc_h < 10 and muf_dx >= 14:
                dx_routes.append(self._tr("dx_route_eu_ja_day"))
            if 12 <= utc_h < 18 and muf_dx >= 14:
                dx_routes.append(self._tr("dx_route_eu_w_day"))
            if 8 <= utc_h < 14 and muf_dx >= 14:
                dx_routes.append(self._tr("dx_route_eu_af_day"))
            if 14 <= utc_h < 20 and muf_dx >= 14:
                dx_routes.append(self._tr("dx_route_eu_oc_day"))
        else:
            if 22 <= utc_h or utc_h < 4:
                dx_routes.append(self._tr("dx_route_eu_w_night"))
            if 2 <= utc_h < 8:
                dx_routes.append(self._tr("dx_route_eu_ja_night"))
        if dx_routes:
            tips.append(("🌍",
                         self._tr("adv_dx_routes").format(routes="  ·  ".join(dx_routes)),
                         "#4FC3F7"))

        # ── 17. Algehele beoordeling ──────────────────────────────────────
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
        overall = (self._tr("score_excellent") if score >= 6 else
                   self._tr("score_good")       if score >= 4 else
                   self._tr("score_fair")        if score >= 2 else
                   self._tr("score_poor"))
        overall_clr = ("#4CAF50" if score >= 6 else
                       "#8BC34A" if score >= 4 else
                       "#FFC107" if score >= 2 else "#F44336")
        open_cnt  = len(hf_open)
        dn_label  = self._tr("day_label") if is_day else self._tr("night_label")
        tips.append(("📊",
                     self._tr("adv_overall_score").format(
                         overall=overall, sfi=s_i, k=k_i,
                         open=open_cnt, daynight=dn_label,
                         lat=f"{self._qth_lat:.1f}"),
                     overall_clr))

        # ── Weergave: 3 gelijke kolommen, vaste kaartengrootte ───────────
        COLS       = 3
        CARD_H     = ADV_CARD_H
        CARD_PAD_X = 8
        CARD_PAD_Y = 5

        for c in range(COLS):
            self._advice_frame.columnconfigure(c, weight=1)

        adv_labels: list = []   # bewaar label-refs voor wraplength-update

        _DOT = 8   # diameter gele stip per kaartje
        new_hashes: dict = {}

        for i, (icon, tekst, kleur) in enumerate(tips):
            col = i % COLS
            row = i // COLS
            self._advice_frame.rowconfigure(row, minsize=CARD_H)

            cell = tk.Frame(self._advice_frame, bg=BG_SURFACE,
                            padx=CARD_PAD_X, pady=CARD_PAD_Y,
                            height=CARD_H)
            cell.grid(row=row, column=col, sticky='nsew',
                      padx=(0, 4 if col < COLS - 1 else 0), pady=(0, 4))
            cell.pack_propagate(False)   # houd vaste hoogte, ongeacht tekst

            lbl = tk.Label(cell, text=f"{icon}  {tekst}", font=_font(9),
                           bg=BG_SURFACE, fg=kleur,
                           anchor='nw', wraplength=400, justify='left')
            lbl.pack(fill=tk.BOTH, expand=True)
            adv_labels.append(lbl)

            # Gele stip rechts boven in de kaart als inhoud gewijzigd is
            card_hash = hash((icon, tekst))
            new_hashes[i] = card_hash
            dot_fill = ("#FFCC00"
                        if (i not in self._advice_card_hashes or
                            self._advice_card_hashes[i] != card_hash)
                        else BG_SURFACE)
            dot_cv = tk.Canvas(cell, width=_DOT, height=_DOT,
                               bg=BG_SURFACE, highlightthickness=0, bd=0)
            dot_cv.place(relx=1.0, rely=0.0, anchor='ne', x=-3, y=4)
            dot_cv.create_oval(1, 1, _DOT - 1, _DOT - 1,
                               fill=dot_fill, outline="")

        self._advice_card_hashes = new_hashes

        # Pas wraplength dynamisch aan op kolombreedte bij resize
        def _on_adv_resize(event, _labels=adv_labels, _cols=COLS,
                           _px=CARD_PAD_X):
            col_w = max(120, (event.width - (_cols - 1) * 4) // _cols - _px * 2 - 4)
            for _l in _labels:
                try:
                    _l.config(wraplength=col_w)
                except tk.TclError:
                    pass

        self._advice_frame.bind("<Configure>", _on_adv_resize)

        # Stuur tips door naar de scrollende ticker onderaan
        self._update_ticker(tips)


    # ──────────────────────────────────────────────────────────────────────────
    # Ticker (scrollende prognose-balk onderaan het venster)
    # ──────────────────────────────────────────────────────────────────────────

    def _build_ticker(self):
        """Bouw de scrollende ticker-balk onderaan self.root."""
        self._ticker_outer = tk.Frame(self.root, bg=BG_PANEL, height=TICKER_H)
        if self._ticker_enabled_var.get():
            self._ticker_outer.pack(side=tk.BOTTOM, fill=tk.X)
        self._ticker_outer.pack_propagate(False)
        outer = self._ticker_outer
        tk.Frame(outer, bg=ACCENT, height=1).pack(side=tk.TOP, fill=tk.X)

        self._ticker_canvas = tk.Canvas(
            outer, bg=BG_PANEL, height=TICKER_H - 1,
            highlightthickness=0, bd=0
        )
        self._ticker_canvas.pack(fill=tk.BOTH, expand=True)

        self._ticker_text_id = self._ticker_canvas.create_text(
            0, (TICKER_H - 1) // 2,
            text="",
            fill=ACCENT,
            font=_font(9),
            anchor='w'
        )
        self._ticker_x      = 0      # huidige x-positie van het tekst-item
        self._ticker_speed  = 2      # pixels per tick
        self._ticker_active = False  # loopt de animatie al?
        self._ticker_msg    = ""     # volledige te scrollen tekst

    def _update_ticker(self, tips: list):
        """Stel nieuwe ticker-tekst in op basis van de tips-lijst."""
        if not hasattr(self, "_ticker_canvas"):
            return
        parts = []
        for icon, tekst, _ in tips:
            parts.append(f"{icon}  {tekst}")
        separator = "    ·    "
        full = separator.join(parts) + "    "
        self._ticker_msg = full

        # Zet tekst op canvas en bepaal breedte
        self._ticker_canvas.itemconfig(self._ticker_text_id, text=full)
        self._ticker_canvas.update_idletasks()
        bbox = self._ticker_canvas.bbox(self._ticker_text_id)
        text_w = (bbox[2] - bbox[0]) if bbox else 800
        canvas_w = max(self._ticker_canvas.winfo_width(), 1)

        # Begin rechts buiten beeld
        self._ticker_x = canvas_w
        self._ticker_canvas.coords(
            self._ticker_text_id,
            self._ticker_x,
            self._ticker_canvas.winfo_height() // 2
        )
        self._ticker_text_w = text_w

        if not self._ticker_active:
            self._ticker_active = True
            self._tick_ticker()

    def _toggle_ticker(self):
        """Toon of verberg de ticker-balk en sla de instelling op."""
        if not hasattr(self, "_ticker_outer"):
            return
        if self._ticker_enabled_var.get():
            self._ticker_outer.pack(side=tk.BOTTOM, fill=tk.X)
            # Herstart animatie als er tekst is
            if self._ticker_msg and not self._ticker_active:
                self._ticker_active = True
                self._tick_ticker()
        else:
            self._ticker_outer.pack_forget()
            self._ticker_active = False
        self._save_cur_settings()

    def _tick_ticker(self):
        """Animatie-loop: verschuif de ticker-tekst elke 30 ms."""
        if not hasattr(self, "_ticker_canvas"):
            return
        if not self._ticker_enabled_var.get():
            self._ticker_active = False
            return
        try:
            canvas_w  = max(self._ticker_canvas.winfo_width(), 1)
            text_w    = getattr(self, "_ticker_text_w", 800)
            self._ticker_x -= self._ticker_speed
            # Zodra de tekst volledig links buiten beeld is, start opnieuw rechts
            if self._ticker_x < -text_w:
                self._ticker_x = canvas_w
            self._ticker_canvas.coords(
                self._ticker_text_id,
                self._ticker_x,
                self._ticker_canvas.winfo_height() // 2
            )
            self.root.after(30, self._tick_ticker)
        except tk.TclError:
            self._ticker_active = False

    def _update_band_cond_panel(self, band_pct_day, band_pct_ngt):
        def _cond(pct):
            if pct == -1:  return "LOS",                        TEXT_DIM
            if pct >= 60:  return self._tr("cond_good"),        "#4CAF50"
            if pct >= 30:  return self._tr("cond_fair"),        "#FFC107"
            if pct >= 1:   return self._tr("cond_poor"),        "#F44336"
            return               self._tr("cond_closed"),       TEXT_DIM

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
        self._db_var.set(f"{self._tr('total_snr')} {snr_db:+d} dB")
        self._save_cur_settings()

        band_pct, muf, luf = _calc_propagation(
            sfi, ssn, k_index,
            qth_lat=self._qth_lat,
            snr_bonus_db=float(snr_db),
            daytime=is_day
        )
        self._muf_var.set(f"MUF: {muf} MHz")
        self._luf_var.set(f"LUF: {luf} MHz")
        if "muf" in self._solar_vars:
            self._solar_vars["muf"].set(f"{muf}")
        if "luf" in self._solar_vars:
            self._solar_vars["luf"].set(f"{luf}")
        # Model foF2 (dagtijd): wordt gebruikt voor vergelijking met ionosonde
        self._last_fof2_model: float = round(muf / 3.8, 2)
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

    # ── Instellingen opslaan ──────────────────────────────────────────────────
    def _save_cur_settings(self):
        _save_settings(self._qth_lat, self._qth_lon,
                       self._refresh_var.get(),
                       self._mode_var.get(),
                       self._power_var.get(),
                       self._ant_var.get(),
                       self._dst_var.get(),
                       self._show_tips_var.get(),
                       self._ticker_enabled_var.get(),
                       self._show_sun_var.get(),
                       self._show_moon_var.get(),
                       self._show_locator_var.get(),
                       self._show_graylijn_var.get(),
                       self._show_iaru_var.get(),
                       self._show_cs_var.get(),
                       self._show_spots_var.get(),
                       self._show_wspr_var.get(),
                       self._hist_range_var.get(),
                       self._hist_sel,
                       self._k_alert_var.get(),
                       self._lang_var.get(),
                       self._cat_port_var.get(),
                       self._cat_baud_var.get(),
                       self._cat_bits_var.get(),
                       self._cat_parity_var.get(),
                       self._cat_stopbits_var.get(),
                       self._cat_flow_var.get(),
                       self._cat_dtr_var.get(),
                       self._cat_rts_var.get(),
                       self._cat_enabled_var.get(),
                       self._cat_radio_var.get(),
                       self._cat_civ_addr_var.get())

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
            pystray.MenuItem(self._tr("tray_show"), self._tray_show, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(self._tr("tray_exit"), self._tray_quit),
        )
        self._tray_icon = pystray.Icon("HAMIOS", tray_img, "HAMIOS v2.3", menu)
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
        # Ionosonde: kies dichtstbijzijnde station o.b.v. QTH
        station = _nearest_iono_station(self._qth_lat, self._qth_lon)
        iono = _fetch_ionosonde(station[0])
        data["iono_fof2"]    = iono["fof2"]
        data["iono_time"]    = iono["time"]
        data["iono_station"] = iono["station"]
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
            pass  # foutmelding via tray-notificatie, geen solar-label meer
            self._schedule_solar()
            return

        for key, var in self._solar_vars.items():
            if key in ("muf", "luf"):
                continue   # worden bijgewerkt door _recalc_prop (model-waarden)
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

        # Proton flux kleur: paars kleurschema (S1→S5 schaal)
        try:
            pf_val = float(data.get("proton_flux", "0").replace("—", "0"))
            if pf_val >= 1000:
                pf_color = "#EA80FC"   # felpaars — S5
            elif pf_val >= 100:
                pf_color = "#CE93D8"   # middel-paars — S3/S4
            elif pf_val >= 10:
                pf_color = "#BA68C8"   # licht-paars — S1/S2
            else:
                pf_color = TEXT_H1
            if hasattr(self, "_solar_val_lbls") and "proton_flux" in self._solar_val_lbls:
                self._solar_val_lbls["proton_flux"].config(fg=pf_color)
        except (ValueError, TypeError):
            pf_val = 0.0

        # Ionosonde foF2: gemeten vs model — kleur op basis van overeenkomst
        iono_fof2_str  = data.get("iono_fof2",    "—")
        iono_time_str  = data.get("iono_time",    "—")
        iono_station   = data.get("iono_station", "—")
        fof2_model     = getattr(self, "_last_fof2_model", 0.0)
        if iono_fof2_str != "—" and fof2_model > 0:
            try:
                fof2_meas = float(iono_fof2_str)
                diff = abs(fof2_meas - fof2_model)
                if diff <= 0.8:
                    iono_color = "#66BB6A"    # groen — goede overeenkomst
                elif diff <= 2.0:
                    iono_color = "#FFA726"    # oranje — matige afwijking
                else:
                    iono_color = "#EF5350"    # rood — grote afwijking
                display_val = f"{fof2_meas:.1f}/{fof2_model:.1f}"
            except (ValueError, TypeError):
                iono_color  = TEXT_DIM
                display_val = f"—/{fof2_model:.1f}"
        elif fof2_model > 0:
            iono_color  = TEXT_DIM
            display_val = f"—/{fof2_model:.1f}"
        else:
            iono_color  = TEXT_DIM
            display_val = "—"
        if "iono_fof2" in self._solar_vars:
            self._solar_vars["iono_fof2"].set(display_val)
        if hasattr(self, "_solar_val_lbls") and "iono_fof2" in self._solar_val_lbls:
            self._solar_val_lbls["iono_fof2"].config(fg=iono_color)
        # Update het label-tekst met stationsnaam (bijv. "foF2 DB/md MHz")
        # via een apart StringVar voor het label zelf is niet beschikbaar; gebruik tooltip
        if hasattr(self, "_iono_station_var") and iono_station != "—":
            # Verkorte naam voor smal label (max 15 tekens incl. dubbele punt)
            short = iono_station[:13]
            self._iono_station_var.set(f"foF2 {short}:")


        # ── X-flare detectie ──────────────────────────────────────────────────
        self._check_xflare(data.get("xray", ""))

        # ── PCA detectie ──────────────────────────────────────────────────────
        self._check_pca(data.get("proton_flux", "—"))

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
                msg = self._tr("xflare_warning").format(xray=xray, dur=dur_min)
                self._xflare_var.set(msg)
                self._xflare_lbl.config(fg="#FF7043")
                if xray != self._last_xflare:
                    self._tray_notify(
                        f"☢ {xray}-flare",
                        self._tr("xflare_notify_body").format(dur=dur_min))
                    self._last_xflare = xray
                return
        self._xflare_var.set("")
        self._last_xflare = ""

    def _check_pca(self, proton_flux_str: str):
        """Detecteer proton event en toon PCA-waarschuwing (paars)."""
        if not hasattr(self, "_pca_var"):
            return
        try:
            pf = float(proton_flux_str.replace("—", "0"))
        except (ValueError, TypeError):
            pf = 0.0

        # NOAA S-schaal voor solare straling (proton events)
        if pf >= 1000:
            s_level, s_color = 5, "#EA80FC"
            dur = self._tr("pca_dur_s5")
        elif pf >= 100:
            s_level, s_color = 3, "#CE93D8"
            dur = self._tr("pca_dur_s3")
        elif pf >= 10:
            s_level, s_color = 1, "#BA68C8"
            dur = self._tr("pca_dur_s1")
        else:
            s_level = 0
            s_color = TEXT_H1
            dur = ""

        if s_level >= 1:
            msg = self._tr("pca_warning").format(s=s_level, pf=pf, dur=dur)
            self._pca_var.set(msg)
            self._pca_lbl.config(fg=s_color)
            if s_level > self._last_pca_level:
                self._tray_notify(
                    f"☢ Proton event S{s_level}",
                    self._tr("pca_notify_body").format(pf=pf, dur=dur))
            self._last_pca_level = s_level
        else:
            self._pca_var.set("")
            self._last_pca_level = 0

    # ── Venster centreren ─────────────────────────────────────────────────────
    def _center_window(self, w_hint: int, h_hint: int = MIN_WINDOW_H):
        # update() zodat canvas-widgets correct gemeten worden (resize-events vuren)
        self.root.update()
        scr_w = self.root.winfo_screenwidth()
        scr_h = self.root.winfo_screenheight()
        usable_w = scr_w - 60
        # Breedte: gebruik hint, begrensd aan scherm
        w = min(w_hint, usable_w)
        # Hoogte: minstens h_hint (= MIN_WINDOW_H), geen scherm-cap zodat alles past
        h = max(h_hint, self.root.winfo_reqheight())
        x = max(0, (scr_w - w) // 2)
        y = max(0, (scr_h - h) // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        # Stel minsize in zodat verkleinen niet onder bruikbare grens gaat
        self.root.minsize(min(900, usable_w), min(700, scr_h))


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
