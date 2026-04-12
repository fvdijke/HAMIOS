"""
HAMIOS v1.0
by Frank van Dijke

HAM radio propagation en DX tool met donkere GUI.
Features: solar/ionosfeer data (SFI, SSN, A/K-index),
          HF band betrouwbaarheid (MUF/LUF model, mode/vermogen/antenne),
          instellingen in INI-bestand.

Dependencies:
  pip install pillow

─────────────────────────────────────────────────────────────────────
TODO
─────────────────────────────────────────────────────────────────────
-> Layout
iaru moet itu regio's worden. 
Regio 1 (Europa, Afrika, Midden-Oosten, GOS, Mongolië), Regio 2 (Amerika) en Regio 3 (Azië-Pacific, minus gebieden in R1/R2). 
Maak een gedetailleerde poly lijn om deze grens aan te geven. 
Maak het ook selecteerbaar.

-> Refresh en data


─────────────────────────────────────────────────────────────────────
Change Log (1.0)
─────────────────────────────────────────────────────────────────────
· 2026-04-12 10:19 CEST — ITU regio-overlay: nauwkeurige grenzen per ITU RR Art.5;
               Lijn-A (R1/R3) met 20 detail-punten door Midden-Oosten (Turkije,
               Syrië/Irak, Koeweit, Golf van Oman, Arabische Zee, Somalische
               kust); Lijn-B (R1/R2) grote-cirkel bogen; Lijn-C Pacific met stap
               60°N/170°W→60°N/120°W. Labels "Regio 1/2/3" i.p.v. "R1/R2/R3".
· 2026-04-12 10:10 CEST — ITU regio-overlay: checkbox hernoemd naar "ITU";
               correcte R1/R2/R3 grenzen per ITU RR Art.5 (N-pool→10°W→72°N→
               50°W/40°N→20°W/Z-pool en N-pool→40°E→60°E/23.5°N→Z-pool);
               gevulde polygonen + gedetailleerde grenslijnen + R2/R3 Pacific-grens.
· 2026-04-10 21:46 CEST — DX Spots boven Advies geplaatst (linker sub-kolom).
· 2026-04-10 21:45 CEST — Wereldkaart vergroot over 2 kolommen; bandopenings-schema
               verplaatst tussen kaart en advies (linker sub-kolom).
· 2026-04-10 21:39 CEST — Advies verplaatst naar linker kolom onder de wereldkaart.
· 2026-04-10 21:36 CEST — Fix DX Spots: s-dict itereerde over keys i.p.v. values;
               veldindices gecorrigeerd (row[1]=freq, row[2]=spotter, row[4]=tijd);
               tijdparsing "HHMMz DD Mon" → "HH:MM"; html.unescape voor comments;
               _callsign_continent() toegevoegd voor sp_cont.
· 2026-04-10 21:32 CEST — Nieuwe schermindeling: Links Wereldkaart (vast 540px),
               midden Band Verloop + Schema + HF Betrouwbaarheid, rechts Solar,
               onderaan DX Spots + Advies.
· 2026-04-10 21:22 CEST — Continent-polygonen (_CONTINENTS) volledig verwijderd.
               Fallback bij ontbrekende NASA-kaart toont nu alleen oceaan + melding.
· 2026-04-10 15:16 CEST — Wereldkaart behoudt 2:1 verhouding bij venster-resize.
               3-koloms layout: Propagatie | Grafieken+Schema+DX | Solar.
· 2026-04-10 14:54 CEST — Live DX Spots panel: dxwatch.com JSON-feed, HF-filter,
               eigen-continent toggle (lat/lon → continent), Canvas-tabel
               (UTC/Band/DX/MHz/Spotter/Comment), refresh elke 2 min + countdown.
· 2026-04-10 14:46 CEST — Graylijn (amber terminator-band) als toggleable overlay.
               IARU regio-overlay R1/R2/R3 (gekleurde banden + grenslijn).
               Groot-cirkel pad: klik op kaart → gele lijn + afstand/richting;
               rechter muisklik wist het pad.
· 2026-04-10 14:40 CEST — QTH lat/lon invoervelden in kaart-header (Enter/FocusOut
               past kaart + propagatie direct aan). Bandschema tijdsas toont
               lokale tijd (CET/CEST); zon-westwaarts bug gecorrigeerd.
· 2026-04-12 10:59 CEST — ITU overlay: regio-kleuren aangepast aan referentie
               (R1=geel, R2=roze, R3=groen) en vulling-alpha verhoogd van 28
               naar 55 (22% dekking) zodat regio's duidelijk zichtbaar zijn.
· 2026-04-12 10:28 CEST — ITU Lijn-A gecorrigeerd: grens loopt nu via Irak/Iran grens
               (46-48E) → Perzische Golf → Golf van Oman (60E) → Arabische Zee
               → 11N/55E → 59E → Z-pool. Arabisch Schiereiland (Saudi, Oman,
               VAE, Jemen, Koeweit, Irak) correct in R1; Iran/Pakistan in R3.
               Eerdere fout: lijn liep door de Rode Zee waardoor Saudi-Arabië
               foutief in R3 viel.
· 2026-04-12 10:28 CEST — (vervangen) ITU grenzen volledig herschreven op basis van officieel
               ITU Radio Regulations Appendix 2: Lijn A loopt N-pool/55E →
               Oeral → Kaukasus (Krasnodar) → Turkije/Syrië → langs 35E naar 30N
               → boog Rode Zee/Golf van Aden → 11N/55E → langs 11N naar 59E →
               Z-pool langs 59E. Arabie (Saudi, Oman, VAE, Jemen) correct in R1;
               Iran, Pakistan, India correct in R3. Opstartvenster gebruikt
               root.update() voor nauwkeurige venstermeting.
· 2026-04-10 14:36 CEST — 60m-band zonder *, K-index als enkel getal met kleur
               (0–2 wit, 3–4 oranje, 5+ rood), K-melding-spinbox direct onder
               K-index geplaatst, bijgewerkt-tijd toont QTH-lokale tijd.
· 2026-04-10 09:20 CEST — Bandopenings-schema (heatmap 0–24 uur UTC per HF-band).
               X-flare detectie: M1+/X → SWF-waarschuwing in solar panel + tray.
               Auroraal absorptie-ovaal op kaart bij K≥4 (rood/oranje band).
               Solar-data geschiedenis: SFI/SSN/K/A opgeslagen in CSV; toggle
               "Solar" vs "Banden" in historiekgrafiek.
· 2026-04-10 09:11 CEST — Changelog herschreven: chronologisch opgeschoond,
               duplicaten verwijderd, laatste aanpassing bovenaan.
· 2026-04-10 09:10 CEST — Systeem-tray: venster sluiten minimaliseert naar tray.
               Tray-menu "HAMIOS tonen" / "Afsluiten". Notificaties bij band-opening
               (≥20%) en K-index drempel-overschrijding (drempel 1–9 instelbaar).
· 2026-04-10 09:04 CEST — Maidenhead-locatorraster als optionele kaartlaag (checkbox
               "Locator"): grote velden (20°×10°) met 2-letter QRA-labels (AA–RR).
· 2026-04-10 09:01 CEST — Alle UI-instellingen opgeslagen in HAMIOS.ini: grafiek-
               bereik, geselecteerde banden, tooltips aan/uit, locatorraster.
· 2026-04-10 08:53 CEST — Advies-panel onderaan: actuele tips op basis van beste
               banden, K-index, SFI/SSN en dag/nacht. Ververst bij elke solar-refresh.
· 2026-04-10 07:41 CEST — Exe-icon (antenne + radiogolven, 256×256, donker thema).
               Zon/maan aan/uit via checkboxes in kaart-header, opgeslagen in INI.
               QTH-markering vereenvoudigd tot kruisje (helder blauw).
· 2026-04-10 07:41 CEST — HF-propagatie afgestemd op QTH: breedtegraad-correctie
               op foF2, aurorale absorptie boven 45°. Dag/nacht automatisch bepaald
               op basis van zonpositie t.o.v. QTH bij elke solar-refresh.
· 2026-04-10 07:37 CEST — Mode-kolom: FT8 altijd rechts (bijv. "SSB / FT8").
               N/F licentiekolom naast bandnaam (NL: N = Novice, F = Full/HAREC).
· 2026-04-09 13:36 CEST — FT8-frequentiekolom toegevoegd aan propagatiepanel
               (IARU-standaardfrequenties, kolomhoofd, ook in tooltip).
· 2026-04-09 13:30 CEST — Historiekgrafiek (alle HF-banden, %) met tijdbereik-
               selectie (Uren/Dagen/Weken/Maanden) en klikbare bandlegenda.
               Data opgeslagen in CSV (90 dagen bewaard).
· 2026-04-09 13:00 CEST — Gesloten banden grijs weergegeven (zelfde stijl als
               LOS/Tropo). Mouse-over tooltips per band en per solar-gegeven.
· 2026-04-09 12:15 CEST — Wereldkaart (blauw thema, equirectangular, 400 px hoog):
               dag/nacht terminator met zachte overgang, zon- en maanpositie, QTH-
               markering. NASA-kaart (2048×1024) automatisch gedownload; polygoon-
               kaart als fallback. Breedtegraad/lengtegraad labels op raster.
· 2026-04-09 12:00 CEST — Solar panel toont alle 15 banden (dag én nacht) via
               MUF/LUF-model; kleurcodes Goed/Fair/Arm/Dicht/LOS.
· 2026-04-09 11:30 CEST — Alle officiële HAM-banden toegevoegd (160m–23cm, incl.
               60m* en VHF/UHF) met startfrequenties en aanbevolen modi.
· 2026-04-09 10:30 CEST — QTH-positie (lat/lon), mode, vermogen en antenne opgeslagen
               in HAMIOS.ini en hersteld bij start.
· 2026-04-09 10:00 CEST — Instelbaar ververs-interval (Uit / 30s / 1 min / 5 min /
               10 min / 30 min / 1 uur); countdown in header. Lokale tijd (CET/CEST)
               en UTC in header; vinkje Zomertijd opgeslagen in HAMIOS.ini.
· 2026-04-08 00:00 CEST — Initiële versie: solar/ionosfeer data panel (SFI, SSN,
               A/K-index, X-ray), HF band betrouwbaarheidspanel (MUF/LUF model,
               mode/vermogen/antenne correctie, gekleurde balkjes per band).


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
# N-pool/10W -> 72N/10W -> 40N/50W -> 30N/20W -> Z-pool/20W
_ITU_B = [
    (90, -10), (72, -10), (40, -50), (30, -20), (0, -20), (-90, -20),
]

# Lijn A: oostgrens R1 / westgrens R3  (ITU Radio Regulations Appendix 2)
# N-pool/55E → Oeral → Kaukasus (Krasnodar/Zwarte Zee) →
# Oost-Turkije → Irak/Iran grens (46-48E) →
# Perzische Golf kust → Golf van Oman (60E) →
# Arabische Zee → 11N/55E → langs 11N naar 59E → Z-pool/59E
#
# R1 bevat: Europa, Afrika, Arabisch Schiereiland (Saudi, Oman, VAE,
#           Jemen, Koeweit), Irak, Syrië, Turkije
# R3 bevat: Iran, Pakistan, India, Azië-Pacific
_ITU_A = [
    (90, 55), (60, 55),        # N-pool → 60N langs 55E
    (55, 55), (50, 52),        # Rusland/Oeral
    (47, 43), (45, 39),        # Kaukasus/Krasnodar
    (41, 40),                   # Turkse Zwarte Zeekust
    (39, 40), (38, 42),        # Oost-Turkije oostwaarts
    (37, 44),                   # Turkije/Irak/Iran driehoek
    (35, 46), (33, 47),        # Irak/Iran grens
    (31, 47), (30, 48),        # Zuid-Irak/Koeweit
    (29, 49), (27, 53),        # Perzische Golf ingang/Qatar
    (25, 57), (23, 59),        # VAE → Noord-Oman
    (21, 60),                   # Oost-Oman (Kaap Ras al-Hadd)
    (18, 60), (15, 58),        # Arabische Zee naar Golf van Aden
    (13, 57), (11, 55),        # 11N/55E (officieel ITU-punt)
    (11, 59),                   # Langs breedtegraad 11N → 59E
    (-90, 59),                  # Z-pool langs 59E
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


# ── Font helper ────────────────────────────────────────────────────────────────
def _font(size=10, weight="normal"):
    return tkfont.Font(family="Segoe UI", size=size, weight=weight)

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
                    "show_iaru": str(show_iaru)}
    cfg["Graph"]  = {"hist_range": hist_range,
                     "selected_bands": ",".join(sorted(hist_sel)) if hist_sel else ""}
    cfg["Alerts"] = {"k_alert": str(k_alert)}
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)

# ── Solar data ophalen ─────────────────────────────────────────────────────────
SOLAR_URL = "https://www.hamqsl.com/solarxml.php"

def _fetch_solar() -> dict:
    try:
        with urllib.request.urlopen(SOLAR_URL, timeout=8) as r:
            xml = r.read()
        root = ET.fromstring(xml)
        sd = root.find(".//solardata")
        if sd is None:
            return {}
        return {
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
    except Exception as e:
        return {"error": str(e)}


def _band_cond(sd, band: str, time_of_day: str) -> str:
    for item in sd.findall("calculatedconditions/band"):
        if item.get("name") == band and item.get("time") == time_of_day:
            return (item.text or "—").strip()
    return "—"


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
    """
    def __init__(self, widget: tk.Widget):
        self._widget = widget
        self._win: tk.Toplevel | None = None

    def show(self, x: int, y: int, content):
        if self._win:
            self._win.destroy()
        self._win = tw = tk.Toplevel(self._widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x + 14}+{y + 10}")
        tw.configure(bg=BORDER)

        outer = tk.Frame(tw, bg=BG_SURFACE, padx=10, pady=8)
        outer.pack()

        def _f(sz=9, bold=False):
            return tkfont.Font(family="Segoe UI", size=sz,
                               weight="bold" if bold else "normal")

        if isinstance(content, list):
            for ri, item in enumerate(content):
                if item is None:
                    tk.Frame(outer, bg=BORDER, height=1).grid(
                        row=ri, column=0, columnspan=2,
                        sticky='ew', pady=(3, 3))
                elif item[1] is None:
                    tk.Label(outer, text=item[0], font=_f(9, bold=True),
                             bg=BG_SURFACE, fg=ACCENT).grid(
                        row=ri, column=0, columnspan=2, sticky='w')
                else:
                    tk.Label(outer, text=item[0], font=_f(9),
                             bg=BG_SURFACE, fg=TEXT_DIM, anchor='w').grid(
                        row=ri, column=0, sticky='w', padx=(0, 14))
                    tk.Label(outer, text=item[1], font=_f(9, bold=True),
                             bg=BG_SURFACE, fg=TEXT_H1, anchor='w').grid(
                        row=ri, column=1, sticky='w')
        else:
            lines = content.split('\n')
            for ri, line in enumerate(lines):
                if line.startswith('─'):
                    tk.Frame(outer, bg=BORDER, height=1).grid(
                        row=ri, column=0, sticky='ew', pady=(2, 2))
                    outer.columnconfigure(0, weight=1)
                else:
                    is_title = ri == 0
                    tk.Label(outer, text=line, justify='left',
                             font=_f(9, bold=is_title),
                             bg=BG_SURFACE,
                             fg=ACCENT if is_title else TEXT_BODY,
                             anchor='w').grid(row=ri, column=0, sticky='w')

    def hide(self):
        if self._win:
            self._win.destroy()
            self._win = None


