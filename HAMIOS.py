"""
HAMIOS v3.0
by Frank van Dijke

HAM radio propagatie- en DX-monitor met donkere GUI.
Features: solar/ionosfeer data (SFI, SSN, A/K-index, Bz, solarwind),
          HF band betrouwbaarheid (MUF/LUF model, mode/vermogen/antenne),
          WSPR/PSKReporter spots op kaart, DX-spot markers,
          CAT-interface (Yaesu/Kenwood/Elecraft/Icom CI-V),
          6 talen (NL/EN/DE/FR/IT/ES), systeemtray, ticker,
          dynamische thema's (Midnight/DeepOcean/HighContrast),
          wereldwijde ionosondes, offline-indicator, DX-spot heatmap.

Dependencies:
  pip install pillow
  pip install pyserial   # optioneel, voor CAT-interface
  pip install pystray    # optioneel, voor systeemtray

─────────────────────────────────────────────────────────────────────
Todo
─────────────────────────────────────────────────────────────────────
- [x] UX: Interactieve kaart (klik bestemming → bereken prop + teken hop-lijn)
- [x] UX: Thema-configuratie (ondersteuning voor meerdere donkere thema's/high-contrast)
- [x] Data: Uitbreiden ionosonde-netwerk naar wereldwijde stations
- [x] Data: Voorspellend model toevoegen op basis van 48u trendanalyse
- [x] Data: WSPR filters implementeren (SNR drempel, band-selectie)
- [x] Stab: Implementeren van "Offline" indicator bij netwerkuitval
- [x] Stab: Validatie toevoegen aan HAMIOS.ini loading process
- [ ] CAT: Retry-mechanisme voor seriële poorten implementeren en _CAT_DISABLED op False zetten
- [x] Vis: Heatmap implementeren voor historische DX-spot activiteit
- [x] Vis: We gaan verder met versie 3.0. Deze versie is volledig geent op hetr verbeteren van de interface.
           Maak een nieuw ontwerp voor de interface waarbij de wereldkaart min of meer centraal staat.
           Het formaat van deze kaart is altijd hetzelfde. Wel moet je nog steeds kunnen zoomen en pannen.
           Zet de selectievakjes op logische plekken. Zet data die gerelateerd is aan ellkaar ook bij elkaar.
           Zorg dat grafieken goed leesbaar zijn. Maak de bandgrafieken mooier.
           Kijk ook of je de band balken aantrekkelijker kan maken.
- [x] Vis: Melding selecties kunnen onder de overige selectie vakjes in het map paneel.
- [x] Vis: Voer een vierde kolom toe voor de DX Spot en zet alle DX spot functies weer aan. Laat de breedte van alle overige kolommen hetzelfde.
           Het totaal scherm mag dus wel breder worden.
- [x] Vis: Voeg een tooltip toe aan de Bz grafiek en maak de grafiek ook aantrekkelijker en duidelijker. Formaal moet hetzelfde blijven.
- [x] Vis: Maak de kolommen in de eerste row net zo breed als de kolommen in de tweede row. De map moet dam wel geresized worden zodat deze neg zo breed is als de tweede kolom.
- [x] Vis: Schakelen tussen thema's werkt niet goed. Thema's blijven hangen.
- [x] Vis: Verplaats de solar/ionosfeer info naar het DX paneel en zet een scheidingslijn (goud) tussen de verschillende blokken.
- [x] Vis: Verwijder de eerste kolom van de bovenste rij (links).
- [x] Vis: Zet HF band betrouwbaarheid als eerste kolom in bovenste rij en maak deze net zo breed als Band opening schema.
- [x] Vis: Maak wereldkaart net zo breed als kolom 2 + 3 van de tweede rij.
- [x] Vis: Zet selectievakjes onder HF betrouwbaarheid met scheidingslijn


─────────────────────────────────────────────────────────────────────
Change Log (3.0)
─────────────────────────────────────────────────────────────────────
· 2026-04-25 16:15 CEST — Cross-platform: platform-detectie (_IS_MAC/_IS_WIN);
               _FONT_SANS (Helvetica Neue/Segoe UI/DejaVu Sans) en _FONT_MONO
               (Menlo/Consolas/DejaVu Sans Mono) vervangen alle hardcoded fontnamen.
               Tooltip-vensters krijgen -topmost True op macOS (Sequoia-fix).
               DX-canvas scroll: Button-4/5 bindings toegevoegd voor Linux;
               muiswiel-richting via event.num/delta werkt nu op alle platforms.

· 2026-04-25 15:30 CEST — Versie 3.0 (vervolg): DX Spots als vierde kolom in top_row
               (breedte 300 px, fill=Y, alle DX-functies actief).
               Bottom_row kolommen uitgelijnd: sched_col=230 px (=solar), bz_col=310 px
               (=HF), hist_col expandeert vrij → map en hist visueel gelijkbreedte.
               Meldingen (K-index/band-alert) verplaatst van solar-paneel naar rij 3 van
               de kaartoverlays (map panel), onder WSPR/Spots/CS/Locator.
               Bz grafiek verbeterd: hoogte 90→120 px; area-fill (blauw/rood tint);
               horizontale gridlijnen bij ±20/±40; tijdgridlijnen 6/12/18h; Y-as lijn;
               cursor-tooltip bij muisbeweging (Bz-waarde + tijdstip); lijndikte 2 px.
               Thema-fix: _apply_theme() gebruikt nu kleur-remap van vorig→nieuw thema
               (THEMES lookup), zodat herhaalschakelingen correct werken. UI gebouwd
               met Midnight-constanten; na _build_ui() altijd remap naar opgeslagen thema.

· 2026-04-29 14:39 CEST — Versie 3.0 (interface todo-items afgerond):
               Solar/ionosfeer verplaatst naar DX-paneel (_build_solar_section);
               gouden scheidingslijnen (ACCENT, 2 px) tussen blokken in DX-paneel.
               Solar kolom verwijderd uit top_row. top_row omgeschakeld naar
               tkinter grid (4 gelijke kolommen, uniform="lc"): HF Betrouwbaarheid
               in col 0 (= breedte Schema), Kaart in col 1-2 (= Bandverloop+Kp),
               col 3 leeg boven Bz+Xray. Selectievakjes (Weergave/Data/Meldingen)
               verplaatst van kaartpaneel naar onder HF Betrouwbaarheid met gouden
               scheidingslijn. Alle 5 open Vis-todo items afgevinkt.

· 2026-04-28 14:13 CEST — Versie 3.0 (data-uitbreiding hoge prioriteit):
               Nieuwe data: solarwind dichtheid (ρ n/cm³), planetaire Kp-index,
               Kp 48u staafdiagram, X-ray 24u log-grafiek, 3-daagse storm-kans
               voorspelling (NOAA SWPC), WSPR spot-teller per band in bandbalken.
               Bottom row uitgebreid naar 4 kolommen: Schema | Bandverloop |
               Kp 48u | Bz+X-ray gestapeld. Solar paneel: 2 extra parameter-rijen
               (sw_density, kp_planet) + kleurcodering. Solar panel ook smaller.

· 2026-04-28 13:15 CEST — Versie 3.0: Interface-redesign: wereldkaart centraal in
               het midden (vaste hoogte 380 px, zoom/pan intact); solar-paneel
               verplaatst naar linkerkolom; HF-bandbetrouwbaarheid naar rechterkolom;
               Onderste rij: 3 gelijke kolommen (Schema | Bandverloop | Bz grafiek),
               allen expand=True zodat hoogte en breedte automatisch gelijk zijn.
               Bz-grafiek als zelfstandig paneel (_build_bz_panel), hoogte dynamisch.
               Map-paneel outer fill=BOTH→gelijke hoogte top-rij; center_col/right_col
               achtergrond BG_PANEL. Graticule-labels aangepast aan crop_t zodat
               graden altijd zichtbaar zijn. DX Spots en PCA/flux-meldingen verwijderd.
               Bandbalken vernieuwd: 22 px, gradient, band-eigen kleur. 2.5 → 3.0.

Change Log (2.5)
─────────────────────────────────────────────────────────────────────
· 2026-04-25 11:05 CEST — Versie 2.5: Ionosonde-netwerk uitgebreid van 6 Europese naar
               21 wereldwijde stations (Europa, Noord- en Zuid-Amerika, Afrika,
               Azië, Australazië); _nearest_iono_station kiest automatisch het
               dichtstbijzijnde station op basis van QTH.
               Offline-indicator: ⚠ OFFLINE-label in header verschijnt bij
               netwerkfout in solar-fetch; verdwijnt zodra verbinding hersteld is.
               DX-spot heatmap: toggle-knop "Heatmap" in DX Spots panel wisselt
               tussen spotenlijst en band × UTC-uur heatmap (24h historiekbuffer).
               Intensiteitskleur per band; spottellingen zichtbaar in cellen.

Change Log (2.4)
─────────────────────────────────────────────────────────────────────
· 2026-04-25 10:58 CEST — Versie 2.4: ThemeManager geïntegreerd (Midnight/DeepOcean/
               HighContrast); dynamische thema-switching via header-menu; recursieve
               kleurtoepassing op alle widgets; opslag van thema-keuze in HAMIOS.ini.
               Interactieve kaart: klik op bestemming toont groot-cirkelpad (kleur
               bepaald door beste propagatieband) + afstand/richting.
               Propagatietrend-advieskaart op basis van SFI/K/band-historiek.
               WSPR SNR-drempel en band-filter instelbaar via _fetch_wspr_spots().
               CONFIG_SCHEMA validatielaag voor HAMIOS.ini (bereik, type, opties).
               Checkboxes/radiobuttons uniform: fg=TEXT_BODY, activeforeground=TEXT_H1.

"""


import configparser
from theme_manager import ThemeManager, THEMES
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
# CAT tijdelijk uitgeschakeld — code intact, interface geblokkeerd tot stabiel
_CAT_DISABLED = True
# ITU regio-overlay tijdelijk uitgeschakeld — grenzen worden herzien
_ITU_DISABLED = True

# ── Platform detectie ──────────────────────────────────────────────────────────
_IS_MAC = sys.platform == "darwin"
_IS_WIN = sys.platform == "win32"
# Platformspecifieke fontnamen
_FONT_SANS = "Helvetica Neue" if _IS_MAC else ("Segoe UI"  if _IS_WIN else "DejaVu Sans")
_FONT_MONO = "Menlo"          if _IS_MAC else ("Consolas"  if _IS_WIN else "DejaVu Sans Mono")

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

# Solar-paneel minimum: header(32) + params(198) + alert-sectie(110) +
#   band-tabel header+11bands(196) + sep(11) + x-flare(44) + PCA(32) = ~623
#   → buffer → 720px (Bz grafiek staat nu in HF band paneel)
SOLAR_MIN_H   = 720

# Minimale venster-hoogte: header + solar + body-marges + advies (vrije hoogte) + ticker
# ADV_SECTION_H + 30px marge voor adv-header en font-scaling variatie
MIN_WINDOW_H  = APP_HDR_H + SOLAR_MIN_H + 6 + ADV_SECTION_H + 30 + TICKER_H

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

# ── ITU regio-grenzen (lat, lon) — officieel ITU RR Art. 5 ───────────────────
# Lijn B: R1/R2 atlantisch (20°W meridiaan, recht van pool tot pool)
_ITU_B = [
    (90, -20), (0, -20), (-90, -20),
]

# Lijn A: R1/R3 Midden-Oosten
# N-pool 40°E → Kaukasus/Oost-Turkije → Irak/Iran → Perzische Golf →
# Golf van Oman → Arabische Zee 11°N/59°E → Z-pool 59°E
_ITU_A = [
    (90,  40),   # N-pool bij 40°E
    (41,  40),   # Kaukasus / Oost-Turkije hoek
    (39,  40),
    (37,  42),   # Turkije / Irak / Syrië
    (36,  44),   # Noord-Irak / Iran grens
    (33,  46),   # Centraal-Irak / Iran
    (29,  48),   # Zuid-Irak / Koeweit / ingang Perzische Golf
    (26,  56),   # VAE / Oman kust
    (22,  59),   # Kaap Ras al-Hadd (Oman) / Golf van Oman
    (11,  59),   # Arabische Zee 11°N/59°E
    (-90, 59),   # Z-pool langs 59°E
]

# Lijn A (Rusland-arm): N-pool 40°E → Oeral → Kazachstaan-grens →
# Mongolië-zuidgrens → Mandsjoerij → Vladivostok
# Rusland, Kazachstaan en Mongolië zijn R1; China/Korea zijn R3
_ITU_A_RUS = [
    (90,  40),   # N-pool (aansluitend op Lijn A)
    (55,  40),   # 55°N / 40°E — richting Oeral
    (51,  52),   # Rusland / Kazachstaan westelijk beginpunt (~Oral)
    (51,  62),   # Rusland / Kazachstaan (Tobol-rivier)
    (51,  83),   # Rusland / Kazachstaan / Altai driewegpunt
    (49,  87),   # Mongolië / Kazachstaan / China hoek
    (46,  94),   # West-Mongolië / China grens
    (46, 106),   # Centraal-Mongolië / China
    (42, 119),   # Oost-Mongolië / Rusland / China driewegpunt (Mandsjoerij)
    (49, 122),   # Amoer-rivier (Rusland / China)
    (48, 130),   # Oessoerikust / Amoer-monding
    (43, 131),   # Vladivostok / Japan Zee kust
]

# Lijn C: R2/R3 Pacific (170°W → 60°N → 120°W)
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
        _FONT_CACHE[key] = tkfont.Font(family=_FONT_SANS, size=size, weight=weight)
    return _FONT_CACHE[key]

# ── Instellingen ───────────────────────────────────────────────────────────────
CONFIG_SCHEMA = {
    "QTH": {
        "lat": {"type": float, "min": -90.0, "max": 90.0, "default": 52.0},
        "lon": {"type": float, "min": -180.0, "max": 180.0, "default": 5.1},
    },
    "App": {
        "refresh": {"type": str, "options": ["30s", "1 min", "5 min", "10 min", "30 min", "1 uur"], "default": "1 min"},
        "mode": {"type": str, "default": "SSB"},
        "power": {"type": str, "default": "100W"},
        "antenna": {"type": str, "default": "Isotropic 0dBi"},
        "dst": {"type": bool, "default": True},
        "show_tips": {"type": bool, "default": True},
        "show_ticker": {"type": bool, "default": True},
        "language": {"type": str, "default": "English"},
    },
    "Map": {
        "show_sun": {"type": bool, "default": True},
        "show_moon": {"type": bool, "default": True},
        "show_locator": {"type": bool, "default": False},
        "show_graylijn": {"type": bool, "default": True},
        "show_iaru": {"type": bool, "default": False},
        "show_cs": {"type": bool, "default": False},
        "show_spots": {"type": bool, "default": False},
        "show_wspr": {"type": bool, "default": False},
        "show_aurora": {"type": bool, "default": True},
    },
    "Graph": {
        "hist_range": {"type": str, "options": ["Uren", "Dagen", "Weken", "Maanden"], "default": "Uren"},
    },
    "Alerts": {
        "k_alert": {"type": int, "min": 0, "max": 9, "default": 4},
        "band_alert": {"type": int, "min": 0, "max": 100, "default": 40},
        "alert_k_en": {"type": bool, "default": True},
        "alert_band_en": {"type": bool, "default": True},
        "alert_xflare_en": {"type": bool, "default": True},
        "alert_pca_en": {"type": bool, "default": True},
    },
    "CAT": {
        "port": {"type": str, "default": ""},
        "baud": {"type": str, "default": "9600"},
        "bits": {"type": str, "default": "8"},
        "parity": {"type": str, "default": "N"},
        "stopbits": {"type": str, "default": "1"},
        "flow": {"type": str, "default": "Geen"},
        "dtr": {"type": bool, "default": False},
        "rts": {"type": bool, "default": False},
        "enabled": {"type": bool, "default": False},
        "radio": {"type": str, "default": "Yaesu CAT"},
        "civ_addr": {"type": str, "default": "0x70"},
    }
}

def _load_settings() -> dict:
    cfg = configparser.ConfigParser()
    cfg.read(SETTINGS_FILE, encoding="utf-8")

    # Pre-extract history selection as it's a special set
    hist_sel_raw = cfg.get("Graph", "selected_bands", fallback="")

    res = {}
    for section, keys in CONFIG_SCHEMA.items():
        for key, spec in keys.items():
            val = None
            try:
                # Use configparser's typed getters
                if spec["type"] == float:
                    val = cfg.getfloat(section, key, fallback=spec["default"])
                elif spec["type"] == int:
                    val = cfg.getint(section, key, fallback=spec["default"])
                elif spec["type"] == bool:
                    val = cfg.getboolean(section, key, fallback=spec["default"])
                else:
                    val = cfg.get(section, key, fallback=spec["default"])

                # Validation: Range check
                if "min" in spec and val < spec["min"]: val = spec["default"]
                if "max" in spec and val > spec["max"]: val = spec["default"]
                # Validation: Option check
                if "options" in spec and val not in spec["options"]: val = spec["default"]

            except (ValueError, TypeError):
                val = spec["default"]

            res[key] = val
            # Handle CAT keys which are stored as 'port', 'baud' etc. in INI but used as 'cat_port' in app
            if section == "CAT":
                res[f"cat_{key}"] = val

    # Special handling for antenna migration
    res["antenna"] = _ANT_KEY_MIGRATION.get(res["antenna"], res["antenna"])

    # Special handling for history set
    res["hist_sel"] = set(hist_sel_raw.split(",")) - {""} if hist_sel_raw else set()

    return res

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
                      show_aurora: bool = True,
                      hist_range: str = "Uren",
                      hist_sel: set = None,
                      k_alert: int = 4,
                      band_alert: int = 40,
                      alert_k_en: bool = True,
                      alert_band_en: bool = True,
                      alert_xflare_en: bool = True,
                      alert_pca_en: bool = True,
                      language: str = "Nederlands",
                      theme: str = "Midnight",
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
                    "language": language, "theme": theme}
    cfg["Map"]   = {"show_sun": str(show_sun), "show_moon": str(show_moon),
                    "show_locator": str(show_locator),
                    "show_graylijn": str(show_graylijn),
                    "show_iaru": str(show_iaru),
                    "show_cs": str(show_cs),
                    "show_spots": str(show_spots),
                    "show_wspr": str(show_wspr),
                    "show_aurora": str(show_aurora)}
    cfg["Graph"]  = {"hist_range": hist_range,
                     "selected_bands": ",".join(sorted(hist_sel)) if hist_sel else ""}
    cfg["Alerts"] = {"k_alert": str(k_alert), "band_alert": str(band_alert),
                     "alert_k_en": str(alert_k_en), "alert_band_en": str(alert_band_en),
                     "alert_xflare_en": str(alert_xflare_en), "alert_pca_en": str(alert_pca_en)}
    cfg["CAT"]    = {"port": cat_port, "baud": cat_baud, "bits": cat_bits,
                     "parity": cat_parity, "stopbits": cat_stopbits,
                     "flow": cat_flow, "dtr": str(cat_dtr), "rts": str(cat_rts),
                     "enabled": str(cat_enabled),
                     "radio": cat_radio, "civ_addr": cat_civ_addr}
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)