# ── Hoofd-GUI ──────────────────────────────────────────────────────────────────
class HAMIOSApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("HAMIOS v1.0")
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
        self._gc_dest: tuple | None = None   # (lat, lon) groot-cirkel bestemming
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
        self._center_window(1400, 900)
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
        tk.Label(hdr, text="📡  HAMIOS v1.0",
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
            ("k_index",  "K-index"),
            ("xray",     "X-ray"),
            ("muf",      "MUF (MHz)"),
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

            # K-index melding direct onder de K-index rij
            if key == "k_index":
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

        # ── Gecombineerde linker+midden zone (kaart overspant beide kolommen) ──
        combined = tk.Frame(top_row, bg=BG_ROOT)
        combined.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Kaart bovenaan, volledige breedte van combined
        self._build_map_panel(combined)

        # Sub-rij onder de kaart: Schema+Advies links  |  Band Verloop+Prop rechts
        sub_row = tk.Frame(combined, bg=BG_ROOT)
        sub_row.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        left_sub = tk.Frame(sub_row, bg=BG_ROOT, width=540)
        left_sub.pack(side=tk.LEFT, fill=tk.Y)
        left_sub.pack_propagate(False)
        self._build_schedule_panel(left_sub)
        self._build_dx_panel(left_sub)
        self._build_advice_panel(left_sub)

        right_sub = tk.Frame(sub_row, bg=BG_ROOT)
        right_sub.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        self._build_hist_panel(right_sub)
        self._build_prop_panel(right_sub)

    # ── Wereldkaart panel ─────────────────────────────────────────────────────
    def _build_map_panel(self, parent):
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.BOTH, expand=True, pady=(0, 0))
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

        self._map_canvas = tk.Canvas(outer, height=400, bg="#1B3A5C",
                                     bd=0, highlightthickness=0)
        self._map_canvas.pack(fill=tk.X)
        self._map_photo = None
        self._map_canvas.bind("<Configure>",  self._on_map_resize)
        self._map_canvas.bind("<Button-1>",   self._on_map_click)
        self._map_canvas.bind("<Button-3>",   self._on_map_clear)

        # Info-label voor groot-cirkel (rechtsonder in canvas)
        self._gc_info_var = tk.StringVar(value="")
        tk.Label(outer, textvariable=self._gc_info_var,
                 font=_font(9), bg=BG_PANEL, fg=ACCENT,
                 anchor='w').pack(fill=tk.X, padx=10, pady=(0, 4))

    def _on_map_resize(self, event):
        """Handhaaf 2:1 verhouding (equirectangulair) bij breedte-wijziging."""
        new_h = max(100, event.width // 2)
        if self._map_canvas.winfo_height() != new_h:
            self._map_canvas.config(height=new_h)
        self._draw_map()

    def _redraw_map(self):
        """Cache ongeldig maken en kaart opnieuw tekenen (na download)."""
        self._map_base_size = None
        self._draw_map()

    def _on_map_click(self, event):
        """Linker muisklik: stel groot-cirkel bestemming in."""
        W = self._map_canvas.winfo_width()  or 960
        H = self._map_canvas.winfo_height() or 400
        lon = event.x / W * 360 - 180
        lat = 90 - event.y / H * 180
        self._gc_dest = (lat, lon)
        dist = _haversine_km(self._qth_lat, self._qth_lon, lat, lon)
        hdg  = _bearing_deg(self._qth_lat, self._qth_lon, lat, lon)
        self._gc_info_var.set(
            f"→  {lat:+.1f}°, {lon:+.1f}°  |  Afstand: {dist:,.0f} km  "
            f"|  Richting: {hdg:.0f}°  (klik rechts om te wissen)")
        self._draw_map()

    def _on_map_clear(self, *_):
        """Rechter muisklik: verwijder groot-cirkel."""
        self._gc_dest = None
        self._gc_info_var.set("")
        self._draw_map()

    def _draw_map(self):
        c = self._map_canvas
        W = c.winfo_width()  or 960
        H = c.winfo_height() or 400

        if not _PIL_OK:
            c.delete("all")
            c.create_rectangle(0, 0, W, H, fill="#1B3A5C", outline="")
            c.create_text(W // 2, H // 2,
                          text="pip install pillow  voor kaartweergave",
                          fill=TEXT_DIM, font=("Segoe UI", 9))
            return

        # ── Basiskaart (gecached bij grootte-wijziging) ───────────────────────
        cache_key = (W, H)
        if getattr(self, "_map_base_size", None) != cache_key:
            if os.path.exists(MAP_FILE):
                # NASA equirectangulaire kaart (2048×1024 = exact 2:1)
                src = Image.open(MAP_FILE).convert("RGB").resize(
                    (W, H), Image.LANCZOS)
                # NASA-topo: oceaan = blauw dominant, land = groen/bruin/wit
                src.putdata([
                    MAP_OCEAN if (b > r + 15 and b > g) else MAP_LAND
                    for r, g, b in src.getdata()
                ])
            else:
                # Fallback: oceaan-achtergrond tijdens download
                src = Image.new("RGB", (W, H), MAP_OCEAN)
                ImageDraw.Draw(src).text(
                    (6, 4), "⬇ NASA-kaart wordt gedownload…", fill=MAP_GRID)

            # Graticule + graden-labels
            d   = ImageDraw.Draw(src)
            LBL = (180, 200, 220)   # contrasterende lichtblauwe kleur
            for lat in range(-60, 90, 30):
                gy = int((90 - lat) / 180 * H)
                d.line([(0, gy), (W, gy)], fill=MAP_GRID, width=1)
                d.text((3, gy + 2), f"{lat:+d}°", fill=LBL)
            for lon in range(-150, 180, 30):
                gx = int((lon + 180) / 360 * W)
                d.line([(gx, 0), (gx, H)], fill=MAP_GRID, width=1)
                d.text((gx + 2, 2), f"{lon:+d}°", fill=LBL)

            self._map_base_img  = src
            self._map_base_size = cache_key

        img  = self._map_base_img.copy()

        # ── Nacht overlay ────────────────────────────────────────────────────
        sun_lat, sun_lon = _subsolar_point()
        night = _night_mask(sun_lat, sun_lon, W, H)
        img   = img.convert("RGBA")
        img   = Image.alpha_composite(img, night)
        img   = img.convert("RGB")
        draw  = ImageDraw.Draw(img)

        # ── Zon ──────────────────────────────────────────────────────────────
        if self._show_sun_var.get():
            sx, sy = _ll_to_xy(sun_lat, sun_lon, W, H)
            draw.ellipse([(sx - 7, sy - 7), (sx + 7, sy + 7)],
                         fill=MAP_SUN, outline=(200, 160, 0), width=1)

        # ── Maan ─────────────────────────────────────────────────────────────
        if self._show_moon_var.get():
            moon_lat, moon_lon = _submoon_point()
            mx, my = _ll_to_xy(moon_lat, moon_lon, W, H)
            draw.ellipse([(mx - 5, my - 5), (mx + 5, my + 5)],
                         fill=MAP_MOON, outline=(150, 150, 150), width=1)

        # ── Graylijn ─────────────────────────────────────────────────────────
        if self._show_graylijn_var.get():
            gray = _graylijn_mask(sun_lat, sun_lon, W, H)
            img  = Image.alpha_composite(img.convert("RGBA"), gray).convert("RGB")
            draw = ImageDraw.Draw(img)

        # ── ITU regio-overlay (correcte R1/R2/R3 grenzen) ───────────────────
        if self._show_iaru_var.get():
            itu_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            id_     = ImageDraw.Draw(itu_img)
            AF, AL  = 55, 220   # alpha vulling / grenslijn  (55≈22% dekking)
            # Kleuren conform referentieplaatje: R1=geel, R2=roze, R3=groen
            C_R1 = (210, 190,  70, AF)
            C_R2 = (210,  80,  80, AF)
            C_R3 = ( 60, 170,  80, AF)

            def _px(pts):
                return [_ll_to_xy(la, lo, W, H) for la, lo in pts]

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

            # R1: Lijn-B → Z-pool → Lijn-A omgekeerd → N-pool
            id_.polygon(_px([
                (90,-10),(72,-10),(40,-50),(30,-20),(0,-20),(-90,-20),
                (-90,59),
                (11,59),(11,55),
                (13,57),(15,58),(18,60),
                (21,60),(23,59),(25,57),
                (27,53),(29,49),
                (30,48),(31,47),(33,47),(35,46),
                (37,44),(38,42),(39,40),
                (41,40),(45,39),(47,43),(50,52),(55,55),
                (60,55),(90,55)
            ]), fill=C_R1)

            # R3 oost (Azië-Pacific): Lijn-A → 180°E
            id_.polygon(_px([
                (90,55),(60,55),(55,55),(50,52),(47,43),
                (45,39),(41,40),
                (39,40),(38,42),(37,44),
                (35,46),(33,47),(31,47),(30,48),
                (29,49),(27,53),(25,57),
                (23,59),(21,60),(18,60),
                (15,58),(13,57),(11,55),
                (11,59),
                (-90,59),(-90,180),(90,180)
            ]), fill=C_R3)

            # ── Grenslijnen ───────────────────────────────────────────────
            for pts, clr, w in [
                (_ITU_B, (255, 200,  80, AL), 2),   # R1/R2
                (_ITU_A, ( 80, 220, 100, AL), 2),   # R1/R3
                (_ITU_C, (160, 220, 160, AL), 1),   # R2/R3 Pacific
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
                x_l, y_l = _ll_to_xy(la, lo, W, H)
                if 0 <= x_l < W and 0 <= y_l < H:
                    id_.text((x_l - 22, y_l - 5), txt, fill=(230,230,230,210))

            img  = Image.alpha_composite(img.convert("RGBA"), itu_img).convert("RGB")
            draw = ImageDraw.Draw(img)

        # ── Maidenhead locatorraster ─────────────────────────────────────────
        if self._show_locator_var.get():
            LOC_GRID = (100, 160, 220, 180)   # lichtblauw, semi-transparant
            LOC_LBL  = (160, 210, 255, 200)
            loc_img  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ld       = ImageDraw.Draw(loc_img)
            # Grote velden: 20° breed × 10° hoog
            for fi in range(19):          # 18 velden in lon-richting
                gx = int(fi * 20 / 360 * W)
                ld.line([(gx, 0), (gx, H)], fill=LOC_GRID, width=1)
            for fi in range(19):          # 18 velden in lat-richting
                gy = int(fi * 10 / 180 * H)
                ld.line([(0, gy), (W, gy)], fill=LOC_GRID, width=1)
            # Labels (2-letter locator) in het midden van elk groot veld
            for lon_i in range(18):
                for lat_i in range(18):
                    lon_c = -180 + lon_i * 20 + 10
                    lat_c =  -90 + lat_i * 10 +  5
                    lbl   = chr(ord('A') + lon_i) + chr(ord('A') + lat_i)
                    cx_l, cy_l = _ll_to_xy(lat_c, lon_c, W, H)
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
            aurora_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ad = ImageDraw.Draw(aurora_img)
            # Trek een horizontale band als proxy voor het ovaal (beide hemisferen)
            thickness = max(4, int(k_val * 1.5))
            alpha = min(200, int(80 + k_val * 15))
            for sign in (1, -1):
                lat_c = sign * aurora_lat
                _, y_c = _ll_to_xy(lat_c, 0, W, H)
                y_top = max(0, y_c - thickness)
                y_bot = min(H, y_c + thickness)
                # Rood/oranje ovaal
                ad.rectangle([(0, y_top), (W, y_bot)],
                              fill=(220, 80, 20, alpha))
            img = Image.alpha_composite(img.convert("RGBA"), aurora_img).convert("RGB")
            draw = ImageDraw.Draw(img)

        # ── Groot-cirkel pad ─────────────────────────────────────────────────
        if self._gc_dest:
            dlat, dlon = self._gc_dest
            pts = _great_circle_pts(self._qth_lat, self._qth_lon, dlat, dlon)
            gc_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            gd     = ImageDraw.Draw(gc_img)
            xy     = [_ll_to_xy(la, lo, W, H) for la, lo in pts]
            # Splits op anti-meridian (|Δx| > W/2) om wraparound te vermijden
            seg_start = 0
            for i in range(1, len(xy)):
                if abs(xy[i][0] - xy[i-1][0]) > W // 2:
                    if i - seg_start > 1:
                        gd.line(xy[seg_start:i], fill=(255, 220, 50, 220), width=2)
                    seg_start = i
            if len(xy) - seg_start > 1:
                gd.line(xy[seg_start:], fill=(255, 220, 50, 220), width=2)
            # Bestemmingsmarkering
            dx, dy = _ll_to_xy(dlat, dlon, W, H)
            gd.ellipse([(dx-5, dy-5), (dx+5, dy+5)], fill=(255, 220, 50, 220))
            img  = Image.alpha_composite(img.convert("RGBA"), gc_img).convert("RGB")
            draw = ImageDraw.Draw(img)

        # ── QTH marker (alleen kruisje) ───────────────────────────────────────
        qx, qy = _ll_to_xy(self._qth_lat, self._qth_lon, W, H)
        draw.line([(qx - 10, qy), (qx + 10, qy)], fill=MAP_QTH, width=2)
        draw.line([(qx, qy - 10), (qx, qy + 10)], fill=MAP_QTH, width=2)

        # ── Tonen ────────────────────────────────────────────────────────────
        self._map_photo = ImageTk.PhotoImage(img)
        c.delete("all")
        c.create_image(0, 0, anchor='nw', image=self._map_photo)

    # ── HF Propagatie panel ───────────────────────────────────────────────────
    def _build_prop_panel(self, parent):
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.X, pady=(6, 0))

        tk.Frame(outer, bg=ACCENT, height=2).pack(fill=tk.X)
        tk.Label(outer, text="📶  HF Band Betrouwbaarheid",
                 font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT,
                 pady=6).pack(anchor='w', padx=10)

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

        BAR_H    = 18
        BAR_PAD  = 4
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
        BAR_H   = 18
        BAR_PAD = 4
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

        self._hist_canvas = tk.Canvas(outer, height=140, bg=BG_PANEL,
                                      bd=0, highlightthickness=0)
        self._hist_canvas.pack(fill=tk.X, padx=10, pady=(0, 6))
        self._hist_canvas.bind("<Configure>", lambda *_: self._draw_hist_graph())

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

    # ── Bandopenings-schema (heatmap) ─────────────────────────────────────────
    def _build_schedule_panel(self, parent):
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.X, pady=(6, 0))
        tk.Frame(outer, bg=ACCENT, height=2).pack(fill=tk.X)

        hdr = tk.Frame(outer, bg=BG_PANEL)
        hdr.pack(fill=tk.X, padx=10, pady=(4, 2))
        tk.Label(hdr, text="🕐  Bandopenings-schema (lokale tijd, vandaag)",
                 font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT).pack(side=tk.LEFT)

        self._sched_canvas = tk.Canvas(outer, height=130, bg=BG_PANEL,
                                       bd=0, highlightthickness=0)
        self._sched_canvas.pack(fill=tk.X, padx=10, pady=(0, 6))
        self._sched_canvas.bind("<Configure>", lambda *_: self._draw_schedule())

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
                pct = pct_map.get(bname, 0)

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

        self._dx_canvas = tk.Canvas(outer, height=196, bg=BG_PANEL,
                                    bd=0, highlightthickness=0)
        self._dx_canvas.pack(fill=tk.X, padx=10, pady=(2, 6))
        self._dx_canvas.bind("<Configure>", lambda *_: self._draw_dx_panel())

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
        self._dx_status_var.set(
            f"{n} van {total} spots  (HF{filt})" if total else "Geen spots beschikbaar")

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
            return

        max_rows = (H - ROW_H - 4) // ROW_H
        for i, s in enumerate(spots[:max_rows]):
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
            max_ch = max(4, C_CMT // 6)
            c.create_text(x, y, text=s.get("comment", "")[:max_ch],
                          fill=TEXT_DIM, font=("Consolas", 8), anchor='nw')

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
        tk.Label(outer, text="💡  Advies",
                 font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT,
                 pady=4).pack(anchor='w', padx=10)
        self._advice_frame = tk.Frame(outer, bg=BG_PANEL)
        self._advice_frame.pack(fill=tk.X, padx=10, pady=(0, 8))

    def _update_advice(self):
        if not hasattr(self, "_advice_frame"):
            return
        for w in self._advice_frame.winfo_children():
            w.destroy()

        data    = self._solar_data
        try:
            sfi     = float(data.get("sfi",     "90").replace("—", "90"))
            ssn     = float(data.get("ssn",     "50").replace("—", "50"))
            k_index = float(data.get("k_index", "2" ).replace("—", "2"))
        except (ValueError, TypeError):
            sfi, ssn, k_index = 90.0, 50.0, 2.0

        is_day  = self._day_var.get()
        bp      = {n: p for n, _, p in self._last_band_pct if p >= 0}

        tips: list[tuple[str, str, str]] = []   # (icon, tekst, kleur)

        # ── Beste band(en) ────────────────────────────────────────────────
        hf_open = [(n, p) for n, p in bp.items() if p > 0]
        hf_open.sort(key=lambda x: -x[1])
        if hf_open:
            best = hf_open[:3]
            bstr = ",  ".join(f"{n} ({p}%)" for n, p in best)
            tips.append(("📡", f"Beste banden nu:  {bstr}", "#4CAF50"))
        else:
            tips.append(("📡", "Alle HF-banden zijn momenteel gesloten.", TEXT_DIM))

        # ── Geomagneetse activiteit ───────────────────────────────────────
        if k_index >= 5:
            tips.append(("⚠️", f"Geomagnetische storm  (K={int(k_index)}) — "
                                "HF-propagatie ernstig verstoord, poolroutes geblokkeerd.",
                         "#F44336"))
        elif k_index >= 3:
            tips.append(("⚡", f"Verhoogde geomagnetische activiteit  (K={int(k_index)}) — "
                                "lagere banden (40m/80m) stabielere keuze.", "#FFC107"))
        else:
            tips.append(("✅", f"Rustige geomagnetische condities  (K={int(k_index)}).",
                         "#4CAF50"))

        # ── SFI / SSN / Zonnecyclus ──────────────────────────────────────
        if sfi >= 150:
            tips.append(("☀️", f"Uitstekende zonnecyclus  (SFI={int(sfi)}, SSN={int(ssn)}) — "
                                "10m/12m/15m kunnen open zijn voor DX.", ACCENT))
        elif sfi >= 100:
            tips.append(("🌤", f"Goede zonnecyclus  (SFI={int(sfi)}, SSN={int(ssn)}) — "
                                "20m/17m/15m zijn beste DX-banden.", ACCENT))
        elif sfi < 80:
            tips.append(("🌧", f"Lage zonactiviteit  (SFI={int(sfi)}, SSN={int(ssn)}) — "
                                "40m en 80m bieden meeste kans; hoge banden grotendeels dicht.",
                         TEXT_DIM))

        # ── Dag/nacht advies ─────────────────────────────────────────────
        if is_day:
            if hf_open and hf_open[0][1] >= 60:
                tips.append(("🌞", "Dagcondities: overweeg SSB of FT8 op de beste band.", TEXT_BODY))
        else:
            night_good = [(n, p) for n, p in bp.items() if p >= 40
                          and any(b == n for b, _, _ in _BANDS if b in ("160m","80m","40m"))]
            if night_good:
                tips.append(("🌙", "Nachtcondities: 40m en 80m zijn vaak beter 's nachts "
                                   "— probeer FT8 voor lange afstanden.", TEXT_BODY))
            else:
                tips.append(("🌙", "Nachtcondities: lagere banden (160m/80m/40m) "
                                   "voor regionale en continentale verbindingen.", TEXT_BODY))

        # ── Weergave ─────────────────────────────────────────────────────
        cols = 2
        for i, (icon, tekst, kleur) in enumerate(tips):
            cell = tk.Frame(self._advice_frame, bg=BG_SURFACE,
                            padx=8, pady=5)
            cell.grid(row=i // cols, column=i % cols,
                      sticky='nsew', padx=(0 if i % cols else 0, 6 if i % cols == 0 else 0),
                      pady=(0, 4))
            self._advice_frame.columnconfigure(i % cols, weight=1)
            tk.Label(cell, text=f"{icon}  {tekst}", font=_font(9),
                     bg=BG_SURFACE, fg=kleur,
                     anchor='w', wraplength=420, justify='left').pack(fill=tk.X)

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
        self._tray_icon = pystray.Icon("HAMIOS", tray_img, "HAMIOS v1.0", menu)
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
        # update() ipv update_idletasks() zodat canvas-widgets ook correct gemeten worden
        self.root.update()
        scr_w = self.root.winfo_screenwidth()
        scr_h = self.root.winfo_screenheight()
        # Gebruik de door tkinter berekende benodigde grootte als die groter is
        req_w = self.root.winfo_reqwidth()
        req_h = self.root.winfo_reqheight()
        w = max(min_w, req_w if req_w > 100 else min_w)
        h = max(min_h, req_h if req_h > 100 else min_h)
        # Niet groter dan het scherm (laat 60px taskbalk-marge vrij)
        w = min(w, scr_w - 60)
        h = min(h, scr_h - 60)
        x = max(0, (scr_w - w) // 2)
        y = max(0, (scr_h - h) // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")


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