def _safe_request(url: str, timeout: int = 10, headers: dict = None) -> tuple[bool, any]:
    """Wrapper voor urllib.request.urlopen om connectiviteit te monitoren.
    Geeft (succes, resultaat) terug.
    """
    if headers is None:
        headers = {"User-Agent": "HAMIOS/1.0"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return True, r.read()
    except (urllib.error.URLError, socket.timeout, Exception):
        return False, None
SOLAR_URL      = "https://www.hamqsl.com/solarxml.php"
SW_SPEED_URL   = "https://services.swpc.noaa.gov/products/summary/solar-wind-speed.json"
SW_MAG_URL     = "https://services.swpc.noaa.gov/products/summary/solar-wind-mag-field.json"
BZ_1DAY_URL    = "https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json"
SPEED_1DAY_URL = "https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json"
# GOES >10 MeV integraalproton flux — meest recente meting (laatste element in array)
# Formaat: [{time_tag, satellite, flux, channel}, ...] — channel "P5" = >10 MeV
PROTON_URL     = "https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json"
# Planetaire Kp-index — 3-uurs blokken, ca. 3 dagen beschikbaar
# Formaat: [["time_tag","kp","a_running","station_count"], ...]
KP_INDEX_URL   = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
# GOES X-ray flux 1-dag — 1-minuut resolutie, short (0.1-0.8 nm) en long (1-8 nm) kanaal
# Formaat: [{time_tag, satellite, current_class, current_ratio, ...}, ...]
XRAY_1DAY_URL  = "https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json"
# 3-daagse geomagnetische storm-kansen — minor (K≥5) / moderate (K≥6) / severe (K≥7)
# Formaat: [[date_str, minor_pct, moderate_pct, severe_pct], ...]
STORM_PROB_URL = "https://services.swpc.noaa.gov/products/noaa-geomagnetic-storm-probabilities.json"
# GIRO/LGDC DIDBase — foF2 van wereldwijde ionosondes
# Formaat antwoord: TSV met commentaarregels (#); kolommen: Time(UTC)  foF2  QD
IONO_URL     = ("https://lgdc.uml.edu/common/DIDBGetValues"
                "?ursiCode={code}&charName=foF2"
                "&fromDate={t_from}&toDate={t_to}")

# Wereldwijde ionosondes: (URSI-code, naam, lat, lon)
# Codes gebaseerd op GIRO/LGDC station registry; niet-responsieve stations
# geven "—" terug door bestaande foutafhandeling in _fetch_ionosonde.
_IONO_STATIONS: list[tuple[str, str, float, float]] = [
    # Europa
    ("DB049", "Dourbes BE",      50.1,   4.6),
    ("JR055", "Juliusruh DE",    54.6,  13.4),
    ("CB953", "Chilton UK",      51.6,  -1.3),
    ("EB040", "Ebro ES",         40.8,   0.5),
    ("AT138", "Athene GR",       38.0,  23.5),
    ("PQ052", "Průhonice CZ",    50.0,  14.6),
    ("RO041", "Rome IT",         41.9,  12.5),
    ("RL052", "Tromso NO",       69.6,  19.2),
    # Noord-Amerika
    ("BC840", "Boulder CO",      40.0,-105.3),
    ("WP937", "Wallops VA",      37.9, -75.5),
    ("MHJ45", "Millstone MA",    42.6, -71.5),
    # Zuid-Amerika
    ("CA830", "Cachoeira BR",   -22.7, -45.0),
    ("SA418", "San Juan PR",     18.5, -66.1),
    # Afrika
    ("HM13R", "Hermanus ZA",    -34.4,  19.2),
    ("AS00Q", "Ascension Isl",   -7.9, -14.4),
    # Azië
    ("KH137", "Khabarovsk RU",   48.5, 135.0),
    ("WU430", "Wuhan CN",        30.5, 114.4),
    ("KK908", "Wakkanai JP",     45.2, 141.8),
    # Australazië
    ("HO535", "Hobart AU",      -42.9, 147.3),
    ("DW41K", "Darwin AU",      -12.5, 130.9),
    ("TH763", "Townsville AU",  -19.6, 146.8),
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
        # ── Solarwind dichtheid (uit plasma 1-day, eerste entry) ──────────────
        try:
            with urllib.request.urlopen(SPEED_1DAY_URL, timeout=6) as r:
                plasma_rows = json.loads(r.read())
            # Formaat: [header_row, [time, density, speed, temperature], ...]
            # Meest recente = laatste rij met geldige density
            p_entry = None
            for row in reversed(plasma_rows[1:] if len(plasma_rows) > 1 else []):
                if isinstance(row, list) and len(row) >= 3:
                    p_entry = row
                    break
            if p_entry:
                dens = p_entry[1]
                data["sw_density"] = f"{float(dens):.1f}" if dens not in (None, "null", "") else "—"
            else:
                data["sw_density"] = "—"
        except Exception:
            data["sw_density"] = "—"
        # ── Planetaire Kp-index (NOAA SWPC summary) ───────────────────────────
        try:
            with urllib.request.urlopen(KP_INDEX_URL, timeout=6) as r:
                kp_rows = json.loads(r.read())
            # Laatste rij met geldige Kp-waarde
            kp_val = None
            for row in reversed(kp_rows[1:] if len(kp_rows) > 1 else []):
                if isinstance(row, list) and len(row) >= 2:
                    try:
                        kp_val = float(row[1])
                        break
                    except (ValueError, TypeError):
                        continue
            data["kp_planet"] = f"{kp_val:.2f}" if kp_val is not None else "—"
        except Exception:
            data["kp_planet"] = "—"
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


# ── Bz / solarwind 24-uurs geschiedenis ──────────────────────────────────────
def _fetch_bz_24h() -> list[tuple[float, float]]:
    """Haal laatste 24u Bz-waarden op van NOAA SWPC (downsampled naar ~120 pts).

    Geeft lijst van (uren_geleden, bz_nT); meest recente punt last.
    """
    try:
        with urllib.request.urlopen(BZ_1DAY_URL, timeout=8) as r:
            rows = json.loads(r.read().decode())
    except Exception:
        return []
    # Eerste rij is header: ["time_tag","bx_gsm","by_gsm","bz_gsm",...]
    if not rows or len(rows) < 2:
        return []
    data_rows = rows[1:]
    now_ts = None
    pts = []
    for row in data_rows:
        try:
            ts_str = row[0]
            bz_val = float(row[3]) if row[3] not in (None, "null", "") else None
            if bz_val is None:
                continue
            # Parse timestamp: "2024-01-01 00:00:00.000"
            ts = datetime.datetime.strptime(ts_str[:19], "%Y-%m-%d %H:%M:%S")
            ts = ts.replace(tzinfo=datetime.timezone.utc)
            if now_ts is None:
                now_ts = datetime.datetime.now(datetime.timezone.utc)
            hours_ago = (now_ts - ts).total_seconds() / 3600
            pts.append((hours_ago, bz_val))
        except Exception:
            continue
    pts.reverse()  # chronologisch (oudste → nieuwste)
    # Downsample naar max 240 punten
    if len(pts) > 240:
        step = len(pts) // 240
        pts = pts[::step]
    return pts


def _fetch_kp_24h() -> list:
    """Haal planetaire Kp-index op (NOAA, 3-uurs blokken, laatste 24-48u).

    Geeft lijst van (hours_ago, kp); meest recente punt last.
    """
    try:
        with urllib.request.urlopen(KP_INDEX_URL, timeout=8) as r:
            rows = json.loads(r.read().decode())
    except Exception:
        return []
    # Eerste rij = kolomhoofden: ["time_tag","kp","a_running","station_count"]
    if not rows or len(rows) < 2:
        return []
    now_ts = datetime.datetime.now(datetime.timezone.utc)
    pts = []
    for row in rows[1:]:
        try:
            ts = datetime.datetime.strptime(row[0][:19], "%Y-%m-%d %H:%M:%S")
            ts = ts.replace(tzinfo=datetime.timezone.utc)
            kp = float(row[1])
            hours_ago = (now_ts - ts).total_seconds() / 3600
            if hours_ago > 48:
                continue
            pts.append((hours_ago, kp))
        except Exception:
            continue
    pts.reverse()
    return pts


def _fetch_xray_24h() -> list:
    """Haal GOES X-ray flux op (0.1–0.8 nm kanaal, laatste 24u).

    Geeft lijst van (hours_ago, flux_watts); downsampled naar max 120 punten.
    """
    try:
        with urllib.request.urlopen(XRAY_1DAY_URL, timeout=8) as r:
            rows = json.loads(r.read().decode())
    except Exception:
        return []
    if not rows:
        return []
    now_ts = datetime.datetime.now(datetime.timezone.utc)
    pts = []
    for entry in rows:
        try:
            # Kies het 0.1-0.8nm (short) kanaal: energy "0.1-0.8nm" of "short"
            if entry.get("energy", "") not in ("0.1-0.8nm", "0.05-0.4nm", "short", ""):
                continue
            flux = float(entry.get("flux") or entry.get("observed_flux") or 0)
            if flux <= 0:
                continue
            ts = datetime.datetime.strptime(entry["time_tag"][:19], "%Y-%m-%d %H:%M:%S")
            ts = ts.replace(tzinfo=datetime.timezone.utc)
            hours_ago = (now_ts - ts).total_seconds() / 3600
            if hours_ago > 24:
                continue
            pts.append((hours_ago, flux))
        except Exception:
            continue
    pts.reverse()
    # Downsample naar max 120 punten
    if len(pts) > 120:
        step = len(pts) // 120
        pts = pts[::step]
    return pts


def _fetch_storm_probs() -> list:
    """Haal 3-daagse geomagnetische storm-kansen op van NOAA SWPC.

    Geeft lijst van dicts {date, minor, moderate, severe} voor 3 dagen.
    """
    try:
        with urllib.request.urlopen(STORM_PROB_URL, timeout=8) as r:
            rows = json.loads(r.read().decode())
    except Exception:
        return []
    # Formaat: [["DateStamp","Minor","Moderate","Severe"], [date, pct, pct, pct], ...]
    result = []
    data_rows = [r for r in rows if isinstance(r, list) and len(r) >= 4
                 and not str(r[0]).startswith("Date")]
    for row in data_rows[:3]:
        try:
            result.append({
                "date":     str(row[0]),
                "minor":    int(row[1]),
                "moderate": int(row[2]),
                "severe":   int(row[3]),
            })
        except Exception:
            continue
    return result


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
    "Magnetic loop":     0,
    "Vertical":          0,
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

# Vertaalsleutels per antenne (internal key → _T key)
_ANT_TR_KEYS = {
    "Isotropic 0dBi":   "ant_isotropic",
    "Magnetic loop":    "ant_mag_loop",
    "Vertical":         "ant_vertical",
    "Groundplane":      "ant_groundplane",
    "Inverted V":       "ant_inverted_v",
    "Dipole ~2dBi":     "ant_dipole",
    "EFHW":             "ant_efhw",
    "OCFD":             "ant_ocfd",
    "J-pole":           "ant_jpole",
    "Long wire":        "ant_longwire",
    "Delta loop ~3dBi": "ant_delta_loop",
    "Quad ~8dBi":       "ant_quad",
    "Yagi ~7dBi":       "ant_yagi",
    "Beam ~10dBi":      "ant_beam",
}
# Migratie: oude (Nederlandse) keys → nieuwe interne keys
_ANT_KEY_MIGRATION = {
    "Magnetische loop": "Magnetic loop",
    "Vertikaal":        "Vertical",
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
# Alleen English is ingebouwd; extra talen worden geladen vanuit langs/*.json
_LANG_NAMES: list[str]       = ["English"]
_LANG_CODES: dict[str, str]  = {"English": "en"}

# Solar-tips per taal: code → {key: (title, body)}
# EN is ingebouwd (zie _SOLAR_TIPS hieronder), rest via taalpacks
_SOLAR_TIPS_PACKS: dict[str, dict[str, tuple]] = {}

_T: dict[str, dict[str, str]] = {
    'exit': {"en": 'Exit'},
    'summer_time': {"en": 'Summer time'},
    'tooltips': {"en": 'Tooltips'},
    'ticker': {"en": 'Ticker'},
    'auto_lbl': {"en": 'Auto:'},
    'lang_lbl': {"en": 'Lang:'},
    'qth_lat_lbl': {"en": 'QTH  Lat:'},
    'lon_lbl': {"en": 'Lon:'},
    'worldmap': {"en": '🌍  World Map'},
    'solar': {"en": '☀  Solar / Ionosphere'},
    'reliability': {"en": '📻  HF Reliability'},
    'schedule': {"en": '📅  Band Opening Schedule'},
    'history': {"en": '📈  Band History'},
    'dx_spots': {"en": '📡  DX Spots'},
    'advice': {"en": '💡  Propagation Advice'},
    'prop_header': {"en": '📶  HF Band Reliability'},
    'hist_header': {"en": '📈  Band History'},
    'sched_header': {"en": '🕐  Band Opening Schedule (local time, today)'},
    'dx_header': {"en": '📡  Live DX Spots (HF)'},
    'adv_header': {"en": '💡  Propagation Analysis & Advice'},
    'sun': {"en": 'Sun'},
    'moon': {"en": 'Moon'},
    'graylijn': {"en": 'Gray line'},
    'locator': {"en": 'Locator'},
    'updated_lbl': {"en": 'Updated'},
    'k_alert_lbl':      {"en": 'Alert K ≥'},
    'band_alert_lbl':   {"en": 'Band open ≥'},
    'alerts_hdr':       {"en": 'Notifications'},
    'alert_xflare_lbl': {"en": 'X-flare / SWF'},
    'alert_pca_lbl':    {"en": 'PCA / Proton'},
    'bz_chart_hdr':     {"en": 'Bz  24h (nT)'},
    'bz_now_lbl':       {"en": 'now'},
    'day_hdr': {"en": 'Day'},
    'night_hdr': {"en": 'Night'},
    'band_hdr': {"en": 'Band'},
    'mode_lbl': {"en": 'Mode:'},
    'power_lbl': {"en": 'Power:'},
    'ant_lbl': {"en": 'Antenna:'},
    'ant_isotropic':  {"en": 'Isotropic 0dBi'},
    'ant_mag_loop':   {"en": 'Magnetic loop'},
    'ant_vertical':   {"en": 'Vertical'},
    'ant_groundplane':{"en": 'Groundplane'},
    'ant_inverted_v': {"en": 'Inverted V'},
    'ant_dipole':     {"en": 'Dipole ~2dBi'},
    'ant_efhw':       {"en": 'EFHW'},
    'ant_ocfd':       {"en": 'OCFD'},
    'ant_jpole':      {"en": 'J-pole'},
    'ant_longwire':   {"en": 'Long wire'},
    'ant_delta_loop': {"en": 'Delta loop ~3dBi'},
    'ant_quad':       {"en": 'Quad ~8dBi'},
    'ant_yagi':       {"en": 'Yagi ~7dBi'},
    'ant_beam':       {"en": 'Beam ~10dBi'},
    'day_auto': {"en": 'Day (auto)'},
    'closed': {"en": 'Closed'},
    'cond_good': {"en": 'Good'},
    'cond_fair': {"en": 'Fair'},
    'cond_poor': {"en": 'Poor'},
    'cond_closed': {"en": 'Closed'},
    'status_lbl': {"en": 'Status:'},
    'reason_lbl': {"en": 'Reason:'},
    'reason_muf_luf': {"en": 'Above MUF or below LUF'},
    'reliability_lbl': {"en": 'Reliability:'},
    'modes_lbl': {"en": 'Modes:'},
    'total_snr': {"en": 'Total:'},
    'quality_lbl': {"en": 'Quality:'},
    'local_lbl': {"en": 'local'},
    'hist_range_h': {"en": 'Hours'},
    'hist_range_d': {"en": 'Days'},
    'hist_range_w': {"en": 'Weeks'},
    'hist_range_m': {"en": 'Months'},
    'no_hist_data': {"en": 'No historical data available yet'},
    'hist_tooltip_hdr': {"en": 'Band History  —  {ts}'},
    'own_cont_lbl': {"en": 'Own continent'},
    'dx_loading': {"en": 'Loading…'},
    'no_dx_spots': {"en": 'No HF spots available'},
    'dx_col_band':    {"en": 'Band'},
    'dx_col_spotter': {"en": 'Spotter'},
    'dx_col_comment': {"en": 'Comment'},
    'hf_col_start':   {"en": 'Start'},
    'hf_col_mode':    {"en": 'Mode'},
    'dx_of': {"en": 'of'},
    'dx_own_cont_filter': {"en": ' · own continent'},
    'no_spots_ts': {"en": 'No spots available  ·  {ts}'},
    'dx_status_fmt': {"en": '{n} of {total} spots  (HF{filt})  ·  {ts}'},
    'map_display_lbl': {"en": 'Display:'},
    'map_data_lbl':    {"en": 'Data:'},
    'sw_density_lbl':  {"en": 'SW density (n/cm³)'},
    'kp_planet_lbl':   {"en": 'Kp (planetary)'},
    'storm_forecast_hdr': {"en": 'Storm forecast (3d)'},
    'kp_chart_hdr':    {"en": 'Kp  48h (3h blocks)'},
    'xray_chart_hdr':  {"en": 'X-ray  24h'},
    'wspr_lbl':        {"en": 'W'},
    'map_nolib': {"en": 'pip install pillow  for map display'},
    'map_downloading': {"en": '⬇ Downloading NASA map…'},
    'distance_lbl': {"en": 'Distance'},
    'direction_lbl': {"en": 'Direction'},
    'right_clk_clear': {"en": 'right-click to clear'},
    'path_day': {"en": 'day'},
    'path_night': {"en": 'night'},
    'path_hops': {"en": 'hop'},
    'path_closed': {"en": 'no open bands'},
    'tray_show': {"en": 'Show HAMIOS'},
    'tray_exit': {"en": 'Exit'},
    'xflare_warning': {"en": '☢  SWF warning: {xray} flare detected. HF dayside disrupted (~{dur} min).'},
    'xflare_notify_body': {"en": 'Short Wave Fadeout expected (~{dur} min). HF dayside temporarily disrupted.'},
    'pca_warning': {"en": '☢  PCA warning S{s}: proton flux {pf:.1f} pfu — polar routes blocked (~{dur}). 160m–40m polar paths unusable.'},
    'pca_dur_s5': {"en": '3–7 days'},
    'pca_dur_s3': {"en": '2–4 days'},
    'pca_dur_s1': {"en": '1–2 days'},
    'pca_notify_body': {"en": 'Proton flux: {pf:.1f} pfu. Polar Cap Absorption — polar routes blocked (~{dur}).'},
    'k_alert_notify_title': {"en": 'K-index {k} — geomagnetic activity'},
    'k_alert_notify_body': {"en": 'K={k}, A={a} — HF propagation disrupted. Use lower bands.'},
    'geo_quiet': {"en": 'quiet'},
    'geo_unsettled': {"en": 'unsettled'},
    'geo_storm': {"en": 'storm'},
    'geo_severe': {"en": 'severe storm'},
    'score_excellent': {"en": 'Excellent 🏆'},
    'score_good': {"en": 'Good ✅'},
    'score_fair': {"en": 'Fair ⚡'},
    'score_poor': {"en": 'Poor ⚠️'},
    'day_label': {"en": 'Day'},
    'night_label': {"en": 'Night'},
    'trend_improving': {"en": 'improving'},
    'trend_worsening': {"en": 'deteriorating'},
    'avg_band_quality': {"en": 'avg. band quality'},
    'adv_best_bands': {"en": 'Best bands now:  {bstr}{extra}'},
    'adv_best_extra': {"en": '  ({n} bands open)'},
    'adv_no_bands': {"en": 'All HF bands are currently closed.'},
    'adv_geo_severe': {"en": 'Severe geomagnetic storm  K={k}, A={a} ({kwal}) — HF almost unusable, auroral absorption on all routes. Wait for recovery (normally within 12–24h).'},
    'adv_geo_storm': {"en": 'Geomagnetic storm  K={k}, A={a} ({kwal}) — polar routes blocked, 40m/80m most reliable. High bands and DX strongly disturbed.'},
    'adv_geo_elevated': {"en": 'Elevated geo-activity  K={k}, A={a} ({kwal}) — lower bands more stable; avoid trans-polar DX. Consider 40m/80m for reliable contacts.'},
    'adv_geo_quiet': {"en": 'Quiet geo conditions  K={k}, A={a} — optimal for all routes incl. polar paths and DX.'},
    'adv_sol_exceptional': {"en": 'Exceptional solar activity  SFI={sfi}, SSN={ssn} — solar cycle maximum. 10m/12m/15m open for worldwide DX; chance of Es enhancement and TEP.'},
    'adv_sol_high': {"en": 'High solar activity  SFI={sfi}, SSN={ssn} — excellent for 10m to 17m DX. F2 propagation strong; MUF high, long skips possible.'},
    'adv_sol_good': {"en": 'Good solar activity  SFI={sfi}, SSN={ssn} — 20m and 17m are primary DX bands; 15m may be open. Expect reliable F2 propagation during the day.'},
    'adv_sol_moderate': {"en": 'Moderate solar activity  SFI={sfi}, SSN={ssn} — 20m/40m most reliable. High bands uncertain; 80m good for regional traffic.'},
    'adv_sol_low': {"en": 'Low solar activity  SFI={sfi}, SSN={ssn} — 40m and 80m offer most chances. Bands ≥15m mostly closed; 160m for night DX.'},
    'adv_sw_stormy': {"en": 'Stormy solar wind  v={spd} km/s, Bz={bz} nT — increased chance of CME impact; K-index may rise quickly. Monitor conditions actively.'},
    'adv_sw_elevated': {"en": "Elevated solar wind  v={spd} km/s, Bz={bz} nT — negative Bz couples to Earth's field → K-index rise possible. Stick to lower bands."},
    'adv_sw_calm': {"en": "Calm solar wind  v={spd} km/s, Bz={bz} nT — positive Bz shields Earth's field. Stable conditions."},
    'adv_sw_normal': {"en": 'Normal solar wind  v={spd} km/s, Bz={bz} nT — no direct effect on propagation expected.'},
    'adv_pf_s5': {"en": 'SEVERE proton event S5  ({pf} pfu) — Polar Cap Absorption active. All polar routes fully blocked 3–7 days. Use equatorial paths (20m/17m).'},
    'adv_pf_s3': {"en": 'Proton event S3  ({pf} pfu) — PCA active: polar routes (EU→JA/W via pole) blocked 2–4 days. 160m/80m/40m polar paths unusable.'},
    'adv_pf_s1': {"en": 'Elevated proton flux S1  ({pf} pfu) — PCA may begin. Monitor polar routes on 40m. Chance of further escalation with active flare activity.'},
    'adv_pf_normal': {"en": 'Proton flux normal  ({pf} pfu) — no Polar Cap Absorption. Polar routes unaffected by proton flux.'},
    'adv_xflare_x': {"en": 'X-flare detected  ({xray}) — Short Wave Fadeout (SWF) possible on dayside; HF temporarily blocked. Recovery expected within 15–60 min.'},
    'adv_xflare_m': {"en": 'M-flare active  ({xray}) — minor SWF possible on lower HF. Increased chance of Proton Event (PCA) at M5+.'},
    'adv_muf_28': {"en": 'MUF={muf} MHz — 10m through 20m all open; F2 layer optimal'},
    'adv_muf_14': {"en": 'MUF={muf} MHz — 20m open; bands > {muf0} MHz closed'},
    'adv_muf_7': {"en": 'MUF={muf} MHz — only 40m–80m usable'},
    'adv_muf_low': {"en": 'MUF={muf} MHz — ionosphere weak; only 80m/160m'},
    'adv_iono_fmt': {"en": 'Ionosphere: {muf_txt}. Estimated LUF ≈ {luf} MHz ({luf_note}).'},
    'adv_luf_elevated': {"en": 'elevated by K-index'},
    'adv_luf_normal': {"en": 'normal'},
    'adv_morning': {"en": 'Morning ({h}:xx local) — F2 layer building up; 20m becoming usable quickly. Grey-line chances for DX paths towards America and Asia.'},
    'adv_midday': {"en": 'Midday ({h}:xx local) — F2 at maximum height; best window for 15m/17m/20m DX. Try SSB or FT8 for trans-Atlantic contacts.'},
    'adv_afternoon': {"en": 'Afternoon ({h}:xx local) — Grey-line approaching; excellent for DX towards Asia and Pacific. 15m and 17m often excellent at this time.'},
    'adv_early_night': {"en": 'Early night ({h}:xx local) — 40m and 80m open for regional European traffic. F2 layer falling; LUF rising on short paths.'},
    'adv_night': {"en": 'Night ({h}:xx local) — 160m and 80m active for trans-Atlantic DX. 40m good for North America. FT8 on low bands for DX distances > 5000 km.'},
    'adv_pre_morning': {"en": 'Pre-dawn ({h}:xx local) — Grey-line approaching; 80m/40m DX window towards Asia/Pacific. 20m starting to open towards America.'},
    'adv_mode_weak': {"en": 'Mode advice: conditions weak ({pct}% on {band}) — consider FT8 (+25 dB gain over SSB) or CW (+10 dB). Current SNR budget: {snr} dB.'},
    'adv_mode_good': {"en": 'Mode advice: good conditions ({pct}% on {band}) — SSB well usable. SNR budget {snr} dB; increase power or improve antenna for more range.'},
    'adv_mode_default': {"en": 'Mode advice: {mode} suitable for current {pct}% on {band}. SNR budget: {snr} dB. FT8 always gives +25 dB extra margin.'},
    'adv_abs_high': {"en": 'Auroral absorption elevated (K={k}, QTH {lat}°) — trans-polar paths (Europe→Canada, Europe→Japan via pole) strongly attenuated. Use equatorial routes via 20m/17m.'},
    'adv_abs_low': {"en": 'Minor absorption possible (K={k}, QTH {lat}°) — polar paths may be sporadically disturbed. Monitor 40m for usability.'},
    'adv_es_high': {"en": 'Sporadic-E chance HIGH (month {month}, {h}:xx local) — 6m/4m/2m may unexpectedly open for distances of 700–2500 km. Monitor 50.313 (FT8) and 50.150 (SSB). Typically 15–90 min duration.'},
    'adv_es_seasonal': {"en": 'Sporadic-E season active (month {month}) but outside peak hours — chance of 6m/4m openings low; most active 09–14h and 17–22h local.'},
    'adv_es_winter': {"en": 'Winter-Es possible (month {month}, {h}:xx local) — rare but sudden openings on 6m; monitor 50.313 MHz.'},
    'adv_tep': {"en": 'TEP window (day {doy}, {h}:xx local) — trans-equatorial propagation possible. Paths towards Central Africa and Latin America on 50 MHz and 144 MHz may be open. Most likely 13–17h local.'},
    'adv_trend_change': {"en": 'Propagation {direction} (last {age}h): {parts}.'},
    'adv_trend_stable': {"en": 'Propagation stable (last {age}h no significant change).'},
    'adv_sc_max': {"en": 'Solar Cycle 25 MAXIMUM — SSN={ssn} (peak expected 2025–2026). Optimal F2 propagation on high bands; enjoy 10m–15m DX while the cycle is at its best.'},
    'adv_sc_high': {"en": 'Solar Cycle 25 high/peak phase — SSN={ssn}. High bands (10m–17m) regularly open for DX. Expect further increase towards cycle peak.'},
    'adv_sc_rising': {"en": 'Solar Cycle 25 rising phase — SSN={ssn}. Cycle building up; 20m–17m reliable, higher bands variable. Positive trend expected.'},
    'adv_sc_transition': {"en": 'Solar cycle in transition — SSN={ssn}. Depending on trend: check whether SSN is rising or falling. 20m/40m form the backbone.'},
    'adv_sc_low': {"en": 'Solar cycle low — SSN={ssn}. Cycle possibly at minimum or early stage; 40m/80m/160m are the most reliable bands.'},
    'adv_storm_recovery': {"en": 'Storm recovery forecast: A={a}, K={k} — estimated normalisation time ≈{rh}h after peak. HF recovery proceeds low-to-high (40m first, then 20m/15m). Monitor K-index for recovery below 3.'},
    'adv_dx_cluster': {"en": 'DX cluster: {n} spots active — top continents: {top}. '},
    'adv_dx_oceania': {"en": 'Oceania ({n}×) active → good East opportunity. '},
    'adv_dx_asia': {"en": 'Asia ({n}×) well represented. '},
    'adv_dx_routes': {"en": 'Optimal DX routes now: {routes}.'},
    'adv_overall_score': {"en": 'Overall propagation score: {overall}  (SFI {sfi} · K {k} · {open} bands open). {daynight} conditions, QTH {lat}°N.'},
    'dx_route_eu_ja_day': {"en": 'EU→JA (Asia) via long path, 14–21 MHz'},
    'dx_route_eu_w_day': {"en": 'EU→W (North America) short path, 14–21 MHz'},
    'dx_route_eu_af_day': {"en": 'EU→Africa short path, 14–28 MHz'},
    'dx_route_eu_oc_day': {"en": 'EU→VK/ZL (Pacific) long path, 14–21 MHz'},
    'dx_route_eu_w_night': {"en": 'EU→W (North America) 40m–80m night DX'},
    'dx_route_eu_ja_night': {"en": 'EU→JA (Asia) 40m–20m via polar night path'},
    'cat_dlg_title': {"en": 'CAT Interface Settings'},
    'cat_ser_port': {"en": 'Serial Port'},
    'cat_port_lbl': {"en": 'Port:'},
    'cat_scan': {"en": 'Scan ▾'},
    'cat_no_ports': {"en": 'No ports found'},
    'cat_no_pyserial': {"en": 'pyserial not installed'},
    'cat_ser_params': {"en": 'Serial Parameters'},
    'cat_baud_lbl': {"en": 'Baud rate:'},
    'cat_bits_lbl': {"en": 'Data bits:'},
    'cat_parity_lbl': {"en": 'Parity:'},
    'cat_stops_lbl': {"en": 'Stop bits:'},
    'cat_hs_title': {"en": 'Handshake & Line Signals'},
    'cat_hs_lbl': {"en": 'Handshake:'},
    'cat_enabled_cb': {"en": 'Enabled'},
    'cat_enable_lbl': {"en": 'Enable CAT interface'},
    'cat_radio_title': {"en": 'Radio type'},
    'cat_type_lbl': {"en": 'Type:'},
    'cat_civ_lbl': {"en": 'CI-V address:'},
    'cat_civ_hint': {"en": 'hex, e.g. 0x70 (IC-7300), 0x94 (IC-705)'},
    'cat_test_btn': {"en": 'Test connection'},
    'cat_save_btn': {"en": 'Save'},
    'cat_cancel_btn': {"en": 'Cancel'},
    'cat_st_no_ser': {"en": '⚠  pyserial not installed  (pip install pyserial)'},
    'cat_st_no_port': {"en": '⚠  No port specified.'},
    'cat_st_ok': {"en": '✔  {port} opened at {baud} baud — connection OK'},
    'cat_par_none': {"en": 'N – None'},
    'cat_par_even': {"en": 'E – Even'},
    'cat_par_odd': {"en": 'O – Odd'},
    'cat_par_mark': {"en": 'M – Mark'},
    'cat_par_space': {"en": 'S – Space'},
    'cat_flow_none': {"en": 'None'},
}

# ── Ingebouwde EN solar-tooltip teksten ──────────────────────────────────────
_SOLAR_TIPS: dict[str, tuple[str, str]] = {
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
                   "High values disturb the ionosphere (higher LUF)."),
    "k_index":    ("K-index (3-hourly)",
                   "3-hourly geomagnetic activity (0–9).\n"
                   "0–2: quiet  |  3–4: unsettled  |  5+: storm\n"
                   "Direct effect on HF absorption and polar routes."),
    "xray":       ("X-ray flux (GOES)",
                   "Solar X-ray flux. Class A/B/C/M/X.\n"
                   "X-flares can suddenly block the ionosphere on the dayside\n"
                   "(SWF – Short Wave Fadeout)."),
    "muf":        ("Maximum Usable Frequency (MUF)",
                   "Highest frequency reflected by the F2-layer on a given path.\n"
                   "Bands above MUF are closed.\n"
                   "Calculated via foF2 × oblique factor 3.8."),
    "luf":        ("Lowest Usable Frequency (LUF)",
                   "Lowest usable frequency due to D-layer absorption.\n"
                   "Bands below LUF are absorbed too strongly.\n"
                   "Rises with higher K-index and auroral activity."),
    "sw_speed":   ("Solar wind speed (km/s)",
                   "Solar wind speed measured by DSCOVR/ACE (NOAA).\n"
                   "< 400: quiet  |  400–600: elevated  |  > 600: stormy\n"
                   "Higher speed can increase geomagnetic activity."),
    "sw_bz":      ("Bz — interplanetary magnetic field (nT)",
                   "Northward (positive) or southward (negative) component\n"
                   "of the interplanetary magnetic field (IMF).\n"
                   "Bz < −10 nT: risk of geomagnetic storm increases strongly.\n"
                   "Negative Bz couples to the Earth's field → higher K-index."),
    "sw_density": ("Solar wind proton density (n/cm³)",
                   "Number of protons per cubic centimetre in the solar wind.\n"
                   "< 5: low  |  5–15: normal  |  > 15: elevated\n"
                   "High density amplifies geomagnetic effects of a CME.\n"
                   "Combined with speed: ram pressure = ½ × ρ × v²."),
    "kp_planet":  ("Planetary K-index (Kp)",
                   "Global 3-hour geomagnetic activity index averaged over 13 stations.\n"
                   "0–2: quiet  |  3–4: unsettled  |  5: minor storm (G1)\n"
                   "6: moderate (G2)  |  7: strong (G3)  |  ≥ 8: severe/extreme\n"
                   "More representative than a single local K-index."),
    "iono_fof2":  ("Ionosonde foF2 — measured vs model (MHz)",
                   "foF2 = critical frequency of the F2-layer (ionosonde measurement).\n"
                   "Measured: current value from nearest European ionosonde\n"
                   "(GIRO/LGDC DIDBase, interval ≈15 min).\n"
                   "Model: HAMIOS calculation based on SFI and SSN.\n"
                   "Green = good match  |  Orange = moderate deviation\n"
                   "Red = large deviation (storm or unusual activity)."),
    "proton_flux":("Proton flux >10 MeV (pfu)",
                   "High-energy protons from solar flares.\n"
                   "< 10 pfu: normal  |  ≥ 10: S1 (PCA possible)\n"
                   "≥ 100 pfu: S3 — polar routes blocked\n"
                   "≥ 1000 pfu: S5 — severe PCA, all polar paths closed\n"
                   "PCA blocks polar routes for 1–7 days."),
    "tip_k_alert":   ("K-index alert",
                      "Notify when the K-index reaches or exceeds the set threshold.\n"
                      "K ≥ 5: geomagnetic storm — HF propagation may be disrupted.\n"
                      "Set to 3–4 for early warning, 5+ for storm conditions."),
    "tip_band_alert":("Band opening alert",
                      "Notify when a band's propagation score reaches the set percentage.\n"
                      "A higher threshold reduces false positives.\n"
                      "Recommended: 50–70% for active monitoring."),
    "tip_xflare_alert":("X-flare alert",
                        "Notify on X-class solar flares (X-ray flux ≥ 10⁻⁴ W/m²).\n"
                        "X-flares can cause Short Wave Fadeout (SWF) on the sunlit side,\n"
                        "blocking HF propagation for minutes to hours."),
    "tip_pca_alert": ("Polar Cap Absorption (PCA) alert",
                      "Notify when proton flux ≥ 10 pfu (S1 event).\n"
                      "High-energy protons from solar flares cause PCA,\n"
                      "blocking polar routes for 1–7 days.\n"
                      "Most critical for paths through Arctic/Antarctic regions."),
}

# ── Taalpack-loader ──────────────────────────────────────────────────────────
def _load_lang_packs() -> None:
    """Scan langs/ naast het script/EXE en laad JSON-taalpacks."""
    import json as _json, os as _os, sys as _sys

    if getattr(_sys, "frozen", False):
        base = _os.path.dirname(_sys.executable)
    else:
        base = _os.path.dirname(_os.path.abspath(__file__))

    langs_dir = _os.path.join(base, "langs")
    if not _os.path.isdir(langs_dir):
        return

    for fn in sorted(_os.listdir(langs_dir)):
        if not fn.lower().endswith(".json"):
            continue
        try:
            with open(_os.path.join(langs_dir, fn), encoding="utf-8") as _f:
                pack = _json.load(_f)
            meta = pack.get("meta", {})
            code = str(meta.get("code", "")).lower().strip()
            name = str(meta.get("name", code)).strip()
            if not code or code == "en":
                continue
            # Vertalingen samenvoegen in _T
            for key, val in pack.get("strings", {}).items():
                if key in _T:
                    _T[key][code] = str(val)
                else:
                    _T[key] = {"en": key, code: str(val)}
            # Solar tips samenvoegen
            tips: dict[str, tuple] = {}
            for tip_key, tip_val in pack.get("solar_tips", {}).items():
                if isinstance(tip_val, list) and len(tip_val) >= 2:
                    tips[tip_key] = (str(tip_val[0]), str(tip_val[1]))
            if tips:
                _SOLAR_TIPS_PACKS[code] = tips
            # Taal registreren (bewaar volgorde)
            if name not in _LANG_NAMES:
                _LANG_NAMES.append(name)
                _LANG_CODES[name] = code
        except Exception:
            pass  # beschadigd of ongeldig bestand — overslaan

_load_lang_packs()

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


def _fetch_wspr_spots(snr_min: int = -20, band_filter: set = None) -> list:
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

            # SNR filter
            if snr < snr_min:
                continue
            # Band filter
            if band_filter and band_name not in band_filter:
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
        if _IS_MAC:
            tw.wm_attributes("-topmost", True)
        tw.configure(bg=BORDER)

        outer = tk.Frame(tw, bg=BG_SURFACE, padx=10, pady=8)
        outer.pack(padx=1, pady=1)   # 1px BORDER zichtbaar rondom

        def _f(sz=9, bold=False):
            return tkfont.Font(family=_FONT_SANS, size=sz,
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
        self.root.title("HAMIOS v3.0")
        self.root.configure(bg=BG_ROOT)

        # Geometrie instellen vóór _build_ui — geen root.update() nodig, geen flicker.
        # winfo_screenwidth/height werkt direct zonder update().
        _scr_w = root.winfo_screenwidth()
        _scr_h = root.winfo_screenheight()
        _DX_EXTRA = 368            # DX-kolom 360 px + padx 8 px
        _ini_w = min(1400 + _DX_EXTRA, _scr_w - 60)
        _ini_h = 1220
        _ini_y = max(0, (_scr_h - _ini_h) // 2)
        root.geometry(f"{_ini_w}x{_ini_h}+{(_scr_w-_ini_w)//2}+{_ini_y}")
        root.minsize(min(900 + _DX_EXTRA, _scr_w - 60), MIN_WINDOW_H)

        self._solar_data: dict = {}
        self._solar_after_id = None
        self._clock_after_id = None

        s = _load_settings()
        self._qth_lat = s["lat"]
        self._qth_lon = s["lon"]

        self._mode_var    = tk.StringVar(value=s["mode"])
        self._power_var   = tk.StringVar(value=s["power"])
        self._ant_var     = tk.StringVar(value=s["antenna"])
        # Display-var voor vertaalde antenne naam (textvariable in menubutton)
        self._ant_display_var = tk.StringVar(
            value=self._tr_static(_ANT_TR_KEYS.get(s["antenna"], ""), s["antenna"],
                                  _LANG_CODES.get(s["language"], "en")))
        self._day_var     = tk.BooleanVar(value=True)
        self._refresh_var = tk.StringVar(value=s["refresh"])
        _saved_lang = s["language"] if s["language"] in _LANG_NAMES else "English"
        self._lang_var    = tk.StringVar(value=_saved_lang)
        self._last_band_pct = [(n, f, 0) for n, f, _ in _BANDS]
        self._history:    list = []   # gevuld door background-thread na _prune_history
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
        self._show_aurora_var   = tk.BooleanVar(value=s["show_aurora"])
        self._show_spots_var    = tk.BooleanVar(value=s["show_spots"])
        self._spot_hit_areas:   list = []   # [{x, y, r, spot}, ...] voor klik-detectie
        self._show_wspr_var     = tk.BooleanVar(value=s["show_wspr"])
        self._wspr_spots:       list = []
        self._wspr_after_id             = None
        self._wspr_snr_min       = tk.IntVar(value=s.get("wspr_snr_min", -20))
        self._wspr_band_filter   = tk.StringVar(value=",".join(s.get("wspr_band_filter", [])))
        self._qth_lat_var = tk.StringVar(value=f"{self._qth_lat:.2f}")
        self._qth_lon_var = tk.StringVar(value=f"{self._qth_lon:.2f}")
        self._tr_widgets: dict = {}   # key → widget of list van widgets voor vertalingen
        # ---- Theme Manager Init ------------------------------------------------
        self.theme_manager = ThemeManager(s)
        self._theme_var = tk.StringVar(value=self.theme_manager.current_theme_name)
        # UI wordt opgebouwd met Midnight-constanten; remap daarna naar opgeslagen thema
        self._applied_theme_name = "Midnight"
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
        self._k_alert_var          = tk.IntVar(value=s["k_alert"])
        self._band_alert_var       = tk.IntVar(value=s["band_alert"])
        self._alert_k_en_var       = tk.BooleanVar(value=s.get("alert_k_en",    True))
        self._alert_band_en_var    = tk.BooleanVar(value=s.get("alert_band_en", True))
        self._alert_xflare_en_var  = tk.BooleanVar(value=s.get("alert_xflare_en", True))
        self._alert_pca_en_var     = tk.BooleanVar(value=s.get("alert_pca_en",  True))
        self._prev_band_open: dict = {}   # name → bool, voor band-opening detectie
        self._prev_k_above: bool   = False
        self._tray_icon             = None
        self._last_xflare: str      = ""   # voor dedup van X-flare tray-notificatie
        self._xflare_var            = tk.StringVar(value="")
        self._last_pca_level: int   = 0    # S-level van vorig proton event (0 = geen)
        self._last_fof2_model: float = 0.0 # model foF2 (MHz), bijgewerkt door _recalc_prop
        self._dx_all_spots: list    = []   # ruwe spots van dxwatch
        self._dx_after_id           = None
        self._net_ok: bool          = True   # False = laatste solar-fetch mislukt
        self._dx_spot_history: list = []     # [(datetime_utc, band_str), ...] — 24h buffer
        self._dx_heatmap_mode: bool = False  # True = heatmap, False = lijst
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
        # Pas opgeslagen thema toe (UI is gebouwd met Midnight-constanten)
        self._applied_theme_name = "Midnight"
        self._apply_theme()
        # Herstel legenda-selectie visueel na opbouw UI
        if self._hist_sel:
            for bname, (lbl_d, lbl_n) in self._leg_widgets.items():
                color  = _BAND_COLORS.get(bname, TEXT_DIM)
                active = bname in self._hist_sel
                lbl_d.config(fg=color     if active else TEXT_DIM)
                lbl_n.config(fg=TEXT_BODY if active else TEXT_DIM,
                             font=_font(8, "bold") if active else _font(8))
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
        # Geschiedenis: prune + laden in background zodat main thread niet blokkeert
        threading.Thread(target=self._load_history_bg, daemon=True).start()
        # Venster tonen na volledige opbouw — correct gecentreerd, geen flicker
        self.root.after(1, self.root.deiconify)

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
    @staticmethod
    def _tr_static(key: str, fallback: str, lang: str) -> str:
        """Vertaling zonder instantie-context (voor gebruik in __init__)."""
        entry = _T.get(key, {})
        return entry.get(lang) or entry.get("en") or fallback

    def _tr(self, key: str) -> str:
        """Geeft vertaling terug; valt terug op EN als taalpack de sleutel mist."""
        lang = _LANG_CODES.get(self._lang_var.get(), "en")
        entry = _T.get(key, {})
        return entry.get(lang) or entry.get("en", key)

    def _refresh_ant_display(self):
        """Zet de vertaalde antenne naam in _ant_display_var op basis van huidige taal."""
        key = self._ant_var.get()
        tr_key = _ANT_TR_KEYS.get(key, "")
        self._ant_display_var.set(self._tr(tr_key) if tr_key else key)
        # Menu labels herbouwen
        if hasattr(self, "_ant_menu"):
            for i, opt in enumerate(list(_ANT_DB.keys())):
                tr = _ANT_TR_KEYS.get(opt, "")
                self._ant_menu.entryconfigure(i, label=self._tr(tr) if tr else opt)

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
        # Antenne display var + menu labels bijwerken
        self._refresh_ant_display()
        # Canvas-panelen opnieuw tekenen (kolom headers, labels, statusteksten)
        self._draw_prop_bars(self._last_band_pct)
        self._filter_dx_spots()
        self._draw_kp_bars(getattr(self, "_last_kp_pts", []))
        self._draw_xray_graph(getattr(self, "_last_xray_pts", []))
        # Advice opnieuw renderen bij taalwissel
        self._update_advice()

    def _on_lang_change(self, *_):
        self._apply_translations()
        self._save_cur_settings()

    def _on_theme_change(self, theme_name):
        """Wissel thema en pas kleuren toe op alle widgets."""
        if self.theme_manager.set_theme(theme_name):
            self._theme_var.set(theme_name)
            self._apply_theme()
            self._save_cur_settings()
            # Kaart moet opnieuw renderen want kleuren kunnen veranderen (indien themed)
            self._draw_map()

    def _apply_theme(self):
        """Doorloop alle widgets en remap kleuren van vorig naar nieuw thema."""
        tm       = self.theme_manager
        new_name = tm.current_theme_name
        prev_name = getattr(self, "_applied_theme_name", "Midnight")

        prev = THEMES[prev_name]
        new  = THEMES[new_name]

        # Bouw kleur-remap: {oud_hex_lower → nieuw_hex}
        color_map: dict[str, str] = {}
        for key in new:
            if prev[key].lower() != new[key].lower():
                color_map[prev[key].lower()] = new[key]

        self.root.configure(bg=new["BG_ROOT"])

        def remap(c: str) -> str:
            return color_map.get(c.lower(), c) if c else c

        def walk(widget):
            try:
                wc = widget.winfo_class()
                if wc in ("Frame", "Toplevel", "LabelFrame"):
                    widget.configure(bg=remap(widget.cget("bg")))
                elif wc == "Label":
                    widget.configure(bg=remap(widget.cget("bg")),
                                     fg=remap(widget.cget("fg")))
                elif wc == "Button":
                    widget.configure(bg=remap(widget.cget("bg")),
                                     fg=remap(widget.cget("fg")),
                                     activebackground=remap(widget.cget("activebackground")),
                                     activeforeground=remap(widget.cget("activeforeground")))
                elif wc in ("Checkbutton", "Radiobutton"):
                    widget.configure(bg=remap(widget.cget("bg")),
                                     fg=remap(widget.cget("fg")),
                                     selectcolor=remap(widget.cget("selectcolor")),
                                     activebackground=remap(widget.cget("activebackground")),
                                     activeforeground=remap(widget.cget("activeforeground")))
                elif wc == "Menubutton":
                    widget.configure(bg=remap(widget.cget("bg")),
                                     fg=remap(widget.cget("fg")),
                                     activebackground=remap(widget.cget("activebackground")),
                                     activeforeground=remap(widget.cget("activeforeground")))
                elif wc == "Canvas":
                    widget.configure(bg=remap(widget.cget("bg")))
                elif wc == "Scrollbar":
                    widget.configure(bg=remap(widget.cget("bg")),
                                     troughcolor=remap(widget.cget("troughcolor")))
                elif wc == "Spinbox":
                    widget.configure(bg=remap(widget.cget("bg")),
                                     fg=remap(widget.cget("fg")),
                                     buttonbackground=remap(widget.cget("buttonbackground")))
                elif wc == "Entry":
                    widget.configure(bg=remap(widget.cget("bg")),
                                     fg=remap(widget.cget("fg")),
                                     insertbackground=remap(widget.cget("insertbackground")))
                for child in widget.winfo_children():
                    walk(child)
            except Exception:
                pass

        walk(self.root)
        self._applied_theme_name = new_name
        # Canvas-inhoud opnieuw tekenen met nieuwe kleuren
        self._draw_bz_graph(getattr(self, "_last_bz_pts", []))
        if hasattr(self, "_last_band_pct"):
            self._draw_prop_bars(self._last_band_pct)

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
        """Eenmalige VFO-lezing bij opstarten (geen herhaling)."""
        if _CAT_DISABLED:
            return
        self._cat_stop_poll()
        if self._cat_enabled_var.get() and _SERIAL_OK:
            self._cat_poll_after_id = self.root.after(500, self._cat_read_once)

    def _cat_stop_poll(self):
        if self._cat_poll_after_id is not None:
            self.root.after_cancel(self._cat_poll_after_id)
            self._cat_poll_after_id = None

    def _cat_read_once(self):
        """Lees VFO-A (en VFO-B) eenmalig van de radio en toon de waarde."""
        if not self._cat_enabled_var.get() or not _SERIAL_OK:
            return
        port = self._cat_port_var.get().strip()
        if not port:
            return

        def _do_read():
            if not self._cat_poll_lock.acquire(blocking=False):
                return
            try:
                baud = int(self._cat_baud_var.get())
                bits = int(self._cat_bits_var.get())
                par  = self._cat_parity_var.get()
                stop = float(self._cat_stopbits_var.get())
                with serial.Serial(port=port, baudrate=baud, bytesize=bits,
                                   parity=par, stopbits=stop, timeout=0.5) as s:
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
        threading.Thread(target=_do_read, daemon=True).start()
        self._cat_poll_after_id = self.root.after(600, self._cat_process_rx)

    def _cat_process_rx(self):
        """Verwerk ontvangen CAT data (eenmalig — geen herplanning)."""
        try:
            while True:
                raw = self._cat_rx_queue.get_nowait()
                self._cat_terminal_log(f"◀ {raw.strip()}", "rx")
                parts = [p.strip() for p in raw.split(";") if p.strip()]
                for p in parts:
                    if p.startswith("FA") and len(p) >= 13:
                        digits = "".join(c for c in p[2:] if c.isdigit())
                        if len(digits) >= 8:
                            self._cat_vfo_a_hz = int(digits[:11].zfill(11))
                    elif p.startswith("FB") and len(p) >= 13:
                        digits = "".join(c for c in p[2:] if c.isdigit())
                        if len(digits) >= 8:
                            self._cat_vfo_b_hz = int(digits[:11].zfill(11))
                if self._cat_vfo_a_hz:
                    txt = f"VFO-A:  {_fmt_freq_hz(self._cat_vfo_a_hz)}"
                    if self._cat_vfo_b_hz:
                        txt += f"    VFO-B:  {_fmt_freq_hz(self._cat_vfo_b_hz)}"
                    self._cat_freq_var.set(txt)
                if hasattr(self, "_last_band_pct") and self._last_band_pct:
                    self._draw_prop_bars(self._last_band_pct)
        except _queue.Empty:
            pass
        # Geen herplanning — eenmalige lezing

    def _open_cat_dialog(self):
        """Open het CAT-interface instellingendialoogvenster."""
        if _CAT_DISABLED:
            import tkinter.messagebox as mb
            mb.showinfo("CAT — tijdelijk uitgeschakeld",
                        "De CAT-interface is tijdelijk uitgeschakeld.\n"
                        "De functionaliteit wordt in een volgende versie afgerond.",
                        parent=self.root)
            return
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
                       bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
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

    def _switch_view(self, view_name):
        """Wissel tussen verschillende hoofdviews in de content area."""
        if view_name not in self._views:
            return
        # Verberg alle views
        for v in self._views.values():
            v.pack_forget()
        # Toon geselecteerde view
        self._views[view_name].pack(fill=tk.BOTH, expand=True)
        # Update navigatie-knoppen kleur
        for key, btn in self._nav_btns.items():
            if key == view_name:
                btn.configure(bg=BG_HOVER, fg=ACCENT)
            else:
                btn.configure(bg=BG_PANEL, fg=TEXT_BODY)

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.root, bg=BG_PANEL, height=42)
        hdr.pack(fill=tk.X)
        tk.Frame(hdr, bg=ACCENT, width=4).pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(hdr, text="📡  HAMIOS v3.0",
                 font=_font(13, "bold"), bg=BG_PANEL, fg=ACCENT,
                 pady=8).pack(side=tk.LEFT, padx=10)

        # Offline indicator — zichtbaar als netwerkfout
        self._offline_lbl = tk.Label(hdr, text="⚠ OFFLINE",
                                     font=_font(9, "bold"), bg=BG_PANEL,
                                     fg="#EF5350", pady=8)
        # Nog niet gepack — verschijnt alleen bij netfout via _update_net_indicator()

        # Exit knop (links, naast titel)
        exit_btn = tk.Button(hdr, text=self._tr("exit"),
                             command=self._quit_app,
                             font=_font(9), bg="#5A1010", fg=TEXT_H1,
                             activebackground="#8B1A1A", activeforeground=TEXT_H1,
                             relief=tk.FLAT, padx=8, pady=2, cursor="hand2")
        exit_btn.pack(side=tk.LEFT, padx=(0, 6))
        self._tr_widgets["exit"] = exit_btn

        # CAT Interface knop (naast Afsluiten) — grijs als tijdelijk uitgeschakeld
        self._cat_btn = tk.Button(hdr, text="CAT  ⚠",
                                  command=self._open_cat_dialog,
                                  font=_font(9), bg="#3A3A3A", fg="#777777",
                                  activebackground="#3A3A3A", activeforeground="#999999",
                                  relief=tk.FLAT, padx=8, pady=2,
                                  cursor="hand2" if not _CAT_DISABLED else "arrow")
        self._cat_btn.pack(side=tk.LEFT, padx=(0, 10))
        if not _CAT_DISABLED:
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

        # ── Thema selector ─────────────────────────────────────────────────────
        tk.Frame(hdr, bg=BORDER, width=1).pack(side=tk.RIGHT, fill=tk.Y, pady=8)
        theme_mb = tk.Menubutton(hdr, textvariable=self._theme_var,
                                 font=_font(9), bg=BG_SURFACE, fg=TEXT_H1,
                                 relief=tk.FLAT, activebackground=BG_HOVER,
                                 activeforeground=TEXT_H1, width=11,
                                 anchor='w', padx=6, pady=3, cursor="hand2")
        theme_menu = tk.Menu(theme_mb, tearoff=False, bg=BG_SURFACE, fg=TEXT_H1,
                             activebackground=ACCENT, activeforeground=BG_ROOT,
                             font=_font(9))
        for tname in THEMES.keys():
            theme_menu.add_command(label=tname,
                                   command=lambda v=tname: self._on_theme_change(v))
        theme_mb["menu"] = theme_menu
        theme_mb.pack(side=tk.RIGHT, padx=(0, 4))
        theme_lbl = tk.Label(hdr, text=self._tr("theme_lbl") if "theme_lbl" in _T else "Theme:",
                            font=_font(9), bg=BG_PANEL, fg=TEXT_DIM)
        theme_lbl.pack(side=tk.RIGHT, padx=(8, 2))
        self._tr_widgets["theme_lbl"] = theme_lbl
        cb_tips = tk.Checkbutton(hdr, text=self._tr("tooltips"), variable=self._show_tips_var,
                                 bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                                 activebackground=BG_PANEL, activeforeground=TEXT_H1,
                                 font=_font(9))
        cb_tips.pack(side=tk.RIGHT, padx=(0, 4))
        self._tr_widgets["tooltips"] = cb_tips
        cb_ticker = tk.Checkbutton(hdr, text=self._tr("ticker"),
                                   variable=self._ticker_enabled_var,
                                   command=self._toggle_ticker,
                                   bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                                   activebackground=BG_PANEL, activeforeground=TEXT_H1,
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

        # ── Hoofd body v3.0: Kaart centraal ──────────────────────────────────
        body = tk.Frame(self.root, bg=BG_ROOT)
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 4))

        # ── DX Spots kolom rechts (eerst pack → verdringt nooit) ──────────────
        dx_col = tk.Frame(body, bg=BG_PANEL, width=360)
        dx_col.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
        dx_col.pack_propagate(False)
        self._build_dx_panel(dx_col)

        # ── Linker gedeelte: grid-layout voor exacte kolomuitlijning ────────────
        # 4 gelijke kolommen; top (rij 0) expandeert, bottom (rij 1) + advies (rij 2) vast
        left_area = tk.Frame(body, bg=BG_ROOT)
        left_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for _c in range(4):
            left_area.columnconfigure(_c, weight=1, uniform="lc")
        left_area.rowconfigure(0, weight=1)   # top_row expandeert verticaal
        left_area.rowconfigure(1, weight=0)   # bottom_row vaste hoogte
        left_area.rowconfigure(2, weight=0)   # advies vaste hoogte

        # ── Top rij: HF Rel (col 0) | Kaart (col 1-2) | leeg (col 3) ────────
        prop_f = tk.Frame(left_area, bg=BG_PANEL)
        prop_f.grid(row=0, column=0, sticky='nsew', padx=(0, 4))
        self._build_prop_panel(prop_f)

        map_f = tk.Frame(left_area, bg=BG_PANEL)
        map_f.grid(row=0, column=1, columnspan=3, sticky='nsew', padx=(0, 4))
        self._build_map_panel(map_f)

        # ── Onderste rij: Schema | Bandverloop | Kp | Bz+Xray ────────────────
        sched_f = tk.Frame(left_area, bg=BG_ROOT)
        sched_f.grid(row=1, column=0, sticky='nsew', padx=(0, 4), pady=(8, 0))
        self._build_schedule_panel(sched_f)

        hist_f = tk.Frame(left_area, bg=BG_ROOT)
        hist_f.grid(row=1, column=1, sticky='nsew', padx=(0, 4), pady=(8, 0))
        self._build_hist_panel(hist_f)

        kp_f = tk.Frame(left_area, bg=BG_ROOT)
        kp_f.grid(row=1, column=2, sticky='nsew', padx=(0, 4), pady=(8, 0))
        self._build_kp_panel(kp_f)

        bz_f = tk.Frame(left_area, bg=BG_ROOT)
        bz_f.grid(row=1, column=3, sticky='nsew', pady=(8, 0))
        self._build_bz_xray_panel(bz_f)

        # ── Advies: volledige breedte ─────────────────────────────────────────
        adv_f = tk.Frame(left_area, bg=BG_ROOT)
        adv_f.grid(row=2, column=0, columnspan=4, sticky='nsew', pady=(8, 0))
        self._build_advice_panel(adv_f)

    # ── Solar / Ionosfeer sectie (herbruikbaar in DX-paneel) ─────────────────
    def _build_solar_section(self, parent):
        """Bouwt solar/ionosfeer info in parent (DX-paneel of elders)."""
        tk.Frame(parent, bg=ACCENT, height=2).pack(fill=tk.X)
        _solar_hdr_lbl = tk.Label(parent, text=self._tr("solar"),
                                  font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT,
                                  pady=6)
        _solar_hdr_lbl.pack(anchor='w', padx=10)
        self._tr_widgets["solar"] = _solar_hdr_lbl

        self._solar_frame = tk.Frame(parent, bg=BG_PANEL)
        self._solar_frame.pack(fill=tk.X, padx=10)

        def _get_solar_tips(lang: str) -> dict:
            return _SOLAR_TIPS_PACKS.get(lang, _SOLAR_TIPS)

        def _bind_tip(widget, key):
            tt = _Tooltip(widget)
            lang = _LANG_CODES.get(self._lang_var.get(), "en")
            tips_dict = _get_solar_tips(lang)
            title, body_txt = tips_dict.get(key, ("", ""))
            text = f"{title}\n{'─' * len(title)}\n{body_txt}" if title else ""
            widget.bind("<Enter>", lambda e, t=tt, tx=text:
                        t.show(e.widget.winfo_rootx() + e.x,
                               e.widget.winfo_rooty() + e.y, tx)
                        if tx and self._show_tips_var.get() else None)
            widget.bind("<Leave>", lambda *_, t=tt: t.hide())

        self._solar_vars     = {}
        self._solar_val_lbls = {}
        self._iono_station_var = tk.StringVar(value="foF2 ms/md:")
        for key, label in [
            ("sfi",        "Solar Flux (SFI)"),
            ("ssn",        "Sunspot Nr (SSN)"),
            ("a_index",    "A-index"),
            ("k_index",    "K-index"),
            ("xray",       "X-ray"),
            ("muf",        "MUF (MHz)"),
            ("luf",        "LUF (MHz)"),
            ("sw_speed",   "Solarwind (km/s)"),
            ("sw_bz",      "Bz (nT)"),
            ("sw_density", None),
            ("kp_planet",  None),
            ("iono_fof2",  None),
        ]:
            row = tk.Frame(self._solar_frame, bg=BG_PANEL)
            row.pack(fill=tk.X, pady=1)
            _TR_LABELS = {"sw_density": "sw_density_lbl", "kp_planet": "kp_planet_lbl"}
            if key == "iono_fof2":
                lbl = tk.Label(row, textvariable=self._iono_station_var,
                               font=_font(8), bg=BG_PANEL,
                               fg=TEXT_DIM, anchor='w', width=14, cursor="question_arrow")
            elif key in _TR_LABELS:
                lbl = tk.Label(row, text=self._tr(_TR_LABELS[key]) + ":",
                               font=_font(8), bg=BG_PANEL,
                               fg=TEXT_DIM, anchor='w', width=14, cursor="question_arrow")
                self._tr_widgets[_TR_LABELS[key]] = lbl
            else:
                lbl = tk.Label(row, text=label + ":", font=_font(8), bg=BG_PANEL,
                               fg=TEXT_DIM, anchor='w', width=14, cursor="question_arrow")
            lbl.pack(side=tk.LEFT)
            _bind_tip(lbl, key)
            var = tk.StringVar(value="—")
            self._solar_vars[key] = var
            val_lbl = tk.Label(row, textvariable=var, font=_font(8, "bold"),
                               bg=BG_PANEL, fg=TEXT_H1, anchor='w', width=7,
                               cursor="question_arrow")
            val_lbl.pack(side=tk.LEFT)
            _bind_tip(val_lbl, key)
            self._solar_val_lbls[key] = val_lbl

        tk.Frame(self._solar_frame, bg=ACCENT, height=1).pack(fill=tk.X, pady=(4, 2))

        # Bandentabel (dag/nacht condities)
        hdr_row = tk.Frame(self._solar_frame, bg=BG_PANEL)
        hdr_row.pack(fill=tk.X)
        for key, w in [("band_hdr", 5), ("day_hdr", 5), ("night_hdr", 5)]:
            lbl = tk.Label(hdr_row, text=self._tr(key), font=_font(8, "bold"),
                           bg=BG_PANEL, fg=ACCENT, width=w, anchor='w')
            lbl.pack(side=tk.LEFT)
            self._tr_widgets.setdefault(key, [])
            self._tr_widgets[key] = (self._tr_widgets[key]
                                     if isinstance(self._tr_widgets[key], list)
                                     else [self._tr_widgets[key]])
            self._tr_widgets[key].append(lbl)

        self._band_cond_labels: dict = {}
        for name, _, is_hf in _BANDS:
            if not is_hf:
                continue
            row = tk.Frame(self._solar_frame, bg=BG_PANEL)
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=name, font=_font(8), bg=BG_PANEL,
                     fg=TEXT_DIM, width=5, anchor='w').pack(side=tk.LEFT)
            day_lbl = tk.Label(row, text="—", font=_font(8, "bold"),
                               bg=BG_PANEL, fg=TEXT_DIM, width=5, anchor='w')
            day_lbl.pack(side=tk.LEFT)
            ngt_lbl = tk.Label(row, text="—", font=_font(8, "bold"),
                               bg=BG_PANEL, fg=TEXT_DIM, width=5, anchor='w')
            ngt_lbl.pack(side=tk.LEFT)
            self._band_cond_labels[name] = (day_lbl, ngt_lbl, is_hf)

        tk.Frame(self._solar_frame, bg=ACCENT, height=1).pack(fill=tk.X, pady=(4, 2))

        # 3-daagse storm-kans voorspelling
        _fc_hdr = tk.Label(self._solar_frame, text=self._tr("storm_forecast_hdr"),
                           font=_font(8, "bold"), bg=BG_PANEL, fg=ACCENT, anchor='w')
        _fc_hdr.pack(fill=tk.X, pady=(0, 1))
        self._tr_widgets["storm_forecast_hdr"] = _fc_hdr
        self._storm_fc_vars = []
        for _ in range(3):
            var = tk.StringVar(value="—")
            lbl = tk.Label(self._solar_frame, textvariable=var,
                           font=_font(7), bg=BG_PANEL, fg=TEXT_DIM, anchor='w')
            lbl.pack(fill=tk.X)
            self._storm_fc_vars.append(var)

    # ── Wereldkaart panel ─────────────────────────────────────────────────────
    def _build_map_panel(self, parent):
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.BOTH, expand=True, pady=(0, 0))
        tk.Frame(outer, bg=ACCENT, height=2).pack(fill=tk.X)

        map_hdr = tk.Frame(outer, bg=BG_PANEL)
        map_hdr.pack(fill=tk.X)
        map_title = tk.Label(map_hdr, text=self._tr("worldmap"),
                             font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT,
                             pady=4)
        map_title.pack(side=tk.LEFT, padx=10)
        self._tr_widgets["worldmap"] = map_title

        self._map_canvas = tk.Canvas(outer, height=380, bg="#1B3A5C",
                                     bd=0, highlightthickness=0)
        self._map_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(2, 2))
        self._map_photo = None
        self._map_canvas.bind("<Configure>",      self._on_map_resize)
        self._map_canvas.bind("<Button-1>",       self._on_map_btn1_press)
        self._map_canvas.bind("<B1-Motion>",      self._on_map_drag)
        self._map_canvas.bind("<ButtonRelease-1>", self._on_map_btn1_release)
        self._map_canvas.bind("<Button-3>",       self._on_map_clear)
        self._map_canvas.bind("<MouseWheel>",     self._on_map_scroll)   # Windows & Mac
        self._map_canvas.bind("<Button-4>",       self._on_map_scroll)   # Linux scroll up
        self._map_canvas.bind("<Button-5>",       self._on_map_scroll)   # Linux scroll down

        # Info-label voor groot-cirkel (richting/afstand)
        self._gc_info_var = tk.StringVar(value="")
        tk.Label(outer, textvariable=self._gc_info_var,
                 font=_font(9), bg=BG_PANEL, fg=ACCENT,
                 anchor='w').pack(fill=tk.X, padx=10, pady=(0, 1))
        # Band-kwaliteit voor het specifieke propagatiepad
        self._gc_path_var = tk.StringVar(value="")
        self._gc_path_best_color = _BAND_COLORS.get("20m", ACCENT)
        self._gc_path_lbl = tk.Label(outer, textvariable=self._gc_path_var,
                                     font=_font(9), bg=BG_PANEL, fg=TEXT_BODY,
                                     anchor='w')
        self._gc_path_lbl.pack(fill=tk.X, padx=10, pady=(0, 4))

    def _on_map_resize(self, _event=None):
        """Kaart herrenderen bij breedte-aanpassing; hoogte is vast (v3.0)."""
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

    def _calc_path_propagation(self, dest_lat: float, dest_lon: float):
        """Band-kwaliteit voor het pad QTH → bestemming op basis van midpunt-ionosfeer."""
        # Midpunt van het groot-cirkelpad (helft van de weg)
        mid_pts = _great_circle_pts(self._qth_lat, self._qth_lon,
                                    dest_lat, dest_lon, n=2)
        mid_lat = mid_pts[1][0] if len(mid_pts) > 1 else (self._qth_lat + dest_lat) / 2
        mid_lon = mid_pts[1][1] if len(mid_pts) > 1 else (self._qth_lon + dest_lon) / 2

        # Dag/nacht op het midpunt
        sun_lat, sun_lon = _subsolar_point()
        sl = math.radians(sun_lat);  ml = math.radians(mid_lat)
        dln = math.radians(mid_lon - sun_lon)
        daytime = (math.sin(sl) * math.sin(ml) +
                   math.cos(sl) * math.cos(ml) * math.cos(dln)) > 0

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
        band_pct, muf, luf = _calc_propagation(
            sfi, ssn, k_index,
            qth_lat=mid_lat,
            snr_bonus_db=snr_db,
            daytime=daytime)
        return band_pct, muf, luf, daytime

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

        # ── Propagatiepad: band-kwaliteit op dit specifieke traject ───────────
        band_pct, muf, luf, daytime = self._calc_path_propagation(lat, lon)
        hops = max(1, round(dist / 3500))
        hop_s = self._tr("path_hops") + ("s" if hops > 1 else "")
        dn = self._tr("path_day") if daytime else self._tr("path_night")
        open_bands = sorted(
            [(n, p, _BAND_COLORS.get(n, ACCENT)) for n, _, p in band_pct
             if 0 < p and p != -1],
            key=lambda x: -x[1])
        if open_bands:
            self._gc_path_best_color = open_bands[0][2]
            self._gc_path_lbl.config(fg=open_bands[0][2])
            parts = "  ·  ".join(
                f"{n} {p}%" for n, p, _ in open_bands[:5])
            self._gc_path_var.set(
                f"  ↳  {dist:,.0f} km / {hops} {hop_s} / {dn}  ▸  {parts}"
                f"  (MUF {muf} MHz)")
        else:
            self._gc_path_best_color = TEXT_DIM
            self._gc_path_lbl.config(fg=TEXT_DIM)
            self._gc_path_var.set(
                f"  ↳  {dist:,.0f} km / {hops} {hop_s} / {dn}  ▸  {self._tr('path_closed')}")

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
            self._gc_path_var.set("")
            self._draw_map()

    def _draw_map(self):
        c = self._map_canvas
        W = c.winfo_width()  or 960
        H = c.winfo_height() or 400
        # Virtuele wereld-afmetingen: altijd 2:1 ongeacht canvas-hoogte
        zoom = max(1.0, self._map_zoom)
        VW   = max(2, int(W * zoom))
        VH   = max(1, int(W // 2 * zoom))

        if not _PIL_OK:
            c.delete("all")
            c.create_rectangle(0, 0, W, H, fill="#1B3A5C", outline="")
            c.create_text(W // 2, H // 2,
                          text=self._tr("map_nolib"),
                          fill=TEXT_DIM, font=(_FONT_SANS, 9))
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
            # crop_t_est: hoeveel pixels van de bovenkant worden weggesneden
            # zodat labels altijd zichtbaar zijn in het canvas-venster
            crop_t_est = max(0, (VH - H) // 2)
            d   = ImageDraw.Draw(src)
            LBL = (180, 200, 220)   # contrasterende lichtblauwe kleur
            for lat in range(-60, 90, 30):
                gy = int((90 - lat) / 180 * VH)
                d.line([(0, gy), (VW, gy)], fill=MAP_GRID, width=1)
                # label net onder de lijn, maar nooit boven de crop-rand
                text_y = max(gy + 2, crop_t_est + 4)
                d.text((3, text_y), f"{lat:+d}°", fill=LBL)
            for lon in range(-150, 180, 30):
                gx = int((lon + 180) / 360 * VW)
                d.line([(gx, 0), (gx, VH)], fill=MAP_GRID, width=1)
                # altijd binnen het zichtbare gebied (crop_t_est + 4px marge)
                d.text((gx + 2, crop_t_est + 4), f"{lon:+d}°", fill=LBL)

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
            bool(self._show_aurora_var.get()),
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
            if not _ITU_DISABLED and self._show_iaru_var.get():
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

                # R2 Amerika: Lijn-C (170°W/120°W) → Lijn-B (20°W) → Z-pool
                id_.polygon(_px([
                    (90,-170),(90,-20),(0,-20),
                    (-90,-20),(-90,-120),(60,-120),(60,-170)
                ]), fill=C_R2)

                # R1 hoofd: Europa + Afrika + Arabisch schiereiland + Turkije/Irak
                # Begrensd: west=20°W, oost=Lijn-A (40°E → 59°E)
                id_.polygon(_px([
                    (90,-20),(0,-20),(-90,-20),(-90,59),
                    (11,59),(22,59),(26,56),(29,48),(33,46),
                    (36,44),(37,42),(39,40),(41,40),
                    (55,40),(90,40)
                ]), fill=C_R1)

                # R3 oost (Azië-Pacific): Lijn-A zuidelijk → 180°E
                id_.polygon(_px([
                    (90,40),(55,40),(41,40),(39,40),(37,42),(36,44),
                    (33,46),(29,48),(26,56),(22,59),(11,59),
                    (-90,59),(-90,180),(90,180)
                ]), fill=C_R3)

                # R1 Rusland-patch: Rusland + Kazachstaan + Mongolië zijn R1
                # Overtekent R3-oost voor het Euraziatisch continent
                id_.polygon(_px([
                    (90, 40),(55, 40),
                    (51, 52),(51, 62),(51, 83),(49, 87),
                    (46, 94),(46,106),(42,119),
                    (49,122),(48,130),(43,131),
                    (45,136),(50,141),(55,141),
                    (59,151),(63,163),(67,178),
                    (90,180),
                ]), fill=C_R1)

                # ── Grenslijnen — alle lijnen dikke donkergroen (conform referentie) ─
                _GRN = (60, 160, 60, AL)
                for pts, clr, w in [
                    (_ITU_B,     _GRN, 2),   # R1/R2 Atlantisch
                    (_ITU_A,     _GRN, 2),   # R1/R3 Midden-Oosten
                    (_ITU_A_RUS, _GRN, 2),   # R1/R3 Rusland-arm
                    (_ITU_C,     _GRN, 2),   # R2/R3 Pacific
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

            # ── Aurora-ring overlay (Feldstein/Holzworth geomagnetisch ovaal) ──
            if self._show_aurora_var.get():
                import math as _math
                aurora_img = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
                ad = ImageDraw.Draw(aurora_img)

                # Kleur op basis van K-index
                if k_val < 3:
                    ar, ag, ab = 60, 200, 60      # groen  — rustig
                elif k_val < 6:
                    ar, ag, ab = 255, 200, 0      # geel   — matig
                else:
                    ar, ag, ab = 220, 60, 20      # rood   — storm
                alpha  = min(210, int(110 + k_val * 11))
                line_w = max(3, int(3 + k_val * 0.8))

                # Meerdere lagen voor fade-effect (breed+transparant → smal+opaque)
                _PASSES = [
                    (6, 0.06), (5, 0.12), (4, 0.22), (3, 0.40), (2, 0.65), (1, 1.0),
                ]

                # Geomagnetische dipool-polen (IGRF-2025 benadering)
                _POLES = [(80.65, -72.65), (-80.65, 107.35)]

                # Colatitude van het ovaal (K=0 → ~23°, K=9 → ~45.5°)
                theta_deg = 23.0 + k_val * 2.5

                def _geomag_to_geo(phi_p, lam_p, theta, psi):
                    geo_lat = _math.asin(
                        _math.sin(phi_p) * _math.cos(theta)
                        + _math.cos(phi_p) * _math.sin(theta) * _math.cos(psi)
                    )
                    geo_lon = lam_p + _math.atan2(
                        _math.sin(theta) * _math.sin(psi),
                        _math.cos(phi_p) * _math.cos(theta)
                        - _math.sin(phi_p) * _math.sin(theta) * _math.cos(psi)
                    )
                    lat_d = _math.degrees(geo_lat)
                    lon_d = _math.degrees(geo_lon)
                    while lon_d > 180:  lon_d -= 360
                    while lon_d < -180: lon_d += 360
                    return lat_d, lon_d

                N = 360
                # Bereken segmenten eenmalig per pool
                all_segs = []
                for pole_lat, pole_lon in _POLES:
                    phi_p = _math.radians(pole_lat)
                    lam_p = _math.radians(pole_lon)
                    theta = _math.radians(theta_deg)
                    pts = []
                    for i in range(N + 1):
                        psi = 2 * _math.pi * i / N
                        lat_d, lon_d = _geomag_to_geo(phi_p, lam_p, theta, psi)
                        pts.append(_ll_to_xy(lat_d, lon_d, VW, VH))
                    # Splits op anti-meridiaan
                    seg = [pts[0]]
                    for i in range(1, len(pts)):
                        if abs(pts[i][0] - pts[i - 1][0]) > VW // 2:
                            if len(seg) > 1:
                                all_segs.append(seg)
                            seg = [pts[i]]
                        else:
                            seg.append(pts[i])
                    if len(seg) > 1:
                        all_segs.append(seg)

                # Teken breed→smal met afnemende transparantie (grayline-stijl fade)
                for w_mult, a_frac in _PASSES:
                    pw = max(1, line_w * w_mult)
                    pa = max(1, int(alpha * a_frac))
                    for seg in all_segs:
                        ad.line(seg, fill=(ar, ag, ab, pa), width=pw)

                img = Image.alpha_composite(img.convert("RGBA"), aurora_img).convert("RGB")
                draw = ImageDraw.Draw(img)

            # ── Groot-cirkel pad (kleur = beste band voor dit traject) ──────────
            if self._gc_dest:
                dlat, dlon = self._gc_dest
                pts = _great_circle_pts(self._qth_lat, self._qth_lon, dlat, dlon)
                gc_img = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
                gd     = ImageDraw.Draw(gc_img)
                xy     = [_ll_to_xy(la, lo, VW, VH) for la, lo in pts]
                # Lijnkleur van beste band (hex → RGB)
                clr_hex = getattr(self, "_gc_path_best_color", "#FFDC32")
                try:
                    cr = int(clr_hex[1:3], 16)
                    cg = int(clr_hex[3:5], 16)
                    cb = int(clr_hex[5:7], 16)
                except Exception:
                    cr, cg, cb = 255, 220, 50
                # Splits op anti-meridian (|Δx| > VW/2) om wraparound te vermijden
                seg_start = 0
                for i in range(1, len(xy)):
                    if abs(xy[i][0] - xy[i-1][0]) > VW // 2:
                        if i - seg_start > 1:
                            gd.line(xy[seg_start:i], fill=(cr, cg, cb, 220), width=2)
                        seg_start = i
                if len(xy) - seg_start > 1:
                    gd.line(xy[seg_start:], fill=(cr, cg, cb, 220), width=2)
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
    def _build_bz_panel(self, parent):
        """Bz 24-uurs grafiek als zelfstandig paneel."""
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.BOTH, expand=True)
        tk.Frame(outer, bg=ACCENT, height=2).pack(fill=tk.X)
        _bz_hdr = tk.Label(outer, text=self._tr("bz_chart_hdr"),
                           font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT, pady=4)
        _bz_hdr.pack(anchor='w', padx=10)
        self._tr_widgets["bz_chart_hdr"] = _bz_hdr
        self._bz_canvas = tk.Canvas(outer, height=120, bg=BG_SURFACE,
                                    bd=0, highlightthickness=0)
        self._bz_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 6))
        self._bz_canvas.bind("<Configure>",
                             lambda *_: self._draw_bz_graph(
                                 getattr(self, "_last_bz_pts", [])))

        # Tooltip: toon Bz-waarde bij muisbeweging
        self._bz_tooltip_id = None
        self._bz_tooltip_win: tk.Toplevel | None = None

        def _bz_on_motion(event):
            pts = getattr(self, "_last_bz_pts", [])
            if not pts:
                return
            c = self._bz_canvas
            W = c.winfo_width() or 200
            H = c.winfo_height() or 120
            PAD_L, PAD_R = 30, 4
            gW = W - PAD_L - PAD_R
            mx = event.x
            # Interpoleer tijdstip op basis van x-positie
            if gW <= 0:
                return
            frac = (mx - PAD_L) / gW         # 0=24h geleden, 1=nu
            hours_ago = 24 * (1.0 - max(0, min(1, frac)))
            # Zoek het dichtstbijzijnde punt
            closest = min(pts, key=lambda p: abs(p[0] - hours_ago))
            bz_val  = closest[1]
            age_h   = int(closest[0])
            age_min = int((closest[0] - age_h) * 60)
            label   = f"Bz: {bz_val:+.1f} nT  ({age_h}h {age_min:02d}m ago)"

            # Verwijder oud tooltip
            if self._bz_tooltip_win:
                try:
                    self._bz_tooltip_win.destroy()
                except Exception:
                    pass
            tw = tk.Toplevel(c)
            tw.wm_overrideredirect(True)
            if _IS_MAC:
                tw.wm_attributes("-topmost", True)
            tw.configure(bg=BORDER)
            tk.Label(tw, text=label, font=_font(8), bg=BG_SURFACE,
                     fg=TEXT_H1, padx=8, pady=4).pack(padx=1, pady=1)
            rx = c.winfo_rootx() + event.x + 12
            ry = c.winfo_rooty() + event.y - 28
            tw.wm_geometry(f"+{rx}+{ry}")
            self._bz_tooltip_win = tw
            # Verticale cursor-lijn op canvas
            c.delete("bz_cursor")
            c.create_line(mx, 0, mx, H, fill=BORDER, dash=(3, 3),
                          tags="bz_cursor")

        def _bz_on_leave(event):
            if self._bz_tooltip_win:
                try:
                    self._bz_tooltip_win.destroy()
                except Exception:
                    pass
                self._bz_tooltip_win = None
            self._bz_canvas.delete("bz_cursor")

        self._bz_canvas.bind("<Motion>", _bz_on_motion)
        self._bz_canvas.bind("<Leave>",  _bz_on_leave)

    def _build_kp_panel(self, parent):
        """Planetaire Kp-index 48-uurs staafdiagram."""
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.BOTH, expand=True)
        tk.Frame(outer, bg=ACCENT, height=2).pack(fill=tk.X)
        _kp_hdr = tk.Label(outer, text=self._tr("kp_chart_hdr"),
                           font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT, pady=4)
        _kp_hdr.pack(anchor='w', padx=10)
        self._tr_widgets["kp_chart_hdr"] = _kp_hdr
        self._kp_canvas = tk.Canvas(outer, height=90, bg=BG_SURFACE,
                                    bd=0, highlightthickness=0)
        self._kp_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 6))
        self._kp_canvas.bind("<Configure>",
                             lambda *_: self._draw_kp_bars(
                                 getattr(self, "_last_kp_pts", [])))

    def _build_bz_xray_panel(self, parent):
        """Gecombineerd paneel: Bz 24u (boven) + X-ray 24u (onder)."""
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.BOTH, expand=True)
        tk.Frame(outer, bg=ACCENT, height=2).pack(fill=tk.X)

        # Bz sectie
        _bz_hdr = tk.Label(outer, text=self._tr("bz_chart_hdr"),
                           font=_font(9, "bold"), bg=BG_PANEL, fg=ACCENT, pady=2)
        _bz_hdr.pack(anchor='w', padx=10)
        self._tr_widgets["bz_chart_hdr"] = _bz_hdr
        self._bz_canvas = tk.Canvas(outer, height=80, bg=BG_SURFACE,
                                    bd=0, highlightthickness=0)
        self._bz_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 4))
        self._bz_canvas.bind("<Configure>",
                             lambda *_: self._draw_bz_graph(
                                 getattr(self, "_last_bz_pts", [])))

        tk.Frame(outer, bg=BORDER, height=1).pack(fill=tk.X, padx=10)

        # X-ray sectie
        _xr_hdr = tk.Label(outer, text=self._tr("xray_chart_hdr"),
                           font=_font(9, "bold"), bg=BG_PANEL, fg=ACCENT, pady=2)
        _xr_hdr.pack(anchor='w', padx=10)
        self._tr_widgets["xray_chart_hdr"] = _xr_hdr
        self._xray_canvas = tk.Canvas(outer, height=80, bg=BG_SURFACE,
                                      bd=0, highlightthickness=0)
        self._xray_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 6))
        self._xray_canvas.bind("<Configure>",
                               lambda *_: self._draw_xray_graph(
                                   getattr(self, "_last_xray_pts", [])))

    def _draw_kp_bars(self, pts: list):
        """Teken planetaire Kp-index als staafdiagram (3u blokken, 48u)."""
        self._last_kp_pts = pts
        if not hasattr(self, "_kp_canvas"):
            return
        c = self._kp_canvas
        c.update_idletasks()
        W = c.winfo_width()  or 200
        H = c.winfo_height() or 100
        c.delete("all")
        c.create_rectangle(0, 0, W, H, fill=BG_SURFACE, outline="")

        if not pts:
            c.create_text(W // 2, H // 2, text="—", fill=TEXT_DIM,
                          font=("Consolas", 9))
            return

        PAD_L, PAD_R, PAD_T, PAD_B = 20, 4, 4, 14
        gW = W - PAD_L - PAD_R
        gH = H - PAD_T - PAD_B
        KP_MAX = 9.0

        # Y-as: 0, 3, 5, 7, 9
        for kp_ref, lbl in [(0, "0"), (3, "3"), (5, "5"), (7, "7"), (9, "9")]:
            yr = PAD_T + int(gH * (1.0 - kp_ref / KP_MAX))
            c.create_line(PAD_L, yr, W - PAD_R, yr, fill=BORDER, dash=(2, 4))
            c.create_text(PAD_L - 2, yr, text=lbl, fill=TEXT_DIM,
                          font=("Consolas", 7), anchor='e')

        # Storm-drempel lijn (Kp ≥ 5)
        y5 = PAD_T + int(gH * (1.0 - 5.0 / KP_MAX))
        c.create_line(PAD_L, y5, W - PAD_R, y5, fill="#FFA726", dash=(4, 2), width=1)

        # Staafbreedte op basis van tijdsduur (~3u blokken over 48u)
        n = len(pts)
        bar_w = max(2, gW // max(n, 1))

        for i, (hours_ago, kp) in enumerate(pts):
            # Positie: meest recente rechts
            x_right = PAD_L + int(gW * (1.0 - hours_ago / 48))
            x_left  = x_right - bar_w + 1
            if x_left < PAD_L:
                x_left = PAD_L
            bar_h = int(gH * min(kp, KP_MAX) / KP_MAX)
            y_top = PAD_T + gH - bar_h

            if kp >= 7:
                color = "#EF5350"
            elif kp >= 5:
                color = "#FFA726"
            elif kp >= 3:
                color = "#FFF176"
            else:
                color = "#4FC3F7"

            if bar_h > 0:
                c.create_rectangle(x_left, y_top, x_right, PAD_T + gH,
                                   fill=color, outline="")

        # Tijdlabels
        c.create_text(PAD_L, H - PAD_B + 2, text="48h",
                      fill=TEXT_DIM, font=("Consolas", 7), anchor='nw')
        c.create_text(W - PAD_R, H - PAD_B + 2, text="nu",
                      fill=TEXT_DIM, font=("Consolas", 7), anchor='ne')
        # Huidige Kp-waarde
        if pts:
            last_kp = pts[-1][1]
            clr = "#EF5350" if last_kp >= 7 else ("#FFA726" if last_kp >= 5 else
                  ("#FFF176" if last_kp >= 3 else "#4FC3F7"))
            c.create_text(W - PAD_R - 2, PAD_T,
                          text=f"{last_kp:.1f}", fill=clr,
                          font=("Consolas", 7, "bold"), anchor='ne')

    def _draw_xray_graph(self, pts: list):
        """Teken GOES X-ray flux 24u op log-schaal (0.1-0.8 nm kanaal)."""
        self._last_xray_pts = pts
        if not hasattr(self, "_xray_canvas"):
            return
        c = self._xray_canvas
        c.update_idletasks()
        W = c.winfo_width()  or 200
        H = c.winfo_height() or 100
        c.delete("all")
        c.create_rectangle(0, 0, W, H, fill=BG_SURFACE, outline="")

        if not pts:
            c.create_text(W // 2, H // 2, text="—", fill=TEXT_DIM,
                          font=("Consolas", 9))
            return

        import math as _math
        PAD_L, PAD_R, PAD_T, PAD_B = 20, 4, 4, 12
        gW = W - PAD_L - PAD_R
        gH = H - PAD_T - PAD_B

        # Log-schaal: A=10⁻⁸, B=10⁻⁷, C=10⁻⁶, M=10⁻⁵, X=10⁻⁴
        LOG_MIN = -8.5   # net onder A-klasse
        LOG_MAX = -3.5   # net boven X10

        _CLASS_BOUNDS = [("A", -8, TEXT_DIM), ("B", -7, "#4FC3F7"),
                         ("C", -6, "#66BB6A"), ("M", -5, "#FFA726"),
                         ("X", -4, "#EF5350")]
        for cls, log_v, col in _CLASS_BOUNDS:
            yr = PAD_T + int(gH * (1.0 - (log_v - LOG_MIN) / (LOG_MAX - LOG_MIN)))
            if PAD_T <= yr <= PAD_T + gH:
                c.create_line(PAD_L, yr, W - PAD_R, yr, fill=BORDER, dash=(2, 4))
                c.create_text(PAD_L - 2, yr, text=cls, fill=col,
                              font=("Consolas", 7), anchor='e')

        def flux_to_y(f):
            if f <= 0:
                return PAD_T + gH
            log_f = _math.log10(f)
            log_f = max(LOG_MIN, min(LOG_MAX, log_f))
            return PAD_T + int(gH * (1.0 - (log_f - LOG_MIN) / (LOG_MAX - LOG_MIN)))

        def t_to_x(hours_ago):
            return PAD_L + int(gW * (1.0 - min(hours_ago, 24) / 24))

        # Lijn tekenen
        prev = None
        for hours_ago, flux in pts:
            x = t_to_x(hours_ago)
            y = flux_to_y(flux)
            log_f = _math.log10(flux) if flux > 0 else LOG_MIN
            if log_f >= -5:
                color = "#EF5350"   # M/X klasse
            elif log_f >= -6:
                color = "#FFA726"   # C klasse
            else:
                color = "#66BB6A"   # A/B klasse
            if prev and abs(x - prev[0]) < 20:
                c.create_line(prev[0], prev[1], x, y, fill=color, width=1)
            prev = (x, y)

        # Huidige waarde en klasse
        if pts:
            last_flux = pts[-1][1]
            if last_flux >= 1e-4:
                cls_str, cls_col = f"X{last_flux/1e-4:.1f}", "#EF5350"
            elif last_flux >= 1e-5:
                cls_str, cls_col = f"M{last_flux/1e-5:.1f}", "#FFA726"
            elif last_flux >= 1e-6:
                cls_str, cls_col = f"C{last_flux/1e-6:.1f}", "#FFF176"
            elif last_flux >= 1e-7:
                cls_str, cls_col = f"B{last_flux/1e-7:.1f}", "#4FC3F7"
            else:
                cls_str, cls_col = f"A{last_flux/1e-8:.1f}", TEXT_DIM
            c.create_text(W - PAD_R - 2, PAD_T,
                          text=cls_str, fill=cls_col,
                          font=("Consolas", 7, "bold"), anchor='ne')

        c.create_text(PAD_L, H - PAD_B + 2, text="24h",
                      fill=TEXT_DIM, font=("Consolas", 7), anchor='nw')
        c.create_text(W - PAD_R, H - PAD_B + 2, text=self._tr("bz_now_lbl"),
                      fill=TEXT_DIM, font=("Consolas", 7), anchor='ne')

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

        def _menubutton(par, var, options, tr_key, width=12, tr_option_keys=None, display_var=None):
            lbl = tk.Label(par, text=self._tr(tr_key), font=_font(9), bg=BG_PANEL,
                           fg=TEXT_DIM)
            lbl.pack(side=tk.LEFT, padx=(0, 2))
            self._tr_widgets[tr_key] = lbl
            dvar = display_var if display_var is not None else var
            mb2 = tk.Menubutton(par, textvariable=dvar, font=_font(9),
                                bg=BG_SURFACE, fg=TEXT_H1, relief=tk.FLAT,
                                activebackground=BG_HOVER, activeforeground=TEXT_H1,
                                width=width, anchor='w', padx=6, pady=3, cursor="hand2")
            menu2 = tk.Menu(mb2, tearoff=False, bg=BG_SURFACE, fg=TEXT_H1,
                            activebackground=ACCENT, activeforeground=BG_ROOT,
                            font=_font(9))
            for opt in options:
                disp = self._tr(tr_option_keys[opt]) if tr_option_keys and opt in tr_option_keys else opt
                def _on_select(v=opt):
                    var.set(v)
                    if display_var is not None and tr_option_keys and v in tr_option_keys:
                        display_var.set(self._tr(tr_option_keys[v]))
                    self._recalc_prop()
                menu2.add_command(label=disp, command=_on_select)
            mb2["menu"] = menu2
            mb2.pack(side=tk.LEFT, padx=(0, 12))
            return menu2

        _menubutton(ctrl, self._mode_var,  list(_MODE_DB.keys()),  "mode_lbl",  width=5)
        _menubutton(ctrl, self._power_var, list(_POWER_DB.keys()), "power_lbl", width=5)
        self._ant_menu = _menubutton(ctrl, self._ant_var, list(_ANT_DB.keys()), "ant_lbl",
                                     width=18, tr_option_keys=_ANT_TR_KEYS,
                                     display_var=self._ant_display_var)

        _day_auto_cb = tk.Checkbutton(ctrl, text=self._tr("day_auto"),
                                      variable=self._day_var,
                                      command=self._recalc_prop,
                                      bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                                      activebackground=BG_PANEL, activeforeground=TEXT_H1,
                                      font=_font(9))
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

        BAR_H    = 22
        BAR_PAD  = 4
        HDR_H    = 16
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

        # VFO-A/B frequentie (alleen zichtbaar als CAT ingeschakeld — verborgen zolang CAT uitgeschakeld)
        self._cat_info_frame = tk.Frame(outer, bg=BG_PANEL)
        self._cat_freq_lbl = tk.Label(self._cat_info_frame, textvariable=self._cat_freq_var,
                                      font=_font(10, "bold"), bg=BG_PANEL,
                                      fg=ACCENT, anchor="w")
        self._cat_freq_lbl.pack(fill=tk.X, padx=12, pady=(0, 2))

        self._update_cat_freq_lbl_visibility()

        # ── Kaartoverlays + meldingen onder HF Betrouwbaarheid ───────────────
        tk.Frame(outer, bg=ACCENT, height=2).pack(fill=tk.X, padx=10, pady=(6, 0))
        ov_frame = tk.Frame(outer, bg=BG_PANEL)
        ov_frame.pack(fill=tk.X, padx=10, pady=(4, 6))

        def _cb_ov(parent_row, tr_key, var, fallback_text=""):
            def _on_toggle():
                self._save_cur_settings()
                self._draw_map()
            cb = tk.Checkbutton(parent_row,
                                text=self._tr(tr_key) if tr_key else fallback_text,
                                variable=var, command=_on_toggle,
                                bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                                activebackground=BG_PANEL, activeforeground=TEXT_H1,
                                font=_font(9))
            cb.pack(side=tk.LEFT, padx=(0, 4))
            if tr_key:
                self._tr_widgets.setdefault(tr_key, [])
                if isinstance(self._tr_widgets[tr_key], list):
                    self._tr_widgets[tr_key].append(cb)
                else:
                    self._tr_widgets[tr_key] = [self._tr_widgets[tr_key], cb]

        # Weergave
        r1 = tk.Frame(ov_frame, bg=BG_PANEL)
        r1.pack(fill=tk.X, pady=(0, 2))
        tk.Label(r1, text=self._tr("map_display_lbl"),
                 font=_font(8), bg=BG_PANEL, fg=TEXT_DIM).pack(side=tk.LEFT, padx=(0, 4))
        _cb_ov(r1, "sun",      self._show_sun_var)
        _cb_ov(r1, "moon",     self._show_moon_var)
        _cb_ov(r1, "graylijn", self._show_graylijn_var)
        _cb_ov(r1, None,       self._show_aurora_var, "Aurora")

        # Data
        r2 = tk.Frame(ov_frame, bg=BG_PANEL)
        r2.pack(fill=tk.X, pady=(0, 2))
        tk.Label(r2, text=self._tr("map_data_lbl"),
                 font=_font(8), bg=BG_PANEL, fg=TEXT_DIM).pack(side=tk.LEFT, padx=(0, 4))
        _cb_ov(r2, None,      self._show_wspr_var,  "WSPR")
        _cb_ov(r2, None,      self._show_spots_var, "Spots")
        _cb_ov(r2, None,      self._show_cs_var,    "CS")
        _cb_ov(r2, "locator", self._show_locator_var)
        if not _ITU_DISABLED:
            _cb_ov(r2, None, self._show_iaru_var, "ITU")

        # Meldingen
        r3 = tk.Frame(ov_frame, bg=BG_PANEL)
        r3.pack(fill=tk.X)
        _alert_lbl = tk.Label(r3, text=self._tr("alerts_hdr") + ":",
                              font=_font(8), bg=BG_PANEL, fg=TEXT_DIM)
        _alert_lbl.pack(side=tk.LEFT, padx=(0, 4))
        self._tr_widgets.setdefault("alerts_hdr", [])
        if not isinstance(self._tr_widgets["alerts_hdr"], list):
            self._tr_widgets["alerts_hdr"] = [self._tr_widgets["alerts_hdr"]]
        self._tr_widgets["alerts_hdr"].append(_alert_lbl)

        _k_cb = tk.Checkbutton(r3, variable=self._alert_k_en_var,
                               command=self._save_cur_settings,
                               bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                               activebackground=BG_PANEL, activeforeground=TEXT_H1,
                               font=_font(9), text=self._tr("k_alert_lbl"))
        _k_cb.pack(side=tk.LEFT, padx=(0, 2))
        self._tr_widgets.setdefault("k_alert_lbl", [])
        if not isinstance(self._tr_widgets["k_alert_lbl"], list):
            self._tr_widgets["k_alert_lbl"] = [self._tr_widgets["k_alert_lbl"]]
        self._tr_widgets["k_alert_lbl"].append(_k_cb)

        tk.Spinbox(r3, from_=1, to=9, width=2, textvariable=self._k_alert_var,
                   command=self._save_cur_settings,
                   bg=BG_SURFACE, fg=TEXT_H1, buttonbackground=BG_SURFACE,
                   relief=tk.FLAT, font=_font(9, "bold")).pack(side=tk.LEFT, padx=(0, 8))

        _b_cb = tk.Checkbutton(r3, variable=self._alert_band_en_var,
                               command=self._save_cur_settings,
                               bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                               activebackground=BG_PANEL, activeforeground=TEXT_H1,
                               font=_font(9), text=self._tr("band_alert_lbl"))
        _b_cb.pack(side=tk.LEFT, padx=(0, 2))
        self._tr_widgets.setdefault("band_alert_lbl", [])
        if not isinstance(self._tr_widgets["band_alert_lbl"], list):
            self._tr_widgets["band_alert_lbl"] = [self._tr_widgets["band_alert_lbl"]]
        self._tr_widgets["band_alert_lbl"].append(_b_cb)

        tk.Spinbox(r3, from_=10, to=90, increment=5, width=3,
                   textvariable=self._band_alert_var, command=self._save_cur_settings,
                   bg=BG_SURFACE, fg=TEXT_H1, buttonbackground=BG_SURFACE,
                   relief=tk.FLAT, font=_font(9, "bold")).pack(side=tk.LEFT, padx=(0, 2))
        tk.Label(r3, text="%", font=_font(9), bg=BG_PANEL,
                 fg=TEXT_DIM).pack(side=tk.LEFT)


    def _draw_prop_bars(self, band_pct):
        self._last_band_pct = band_pct
        c = self._prop_canvas
        c.delete("all")
        self._bar_rows = []
        self._bar_band_rows = []

        W       = c.winfo_width() or 700
        BAR_H   = 22
        BAR_PAD = 4
        HDR_H   = 16
        LABEL_W = 46
        PCT_W   = 40
        FREQ_W  = 58
        MODES_W = 80
        FT8_W   = 54
        WSPR_W  = 34   # kolom voor WSPR spot-teller
        BAR_X   = LABEL_W + 4
        BAR_MAX = max(40, W - BAR_X - PCT_W - FREQ_W - MODES_W - FT8_W - WSPR_W - 10)
        wspr_counts = getattr(self, "_wspr_band_counts", {})

        def _gradient_fill(x1, y1, x2, y2, color):
            """Gradiëntbalk: heldere bandkleur boven → 50% donkerder onder."""
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            h = max(1, y2 - y1)
            slices = min(h, 6)
            for i in range(slices):
                factor = 1.0 - (i / slices) * 0.50
                cr = min(255, int(r * factor))
                cg = min(255, int(g * factor))
                cb = min(255, int(b * factor))
                sy1 = y1 + i * h // slices
                sy2 = y1 + (i + 1) * h // slices if i < slices - 1 else y2
                c.create_rectangle(x1, sy1, x2, sy2,
                                   fill=f"#{cr:02x}{cg:02x}{cb:02x}", outline="")

        # Kolomhoofden
        def _hdr(x, w, txt):
            c.create_text(x + w // 2, HDR_H // 2, text=txt,
                          font=(_FONT_SANS, 8, "bold"), fill=ACCENT, anchor='center')

        _hdr(BAR_X,                                       BAR_MAX, "")
        _hdr(BAR_X + BAR_MAX,                             PCT_W,   "%")
        _hdr(BAR_X + BAR_MAX + PCT_W,                     FREQ_W,  self._tr("hf_col_start"))
        _hdr(BAR_X + BAR_MAX + PCT_W + FREQ_W,            MODES_W, self._tr("hf_col_mode"))
        _hdr(BAR_X + BAR_MAX + PCT_W + FREQ_W + MODES_W,               FT8_W,  "FT8")
        _hdr(BAR_X + BAR_MAX + PCT_W + FREQ_W + MODES_W + FT8_W,     WSPR_W, "W")

        hf_pct = [(n, f, p) for n, f, p in band_pct if p != -1]
        for i, entry in enumerate(hf_pct):
            name, freq, pct = entry[0], entry[1], entry[2]
            y = HDR_H + BAR_PAD + i * (BAR_H + BAR_PAD)
            band_color = _BAND_COLORS.get(name, TEXT_DIM)

            # Bandnaam — band-specifieke kleur, vet
            c.create_text(LABEL_W - 2, y + BAR_H // 2,
                          text=name, font=(_FONT_SANS, 9, "bold"),
                          fill=band_color, anchor='e')

            freq_str = f"{freq:.3f} MHz" if freq < 1000 else f"{freq/1000:.3f} GHz"

            # Balk achtergrond (met 1 px rand-inzet voor subtiele 3D rand)
            c.create_rectangle(BAR_X, y + 1, BAR_X + BAR_MAX, y + BAR_H - 1,
                               fill=BG_SURFACE, outline=BORDER, width=1)

            if pct == 0:
                c.create_text(BAR_X + BAR_MAX // 2, y + BAR_H // 2,
                              text=self._tr("closed"), font=(_FONT_SANS, 8),
                              fill=TEXT_DIM, anchor='center')
                c.create_text(BAR_X + BAR_MAX + PCT_W // 2, y + BAR_H // 2,
                              text="0%", font=(_FONT_SANS, 9, "bold"),
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
                fill_w = int(BAR_MAX * pct / 100)
                cond = (self._tr("cond_good") if pct >= 60 else
                        (self._tr("cond_fair") if pct >= 30 else self._tr("cond_poor")))
                if fill_w > 3:
                    _gradient_fill(BAR_X + 1, y + 2, BAR_X + fill_w, y + BAR_H - 2,
                                   band_color)
                    # Glans-lijn bovenaan de balk
                    gr = min(255, int(int(band_color[1:3], 16) * 1.5))
                    gg = min(255, int(int(band_color[3:5], 16) * 1.5))
                    gb = min(255, int(int(band_color[5:7], 16) * 1.5))
                    c.create_line(BAR_X + 2, y + 2, BAR_X + fill_w - 1, y + 2,
                                  fill=f"#{gr:02x}{gg:02x}{gb:02x}", width=1)
                c.create_text(BAR_X + BAR_MAX + PCT_W // 2, y + BAR_H // 2,
                              text=f"{pct}%", font=(_FONT_SANS, 9, "bold"),
                              fill=TEXT_H1, anchor='center')
                tip = [
                    (f"{name}  ·  {freq_str}", None),
                    None,
                    (self._tr("reliability_lbl"), f"{pct}%  –  {cond}"),
                    (self._tr("modes_lbl"),        _BAND_MODES.get(name, "—")),
                    ("FT8:",                       _BAND_FT8.get(name, "—") + " MHz"),
                ]

            # Frequentie
            c.create_text(BAR_X + BAR_MAX + PCT_W + FREQ_W // 2, y + BAR_H // 2,
                          text=freq_str.split()[0], font=(_FONT_SANS, 8),
                          fill=TEXT_DIM, anchor='center')

            # Modi
            c.create_text(BAR_X + BAR_MAX + PCT_W + FREQ_W + MODES_W // 2, y + BAR_H // 2,
                          text=_BAND_MODES.get(name, ""), font=(_FONT_SANS, 8),
                          fill=TEXT_DIM, anchor='center')

            # FT8 frequentie
            ft8 = _BAND_FT8.get(name, "—")
            c.create_text(BAR_X + BAR_MAX + PCT_W + FREQ_W + MODES_W + FT8_W // 2,
                          y + BAR_H // 2,
                          text=ft8, font=(_FONT_SANS, 8),
                          fill=ACCENT if ft8 != "—" else TEXT_DIM, anchor='center')

            # WSPR spot-teller — klein, grijs als 0, geel als actief
            w_cnt = wspr_counts.get(name, 0)
            w_x   = BAR_X + BAR_MAX + PCT_W + FREQ_W + MODES_W + FT8_W + WSPR_W // 2
            if w_cnt:
                c.create_text(w_x, y + BAR_H // 2,
                              text=str(w_cnt), font=(_FONT_SANS, 8, "bold"),
                              fill=ACCENT, anchor='center')
            else:
                c.create_text(w_x, y + BAR_H // 2,
                              text="·", font=(_FONT_SANS, 8),
                              fill=TEXT_DIM, anchor='center')

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
                                      font=(_FONT_SANS, 7, "bold"),
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
        if _CAT_DISABLED:
            return
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
        outer.pack(fill=tk.BOTH, expand=True, pady=(0, 0))

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

        self._hist_canvas = tk.Canvas(outer, height=90, bg=BG_PANEL,
                                      bd=0, highlightthickness=0)
        self._hist_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 6))
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
                          fill=TEXT_DIM, font=(_FONT_SANS, 7), anchor='e')

        if len(data) < 2:
            c.create_text(W // 2, PAD_T + gh // 2,
                          text=self._tr("no_hist_data"),
                          fill=TEXT_DIM, font=(_FONT_SANS, 9), anchor='center')
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
        outer.pack(fill=tk.BOTH, expand=True, pady=(0, 0))
        tk.Frame(outer, bg=ACCENT, height=2).pack(fill=tk.X)

        hdr = tk.Frame(outer, bg=BG_PANEL)
        hdr.pack(fill=tk.X, padx=10, pady=(4, 2))
        _sched_title = tk.Label(hdr, text=self._tr("sched_header"),
                                font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT)
        _sched_title.pack(side=tk.LEFT)
        self._tr_widgets["sched_header"] = _sched_title
        self._sched_canvas = tk.Canvas(outer, height=180, bg=BG_PANEL,
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
                          fill=TEXT_DIM, font=(_FONT_SANS, 7), anchor='s')

        # ── Bereken propagatie per uur en per band ────────────────────────
        # grid_data[bi][h] = pct  (voor hover-tooltip)
        grid_data: list[list[int]] = [[0] * n_hours for _ in range(n_bands)]

        for bi, (bname, _) in enumerate(hf_bands):
            cy = PAD_T + bi * cell_h
            # Bandnaam links
            c.create_text(PAD_L - 3, cy + cell_h // 2, text=bname,
                          fill=TEXT_DIM, font=(_FONT_SANS, 7), anchor='e')
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
        outer.pack(fill=tk.BOTH, expand=True)

        # ── Solar / Ionosfeer sectie bovenin DX-paneel ───────────────────────
        self._build_solar_section(outer)

        # Gouden scheidingslijn tussen solar en DX spots
        tk.Frame(outer, bg=ACCENT, height=2).pack(fill=tk.X, pady=(6, 0))

        hdr = tk.Frame(outer, bg=BG_PANEL)
        hdr.pack(fill=tk.X, padx=10, pady=(4, 2))
        _dx_title = tk.Label(hdr, text=self._tr("dx_header"),
                             font=_font(10, "bold"), bg=BG_PANEL, fg=ACCENT)
        _dx_title.pack(side=tk.LEFT)
        self._tr_widgets["dx_header"] = _dx_title
        _dx_own_cb = tk.Checkbutton(hdr, text=self._tr("own_cont_lbl"),
                                    variable=self._dx_own_cont_var,
                                    command=self._filter_dx_spots,
                                    bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                                    activebackground=BG_PANEL, activeforeground=TEXT_H1,
                                    font=_font(9))
        _dx_own_cb.pack(side=tk.RIGHT, padx=(0, 4))
        self._tr_widgets["own_cont_lbl"] = _dx_own_cb

        # Heatmap toggle knop
        self._dx_heatmap_btn = tk.Button(
            hdr, text="Heatmap",
            command=self._toggle_dx_heatmap,
            font=_font(8), bg=BG_SURFACE, fg=TEXT_DIM,
            activebackground=BG_HOVER, activeforeground=TEXT_H1,
            relief=tk.FLAT, padx=6, pady=1, cursor="hand2")
        self._dx_heatmap_btn.pack(side=tk.RIGHT, padx=(0, 6))

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
        def _dx_scroll(e):
            if e.num == 4 or e.delta > 0:
                self._dx_canvas.yview_scroll(-1, "units")
            else:
                self._dx_canvas.yview_scroll(1, "units")
        self._dx_canvas.bind("<MouseWheel>", _dx_scroll)   # Windows & Mac
        self._dx_canvas.bind("<Button-4>",   _dx_scroll)   # Linux scroll up
        self._dx_canvas.bind("<Button-5>",   _dx_scroll)   # Linux scroll down

    def _filter_dx_spots(self):
        if not hasattr(self, "_dx_status_var"):
            return
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

    def _toggle_dx_heatmap(self):
        self._dx_heatmap_mode = not self._dx_heatmap_mode
        if self._dx_heatmap_mode:
            self._dx_heatmap_btn.config(fg=ACCENT, bg=BG_HOVER)
        else:
            self._dx_heatmap_btn.config(fg=TEXT_DIM, bg=BG_SURFACE)
        self._draw_dx_panel()

    def _draw_dx_heatmap(self, c, W: int, H: int):
        """Teken heatmap: band (Y) × UTC-uur (X) → spot-intensiteit."""
        BANDS = ["160m","80m","60m","40m","30m","20m","17m","15m","12m","10m","6m"]
        HOURS = 24
        MARGIN_L = 38   # bandnaam links
        MARGIN_B = 18   # uurlabels onder
        MARGIN_T = 6

        cw = max(1, (W - MARGIN_L) // HOURS)     # cel breedte
        ch = max(1, (H - MARGIN_T - MARGIN_B) // len(BANDS))  # cel hoogte

        # Tel spots per (band, uur)
        counts: dict[tuple, int] = {}
        for ts, band in self._dx_spot_history:
            h = ts.hour
            counts[(band, h)] = counts.get((band, h), 0) + 1

        max_count = max(counts.values(), default=1)

        for bi, band in enumerate(BANDS):
            y0 = MARGIN_T + bi * ch
            y1 = y0 + ch
            # Bandlabel
            color = _BAND_COLORS.get(band, TEXT_DIM)
            c.create_text(MARGIN_L - 3, (y0 + y1) // 2,
                          text=band, fill=color,
                          font=(_FONT_MONO, 7, "bold"), anchor='e')
            for hour in range(HOURS):
                x0 = MARGIN_L + hour * cw
                x1 = x0 + cw - 1
                cnt = counts.get((band, hour), 0)
                if cnt:
                    intensity = min(1.0, cnt / max_count)
                    base = _BAND_COLORS.get(band, "#607080")
                    # Alpha-simulatie: vervaag van BG_SURFACE naar base_color
                    r0, g0, b0 = int(BG_SURFACE[1:3], 16), int(BG_SURFACE[3:5], 16), int(BG_SURFACE[5:7], 16)
                    r1, g1, b1 = int(base[1:3], 16), int(base[3:5], 16), int(base[5:7], 16)
                    r = int(r0 + (r1 - r0) * intensity)
                    g = int(g0 + (g1 - g0) * intensity)
                    b = int(b0 + (b1 - b0) * intensity)
                    fill = f"#{r:02X}{g:02X}{b:02X}"
                else:
                    fill = BG_SURFACE
                c.create_rectangle(x0, y0, x1, y1 - 1, fill=fill, outline="")
                if cnt and cw >= 12:
                    c.create_text((x0 + x1) // 2, (y0 + y1) // 2,
                                  text=str(cnt), fill=BG_ROOT if intensity > 0.5 else TEXT_DIM,
                                  font=(_FONT_MONO, 6))

        # Uurlabels onderin
        for hour in range(0, HOURS, 3):
            x = MARGIN_L + hour * cw + cw // 2
            c.create_text(x, H - MARGIN_B + 3,
                          text=f"{hour:02d}", fill=TEXT_DIM,
                          font=(_FONT_MONO, 7), anchor='n')

        # "UTC" label
        c.create_text(MARGIN_L + (HOURS * cw) // 2, H - 3,
                      text="UTC", fill=TEXT_DIM, font=(_FONT_MONO, 6), anchor='s')

        # Geen history-label
        if not self._dx_spot_history:
            c.create_text(W // 2, H // 2,
                          text="Nog geen spothistorie (wacht op eerste refresh…)",
                          fill=TEXT_DIM, font=(_FONT_SANS, 8), anchor='center')

        c.configure(scrollregion=(0, 0, W, H))

    def _draw_dx_panel(self):
        if not hasattr(self, "_dx_canvas"):
            return
        c = self._dx_canvas
        c.delete("all")
        W = c.winfo_width() or 700
        H = c.winfo_height() or 196

        if getattr(self, "_dx_heatmap_mode", False):
            self._draw_dx_heatmap(c, W, H)
            return

        spots = getattr(self, "_dx_filtered", [])
        ROW_H = 16
        C_UTC  = 38;  C_BAND = 38;  C_DX = 84
        C_FREQ = 68;  C_SPOT = 74
        C_CMT  = max(40, W - C_UTC - C_BAND - C_DX - C_FREQ - C_SPOT - 12)

        # Kolomkoppen
        for txt, x in [("UTC",                          4),
                       (self._tr("dx_col_band"),        4 + C_UTC),
                       ("DX",                           4 + C_UTC + C_BAND),
                       ("MHz",                          4 + C_UTC + C_BAND + C_DX),
                       (self._tr("dx_col_spotter"),     4 + C_UTC + C_BAND + C_DX + C_FREQ),
                       (self._tr("dx_col_comment"),     4 + C_UTC + C_BAND + C_DX + C_FREQ + C_SPOT)]:
            c.create_text(x, 2, text=txt, fill=ACCENT,
                          font=(_FONT_MONO, 8, "bold"), anchor='nw')
        c.create_line(0, ROW_H + 2, W, ROW_H + 2, fill=BORDER)

        if not spots:
            c.create_text(W // 2, H // 2,
                          text=self._tr("no_dx_spots"),
                          fill=TEXT_DIM, font=(_FONT_SANS, 9), anchor='center')
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
            c.create_text(x, y, text=s["time"],         fill=TEXT_DIM,  font=(_FONT_MONO, 8), anchor='nw'); x += C_UTC
            c.create_text(x, y, text=band,              fill=color,     font=(_FONT_MONO, 8, "bold"), anchor='nw'); x += C_BAND
            c.create_text(x, y, text=s["dx"][:11],      fill=TEXT_H1,   font=(_FONT_MONO, 8), anchor='nw'); x += C_DX
            c.create_text(x, y, text=s["freq_mhz"],     fill=TEXT_BODY, font=(_FONT_MONO, 8), anchor='nw'); x += C_FREQ
            c.create_text(x, y, text=s["spotter"][:10], fill=TEXT_DIM,  font=(_FONT_MONO, 8), anchor='nw'); x += C_SPOT
            c.create_text(x, y, text=s.get("comment", "")[:max_ch],
                          fill=TEXT_DIM, font=(_FONT_MONO, 8), anchor='nw')
        total_h = ROW_H + 4 + len(spots) * ROW_H
        c.configure(scrollregion=(0, 0, W, total_h))

    def _refresh_dx(self):
        spots = _fetch_dx_spots()
        self.root.after(0, lambda: self._on_dx_spots(spots))

    def _on_dx_spots(self, spots: list):
        self._dx_all_spots = spots
        # Accumuleer history voor heatmap (24h buffer)
        now = datetime.datetime.now(datetime.timezone.utc)
        cutoff = now - datetime.timedelta(hours=24)
        new_entries = [(now, s["band"]) for s in spots if s.get("band")]
        self._dx_spot_history = (
            [(t, b) for t, b in self._dx_spot_history if t >= cutoff]
            + new_entries
        )
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
        def _do_fetch():
            snr_min = self._wspr_snr_min.get()
            band_filter_raw = self._wspr_band_filter.get()
            band_filter = set(band_filter_raw.split(",")) - {""} if band_filter_raw else None
            spots = _fetch_wspr_spots(snr_min=snr_min, band_filter=band_filter)
            self.root.after(0, lambda: self._on_wspr_spots(spots))

        threading.Thread(target=_do_fetch, daemon=True).start()

    def _on_wspr_spots(self, spots: list):
        self._wspr_spots = spots
        # Tel spots per band voor weergave in bandbalken
        counts: dict = {}
        for s in spots:
            b = s.get("band", "")
            if b:
                counts[b] = counts.get(b, 0) + 1
        self._wspr_band_counts = counts
        if self._show_wspr_var.get():
            self._draw_map()
        # Bandbalken hertekenen zodat WSPR-tellers direct zichtbaar zijn
        self._draw_prop_bars(self._last_band_pct)
        self._schedule_wspr()

    def _schedule_wspr(self):
        self._wspr_after_id = self.root.after(
            WSPR_REFRESH_SECS * 1000,
            lambda: threading.Thread(target=self._refresh_wspr, daemon=True).start()
        )

    # ── Advies panel ─────────────────────────────────────────────────────────
    def _build_advice_panel(self, parent):
        # Geen vaste hoogte op outer — inhoud bepaalt de hoogte via adv_wrap (fixed)
        outer = tk.Frame(parent, bg=BG_PANEL)
        # side=BOTTOM: claimt ruimte vóórdat top_row uitbreidt met expand=True
        outer.pack(side=tk.BOTTOM, fill=tk.X, pady=(6, 0))
        tk.Frame(outer, bg=ACCENT, height=2).pack(fill=tk.X)
        adv_hdr = tk.Frame(outer, bg=BG_PANEL)
        adv_hdr.pack(fill=tk.X, padx=10, pady=(4, 2))
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
                       self._show_aurora_var.get(),
                       self._hist_range_var.get(),
                       self._hist_sel,
                       self._k_alert_var.get(),
                       self._band_alert_var.get(),
                       self._alert_k_en_var.get(),
                       self._alert_band_en_var.get(),
                       self._alert_xflare_en_var.get(),
                       self._alert_pca_en_var.get(),
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
        self._tray_icon = pystray.Icon("HAMIOS", tray_img, "HAMIOS v3.0", menu)
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
        k_threshold    = self._k_alert_var.get()
        band_threshold = self._band_alert_var.get()

        # ── K-index drempel ──────────────────────────────────────────────
        k_above = k_index >= k_threshold
        if k_above and not self._prev_k_above and self._alert_k_en_var.get():
            self._tray_notify(
                "⚠️ Geomagnetische storm",
                f"K-index is gestegen naar {int(k_index)} (drempel: {k_threshold}). "
                "HF-propagatie kan verstoord zijn.")
        self._prev_k_above = k_above

        # ── Band-opening detectie (drempel instelbaar) ───────────────────
        newly_open = []
        for name, pct in bp.items():
            was_open = self._prev_band_open.get(name, False)
            is_open  = pct >= band_threshold
            if is_open and not was_open:
                newly_open.append(f"{name} ({pct}%)")
            self._prev_band_open[name] = is_open

        if newly_open and self._alert_band_en_var.get():
            bands_str = ",  ".join(newly_open)
            self._tray_notify(
                "📡 Band geopend",
                f"{bands_str} — kwaliteit ≥ {band_threshold}%.")

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

    def _update_net_indicator(self, ok: bool):
        """Toon of verberg de OFFLINE-indicator in de header (main-thread)."""
        self._net_ok = ok
        if ok:
            self._offline_lbl.pack_forget()
        else:
            # Pack direct na de HAMIOS-titel (links)
            if not self._offline_lbl.winfo_ismapped():
                self._offline_lbl.pack(side=tk.LEFT, padx=(0, 6))

    # ── Solar data ────────────────────────────────────────────────────────────
    def _refresh_solar(self):
        data = _fetch_solar()
        net_ok = "error" not in data and bool(data)
        # Ionosonde: kies dichtstbijzijnde station o.b.v. QTH
        station = _nearest_iono_station(self._qth_lat, self._qth_lon)
        iono = _fetch_ionosonde(station[0])
        data["iono_fof2"]    = iono["fof2"]
        data["iono_time"]    = iono["time"]
        data["iono_station"] = iono["station"]
        # Bz 24-uurs geschiedenis
        data["bz_history"]   = _fetch_bz_24h()
        # Nieuwe data: Kp-historiek, X-ray, storm-kansen
        data["kp_history"]   = _fetch_kp_24h()
        data["xray_history"] = _fetch_xray_24h()
        data["storm_probs"]  = _fetch_storm_probs()
        self.root.after(0, lambda: self._update_net_indicator(net_ok))
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


        # ── Kp-kleur: storm-kleuring ─────────────────────────────────────────
        try:
            kp_p = float(data.get("kp_planet", "0").replace("—", "0"))
            if kp_p >= 7:
                kp_color = "#EF5350"   # rood — severe storm
            elif kp_p >= 5:
                kp_color = "#FFA726"   # oranje — storm
            elif kp_p >= 3:
                kp_color = "#FFF176"   # geel — onrustig
            else:
                kp_color = TEXT_H1
            if hasattr(self, "_solar_val_lbls") and "kp_planet" in self._solar_val_lbls:
                self._solar_val_lbls["kp_planet"].config(fg=kp_color)
        except (ValueError, TypeError):
            pass

        # ── Solarwind dichtheid — kleur op basis van niveau ─────────────────
        try:
            dens = float(data.get("sw_density", "0").replace("—", "0"))
            if dens > 15:
                dens_color = "#FFA726"
            elif dens > 5:
                dens_color = TEXT_H1
            else:
                dens_color = TEXT_DIM
            if hasattr(self, "_solar_val_lbls") and "sw_density" in self._solar_val_lbls:
                self._solar_val_lbls["sw_density"].config(fg=dens_color)
        except (ValueError, TypeError):
            pass

        # ── 3-daagse storm-kans weergave ─────────────────────────────────────
        if hasattr(self, "_storm_fc_vars"):
            probs = data.get("storm_probs", [])
            days = ["Morgen", "Overmorgen", "Dag 3"]
            for i, var in enumerate(self._storm_fc_vars):
                if i < len(probs):
                    p = probs[i]
                    d = str(p.get("date", ""))[-5:]  # MM-DD
                    mn, mo, sv = p.get("minor", 0), p.get("moderate", 0), p.get("severe", 0)
                    var.set(f"{days[i]} ({d}): K5={mn}% K6={mo}% K7={sv}%")
                else:
                    var.set("—")

        # ── Bz 24-uurs grafiek ────────────────────────────────────────────────
        if "bz_history" in data:
            self._draw_bz_graph(data["bz_history"])

        # ── Kp 48-uurs staafdiagram ───────────────────────────────────────────
        if "kp_history" in data:
            self._draw_kp_bars(data["kp_history"])

        # ── X-ray 24-uurs grafiek ─────────────────────────────────────────────
        if "xray_history" in data:
            self._draw_xray_graph(data["xray_history"])

        self._recalc_prop(auto_daynight=True)
        self.root.after(0, self._draw_map)
        self._schedule_solar()

    def _draw_bz_graph(self, pts: list):
        """Teken Bz 24-uurs grafiek op self._bz_canvas."""
        self._last_bz_pts = pts
        if not hasattr(self, "_bz_canvas"):
            return
        c = self._bz_canvas
        c.update_idletasks()
        W = c.winfo_width()  or 200
        H = c.winfo_height() or 120
        c.delete("all")

        # Achtergrond
        c.create_rectangle(0, 0, W, H, fill=BG_SURFACE, outline="")

        if not pts:
            c.create_text(W // 2, H // 2, text="—", fill=TEXT_DIM,
                          font=(_FONT_MONO, 9))
            return

        BZ_MAX = 40.0
        PAD_L, PAD_R, PAD_T, PAD_B = 30, 6, 6, 16

        gW = W - PAD_L - PAD_R
        gH = H - PAD_T - PAD_B

        def bz_to_y(bz):
            return PAD_T + gH / 2 - (max(-BZ_MAX, min(BZ_MAX, bz)) / BZ_MAX) * (gH / 2)

        def t_to_x(hours_ago):
            return PAD_L + gW * (1.0 - min(hours_ago, 24) / 24)

        y0 = bz_to_y(0)

        # Lichte horizontale gridlijnen bij -20, 0, +20
        for bz_ref in (-20, 0, 20):
            yr = bz_to_y(bz_ref)
            is_zero = bz_ref == 0
            # Nul-as iets helderder
            grid_color = "#404850" if not is_zero else "#505860"
            dash = () if not is_zero else (4, 4)
            c.create_line(PAD_L, yr, W - PAD_R, yr,
                          fill=grid_color, width=1, dash=dash)

        # Tijdgridlijnen bij 6, 12, 18h geleden
        for h in (6, 12, 18):
            xg = t_to_x(h)
            c.create_line(xg, PAD_T, xg, H - PAD_B, fill="#404850", width=1, dash=(2, 4))

        # Y-as labels
        for bz_ref, lbl in [(-20, "-20"), (0, "0"), (20, "+20"), (-40, "-40"), (40, "+40")]:
            yr = bz_to_y(bz_ref)
            if PAD_T <= yr <= H - PAD_B:
                c.create_text(PAD_L - 3, yr, text=lbl, fill=TEXT_DIM,
                              font=(_FONT_MONO, 7), anchor='e')

        # Tijdlabels
        for h, lbl, anch in [(24, "24h", 'nw'), (12, "12h", 'n'), (0, self._tr("bz_now_lbl"), 'ne')]:
            xg = t_to_x(h)
            c.create_text(xg, H - PAD_B + 2, text=lbl,
                          fill=TEXT_DIM, font=(_FONT_MONO, 7), anchor=anch)

        # Bouw gesorteerde lijst: oudste punt eerst (hours_ago aflopend)
        ordered = sorted(pts, key=lambda p: p[0], reverse=True)
        xy_all  = [(t_to_x(ha), bz_to_y(bz), bz) for ha, bz in ordered]

        # Area fill: één aaneengesloten polygoon per kleur, gesloten op nul-as
        poly_pos = [PAD_L, y0]
        poly_neg = [PAD_L, y0]
        for x, y, bz in xy_all:
            if bz >= 0:
                poly_pos += [x, y]
            else:
                poly_neg += [x, y]
        if len(xy_all) >= 2:
            last_x = xy_all[-1][0]
            if len(poly_pos) >= 6:
                c.create_polygon(poly_pos + [last_x, y0], fill="#1A3A4A", outline="")
            if len(poly_neg) >= 6:
                c.create_polygon(poly_neg + [last_x, y0], fill="#3A1A1A", outline="")

        # Lijnlaag: segment per kleur op nul-crossing
        if len(xy_all) >= 2:
            for i in range(len(xy_all) - 1):
                x1, y1, bz1 = xy_all[i]
                x2, y2, _   = xy_all[i + 1]
                color = "#4FC3F7" if bz1 >= 0 else "#EF5350"
                c.create_line(x1, y1, x2, y2, fill=color, width=2)

        # Huidige Bz-waarde: grote tekst rechtsboven
        last_bz = ordered[-1][1]
        clr = "#EF5350" if last_bz < -10 else ("#FFA726" if last_bz < 0 else "#4FC3F7")
        c.create_text(W - PAD_R - 2, PAD_T,
                      text=f"{last_bz:+.1f} nT", fill=clr,
                      font=(_FONT_MONO, 8, "bold"), anchor='ne')

        # Y-as lijn
        c.create_line(PAD_L, PAD_T, PAD_L, H - PAD_B, fill=BORDER, width=1)

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
                if xray != self._last_xflare and self._alert_xflare_en_var.get():
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
            if s_level > self._last_pca_level and self._alert_pca_en_var.get():
                self._tray_notify(
                    f"☢ Proton event S{s_level}",
                    self._tr("pca_notify_body").format(pf=pf, dur=dur))
            self._last_pca_level = s_level
        else:
            self._pca_var.set("")
            self._last_pca_level = 0

    # ── Geschiedenis laden in background ──────────────────────────────────────
    def _load_history_bg(self):
        """Prune + laad geschiedenis buiten de main thread; update hist-grafiek daarna."""
        _prune_history()
        rows = _load_history()
        self.root.after(0, lambda: self._on_history_loaded(rows))

    def _on_history_loaded(self, rows: list):
        self._history = rows
        self._draw_hist_graph()


# ── Entrypoint ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import signal
    import traceback as _tb

    root = tk.Tk()
    root.withdraw()   # verberg tot UI volledig is opgebouwd en gecentreerd

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
