"""
HAMIOS v4.0.2
by Frank van Dijke

Real-time HF propagation, solar weather and DX monitor for Windows.

Features:
  Solar / ionosphere
    SFI, SSN, A/K/Kp-index, Bz, solar wind speed & density,
    X-ray 24h chart, Kp 48h bar chart, 3-day geomagnetic storm forecast,
    worldwide ionosondes (nearest foF2 + map markers), MUF/LUF model.

  HF Band Reliability
    MUF/LUF propagation model (SFI, SSN, K-index, QTH latitude),
    SNR budget per mode/power/antenna, gradient band bars in band colours,
    band opening schedule (24h heatmap, local time), band history (90 days).

  World Map
    Equirectangular NASA map, zoom/pan (1×–8×), great-circle paths,
    day/night terminator, gray line, aurora oval (K-index / IGRF-2025),
    sun + moon position (moon shows current phase, southern-hemisphere aware),
    sun/moon 24h trajectory path, ITU region overlay (R1/R2/R3),
    Maidenhead locator grid, callsign prefix layer (~110 DXCC),
    WSPR spots, DX cluster spots, ionosonde markers on map.

  Satellite Tracking  (🛰 Sat)
    TLE data from Celestrak (Amateur/ISS/Weather/CubeSat),
    position dot, orbital path (past + future, CEST/CET times),
    footprint overlay (green when QTH inside coverage zone),
    QTH-in-zone notification in alerts panel,
    category filter, ↻ TLE on-demand refresh.

  Spy / Numbers Stations  (🕵 Spy)
    24 stations — name, country, frequencies, mode, broadcast schedule,
    sortable columns, active/inactive filter, hover detail panel,
    editable hamios_spy_stations.json.

  DX Spots
    dxwatch.com JSON feed (5 min), own-continent filter,
    heatmap mode (band × UTC-hour, 24h buffer),
    spots drawn as markers on world map.

  Propagation Advice
    12 analysis cards: best bands, geo-storm, solar activity, solar wind,
    X-flare/SWF, ionosphere (MUF/LUF), day/night windows, mode advice,
    auroral absorption, DX cluster analysis, overall score, storm forecast.

  Notifications & Alerts
    K-index storm alert, band-open threshold, X-flare/SWF warning,
    PCA/proton event warning, satellite overhead indicator (with elevation).

  Other
    14 languages via external language packs (langs/*.json),
    dynamic themes (Midnight / DeepOcean / HighContrast),
    system tray (minimise + tray notifications),
    scrolling ticker, auto-refresh (30 s – 1 h),
    all settings saved to HAMIOS.ini,
    CAT interface (temporarily disabled, code intact).

Dependencies:
  pip install pillow
  pip install pyserial   # optioneel, voor CAT-interface
  pip install pystray    # optioneel, voor systeemtray
  pip install websocket-client  # optioneel, voor live blikseminslagen

─────────────────────────────────────────────────────────────────────
Todo
─────────────────────────────────────────────────────────────────────
- Splashscreen -
- [x] Fix: Splashscreen reageert niet op selectie wel of niet tonen — show_splash verplaatst naar App-sectie in INI (was Map)
- [x] Fix: Laat syntax zien per dependency om te installeren

- Panelen -
- [x] Fix: Panelen moeten altijd op de voorgrond — lift interval 500ms→2000ms
- [x] Fix: De panelen moeten actief worden waar je deze ook aanklikt

- Spy paneel -
- [x] Fix: Spy paneel start niet in het midden van het scherm — win.update() + winfo_width()
- [x] Fix: Sat paneel start niet in het midden van het scherm — win.update() + winfo_width()

- Onweer paneel -
- [x] Fix: Geen onweer informatie (wereldwijd of bij qth) — websocket-client installeren + CAPE altijd geladen
- [x] Fix: Onweerpaneel status geeft Verbroken — alleen tonen als verbinding ooit live was

- Worldmap -
- [x] Vis: Meridianen mogen iets lichter van kleur (cyan)
- [x] Vis: Color picker in settings voor Worldmap en meridianen — 🎨 sectie in Instellingen

- Solar verloop panel -
- [x] Fix: geen uitleg informatie bij grafiek. Maak uitgebreide explainer

- Tooltips -
- [x] Fix: Xray, Bz en Kp, Maak uitgebreide explainer
- [x] Fix: Solar history tooltip blijft staan — <Leave> binding toegevoegd
- [x] Fix: Meer uitgebreidere uitleg bij alle tooltips

─────────────────────────────────────────────────────────────────────
Change Log (4.0.1)
─────────────────────────────────────────────────────────────────────
· 2026-05-12 13:49 — Uitgebreide Nederlandse tooltips toegevoegd:
  Band condities tabel: hover-tooltip per bandnaam (freq, propagatiekarakter, advies).
  Storm forecast header: tooltip met K5/K6/K7+ uitleg en kansen per dag.
  Meldingen paneel: tooltips op K-alert, band-alert, X-flare en PCA checkbuttons.
  Band reliability bars: verrijkte tooltip met Kwaliteit en Advies per band.

· 2026-05-12 13:33 — Bug fixes: splash INI-sectie, dialogen gecentreerd, lightning status,
  color picker voor kaart, solar history tooltip <Leave>, lift interval 2s.

· 2026-05-11 19:05 — Splash toggle fix, panel lift improvements, spy/sat dialog centering,
  Bz/Kp/Xray comprehensive tooltips, solar history legend, lighter cyan graticule,
  recursive panel click activation.

· 2026-05-11 18:14 — Overlay tekst leesbaarder (TEXT_BODY), grayline donkerder (100,130,90),
  lightning-panel toont correcte status als websocket-client ontbreekt,
  panelen altijd naar voren (_lift_all_panels + desktop bind + DraggablePanel.show),
  emoji-iconen toegevoegd aan band_cond_hdr/storm_fc_hdr/solar_hist_hdr in lang_nl.json,
  Bz Y-as zoom-control (SpinBox 10–100 nT) in standalone Bz-paneel,
  rijkere tooltips met context voor Bz/Kp/X-ray charts,
  flash-ring ripple-effect (10s) bij nieuwe blikseminslagen op de kaart.

· 2026-05-11 — Overlay beschrijvingen, satelliet hover tooltip, iconen fixes,
  grayline kleur, band legenda terug, 2:1 ratio fix, ITU verwijderd,
  sat in Data overlay, lightning default aan, Arm→Gesloten vertaling.

· 2026-05-11 17:47 — Panel splits (3 nieuwe panelen):
  _build_solar_section: band-tabel en stormprognose-sectie verwijderd.
  _build_band_cond_panel: nieuw paneel voor band dag/nacht condities.
  _build_storm_fc_panel: nieuw paneel voor 3-daagse stormprognose.
  _build_solar_hist_panel + _draw_solar_hist_chart: solar historiek (SFI+Kp)
  als apart paneel; _draw_hist_graph toont nu alleen bandlijnen.
  Drie nieuwe IDs in _PANEL_DEFAULTS, _PANEL_MAP, _update_panel_titles,
  _PANEL_LABELS in settings en _T + lang_nl.json.
  _draw_solar_hist_chart() toegevoegd aan alle _draw_hist_graph()-aanroepen.

· 2026-05-11 17:11 — Meerdere verbeteringen (Changes 1–11):
  Fix 2:1 ratio: VH = W//2 * zoom in _draw_map() en _draw_dx_spots()
  zodat satelliet- en overlay-posities correct blijven na resize.
  Grayline-kleur verzacht: amber (255,200,60) → gedempt groen-grijs (180,200,160).
  ITU volledig verwijderd: _ITU_DISABLED, arrays (_ITU_B/A/A_RUS/C),
  ITU-tekenblok in _draw_map(), overlay-entry, CONFIG_SCHEMA, _save_settings.
  Sat overlay verplaatst van Display naar Data in overlay-dialoog.
  Band history legenda terug: klikbare kleurlabels onder de grafiek;
  _toggle_band werkt ook legendakleuren bij.
  Worldmap placeholder: tweede tekstlijn met gebruiksuitleg.
  Sat dialoog: oranje waarschuwing als satelliet-overlay uitstaat.
  Panelen altijd in front: content.bind("<Button-1>") → frame.lift().
  Snap-to-grid instelling (1–20 px) toegevoegd aan Layout-sectie in Instellingen.

· 2026-05-09 10:34 CEST — Vis: kaart-overlays naar header-knop:
  "🗺 Overlay"-knop in header opent dialoog met Display- en Data-groepen.
  Overlay-rij verwijderd uit worldmap paneel (minder druk, meer kaartruimte).
  Splash centrering: winfo_reqwidth na update_idletasks + fallback 480×360.
  overlay_btn vertaalsleutel in alle 13 taalbestanden.

· 2026-05-09 10:08 CEST — Drie startup-fixes:
  1. Bare Tk-window: root gepositioneerd op -32000,-32000 met overrideredirect,
     geen deiconify → splash Toplevel verschijnt zonder zichtbare root.
  2. Splash centrering: win.update() voor dimensiemeting + geometry met
     winfo_width/height ipv winfo_reqwidth/height.
  3. Startup = saved default: _load_startup_window_geometry() leest __window__
     uit __default__ en past venstergrootte/-positie toe na app-init.

· 2026-05-09 10:00 CEST — Fixes:
  Splash screen gecentreerd (//3 → //2 verticaal).
  Lightning paneel default positie 440,800 → 1200,800 (overlapte met kp_48h).
  _layout.get(pid) met fallback zodat nieuwe panels werken bij oude INI.

· 2026-05-09 09:54 CEST — Splash screen:
  _check_and_show_dependencies() vervangen door volwaardig _show_splash():
  App-naam (groot), versienummer, ✅/❌ per dep, kopieer-commando, amber
  "Doorgaan →"-knop. Vinkje "Toon bij opstarten" slaat direct naar INI.
  Settings heeft ook splash-toggle onder Dependencies.
  show_splash in CONFIG_SCHEMA, _save_settings en _save_cur_settings.

· 2026-05-09 09:48 CEST — Dependency-status in settings + startup fix:
  Settings-dialoog toont "📦 Dependencies" sectie onderaan met ✅/❌ per package.
  Klik op install-commando kopieert naar klembord.
  Startup: root.deiconify()+update() vóór dep-dialoog zodat Toplevel zichtbaar
  is; -topmost + focus_force() op dialoog; root.withdraw() na dep-check.

· 2026-05-09 09:43 CEST — Dependency-check bij opstarten:
  _check_and_show_dependencies(): dialoog met groene vinkjes (aanwezig) en
  rode kruisjes (ontbreekt). Klik op install-commando = kopieer naar klembord.
  _SERIAL_OK definitie toegevoegd (pyserial import ontbrak).
  Lightning-paneel toegevoegd aan Settings→Panelen lijst.

· 2026-05-08 21:59 CEST — Fix: onweer-paneel zichtbaar + dubbele iconen weg:
  Lightning default positie 820,1220 → 440,800 (was buiten beeld).
  Settings/panelen checkboxes: lbl=_tr(tr_key) ipv f"{icon}  {_tr(tr_key)}"
  (vertaling bevat al emoji).

· 2026-05-08 — v4.0.2: Onweer-layer en voorspellingspaneel:
  Blitzortung WebSocket voor live blikseminslagen op kaart.
  Open-Meteo CAPE/LI voorspelling als apart Onweer-paneel (⚡).
  QRN-waarschuwing op basis van CAPE en actieve inslagen.

· 2026-05-08 21:01 CEST — Settings live vertaling:
  Settings-knop geregistreerd in _tr_widgets → wordt direct bijgewerkt.
  _apply_translations() sluit en heropent de settings-dialoog (after 50ms)
  als die open is bij taalwisseling — alle tekst direct correct.

· 2026-05-08 20:57 CEST — Panelen-knop weg; alles in Instellingen-dialoog:
  Panelen-menuknop verwijderd uit header. Reset layout, Opslaan als standaard
  en Profielen (nieuw/laden/overschrijven/verwijderen) verplaatst naar een
  Layout- en Profielen-sectie in de settings-dialoog.
  8 nieuwe vertaalsleutels in alle 13 talen.

· 2026-05-08 20:48 CEST — Settings-dialoog panelen + exit rechts + startup-fix:
  Panelen-sectie in settings-dialoog: vinkjes delen _panel_vis_vars met het
  Panelen-menu → altijd synchroon. Exit-knop verplaatst naar rechts (? | ✕ | ⛶).
  _load_panel_layout() laadt nu eerst __default__ uit hamios_layouts.json zodat
  startup-indeling overeenkomt met "Opslaan als standaard".

· 2026-05-08 20:45 CEST — Vertalingen volledig:
  8 nieuwe sleutels in _T en alle 13 taalbestanden: theme_lbl, sw_speed_lbl,
  settings_btn/title/qth/iface, close_lbl, panels_btn.
  Hardcoded strings in header en settings-dialoog vervangen door _tr().

· 2026-05-08 20:39 CEST — Header opgeruimd: ⚙ Instellingen-dialoog:
  QTH, tooltips, ticker, taal, thema, zomertijd verplaatst naar
  _open_settings_dialog() Toplevel. Help-knop rechts voor Fullscreen.
  Header behoudt: titel | Exit | Panelen | Sat | Spy | CAT | ⚙ Instellingen
  rechts: Auto: [interval] countdown | separator | tijd | ? | ⛶

· 2026-05-08 20:31 CEST — Performance: drag/resize drastisch versneld:
  _active_drag class-var in DraggablePanel; after_idle batching in drag/resize-
  move; on_release callback triggert _deferred_redraw(). _debounce() helper:
  alle 10 canvas-<Configure> bindings wachten 150ms. Geen PIL-renders tijdens
  drag/resize — hertekenen pas bij loslaten. Line-ending fix: dubbele CR weg.

· 2026-05-08 20:21 CEST — Profiel overschrijven:
  Elk profiel in het submenu heeft nu "💾 Overschrijven" naast Laden/Verwijderen.
  _overwrite_named_layout() slaat de huidige layout direct op onder de bestaande naam.

· 2026-05-08 20:12 CEST — Dubbele iconen weg + snap-raster 2px:
  DraggablePanel.update_title/_icon_lbl gebruikt nu alleen title (geen icon-
  parameter voorvoegsel); vertaalde titels bevatten al emoji. _PANEL_GRID 10→2.

· 2026-05-08 20:05 CEST — Layout-presets systeem:
  "💾 Opslaan als standaard" slaat venster+panelen op als __default__;
  "↺ Reset layout" gebruikt die opgeslagen standaard of _PANEL_DEFAULTS.
  "👤 Profielen" submenu: nieuw opslaan + opgeslagen profielen laden/verwijderen.
  Opslag in hamios_layouts.json (venstergrootte+positie inbegrepen).

· 2026-05-08 19:56 CEST — Meldingen-paneel + worldmap fix:
  Meldingen (🔔 alerts) als apart DraggablePanel: K-drempel, band-drempel,
  X-flare/PCA knoppen, satelliet-in-QTH-zone; verwijderd uit band_rel paneel.
  Toegevoegd aan _PANEL_DEFAULTS (0,500,200,280), _PANEL_MAP en _update_panel_titles.
  Worldmap: 2:1 ratio losgelaten; VH = canvas H × zoom — kaart vult het volledige
  paneel ongeacht de hoogte; ook DX/WSPR overlays bijgewerkt.

· 2026-05-08 19:51 CEST — Paneel-verbeteringen (3):
  Afgeronde hoeken verwijderd; outer frame terug naar tk.Frame met bg=ACCENT.
  1px amber lijn rondom het paneel: tbar padx=1 pady=(1,0), content padx=1 pady=(0,1).
  lift() werkt weer correct (tk.Frame, geen Canvas-conflict meer).

· 2026-05-08 19:43 CEST — Paneel-verbeteringen (2):
  Bz 24h en X-ray 24h gesplitst in twee aparte panelen (bz_24h, xray_24h)
  met eigen build-wrappers en eigen tooltip/cursor handlers.
  Header-kleuren omgedraaid: bg=BG_PANEL fg=ACCENT (donker+amber ipv amber+donker).
  Blauwe balk onder worldmap verholpen: canvas bg #1B3A5C→BG_ROOT.
  Fullscreen-knop verplaatst naar helemaal rechts in de header.
  _update_corners gebruikt altijd BG_ROOT (volgt thema-wisseling).

· 2026-05-08 19:31 CEST — Paneel-verbeteringen:
  Wereldkaart: canvas fill=BOTH+expand zodat kaart het hele paneel vult.
  Panelen-knop: amber tekst (#FFA726) en ▦-icoon.
  Afgeronde hoeken: outer frame van tk.Frame naar tk.Canvas; _update_corners()
  overschrijft de 4 hoek-vierkantjes met achtergrondkleur (r=7px).
  Reset layout: "↺ Reset layout" menu-item in Panelen-menu roept
  _reset_panel_layout() aan — herstelt alle panelen naar _PANEL_DEFAULTS.

· 2026-05-08 — v4.0.1: Volledig nieuwe interface
  DraggablePanel systeem: alle panelen sleepbaar, aanpasbaar,
  snap-raster (10px), amber kader + titelbalk per paneel, ✕-knop.
  9 panelen op vrij canvas: Band Rel, Wereldkaart, Solar, Band Schema,
  Band Verloop, Kp 48h, Bz+Xray, DX Spots, Propagatie Advies.
  Fullscreen (F11/⛶), paneel-toggle menu in header, positie/grootte
  opgeslagen per paneel in HAMIOS.ini [Panels]. Solar en DX Spots
  zijn nu aparte panelen. Hoogte ook aanpasbaar (resizable=True,True).

Change Log (3.4)
─────────────────────────────────────────────────────────────────────
· 2026-05-07 16:55 CEST — Grafieken: tooltips, legenda en layout:
  Band-legenda frame verwijderd; ruimte benut voor grotere grafiekverhouding
  (62% banden / 10px gap / 38% solar-strip). Klik op grafiek filtert band.
  _on_hist_motion: band-legenda + solar-sectie (SFI/K/A/Bz) + hint in tooltip.
  Kp 48h: _Tooltip met K-waarde, storm-status, tijdstip, cursor-lijn.
  X-ray 24h: _Tooltip met flare-klasse, flux, tijdstip, cursor-lijn.
  Bz 24h: Toplevel→_Tooltip; positief/negatief Bz-interpretatie toegevoegd.
  3 nieuwe vertaalsleutels in alle 13 taalbestanden.


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
try:
    import serial as _serial_lib
    _SERIAL_OK = True
except ImportError:
    _serial_lib = None
    _SERIAL_OK = False
try:
    import websocket as _ws_lib
    _WEBSOCKET_OK = True
except ImportError:
    _WEBSOCKET_OK = False
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
import json as _json_mod
import logging
import logging.handlers
import time as _time_mod
import pickle as _pickle_mod

# ── Logging setup ──────────────────────────────────────────────────────────────
_LOG_FILE = os.path.join(
    os.path.dirname(sys.executable) if getattr(sys, "frozen", False)
    else os.path.dirname(os.path.abspath(__file__)),
    "HAMIOS.log"
)
_log_handler = logging.handlers.RotatingFileHandler(
    _LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
)
_log_handler.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)-7s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
))
log = logging.getLogger("HAMIOS")
log.setLevel(logging.INFO)
log.addHandler(_log_handler)

# ── Disk cache (JSON + TTL) ────────────────────────────────────────────────────
_CACHE_FILE = os.path.join(os.path.dirname(_LOG_FILE), "HAMIOS_cache.pkl")
_cache_lock = threading.Lock()

def _cache_get(key: str, max_age_s: int = 300):
    """Return cached value for key if younger than max_age_s, else None."""
    try:
        with _cache_lock:
            if not os.path.exists(_CACHE_FILE):
                return None
            with open(_CACHE_FILE, "rb") as f:
                store = _pickle_mod.load(f)
        entry = store.get(key)
        if entry and (_time_mod.time() - entry["ts"]) < max_age_s:
            return entry["data"]
    except Exception:
        pass
    return None

def _cache_set(key: str, data):
    """Write data into the disk cache under key."""
    try:
        with _cache_lock:
            store = {}
            if os.path.exists(_CACHE_FILE):
                try:
                    with open(_CACHE_FILE, "rb") as f:
                        store = _pickle_mod.load(f)
                except Exception:
                    store = {}
            store[key] = {"ts": _time_mod.time(), "data": data}
            with open(_CACHE_FILE, "wb") as f:
                _pickle_mod.dump(store, f)
    except Exception as e:
        log.warning("Cache write failed: %s", e)

# ── Network retry wrapper ──────────────────────────────────────────────────────
def _fetch_with_retry(url: str, timeout: int = 8, retries: int = 3,
                      headers: dict = None) -> bytes | None:
    """Fetch URL with exponential-backoff retry. Returns bytes or None."""
    if headers is None:
        headers = {"User-Agent": "HAMIOS/3.1"}
    delay = 2
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as exc:
            log.warning("Fetch attempt %d/%d failed for %s: %s",
                        attempt + 1, retries, url, exc)
            if attempt < retries - 1:
                _time_mod.sleep(delay)
                delay *= 2
    return None

# CAT temporarily disabled — code intact, interface blocked until stable
_CAT_DISABLED = True

# ── Satellite tracking ─────────────────────────────────────────────────────────
_TLE_GROUPS = {
    "Amateur":  "https://celestrak.org/NORAD/elements/gp.php?GROUP=amateur&FORMAT=tle",
    "ISS":      "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=tle",
    "Weather":  "https://celestrak.org/NORAD/elements/gp.php?GROUP=weather&FORMAT=tle",
    "CubeSat":  "https://celestrak.org/NORAD/elements/gp.php?GROUP=cubesat&FORMAT=tle",
}
_TLE_CACHE_FILE = None   # set after APP_DIR is defined

# ── Platform detection ─────────────────────────────────────────────────────────
_IS_MAC = sys.platform == "darwin"
_IS_WIN = sys.platform == "win32"
# Platform-specific font names
_FONT_SANS = "Helvetica Neue" if _IS_MAC else ("Segoe UI"  if _IS_WIN else "DejaVu Sans")
_FONT_MONO = "Menlo"          if _IS_MAC else ("Consolas"  if _IS_WIN else "DejaVu Sans Mono")

# ── Paths ──────────────────────────────────────────────────────────────────────
APP_DIR       = (os.path.dirname(sys.executable)
                 if getattr(sys, "frozen", False)
                 else os.path.dirname(os.path.abspath(__file__)))
SETTINGS_FILE   = os.path.join(APP_DIR, "HAMIOS.ini")
HIST_FILE       = os.path.join(APP_DIR, "HAMIOS_history.csv")
_TLE_CACHE_FILE  = os.path.join(APP_DIR, "hamios_tle.json")
_SPY_FILE        = os.path.join(APP_DIR, "hamios_spy_stations.json")
_LAYOUTS_FILE    = os.path.join(APP_DIR, "hamios_layouts.json")
# Lightning
BLITZORTUNG_WS       = "wss://ws1.blitzortung.org:443/"   # poort 3000 geweigerd; 443 werkt
STORM_FORECAST_URL   = "https://api.open-meteo.com/v1/forecast"
_LIGHTNING_KEEP_MIN  = 30   # bewaar inslagen van afgelopen N minuten
# Equirectangular NASA map (2048×1024 = exact 2:1 → coordinates are correct)
MAP_FILE      = os.path.join(APP_DIR, "worldmap_eq.jpg")
MAP_URL       = ("https://eoimages.gsfc.nasa.gov/images/imagerecords/"
                 "57000/57752/land_shallow_topo_2048.jpg")

# ── Theme ──────────────────────────────────────────────────────────────────────
# ── Fixed layout row heights ───────────────────────────────────────────────────
APP_HDR_H  = 42    # header bar
TICKER_H   = 22    # ticker bar
ROW_0_H    = 551   # top row:    map canvas (449) + chrome (102)
ROW_1_H    = 275   # bottom row: schema / hist / kp / bz+xray
ROW_2_H    = 380   # advice row
LAYOUT_PAD = 20    # body pady + grid paddings
WINDOW_H   = APP_HDR_H + ROW_0_H + ROW_1_H + ROW_2_H + TICKER_H + LAYOUT_PAD  # 1250

# Advice card sizing derived from ROW_2_H
# ROW_2_H = ADV_HDR_STRIP + ADV_ROWS*(ADV_CARD_H+ADV_CARD_GAP) + 8
# 340 = 40 + 4*(ADV_CARD_H+ADV_CARD_GAP) + 8  →  ADV_CARD_H+GAP = 73
ADV_ROWS     = 4
ADV_CARD_H   = 70   # 70 + 3 = 73  →  4*73+48 = 340 ✓
ADV_CARD_GAP = 3
ADV_HDR_STRIP  = 40
ADV_SECTION_H  = ADV_HDR_STRIP + ADV_ROWS * (ADV_CARD_H + ADV_CARD_GAP) + 8  # 340

# Solar panel minimum: header(32) + params(198) + alert section(110) +
#   band table header+11bands(196) + sep(11) + x-flare(44) + PCA(32) = ~623
#   → buffer → 720px (Bz graph is now in HF band panel)
SOLAR_MIN_H   = 720

# Minimum window height: header + solar + body margins + advice (free height) + ticker
# ADV_SECTION_H + 30px margin for advice header and font-scaling variation
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

# ── Draggable panelen ─────────────────────────────────────────────────────────
_PANEL_GRID = 2    # snap-raster in pixels

# Standaard paneel-layout (id → (x, y, w, h, zichtbaar))
_PANEL_DEFAULTS: dict = {
    "band_rel":   (0,    0,    430, 600, True),
    "worldmap":   (440,  0,    740, 490, True),
    "solar":      (1190, 0,    370, 600, True),
    "band_sched": (440,  500,  370, 290, True),
    "band_hist":  (820,  500,  370, 290, True),
    "band_cond":  (0,    500,  200, 400, True),
    "storm_fc":   (0,    910,  200, 140, True),
    "solar_hist": (820,  800,  370, 120, True),
    "kp_48h":     (440,  800,  370, 270, True),
    "bz_24h":     (820,  800,  370, 200, True),
    "xray_24h":   (820, 1010,  370, 200, True),
    "lightning":  (1200, 800,  370, 300, True),
    "alerts":     (0,    500,  200, 280, True),
    "dx_spots":   (1200, 610,  370, 460, True),
    "prop_adv":   (0,    610,  430, 460, True),
}

# ── Map colours ───────────────────────────────────────────────────────────────
MAP_OCEAN  = (27,  58,  92)    # dark blue
MAP_LAND   = (45,  96, 128)    # blue-grey
MAP_COAST  = (60, 122, 160)    # coastline
MAP_NIGHT  = (0,    8,  20, 150)  # night overlay (RGBA)
MAP_GRID   = (45,  90, 140)    # graticule — licht cyaan
MAP_SUN    = (255, 215,   0)   # sun
MAP_MOON   = (200, 200, 200)   # moon
MAP_QTH    = ( 80, 180, 255)   # own position (bright blue)





def _ll_to_xy(lat: float, lon: float, W: int, H: int) -> tuple:
    """Latitude/longitude → canvas coordinates (equirectangular)."""
    x = int((lon + 180) / 360 * W)
    y = int((90 - lat) / 180 * H)
    return x, y


def _subsolar_point() -> tuple:
    """Returns (lat, lon) of the point directly below the sun."""
    now = datetime.datetime.now(datetime.timezone.utc)
    doy = now.timetuple().tm_yday
    decl = -23.45 * math.cos(math.radians(360 / 365 * (doy + 10)))
    ut   = now.hour + now.minute / 60 + now.second / 3600
    lon  = -(ut - 12) * 15
    lon  = ((lon + 180) % 360) - 180
    return decl, lon


def _is_daytime_at_qth(lat: float, lon: float) -> bool:
    """True if the sun is above the horizon at the given QTH position."""
    sun_lat, sun_lon = _subsolar_point()
    lat_r     = math.radians(lat)
    sun_lat_r = math.radians(sun_lat)
    dlon_r    = math.radians(lon - sun_lon)
    cos_angle = (math.sin(lat_r)   * math.sin(sun_lat_r) +
                 math.cos(lat_r)   * math.cos(sun_lat_r) * math.cos(dlon_r))
    return cos_angle > 0


def _submoon_point() -> tuple:
    """Returns (lat, lon) of the point directly below the moon (simplified)."""
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


def _moon_phase_deg() -> float:
    """Maanfase in graden: 0=nieuwe maan, 90=eerste kwartier,
    180=volle maan, 270=laatste kwartier."""
    _, sun_lon  = _subsolar_point()
    _, moon_lon = _submoon_point()
    return (moon_lon - sun_lon + 360) % 360


def _moon_phase_icon(size: int, phase_deg: float,
                     qth_lat: float = 52.0) -> "Image":
    """Render een maanfase-icoon (PIL RGBA, size×size px).

    De verlichte kant wordt bepaald door de fase; het icoon wordt
    horizontaal gespiegeld voor waarnemers op het zuidelijk halfrond.
    """
    phase  = math.radians(phase_deg)
    icon   = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    pix    = icon.load()
    r      = size / 2 - 0.5
    cx = cy = size / 2 - 0.5

    LIT  = (235, 225, 190, 255)   # verlicht gedeelte
    DARK = (28,  28,  42,  255)   # onverlicht gedeelte

    flip = qth_lat < 0            # zuidelijk halfrond: spiegel

    for py in range(size):
        for px in range(size):
            dx = px - cx
            dy = py - cy
            if dx * dx + dy * dy > r * r:
                continue
            # x-positie van de terminator op deze y
            cos_y  = math.sqrt(max(0.0, 1.0 - (dy / r) ** 2))
            x_term = math.cos(phase) * r * cos_y
            # Toenemende maan (0–180°): verlicht rechts van terminator
            # Afnemende maan (180–360°): verlicht links
            lit = (dx > x_term) if phase <= math.pi else (dx < x_term)
            if flip:
                lit = not lit
            pix[px, py] = LIT if lit else DARK

    # Subtiele rand
    d = ImageDraw.Draw(icon)
    d.ellipse([(0, 0), (size - 1, size - 1)], outline=(140, 135, 110, 160))
    return icon


def _sun_path_pts(steps: int = 48) -> list:
    """Return (lat, lon_unwrapped) for the sun over ±12 h, unwrapped for PIL drawing."""
    now  = datetime.datetime.now(datetime.timezone.utc)
    pts  = []
    prev = None
    for i in range(steps + 1):
        t    = now + datetime.timedelta(hours=-12 + i * 24 / steps)
        doy  = t.timetuple().tm_yday
        decl = -23.45 * math.cos(math.radians(360 / 365 * (doy + 10)))
        ut   = t.hour + t.minute / 60 + t.second / 3600
        lon  = -(ut - 12) * 15          # no modulo — keep unwrapped
        if prev is not None:
            while lon - prev > 180:  lon -= 360
            while prev - lon > 180:  lon += 360
        pts.append((decl, lon))
        prev = lon
    return pts


def _moon_path_pts(steps: int = 48) -> list:
    """Return (lat, lon_unwrapped) for the moon over ±12 h, unwrapped for PIL drawing."""
    now  = datetime.datetime.now(datetime.timezone.utc)
    J2K  = datetime.datetime(2000, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    pts  = []
    prev = None
    for i in range(steps + 1):
        t    = now + datetime.timedelta(hours=-12 + i * 24 / steps)
        d    = (t - J2K).total_seconds() / 86400
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
        ut   = t.hour + t.minute / 60 + t.second / 3600
        GMST = (6.697375 + 0.0657098242 * d + ut) % 24
        lon  = (ra / 15 - GMST) * 15   # no modulo — keep unwrapped
        if prev is not None:
            while lon - prev > 180:  lon -= 360
            while prev - lon > 180:  lon += 360
        pts.append((lat, lon))
        prev = lon
    return pts


def _night_mask(sun_lat: float, sun_lon: float, W: int, H: int) -> "Image":
    """Night mask at full resolution with soft terminator transition.

    Optimisation: cos(lon − sun_lon) is pre-computed once per column,
    so the inner loop contains only a multiplication and addition.
    The transition zone (±SOFT degrees) fades from transparent to full night.
    """
    SOFT    = 0.06          # width of soft transition in cos units (~3–4°)
    NR, NG, NB, NA = MAP_NIGHT

    slr     = math.radians(sun_lat)
    slon    = math.radians(sun_lon)
    sin_sun = math.sin(slr)
    cos_sun = math.cos(slr)

    # Pre-computed cos(lon − sun_lon) per column — trig disappears from the loop
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
                # Soft transition: linear from 0 → NA
                alpha = int(NA * (SOFT - ca) / (2 * SOFT))
                px[x, y] = (NR, NG, NB, alpha)

    return img


def _graylijn_mask(sun_lat: float, sun_lon: float, W: int, H: int) -> "Image":
    """Golden-yellow band along the terminator (grey line, ~9° wide = ±~1000 km)."""
    HALF  = 0.155          # cos units half-band width (~9°)
    GR, GG, GB = 100, 130, 90  # donker gedempt groen-grijs

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
    """Return list of (lat, lon) along the great circle from point 1 to point 2."""
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


# ── Font helper (cached — each combination is created only once) ───────────────
_FONT_CACHE: dict = {}

def _font(size=10, weight="normal"):
    key = (size, weight)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = tkfont.Font(family=_FONT_SANS, size=size, weight=weight)
    return _FONT_CACHE[key]

# ── Settings ───────────────────────────────────────────────────────────────────
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
        "theme":      {"type": str, "options": ["Midnight", "DeepOcean", "HighContrast"], "default": "Midnight"},
        "show_splash": {"type": bool, "default": True},
    },
    "Map": {
        "show_sun": {"type": bool, "default": True},
        "show_moon": {"type": bool, "default": True},
        "show_locator": {"type": bool, "default": False},
        "show_graylijn": {"type": bool, "default": True},
        "show_cs": {"type": bool, "default": False},
        "show_spots": {"type": bool, "default": False},
        "show_wspr": {"type": bool, "default": False},
        "show_aurora":        {"type": bool, "default": True},
        "show_sat":           {"type": bool, "default": True},
        "show_sunmoon_path":  {"type": bool, "default": False},
        "show_iono":          {"type": bool, "default": False},
        "show_lightning":      {"type": bool, "default": True},
        "lightning_fade_min":  {"type": int,  "min": 1, "max": 60, "default": 30},
        "dx_own_cont": {"type": bool, "default": True},
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
                      show_cs: bool = False,
                      show_spots: bool = False,
                      show_wspr: bool = False,
                      show_aurora: bool = True,
                      show_sat: bool = True,
                      show_sunmoon_path: bool = False,
                      show_iono: bool = False,
                      show_lightning:     bool = True,
                      lightning_fade_min: int  = 30,
                      show_splash:        bool = True,
                      dx_own_cont: bool = True,
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
    cfg.read(SETTINGS_FILE, encoding="utf-8")   # preserve extra sections (e.g. [Satellites])
    cfg["QTH"]   = {"lat": str(lat), "lon": str(lon)}
    cfg["App"]   = {"refresh": refresh, "mode": mode, "power": power,
                    "antenna": antenna, "dst": str(dst),
                    "show_tips": str(show_tips), "show_ticker": str(show_ticker),
                    "language": language, "theme": theme,
                    "show_splash": str(show_splash)}   # hier, niet in Map
    cfg["Map"]   = {"show_sun": str(show_sun), "show_moon": str(show_moon),
                    "show_locator": str(show_locator),
                    "show_graylijn": str(show_graylijn),
                    "show_cs": str(show_cs),
                    "show_spots": str(show_spots),
                    "show_wspr": str(show_wspr),
                    "show_aurora":       str(show_aurora),
                    "show_sat":          str(show_sat),
                    "show_sunmoon_path": str(show_sunmoon_path),
                    "show_iono":         str(show_iono),
                    "show_lightning":     str(show_lightning),
                    "lightning_fade_min": str(lightning_fade_min),
                    "dx_own_cont":       str(dx_own_cont)}
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


def _load_startup_window_geometry() -> tuple | None:
    """Retourneert (x, y, w, h) van het venster uit de saved default, of None."""
    try:
        layouts = _load_layouts()
        if "__default__" in layouts:
            win = layouts["__default__"].get("__window__")
            if win and len(win) >= 4:
                return tuple(int(v) for v in win[:4])
    except Exception:
        pass
    return None


def _load_panel_layout() -> dict:
    """Lees paneel-layout.  Volgorde van prioriteit:
    1. __default__ in hamios_layouts.json  (opgeslagen door gebruiker)
    2. [Panels] sectie in HAMIOS.ini
    3. _PANEL_DEFAULTS (code-standaard)
    """
    # 1. Opgeslagen standaard
    try:
        layouts = _load_layouts()
        if "__default__" in layouts:
            saved = layouts["__default__"]
            result = {}
            for pid, defaults in _PANEL_DEFAULTS.items():
                dx, dy, dw, dh, dvis = defaults
                vals = saved.get(pid)
                if vals and len(vals) >= 5:
                    result[pid] = tuple(vals[:5])
                else:
                    result[pid] = defaults
            return result
    except Exception:
        pass

    # 2. INI
    cfg = configparser.ConfigParser()
    cfg.read(SETTINGS_FILE, encoding="utf-8")
    result = {}
    for pid, defaults in _PANEL_DEFAULTS.items():
        dx, dy, dw, dh, dvis = defaults
        try:
            x   = cfg.getint("Panels",     f"{pid}_x",   fallback=dx)
            y   = cfg.getint("Panels",     f"{pid}_y",   fallback=dy)
            w   = cfg.getint("Panels",     f"{pid}_w",   fallback=dw)
            h   = cfg.getint("Panels",     f"{pid}_h",   fallback=dh)
            vis = cfg.getboolean("Panels", f"{pid}_vis", fallback=dvis)
        except Exception:
            x, y, w, h, vis = dx, dy, dw, dh, dvis
        result[pid] = (x, y, w, h, vis)
    return result


def _save_panel_layout(panels: dict) -> None:
    """Schrijf paneel-layout naar INI [Panels] sectie."""
    cfg = configparser.ConfigParser()
    cfg.read(SETTINGS_FILE, encoding="utf-8")
    if not cfg.has_section("Panels"):
        cfg.add_section("Panels")
    for pid, panel in panels.items():
        x, y, w, h = panel.get_geometry()
        vis = panel.is_visible()
        cfg.set("Panels", f"{pid}_x",   str(x))
        cfg.set("Panels", f"{pid}_y",   str(y))
        cfg.set("Panels", f"{pid}_w",   str(w))
        cfg.set("Panels", f"{pid}_h",   str(h))
        cfg.set("Panels", f"{pid}_vis", str(vis))
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)


def _load_layouts() -> dict:
    """Laad gebruikers-layouts uit hamios_layouts.json."""
    try:
        if os.path.exists(_LAYOUTS_FILE):
            with open(_LAYOUTS_FILE, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_layouts(layouts: dict) -> None:
    """Schrijf gebruikers-layouts naar hamios_layouts.json."""
    try:
        with open(_LAYOUTS_FILE, "w", encoding="utf-8") as f:
            json.dump(layouts, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log.warning("layouts save failed: %s", e)


def _safe_request(url: str, timeout: int = 10, headers: dict = None) -> tuple[bool, any]:
    """Wrapper for urllib.request.urlopen to monitor connectivity.
    Returns (success, result).
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
# JSON endpoints zijn 404 per 2026; gebruik de text-forecast URL
STORM_PROB_URL  = "https://services.swpc.noaa.gov/text/3-day-geomag-forecast.txt"
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
        cached = _cache_get("solar", max_age_s=120)
        if cached:
            log.info("solar: cache hit")
            return cached
        xml = _fetch_with_retry(SOLAR_URL, timeout=8)
        if xml is None:
            log.warning("solar: all retries failed, returning empty")
            return _cache_get("solar", max_age_s=86400) or {}
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
        # ── Solar wind (NOAA SWPC) ────────────────────────────────────────────
        # Both endpoints return a list of dicts: [{...}, ...]
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
        # ── Solar wind density (from plasma 1-day, first entry) ──────────────
        try:
            with urllib.request.urlopen(SPEED_1DAY_URL, timeout=6) as r:
                plasma_rows = json.loads(r.read())
            # Format: [header_row, [time, density, speed, temperature], ...]
            # Most recent = last row with valid density
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
        # ── Planetary Kp-index (NOAA SWPC summary) ────────────────────────────
        try:
            with urllib.request.urlopen(KP_INDEX_URL, timeout=6) as r:
                kp_rows = json.loads(r.read())
            # Last row with valid Kp value
            kp_val = None
            for row in reversed(kp_rows):
                try:
                    if isinstance(row, dict):
                        kp_val = float(row.get("Kp") or row.get("kp") or 0)
                    elif isinstance(row, list) and len(row) >= 2:
                        if str(row[0]).lower().startswith("time"):
                            continue
                        kp_val = float(row[1])
                    else:
                        continue
                    break
                except (ValueError, TypeError):
                    continue
            data["kp_planet"] = f"{kp_val:.2f}" if kp_val is not None else "—"
        except Exception:
            data["kp_planet"] = "—"
        # ── Proton flux >10 MeV (GOES SWPC) ───────────────────────────────────
        # Primary: HamQSL XML 'protonflux' field; backup: NOAA GOES JSON
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
        _cache_set("solar", data)
        log.info("solar: fetched OK (SFI=%s K=%s)", data.get("sfi","?"), data.get("k_index","?"))
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
    """Fetch last 24h Bz values from NOAA SWPC (downsampled to ~120 pts).

    Returns list of (hours_ago, bz_nT); most recent point last.
    """
    try:
        raw = _fetch_with_retry(BZ_1DAY_URL, timeout=8)
        if raw is None:
            return _cache_get("bz_24h", max_age_s=3600) or []
        rows = json.loads(raw.decode())
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
    # Downsample to max 240 points
    if len(pts) > 240:
        step = len(pts) // 240
        pts = pts[::step]
    _cache_set("bz_24h", pts)
    return pts


def _fetch_kp_24h() -> list:
    """Fetch planetary Kp-index from NOAA (3-hour blocks, last 24-48h).

    Returns list of (hours_ago, kp); most recent point last.
    """
    cached = _cache_get("kp_24h", max_age_s=600)
    if cached is not None:
        return cached
    raw = _fetch_with_retry(KP_INDEX_URL, timeout=8)
    if raw is None:
        return _cache_get("kp_24h", max_age_s=86400) or []
    try:
        rows = json.loads(raw.decode())
    except Exception:
        return []
    # API returns list-of-dicts {'time_tag','Kp'} or legacy list-of-arrays
    if not rows:
        return []
    now_ts = datetime.datetime.now(datetime.timezone.utc)
    pts = []
    for row in rows:
        try:
            if isinstance(row, dict):
                ts_raw = str(row.get("time_tag", ""))
                kp     = float(row.get("Kp") or row.get("kp") or 0)
            elif isinstance(row, list) and len(row) >= 2:
                if str(row[0]).lower().startswith("time"):
                    continue   # header row
                ts_raw = str(row[0])
                kp     = float(row[1])
            else:
                continue
            ts = datetime.datetime.strptime(
                ts_raw[:19].replace("T", " "), "%Y-%m-%d %H:%M:%S")
            ts = ts.replace(tzinfo=datetime.timezone.utc)
            hours_ago = (now_ts - ts).total_seconds() / 3600
            if hours_ago > 48:
                continue
            pts.append((hours_ago, kp))
        except Exception:
            continue
    pts.reverse()
    _cache_set("kp_24h", pts)
    return pts


def _fetch_xray_24h() -> list:
    """Fetch GOES X-ray flux (0.1–0.8 nm channel, last 24h).

    Returns list of (hours_ago, flux_watts); downsampled to max 120 points.
    """
    cached = _cache_get("xray_24h", max_age_s=300)
    if cached is not None:
        return cached
    raw = _fetch_with_retry(XRAY_1DAY_URL, timeout=8)
    if raw is None:
        return _cache_get("xray_24h", max_age_s=86400) or []
    try:
        rows = json.loads(raw.decode())
    except Exception:
        return []
    if not rows:
        return []
    now_ts = datetime.datetime.now(datetime.timezone.utc)
    pts = []
    for entry in rows:
        try:
            # Use only 0.1-0.8nm channel (standard SXR); timestamps may use T or space
            if entry.get("energy", "") not in ("0.1-0.8nm", "short", ""):
                continue
            flux = float(entry.get("flux") or entry.get("observed_flux") or 0)
            if flux <= 0:
                continue
            ts_raw = entry.get("time_tag", "")
            ts = datetime.datetime.strptime(
                ts_raw[:19].replace("T", " "), "%Y-%m-%d %H:%M:%S")
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
    _cache_set("xray_24h", pts)
    return pts


def _fetch_storm_probs() -> list:
    """Fetch 3-day geomagnetic storm probabilities from NOAA SWPC text forecast.

    Returns list of dicts {date, minor, moderate, severe} for 3 days.
    """
    cached = _cache_get("storm_probs", max_age_s=3600)
    if cached is not None:
        return cached
    raw = _fetch_with_retry(STORM_PROB_URL, timeout=8, retries=2)
    if raw is None:
        log.info("storm_probs: fetch failed, using cache/empty")
        return _cache_get("storm_probs", max_age_s=86400) or []
    try:
        result = _parse_storm_probs_txt(raw.decode("utf-8", errors="replace"))
    except Exception as e:
        log.warning("storm_probs parse error: %s", e)
        return []
    _cache_set("storm_probs", result)
    return result


def _parse_storm_probs_txt(text: str) -> list:
    """Parse NOAA 3-day geomag forecast text into [{date, minor, moderate, severe}]."""
    import re
    result = []

    # "NOAA Geomagnetic Activity Probabilities 07 May-09 May"
    date_m = re.search(r'Probabilities\s+(\d{1,2}\s+\w+)', text)
    if date_m:
        try:
            year = datetime.datetime.utcnow().year
            start = datetime.datetime.strptime(f"{date_m.group(1)} {year}", "%d %b %Y")
            dates = [(start + datetime.timedelta(days=i)).strftime("%m-%d")
                     for i in range(3)]
        except Exception:
            dates = ["", "", ""]
    else:
        dates = ["", "", ""]

    minor_m    = re.search(r'Minor storm\s+([\d/]+)',         text)
    moderate_m = re.search(r'Moderate storm\s+([\d/]+)',      text)
    severe_m   = re.search(r'Strong-Extreme storm\s+([\d/]+)', text)

    if not (minor_m and moderate_m and severe_m):
        return []

    minor_v    = [int(v) for v in minor_m.group(1).split('/')]
    moderate_v = [int(v) for v in moderate_m.group(1).split('/')]
    severe_v   = [int(v) for v in severe_m.group(1).split('/')]

    for i in range(min(3, len(minor_v), len(moderate_v), len(severe_v))):
        result.append({
            "date":     dates[i] if i < len(dates) else "",
            "minor":    minor_v[i],
            "moderate": moderate_v[i],
            "severe":   severe_v[i],
        })
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
    'alerts_hdr':       {"en": '🔔  Notifications'},
    'alert_xflare_lbl': {"en": 'X-flare / SWF'},
    'alert_pca_lbl':    {"en": 'PCA / Proton'},
    'sat_zone_hdr':     {"en": '🛰  Satellite in QTH zone:'},
    'sat_zone_none':    {"en": '—'},
    'bz_chart_hdr':     {"en": '⚡  Bz 24h (nT)'},
    'bz_now_lbl':       {"en": 'now'},
    'theme_lbl':        {"en": 'Theme:'},
    'sw_speed_lbl':     {"en": 'SW:'},
    'settings_btn':     {"en": '⚙  Settings'},
    'settings_title':   {"en": '⚙  Settings'},
    'settings_qth':     {"en": 'QTH'},
    'settings_iface':        {"en": 'Interface'},
    'settings_layout':       {"en": 'Layout'},
    'settings_reset_layout': {"en": '↺  Reset layout'},
    'settings_save_default': {"en": '💾  Save as default'},
    'settings_profiles':     {"en": 'Profiles'},
    'settings_new_profile':  {"en": '＋  New profile...'},
    'settings_load':         {"en": '▶  Load'},
    'settings_overwrite':    {"en": '↻  Overwrite'},
    'settings_delete':       {"en": '🗑  Delete'},
    'close_lbl':             {"en": 'Close'},
    'panels_btn':            {"en": '▦  Panels'},
    'hist_bands_lbl':   {"en": 'Band reliability'},
    'hist_solar_lbl':   {"en": 'Solar indices'},
    'hist_click_hint':  {"en": 'Click chart · filter bands'},
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
    'overlay_btn':     {"en": '🗺  Overlay'},
    'map_pad_lbl':     {"en": 'Path'},
    'map_aurora_lbl':  {"en": 'Aurora'},
    'map_sat_lbl':     {"en": 'Sat'},
    'map_wspr_lbl':    {"en": 'WSPR'},
    'map_spots_lbl':   {"en": 'Spots'},
    'map_cs_lbl':      {"en": 'CS'},
    'map_iono_lbl':    {"en": 'Iono'},
    'map_lightning_lbl':  {"en": 'Ltng'},
    'lightning_hdr':      {"en": '⚡  Lightning'},
    'lightning_no_dep':   {"en": 'pip install websocket-client'},
    'lightning_conn':     {"en": 'Connecting to Blitzortung...'},
    'lightning_live':     {"en": '🟢 Live'},
    'lightning_disc':     {"en": '🔴 Disconnected — retrying...'},
    'lightning_strikes':  {"en": '{n} strikes (last {m} min)'},
    'storm_forecast_24h': {"en": '⚡  Storm forecast 24h'},
    'qrn_lbl':            {"en": 'QRN level:'},
    'qrn_low':            {"en": 'Low'},
    'qrn_moderate':       {"en": 'Moderate'},
    'qrn_high':           {"en": 'High — HF < 15 MHz disrupted'},
    'sw_density_lbl':  {"en": 'SW density (n/cm³)'},
    'kp_planet_lbl':   {"en": 'Kp (planetary)'},
    'storm_forecast_hdr': {"en": 'Storm forecast (3d)'},
    'band_cond_hdr':  {"en": '📻  Band Conditions'},
    'storm_fc_hdr':   {"en": '🌩  Storm Forecast'},
    'solar_hist_hdr': {"en": '☀  Solar History'},
    'kp_chart_hdr':    {"en": '🧲  Kp 48h'},
    'xray_chart_hdr':  {"en": '☢  X-ray 24h'},
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
    'adv_storm_fc_quiet':  {"en": '3-day forecast: quiet (K5 probability ≤5% each day). Stable HF expected.'},
    'adv_storm_fc_watch':  {"en": '3-day forecast: storm watch — {day} K5={mn}% K6={mo}% K7={sv}%. Plan DX sessions for calmer days.'},
    'adv_storm_fc_likely': {"en": '3-day forecast: storm likely — {day} K5={mn}% K6={mo}%. Prepare lower-band alternative routes.'},
    'adv_sw_ram_high':     {"en": 'Solar wind ram pressure elevated — speed {spd} km/s, density {dens} n/cm³ (P={pram:.0f} nPa). CME impact possible; monitor K-index.'},
    'adv_sw_ram_normal':   {"en": 'Solar wind nominal — speed {spd} km/s, density {dens} n/cm³. No immediate geomagnetic effects expected.'},
    'adv_kp_rising':       {"en": 'Kp rising last {h}h: {old:.1f}→{new:.1f} — geomagnetic activity increasing. Switch to lower bands; avoid polar routes.'},
    'adv_kp_falling':      {"en": 'Kp falling last {h}h: {old:.1f}→{new:.1f} — storm recovery in progress. Higher bands recovering; 20m improving.'},
    'adv_kp_stable':       {"en": 'Kp stable last {h}h at {kp:.1f} — geomagnetic conditions steady.'},
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
_HIST_SOLAR_COLS = ["sfi", "ssn", "k_index", "a_index",
                    "bz", "sw_speed", "sw_density", "xray"]
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


# ── DraggablePanel ────────────────────────────────────────────────────────────
class DraggablePanel:
    """Sleepbaar en aanpasbaar paneel met amber rand en titelbalk.

    Geplaatst via place() op een parent-widget (de desktop).
    Sleep via de amber titelbalk; grootte via resize-handle rechtsonder.
    Grid-snapping bij loslaten (_PANEL_GRID pixels).
    """
    _TITLE_H    = 26
    _MIN_W      = 160
    _MIN_H      = 100
    _active_drag = False   # class-level vlag: True tijdens drag/resize van élk paneel

    def __init__(self, parent: tk.Widget, title: str, icon: str = "",
                 panel_id: str = "", on_vis_change=None, on_release=None):
        self.panel_id       = panel_id
        self._on_vis_change = on_vis_change
        self._on_release    = on_release   # callback na drag/resize-einde
        self._visible       = True
        self._x = self._y   = 0
        self._w = self._h   = 300
        self._drag_sx = self._drag_sy = 0
        self._drag_ox = self._drag_oy = 0
        self._resize_sx = self._resize_sy = 0
        self._resize_ow = self._resize_oh = 0
        self._move_pending  = False

        # Outer frame: bg=ACCENT → 1px amber lijn rondom het paneel
        self.frame = tk.Frame(parent, bg=ACCENT, bd=0)

        # Titelbalk — donkere achtergrond, amber tekst; 1px amber zichtbaar boven+zijkanten
        self._tbar = tk.Frame(self.frame, bg=BG_PANEL, height=self._TITLE_H)
        self._tbar.pack(side=tk.TOP, fill=tk.X, padx=1, pady=(1, 0))
        self._tbar.pack_propagate(False)

        self._icon_lbl = tk.Label(
            self._tbar,
            text=title,          # titel bevat al emoji via vertaling
            font=_font(9, "bold"), bg=BG_PANEL, fg=ACCENT,
            anchor='w', padx=6
        )
        self._icon_lbl.pack(side=tk.LEFT, fill=tk.Y)

        self._hide_btn = tk.Button(
            self._tbar, text="✕",
            font=_font(8), bg=BG_PANEL, fg=ACCENT,
            activebackground=ACCENT, activeforeground=BG_ROOT,
            relief=tk.FLAT, padx=5, pady=0, cursor="hand2",
            command=self._toggle_hide
        )
        self._hide_btn.pack(side=tk.RIGHT, padx=(0, 3), pady=2)

        # Inhoud — 1px amber zichtbaar aan zijkanten en onderkant
        self.content = tk.Frame(self.frame, bg=BG_PANEL)
        self.content.pack(fill=tk.BOTH, expand=True, padx=1, pady=(0, 1))

        # Resize-handle rechtsonder (op outer frame zodat hij altijd zichtbaar is)
        self._rhandle = tk.Label(
            self.frame, text="◢",
            font=_font(8, "bold"), bg=ACCENT, fg=BG_PANEL,
            cursor="size_nw_se", bd=0
        )
        self._rhandle.place(relx=1.0, rely=1.0, anchor='se', x=-1, y=-1)

        # Drag-bindings op titelbalk en icoon-label
        for w in (self._tbar, self._icon_lbl):
            w.bind("<Button-1>",        self._on_drag_start)
            w.bind("<B1-Motion>",        self._on_drag_move)
            w.bind("<ButtonRelease-1>",  self._on_drag_end)

        # Resize-bindings op handle
        self._rhandle.bind("<Button-1>",        self._on_resize_start)
        self._rhandle.bind("<B1-Motion>",        self._on_resize_move)
        self._rhandle.bind("<ButtonRelease-1>",  self._on_resize_end)

        # Klik op content-area brengt het paneel naar de voorgrond
        self.content.bind("<Button-1>", lambda _: self.frame.lift(), add="+")

        # Zorg dat klikken OVERAL op het paneel het naar voren brengt
        def _bind_lift_recursive(widget):
            widget.bind("<Button-1>", lambda _: self.frame.lift(), add="+")
            for child in widget.winfo_children():
                _bind_lift_recursive(child)
        # Bind na build (content is nog leeg nu, maar after_idle pakt children op)
        self.frame.after_idle(lambda: _bind_lift_recursive(self.frame))

    # ── Titel bijwerken (bij taalwisseling) ──────────────────────────────────
    def update_title(self, title: str, icon: str = ""):
        self._icon_lbl.config(text=title)

    # ── Zichtbaarheid ────────────────────────────────────────────────────────
    def _toggle_hide(self):
        self.hide()
        if self._on_vis_change:
            self._on_vis_change(self.panel_id, False)

    def hide(self):
        self.frame.place_forget()
        self._visible = False

    def show(self):
        self._place_frame()
        self.frame.after_idle(self.frame.lift)
        self._visible = True

    def is_visible(self) -> bool:
        return self._visible

    # ── Plaatsing ────────────────────────────────────────────────────────────
    def place(self, x: int, y: int, w: int, h: int):
        self._x, self._y = int(x), int(y)
        self._w, self._h = int(w), int(h)
        self._place_frame()

    def _place_frame(self):
        self.frame.place(x=self._x, y=self._y,
                         width=self._w, height=self._h)

    def get_geometry(self) -> tuple:
        return self._x, self._y, self._w, self._h

    # ── Drag ────────────────────────────────────────────────────────────────
    def _on_drag_start(self, event):
        self._drag_sx   = event.x_root
        self._drag_sy   = event.y_root
        self._drag_ox   = self._x
        self._drag_oy   = self._y
        self._move_pending = False
        DraggablePanel._active_drag = True
        self.frame.lift()

    def _on_drag_move(self, event):
        dx = event.x_root - self._drag_sx
        dy = event.y_root - self._drag_sy
        self._x = max(0, self._drag_ox + dx)
        self._y = max(0, self._drag_oy + dy)
        # Batch: plan één _place_frame per event-loop iteratie
        if not self._move_pending:
            self._move_pending = True
            self.frame.after_idle(self._flush_move)

    def _flush_move(self):
        self._move_pending = False
        self._place_frame()

    def _on_drag_end(self, _event):
        g = _PANEL_GRID
        self._x = round(self._x / g) * g
        self._y = round(self._y / g) * g
        self._place_frame()
        DraggablePanel._active_drag = False
        if self._on_release:
            self._on_release()

    # ── Resize ──────────────────────────────────────────────────────────────
    def _on_resize_start(self, event):
        self._resize_sx  = event.x_root
        self._resize_sy  = event.y_root
        self._resize_ow  = self._w
        self._resize_oh  = self._h
        self._move_pending = False
        DraggablePanel._active_drag = True

    def _on_resize_move(self, event):
        dw = event.x_root - self._resize_sx
        dh = event.y_root - self._resize_sy
        self._w = max(self._MIN_W, self._resize_ow + dw)
        self._h = max(self._MIN_H, self._resize_oh + dh)
        if not self._move_pending:
            self._move_pending = True
            self.frame.after_idle(self._flush_move)

    def _on_resize_end(self, _event):
        g = _PANEL_GRID
        self._w = round(self._w / g) * g
        self._h = round(self._h / g) * g
        self._place_frame()
        DraggablePanel._active_drag = False
        if self._on_release:
            self._on_release()


# ── Satellite TLE helpers ──────────────────────────────────────────────────────

def _parse_tle_text(text: str) -> list[tuple[str, str, str]]:
    """Parse TLE text into list of (name, line1, line2) tuples."""
    sats = []
    lines = [l.rstrip() for l in text.splitlines() if l.strip()]
    i = 0
    while i < len(lines) - 2:
        if lines[i+1].startswith("1 ") and lines[i+2].startswith("2 "):
            sats.append((lines[i].strip(), lines[i+1], lines[i+2]))
            i += 3
        else:
            i += 1
    return sats


def _fetch_tle_group(group: str, url: str) -> list[tuple[str, str, str]]:
    """Fetch and parse TLE data for a group from Celestrak."""
    try:
        raw = _fetch_with_retry(url, timeout=10, retries=2)
        if raw is None:
            return []
        return _parse_tle_text(raw.decode("utf-8", errors="replace"))
    except Exception as e:
        log.warning("TLE fetch failed for %s: %s", group, e)
        return []


def _load_tle_cache() -> dict:
    """Load TLE cache from disk. Returns {group: [(name,l1,l2), ...]}."""
    try:
        if os.path.exists(_TLE_CACHE_FILE):
            with open(_TLE_CACHE_FILE, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_tle_cache(data: dict):
    """Save TLE data to disk cache."""
    try:
        with open(_TLE_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception as e:
        log.warning("TLE cache write failed: %s", e)


def _sgp4_latlon(line1: str, line2: str,
                 offset_min: float = 0.0) -> tuple[float, float, float] | None:
    """Simplified TLE propagator — returns (lat_deg, lon_deg, alt_km).

    offset_min: minutes relative to now (negative = past, positive = future).
    Uses Keplerian propagation without perturbations.
    Accuracy ~50 km, adequate for map display.
    """
    try:
        # Parse epoch from Line 1 (cols 18-32)
        ep = line1[18:32].strip()
        yr2 = int(ep[:2])
        yr = 2000 + yr2 if yr2 < 57 else 1900 + yr2
        day_of_year = float(ep[2:])
        epoch_dt = (datetime.datetime(yr, 1, 1, tzinfo=datetime.timezone.utc)
                    + datetime.timedelta(days=day_of_year - 1))

        # Parse Line 2
        incl  = math.radians(float(line2[8:16]))
        raan  = math.radians(float(line2[17:25]))
        ecc   = float("0." + line2[26:33])
        argp  = math.radians(float(line2[34:42]))
        M0    = math.radians(float(line2[43:51]))
        n_rev = float(line2[52:63])          # rev/day

        # Time since epoch in minutes
        now = datetime.datetime.now(datetime.timezone.utc)
        t_min = (now - epoch_dt).total_seconds() / 60.0 + offset_min

        # Mean motion rad/min and semi-major axis
        n_rad_min = n_rev * 2 * math.pi / (24 * 60)
        n_rad_s   = n_rev * 2 * math.pi / 86400
        mu = 398600.4418  # km³/s²
        a  = (mu / n_rad_s ** 2) ** (1 / 3)

        # Mean anomaly at current time
        M = (M0 + n_rad_min * t_min) % (2 * math.pi)

        # Solve Kepler's equation (10 iterations)
        E = M
        for _ in range(10):
            E = M + ecc * math.sin(E)

        # True anomaly and radius
        cos_E = math.cos(E)
        nu = math.atan2(math.sqrt(1 - ecc ** 2) * math.sin(E), cos_E - ecc)
        r  = a * (1 - ecc * cos_E)

        # Position in orbital plane → ECI
        xp = r * math.cos(nu)
        yp = r * math.sin(nu)

        cr, sr = math.cos(raan),  math.sin(raan)
        co, so = math.cos(argp),  math.sin(argp)
        ci, si = math.cos(incl),  math.sin(incl)

        x_eci = (cr*co - sr*so*ci)*xp + (-cr*so - sr*co*ci)*yp
        y_eci = (sr*co + cr*so*ci)*xp + (-sr*so + cr*co*ci)*yp
        z_eci =          si*so    *xp +           si*co    *yp

        # GMST at the actual position time (now + offset_min), not just now.
        # Without this correction the Earth appears frozen → track doesn't shift.
        J2000     = datetime.datetime(2000, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
        jd_offset = (now - J2000).total_seconds() / 86400 + offset_min / 1440.0
        gmst_deg  = (280.46061837 + 360.98564736629 * jd_offset) % 360
        g = math.radians(gmst_deg)

        x_ecef =  x_eci * math.cos(g) + y_eci * math.sin(g)
        y_ecef = -x_eci * math.sin(g) + y_eci * math.cos(g)
        z_ecef =  z_eci

        # Clamp to avoid asin domain error from floating-point rounding
        lat = math.degrees(math.asin(max(-1.0, min(1.0, z_ecef / r))))
        lon = math.degrees(math.atan2(y_ecef, x_ecef))
        alt = r - 6371.0   # altitude in km

        return lat, lon, alt
    except Exception:
        return None


def _calc_sat_path(line1: str, line2: str,
                   back_min: int = 60, fwd_min: int = 720,
                   back_step: int = 1, fwd_step: int = 10
                   ) -> tuple[list, list]:
    """Calculate orbital path segments.

    Returns (past_pts, fwd_pts) each as list of [lat, lon].
    back_step=1 min  → smooth past curve (60 points).
    fwd_step=10 min  → sparse future dots (72 points).
    [None, None] marks antimeridian breaks in each list.
    """
    def _segment(start, end, step):
        """Returns list of [lat, lon, offset_min] or [None, None, None] for breaks.
        step may be fractional (e.g. 0.5 min)."""
        seg: list = []
        prev_lon: float | None = None
        n = int((end - start) / step) + 1
        for i in range(n):
            offset = start + i * step
            if offset > end + 1e-9:
                break
            r = _sgp4_latlon(line1, line2, offset)
            if r is None:
                seg.append([None, None, None])
                prev_lon = None
                continue
            lat, lon, _ = r
            if prev_lon is not None and abs(lon - prev_lon) > 180:
                seg.append([None, None, None])   # antimeridian break
            seg.append([lat, lon, offset])
            prev_lon = lon
        return seg

    past_pts = _segment(-back_min, 0,       back_step)
    fwd_pts  = _segment(fwd_step,  fwd_min, fwd_step)
    return past_pts, fwd_pts


# ── Spy stations helpers ───────────────────────────────────────────────────────

_SPY_STATIONS_DEFAULT = [
    {"name": "UVB-76 (The Buzzer)", "country": "Rusland", "frequencies": ["4625 kHz"], "mode": "AM/USB", "active": True, "schedule": "Continu 24/7. Spraakberichten onregelmatig, geen vast patroon.", "info": "Continu 24/7 brom-toon, af en toe onderbroken door gesproken boodschappen in het Russisch (5-cijferige groepen). Vermoedelijk Russisch militair / GRU. Uitzendlocatie nabij Sint-Petersburg."},
    {"name": "M14a (The Pip)", "country": "Rusland", "frequencies": ["3756 kHz", "5448 kHz"], "mode": "USB", "active": True, "schedule": "Continu 24/7. Pip-toon elke ~2 seconden; spraak onregelmatig.", "info": "Korte 'pip'-toon elke twee seconden, af en toe spraakberichten. Russisch militair. Verwant aan UVB-76."},
    {"name": "S30 (The Alarm / Squeaky Wheel)", "country": "Rusland", "frequencies": ["3828 kHz", "4770 kHz", "7039 kHz"], "mode": "USB", "active": True, "schedule": "Continu 24/7 op wisselende frequenties.", "info": "Regelmatige 'piep'-toon vergelijkbaar met een alarmbel. Vermoedelijk Russische marine of GRU."},
    {"name": "M12a (The Lincolnshire Poacher)", "country": "Verenigd Koninkrijk", "frequencies": ["5765 kHz", "11545 kHz"], "mode": "AM/USB", "active": False, "schedule": "Was actief: dagelijks ~06:00, 10:00, 14:00, 18:00, 22:00 UTC (± 30 min). Gestopt ca. 2008.", "info": "Muziekintro 'Lincolnshire Poacher', gevolgd door 5-cijferige Engelse nummers. Geopereerd vanuit Akrotiri, Cyprus (GCHQ/MI6). Gestopt ca. 2008."},
    {"name": "SK01 (Cherry Ripe)", "country": "Verenigd Koninkrijk", "frequencies": ["4350 kHz", "8500 kHz"], "mode": "USB", "active": False, "schedule": "Was actief: onregelmatig, veelal 's nachts UTC. Gestopt ca. 2009.", "info": "Melodie 'Cherry Ripe' als intro, gevolgd door getelde nummers. Vermoedelijk GCHQ/MI6, gestopt ca. 2009."},
    {"name": "V24 / XM (Atencion)", "country": "Cuba", "frequencies": ["7887 kHz", "9955 kHz", "14872 kHz"], "mode": "AM/USB", "active": True, "schedule": "Di/Do/Za: 21:30-22:00 UTC op 7887 kHz; extra uitzendingen op onregelmatige tijden.", "info": "Begint met 'Atencion, Atencion', gevolgd door Spaanstalige 5-cijferige groepen. Cubaanse inlichtingendienst (DGI). Richt zich op CIA-activa in Cuba en Latijns-Amerika."},
    {"name": "HM01", "country": "Noord-Korea", "frequencies": ["6400 kHz", "9100 kHz", "11545 kHz"], "mode": "AM", "active": True, "schedule": "Ma/Wo/Vr: 00:00-00:30 UTC op 6400 kHz; 02:00-02:30 UTC op 9100 kHz. Aanvullende uitzendingen wisselend.", "info": "Koreaanse vrouwenstem met nummers, voorafgegaan door muziek. Reconnaissancebureau Noord-Korea. Uitzendingen regelmatig gemeld."},
    {"name": "E10 (Swedish Rhapsody)", "country": "Oost-Duitsland / onbekend", "frequencies": ["5765 kHz", "9157 kHz"], "mode": "AM", "active": False, "schedule": "Was actief: wisselend, voornamelijk avonduren CET. Gestopt eind jaren '90.", "info": "Muziekdoosje speelt 'Swedish Rhapsody', kinderstem leest 3-cijferige groepen. DDR Stasi-gebruik vermoedelijk. Gestopt eind jaren '90."},
    {"name": "E11 (Oblique)", "country": "Onbekend (West-Europa?)", "frequencies": ["6959 kHz", "8149 kHz"], "mode": "USB", "active": False, "schedule": "Was actief: onregelmatig, geen vast patroon bekend. Gestopt ca. 2000.", "info": "Schuine streep '/' gevolgd door lettergroepen in fonetisch alfabet. Vermoedelijk Duits of Tsjechisch."},
    {"name": "E03 (Czech Lady)", "country": "Tsjecho-Slowakije / Tsjechië", "frequencies": ["6840 kHz", "7485 kHz", "9350 kHz"], "mode": "AM", "active": False, "schedule": "Was actief: dagelijks meerdere blokken, o.a. 08:00, 13:00, 19:00 UTC. Gestopt ca. 1997.", "info": "Tsjechische vrouwenstem met 5-cijferige groepen. StB (Tsjechische geheime dienst). Gestopt ca. 1997."},
    {"name": "V07 (Cuban Numbers – Spaanstalig)", "country": "Cuba", "frequencies": ["9330 kHz", "11530 kHz"], "mode": "AM/USB", "active": True, "schedule": "Ma/Wo/Vr: 01:00-01:30 UTC op 9330 kHz; frequenties wisselend per seizoen.", "info": "Variant van Atencion-familie. Spaanstalige 5-cijferige groepen. DGI Cuba. Actief op wisselende frequenties."},
    {"name": "M03 (Russian Man)", "country": "Rusland", "frequencies": ["4583 kHz", "6998 kHz", "9131 kHz"], "mode": "USB", "active": True, "schedule": "Onregelmatig; waarnemingen voornamelijk 04:00-08:00 UTC en 16:00-20:00 UTC.", "info": "Russische mannenstem met 5-cijferige groepen. Vermoedelijk FSB of SVR. Actief op wisselende frequenties."},
    {"name": "G06 (Russian Lady)", "country": "Rusland", "frequencies": ["7344 kHz", "9057 kHz"], "mode": "USB", "active": True, "schedule": "Onregelmatig; vaker in ochtend- en avonduren UTC. Verwant patroon aan M03.", "info": "Russische vrouwenstem met getallen. Vermoedelijk SVR of GRU. Sterk verwant aan M03."},
    {"name": "P03 (Attention!)", "country": "Cuba / onbekend", "frequencies": ["5765 kHz", "7887 kHz"], "mode": "AM", "active": False, "schedule": "Was actief: wisselend, geen regelmatig schema gedocumenteerd. Gestopt ca. 2010.", "info": "Gelijkend op Atencion-station maar met afwijkende toonhoogte. Verwantschap met Cubaanse inlichtingendienst."},
    {"name": "S11a (Cynthia)", "country": "Rusland / Cuba", "frequencies": ["11464 kHz", "14489 kHz"], "mode": "USB", "active": False, "schedule": "Was actief: onregelmatig, vaker in avonduren UTC. Gestopt ca. 2000.", "info": "Muziekintro gevolgd door 5-cijferige Russische nummers. Vermoedelijk KGB-dochterorganisatie. Gestopt ca. 2000."},
    {"name": "V02a (The Counting Station)", "country": "Onbekend", "frequencies": ["10145 kHz", "14670 kHz"], "mode": "USB", "active": False, "schedule": "Was actief: geen vast schema, sporadische waarnemingen. Gestopt ca. 2005.", "info": "Vrouwenstem telt langzaam getallen in het Engels. Oorsprong onduidelijk; mogelijke CIA-link."},
    {"name": "M98", "country": "Rusland", "frequencies": ["8507.5 kHz"], "mode": "USB", "active": True, "schedule": "Continu aanwezig op 8507.5 kHz; berichten op onregelmatige tijden.", "info": "Moderne Russische numbers station met geautomatiseerde stem. Actief op vaste frequentie. FSB/GRU vermoedelijk."},
    {"name": "VC01 (Cuban Lady Counts)", "country": "Cuba", "frequencies": ["9955 kHz", "15175 kHz"], "mode": "AM", "active": True, "schedule": "Di/Do/Za: 03:00-03:30 UTC op 9955 kHz; aanvullend op 15175 kHz overdag.", "info": "Spaanstalige vrouwenstem telt langzame 5-cijferige groepen. Verwant aan Atencion-familie. DGI Cuba."},
    {"name": "F06 (Magnetic Fields / Numbers)", "country": "Onbekend", "frequencies": ["5765 kHz", "6325 kHz"], "mode": "USB", "active": False, "schedule": "Was actief: geen regelmatig schema gedocumenteerd. Gestopt ca. 2005.", "info": "Toon-reeksen die getallen coderen. Exacte herkomst onbekend. Europese of Russische origine vermoedelijk."},
    {"name": "4XZ (Israëlische marine)", "country": "Israël", "frequencies": ["5810 kHz", "8137 kHz", "12157 kHz"], "mode": "CW", "active": True, "schedule": "Continu 24/7; weerberichten elke 3 uur op XX:20 en XX:50 UTC.", "info": "IDF Marine seinstation. Morse-code navigatie- en operationele berichten. Roepnaam 4XZ. Actief."},
    {"name": "CHU (Canadese tijdsignaal)", "country": "Canada", "frequencies": ["3330 kHz", "7850 kHz", "14670 kHz"], "mode": "AM/USB", "active": True, "schedule": "Continu 24/7; tijdaankondiging elke minuut, gesproken aankondiging elk uur.", "info": "Officieel tijdsignaalstation van Canada (NRC). Tijdcodes + gesproken aankondigingen in Engels/Frans. Niet strikt 'spy', wel veelvuldig gebruikt voor bearingkalibratie door inlichtingendiensten."},
    {"name": "E06 (Yosemite Sam)", "country": "USA (USAF vermoedelijk)", "frequencies": ["4316 kHz", "8992 kHz"], "mode": "USB", "active": False, "schedule": "Was actief: sporadisch, geen regelmatig schema. Gestopt ca. 2004.", "info": "Fragment uit Looney Tunes (Yosemite Sam) gevolgd door data-bursts. Vermoedelijk test-uitzending USAF. Gestopt ca. 2004."},
    {"name": "XSL (Chinese marinestation)", "country": "China", "frequencies": ["8408 kHz", "12578 kHz", "16806 kHz"], "mode": "CW/USB", "active": True, "schedule": "Dagelijks meerdere uitzendblokken; CW-oproepen op vaste tijden rond 00:00, 06:00, 12:00, 18:00 UTC.", "info": "PLAN (Peoples Liberation Army Navy) maritiem communicatiestation. CW en digitale modes. Actief op meerdere frequenties."},
    {"name": "RDL (Russische marine, Moskou)", "country": "Rusland", "frequencies": ["12649 kHz", "16432 kHz"], "mode": "CW", "active": True, "schedule": "Dagelijks; CW-berichten op onregelmatige maar vaste terugkerende blokken, veelal 08:00-10:00 en 14:00-16:00 UTC.", "info": "Russisch marineseinstation. CW orders en navigatieberichten. Nauw verbonden met Russische onderzeebootoperaties."},
]


def _load_spy_stations() -> list:
    """Load spy stations from JSON file; create the file from defaults if absent."""
    if not os.path.exists(_SPY_FILE):
        try:
            with open(_SPY_FILE, "w", encoding="utf-8") as f:
                json.dump(_SPY_STATIONS_DEFAULT, f, ensure_ascii=False, indent=2)
            log.info("spy stations: created default file at %s", _SPY_FILE)
        except Exception as e:
            log.warning("spy stations: could not create file: %s", e)
            return list(_SPY_STATIONS_DEFAULT)
    try:
        with open(_SPY_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log.warning("spy stations: load failed (%s), using built-in defaults", e)
        return list(_SPY_STATIONS_DEFAULT)


# ── Spy stations dialog ────────────────────────────────────────────────────────

class _SpyDialog:
    """Tabel-dialoog voor spy/numbers stations met sorteerbare kolommen en actief-filter."""

    _AMBER = "#FFA726"
    # (kolomlabel, sort-sleutel, breedte)
    _COLS = [
        ("●",      "_active", 28),
        ("Naam",   "name",   220),
        ("Land",   "country",150),
        ("Freq.",  "freq",   160),
        ("Mode",   "mode",    60),
    ]

    def __init__(self, root: tk.Tk, stations: list):
        self._root      = root
        self._stations  = stations
        self._win: tk.Toplevel | None = None
        self._filter_var: tk.StringVar | None  = None
        self._active_var: tk.StringVar | None  = None
        self._tbl:  tk.Frame | None = None
        self._cvs:  tk.Canvas | None = None
        self._detail_var: tk.StringVar | None  = None
        self._hdr_btns: dict[str, tk.Button]   = {}
        self._sort_col  = "name"
        self._sort_asc  = True

    # ── helpers ───────────────────────────────────────────────────────────────

    def _bind_scroll(self, widget, handler):
        widget.bind("<MouseWheel>", handler)
        widget.bind("<Button-4>",   handler)
        widget.bind("<Button-5>",   handler)
        for child in widget.winfo_children():
            self._bind_scroll(child, handler)

    def _sort_key(self, st: dict) -> str:
        k = self._sort_col
        if k == "_active":
            return "0" if st.get("active") else "1"
        if k == "freq":
            freqs = st.get("frequencies", [])
            return freqs[0] if freqs else ""
        return st.get(k, "").lower()

    def _filtered(self) -> list:
        q    = (self._filter_var.get() if self._filter_var else "").lower().strip()
        show = (self._active_var.get() if self._active_var else "alle")
        out  = []
        for s in self._stations:
            active = s.get("active", False)
            if show == "actief"   and not active: continue
            if show == "inactief" and active:     continue
            if q and not (
                q in s.get("name",    "").lower() or
                q in s.get("country", "").lower() or
                any(q in f.lower() for f in s.get("frequencies", []))
            ):
                continue
            out.append(s)
        out.sort(key=self._sort_key, reverse=not self._sort_asc)
        return out

    def _refresh(self, *_):
        if self._tbl:
            self._build_table()

    def _set_sort(self, col: str):
        if self._sort_col == col:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_col = col
            self._sort_asc = True
        self._update_hdr_labels()
        self._build_table()

    def _update_hdr_labels(self):
        for col_lbl, col_key, _ in self._COLS:
            btn = self._hdr_btns.get(col_key)
            if btn is None:
                continue
            if col_key == self._sort_col:
                arrow = " ↑" if self._sort_asc else " ↓"
                btn.config(text=col_lbl + arrow, fg=self._AMBER)
            else:
                btn.config(text=col_lbl, fg=ACCENT)

    def _build_table(self):
        tbl = self._tbl
        for w in tbl.winfo_children():
            w.destroy()

        rows = self._filtered()
        if not rows:
            tk.Label(tbl, text="Geen resultaten.", font=_font(9),
                     bg=BG_SURFACE, fg=TEXT_DIM
                     ).grid(row=0, column=0, columnspan=len(self._COLS),
                            padx=12, pady=8, sticky='w')
        else:
            for ri, st in enumerate(rows):
                row_bg = BG_SURFACE if ri % 2 == 0 else BG_PANEL
                active = st.get("active", False)
                info     = st.get("info", "")
                schedule = st.get("schedule", "")
                detail   = (f"{info}\n\n🕐 Schema: {schedule}"
                            if info and schedule else info or schedule or "—")
                freq_str = " · ".join(st.get("frequencies", []))
                vals = [
                    ("●",                       _font(9, "bold"), "#66BB6A" if active else "#EF5350"),
                    (st.get("name",    ""),      _font(9),        TEXT_H1),
                    (st.get("country", ""),      _font(9),        TEXT_BODY),
                    (freq_str,                   _font(8),        self._AMBER),
                    (st.get("mode",    ""),      _font(8),        TEXT_DIM),
                ]
                for ci, (txt, fnt, fg) in enumerate(vals):
                    lbl = tk.Label(tbl, text=txt, font=fnt, bg=row_bg,
                                   fg=fg, anchor='w', padx=4, pady=2)
                    lbl.grid(row=ri, column=ci, sticky='ew')
                    lbl.bind("<Enter>", lambda _, d=detail: self._detail_var.set(d))
                    lbl.bind("<Leave>", lambda _: self._detail_var.set(
                        "Beweeg de muis over een rij voor meer informatie."))

        for ci, (_, _, w) in enumerate(self._COLS):
            tbl.columnconfigure(ci, minsize=w)

        tbl.update_idletasks()
        self._cvs.config(scrollregion=self._cvs.bbox("all"))
        scroll_h = lambda e: self._cvs.yview_scroll(
            -1 if (e.delta > 0 or e.num == 4) else 1, "units")
        self._bind_scroll(tbl, scroll_h)

    # ── public ────────────────────────────────────────────────────────────────

    def show(self):
        if self._win and self._win.winfo_exists():
            self._win.lift()
            return

        win = tk.Toplevel(self._root)
        self._win = win
        win.title("Spy / Numbers Stations")
        win.configure(bg=BG_PANEL)
        win.geometry("700x620")
        win.update()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        ww = win.winfo_width()  or 700
        wh = win.winfo_height() or 620
        win.geometry(f"+{(sw-ww)//2}+{(sh-wh)//2}")
        win.resizable(True, True)

        tk.Frame(win, bg=self._AMBER, height=2).pack(fill=tk.X)
        tk.Label(win, text="🕵  Spy / Numbers Stations",
                 font=_font(11, "bold"), bg=BG_PANEL,
                 fg=self._AMBER, pady=6).pack(anchor='w', padx=12)

        # ── Toolbar ───────────────────────────────────────────────────────────
        toolbar = tk.Frame(win, bg=BG_PANEL)
        toolbar.pack(fill=tk.X, padx=10, pady=(0, 4))

        # Text filter
        tk.Label(toolbar, text="Zoek:", font=_font(9),
                 bg=BG_PANEL, fg=TEXT_DIM).pack(side=tk.LEFT)
        self._filter_var = tk.StringVar()
        tk.Entry(toolbar, textvariable=self._filter_var,
                 font=_font(9), bg=BG_SURFACE, fg=TEXT_H1,
                 insertbackground=TEXT_H1, relief=tk.FLAT, width=20
                 ).pack(side=tk.LEFT, padx=(4, 16))
        self._filter_var.trace_add("write", self._refresh)

        # Active/inactive filter
        tk.Label(toolbar, text="Toon:", font=_font(9),
                 bg=BG_PANEL, fg=TEXT_DIM).pack(side=tk.LEFT)
        self._active_var = tk.StringVar(value="alle")
        for val, lbl in [("alle", "Alle"), ("actief", "Actief"), ("inactief", "Inactief")]:
            tk.Radiobutton(toolbar, text=lbl, variable=self._active_var,
                           value=val, command=self._refresh,
                           font=_font(9), bg=BG_PANEL, fg=TEXT_BODY,
                           selectcolor=BG_SURFACE, activebackground=BG_PANEL,
                           activeforeground=TEXT_H1
                           ).pack(side=tk.LEFT, padx=(4, 0))

        # ── Column headers ────────────────────────────────────────────────────
        hdr_frame = tk.Frame(win, bg=BG_SURFACE)
        hdr_frame.pack(fill=tk.X, padx=10)
        self._hdr_btns = {}
        for ci, (col_lbl, col_key, col_w) in enumerate(self._COLS):
            btn = tk.Button(hdr_frame, text=col_lbl,
                            font=_font(8, "bold"),
                            bg=BG_SURFACE, fg=ACCENT,
                            relief=tk.FLAT, anchor='w', padx=4,
                            cursor="hand2",
                            command=lambda k=col_key: self._set_sort(k))
            btn.grid(row=0, column=ci, sticky='ew', ipady=3)
            hdr_frame.columnconfigure(ci, minsize=col_w)
            self._hdr_btns[col_key] = btn
        tk.Frame(hdr_frame, bg=BORDER, height=1).grid(
            row=1, column=0, columnspan=len(self._COLS), sticky='ew')
        self._update_hdr_labels()

        # ── Scrollable table ──────────────────────────────────────────────────
        frm = tk.Frame(win, bg=BG_PANEL)
        frm.pack(fill=tk.BOTH, expand=True, padx=10)
        sb = tk.Scrollbar(frm)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        cvs = tk.Canvas(frm, bg=BG_SURFACE, highlightthickness=0,
                        yscrollcommand=sb.set)
        cvs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.config(command=cvs.yview)
        self._cvs = cvs

        tbl = tk.Frame(cvs, bg=BG_SURFACE)
        cvs.create_window((0, 0), window=tbl, anchor='nw')
        tbl.bind("<Configure>",
                 lambda _: cvs.config(scrollregion=cvs.bbox("all")))
        self._tbl = tbl
        self._build_table()

        # ── Detail panel ──────────────────────────────────────────────────────
        tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X, pady=(4, 0))
        self._detail_var = tk.StringVar(value="Beweeg de muis over een rij voor meer informatie.")
        tk.Label(win, textvariable=self._detail_var,
                 font=_font(8), bg=BG_PANEL, fg=TEXT_H1,
                 anchor='w', wraplength=660, justify=tk.LEFT, pady=4
                 ).pack(fill=tk.X, padx=12)

        # ── Bottom bar ────────────────────────────────────────────────────────
        tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X)
        btn_row = tk.Frame(win, bg=BG_PANEL)
        btn_row.pack(fill=tk.X, padx=10, pady=6)
        tk.Label(btn_row, text=f"{len(self._stations)} stations  ·  hamios_spy_stations.json",
                 font=_font(8), bg=BG_PANEL, fg=TEXT_DIM).pack(side=tk.LEFT)
        tk.Button(btn_row, text="Close",
                  command=win.destroy,
                  font=_font(9), bg=BG_SURFACE, fg=self._AMBER,
                  relief=tk.FLAT, padx=12, cursor="hand2"
                  ).pack(side=tk.RIGHT)


# ── Satellite selection dialog ─────────────────────────────────────────────────
class _SatelliteDialog:
    """Satellite selection dialog with two checkboxes per satellite.

    Column 1 (●): show position dot on map.
    Column 2 (~): show orbital path (−1h … +12h). Disabled when ● is off.
    """

    def __init__(self, root: tk.Tk, tle_data: dict,
                 selected: set, path_selected: set, fp_selected: set,
                 on_close, app_ref=None):
        self._root         = root
        self._tle          = tle_data
        self._sel          = set(selected)
        self._path_sel     = set(path_selected)
        self._fp_sel       = set(fp_selected)
        self._on_close     = on_close
        self._app_ref      = app_ref   # HAMIOSApp ref for hours settings
        self._pos_vars:  dict[str, tk.BooleanVar] = {}
        self._path_vars: dict[str, tk.BooleanVar] = {}
        self._fp_vars:   dict[str, tk.BooleanVar] = {}
        self._path_cbs:  dict[str, tk.Checkbutton] = {}
        self._fp_cbs:    dict[str, tk.Checkbutton] = {}
        self._status_var = None
        self._refresh_btn: tk.Button | None = None
        self._cat_var: tk.StringVar | None = None
        self._win: tk.Toplevel | None = None

    # ── helpers ───────────────────────────────────────────────────────────────
    def _bind_scroll(self, widget, handler):
        """Recursively bind MouseWheel on widget and all children."""
        widget.bind("<MouseWheel>", handler)
        widget.bind("<Button-4>",   handler)
        widget.bind("<Button-5>",   handler)
        for child in widget.winfo_children():
            self._bind_scroll(child, handler)

    def _build_table(self, tbl, cvs):
        """(Re)build satellite rows inside tbl. Clears old widgets first."""
        for w in tbl.winfo_children():
            w.destroy()

        C_NAME = 220
        C_CB   = 72
        tbl.columnconfigure(0, minsize=C_NAME)
        for c in range(1, 4):
            tbl.columnconfigure(c, minsize=C_CB)

        # Column headers
        for col, txt in enumerate(["Satelliet", "Positie", "Path", "Footprint"]):
            tk.Label(tbl, text=txt, font=_font(8, "bold"),
                     bg=BG_SURFACE, fg=ACCENT, anchor='center'
                     ).grid(row=0, column=col, sticky='ew',
                            padx=(6 if col == 0 else 0, 0), pady=(4, 2))
        tk.Frame(tbl, bg=BORDER, height=1).grid(
            row=1, column=0, columnspan=4, sticky='ew', pady=(0, 2))

        self._pos_vars  = {}
        self._path_vars = {}
        self._fp_vars   = {}
        self._path_cbs  = {}
        self._fp_cbs    = {}

        cat_filter = self._cat_var.get() if self._cat_var else "All"

        grid_row = 2
        for group, sats in sorted(self._tle.items()):
            if cat_filter != "All" and group != cat_filter:
                continue
            tk.Label(tbl, text=f"  {group}", font=_font(9, "bold"),
                     bg=BG_SURFACE, fg=ACCENT, anchor='w'
                     ).grid(row=grid_row, column=0, columnspan=4,
                            sticky='w', pady=(6, 1), padx=4)
            grid_row += 1

            for name, _l1, _l2 in sorted(sats, key=lambda x: x[0]):
                dep = tk.NORMAL if name in self._sel else tk.DISABLED

                tk.Label(tbl, text=name, bg=BG_SURFACE,
                         fg=TEXT_BODY, font=_font(8), anchor='w'
                         ).grid(row=grid_row, column=0, sticky='w', padx=(8, 0))

                pv = tk.BooleanVar(value=name in self._sel)
                self._pos_vars[name] = pv
                tk.Checkbutton(tbl, variable=pv, text="",
                               command=lambda n=name, v=pv: self._toggle_pos(n, v),
                               bg=BG_SURFACE, fg=TEXT_H1,
                               selectcolor="#505560",
                               activebackground=BG_SURFACE,
                               activeforeground=TEXT_H1,
                               state=tk.NORMAL
                               ).grid(row=grid_row, column=1)

                pathv = tk.BooleanVar(value=name in self._path_sel)
                self._path_vars[name] = pathv
                pcb = tk.Checkbutton(tbl, variable=pathv, text="",
                                     command=lambda n=name, v=pathv: self._toggle_path(n, v),
                                     bg=BG_SURFACE, fg=TEXT_H1,
                                     selectcolor="#505560",
                                     disabledforeground=TEXT_DIM,
                                     activebackground=BG_SURFACE,
                                     activeforeground=TEXT_H1,
                                     state=dep)
                pcb.grid(row=grid_row, column=2)
                self._path_cbs[name] = pcb

                fpv = tk.BooleanVar(value=name in self._fp_sel)
                self._fp_vars[name] = fpv
                fpcb = tk.Checkbutton(tbl, variable=fpv, text="",
                                      command=lambda n=name, v=fpv: self._toggle_fp(n, v),
                                      bg=BG_SURFACE, fg=TEXT_H1,
                                      selectcolor="#505560",
                                      disabledforeground=TEXT_DIM,
                                      activebackground=BG_SURFACE,
                                      activeforeground=TEXT_H1,
                                      state=dep)
                fpcb.grid(row=grid_row, column=3)
                self._fp_cbs[name] = fpcb
                grid_row += 1

        # Bind scrollwheel on every widget so cursor position doesn't matter
        scroll_h = lambda e: cvs.yview_scroll(
            -1 if (e.delta > 0 or e.num == 4) else 1, "units")
        self._bind_scroll(tbl, scroll_h)
        tbl.update_idletasks()
        cvs.config(scrollregion=cvs.bbox("all"))

    # ── public ────────────────────────────────────────────────────────────────
    def show(self, selected: set = None, path_sel: set = None,
             fp_sel: set = None):
        """Open dialog (or re-sync if already open). Always reflects current state."""
        if selected  is not None: self._sel      = set(selected)
        if path_sel  is not None: self._path_sel = set(path_sel)
        if fp_sel    is not None: self._fp_sel   = set(fp_sel)

        if self._win and self._win.winfo_exists():
            self._build_table(self._tbl, self._cvs)
            self._win.lift()
            return

        win = tk.Toplevel(self._root)
        self._win = win
        win.title("Satellite Tracking")
        win.configure(bg=BG_PANEL)
        win.geometry("560x580")
        win.update()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        ww = win.winfo_width()  or 560
        wh = win.winfo_height() or 580
        win.geometry(f"+{(sw-ww)//2}+{(sh-wh)//2}")
        win.resizable(True, True)

        tk.Frame(win, bg=ACCENT, height=2).pack(fill=tk.X)
        tk.Label(win, text="🛰  Satellite Tracking",
                 font=_font(11, "bold"), bg=BG_PANEL,
                 fg=ACCENT, pady=6).pack(anchor='w', padx=12)

        # Category filter
        self._cat_var = tk.StringVar(value="All")
        cat_row = tk.Frame(win, bg=BG_PANEL)
        cat_row.pack(fill=tk.X, padx=10, pady=(0, 4))
        tk.Label(cat_row, text="Categorie:", font=_font(9),
                 bg=BG_PANEL, fg=TEXT_DIM).pack(side=tk.LEFT)
        categories = ["All"] + sorted(self._tle.keys())
        for cat in categories:
            tk.Radiobutton(cat_row, text=cat, variable=self._cat_var,
                           value=cat,
                           command=lambda: self._build_table(self._tbl, self._cvs),
                           font=_font(9), bg=BG_PANEL, fg=TEXT_BODY,
                           selectcolor=BG_SURFACE, activebackground=BG_PANEL,
                           activeforeground=TEXT_H1
                           ).pack(side=tk.LEFT, padx=(4, 0))

        frm = tk.Frame(win, bg=BG_PANEL)
        frm.pack(fill=tk.BOTH, expand=True, padx=10)
        sb = tk.Scrollbar(frm)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        cvs = tk.Canvas(frm, bg=BG_SURFACE, highlightthickness=0,
                        yscrollcommand=sb.set)
        cvs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.config(command=cvs.yview)

        tbl = tk.Frame(cvs, bg=BG_SURFACE)
        cvs.create_window((0, 0), window=tbl, anchor='nw')
        tbl.bind("<Configure>",
                 lambda _: cvs.config(scrollregion=cvs.bbox("all")))

        self._tbl = tbl
        self._cvs = cvs
        self._build_table(tbl, cvs)

        # Hours controls
        tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X, pady=(4, 0))
        hrs_row = tk.Frame(win, bg=BG_PANEL)
        hrs_row.pack(fill=tk.X, padx=10, pady=(4, 0))

        def _make_hours(parent, label, initial, on_change):
            tk.Label(parent, text=label, font=_font(8), bg=BG_PANEL,
                     fg=TEXT_DIM).pack(side=tk.LEFT)
            var = tk.IntVar(value=initial)
            sb = tk.Spinbox(parent, from_=1, to=24, width=3,
                            textvariable=var,
                            command=lambda: on_change(var.get()),
                            bg=BG_SURFACE, fg=TEXT_H1,
                            buttonbackground=BG_SURFACE,
                            relief=tk.FLAT, font=_font(9, "bold"))
            sb.bind("<Return>",    lambda _: on_change(var.get()))
            sb.bind("<FocusOut>",  lambda _: on_change(var.get()))
            sb.pack(side=tk.LEFT, padx=(2, 12))
            return var

        self._back_h_var = _make_hours(
            hrs_row, "Verleden (uur):", self._app_ref._sat_back_h,
            lambda v: self._set_hours(v, "back"))
        self._fwd_h_var = _make_hours(
            hrs_row, "Toekomst (uur):", self._app_ref._sat_fwd_h,
            lambda v: self._set_hours(v, "fwd"))

        # Waarschuwing als satelliet-overlay uitstaat
        warn_frame = tk.Frame(win, bg=BG_PANEL)
        warn_frame.pack(fill=tk.X, padx=10, pady=(0, 2))
        if self._app_ref and not self._app_ref._show_sat_var.get():
            tk.Label(warn_frame,
                     text="⚠  Satelliet-overlay staat UIT in Overlay-instellingen",
                     font=_font(8), bg=BG_PANEL, fg="#FFA726",
                     anchor='w').pack(fill=tk.X)

        # Bottom bar
        tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X, pady=(4, 0))
        btn_row = tk.Frame(win, bg=BG_PANEL)
        btn_row.pack(fill=tk.X, padx=10, pady=6)

        tk.Button(btn_row, text="Clear all",
                  command=self._clear,
                  font=_font(9), bg=BG_SURFACE, fg="#FFA726",
                  relief=tk.FLAT, padx=8, cursor="hand2"
                  ).pack(side=tk.LEFT)
        self._refresh_btn = tk.Button(btn_row, text="↻  TLE",
                  command=self._refresh_tle,
                  font=_font(9), bg=BG_SURFACE, fg="#FFA726",
                  relief=tk.FLAT, padx=8, cursor="hand2")
        self._refresh_btn.pack(side=tk.LEFT, padx=(6, 0))
        self._status_var = tk.StringVar(value=self._status_text())
        tk.Label(btn_row, textvariable=self._status_var,
                 font=_font(8), bg=BG_PANEL,
                 fg=TEXT_DIM).pack(side=tk.LEFT, padx=(8, 0))
        tk.Button(btn_row, text="Close",
                  command=self._close,
                  font=_font(9), bg=BG_SURFACE, fg="#FFA726",
                  relief=tk.FLAT, padx=12, cursor="hand2"
                  ).pack(side=tk.RIGHT)

    def _status_text(self):
        p = len(self._sel); pa = len(self._path_sel); fp = len(self._fp_sel)
        return (f"{p} pos  ·  {pa} path  ·  {fp} footprint")

    def _update_status(self):
        if self._status_var:
            self._status_var.set(self._status_text())

    def _toggle_pos(self, name: str, var: tk.BooleanVar):
        if var.get():
            self._sel.add(name)
            for cb_dict in (self._path_cbs, self._fp_cbs):
                if name in cb_dict:
                    cb_dict[name].config(state=tk.NORMAL, fg=TEXT_BODY)
        else:
            self._sel.discard(name)
            for v_dict, s_set, cb_dict in (
                    (self._path_vars, self._path_sel, self._path_cbs),
                    (self._fp_vars,   self._fp_sel,   self._fp_cbs)):
                if name in v_dict:
                    v_dict[name].set(False)
                s_set.discard(name)
                if name in cb_dict:
                    cb_dict[name].config(state=tk.DISABLED, fg=TEXT_DIM)
        self._update_status()
        self._on_close(self._sel, self._path_sel, self._fp_sel)

    def _toggle_path(self, name: str, var: tk.BooleanVar):
        if var.get():
            self._path_sel.add(name)
        else:
            self._path_sel.discard(name)
        self._update_status()
        self._on_close(self._sel, self._path_sel, self._fp_sel)

    def _toggle_fp(self, name: str, var: tk.BooleanVar):
        if var.get():
            self._fp_sel.add(name)
        else:
            self._fp_sel.discard(name)
        self._update_status()
        self._on_close(self._sel, self._path_sel, self._fp_sel)

    def _clear(self):
        self._sel.clear(); self._path_sel.clear(); self._fp_sel.clear()
        for v in (*self._pos_vars.values(),
                  *self._path_vars.values(),
                  *self._fp_vars.values()):
            v.set(False)
        for cb in (*self._path_cbs.values(), *self._fp_cbs.values()):
            cb.config(state=tk.DISABLED, fg=TEXT_DIM)
        self._update_status()
        self._on_close(self._sel, self._path_sel, self._fp_sel)

    def _close(self):
        self._on_close(self._sel, self._path_sel, self._fp_sel)
        if self._win:
            self._win.destroy()

    def _set_hours(self, value: int, which: str):
        """Update path hours in the app and recompute paths."""
        if self._app_ref is None:
            return
        v = max(1, min(24, int(value)))
        if which == "back":
            self._app_ref._sat_back_h = v
        else:
            self._app_ref._sat_fwd_h = v
        self._app_ref._save_sat_ini()
        if self._app_ref._sat_path_sel:
            import threading as _thr
            _thr.Thread(target=self._app_ref._bg_sat_refresh,
                        daemon=True).start()

    def _refresh_tle(self):
        """Force-fetch fresh TLE from Celestrak and rebuild the satellite list."""
        if self._refresh_btn:
            self._refresh_btn.config(state=tk.DISABLED, text="Laden…", fg=TEXT_DIM)
        threading.Thread(target=self._do_refresh_tle, daemon=True).start()

    def _do_refresh_tle(self):
        cache = {}
        for group, url in _TLE_GROUPS.items():
            sats = _fetch_tle_group(group, url)
            if sats:
                cache[group] = [[n, l1, l2] for n, l1, l2 in sats]
            log.info("TLE refresh %s: %d satellites", group, len(sats))
        if cache:
            _save_tle_cache(cache)
        self._root.after(0, self._on_tle_done, cache)

    def _on_tle_done(self, cache: dict):
        if self._refresh_btn:
            self._refresh_btn.config(state=tk.NORMAL, text="↻  TLE", fg="#FFA726")
        if not cache:
            return
        if self._app_ref is not None:
            self._app_ref._tle_data = cache
        self._tle = {g: [(r[0], r[1], r[2]) for r in v] for g, v in cache.items()}
        if self._win and self._win.winfo_exists():
            self._build_table(self._tbl, self._cvs)


# ── Dependency-check bij opstarten ────────────────────────────────────────────

def _show_splash(root: tk.Tk) -> bool:
    """Splash screen bij opstarten: naam/versie, dependency-status, toon-vinkje.

    Leest 'show_splash' uit HAMIOS.ini. Toont altijd als er vereiste packages
    ontbreken, anders alleen als show_splash=True.
    Retourneert True = doorgaan, False = afsluiten.
    """
    import configparser as _cp

    # Lees show_splash direct uit INI (app nog niet gestart)
    _cfg = _cp.ConfigParser()
    _cfg.read(SETTINGS_FILE, encoding="utf-8")
    try:
        show_splash = _cfg.getboolean("App", "show_splash", fallback=True)
    except Exception:
        show_splash = True

    DEPS = [
        ("Pillow",           "pillow",            _PIL_OK,       True,
         "Kaartweergave, overlays, maanfase"),
        ("pystray",          "pystray",           _TRAY_OK,      False,
         "Systeem-tray icoon en notificaties"),
        ("pyserial",         "pyserial",          _SERIAL_OK,    False,
         "CAT-interface (rig control)"),
        ("websocket-client", "websocket-client",  _WEBSOCKET_OK, False,
         "Live blikseminslagen (Blitzortung)"),
    ]
    missing_required = [d for d in DEPS if not d[2] and d[3]]
    missing_optional = [d for d in DEPS if not d[2] and not d[3]]

    # Toon alleen als: splash aan ÓÓÓF vereiste dep ontbreekt
    if not show_splash and not missing_required:
        return True

    BG      = "#1A1C1F"
    BG_CARD = "#22252A"
    BG_DEP  = "#2A2E35"
    AMBER   = "#C8A84B"
    DIM     = "#606870"
    FG      = "#F0E6C8"

    win = tk.Toplevel(root)
    win.title("HAMIOS")
    win.configure(bg=BG)
    win.resizable(False, False)
    win.attributes("-topmost", True)
    win.grab_set()
    win.focus_force()

    result    = [True]
    splash_var = tk.BooleanVar(value=show_splash)

    def _save_splash_pref():
        """Sla splash-voorkeur direct op in INI."""
        try:
            cfg2 = _cp.ConfigParser()
            cfg2.read(SETTINGS_FILE, encoding="utf-8")
            if not cfg2.has_section("App"):
                cfg2.add_section("App")
            cfg2.set("App", "show_splash", str(splash_var.get()))
            with open(SETTINGS_FILE, "w", encoding="utf-8") as _f:
                cfg2.write(_f)
        except Exception:
            pass

    # ── Amber top-balk ────────────────────────────────────────────────────────
    tk.Frame(win, bg=AMBER, height=3).pack(fill=tk.X)

    # ── App naam + versie ─────────────────────────────────────────────────────
    header = tk.Frame(win, bg=BG_CARD)
    header.pack(fill=tk.X)
    tk.Label(header, text="📡  HAMIOS",
             font=("Segoe UI", 22, "bold"), bg=BG_CARD, fg=AMBER,
             pady=10).pack(side=tk.LEFT, padx=20)
    ver_frame = tk.Frame(header, bg=BG_CARD)
    ver_frame.pack(side=tk.RIGHT, padx=20, pady=10)
    tk.Label(ver_frame, text=f"v{_APP_VERSION}",
             font=("Segoe UI", 14, "bold"), bg=BG_CARD, fg=AMBER,
             anchor='e').pack(anchor='e')
    tk.Label(ver_frame, text="HF Propagation & DX Monitor",
             font=("Segoe UI", 9), bg=BG_CARD, fg=DIM,
             anchor='e').pack(anchor='e')
    tk.Label(ver_frame, text="by Frank van Dijke · Claude AI",
             font=("Segoe UI", 8), bg=BG_CARD, fg=DIM,
             anchor='e').pack(anchor='e')

    tk.Frame(win, bg=AMBER, height=1).pack(fill=tk.X)

    # ── Dependencies ──────────────────────────────────────────────────────────
    tk.Label(win, text="📦  Dependencies",
             font=("Segoe UI", 9, "bold"), bg=BG, fg=AMBER,
             anchor='w').pack(fill=tk.X, padx=16, pady=(10, 4))

    dep_card = tk.Frame(win, bg=BG_DEP)
    dep_card.pack(fill=tk.X, padx=12, pady=(0, 6))

    for name, pkg, is_ok, required, desc in DEPS:
        row = tk.Frame(dep_card, bg=BG_DEP)
        row.pack(fill=tk.X, padx=8, pady=3)
        icon = "✅" if is_ok else "❌"
        iclr = "#66BB6A" if is_ok else ("#EF5350" if required else "#FFA726")
        tk.Label(row, text=icon, font=("Segoe UI", 10),
                 bg=BG_DEP, fg=iclr, width=3).pack(side=tk.LEFT)
        lbl_type = " [vereist]" if required else " [optioneel]"
        info = tk.Frame(row, bg=BG_DEP)
        info.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(info, text=f"{name}{lbl_type}",
                 font=("Segoe UI", 9, "bold"), bg=BG_DEP,
                 fg=FG if is_ok else iclr, anchor='w').pack(fill=tk.X)
        tk.Label(info, text=desc,
                 font=("Segoe UI", 8), bg=BG_DEP, fg=DIM,
                 anchor='w').pack(fill=tk.X)
        if not is_ok:
            cmd = f"  pip install {pkg}  "
            cmd_lbl = tk.Label(row, text=cmd,
                               font=("Consolas", 8), bg="#1A1C1F",
                               fg=AMBER, padx=6, pady=2, cursor="hand2",
                               relief=tk.GROOVE, bd=1)
            cmd_lbl.pack(side=tk.LEFT, padx=(8, 0))
            cmd_lbl.bind("<Button-1>",
                         lambda _, c=cmd: (root.clipboard_clear(),
                                           root.clipboard_append(c)))
            tk.Label(row, text="← kopieer",
                     font=("Segoe UI", 7), bg=BG_DEP, fg=DIM
                     ).pack(side=tk.LEFT, padx=(4, 0))

    # Samenvatting
    if missing_required:
        msg, mclr = (f"⚠️  {len(missing_required)} vereiste package(s) ontbreken.",
                     "#EF5350")
    elif missing_optional:
        msg, mclr = (f"ℹ️  {len(missing_optional)} optionele package(s) ontbreken — "
                     f"bijbehorende functies uitgeschakeld.", "#FFA726")
    else:
        msg, mclr = ("✅  Alle dependencies aanwezig.", "#66BB6A")

    tk.Label(win, text=msg, font=("Segoe UI", 8), bg=BG, fg=mclr,
             wraplength=440, justify=tk.LEFT).pack(anchor='w', padx=16, pady=(0, 6))

    # ── Onderste balk: vinkje + knoppen ──────────────────────────────────────
    tk.Frame(win, bg="#383E47", height=1).pack(fill=tk.X, padx=0)
    bottom = tk.Frame(win, bg=BG_CARD)
    bottom.pack(fill=tk.X, padx=0)

    # Vinkje
    cb = tk.Checkbutton(bottom, text="Toon dit scherm bij opstarten",
                        variable=splash_var,
                        command=_save_splash_pref,
                        bg=BG_CARD, fg=FG, selectcolor=BG_DEP,
                        activebackground=BG_CARD, activeforeground=FG,
                        font=("Segoe UI", 9))
    cb.pack(side=tk.LEFT, padx=14, pady=10)

    def _go():
        _save_splash_pref()
        result[0] = True
        win.destroy()

    def _quit():
        _save_splash_pref()
        result[0] = False
        win.destroy()

    if missing_required:
        tk.Button(bottom, text="Afsluiten", command=_quit,
                  font=("Segoe UI", 9), bg="#5A1010", fg=FG,
                  relief=tk.FLAT, padx=12, pady=4, cursor="hand2"
                  ).pack(side=tk.RIGHT, padx=(4, 14), pady=8)

    tk.Button(bottom, text="Doorgaan  →", command=_go,
              font=("Segoe UI", 9, "bold"), bg=AMBER, fg=BG,
              activebackground="#D4B050", activeforeground=BG,
              relief=tk.FLAT, padx=14, pady=4, cursor="hand2"
              ).pack(side=tk.RIGHT, padx=(14, 4), pady=8)

    # Centreer: gebruik winfo_reqwidth na update_idletasks (betrouwbaarder dan winfo_width)
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    ww = win.winfo_reqwidth()
    wh = win.winfo_reqheight()
    if ww < 10:   # fallback als nog niet berekend
        ww, wh = 480, 360
    x  = max(0, (sw - ww) // 2)
    y  = max(0, (sh - wh) // 2)
    win.geometry(f"+{x}+{y}")
    win.update_idletasks()
    win.attributes("-topmost", False)

    root.wait_window(win)
    return result[0]


# Alias voor achterwaartse compatibiliteit
def _check_and_show_dependencies(root: tk.Tk) -> bool:
    return _show_splash(root)


# ── Hoofd-GUI ──────────────────────────────────────────────────────────────────
class HAMIOSApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("HAMIOS v4.0.2")
        self.root.configure(bg=BG_ROOT)

        # Geometrie instellen vóór _build_ui — geen root.update() nodig, geen flicker.
        _scr_w = root.winfo_screenwidth()
        _scr_h = root.winfo_screenheight()
        _ini_w = min(1600, _scr_w - 60)
        _ini_h = min(1000, _scr_h - 60)
        _ini_x = (_scr_w - _ini_w) // 2
        _ini_y = max(0, (_scr_h - _ini_h) // 2)
        root.geometry(f"{_ini_w}x{_ini_h}+{_ini_x}+{_ini_y}")
        root.minsize(900, 600)
        root.resizable(True, True)   # v4: hoogte én breedte aanpasbaar

        self._solar_data: dict = {}
        self._solar_after_id = None
        self._clock_after_id = None
        # Help dialog (lazy-init; version check runs in background)
        self._help_dlg: _HelpDialog | None = None
        root.bind_all("<F1>", lambda _e: self._open_help())

        # Satellite tracking state
        self._tle_data:       dict = _load_tle_cache()
        self._sat_selected:   set  = set()
        self._sat_path_sel:   set  = set()   # show orbital path
        self._sat_fp_sel:     set  = set()   # show footprint
        self._sat_back_h:     int  = 1       # hours of past path
        self._sat_fwd_h:      int  = 12      # hours of future path
        self._sat_positions:     dict = {}   # name → (lat, lon, alt)
        self._sat_paths:         dict = {}   # name → (past_pts, fwd_pts)
        self._sat_path_hits:     list = []   # [(lat, lon, dt_str), ...]
        self._sat_tip_win: tk.Toplevel | None = None
        self._sat_dlg: _SatelliteDialog | None = None
        self._sat_after_id = None
        # Restore saved selections from INI (after s = _load_settings() above)
        self.root.after(10, self._load_sat_ini)

        # Spy stations
        self._spy_stations: list = _load_spy_stations()
        self._spy_dlg: _SpyDialog | None = None

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
        self._show_iaru_var     = tk.BooleanVar(value=False)  # ITU verwijderd; bewaard voor render_key compatibiliteit
        self._show_cs_var       = tk.BooleanVar(value=s["show_cs"])
        self._show_aurora_var        = tk.BooleanVar(value=s["show_aurora"])
        self._show_sat_var           = tk.BooleanVar(value=s.get("show_sat", True))
        self._show_sunmoon_path_var  = tk.BooleanVar(value=s.get("show_sunmoon_path", False))
        self._show_iono_var          = tk.BooleanVar(value=s.get("show_iono", False))
        self._show_lightning_var  = tk.BooleanVar(value=s.get("show_lightning", True))
        self._lightning_fade_min  = int(s.get("lightning_fade_min", _LIGHTNING_KEEP_MIN))
        self._show_splash_var    = tk.BooleanVar(value=s.get("show_splash",    True))
        self._bz_range_var       = tk.IntVar(value=40)
        self._lightning_strikes: list  = []   # [(lat, lon, datetime, energy), ...]
        self._storm_forecast:    dict  = {}   # {unix_ts: {code, cape, lift}}
        self._lightning_ws_running     = False
        self._lightning_reconnect_id   = None
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
        self._dx_own_cont_var       = tk.BooleanVar(value=s.get("dx_own_cont", True))
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
        # Legenda-selectie herstel: visuele widgets bestaan niet meer,
        # bandfilter blijft bewaard via _hist_sel en werkt via canvas-klik
        self._tick_clock()
        self._start_tray()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        threading.Thread(target=self._refresh_solar, daemon=True).start()
        if _WEBSOCKET_OK:
            self.root.after(2000, self._start_lightning_ws)
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
        # Start satellite position refresh loop
        self._schedule_sat_refresh()
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
        # Paneel-titelbalk teksten bijwerken
        self._update_panel_titles()
        # Settings-dialoog opnieuw opbouwen als die open is
        if getattr(self, "_settings_win", None) and self._settings_win.winfo_exists():
            self._settings_win.destroy()
            self._settings_win = None
            self.root.after(50, self._open_settings_dialog)

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

        # Aparte maps voor achtergrond- vs. voorgrondkleuren.
        # In HighContrast zijn TEXT_H1 en BORDER beide "#FFFFFF"; één gecombineerde
        # map zou de ene entry door de andere laten overschrijven waardoor tekst-
        # en kaderkleur verwisseld worden.  Door type te scheiden krijgt elke widget-
        # eigenschap de juiste nieuwe kleur.
        _BG_KEYS = ("BG_ROOT", "BG_PANEL", "BG_SURFACE", "BG_HOVER", "BORDER")
        _FG_KEYS = ("ACCENT", "TEXT_H1", "TEXT_BODY", "TEXT_DIM")

        bg_map = {prev[k].lower(): new[k] for k in _BG_KEYS
                  if prev[k].lower() != new[k].lower()}
        fg_map = {prev[k].lower(): new[k] for k in _FG_KEYS
                  if prev[k].lower() != new[k].lower()}

        def remap_bg(c: str) -> str:
            return bg_map.get(c.lower(), c) if c else c

        def remap_fg(c: str) -> str:
            return fg_map.get(c.lower(), c) if c else c

        def remap_act(c: str) -> str:
            """Active-/select-kleuren kunnen fg of bg zijn — probeer fg eerst."""
            lc = c.lower() if c else ""
            return fg_map.get(lc, bg_map.get(lc, c)) if c else c

        self.root.configure(bg=new["BG_ROOT"])

        def walk(widget):
            # Widget configureren en recursie in APARTE try-blokken zodat een
            # exception bij het configureren de kinderen niet overslaat.
            try:
                wc = widget.winfo_class()
                if wc in ("Frame", "Toplevel", "LabelFrame"):
                    widget.configure(bg=remap_bg(widget.cget("bg")))
                elif wc == "Label":
                    widget.configure(bg=remap_bg(widget.cget("bg")),
                                     fg=remap_fg(widget.cget("fg")))
                elif wc == "Button":
                    widget.configure(bg=remap_bg(widget.cget("bg")),
                                     fg=remap_fg(widget.cget("fg")),
                                     activebackground=remap_bg(widget.cget("activebackground")),
                                     activeforeground=remap_act(widget.cget("activeforeground")))
                elif wc in ("Checkbutton", "Radiobutton"):
                    widget.configure(bg=remap_bg(widget.cget("bg")),
                                     fg=remap_fg(widget.cget("fg")),
                                     selectcolor=remap_bg(widget.cget("selectcolor")),
                                     activebackground=remap_bg(widget.cget("activebackground")),
                                     activeforeground=remap_act(widget.cget("activeforeground")))
                elif wc in ("Menubutton", "Menu"):
                    widget.configure(bg=remap_bg(widget.cget("bg")),
                                     fg=remap_fg(widget.cget("fg")),
                                     activebackground=remap_bg(widget.cget("activebackground")),
                                     activeforeground=remap_act(widget.cget("activeforeground")))
                elif wc == "Canvas":
                    widget.configure(bg=remap_bg(widget.cget("bg")))
                elif wc == "Scrollbar":
                    widget.configure(bg=remap_bg(widget.cget("bg")),
                                     troughcolor=remap_bg(widget.cget("troughcolor")))
                elif wc == "Spinbox":
                    widget.configure(bg=remap_bg(widget.cget("bg")),
                                     fg=remap_fg(widget.cget("fg")),
                                     buttonbackground=remap_bg(widget.cget("buttonbackground")))
                elif wc in ("Entry", "Text"):
                    widget.configure(bg=remap_bg(widget.cget("bg")),
                                     fg=remap_fg(widget.cget("fg")),
                                     insertbackground=remap_fg(widget.cget("insertbackground")))
                elif wc == "Listbox":
                    widget.configure(bg=remap_bg(widget.cget("bg")),
                                     fg=remap_fg(widget.cget("fg")),
                                     selectbackground=remap_bg(widget.cget("selectbackground")),
                                     selectforeground=remap_fg(widget.cget("selectforeground")))
            except Exception:
                pass
            # Altijd recurseren, ook als het configureren van de widget zelf mislukte
            try:
                for child in widget.winfo_children():
                    walk(child)
            except Exception:
                pass

        walk(self.root)
        self._applied_theme_name = new_name

        # ── Module-globals bijwerken zodat alle herteken-code de juiste kleuren gebruikt ──
        global BG_ROOT, BG_PANEL, BG_SURFACE, BG_HOVER
        global ACCENT, TEXT_H1, TEXT_BODY, TEXT_DIM, BORDER
        BG_ROOT    = new["BG_ROOT"]
        BG_PANEL   = new["BG_PANEL"]
        BG_SURFACE = new["BG_SURFACE"]
        BG_HOVER   = new["BG_HOVER"]
        ACCENT     = new["ACCENT"]
        TEXT_H1    = new["TEXT_H1"]
        TEXT_BODY  = new["TEXT_BODY"]
        TEXT_DIM   = new["TEXT_DIM"]
        BORDER     = new["BORDER"]

        # ── Alle canvassen opnieuw tekenen met nieuwe kleuren ──
        self._map_base_size = None          # invalideert gecachede basiskaart
        self._map_render_key = None         # invalideert satelliet-overlay cache
        self.root.after(0, self._draw_map)
        self._draw_bz_graph(getattr(self, "_last_bz_pts", []))
        self._draw_kp_bars(getattr(self, "_last_kp_pts", []))
        self._draw_xray_graph(getattr(self, "_last_xray_pts", []))
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

    def _open_settings_dialog(self):
        """Instellingen-dialoog: QTH, taal, thema, tooltips, ticker, zomertijd."""
        if hasattr(self, "_settings_win") and self._settings_win and \
                self._settings_win.winfo_exists():
            self._settings_win.lift()
            return

        win = tk.Toplevel(self.root)
        self._settings_win = win
        win.title(self._tr("settings_title"))
        win.configure(bg=BG_PANEL)
        win.resizable(False, False)

        tk.Frame(win, bg=ACCENT, height=2).pack(fill=tk.X)
        tk.Label(win, text=self._tr("settings_title"), font=_font(11, "bold"),
                 bg=BG_PANEL, fg=ACCENT, pady=6).pack(anchor='w', padx=14)

        def section(parent, title):
            tk.Frame(parent, bg=BORDER, height=1).pack(fill=tk.X, padx=10, pady=(8, 4))
            tk.Label(parent, text=title, font=_font(8, "bold"),
                     bg=BG_PANEL, fg=ACCENT, anchor='w').pack(fill=tk.X, padx=12)

        def row(parent):
            f = tk.Frame(parent, bg=BG_PANEL)
            f.pack(fill=tk.X, padx=12, pady=2)
            return f

        # ── QTH ──────────────────────────────────────────────────────────────
        section(win, self._tr("settings_qth"))
        r = row(win)
        tk.Label(r, text=self._tr("qth_lat_lbl"), font=_font(9),
                 bg=BG_PANEL, fg=TEXT_DIM, width=10, anchor='w').pack(side=tk.LEFT)
        lat_e = tk.Entry(r, textvariable=self._qth_lat_var, width=9,
                         bg=BG_SURFACE, fg=TEXT_H1, insertbackground=TEXT_H1,
                         relief=tk.FLAT, font=_font(9))
        lat_e.pack(side=tk.LEFT, padx=(4, 12))
        lat_e.bind("<Return>",   self._apply_qth)
        lat_e.bind("<FocusOut>", self._apply_qth)
        tk.Label(r, text=self._tr("lon_lbl"), font=_font(9),
                 bg=BG_PANEL, fg=TEXT_DIM, anchor='w').pack(side=tk.LEFT)
        lon_e = tk.Entry(r, textvariable=self._qth_lon_var, width=10,
                         bg=BG_SURFACE, fg=TEXT_H1, insertbackground=TEXT_H1,
                         relief=tk.FLAT, font=_font(9))
        lon_e.pack(side=tk.LEFT, padx=(4, 0))
        lon_e.bind("<Return>",   self._apply_qth)
        lon_e.bind("<FocusOut>", self._apply_qth)

        # ── Interface ─────────────────────────────────────────────────────────
        section(win, self._tr("settings_iface"))

        # Taal
        r = row(win)
        tk.Label(r, text=self._tr("lang_lbl"), font=_font(9),
                 bg=BG_PANEL, fg=TEXT_DIM, width=10, anchor='w').pack(side=tk.LEFT)
        lang_mb = tk.Menubutton(r, textvariable=self._lang_var,
                                font=_font(9), bg=BG_SURFACE, fg=TEXT_H1,
                                relief=tk.FLAT, activebackground=BG_HOVER,
                                activeforeground=TEXT_H1, width=14,
                                anchor='w', padx=6, pady=2, cursor="hand2")
        lang_menu = tk.Menu(lang_mb, tearoff=False, bg=BG_SURFACE, fg=TEXT_H1,
                            activebackground=ACCENT, activeforeground=BG_ROOT,
                            font=_font(9))
        for name in _LANG_NAMES:
            lang_menu.add_command(label=name,
                                  command=lambda v=name: (self._lang_var.set(v),
                                                          self._on_lang_change()))
        lang_mb["menu"] = lang_menu
        lang_mb.pack(side=tk.LEFT, padx=(4, 0))

        # Thema
        r = row(win)
        tk.Label(r, text=self._tr("theme_lbl"),
                 font=_font(9), bg=BG_PANEL, fg=TEXT_DIM, width=10, anchor='w'
                 ).pack(side=tk.LEFT)
        theme_mb = tk.Menubutton(r, textvariable=self._theme_var,
                                 font=_font(9), bg=BG_SURFACE, fg=TEXT_H1,
                                 relief=tk.FLAT, activebackground=BG_HOVER,
                                 activeforeground=TEXT_H1, width=14,
                                 anchor='w', padx=6, pady=2, cursor="hand2")
        theme_menu = tk.Menu(theme_mb, tearoff=False, bg=BG_SURFACE, fg=TEXT_H1,
                             activebackground=ACCENT, activeforeground=BG_ROOT,
                             font=_font(9))
        for tname in THEMES.keys():
            theme_menu.add_command(label=tname,
                                   command=lambda v=tname: self._on_theme_change(v))
        theme_mb["menu"] = theme_menu
        theme_mb.pack(side=tk.LEFT, padx=(4, 0))

        # Zomertijd
        r = row(win)
        tk.Checkbutton(r, text=self._tr("summer_time"),
                       variable=self._dst_var, command=self._save_cur_settings,
                       bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                       activebackground=BG_PANEL, activeforeground=TEXT_H1,
                       font=_font(9)).pack(side=tk.LEFT)

        # Tooltips + Ticker
        r = row(win)
        tk.Checkbutton(r, text=self._tr("tooltips"), variable=self._show_tips_var,
                       command=self._save_cur_settings,
                       bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                       activebackground=BG_PANEL, activeforeground=TEXT_H1,
                       font=_font(9)).pack(side=tk.LEFT, padx=(0, 16))
        tk.Checkbutton(r, text=self._tr("ticker"), variable=self._ticker_enabled_var,
                       command=self._toggle_ticker,
                       bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                       activebackground=BG_PANEL, activeforeground=TEXT_H1,
                       font=_font(9)).pack(side=tk.LEFT)

        # ── Panelen ───────────────────────────────────────────────────────────
        section(win, self._tr("panels_btn"))
        panels_frame = tk.Frame(win, bg=BG_PANEL)
        panels_frame.pack(fill=tk.X, padx=12, pady=(2, 0))

        _PANEL_LABELS = {
            "band_rel":   ("prop_header",  "📶"),
            "worldmap":   ("worldmap",     "🗺"),
            "solar":      ("solar",        "☀"),
            "alerts":     ("alerts_hdr",   "🔔"),
            "band_sched": ("sched_header", "🗓"),
            "band_hist":  ("hist_header",  "📈"),
            "band_cond":  ("band_cond_hdr",  "📻"),
            "storm_fc":   ("storm_fc_hdr",   "🌩"),
            "solar_hist": ("solar_hist_hdr", "☀"),
            "kp_48h":     ("kp_chart_hdr", "🧲"),
            "bz_24h":     ("bz_chart_hdr",  "⚡"),
            "xray_24h":   ("xray_chart_hdr","☢"),
            "lightning":  ("lightning_hdr",  "⚡"),
            "dx_spots":   ("dx_header",     "📡"),
            "prop_adv":   ("adv_header",    "💡"),
        }
        col, max_col = 0, 2
        r = None
        for pid, (tr_key, icon) in _PANEL_LABELS.items():
            var = self._panel_vis_vars.get(pid)
            if var is None:
                continue
            if col % max_col == 0:
                r = tk.Frame(panels_frame, bg=BG_PANEL)
                r.pack(fill=tk.X, pady=1)
            lbl = self._tr(tr_key)   # vertaling bevat al emoji
            cb = tk.Checkbutton(r, text=lbl, variable=var,
                                command=lambda p=pid, v=var: (
                                    self._panels[p].show() if v.get()
                                    else self._panels[p].hide(),
                                    self._save_cur_settings()),
                                bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                                activebackground=BG_PANEL, activeforeground=TEXT_H1,
                                font=_font(9), anchor='w', width=22)
            cb.pack(side=tk.LEFT, padx=(0, 4))
            col += 1

        # ── Kaart kleuren ─────────────────────────────────────────────────────
        section(win, "🎨  Kaart kleuren")
        colors_row = row(win)

        def _pick_color(title, current_rgb, callback):
            from tkinter import colorchooser
            hex_cur = "#{:02x}{:02x}{:02x}".format(*current_rgb)
            result = colorchooser.askcolor(color=hex_cur, title=title, parent=win)
            if result and result[0]:
                r, g, b = (int(x) for x in result[0])
                callback((r, g, b))
                self._map_base_size = None
                self._map_render_key = None
                self.root.after(0, self._draw_map)

        def _grid_btn():
            global MAP_GRID
            _pick_color("Meridiaan kleur", MAP_GRID,
                        lambda c: globals().__setitem__("MAP_GRID", c)
                        or setattr(self, "_map_grid_color", c))

        def _ocean_btn():
            global MAP_OCEAN
            _pick_color("Oceaan kleur", MAP_OCEAN,
                        lambda c: globals().__setitem__("MAP_OCEAN", c))

        tk.Button(colors_row, text="Meridianen",
                  command=_grid_btn,
                  font=_font(9), bg=BG_SURFACE, fg="#FFA726",
                  relief=tk.FLAT, padx=8, pady=2, cursor="hand2"
                  ).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(colors_row, text="Oceaan",
                  command=_ocean_btn,
                  font=_font(9), bg=BG_SURFACE, fg="#FFA726",
                  relief=tk.FLAT, padx=8, pady=2, cursor="hand2"
                  ).pack(side=tk.LEFT)
        tk.Label(colors_row, text="(kleur wordt direct toegepast)",
                 font=_font(8), bg=BG_PANEL, fg=TEXT_DIM
                 ).pack(side=tk.LEFT, padx=(8, 0))

        # ── Layout ────────────────────────────────────────────────────────────
        section(win, self._tr("settings_layout"))

        layout_row = row(win)
        tk.Button(layout_row, text=self._tr("settings_reset_layout"),
                  command=self._reset_panel_layout,
                  font=_font(9), bg=BG_SURFACE, fg="#FFA726",
                  relief=tk.FLAT, padx=8, pady=2, cursor="hand2"
                  ).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(layout_row, text=self._tr("settings_save_default"),
                  command=self._save_as_default_layout,
                  font=_font(9), bg=BG_SURFACE, fg="#FFA726",
                  relief=tk.FLAT, padx=8, pady=2, cursor="hand2"
                  ).pack(side=tk.LEFT)

        # Snap-to-grid instelling
        grid_row = row(win)
        tk.Label(grid_row, text="Snap-raster (px):",
                 font=_font(9), bg=BG_PANEL, fg=TEXT_DIM,
                 width=16, anchor='w').pack(side=tk.LEFT)
        self._grid_var = tk.IntVar(value=_PANEL_GRID)
        def _on_grid_change(*_):
            global _PANEL_GRID
            try:
                _PANEL_GRID = max(1, min(20, self._grid_var.get()))
            except Exception:
                pass
        tk.Spinbox(grid_row, from_=1, to=20, width=4,
                   textvariable=self._grid_var,
                   command=_on_grid_change,
                   bg=BG_SURFACE, fg=TEXT_H1, buttonbackground=BG_SURFACE,
                   relief=tk.FLAT, font=_font(9)).pack(side=tk.LEFT, padx=(4, 0))
        self._grid_var.trace_add("write", _on_grid_change)

        # Profielen-lijst (dynamisch opgebouwd)
        section(win, self._tr("settings_profiles"))
        self._settings_profiles_frame = tk.Frame(win, bg=BG_PANEL)
        self._settings_profiles_frame.pack(fill=tk.X, padx=12, pady=(2, 4))
        self._settings_win_ref = win
        self._refresh_settings_profiles()

        # ── Dependencies ──────────────────────────────────────────────────────
        section(win, "📦  Dependencies")
        dep_frame = tk.Frame(win, bg=BG_PANEL)
        dep_frame.pack(fill=tk.X, padx=12, pady=(2, 0))

        DEPS_SETTINGS = [
            ("Pillow",           _PIL_OK,       True,  "pip install pillow"),
            ("pystray",          _TRAY_OK,      False, "pip install pystray"),
            ("pyserial",         _SERIAL_OK,    False, "pip install pyserial"),
            ("websocket-client", _WEBSOCKET_OK, False, "pip install websocket-client"),
        ]
        for pkg_name, is_ok, required, install_cmd in DEPS_SETTINGS:
            dr = tk.Frame(dep_frame, bg=BG_PANEL)
            dr.pack(fill=tk.X, pady=1)
            icon  = "✅" if is_ok else "❌"
            iclr  = "#66BB6A" if is_ok else ("#EF5350" if required else "#FFA726")
            tk.Label(dr, text=icon, font=_font(9),
                     bg=BG_PANEL, fg=iclr, width=3).pack(side=tk.LEFT)
            lbl_type = " [vereist]" if required else " [optioneel]"
            tk.Label(dr, text=f"{pkg_name}{lbl_type}",
                     font=_font(9), bg=BG_PANEL,
                     fg=TEXT_H1 if is_ok else iclr,
                     anchor='w').pack(side=tk.LEFT, padx=(0, 10))
            if not is_ok:
                cmd_lbl = tk.Label(dr, text=install_cmd,
                                   font=(_FONT_MONO, 8), bg=BG_SURFACE,
                                   fg=ACCENT, padx=6, pady=1, cursor="hand2")
                cmd_lbl.pack(side=tk.LEFT)
                cmd_lbl.bind("<Button-1>",
                             lambda _, c=install_cmd: (
                                 self.root.clipboard_clear(),
                                 self.root.clipboard_append(c)))
                tk.Label(dr, text="← kopieer", font=_font(7),
                         bg=BG_PANEL, fg=TEXT_DIM).pack(side=tk.LEFT, padx=(4, 0))

        # Splash-toggle
        tk.Frame(dep_frame, bg=BORDER, height=1).pack(fill=tk.X, pady=(6, 2))
        tk.Checkbutton(dep_frame,
                       text="Toon splash screen bij opstarten",
                       variable=self._show_splash_var,
                       command=self._save_cur_settings,
                       bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                       activebackground=BG_PANEL, activeforeground=TEXT_H1,
                       font=_font(9)).pack(anchor='w', pady=(0, 4))

        # ── Sluiten ───────────────────────────────────────────────────────────
        tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X, padx=10, pady=(8, 0))
        btn_row = tk.Frame(win, bg=BG_PANEL)
        btn_row.pack(fill=tk.X, padx=12, pady=8)
        tk.Button(btn_row, text=self._tr("close_lbl"), command=win.destroy,
                  font=_font(9), bg=BG_SURFACE, fg="#FFA726",
                  relief=tk.FLAT, padx=12, cursor="hand2").pack(side=tk.RIGHT)

        win.update_idletasks()
        rx = self.root.winfo_x() + (self.root.winfo_width()  - win.winfo_reqwidth())  // 2
        ry = self.root.winfo_y() + (self.root.winfo_height() - win.winfo_reqheight()) // 2
        win.geometry(f"+{max(0,rx)}+{max(0,ry)}")

    def _open_overlay_dialog(self):
        """Overlay-dialoog: alle kaart-overlays gegroepeerd in Display en Data."""
        if hasattr(self, "_overlay_win") and self._overlay_win and \
                self._overlay_win.winfo_exists():
            self._overlay_win.lift()
            return

        win = tk.Toplevel(self.root)
        self._overlay_win = win
        win.title(self._tr("overlay_btn"))
        win.configure(bg=BG_PANEL)
        win.resizable(False, False)

        tk.Frame(win, bg=ACCENT, height=2).pack(fill=tk.X)
        tk.Label(win, text=self._tr("overlay_btn"),
                 font=_font(11, "bold"), bg=BG_PANEL, fg=ACCENT,
                 pady=6).pack(anchor='w', padx=14)

        def _cb(parent, tr_key, var, desc=""):
            def _redraw():
                self._save_cur_settings()
                self._draw_map()
            row = tk.Frame(parent, bg=BG_PANEL)
            row.pack(fill=tk.X, pady=1)
            cb = tk.Checkbutton(row, text=self._tr(tr_key),
                                variable=var, command=_redraw,
                                bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                                activebackground=BG_PANEL, activeforeground=TEXT_H1,
                                font=_font(9), anchor='w', width=18)
            cb.pack(side=tk.LEFT)
            self._tr_widgets.setdefault(tr_key, [])
            if not isinstance(self._tr_widgets[tr_key], list):
                self._tr_widgets[tr_key] = [self._tr_widgets[tr_key]]
            self._tr_widgets[tr_key].append(cb)
            if desc:
                tk.Label(row, text=desc, font=_font(7), bg=BG_PANEL,
                         fg=TEXT_BODY, anchor='w').pack(side=tk.LEFT, padx=(4,0))

        def section(title):
            tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X, padx=10, pady=(6, 2))
            tk.Label(win, text=title, font=_font(8, "bold"),
                     bg=BG_PANEL, fg=ACCENT, anchor='w').pack(fill=tk.X, padx=12)

        # ── Display ───────────────────────────────────────────────────────────
        section(self._tr("map_display_lbl"))
        disp = tk.Frame(win, bg=BG_PANEL)
        disp.pack(fill=tk.X, padx=12, pady=(2, 0))
        for tr_key, var, desc in [
            ("sun",           self._show_sun_var,           "Geocentrische zonpositie op kaart"),
            ("moon",          self._show_moon_var,          "Maanpositie + fase-icoon"),
            ("map_pad_lbl",   self._show_sunmoon_path_var,  "24u traject van zon en maan"),
            ("graylijn",      self._show_graylijn_var,      "Overgangszone dag/nacht (~1000 km)"),
            ("map_aurora_lbl",self._show_aurora_var,        "Aurora-ovaal op basis van K-index"),
        ]:
            _cb(disp, tr_key, var, desc)

        # ── Data ──────────────────────────────────────────────────────────────
        section(self._tr("map_data_lbl"))
        data = tk.Frame(win, bg=BG_PANEL)
        data.pack(fill=tk.X, padx=12, pady=(2, 0))
        data_overlays = [
            ("map_sat_lbl",       self._show_sat_var,          "Posities geselecteerde satellieten"),
            ("map_wspr_lbl",      self._show_wspr_var,         "WSPR propagatiepaden (wspr.rocks)"),
            ("map_spots_lbl",     self._show_spots_var,        "Live DX-cluster spots"),
            ("map_cs_lbl",        self._show_cs_var,           "Callsign-prefix laag (~110 DXCC)"),
            ("locator",           self._show_locator_var,      "Maidenhead locatorraster 20°×10°"),
            ("map_iono_lbl",      self._show_iono_var,         "Ionosonde-stations (GIRO/LGDC)"),
            ("map_lightning_lbl", self._show_lightning_var,    "Live blikseminslagen (Blitzortung)"),
        ]
        for tr_key, var, desc in data_overlays:
            _cb(data, tr_key, var, desc)

        # ── Sluiten ───────────────────────────────────────────────────────────
        tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X, padx=10, pady=(8, 0))
        btn_row = tk.Frame(win, bg=BG_PANEL)
        btn_row.pack(fill=tk.X, padx=12, pady=6)
        tk.Button(btn_row, text=self._tr("close_lbl"), command=win.destroy,
                  font=_font(9), bg=BG_SURFACE, fg="#FFA726",
                  relief=tk.FLAT, padx=12, cursor="hand2").pack(side=tk.RIGHT)

        win.update_idletasks()
        rx = self.root.winfo_x() + (self.root.winfo_width()  - win.winfo_reqwidth())  // 2
        ry = self.root.winfo_y() + (self.root.winfo_height() - win.winfo_reqheight()) // 2
        win.geometry(f"+{max(0,rx)}+{max(0,ry)}")

    def _open_help(self, _event=None):
        """Open the Help / About dialog (F1 or header button)."""
        if self._help_dlg is None:
            self._help_dlg = _HelpDialog(self.root)
            # Version check in background so it doesn't block startup
            def _bg_check():
                tag, url = _check_latest_version()
                self.root.after(0, lambda: self._on_version_checked(tag, url))
            threading.Thread(target=_bg_check, daemon=True).start()
        self._help_dlg.show()

    def _on_version_checked(self, latest: str, url: str):
        if self._help_dlg:
            self._help_dlg._latest = latest
            self._help_dlg._url = url

    # ── Satellite tracking ────────────────────────────────────────────────────
    def _open_sat_dialog(self):
        """Open satellite selection dialog; fetch TLE if cache is empty."""
        if not self._tle_data:
            self._sat_btn.config(fg="#FFA726", text="🛰  Loading…")
            threading.Thread(target=self._fetch_all_tle, daemon=True).start()
        else:
            self._show_sat_dialog()

    def _fetch_all_tle(self):
        """Background: fetch TLE for all groups and open dialog."""
        cache = {}
        for group, url in _TLE_GROUPS.items():
            sats = _fetch_tle_group(group, url)
            if sats:
                cache[group] = [[n, l1, l2] for n, l1, l2 in sats]
            log.info("TLE %s: %d satellites", group, len(sats))
        if cache:
            _save_tle_cache(cache)
            self._tle_data = cache
        self.root.after(0, self._on_tle_loaded)

    def _on_tle_loaded(self):
        self._sat_btn.config(fg=TEXT_DIM, text="🛰  Sat")
        self._show_sat_dialog()

    def _open_spy_dialog(self):
        """Open spy/numbers stations dialog."""
        if self._spy_dlg is None or not (
                self._spy_dlg._win and self._spy_dlg._win.winfo_exists()):
            self._spy_dlg = _SpyDialog(self.root, self._spy_stations)
        self._spy_dlg.show()

    def _show_sat_dialog(self):
        tle = {g: [(r[0], r[1], r[2]) for r in v]
               for g, v in self._tle_data.items()}
        if self._sat_dlg is None or not (
                self._sat_dlg._win and self._sat_dlg._win.winfo_exists()):
            self._sat_dlg = _SatelliteDialog(
                self.root, tle,
                self._sat_selected, self._sat_path_sel, self._sat_fp_sel,
                self._on_sat_selection_change, app_ref=self)
        # Always pass current selections so dialog reflects INI/state correctly
        self._sat_dlg.show(
            selected=self._sat_selected,
            path_sel=self._sat_path_sel,
            fp_sel=self._sat_fp_sel)

    def _on_sat_selection_change(self, selected: set, path_sel: set,
                                 fp_sel: set):
        self._sat_selected  = set(selected)
        self._sat_path_sel  = set(path_sel)
        self._sat_fp_sel    = set(fp_sel)
        # Debounce: snel achter elkaar aangevinkte satellieten starten slechts
        # één achtergrond-berekening.  _save_sat_ini + _refresh zitten in de
        # thread zodat de main thread nooit blokkeert (ook niet door schijf-I/O
        # op OneDrive).
        if getattr(self, "_sat_change_id", None):
            self.root.after_cancel(self._sat_change_id)
        self._sat_change_id = self.root.after(
            150, lambda: threading.Thread(
                target=self._bg_sat_save_refresh, daemon=True).start())

    def _bg_sat_save_refresh(self):
        """Achtergrond: herbereken posities/paden → teken kaart → sla INI op.
        Volgorde is bewust: kaart-update mag niet wachten op trage OneDrive-write.
        """
        self._refresh_sat_positions()          # snel: posities berekenen
        self.root.after(0, self._draw_map)     # kaart updaten (main thread)
        self._save_sat_ini()                   # traag: OneDrive write (kan wachten)

    def _refresh_sat_positions(self):
        """Compute current positions and paths for selected satellites."""
        tle_lookup: dict[str, tuple[str, str]] = {}
        for sats in self._tle_data.values():
            for row in sats:
                tle_lookup[row[0]] = (row[1], row[2])

        # Positions (all selected satellites)
        pos: dict = {}
        for name in self._sat_selected:
            if name in tle_lookup:
                r = _sgp4_latlon(tle_lookup[name][0], tle_lookup[name][1])
                if r:
                    pos[name] = r
        self._sat_positions = pos

        # Paths (−1h past, +12h future, separate step sizes)
        paths: dict = {}
        for name in self._sat_path_sel:
            if name in tle_lookup:
                past, fwd = _calc_sat_path(
                    tle_lookup[name][0], tle_lookup[name][1],
                    back_min=self._sat_back_h * 60,
                    fwd_min=self._sat_fwd_h * 60,
                    back_step=1, fwd_step=0.5)
                paths[name] = (past, fwd)
        self._sat_paths = paths

        self._map_render_key = None
        self.root.after(0, self._update_sat_zone_label)

    def _update_sat_zone_label(self):
        """Bereken welke geselecteerde satellieten boven het QTH vliegen en
        update het label in het meldingen-paneel."""
        if not hasattr(self, "_sat_zone_var"):
            return
        R_EARTH   = 6371.0
        qth_lat_r = math.radians(getattr(self, "_qth_lat", 52.0))
        qth_lon_r = math.radians(getattr(self, "_qth_lon",  5.0))
        visible   = []
        for name, (flat, flon, falt) in getattr(self, "_sat_positions", {}).items():
            if falt <= 0:
                continue
            rho = math.acos(min(1.0, R_EARTH / (R_EARTH + falt)))
            lat0_r = math.radians(flat)
            lon0_r = math.radians(flon)
            dist = math.acos(min(1.0,
                math.sin(lat0_r) * math.sin(qth_lat_r) +
                math.cos(lat0_r) * math.cos(qth_lat_r) *
                math.cos(qth_lon_r - lon0_r)))
            if dist < rho:
                elev = math.degrees(math.asin(min(1.0,
                    (math.cos(dist) - R_EARTH / (R_EARTH + falt)) /
                    math.sin(rho))))
                short = name.split("(")[0].strip()
                visible.append(f"{short} ({elev:.0f}°)")
        if visible:
            self._sat_zone_var.set("\n".join(visible))
            self._sat_zone_lbl.config(fg="#66BB6A")
        else:
            self._sat_zone_var.set("—")
            self._sat_zone_lbl.config(fg=TEXT_DIM)

    # ── Satellite INI persistence ─────────────────────────────────────────────
    def _save_sat_ini(self):
        """Save satellite selections to HAMIOS.ini under [Satellites]."""
        import configparser as _cp
        cfg = _cp.ConfigParser()
        cfg.read(SETTINGS_FILE, encoding="utf-8")
        if "Satellites" not in cfg:
            cfg["Satellites"] = {}
        cfg["Satellites"]["selected"]  = ",".join(sorted(self._sat_selected))
        cfg["Satellites"]["path_sel"]  = ",".join(sorted(self._sat_path_sel))
        cfg["Satellites"]["fp_sel"]    = ",".join(sorted(self._sat_fp_sel))
        cfg["Satellites"]["back_h"]    = str(self._sat_back_h)
        cfg["Satellites"]["fwd_h"]     = str(self._sat_fwd_h)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            cfg.write(f)

    def _load_sat_ini(self):
        """Load satellite selections from HAMIOS.ini and trigger refresh."""
        import configparser as _cp
        cfg = _cp.ConfigParser()
        cfg.read(SETTINGS_FILE, encoding="utf-8")
        s = cfg["Satellites"] if "Satellites" in cfg else {}
        def _parse(key):
            raw = s.get(key, "")
            return set(x for x in raw.split(",") if x.strip())
        self._sat_selected = _parse("selected")
        self._sat_path_sel = _parse("path_sel")
        self._sat_fp_sel   = _parse("fp_sel")
        try: self._sat_back_h = int(s.get("back_h", "1"))
        except ValueError: self._sat_back_h = 1
        try: self._sat_fwd_h  = int(s.get("fwd_h",  "12"))
        except ValueError: self._sat_fwd_h  = 12
        # Immediately compute positions / paths if any selections were restored
        if self._sat_selected or self._sat_path_sel or self._sat_fp_sel:
            threading.Thread(target=self._bg_sat_refresh, daemon=True).start()

    def _schedule_sat_refresh(self):
        """Re-schedule satellite position refresh every 30 s."""
        if self._sat_selected or self._sat_path_sel:
            threading.Thread(target=self._bg_sat_refresh, daemon=True).start()
        self._sat_after_id = self.root.after(30_000, self._schedule_sat_refresh)

    def _bg_sat_refresh(self):
        """Refresh positions and paths in background thread."""
        self._refresh_sat_positions()
        self.root.after(0, self._draw_map)

    def _quit_app(self):
        """Gracefully shut down: stop tray, save settings, close window."""
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
        tk.Label(hdr, text="📡  HAMIOS v4.0.2",
                 font=_font(13, "bold"), bg=BG_PANEL, fg=ACCENT,
                 pady=8).pack(side=tk.LEFT, padx=10)

        # Offline indicator — zichtbaar als netwerkfout
        self._offline_lbl = tk.Label(hdr, text="⚠ OFFLINE",
                                     font=_font(9, "bold"), bg=BG_PANEL,
                                     fg="#EF5350", pady=8)
        # Nog niet gepack — verschijnt alleen bij netfout via _update_net_indicator()

        # Exit knop — wordt rechts gepacked na rechter items
        exit_btn = tk.Button(hdr, text=self._tr("exit"),
                             command=self._quit_app,
                             font=_font(9), bg="#5A1010", fg=TEXT_H1,
                             activebackground="#8B1A1A", activeforeground=TEXT_H1,
                             relief=tk.FLAT, padx=8, pady=2, cursor="hand2")
        self._tr_widgets["exit"] = exit_btn

        # Fullscreen-knop (wordt rechts gepacked na de rechter-kant items)
        self._fs_var = tk.BooleanVar(value=False)
        self._fs_btn = tk.Button(hdr, text="⛶",
                                  command=self._toggle_fullscreen,
                                  font=_font(10), bg=BG_SURFACE, fg=ACCENT,
                                  activebackground=BG_HOVER, activeforeground=TEXT_H1,
                                  relief=tk.FLAT, padx=7, pady=2, cursor="hand2")
        self.root.bind("<F11>", lambda _: self._toggle_fullscreen())
        self.root.bind("<Escape>", lambda _: (
            self._toggle_fullscreen() if self._fs_var.get() else None))

        # Panelen-zichtbaarheid wordt beheerd via het Instellingen-paneel
        self._panel_vis_vars: dict = {}

        # Instellingen-knop
        _settings_btn = tk.Button(hdr, text=self._tr("settings_btn"),
                  command=self._open_settings_dialog,
                  font=_font(9), bg=BG_SURFACE, fg="#FFA726",
                  activebackground=BG_HOVER, activeforeground=TEXT_H1,
                  relief=tk.FLAT, padx=8, pady=2, cursor="hand2")
        _settings_btn.pack(side=tk.LEFT, padx=(0, 4))
        self._tr_widgets["settings_btn"] = _settings_btn

        # Overlay-knop
        _overlay_btn = tk.Button(hdr, text=self._tr("overlay_btn"),
                  command=self._open_overlay_dialog,
                  font=_font(9), bg=BG_SURFACE, fg="#FFA726",
                  activebackground=BG_HOVER, activeforeground=TEXT_H1,
                  relief=tk.FLAT, padx=8, pady=2, cursor="hand2")
        _overlay_btn.pack(side=tk.LEFT, padx=(0, 6))
        self._tr_widgets["overlay_btn"] = _overlay_btn

        # Satellite button (always amber)
        self._sat_btn = tk.Button(hdr, text="🛰  Sat",
                                  command=self._open_sat_dialog,
                                  font=_font(9), bg=BG_SURFACE, fg="#FFA726",
                                  activebackground=BG_HOVER,
                                  activeforeground=TEXT_H1,
                                  relief=tk.FLAT, padx=8, pady=2,
                                  cursor="hand2")
        self._sat_btn.pack(side=tk.LEFT, padx=(0, 4))

        # Spy stations button
        tk.Button(hdr, text="🕵  Spy",
                  command=self._open_spy_dialog,
                  font=_font(9), bg=BG_SURFACE, fg="#FFA726",
                  activebackground=BG_HOVER, activeforeground=TEXT_H1,
                  relief=tk.FLAT, padx=8, pady=2,
                  cursor="hand2").pack(side=tk.LEFT, padx=(0, 6))

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
        # Fullscreen uiterst rechts
        self._fs_btn.pack(side=tk.RIGHT, padx=(2, 4))

        # Exit rechts van help, links van fullscreen
        exit_btn.pack(side=tk.RIGHT, padx=(0, 2))

        # Help direct voor exit
        tk.Button(hdr, text="?",
                  command=self._open_help,
                  font=_font(9), bg=BG_SURFACE, fg=ACCENT,
                  activebackground=BG_HOVER, activeforeground=TEXT_H1,
                  relief=tk.FLAT, padx=7, pady=2, cursor="hand2"
                  ).pack(side=tk.RIGHT, padx=(0, 2))

        tk.Frame(hdr, bg=BORDER, width=1).pack(side=tk.RIGHT, fill=tk.Y, pady=8)

        # Tijden rechts (UTC + lokaal)
        self._utc_var   = tk.StringVar()
        self._local_var = tk.StringVar()
        tk.Label(hdr, textvariable=self._utc_var,
                 font=_font(10), bg=BG_PANEL, fg=TEXT_DIM).pack(side=tk.RIGHT, padx=(0, 12))
        tk.Frame(hdr, bg=BORDER, width=1).pack(side=tk.RIGHT, fill=tk.Y, pady=8)
        tk.Label(hdr, textvariable=self._local_var,
                 font=_font(10, "bold"), bg=BG_PANEL, fg=TEXT_H1).pack(side=tk.RIGHT, padx=(0, 8))

        tk.Frame(hdr, bg=BORDER, width=1).pack(side=tk.RIGHT, fill=tk.Y, pady=8)

        # Refresh interval + countdown
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
        mb.pack(side=tk.RIGHT, padx=(0, 4))
        self._countdown_var = tk.StringVar(value="")
        tk.Label(hdr, textvariable=self._countdown_var,
                 font=_font(9), bg=BG_PANEL, fg=ACCENT).pack(side=tk.RIGHT, padx=(0, 4))
        auto_lbl = tk.Label(hdr, text=self._tr("auto_lbl"), font=_font(9),
                            bg=BG_PANEL, fg=TEXT_DIM)
        auto_lbl.pack(side=tk.RIGHT, padx=(4, 2))
        self._tr_widgets["auto_lbl"] = auto_lbl

        # Ticker onderaan (pack VOOR body zodat hij aan de onderkant blijft)
        self._build_ticker()

        # ── v4.0.1: Desktop — panelen via place() ─────────────────────────────
        self._desktop = tk.Frame(self.root, bg=BG_ROOT)
        self._desktop.pack(fill=tk.BOTH, expand=True)
        self._desktop.bind("<Button-1>",
                           lambda _: self.root.after(10, self._lift_all_panels))

        # Zorg dat panelen altijd vooraan blijven via periodieke lift
        def _keep_panels_front():
            if hasattr(self, "_panels"):
                for p in self._panels.values():
                    if p.is_visible():
                        try:
                            p.frame.lift()
                        except Exception:
                            pass
            self.root.after(2000, _keep_panels_front)
        self.root.after(2000, _keep_panels_front)

        _layout = _load_panel_layout()
        self._panels: dict = {}

        _PANEL_MAP = [
            ("band_rel",   "prop_header",  "📶", self._build_prop_panel),
            ("worldmap",   "worldmap",     "🗺",  self._build_map_panel),
            ("solar",      "solar",        "☀",  self._build_solar_panel),
            ("band_sched", "sched_header", "🗓",  self._build_schedule_panel),
            ("band_hist",  "hist_header",  "📈",  self._build_hist_panel),
            ("band_cond",  "band_cond_hdr",  "📻", self._build_band_cond_panel),
            ("storm_fc",   "storm_fc_hdr",   "🌩", self._build_storm_fc_panel),
            ("solar_hist", "solar_hist_hdr", "☀",  self._build_solar_hist_panel),
            ("kp_48h",     "kp_chart_hdr",  "🧲", self._build_kp_panel),
            ("alerts",     "alerts_hdr",    "🔔", self._build_alerts_panel),
            ("bz_24h",     "bz_chart_hdr",  "⚡", self._build_bz_panel_only),
            ("xray_24h",   "xray_chart_hdr","☢",  self._build_xray_panel_only),
            ("lightning",  "lightning_hdr", "⚡", self._build_lightning_panel),
            ("dx_spots",   "dx_header",     "📡", self._build_dx_spots_panel),
            ("prop_adv",   "adv_header",  "💡",  self._build_advice_panel),
        ]
        for pid, tr_key, icon, build_fn in _PANEL_MAP:
            x, y, w, h, vis = _layout.get(pid, _PANEL_DEFAULTS.get(pid, (0, 0, 300, 200, True)))
            p = DraggablePanel(
                self._desktop, self._tr(tr_key), icon,
                panel_id=pid, on_vis_change=self._on_panel_vis_change,
                on_release=self._deferred_redraw
            )
            p.place(x, y, w, h)
            build_fn(p.content)
            if not vis:
                p.hide()
            self._panels[pid] = p
            # Zichtbaarheid-var (gedeeld met settings-dialoog)
            var = tk.BooleanVar(value=vis)
            self._panel_vis_vars[pid] = var

    # ── Solar paneel wrapper ──────────────────────────────────────────────────
    def _build_solar_panel(self, parent):
        """Solar/Ionosfeer paneel — wrapper rondom _build_solar_section."""
        self._build_solar_section(parent)

    # ── Fullscreen ────────────────────────────────────────────────────────────
    def _toggle_fullscreen(self):
        fs = not self._fs_var.get()
        self._fs_var.set(fs)
        if _IS_WIN:
            self.root.state("zoomed" if fs else "normal")
        else:
            self.root.attributes("-fullscreen", fs)
        self._fs_btn.config(text="⊡" if fs else "⛶")

    # ── Paneel-zichtbaarheid callback ────────────────────────────────────────
    # ── Performance: debounce helper ─────────────────────────────────────────
    def _debounce(self, key: str, ms: int, fn):
        """Plan fn ms milliseconden na de laatste aanroep (annuleer eerdere)."""
        attr = f"_deb_{key}"
        old = getattr(self, attr, None)
        if old:
            try:
                self.root.after_cancel(old)
            except Exception:
                pass
        setattr(self, attr, self.root.after(ms, fn))

    def _deferred_redraw(self):
        """Herteken alle canvassen na drag/resize-einde."""
        self._draw_map()
        self._draw_bz_graph(getattr(self, "_last_bz_pts", []))
        self._draw_kp_bars(getattr(self, "_last_kp_pts", []))
        self._draw_xray_graph(getattr(self, "_last_xray_pts", []))
        self._draw_hist_graph()
        self._draw_solar_hist_chart()
        self._draw_schedule()
        if hasattr(self, "_last_band_pct") and self._last_band_pct:
            self._draw_prop_bars(self._last_band_pct)

    def _on_panel_vis_change(self, panel_id: str, visible: bool):
        var = self._panel_vis_vars.get(panel_id)
        if var:
            var.set(visible)
        self._save_cur_settings()

    def _lift_all_panels(self):
        """Breng alle panelen naar voren."""
        for p in self._panels.values():
            if p.is_visible():
                try:
                    p.frame.lift()
                except Exception:
                    pass

    def _current_layout_dict(self) -> dict:
        """Huidige paneel- en venstergeometrie als opslaan-dict."""
        layout: dict = {}
        for pid, panel in self._panels.items():
            x, y, w, h = panel.get_geometry()
            layout[pid] = [x, y, w, h, panel.is_visible()]
        layout["__window__"] = [
            self.root.winfo_x(), self.root.winfo_y(),
            self.root.winfo_width(), self.root.winfo_height()
        ]
        return layout

    def _apply_layout_dict(self, layout: dict):
        """Pas een opgeslagen layout-dict toe op panelen en venster."""
        win = layout.get("__window__")
        if win and len(win) >= 4:
            self.root.geometry(f"{win[2]}x{win[3]}+{win[0]}+{win[1]}")
        for pid, vals in layout.items():
            if pid == "__window__" or len(vals) < 5:
                continue
            p = self._panels.get(pid)
            if not p:
                continue
            p.place(vals[0], vals[1], vals[2], vals[3])
            if vals[4]:
                p.show()
            else:
                p.hide()
            var = self._panel_vis_vars.get(pid)
            if var:
                var.set(vals[4])
        self._save_cur_settings()
        self.root.after(100, self._draw_map)

    def _reset_panel_layout(self):
        """Herstel naar opgeslagen standaard, of naar _PANEL_DEFAULTS."""
        layouts = _load_layouts()
        if "__default__" in layouts:
            self._apply_layout_dict(layouts["__default__"])
            return
        for pid, (x, y, w, h, vis) in _PANEL_DEFAULTS.items():
            p = self._panels.get(pid)
            if not p:
                continue
            p.place(x, y, w, h)
            if vis:
                p.show()
            else:
                p.hide()
            var = self._panel_vis_vars.get(pid)
            if var:
                var.set(vis)
        self._save_cur_settings()
        self.root.after(100, self._draw_map)

    def _save_as_default_layout(self):
        """Sla huidige layout op als standaard (gebruikt door Reset layout)."""
        layouts = _load_layouts()
        layouts["__default__"] = self._current_layout_dict()
        _save_layouts(layouts)

    def _save_named_layout(self):
        """Vraag een naam en sla de huidige layout op als profiel."""
        from tkinter import simpledialog
        name = simpledialog.askstring(
            "Profiel opslaan",
            "Naam voor dit profiel:",
            parent=self.root
        )
        if not name or not name.strip():
            return
        name = name.strip()
        layouts = _load_layouts()
        layouts[name] = self._current_layout_dict()
        _save_layouts(layouts)
        self._refresh_profiles_menu()

    def _load_named_layout(self, name: str):
        """Laad een opgeslagen profiel."""
        layouts = _load_layouts()
        if name in layouts:
            self._apply_layout_dict(layouts[name])

    def _overwrite_named_layout(self, name: str):
        """Overschrijf een bestaand profiel met de huidige layout."""
        layouts = _load_layouts()
        layouts[name] = self._current_layout_dict()
        _save_layouts(layouts)

    def _delete_named_layout(self, name: str):
        """Verwijder een opgeslagen profiel."""
        layouts = _load_layouts()
        layouts.pop(name, None)
        _save_layouts(layouts)
        self._refresh_profiles_menu()

    def _refresh_profiles_menu(self):
        """Verouderd — profielen staan nu in de settings-dialoog."""
        self._refresh_settings_profiles()

    def _refresh_settings_profiles(self):
        """Bouw de profielen-lijst in de settings-dialoog opnieuw op."""
        f = getattr(self, "_settings_profiles_frame", None)
        if f is None or not f.winfo_exists():
            return
        for w in f.winfo_children():
            w.destroy()

        # Knop: nieuw profiel
        new_r = tk.Frame(f, bg=BG_PANEL)
        new_r.pack(fill=tk.X, pady=(0, 4))
        tk.Button(new_r, text=self._tr("settings_new_profile"),
                  command=lambda: (self._save_named_layout(),
                                   self._refresh_settings_profiles()),
                  font=_font(9), bg=BG_SURFACE, fg="#FFA726",
                  relief=tk.FLAT, padx=8, pady=2, cursor="hand2"
                  ).pack(side=tk.LEFT)

        layouts = _load_layouts()
        user_profiles = sorted(k for k in layouts if not k.startswith("__"))
        for name in user_profiles:
            r = tk.Frame(f, bg=BG_PANEL)
            r.pack(fill=tk.X, pady=1)
            tk.Label(r, text=name, font=_font(9), bg=BG_PANEL,
                     fg=TEXT_H1, anchor='w', width=20).pack(side=tk.LEFT, padx=(0, 6))
            for lbl_key, cmd in [
                ("settings_load",      lambda n=name: (self._load_named_layout(n),)),
                ("settings_overwrite", lambda n=name: (self._overwrite_named_layout(n),)),
                ("settings_delete",    lambda n=name: (self._delete_named_layout(n),
                                                        self._refresh_settings_profiles())),
            ]:
                tk.Button(r, text=self._tr(lbl_key),
                          command=cmd,
                          font=_font(8), bg=BG_SURFACE, fg="#FFA726",
                          relief=tk.FLAT, padx=6, pady=1, cursor="hand2"
                          ).pack(side=tk.LEFT, padx=(0, 3))

    # ── Paneel-titels bijwerken na taalwisseling ─────────────────────────────
    def _update_panel_titles(self):
        _TITLE_MAP = {
            "band_rel":   ("prop_header",  "📶"),
            "worldmap":   ("worldmap",     "🗺"),
            "solar":      ("solar",        "☀"),
            "band_sched": ("sched_header", "🗓"),
            "band_hist":  ("hist_header",  "📈"),
            "band_cond":  ("band_cond_hdr",  "📻"),
            "storm_fc":   ("storm_fc_hdr",   "🌩"),
            "solar_hist": ("solar_hist_hdr", "☀"),
            "alerts":     ("alerts_hdr",      "🔔"),
            "kp_48h":     ("kp_chart_hdr",   "🧲"),
            "bz_24h":     ("bz_chart_hdr",   "⚡"),
            "xray_24h":   ("xray_chart_hdr", "☢"),
            "lightning":  ("lightning_hdr",  "⚡"),
            "dx_spots":   ("dx_header",      "📡"),
            "prop_adv":   ("adv_header",   "💡"),
        }
        for pid, (tr_key, icon) in _TITLE_MAP.items():
            p = getattr(self, "_panels", {}).get(pid)
            if p:
                p.update_title(self._tr(tr_key), icon)

    # ── Solar / Ionosfeer sectie ──────────────────────────────────────────────
    def _build_solar_section(self, parent):
        """Bouwt solar/ionosfeer info in parent."""
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
            row.pack(fill=tk.X, pady=1, padx=(8, 0))
            _TR_LABELS = {"sw_density": "sw_density_lbl", "kp_planet": "kp_planet_lbl"}
            if key == "iono_fof2":
                lbl = tk.Label(row, textvariable=self._iono_station_var,
                               font=_font(8), bg=BG_PANEL,
                               fg=TEXT_DIM, anchor='w', width=27, cursor="question_arrow")
            elif key in _TR_LABELS:
                lbl = tk.Label(row, text=self._tr(_TR_LABELS[key]) + ":",
                               font=_font(8), bg=BG_PANEL,
                               fg=TEXT_DIM, anchor='w', width=27, cursor="question_arrow")
                self._tr_widgets[_TR_LABELS[key]] = lbl
            else:
                lbl = tk.Label(row, text=label + ":", font=_font(8), bg=BG_PANEL,
                               fg=TEXT_DIM, anchor='w', width=27, cursor="question_arrow")
            lbl.pack(side=tk.LEFT)
            _bind_tip(lbl, key)
            var = tk.StringVar(value="—")
            self._solar_vars[key] = var
            val_lbl = tk.Label(row, textvariable=var, font=_font(8, "bold"),
                               bg=BG_PANEL, fg=TEXT_H1, anchor='w', width=9,
                               cursor="question_arrow")
            val_lbl.pack(side=tk.LEFT)
            _bind_tip(val_lbl, key)
            self._solar_val_lbls[key] = val_lbl

    def _build_band_cond_panel(self, parent):
        """Band dag/nacht condities paneel."""
        BAND_INFO = {
            "160m": ("1.8–2.0 MHz — Nachtsband", "Werkt 's nachts via F2-laag. Overdag sterk geabsorbeerd. Goed voor regionale DX bij laag K-index."),
            "80m":  ("3.5–4.0 MHz — Avond/nacht", "Nachtsband, ook vroege ochtend. Skip ~200-2000 km. Gevoelig voor K-index."),
            "60m":  ("5 MHz — Noodband", "Beperkte banden per regio. Dag/nacht bruikbaar bij gemiddelde SFI."),
            "40m":  ("7 MHz — Dagelijks betrouwbaar", "Beste dag-DX band bij lage SFI. Nachts lange skip. MUF ±10-14 MHz."),
            "30m":  ("10 MHz — WARC-band", "CW/digi only. Bijna altijd open. Overdag regionaal, 's nachts DX."),
            "20m":  ("14 MHz — Hoofd-DX band", "Meest betrouwbare DX-band. Open bij SFI>80. Dag: F2-propagatie wereldwijd."),
            "17m":  ("18 MHz — WARC DX-band", "Uitstekend voor DX bij hoge SFI. Gevoeliger voor storm dan 20m."),
            "15m":  ("21 MHz — Zonnecyclus band", "Open bij hoge SFI (>100). Beste propagatie rond middaguur lokaal."),
            "12m":  ("24 MHz — WARC hoge band", "Vereist SFI>110. Trans-equatoriaal en F2 bij zonnemaxima."),
            "10m":  ("28–30 MHz — Ionosfeer afhankelijk", "Gesloten bij laag SFI. Spectaculair open bij SFI>150. Es-opens mogelijk."),
            "6m":   ("50 MHz — Magic band", "Normaal gesloten via ionosfeer. Sporadisch-E (mei-aug) geeft verrassende DX."),
        }

        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        band_tbl = tk.Frame(outer, bg=BG_PANEL)
        band_tbl.pack(fill=tk.X, pady=(0, 2))
        band_tbl.columnconfigure(0, minsize=52)
        band_tbl.columnconfigure(1, minsize=72)
        band_tbl.columnconfigure(2, minsize=72)

        hdr_keys = [("band_hdr", 0), ("day_hdr", 1), ("night_hdr", 2)]
        for key, col in hdr_keys:
            lbl = tk.Label(band_tbl, text=self._tr(key), font=_font(8, "bold"),
                           bg=BG_PANEL, fg=ACCENT, anchor='w')
            lbl.grid(row=0, column=col, sticky='w', pady=(0, 1))
            self._tr_widgets.setdefault(key, [])
            if not isinstance(self._tr_widgets[key], list):
                self._tr_widgets[key] = [self._tr_widgets[key]]
            self._tr_widgets[key].append(lbl)

        self._band_cond_labels: dict = {}
        grid_row = 1
        for name, _, is_hf in _BANDS:
            if not is_hf:
                continue
            bname_lbl = tk.Label(band_tbl, text=name, font=_font(8), bg=BG_PANEL,
                                 fg=TEXT_DIM, anchor='w', cursor="question_arrow")
            bname_lbl.grid(row=grid_row, column=0, sticky='w')
            if name in BAND_INFO:
                title, body = BAND_INFO[name]
                tt = _Tooltip(bname_lbl)
                tip_text = f"{title}\n{'─'*len(title)}\n{body}"
                bname_lbl.bind("<Enter>", lambda e, t=tt, tx=tip_text:
                    t.show(e.widget.winfo_rootx()+e.x, e.widget.winfo_rooty()+e.y, tx)
                    if getattr(self, "_show_tips_var", None) and self._show_tips_var.get() else None)
                bname_lbl.bind("<Leave>", lambda *_, t=tt: t.hide())
            day_lbl = tk.Label(band_tbl, text="—", font=_font(8, "bold"),
                               bg=BG_PANEL, fg=TEXT_DIM, anchor='w')
            day_lbl.grid(row=grid_row, column=1, sticky='w')
            ngt_lbl = tk.Label(band_tbl, text="—", font=_font(8, "bold"),
                               bg=BG_PANEL, fg=TEXT_DIM, anchor='w')
            ngt_lbl.grid(row=grid_row, column=2, sticky='w')
            self._band_cond_labels[name] = (day_lbl, ngt_lbl, is_hf)
            grid_row += 1

    def _build_storm_fc_panel(self, parent):
        """3-daagse stormkans voorspelling paneel."""
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)
        _fc_hdr = tk.Label(outer, text=self._tr("storm_forecast_hdr"),
                           font=_font(8, "bold"), bg=BG_PANEL, fg=ACCENT, anchor='w',
                           cursor="question_arrow")
        _fc_hdr.pack(fill=tk.X, pady=(0, 1))
        self._tr_widgets["storm_forecast_hdr"] = _fc_hdr
        storm_tt = _Tooltip(_fc_hdr)
        storm_tip = ("3-daagse geomagnetische stormkans\n" + "─"*35 + "\n"
                     "K5 (G1): lichte storm — poolroutes verstoord\n"
                     "K6 (G2): matige storm — 40m/80m meest betrouwbaar\n"
                     "K7+ (G3+): zware storm — HF grotendeels onbruikbaar\n\n"
                     "Percentages geven kans op storm die dag.\n"
                     "Bron: NOAA 3-day geomagnetic forecast.")
        _fc_hdr.bind("<Enter>", lambda e, t=storm_tt, tx=storm_tip:
            t.show(e.widget.winfo_rootx()+e.x, e.widget.winfo_rooty()+e.y, tx)
            if getattr(self, "_show_tips_var", None) and self._show_tips_var.get() else None)
        _fc_hdr.bind("<Leave>", lambda *_, t=storm_tt: t.hide())
        self._storm_fc_vars = []
        for _ in range(3):
            var = tk.StringVar(value="—")
            lbl = tk.Label(outer, textvariable=var,
                           font=_font(7), bg=BG_PANEL, fg=TEXT_BODY, anchor='w')
            lbl.pack(fill=tk.X)
            self._storm_fc_vars.append(var)

    def _build_solar_hist_panel(self, parent):
        """Solar-indices historiek paneel (SFI + Kp)."""
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.BOTH, expand=True)
        self._solar_hist_canvas = tk.Canvas(
            outer, bg=BG_PANEL, bd=0, highlightthickness=0, height=80)
        self._solar_hist_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(4, 8))
        self._solar_hist_canvas.bind(
            "<Configure>",
            lambda *_: self._debounce("solhist", 150, self._draw_solar_hist_chart))
        self._solar_hist_canvas.bind("<Enter>", lambda e: self._show_solar_hist_tip(e))
        self._solar_hist_canvas.bind("<Leave>",
            lambda _: getattr(self, "_solar_hist_tt", None) and
                      self._solar_hist_tt.hide())

    # ── Wereldkaart panel ─────────────────────────────────────────────────────
    def _build_map_panel(self, parent):
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.BOTH, expand=True)
        # Overlay-selecties zijn verplaatst naar de 🗺 Overlay-knop in de header

        # GC-labels net boven de selectievakjes
        self._gc_path_var = tk.StringVar(value="")
        self._gc_path_best_color = _BAND_COLORS.get("20m", ACCENT)
        self._gc_path_lbl = tk.Label(outer, textvariable=self._gc_path_var,
                                     font=_font(9), bg=BG_PANEL, fg=TEXT_BODY,
                                     anchor='w')
        self._gc_path_lbl.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 1))

        self._gc_info_var = tk.StringVar(value="")
        tk.Label(outer, textvariable=self._gc_info_var,
                 font=_font(9), bg=BG_PANEL, fg=ACCENT,
                 anchor='w').pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 0))

        # Canvas fills column width; height = width // 2 (exact 2:1, set by _on_map_resize).
        self._map_canvas = tk.Canvas(outer, bg=BG_ROOT,
                                     bd=0, highlightthickness=0)
        self._map_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(2, 2))
        self._map_photo = None
        self._map_canvas.bind("<Configure>",
                              lambda *_: self._debounce("map", 150, self._on_map_resize))
        self._map_canvas.bind("<Button-1>",        self._on_map_btn1_press)
        self._map_canvas.bind("<B1-Motion>",       self._on_map_drag)
        self._map_canvas.bind("<ButtonRelease-1>", self._on_map_btn1_release)
        self._map_canvas.bind("<Button-3>",        self._on_map_clear)
        self._map_canvas.bind("<MouseWheel>",      self._on_map_scroll)
        self._map_canvas.bind("<Button-4>",        self._on_map_scroll)
        self._map_canvas.bind("<Button-5>",        self._on_map_scroll)
        self._map_canvas.bind("<Motion>",          self._on_map_motion)
        self._map_canvas.bind("<Leave>",           lambda _: self._hide_sat_tip())

    def _on_map_motion(self, event):
        """Show satellite path time-tooltip when cursor is near a path point."""
        c  = self._map_canvas
        W  = c.winfo_width() or 960
        zoom = max(1.0, self._map_zoom)
        VW   = max(2, int(W * zoom))
        VH   = max(1, int(W // 2 * zoom))
        cl   = self._map_crop_left
        ct   = self._map_crop_top

        # Satelliet pad tooltip
        if self._sat_path_hits:
            THRESH = 8   # pixel radius for hit detection
            best_d, best_s = THRESH + 1, None
            for lat, lon, dt_s in self._sat_path_hits:
                mx, my = _ll_to_xy(lat, lon, VW, VH)
                dx = event.x - (mx - cl)
                dy = event.y - (my - ct)
                d  = (dx*dx + dy*dy) ** 0.5
                if d < best_d:
                    best_d, best_s = d, dt_s
            if best_s:
                self._show_sat_tip(event, best_s)
                return

        # Satelliet positie tooltip bij hover
        if not self._sat_tip_win or not self._sat_tip_win.winfo_exists():
            for sname, (slat, slon, salt) in getattr(self, "_sat_positions", {}).items():
                sx = int((slon + 180) / 360 * VW) - cl
                sy = int((90 - slat) / 180 * VH) - ct
                if abs(event.x - sx) < 12 and abs(event.y - sy) < 12:
                    # Bereken elevatie t.o.v. QTH
                    R = 6371.0
                    import math as _math
                    qth_r = _math.radians(self._qth_lat)
                    sat_r = _math.radians(slat)
                    dlon  = _math.radians(slon - self._qth_lon)
                    dist  = _math.acos(min(1.0,
                        _math.sin(qth_r)*_math.sin(sat_r) +
                        _math.cos(qth_r)*_math.cos(sat_r)*_math.cos(dlon)))
                    elev  = _math.degrees(_math.atan2(
                        _math.cos(dist) - R/(R+salt),
                        _math.sin(dist))) if salt > 0 else 0
                    self._show_sat_tip(event,
                        f"{sname}\nLat {slat:.1f}°  Lon {slon:.1f}°\n"
                        f"Hoogte {salt:.0f} km  Elevatie {elev:.1f}°")
                    return

        self._hide_sat_tip()

    def _show_sat_tip(self, event, text: str):
        """Create or update the satellite path tooltip near the cursor."""
        if self._sat_tip_win is None:
            win = tk.Toplevel(self.root)
            win.wm_overrideredirect(True)
            if _IS_MAC:
                win.wm_attributes("-topmost", True)
            win.configure(bg=BORDER)
            tk.Label(win, text=text,
                     font=(_FONT_MONO, 8), bg=BG_SURFACE,
                     fg="#B8A050",   # dimmed amber
                     padx=6, pady=3).pack(padx=1, pady=1)
            self._sat_tip_win = win
        else:
            try:
                self._sat_tip_win.winfo_children()[0].config(text=text)
            except Exception:
                pass
        rx = self._map_canvas.winfo_rootx() + event.x + 14
        ry = self._map_canvas.winfo_rooty() + event.y - 22
        self._sat_tip_win.wm_geometry(f"+{rx}+{ry}")

    def _hide_sat_tip(self):
        if self._sat_tip_win:
            try:
                self._sat_tip_win.destroy()
            except Exception:
                pass
            self._sat_tip_win = None

    def _on_map_resize(self, _event=None):
        """Herteken kaart bij resize van het canvas (v4: canvas vult paneel)."""
        self._map_base_size = None
        self._draw_map()

    def _redraw_map(self):
        """Cache ongeldig maken en kaart opnieuw tekenen (na download)."""
        self._map_zoom = 1.0
        self._map_cx   = 0.0
        self._map_cy   = 0.0
        self._map_base_size = None
        self._draw_map()

    def _viewport_to_latlon(self, vx: int, vy: int) -> tuple[float, float]:
        """Viewport pixel → (lat, lon) with zoom/pan."""
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
        # Determine lat/lon under cursor before zoom (always width-based 2:1)
        VW_old = int(W * old_zoom);  VH_old = int(W // 2 * old_zoom)
        VW_new = int(W * new_zoom);  VH_new = int(W // 2 * new_zoom)
        wx_old   = self._map_crop_left + event.x
        wy_old   = self._map_crop_top  + event.y
        lon_cur  = wx_old / VW_old * 360 - 180
        lat_cur  = 90 - wy_old / VH_old * 180
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
        H = c.winfo_height() or 480
        zoom = max(1.0, self._map_zoom)
        # Gebruik de werkelijke canvashoogte — paneel is vrij resizable.
        VW   = max(2, int(W * zoom))
        VH   = max(1, int(W // 2 * zoom))   # altijd 2:1 voor correcte coördinaten

        if not _PIL_OK:
            c.delete("all")
            c.create_rectangle(0, 0, W, H, fill="#1B3A5C", outline="")
            c.create_text(W // 2, H // 2 - 10,
                          text=self._tr("map_nolib"),
                          fill=TEXT_DIM, font=(_FONT_SANS, 9))
            c.create_text(W // 2, H // 2 + 12,
                          text="Klik op de kaart voor een groot-cirkelpad · Scroll om in te zoomen",
                          fill=TEXT_DIM, font=(_FONT_SANS, 8), anchor='center')
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

            # Graticule + degree labels
            # Canvas height = VH (W//2) so no crop offset needed — draw at natural positions.
            d   = ImageDraw.Draw(src)
            LBL = (180, 200, 220)
            for lat in range(-60, 90, 30):
                gy = int((90 - lat) / 180 * VH)
                d.line([(0, gy), (VW, gy)], fill=MAP_GRID, width=1)
                d.text((3, gy + 2), f"{lat:+d}°", fill=LBL)
            for lon in range(-150, 180, 30):
                gx = int((lon + 180) / 360 * VW)
                d.line([(gx, 0), (gx, VH)], fill=MAP_GRID, width=1)
                d.text((gx + 2, 3), f"{lon:+d}°", fill=LBL)

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
            # Satelliet-state: selectie-wijziging invalideert de cache direct.
            bool(getattr(self, "_show_sat_var", None)
                 and self._show_sat_var.get()),
            frozenset(getattr(self, "_sat_selected", set())),
            frozenset(getattr(self, "_sat_path_sel", set())),
            frozenset(getattr(self, "_sat_fp_sel",   set())),
            bool(self._show_sunmoon_path_var.get()),
            bool(self._show_iono_var.get()),
            round(_moon_phase_deg(), 3) if self._show_moon_var.get() else 0,
            bool(getattr(self, "_show_lightning_var", None)
                 and self._show_lightning_var.get()),
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

            # ── Maan (fase-icoon ten opzichte van QTH-breedtegraad) ──────────
            if self._show_moon_var.get():
                moon_lat, moon_lon = _submoon_point()
                mx, my = _ll_to_xy(moon_lat, moon_lon, VW, VH)
                MOON_ICON_SIZE = 18
                phase = _moon_phase_deg()
                moon_icon = _moon_phase_icon(MOON_ICON_SIZE, phase,
                                             getattr(self, "_qth_lat", 52.0))
                mo = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
                mo.paste(moon_icon,
                         (mx - MOON_ICON_SIZE // 2, my - MOON_ICON_SIZE // 2))
                img  = Image.alpha_composite(img.convert("RGBA"), mo).convert("RGB")
                draw = ImageDraw.Draw(img)

            # ── Zon/maan 24-uurs pad ─────────────────────────────────────────
            if self._show_sunmoon_path_var.get():
                path_img = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
                pd = ImageDraw.Draw(path_img)

                def _draw_path(pts, clr):
                    px = [(int((lo + 180) / 360 * VW),
                           int((90 - la)  / 180 * VH)) for la, lo in pts]
                    for dx in (-VW, 0, VW):
                        for x, y in px:
                            pd.ellipse([(x+dx-2, y-2), (x+dx+2, y+2)], fill=clr)

                if self._show_sun_var.get():
                    _draw_path(_sun_path_pts(), (255, 200, 0, 110))
                if self._show_moon_var.get():
                    _draw_path(_moon_path_pts(), (180, 180, 180, 100))

                img  = Image.alpha_composite(img.convert("RGBA"), path_img).convert("RGB")
                draw = ImageDraw.Draw(img)

            # ── Graylijn — ook op ¼ resolutie ────────────────────────────────
            if self._show_graylijn_var.get():
                gray_small = _graylijn_mask(sun_lat, sun_lon, NW, NH)
                gray = gray_small.resize((VW, VH), Image.BILINEAR)
                img  = Image.alpha_composite(img.convert("RGBA"), gray).convert("RGB")
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

            # ── Ionosonde markers ────────────────────────────────────────────
            if self._show_iono_var.get():
                IONO_CLR  = (80, 200, 220)    # cyan
                IONO_NEAR = (120, 255, 120)   # groen voor dichtstbijzijnde
                nearest   = _nearest_iono_station(self._qth_lat, self._qth_lon)
                for code, name, ilat, ilon in _IONO_STATIONS:
                    ix, iy = _ll_to_xy(ilat, ilon, VW, VH)
                    clr = IONO_NEAR if code == nearest[0] else IONO_CLR
                    # Driehoek-marker (3 punten)
                    draw.polygon([(ix, iy - 6), (ix - 5, iy + 4), (ix + 5, iy + 4)],
                                 fill=clr, outline=(0, 0, 0))
                    short = name.split()[0][:8]
                    draw.text((ix + 6, iy - 5), short, fill=clr, font=None)

            # ── QTH marker ───────────────────────────────────────────────────
            qx, qy = _ll_to_xy(self._qth_lat, self._qth_lon, VW, VH)
            draw.line([(qx - 10, qy), (qx + 10, qy)], fill=MAP_QTH, width=2)
            draw.line([(qx, qy - 10), (qx, qy + 10)], fill=MAP_QTH, width=2)

            # ── Satellite overlay (paths / footprints / positions) ───────────
            _draw_sat  = (getattr(self, "_show_sat_var", None) is not None
                          and self._show_sat_var.get())
            PATH_PAST  = (160, 140,  45)
            PATH_FWD   = (255, 215,  50, 220)
            FP_CLR     = (200, 160,  40,  80)
            FP_CLR_QTH = ( 40, 200,  80,  90)
            FP_OUT     = (220, 180,  60, 160)
            FP_OUT_QTH = ( 60, 220, 100, 180)

            for sname, path_tuple in (getattr(self, "_sat_paths", {}) if _draw_sat else {}).items():
                if not path_tuple or len(path_tuple) != 2:
                    continue
                past_pts, fwd_pts = path_tuple

                # Past — draw directly on img (RGB) for solid, crisp line
                prev = None
                for pt in past_pts:
                    if pt[0] is None:
                        prev = None
                        continue
                    cx, cy = _ll_to_xy(pt[0], pt[1], VW, VH)
                    if prev:
                        draw.line([prev, (cx, cy)], fill=PATH_PAST, width=2)
                    prev = (cx, cy)

                # Future — tiny dots on transparent overlay
                fwd_img = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
                fd = ImageDraw.Draw(fwd_img)
                for pt in fwd_pts:
                    if pt[0] is None:
                        continue
                    cx, cy = _ll_to_xy(pt[0], pt[1], VW, VH)
                    fd.point([(cx, cy)], fill=PATH_FWD)
                img  = Image.alpha_composite(img.convert("RGBA"),
                                             fwd_img).convert("RGB")
                draw = ImageDraw.Draw(img)

            # ── Satellite footprints ──────────────────────────────────────────
            R_EARTH = 6371.0
            for sname, (flat, flon, falt) in (
                    getattr(self, "_sat_positions", {}) if _draw_sat else {}).items():
                if sname not in getattr(self, "_sat_fp_sel", set()):
                    continue
                if falt <= 0:
                    continue
                rho = math.acos(min(1.0, R_EARTH / (R_EARTH + falt)))
                lat0_r = math.radians(flat)
                lon0_r = math.radians(flon)

                # Check of QTH binnen de footprint valt
                qth_lat_r = math.radians(getattr(self, "_qth_lat", 52.0))
                qth_lon_r = math.radians(getattr(self, "_qth_lon",  5.0))
                qth_dist  = math.acos(min(1.0,
                    math.sin(lat0_r) * math.sin(qth_lat_r) +
                    math.cos(lat0_r) * math.cos(qth_lat_r) *
                    math.cos(qth_lon_r - lon0_r)))
                qth_in_fp = qth_dist < rho
                fill_clr  = FP_CLR_QTH if qth_in_fp else FP_CLR
                out_clr   = FP_OUT_QTH if qth_in_fp else FP_OUT
                # Compute footprint with lons unwrapped relative to the
                # satellite position.  No wrapping means no lon-jump > 180°,
                # so the polygon is always convex in pixel space and Pillow
                # fills it correctly.  A second pass at x±VW makes the
                # footprint appear on the opposite map edge when it crosses
                # the antimeridian.
                fp_pts = []
                ref_lon = flon
                for az_deg in range(0, 360, 5):
                    theta = math.radians(az_deg)
                    fp_lat = math.degrees(
                        math.asin(math.sin(lat0_r) * math.cos(rho)
                                  + math.cos(lat0_r) * math.sin(rho) * math.cos(theta)))
                    dlon = math.atan2(
                        math.sin(theta) * math.sin(rho) * math.cos(lat0_r),
                        math.cos(rho) - math.sin(lat0_r) * math.sin(math.radians(fp_lat)))
                    fp_lon = math.degrees(lon0_r + dlon)
                    # Unwrap to stay within 180° of the satellite
                    while fp_lon - ref_lon >  180: fp_lon -= 360
                    while ref_lon - fp_lon >  180: fp_lon += 360
                    fp_pts.append((int((fp_lon + 180) / 360 * VW),
                                   int((90 - fp_lat) / 180 * VH)))

                if len(fp_pts) >= 3:
                    rho_deg    = math.degrees(rho)
                    dist_south = 90.0 + flat   # ° van satelliet tot zuidpool
                    dist_north = 90.0 - flat   # ° van satelliet tot noordpool

                    fp_img = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
                    fd = ImageDraw.Draw(fp_img)

                    # Polaire kap: teken de rechthoek EERST zodat het
                    # polygon daarna de bovenrand afdekt en de harde
                    # alpha-overgangsrand verborgen blijft.
                    if dist_south < rho_deg:
                        lat_full = rho_deg - 180.0 - flat
                        yf = max(0, min(VH - 1,
                                        int((90.0 - lat_full) / 180.0 * VH)))
                        fd.rectangle([0, yf, VW - 1, VH - 1], fill=fill_clr)
                    if dist_north < rho_deg:
                        lat_full = 180.0 - rho_deg - flat
                        yf = max(0, min(VH - 1,
                                        int((90.0 - lat_full) / 180.0 * VH)))
                        fd.rectangle([0, 0, VW - 1, yf], fill=fill_clr)

                    # Polygon daarna; outline alleen bij vrij-zwevende footprints.
                    # Bij een polaire kap geeft de outline een zichtbare lijn
                    # langs de onderste boog → onderdrukken.
                    has_polar = (dist_south < rho_deg) or (dist_north < rho_deg)
                    poly_out  = None if has_polar else out_clr
                    fd.polygon(fp_pts, fill=fill_clr, outline=poly_out)
                    # Wrapped copies for footprints that straddle ±180°
                    for dx in (-VW, VW):
                        fd.polygon([(x + dx, y) for x, y in fp_pts],
                                   fill=fill_clr, outline=poly_out)

                    img = Image.alpha_composite(img.convert("RGBA"),
                                                fp_img).convert("RGB")
                    draw = ImageDraw.Draw(img)

            # ── Satellite positions ───────────────────────────────────────────
            SAT_CLR = (255, 220, 60)   # yellow
            for sname, (slat, slon, salt) in (
                    getattr(self, "_sat_positions", {}) if _draw_sat else {}).items():
                sx, sy = _ll_to_xy(slat, slon, VW, VH)
                draw.ellipse([(sx-6, sy-6), (sx+6, sy+6)],
                             fill=SAT_CLR, outline=(200, 160, 0), width=1)
                short = sname.split("(")[0].strip()[:12]
                draw.text((sx + 8, sy - 5), short,
                          fill=SAT_CLR, font=None)

            # Sla volledig gerenderde afbeelding op in cache
            self._map_render_img = img
            self._map_render_key = render_key

        # ── Pan/crop from cached render image ────────────────────────────────
        img    = self._map_render_img
        crop_l = 0
        crop_t = 0
        if zoom > 1.0:
            world_cx = int((self._map_cx + 180) / 360 * VW)
            world_cy = int((90 - self._map_cy) / 180 * VH)
            crop_l   = max(0, min(VW - W, world_cx - W // 2))
            crop_t   = max(0, min(VH - H, world_cy - H // 2))
            img      = img.crop((crop_l, crop_t, crop_l + W, crop_t + H))
        else:
            # Center image in canvas (handles both tall-canvas and wide-canvas)
            crop_l = max(0, (VW - W) // 2)
            crop_t = max(0, (VH - H) // 2)
            if crop_l > 0 or crop_t > 0:
                img = img.crop((crop_l, crop_t, crop_l + W, crop_t + H))
        self._map_crop_left = crop_l
        self._map_crop_top  = crop_t

        # ── Build satellite path hit areas for hover tooltip ──────────────────
        _now    = datetime.datetime.now(datetime.timezone.utc)
        tz_off  = 2 if getattr(self, "_dst_var", None) and self._dst_var.get() else 1
        tz_name = "CEST" if tz_off == 2 else "CET"
        tz_local = datetime.timezone(datetime.timedelta(hours=tz_off))
        hits = []
        for _, ptuple in getattr(self, "_sat_paths", {}).items():
            if not ptuple or len(ptuple) != 2:
                continue
            for seg in ptuple:          # past_pts, fwd_pts
                for pt in seg:
                    if pt[0] is None or len(pt) < 3:
                        continue
                    dt_local = (_now + datetime.timedelta(minutes=float(pt[2]))
                                ).astimezone(tz_local)
                    hits.append((pt[0], pt[1],
                                 dt_local.strftime(f"%d %b  %H:%M {tz_name}")))
        self._sat_path_hits = hits

        # ── Tonen (bliksem als losse canvas-items voor real-time fade) ──────
        self._map_photo = ImageTk.PhotoImage(img)
        c.delete("all")
        c.create_image(0, 0, anchor='nw', image=self._map_photo)
        self._draw_dx_spots()
        # Bliksem direct als canvas-items (real-time, geen PIL nodig)
        self._draw_lightning_canvas_overlay()
        self._draw_wspr_spots()

    def _draw_lightning_canvas_overlay(self):
        """Teken blikseminslagen real-time als canvas-items (geen PIL, geen volledige render).

        Wordt aangeroepen na elke nieuwe inslag en elke 500ms voor fade-animatie.
        """
        if not hasattr(self, "_map_canvas"):
            return
        c = self._map_canvas
        c.delete("lightning")   # verwijder vorige inslagen-items

        if not (getattr(self, "_show_lightning_var", None)
                and self._show_lightning_var.get()):
            return

        strikes = list(getattr(self, "_lightning_strikes", []))
        flashes = list(getattr(self, "_lightning_flashes", []))
        if not strikes and not flashes:
            return

        W    = c.winfo_width()  or 960
        H    = c.winfo_height() or 480
        zoom = max(1.0, getattr(self, "_map_zoom", 1.0))
        VW   = max(2, int(W * zoom))
        VH   = max(1, int(W // 2 * zoom))
        crop_l = getattr(self, "_map_crop_left", 0)
        crop_t = getattr(self, "_map_crop_top",  0)
        now_lt   = datetime.datetime.now(datetime.timezone.utc)
        fade_min = getattr(self, "_lightning_fade_min", _LIGHTNING_KEEP_MIN)

        for slat, slon, stime, _energy in strikes:
            age_s = max(0, (now_lt - stime).total_seconds())
            if age_s > fade_min * 60:
                continue
            f = 1.0 - age_s / max(1, fade_min * 60)   # 1=nieuw → 0=oud
            sz = max(2, min(5, 2 + int(f * 3)))
            vx = int((slon + 180) / 360 * VW) - crop_l
            vy = int((90 - slat) / 180 * VH) - crop_t
            if not (0 <= vx < W and 0 <= vy < H):
                continue
            # Kleur: wit → geel → oranje, vervaagt naar achtergrond
            if age_s < 60:
                r, g, b = 255, 255, int(180 + 75 * f)
            elif age_s < 300:
                r, g, b = 255, int(150 + 105 * f), 30
            else:
                r, g, b = int(150 + 105 * f), int(60 + 60 * f), 0
            # Fade simuleren door kleur te dimmen
            r = int(r * f); g = int(g * f); b = int(b * f)
            clr = f"#{r:02x}{g:02x}{b:02x}"
            c.create_oval(vx-sz, vy-sz, vx+sz, vy+sz,
                          fill=clr, outline="", tags="lightning")

        # Flash-ringen (10s)
        now_flashes = []
        for flat, flon, ftime in flashes:
            age_s = max(0, (now_lt - ftime).total_seconds())
            if age_s >= 10:
                continue
            now_flashes.append((flat, flon, ftime))
            f    = 1.0 - age_s / 10
            sz   = int(6 + age_s * 3)
            r2   = int(255 * f); g2 = int(255 * f); b2 = int(80 * f)
            clr  = f"#{r2:02x}{g2:02x}{b2:02x}"
            vx   = int((flon + 180) / 360 * VW) - crop_l
            vy   = int((90 - flat) / 180 * VH) - crop_t
            if 0 <= vx < W and 0 <= vy < H:
                c.create_oval(vx-sz, vy-sz, vx+sz, vy+sz,
                              outline=clr, tags="lightning")
        self._lightning_flashes = now_flashes

        # Volgende fade-stap (500ms interval zolang er inslagen zijn)
        if hasattr(self, "_lightning_after_id"):
            try:
                self.root.after_cancel(self._lightning_after_id)
            except Exception:
                pass
        self._lightning_after_id = self.root.after(
            500, self._draw_lightning_canvas_overlay)

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
        H  = c.winfo_height() or 480
        VW = int(W * max(1.0, self._map_zoom))
        VH = int(W // 2 * max(1.0, self._map_zoom))
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
        self._bz_canvas = tk.Canvas(outer, height=140, bg=BG_SURFACE,
                                    bd=0, highlightthickness=0)
        self._bz_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 6))
        self._bz_canvas.bind("<Configure>",
                             lambda *_: self._debounce("bz", 150,
                                 lambda: self._draw_bz_graph(
                                     getattr(self, "_last_bz_pts", []))))

        # Tooltip via standaard _Tooltip class
        self._bz_tip = _Tooltip(self._bz_canvas)

        def _bz_on_motion(event):
            if not self._show_tips_var.get():
                return
            pts = getattr(self, "_last_bz_pts", [])
            if not pts:
                self._bz_tip.hide(); return
            c  = self._bz_canvas
            W  = c.winfo_width() or 200
            H  = c.winfo_height() or 120
            PAD_L, PAD_R = 30, 4
            gW = W - PAD_L - PAD_R
            if gW <= 0:
                return
            frac      = (event.x - PAD_L) / gW
            hours_ago = 24 * (1.0 - max(0.0, min(1.0, frac)))
            closest   = min(pts, key=lambda p: abs(p[0] - hours_ago))
            bz_val    = closest[1]
            age_h     = int(closest[0])
            age_min   = int((closest[0] - age_h) * 60)
            t_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=closest[0])
            ts_lbl = t_ago.astimezone().strftime("%d %b %H:%M")
            bz_meaning = ("Positief Bz beschermt aardveld → rustig" if bz_val > 2
                          else "Negatief Bz koppelt aan aardveld → storm risico" if bz_val < -2
                          else "Neutraal Bz — geen direct effect")
            tip = [("⚡  Bz 24u (nT)", None),
                   ("Z-component van het interplanetaire magneetveld.", None), None,
                   ("Bz:", f"{bz_val:+.1f} nT"),
                   ("Betekenis:", bz_meaning),
                   ("Tijd:", ts_lbl)]
            rx = c.winfo_rootx() + event.x
            ry = c.winfo_rooty() + event.y
            self._bz_tip.show(rx, ry, tip)
            c.delete("bz_cursor")
            c.create_line(event.x, 0, event.x, H, fill=BORDER, dash=(3, 3),
                          tags="bz_cursor")

        def _bz_on_leave(_event):
            self._bz_tip.hide()
            self._bz_canvas.delete("bz_cursor")

        self._bz_canvas.bind("<Motion>", _bz_on_motion)
        self._bz_canvas.bind("<Leave>",  _bz_on_leave)

    def _build_kp_panel(self, parent):
        """Planetaire Kp-index 48-uurs staafdiagram."""
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.BOTH, expand=True)
        self._kp_canvas = tk.Canvas(outer, height=120, bg=BG_SURFACE,
                                    bd=0, highlightthickness=0)
        self._kp_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 6))
        self._kp_canvas.bind("<Configure>",
                             lambda *_: self._debounce("kp", 150,
                                 lambda: self._draw_kp_bars(
                                     getattr(self, "_last_kp_pts", []))))
        self._kp_tooltip = _Tooltip(self._kp_canvas)

        def _kp_motion(event):
            if not self._show_tips_var.get():
                return
            pts = getattr(self, "_last_kp_pts", [])
            if not pts:
                self._kp_tooltip.hide(); return
            c  = self._kp_canvas
            W  = c.winfo_width() or 200
            PAD_L, PAD_R = 20, 4
            gW = W - PAD_L - PAD_R
            frac = (event.x - PAD_L) / max(1, gW)
            hours_ago = 48 * (1.0 - max(0.0, min(1.0, frac)))
            ha, kp = min(pts, key=lambda p: abs(p[0] - hours_ago))
            t_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=ha)
            ts_lbl = t_ago.astimezone().strftime("%d %b %H:%M")
            k_status = (self._tr("geo_quiet")     if kp < 3 else
                        self._tr("geo_unsettled") if kp < 5 else
                        self._tr("geo_storm")     if kp < 7 else
                        self._tr("geo_severe"))
            k_meaning = ("K 0-2: Rustig — optimale HF-omstandigheden" if kp < 3
                         else "K 3-4: Onrustig — lagere banden stabieler" if kp < 5
                         else "K 5-6: Kleine storm — poolroutes geblokkeerd" if kp < 7
                         else "K 7+: Zware storm — HF grotendeels onbruikbaar")
            tip = [("🧲  Kp-index 48u", None),
                   ("Planetaire K-index maat voor geomagn. activiteit.", None), None,
                   ("K-index:", f"{kp:.1f}"),
                   ("Status:", k_status),
                   ("Impact:", k_meaning),
                   ("Tijd:", ts_lbl)]
            rx = c.winfo_rootx() + event.x
            ry = c.winfo_rooty() + event.y
            self._kp_tooltip.show(rx, ry, tip)
            c.delete("kp_cursor")
            c.create_line(event.x, 0, event.x, c.winfo_height(),
                          fill=BORDER, dash=(3, 3), tags="kp_cursor")

        self._kp_canvas.bind("<Motion>", _kp_motion)
        self._kp_canvas.bind("<Leave>",  lambda _: (self._kp_tooltip.hide(),
                                                     self._kp_canvas.delete("kp_cursor")))

    def _build_bz_xray_panel(self, parent):
        """Gecombineerd paneel: Bz 24u (boven) + X-ray 24u (onder)."""
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.BOTH, expand=True)

        # Bz sectie
        _bz_hdr = tk.Label(outer, text=self._tr("bz_chart_hdr"),
                           font=_font(9, "bold"), bg=BG_PANEL, fg=ACCENT, pady=2)
        _bz_hdr.pack(anchor='w', padx=10)
        self._tr_widgets["bz_chart_hdr"] = _bz_hdr
        self._bz_canvas = tk.Canvas(outer, height=100, bg=BG_SURFACE,
                                    bd=0, highlightthickness=0)
        self._bz_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 4))
        self._bz_canvas.bind("<Configure>",
                             lambda *_: self._debounce("bz", 150,
                                 lambda: self._draw_bz_graph(
                                     getattr(self, "_last_bz_pts", []))))

        tk.Frame(outer, bg=BORDER, height=1).pack(fill=tk.X, padx=10)

        # X-ray sectie
        _xr_hdr = tk.Label(outer, text=self._tr("xray_chart_hdr"),
                           font=_font(9, "bold"), bg=BG_PANEL, fg=ACCENT, pady=2)
        _xr_hdr.pack(anchor='w', padx=10)
        self._tr_widgets["xray_chart_hdr"] = _xr_hdr
        self._xray_canvas = tk.Canvas(outer, height=100, bg=BG_SURFACE,
                                      bd=0, highlightthickness=0)
        self._xray_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 6))
        self._xray_canvas.bind("<Configure>",
                               lambda *_: self._debounce("xray", 150,
                                   lambda: self._draw_xray_graph(
                                       getattr(self, "_last_xray_pts", []))))
        self._xray_tooltip = _Tooltip(self._xray_canvas)

        def _xray_motion(event):
            if not self._show_tips_var.get():
                return
            pts = getattr(self, "_last_xray_pts", [])
            if not pts:
                self._xray_tooltip.hide(); return
            c  = self._xray_canvas
            W  = c.winfo_width() or 200
            PAD_L, PAD_R = 20, 4
            gW = W - PAD_L - PAD_R
            frac = (event.x - PAD_L) / max(1, gW)
            hours_ago = 24 * (1.0 - max(0.0, min(1.0, frac)))
            ha, flux = min(pts, key=lambda p: abs(p[0] - hours_ago))
            t_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=ha)
            ts_lbl = t_ago.astimezone().strftime("%d %b %H:%M")
            import math as _m
            if   flux >= 1e-4: cls = f"X{flux/1e-4:.1f}"
            elif flux >= 1e-5: cls = f"M{flux/1e-5:.1f}"
            elif flux >= 1e-6: cls = f"C{flux/1e-6:.1f}"
            elif flux >= 1e-7: cls = f"B{flux/1e-7:.1f}"
            else:              cls = f"A{flux/1e-8:.1f}"
            xray_meaning = ("X-vlam — SWF mogelijk, HF dagzijde verstoord" if flux >= 1e-4
                            else "M-vlam — verhoogde kans op SWF" if flux >= 1e-5
                            else "C-vlam — lichte impact" if flux >= 1e-6
                            else "A/B-klasse — normaal achtergrondniveau")
            tip = [("☢  X-straling 24u", None),
                   ("GOES röntgenflux van de zon (log-schaal).", None), None,
                   ("Klasse:", cls),
                   ("Flux:", f"{flux:.2e} W/m²"),
                   ("Impact:", xray_meaning),
                   ("Tijd:", ts_lbl)]
            rx = c.winfo_rootx() + event.x
            ry = c.winfo_rooty() + event.y
            self._xray_tooltip.show(rx, ry, tip)
            c.delete("xray_cursor")
            c.create_line(event.x, 0, event.x, c.winfo_height(),
                          fill=BORDER, dash=(3, 3), tags="xray_cursor")

        self._xray_canvas.bind("<Motion>", _xray_motion)
        self._xray_canvas.bind("<Leave>",  lambda _: (self._xray_tooltip.hide(),
                                                       self._xray_canvas.delete("xray_cursor")))

    def _build_bz_panel_only(self, parent):
        """Zelfstandig Bz 24h paneel (gesplitst van bz_xray)."""
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.BOTH, expand=True)
        ctrl_row = tk.Frame(outer, bg=BG_PANEL)
        ctrl_row.pack(fill=tk.X, padx=10, pady=(2, 0))
        tk.Label(ctrl_row, text="Y ±", font=_font(8), bg=BG_PANEL,
                 fg=TEXT_DIM).pack(side=tk.LEFT)
        if not hasattr(self, "_bz_range_var"):
            self._bz_range_var = tk.IntVar(value=40)
        tk.Spinbox(ctrl_row, from_=10, to=100, increment=10, width=4,
                   textvariable=self._bz_range_var,
                   command=lambda: self._draw_bz_graph(
                       getattr(self, "_last_bz_pts", [])),
                   bg=BG_SURFACE, fg=TEXT_H1, buttonbackground=BG_SURFACE,
                   relief=tk.FLAT, font=_font(8)).pack(side=tk.LEFT, padx=(2, 4))
        tk.Label(ctrl_row, text="nT", font=_font(8), bg=BG_PANEL,
                 fg=TEXT_DIM).pack(side=tk.LEFT)
        self._bz_canvas = tk.Canvas(outer, bg=BG_SURFACE, bd=0, highlightthickness=0)
        self._bz_canvas.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 8))
        self._bz_canvas.bind("<Configure>",
                             lambda *_: self._debounce("bz", 150,
                                 lambda: self._draw_bz_graph(
                                     getattr(self, "_last_bz_pts", []))))
        self._bz_tip = _Tooltip(self._bz_canvas)

        def _bz_on_motion(event):
            if not self._show_tips_var.get():
                return
            pts = getattr(self, "_last_bz_pts", [])
            if not pts:
                self._bz_tip.hide(); return
            c = self._bz_canvas
            W = c.winfo_width() or 200; H = c.winfo_height() or 120
            PAD_L, PAD_R = 30, 4; gW = W - PAD_L - PAD_R
            if gW <= 0: return
            frac = (event.x - PAD_L) / gW
            hours_ago = 24 * (1.0 - max(0.0, min(1.0, frac)))
            closest = min(pts, key=lambda p: abs(p[0] - hours_ago))
            bz_val = closest[1]
            t_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=closest[0])
            ts_lbl = t_ago.astimezone().strftime("%d %b %H:%M")
            bz_meaning = ("Positief Bz beschermt aardveld → rustig" if bz_val > 2
                          else "Negatief Bz koppelt aan aardveld → storm risico" if bz_val < -2
                          else "Neutraal Bz — geen direct effect")
            tip = [("⚡  Bz 24u (nT)", None),
                   ("Z-component van het interplanetaire magneetveld.", None), None,
                   ("Bz:", f"{bz_val:+.1f} nT"),
                   ("Betekenis:", bz_meaning),
                   ("Tijd:", ts_lbl)]
            self._bz_tip.show(c.winfo_rootx() + event.x, c.winfo_rooty() + event.y, tip)
            c.delete("bz_cursor")
            c.create_line(event.x, 0, event.x, H, fill=BORDER, dash=(3, 3), tags="bz_cursor")

        def _bz_on_leave(_e):
            self._bz_tip.hide()
            self._bz_canvas.delete("bz_cursor")

        self._bz_canvas.bind("<Motion>", _bz_on_motion)
        self._bz_canvas.bind("<Leave>",  _bz_on_leave)

    def _build_xray_panel_only(self, parent):
        """Zelfstandig X-ray 24h paneel (gesplitst van bz_xray)."""
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.BOTH, expand=True)
        self._xray_canvas = tk.Canvas(outer, bg=BG_SURFACE, bd=0, highlightthickness=0)
        self._xray_canvas.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 8))
        self._xray_canvas.bind("<Configure>",
                               lambda *_: self._debounce("xray", 150,
                                   lambda: self._draw_xray_graph(
                                       getattr(self, "_last_xray_pts", []))))
        self._xray_tooltip = _Tooltip(self._xray_canvas)

        def _xray_motion(event):
            if not self._show_tips_var.get():
                return
            pts = getattr(self, "_last_xray_pts", [])
            if not pts:
                self._xray_tooltip.hide(); return
            c = self._xray_canvas
            W = c.winfo_width() or 200; PAD_L, PAD_R = 20, 4; gW = W - PAD_L - PAD_R
            frac = (event.x - PAD_L) / max(1, gW)
            ha, flux = min(pts, key=lambda p: abs(p[0] - 24*(1.0 - max(0.0, min(1.0, frac)))))
            t_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=ha)
            ts_lbl = t_ago.astimezone().strftime("%d %b %H:%M")
            if   flux >= 1e-4: cls = f"X{flux/1e-4:.1f}"
            elif flux >= 1e-5: cls = f"M{flux/1e-5:.1f}"
            elif flux >= 1e-6: cls = f"C{flux/1e-6:.1f}"
            elif flux >= 1e-7: cls = f"B{flux/1e-7:.1f}"
            else:              cls = f"A{flux/1e-8:.1f}"
            xray_meaning = ("X-vlam — SWF mogelijk, HF dagzijde verstoord" if flux >= 1e-4
                            else "M-vlam — verhoogde kans op SWF" if flux >= 1e-5
                            else "C-vlam — lichte impact" if flux >= 1e-6
                            else "A/B-klasse — normaal achtergrondniveau")
            tip = [("☢  X-straling 24u", None),
                   ("GOES röntgenflux van de zon (log-schaal).", None), None,
                   ("Klasse:", cls),
                   ("Flux:", f"{flux:.2e} W/m²"),
                   ("Impact:", xray_meaning),
                   ("Tijd:", ts_lbl)]
            self._xray_tooltip.show(c.winfo_rootx() + event.x, c.winfo_rooty() + event.y, tip)
            c.delete("xray_cursor")
            c.create_line(event.x, 0, event.x, c.winfo_height(),
                          fill=BORDER, dash=(3, 3), tags="xray_cursor")

        self._xray_canvas.bind("<Motion>", _xray_motion)
        self._xray_canvas.bind("<Leave>",  lambda _: (self._xray_tooltip.hide(),
                                                       self._xray_canvas.delete("xray_cursor")))

    # ── Onweer: Blitzortung WebSocket ─────────────────────────────────────────

    def _start_lightning_ws(self):
        """Start Blitzortung WebSocket verbinding in achtergrond-thread."""
        if not _WEBSOCKET_OK:
            if hasattr(self, "_lightning_status_var"):
                self._lightning_status_var.set(self._tr("lightning_no_dep"))
            return
        if self._lightning_ws_running:
            return
        self._lightning_ws_running = True
        if hasattr(self, "_lightning_status_var"):
            self.root.after(0, lambda: self._lightning_status_var.set(
                self._tr("lightning_conn")))
        threading.Thread(target=self._lightning_ws_thread, daemon=True).start()

    def _lightning_ws_thread(self):
        """WebSocket thread: ontvangt inslagen van Blitzortung (poort 443).

        Blitzortung gebruikt een compact binair JSON-formaat waarbij getallen
        worden gesplitst met niet-ASCII tekens (U+0106..U+01FF).
        We gebruiken regex om lat/lon direct uit de ruwe string te extraheren.
        """
        import re as _re

        def _parse_blitzortung(message):
            """Extraheer lat/lon uit het Blitzortung compact-JSON formaat.

            Blitzortung port 443 gebruikt een binair gecodeerd formaat waarbij:
            - "lat" aanwezig is (zonder sluitend aanhalingsteken voor de waarde)
            - lon/x zonder tekstuele sleutelnaam (positie-gebaseerd)
            - Getallen worden gesplitst met non-ASCII Unicode-tekens
            """
            # Methode 1: standaard JSON
            try:
                data = json.loads(message)
                lat = data.get("lat") or data.get("y")
                lon = data.get("lon") or data.get("x")
                if lat is not None and lon is not None:
                    return float(lat), float(lon), 1
            except Exception:
                pass

            # Methode 2: Positionale extractie — alle floats ≥3 decimalen
            # Format: ..., lat_value, lon_value, ... (positie 1 en 2 zijn lat/lon)
            floats = _re.findall(r'([+-]?\d{1,3}\.\d{3,})', message)
            if len(floats) >= 2:
                lat, lon = float(floats[0]), float(floats[1])
                if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0:
                    return lat, lon, 1

            # Methode 3: "lat" key zonder sluitend quote
            lat_m = _re.search(r'"lat[^\d\-+]*([+-]?\d+\.\d+)', message)
            lon_m = _re.search(r'"lon[^\d\-+]*([+-]?\d+\.\d+)', message)
            if lat_m and lon_m:
                return float(lat_m.group(1)), float(lon_m.group(1)), 1

            return None, None, 0

        def _on_message(ws, message):
            try:
                lat, lon, energy = _parse_blitzortung(message)
                if lat is None or lon is None:
                    return
                now = datetime.datetime.now(datetime.timezone.utc)
                self._lightning_strikes.append((lat, lon, now, energy))
                # Flash marker voor ripple-effect (10s)
                self._lightning_flashes = getattr(self, "_lightning_flashes", [])
                self._lightning_flashes.append((lat, lon, now))
                # Prune oude inslagen
                cutoff = now - datetime.timedelta(minutes=_LIGHTNING_KEEP_MIN)
                self._lightning_strikes = [
                    s for s in self._lightning_strikes if s[2] >= cutoff]
                # Update teller
                if hasattr(self, "_lightning_count_var"):
                    cnt = len(self._lightning_strikes)
                    self.root.after(0, lambda c=cnt: self._lightning_count_var.set(
                        self._tr("lightning_strikes").format(
                            n=c, m=_LIGHTNING_KEEP_MIN)))
                # Real-time canvas overlay (direct, geen PIL render nodig)
                self.root.after(0, self._draw_lightning_canvas_overlay)
            except Exception as e:
                log.debug("lightning parse error: %s", e)

        def _on_open(ws):
            ws.send('{"a": 111}')
            self._lightning_ws_running = True
            if hasattr(self, "_lightning_status_var"):
                self.root.after(0, lambda: self._lightning_status_var.set(
                    self._tr("lightning_live")))

        def _on_error(ws, err):
            log.warning("Blitzortung error: %s", err)

        def _on_close(ws, code, msg):
            self._lightning_ws_running = False
            # Toon "verbroken" alleen als verbinding ooit live was
            if hasattr(self, "_lightning_status_var") and getattr(self, "_lightning_was_live", False):
                self.root.after(0, lambda: self._lightning_status_var.set(
                    self._tr("lightning_disc")))
            self._lightning_was_live = False
            # Herverbinden na 60 seconden
            self._lightning_reconnect_id = self.root.after(
                60_000, self._start_lightning_ws)

        def _on_open_tracked(ws):
            self._lightning_was_live = True
            _on_open(ws)

        # Probeer ws1..ws4 op poort 443 totdat een verbinding lukt
        _WS_HOSTS = [f"wss://ws{i}.blitzortung.org:443/" for i in range(1, 5)]
        _ws_url = getattr(self, "_lightning_last_host", _WS_HOSTS[0])
        try:
            ws = _ws_lib.WebSocketApp(
                _ws_url,
                on_message=_on_message,
                on_open=_on_open_tracked,
                on_error=_on_error,
                on_close=_on_close,
            )
            ws.run_forever(ping_interval=30, ping_timeout=10)
        except Exception as e:
            log.warning("Blitzortung connect failed on %s: %s", _ws_url, e)
            self._lightning_ws_running = False
            # Roteer naar volgende host bij volgende poging
            try:
                idx = _WS_HOSTS.index(_ws_url)
                self._lightning_last_host = _WS_HOSTS[(idx + 1) % len(_WS_HOSTS)]
            except ValueError:
                self._lightning_last_host = _WS_HOSTS[0]
            if hasattr(self, "_lightning_status_var"):
                self.root.after(0, lambda: self._lightning_status_var.set(
                    f"⚠ Host {_ws_url} geweigerd — volgende poging 60s"))

    def _fetch_storm_forecast(self):
        """Haal CAPE/onweersverwachting op van Open-Meteo (achtergrond)."""
        lat  = getattr(self, "_qth_lat", 52.0)
        lon  = getattr(self, "_qth_lon",  5.0)
        url  = (f"{STORM_FORECAST_URL}"
                f"?latitude={lat:.4f}&longitude={lon:.4f}"
                f"&hourly=weather_code,cape,lifted_index"
                f"&forecast_days=2&timeformat=unixtime&timezone=auto")
        raw  = _fetch_with_retry(url, timeout=10, retries=2)
        if raw is None:
            return
        try:
            data    = json.loads(raw.decode())
            hourly  = data.get("hourly", {})
            times   = hourly.get("time", [])
            codes   = hourly.get("weather_code", [])
            capes   = hourly.get("cape", [])
            lifts   = hourly.get("lifted_index", [])
            now_ts  = datetime.datetime.now(datetime.timezone.utc).timestamp()
            result  = {}
            for i, t in enumerate(times):
                if t < now_ts - 3600:
                    continue
                result[t] = {
                    "code": codes[i] if i < len(codes) else 0,
                    "cape": float(capes[i] or 0) if i < len(capes) else 0.0,
                    "lift": float(lifts[i] or 0) if i < len(lifts) else 0.0,
                }
            self._storm_forecast = result
            self.root.after(0, self._draw_storm_chart)
        except Exception as e:
            log.warning("storm forecast parse error: %s", e)

    def _build_lightning_panel(self, parent):
        """Onweer-paneel: live blikseminslagen + CAPE-voorspelling."""
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.BOTH, expand=True)

        # Status + teller
        self._lightning_status_var = tk.StringVar(
            value=self._tr("lightning_no_dep") if not _WEBSOCKET_OK
            else self._tr("lightning_conn"))
        tk.Label(outer, textvariable=self._lightning_status_var,
                 font=_font(8), bg=BG_PANEL, fg=TEXT_DIM,
                 anchor='w').pack(fill=tk.X, padx=10, pady=(4, 0))

        self._lightning_count_var = tk.StringVar(
            value=self._tr("lightning_strikes").format(
                n=0, m=_LIGHTNING_KEEP_MIN))
        tk.Label(outer, textvariable=self._lightning_count_var,
                 font=_font(9, "bold"), bg=BG_PANEL,
                 fg="#FFF176", anchor='w').pack(fill=tk.X, padx=10)

        # Fade-tijd instelling
        fade_row = tk.Frame(outer, bg=BG_PANEL)
        fade_row.pack(fill=tk.X, padx=10, pady=(2, 0))
        tk.Label(fade_row, text="Fade na:", font=_font(8),
                 bg=BG_PANEL, fg=TEXT_DIM).pack(side=tk.LEFT)
        self._lightning_fade_var = tk.IntVar(
            value=getattr(self, "_lightning_fade_min", _LIGHTNING_KEEP_MIN))

        def _on_fade_change(*_):
            try:
                v = max(1, min(60, self._lightning_fade_var.get()))
                self._lightning_fade_min = v
                self._lightning_fade_var.set(v)
                self._save_cur_settings()
            except Exception:
                pass

        tk.Spinbox(fade_row, from_=1, to=60, width=3,
                   textvariable=self._lightning_fade_var,
                   command=_on_fade_change,
                   bg=BG_SURFACE, fg=TEXT_H1, buttonbackground=BG_SURFACE,
                   relief=tk.FLAT, font=_font(8)).pack(side=tk.LEFT, padx=(4, 0))
        tk.Label(fade_row, text="min", font=_font(8),
                 bg=BG_PANEL, fg=TEXT_DIM).pack(side=tk.LEFT, padx=(2, 0))
        self._lightning_fade_var.trace_add("write", _on_fade_change)

        # QRN niveau
        qrn_row = tk.Frame(outer, bg=BG_PANEL)
        qrn_row.pack(fill=tk.X, padx=10, pady=(2, 0))
        tk.Label(qrn_row, text=self._tr("qrn_lbl"),
                 font=_font(8), bg=BG_PANEL, fg=TEXT_DIM).pack(side=tk.LEFT)
        self._qrn_var = tk.StringVar(value="—")
        tk.Label(qrn_row, textvariable=self._qrn_var,
                 font=_font(8, "bold"), bg=BG_PANEL,
                 fg=ACCENT).pack(side=tk.LEFT, padx=(6, 0))

        # CAPE forecast canvas
        tk.Frame(outer, bg=BORDER, height=1).pack(fill=tk.X, padx=10, pady=(6, 2))
        tk.Label(outer, text=self._tr("storm_forecast_24h"),
                 font=_font(8, "bold"), bg=BG_PANEL, fg=ACCENT,
                 anchor='w').pack(fill=tk.X, padx=10)
        self._lightning_canvas = tk.Canvas(
            outer, bg=BG_SURFACE, bd=0, highlightthickness=0, height=120)
        self._lightning_canvas.pack(
            fill=tk.BOTH, expand=True, padx=10, pady=(2, 8))
        self._lightning_canvas.bind(
            "<Configure>",
            lambda *_: self._debounce("lstorm", 150, self._draw_storm_chart))

        # Toon status
        if hasattr(self, "_lightning_status_var"):
            if _WEBSOCKET_OK:
                self._lightning_status_var.set(self._tr("lightning_conn"))
            else:
                self._lightning_status_var.set(self._tr("lightning_no_dep"))
        # Start WebSocket als beschikbaar
        if _WEBSOCKET_OK and not self._lightning_ws_running:
            self.root.after(500, self._start_lightning_ws)
        # Start forecast fetch — direct en via thread
        threading.Thread(
            target=self._fetch_storm_forecast, daemon=True).start()
        self.root.after(0, lambda: threading.Thread(
            target=self._fetch_storm_forecast, daemon=True).start())
        # Periodieke forecast refresh (elke 10 min)
        self.root.after(600_000, self._schedule_storm_refresh)

    def _schedule_storm_refresh(self):
        threading.Thread(target=self._fetch_storm_forecast, daemon=True).start()
        self.root.after(600_000, self._schedule_storm_refresh)

    def _draw_storm_chart(self):
        """Teken CAPE-voorspelling als staafdiagram."""
        if not hasattr(self, "_lightning_canvas"):
            return
        c = self._lightning_canvas
        c.delete("all")
        W = c.winfo_width() or 300
        H = c.winfo_height() or 120
        c.create_rectangle(0, 0, W, H, fill=BG_SURFACE, outline="")

        forecast = self._storm_forecast
        if not forecast:
            c.create_text(W // 2, H // 2, text="—",
                          fill=TEXT_DIM, font=(_FONT_MONO, 9))
            return

        PAD_L, PAD_R, PAD_T, PAD_B = 28, 4, 4, 16
        gW = W - PAD_L - PAD_R
        gH = H - PAD_T - PAD_B
        CAPE_MAX = 3000.0

        now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
        # Neem maximaal 24 uur vooruit
        hours = sorted(t for t in forecast if t >= now_ts - 1800)[:24]
        if not hours:
            return

        bar_w = max(2, gW // max(len(hours), 1))

        # QRN berekenen: max CAPE of onweers code
        max_cape = max((forecast[t]["cape"] for t in hours), default=0)
        has_storm_code = any(forecast[t]["code"] in (95, 96, 99) for t in hours[:12])
        if max_cape > 1500 or has_storm_code:
            qrn_lbl = self._tr("qrn_high");   qrn_clr = "#EF5350"
        elif max_cape > 500:
            qrn_lbl = self._tr("qrn_moderate"); qrn_clr = "#FFA726"
        else:
            qrn_lbl = self._tr("qrn_low");     qrn_clr = "#66BB6A"
        if hasattr(self, "_qrn_var"):
            self._qrn_var.set(qrn_lbl)
            # Kleur het QRN label
            try:
                self._lightning_canvas.master.master.nametowidget(
                    str(self._qrn_var))
            except Exception:
                pass

        # Y-rasterlijnen
        for cape_ref in (500, 1500, 3000):
            yr = PAD_T + int(gH * (1 - cape_ref / CAPE_MAX))
            if PAD_T <= yr <= PAD_T + gH:
                c.create_line(PAD_L, yr, W - PAD_R, yr,
                              fill=BORDER, dash=(2, 4))
                c.create_text(PAD_L - 2, yr, text=str(cape_ref // 100),
                              fill=TEXT_DIM, font=(_FONT_SANS, 6), anchor='e')

        # Staven
        for i, ts in enumerate(hours):
            cape = forecast[ts].get("cape", 0) or 0
            code = forecast[ts].get("code", 0) or 0
            bar_h = int(gH * min(cape, CAPE_MAX) / CAPE_MAX)
            x_left  = PAD_L + i * bar_w
            x_right = x_left + bar_w - 1
            y_top   = PAD_T + gH - bar_h

            if code in (95, 96, 99):
                clr = "#EF5350"   # onweerscode
            elif cape > 1500:
                clr = "#FFA726"
            elif cape > 500:
                clr = "#FFF176"
            else:
                clr = "#4FC3F7"

            if bar_h > 0:
                c.create_rectangle(x_left, y_top, x_right, PAD_T + gH,
                                   fill=clr, outline="")

        # Tijdlabels (elke 6u)
        for i, ts in enumerate(hours):
            if i % 6 == 0:
                t_lbl = datetime.datetime.fromtimestamp(ts).strftime("%H")
                x = PAD_L + i * bar_w
                c.create_text(x, H - PAD_B + 2, text=t_lbl,
                              fill=TEXT_DIM, font=(_FONT_SANS, 6), anchor='nw')

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
        outer.pack(fill=tk.BOTH, expand=True)

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
                               lambda *_: self._debounce("prop", 150,
                                   lambda: self._draw_prop_bars(
                                       getattr(self, "_last_band_pct", []))))
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

        # Meldingen staan in het aparte "alerts"-paneel


    def _build_alerts_panel(self, parent):
        """Meldingen-paneel: K-drempel, band-opening drempel, satelliet in QTH-zone."""
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        def _tr_cb(frame, tr_key):
            """Helper: registreer widget in _tr_widgets als lijst."""
            self._tr_widgets.setdefault(tr_key, [])
            if not isinstance(self._tr_widgets[tr_key], list):
                self._tr_widgets[tr_key] = [self._tr_widgets[tr_key]]
            self._tr_widgets[tr_key].append(frame)

        def _bind_tip(widget, tip_key):
            """Bind _SOLAR_TIPS tooltip to widget if key exists."""
            from_tips = _SOLAR_TIPS.get(tip_key, None)
            if not from_tips:
                return
            title, body = from_tips[0], from_tips[1]
            tip_text = f"{title}\n{'─'*max(1,len(title))}\n{body}" if title else ""
            if not tip_text:
                return
            tt = _Tooltip(widget)
            widget.bind("<Enter>", lambda e, t=tt, tx=tip_text:
                t.show(e.widget.winfo_rootx()+e.x, e.widget.winfo_rooty()+e.y, tx)
                if getattr(self, "_show_tips_var", None) and self._show_tips_var.get() else None)
            widget.bind("<Leave>", lambda *_, t=tt: t.hide())

        # ── K-index drempel ───────────────────────────────────────────────────
        rk = tk.Frame(outer, bg=BG_PANEL)
        rk.pack(fill=tk.X, pady=(0, 4))
        _k_cb = tk.Checkbutton(rk, variable=self._alert_k_en_var,
                               command=self._save_cur_settings,
                               bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                               activebackground=BG_PANEL, activeforeground=TEXT_H1,
                               font=_font(9), text=self._tr("k_alert_lbl"),
                               cursor="question_arrow")
        _k_cb.pack(side=tk.LEFT, padx=(0, 4))
        _tr_cb(_k_cb, "k_alert_lbl")
        _bind_tip(_k_cb, "tip_k_alert")
        tk.Spinbox(rk, from_=1, to=9, width=2, textvariable=self._k_alert_var,
                   command=self._save_cur_settings,
                   bg=BG_SURFACE, fg=TEXT_H1, buttonbackground=BG_SURFACE,
                   relief=tk.FLAT, font=_font(9, "bold")).pack(side=tk.LEFT)

        # ── Band-opening drempel ──────────────────────────────────────────────
        rb = tk.Frame(outer, bg=BG_PANEL)
        rb.pack(fill=tk.X, pady=(0, 4))
        _b_cb = tk.Checkbutton(rb, variable=self._alert_band_en_var,
                               command=self._save_cur_settings,
                               bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                               activebackground=BG_PANEL, activeforeground=TEXT_H1,
                               font=_font(9), text=self._tr("band_alert_lbl"),
                               cursor="question_arrow")
        _b_cb.pack(side=tk.LEFT, padx=(0, 4))
        _tr_cb(_b_cb, "band_alert_lbl")
        _bind_tip(_b_cb, "tip_band_alert")
        tk.Spinbox(rb, from_=10, to=90, increment=5, width=3,
                   textvariable=self._band_alert_var, command=self._save_cur_settings,
                   bg=BG_SURFACE, fg=TEXT_H1, buttonbackground=BG_SURFACE,
                   relief=tk.FLAT, font=_font(9, "bold")).pack(side=tk.LEFT)
        tk.Label(rb, text="%", font=_font(9), bg=BG_PANEL,
                 fg=TEXT_DIM).pack(side=tk.LEFT, padx=(2, 0))

        # ── X-flare / PCA knoppen ─────────────────────────────────────────────
        def _alert_cb(frame, var, tr_key, tip_key=None):
            cb = tk.Checkbutton(frame, variable=var, command=self._save_cur_settings,
                                bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                                activebackground=BG_PANEL, activeforeground=TEXT_H1,
                                font=_font(9), text=self._tr(tr_key),
                                cursor="question_arrow" if tip_key else "")
            cb.pack(side=tk.LEFT, padx=(0, 4))
            _tr_cb(cb, tr_key)
            if tip_key:
                _bind_tip(cb, tip_key)

        rx = tk.Frame(outer, bg=BG_PANEL)
        rx.pack(fill=tk.X, pady=(0, 1))
        _alert_cb(rx, self._alert_xflare_en_var, "alert_xflare_lbl", "tip_xflare_alert")

        rp = tk.Frame(outer, bg=BG_PANEL)
        rp.pack(fill=tk.X, pady=(0, 4))
        _alert_cb(rp, self._alert_pca_en_var, "alert_pca_lbl", "tip_pca_alert")

        # ── Satelliet in QTH-zone ─────────────────────────────────────────────
        tk.Frame(outer, bg=BORDER, height=1).pack(fill=tk.X, pady=(4, 4))
        _sz_lbl = tk.Label(outer, text=self._tr("sat_zone_hdr"),
                           font=_font(8), bg=BG_PANEL, fg=TEXT_DIM, anchor='w')
        _sz_lbl.pack(fill=tk.X)
        self._tr_widgets["sat_zone_hdr"] = _sz_lbl
        self._sat_zone_var = tk.StringVar(value="—")
        self._sat_zone_lbl = tk.Label(outer, textvariable=self._sat_zone_var,
                                      font=_font(8, "bold"), bg=BG_PANEL,
                                      fg="#66BB6A", anchor='w', wraplength=200,
                                      justify=tk.LEFT)
        self._sat_zone_lbl.pack(fill=tk.X, pady=(0, 4))

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
        for idx, (y0, y1, base_tip) in enumerate(self._bar_rows):
            if y0 <= event.y <= y1:
                self._prop_canvas.config(cursor="hand2")
                if self._show_tips_var.get():
                    rx = self._prop_canvas.winfo_rootx() + event.x
                    ry = self._prop_canvas.winfo_rooty() + event.y
                    # Verrijkte tooltip: kwaliteit + advies toevoegen aan bestaande tip
                    pct = 0
                    name = ""
                    if idx < len(self._bar_band_rows):
                        _, _, name, _ = self._bar_band_rows[idx]
                        bp = {n: p for n, _, p in getattr(self, "_last_band_pct", [])}
                        pct = bp.get(name, 0)
                    if pct <= 0:
                        quality = "Gesloten"
                        advice = "Band niet bruikbaar via ionosfeer."
                    elif pct < 30:
                        quality = "Slecht"
                        advice = "Probeer FT8 of CW voor zwakke signalen."
                    elif pct < 60:
                        quality = "Matig"
                        advice = "SSB mogelijk, FT8 geeft extra marge."
                    elif pct < 85:
                        quality = "Goed"
                        advice = "SSB goed bruikbaar. FT8 voor DX."
                    else:
                        quality = "Uitstekend"
                        advice = "Alle modi. Ideaal voor DX en lange skip."
                    tip = list(base_tip) + [
                        None,
                        ("Kwaliteit:", quality),
                        ("Advies:", advice),
                    ]
                    self._tooltip.show(rx, ry, tip)
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
        outer.pack(fill=tk.BOTH, expand=True)

        hdr = tk.Frame(outer, bg=BG_PANEL)
        hdr.pack(fill=tk.X, padx=10, pady=(4, 2))

        # Radiobuttons: value = interne NL-sleutel (opgeslagen in INI), text = vertaald
        _HIST_RANGE_KEYS = [("Uren", "hist_range_h"), ("Dagen", "hist_range_d"),
                            ("Weken", "hist_range_w"), ("Maanden", "hist_range_m")]
        self._hist_range_rbs: list = []   # [(rb_widget, tr_key), …] voor live-vertaling
        for val, tr_key in _HIST_RANGE_KEYS:
            rb = tk.Radiobutton(hdr, text=self._tr(tr_key),
                                variable=self._hist_range_var,
                                value=val,
                                command=lambda: (self._save_cur_settings(), self._draw_hist_graph(), self._draw_solar_hist_chart()),
                                bg=BG_PANEL, fg=TEXT_BODY, selectcolor=BG_SURFACE,
                                activebackground=BG_PANEL, activeforeground=TEXT_H1,
                                font=_font(9))
            rb.pack(side=tk.LEFT, padx=(8, 0))
            self._hist_range_rbs.append((rb, tr_key))

        self._hist_canvas = tk.Canvas(outer, height=160, bg=BG_PANEL,
                                      bd=0, highlightthickness=0)
        self._hist_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 6))
        self._hist_canvas.bind("<Configure>",
                               lambda *_: self._debounce("hist", 150, self._draw_hist_graph))
        self._hist_tooltip = _Tooltip(self._hist_canvas)
        self._hist_layout: dict = {}
        self._hist_canvas.bind("<Motion>",   self._on_hist_motion)
        self._hist_canvas.bind("<Leave>",    lambda *_: self._hist_tooltip.hide())
        self._hist_canvas.bind("<Button-1>", self._on_hist_click)

        # Compacte band-legenda (klikbaar voor filter)
        self._leg_frame = tk.Frame(outer, bg=BG_PANEL)
        self._leg_frame.pack(fill=tk.X, padx=10, pady=(0, 4))
        self._leg_widgets: dict = {}
        for bname, _, is_hf in _BANDS:
            if not is_hf:
                continue
            color = _BAND_COLORS.get(bname, TEXT_DIM)
            lbl = tk.Label(self._leg_frame, text=bname,
                           font=_font(7), bg=BG_PANEL,
                           fg=color, cursor="hand2")
            lbl.pack(side=tk.LEFT, padx=(0, 4))
            lbl.bind("<Button-1>", lambda _, n=bname: self._toggle_band(n))
            self._leg_widgets[bname] = lbl

    def _toggle_band(self, name: str):
        if name in self._hist_sel:
            self._hist_sel.discard(name)
        else:
            self._hist_sel.add(name)
        # Update legend colors
        for bname, lbl in getattr(self, "_leg_widgets", {}).items():
            if lbl is None:
                continue
            color = _BAND_COLORS.get(bname, TEXT_DIM)
            active = (not self._hist_sel) or (bname in self._hist_sel)
            try:
                lbl.config(fg=color if active else TEXT_DIM,
                           font=_font(7, "bold") if bname in self._hist_sel else _font(7))
            except Exception:
                pass
        self._save_cur_settings()
        self._draw_hist_graph()
        self._draw_solar_hist_chart()

    def _on_hist_click(self, event: tk.Event):
        """Klik op de grafiek: wissel filter voor de dichtstbijzijnde band."""
        lay = self._hist_layout
        if not lay or len(lay.get("data", [])) < 2:
            return
        x_frac   = (event.x - lay["pad_l"]) / max(1.0, lay["gw"])
        target_t = lay["t0"] + x_frac * lay["dt"]
        _, bp, _ = min(lay["data"], key=lambda d: abs(d[0].timestamp() - target_t))
        hf = [(n, max(0, bp.get(n, 0))) for n, _, hf in _BANDS if hf]
        if not hf:
            return
        H       = self._hist_canvas.winfo_height() or 160
        PAD_T   = 8
        PAD_B   = 18
        BAND_H  = H - PAD_T - PAD_B
        y_frac  = (event.y - PAD_T) / max(1, BAND_H)
        target_pct = max(0, min(100, 100 * (1.0 - y_frac)))
        nearest, _ = min(hf, key=lambda x: abs(x[1] - target_pct))
        self._toggle_band(nearest)

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
        BAND_H = H - PAD_T - PAD_B
        gw = W - PAD_L - PAD_R

        # ── Banden historiek ─────────────────────────────────────────────────────
        for pct in (0, 25, 50, 75, 100):
            gy = PAD_T + BAND_H - int(BAND_H * pct / 100)
            c.create_line(PAD_L, gy, W - PAD_R, gy,
                          fill=BORDER, dash=(2, 4))
            c.create_text(PAD_L - 3, gy, text=str(pct),
                          fill=TEXT_DIM, font=(_FONT_SANS, 7), anchor='e')

        if len(data) < 2:
            c.create_text(W // 2, PAD_T + BAND_H // 2,
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
            if self._hist_sel and name not in self._hist_sel:
                continue
            color = _BAND_COLORS.get(name, TEXT_DIM)
            pts = []
            for ts, bp, _ in data:
                pct = max(0, bp.get(name, 0))
                tx = PAD_L + int(gw * (ts.timestamp() - t0) / dt)
                ty = PAD_T + BAND_H - int(BAND_H * pct / 100)
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

    def _draw_solar_hist_chart(self):
        """Teken solar-indices historiek (SFI + Kp) op _solar_hist_canvas."""
        if not hasattr(self, "_solar_hist_canvas"):
            return
        c = self._solar_hist_canvas
        c.delete("all")
        W = c.winfo_width() or 700
        H = c.winfo_height() or 80

        c.create_rectangle(0, 0, W, H, fill=BG_SURFACE, outline="")

        # Legend
        c.create_text(4, 4, text="SFI", fill="#FFA726",
                      font=(_FONT_SANS, 6, "bold"), anchor='nw')
        c.create_text(30, 4, text="K-index: ",
                      fill=TEXT_DIM, font=(_FONT_SANS, 6), anchor='nw')
        for k_val, clr, lbl in [(0,"#4FC3F7","0-2"), (3,"#FFF176","3-4"),
                                  (5,"#FFA726","5-6"), (7,"#EF5350","7+")]:
            c.create_text(70 + k_val*10, 4, text=lbl, fill=clr,
                          font=(_FONT_SANS, 6), anchor='nw')

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

        if len(data) < 2:
            c.create_text(W // 2, H // 2,
                          text=self._tr("no_hist_data"),
                          fill=TEXT_DIM, font=(_FONT_SANS, 9), anchor='center')
            return

        PAD_L, PAD_R, PAD_T, PAD_B = 36, 8, 4, 14
        t0 = t_min.timestamp()
        t1 = now.timestamp()
        dt = max(1.0, t1 - t0)
        gw = W - PAD_L - PAD_R

        sy0 = PAD_T
        sy1 = H - PAD_B
        sh  = max(1, sy1 - sy0)

        def _sol_y(val, mn, mx):
            v = max(mn, min(mx, val))
            return sy0 + int(sh * (1.0 - (v - mn) / max(1, mx - mn)))

        # SFI-lijn (amber, linkeras 50–300)
        sfi_pts = []
        for ts, _, sol in data:
            sfi = sol.get("sfi", 0)
            if sfi:
                tx = PAD_L + int(gw * (ts.timestamp() - t0) / dt)
                ty = _sol_y(sfi, 50, 300)
                sfi_pts.append((tx, ty))
        for j in range(len(sfi_pts) - 1):
            c.create_line(sfi_pts[j][0], sfi_pts[j][1],
                          sfi_pts[j+1][0], sfi_pts[j+1][1],
                          fill="#FFA726", width=1)

        # K-index vlakken (gekleurd op K-niveau)
        _K_CLR = {0: "#4CAF50", 1: "#4CAF50", 2: "#4CAF50",
                  3: "#FFC107", 4: "#FF9800",
                  5: "#F44336", 6: "#E91E63", 7: "#9C27B0",
                  8: "#9C27B0", 9: "#9C27B0"}
        k_pts = [(ts, sol.get("k_index", 0)) for ts, _, sol in data]
        for j in range(len(k_pts) - 1):
            tx1 = PAD_L + int(gw * (k_pts[j][0].timestamp()   - t0) / dt)
            tx2 = PAD_L + int(gw * (k_pts[j+1][0].timestamp() - t0) / dt)
            k   = int(round(k_pts[j][1]))
            ty  = _sol_y(k, 0, 9)
            clr = _K_CLR.get(k, "#666666")
            if tx2 > tx1:
                c.create_rectangle(tx1, ty, tx2, sy1, fill=clr, outline="",
                                   stipple="gray25")

        # Y-labels: SFI links, K rechts
        for label, y_frac in [("300", 0.0), ("SFI", 0.5), ("50", 1.0)]:
            c.create_text(PAD_L - 3, sy0 + int(sh * y_frac),
                          text=label, fill="#FFA726",
                          font=(_FONT_SANS, 6), anchor='e')
        for k_lbl in (0, 3, 6, 9):
            ky = _sol_y(k_lbl, 0, 9)
            c.create_text(W - PAD_R + 2, ky,
                          text=str(k_lbl), fill=_K_CLR.get(k_lbl, "#666666"),
                          font=(_FONT_SANS, 6), anchor='w')

    def _show_solar_hist_tip(self, event):
        if not self._show_tips_var.get():
            return
        tip = [("☀  Solar History", None), None,
               ("SFI lijn:", "Solar Flux Index — hoe hoger, hoe beter HF"),
               ("K-index balken:", "Geomagnetische activiteit — hoog = storing"),
               ("Blauw:", "K 0–2 (rustig)  •  Geel: K 3–4  •  Rood: K 5+")]
        tt = getattr(self, "_solar_hist_tt", None)
        if tt is None:
            self._solar_hist_tt = _Tooltip(self._solar_hist_canvas)
            tt = self._solar_hist_tt
        c = self._solar_hist_canvas
        tt.show(c.winfo_rootx() + event.x, c.winfo_rooty() + event.y, tip)

    # ── Bandopenings-schema (heatmap) ─────────────────────────────────────────
    def _build_schedule_panel(self, parent):
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.BOTH, expand=True)
        self._sched_canvas = tk.Canvas(outer, height=120, bg=BG_PANEL,
                                       bd=0, highlightthickness=0)
        self._sched_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 6))
        self._sched_canvas.bind("<Configure>",
                                lambda *_: self._debounce("sched", 150, self._draw_schedule))
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
        lay  = self._hist_layout
        data = lay.get("data", [])
        if len(data) < 2:
            self._hist_tooltip.hide()
            return
        x_frac   = (event.x - lay["pad_l"]) / max(1.0, lay["gw"])
        target_t = lay["t0"] + x_frac * lay["dt"]
        ts, bp, sol = min(data, key=lambda d: abs(d[0].timestamp() - target_t))
        local_ts = ts.astimezone().strftime("%d %b %H:%M")

        # ── Koptekst ─────────────────────────────────────────────────────────────
        tip = [(self._tr("hist_tooltip_hdr").format(ts=local_ts), None), None]

        # ── Band-legenda met kleur-indicator en percentage ────────────────────────
        tip.append((self._tr("hist_bands_lbl"), None))
        hf = [(n, max(0, bp.get(n, 0))) for n, _, hf in _BANDS if hf]
        hf.sort(key=lambda x: -x[1])
        for bname, pct in hf:
            if self._hist_sel and bname not in self._hist_sel:
                continue
            clr_block = "━"  # kleur-indicator (tooltip toont tekst, kleur via label)
            tip.append((f"{clr_block} {bname}", f"{pct}%"))
        tip.append(None)

        # ── Solar-indices ─────────────────────────────────────────────────────────
        tip.append((self._tr("hist_solar_lbl"), None))
        sfi  = sol.get("sfi", 0)
        k    = sol.get("k_index", 0)
        ssn  = sol.get("ssn", 0)
        a    = sol.get("a_index", 0)
        bz   = sol.get("bz", None)
        spd  = sol.get("sw_speed", None)
        if sfi:  tip.append(("SFI:", f"{sfi:.0f}"))
        if ssn:  tip.append(("SSN:", f"{ssn:.0f}"))
        k_lbl = (self._tr("geo_quiet")     if k < 3 else
                 self._tr("geo_unsettled") if k < 5 else
                 self._tr("geo_storm"))
        tip.append(("K-index:", f"{k:.1f} ({k_lbl})"))
        if a:    tip.append(("A-index:", f"{a:.0f}"))
        if bz is not None and bz != 0:
            tip.append(("Bz:", f"{bz:+.1f} nT"))
        if spd:  tip.append((self._tr("sw_speed_lbl") if "sw_speed_lbl" in _T else "SW:", f"{spd:.0f} km/s"))
        tip.append(None)
        tip.append((self._tr("hist_click_hint"), None))

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
        """Legacy wrapper — gebruik _build_dx_spots_panel voor v4 panelen."""
        self._build_dx_spots_panel(parent)

    def _build_dx_spots_panel(self, parent):
        """Live DX Spots paneel (zonder solar sectie)."""
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.BOTH, expand=True)

        hdr = tk.Frame(outer, bg=BG_PANEL)
        hdr.pack(fill=tk.X, padx=10, pady=(4, 2))
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
        self._dx_sb = tk.Scrollbar(dx_wrap, orient=tk.VERTICAL,
                                   command=self._dx_canvas.yview,
                                   bg=BG_SURFACE, troughcolor=BG_ROOT, width=8)
        self._dx_canvas.configure(yscrollcommand=self._dx_sb.set)
        # Scrollbar wordt pas getoond als de inhoud de canvas overschrijdt
        self._dx_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._dx_canvas.bind("<Configure>",
                             lambda *_: self._debounce("dx", 150, self._draw_dx_panel))
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
        C_UTC  = 34;  C_BAND = 34;  C_DX = 68
        C_FREQ = 60;  C_SPOT = 66
        C_CMT  = max(40, W - C_UTC - C_BAND - C_DX - C_FREQ - C_SPOT - 12)

        # Kolomkoppen
        for txt, x in [("UTC",                          4),
                       (self._tr("dx_col_band"),        4 + C_UTC),
                       ("DX",                           4 + C_UTC + C_BAND),
                       ("MHz",                          4 + C_UTC + C_BAND + C_DX),
                       (self._tr("dx_col_spotter"),     4 + C_UTC + C_BAND + C_DX + C_FREQ),
                       (self._tr("dx_col_comment"),     4 + C_UTC + C_BAND + C_DX + C_FREQ + C_SPOT)]:
            c.create_text(x, 2, text=txt, fill=ACCENT,
                          font=(_FONT_MONO, 7, "bold"), anchor='nw')
        c.create_line(0, ROW_H + 2, W, ROW_H + 2, fill=BORDER)

        if not spots:
            c.create_text(W // 2, H // 2,
                          text=self._tr("no_dx_spots"),
                          fill=TEXT_DIM, font=(_FONT_SANS, 9), anchor='center')
            c.configure(scrollregion=(0, 0, W, H))
            if hasattr(self, "_dx_sb"):
                self._dx_sb.pack_forget()
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
        if hasattr(self, "_dx_sb"):
            if total_h > H:
                self._dx_sb.pack(side=tk.RIGHT, fill=tk.Y, before=c)
            else:
                self._dx_sb.pack_forget()

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
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill=tk.BOTH, expand=True)
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

        # ── 3-day storm probability forecast ─────────────────────────────
        storm_probs = data.get("storm_probs", [])
        if storm_probs:
            worst = max(storm_probs, key=lambda p: p.get("minor", 0))
            mn_max = worst.get("minor", 0)
            mo_max = worst.get("moderate", 0)
            sv_max = worst.get("severe", 0)
            day_s  = str(worst.get("date", ""))[-5:]
            if mn_max >= 40 or mo_max >= 20:
                tips.append(("🌩",
                    self._tr("adv_storm_fc_likely").format(
                        day=day_s, mn=mn_max, mo=mo_max),
                    "#F44336"))
            elif mn_max >= 15 or mo_max >= 5:
                tips.append(("⚠️",
                    self._tr("adv_storm_fc_watch").format(
                        day=day_s, mn=mn_max, mo=mo_max, sv=sv_max),
                    "#FFC107"))
            else:
                tips.append(("🛡",
                    self._tr("adv_storm_fc_quiet"),
                    "#4CAF50"))

        # ── Solar wind ram pressure ────────────────────────────────────────
        try:
            spd_f  = float(data.get("sw_speed", "0").replace("—", "0"))
            dens_f = float(data.get("sw_density", "0").replace("—", "0"))
            # Ram pressure P = 0.5 × m_p × n × v² ≈ 1.67e-27 × n×1e6 × v²×1e6 / 1e-9
            # Simplified: P [nPa] ≈ 1.67e-6 × dens [n/cm³] × (spd [km/s])²
            pram = 1.67e-6 * dens_f * (spd_f ** 2)
            if pram > 5.0 or dens_f > 15:
                tips.append(("💥",
                    self._tr("adv_sw_ram_high").format(
                        spd=int(spd_f), dens=f"{dens_f:.1f}", pram=pram),
                    "#FFA726"))
            else:
                tips.append(("💨",
                    self._tr("adv_sw_ram_normal").format(
                        spd=int(spd_f), dens=f"{dens_f:.1f}"),
                    TEXT_BODY))
        except (ValueError, TypeError):
            pass

        # ── Kp trend (rising / falling / stable over last 12h) ────────────
        kp_hist = getattr(self, "_last_kp_pts", [])
        if len(kp_hist) >= 4:
            # Compare first and last 2 points over ~12h window
            pts_12h = [(h, k) for h, k in kp_hist if h <= 12]
            if len(pts_12h) >= 4:
                old_kp = sum(k for _, k in pts_12h[:2]) / 2
                new_kp = sum(k for _, k in pts_12h[-2:]) / 2
                delta  = new_kp - old_kp
                h_span = int(pts_12h[0][0])
                if delta > 1.0:
                    tips.append(("📈",
                        self._tr("adv_kp_rising").format(
                            h=h_span, old=old_kp, new=new_kp),
                        "#F44336"))
                elif delta < -1.0:
                    tips.append(("📉",
                        self._tr("adv_kp_falling").format(
                            h=h_span, old=old_kp, new=new_kp),
                        "#4CAF50"))
                else:
                    tips.append(("📊",
                        self._tr("adv_kp_stable").format(
                            h=h_span, kp=new_kp),
                        TEXT_DIM))

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
        for name, (day_lbl, ngt_lbl, is_hf) in getattr(self, "_band_cond_labels", {}).items():
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
        def _flt(key, default=0.0):
            try:
                return float(data.get(key, str(default)).replace("—", str(default)))
            except (ValueError, TypeError):
                return default

        # Bz: meest recente waarde uit bz_history (laatste punt)
        bz_hist = data.get("bz_history", [])
        bz_now  = bz_hist[-1][1] if bz_hist and len(bz_hist[-1]) >= 2 else 0.0
        try:
            bz_now = float(bz_now)
        except (TypeError, ValueError):
            bz_now = 0.0

        # X-ray: eerste karakter als proxy (A=1, B=2, C=3, M=4, X=5)
        _xray_class = {"A": 1, "B": 2, "C": 3, "M": 4, "X": 5}
        xray_str = data.get("xray", "")
        xray_num = _xray_class.get(xray_str[:1].upper(), 0) if xray_str else 0

        sol = {
            "sfi":        sfi,
            "ssn":        ssn,
            "k_index":    k_index,
            "a_index":    a_val,
            "bz":         bz_now,
            "sw_speed":   _flt("sw_speed"),
            "sw_density": _flt("sw_density"),
            "xray":       xray_num,
        }
        self._history.append((now, bp, sol))
        _append_history(now, bp, sol)
        self._draw_hist_graph()
        self._draw_solar_hist_chart()
        self._draw_schedule()
        self._update_advice()
        self._check_alerts(bp, k_index)

    # ── Instellingen opslaan ──────────────────────────────────────────────────
    def _save_cur_settings(self):
        if hasattr(self, "_panels") and self._panels:
            _save_panel_layout(self._panels)
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
                       self._show_cs_var.get(),
                       self._show_spots_var.get(),
                       self._show_wspr_var.get(),
                       self._show_aurora_var.get(),
                       self._show_sat_var.get(),
                       self._show_sunmoon_path_var.get(),
                       self._show_iono_var.get(),
                       self._show_lightning_var.get(),
                       getattr(self, "_lightning_fade_min", 30),
                       self._show_splash_var.get(),
                       self._dx_own_cont_var.get(),
                       self._hist_range_var.get(),
                       self._hist_sel,
                       self._k_alert_var.get(),
                       self._band_alert_var.get(),
                       self._alert_k_en_var.get(),
                       self._alert_band_en_var.get(),
                       self._alert_xflare_en_var.get(),
                       self._alert_pca_en_var.get(),
                       self._lang_var.get(),
                       self._theme_var.get(),
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
        self._tray_icon = pystray.Icon("HAMIOS", tray_img, "HAMIOS v4.0.2", menu)
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

        BZ_MAX = float(getattr(self, "_bz_range_var",
                               type("", (), {"get": lambda s: 40})()).get())
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
        self._draw_solar_hist_chart()


# ── Version check (GitHub releases API) ────────────────────────────────────────
_APP_VERSION = "4.0.2"
_GITHUB_RELEASES_URL = "https://api.github.com/repos/fvdijke/HAMIOS/releases/latest"

def _check_latest_version() -> tuple[str, str]:
    """Return (latest_tag, release_url) or ("", "") on failure."""
    try:
        raw = _fetch_with_retry(_GITHUB_RELEASES_URL, timeout=6, retries=1,
                                headers={"User-Agent": "HAMIOS/3.1",
                                         "Accept": "application/vnd.github.v3+json"})
        if raw is None:
            return "", ""
        data = json.loads(raw.decode())
        return data.get("tag_name", ""), data.get("html_url", "")
    except Exception:
        return "", ""


# ── Help / About dialog ─────────────────────────────────────────────────────────
class _HelpDialog:
    """Floating help/about dialog (F1 or header button)."""

    CONTENT = """\
HAMIOS v{ver}  —  HF Propagation & DX Monitor
by Frank van Dijke  ·  Developed with Claude AI

─── Draggable Panels ─────────────────────────────────────
  All panels are freely draggable and resizable.
  Drag via the amber title bar · Resize via ◢ (bottom-right).
  ⚙ Settings  →  manage panels, layout presets, QTH, theme, language.
  🗺 Overlay   →  toggle map overlays (Display / Data groups).

─── Panels overview ──────────────────────────────────────
  📶 HF Band Reliability   Gradient bars per band (MUF/LUF model).
  🌍 World Map             Click=GC-path · Scroll=zoom · Drag=pan.
  ☀ Solar / Ionosphere    SFI, SSN, K/A-index, Bz, MUF, LUF, foF2.
  📻 Band Conditions       Day / Night reliability per HF band.
  🌩 Storm Forecast        3-day geomagnetic storm probability.
  ☀ Solar History         SFI line + Kp bars over time.
  📈 Band History          Band reliability over time (click to filter).
  🧲 Kp 48h               Planetary K-index bar chart.
  ⚡ Bz 24h               IMF Bz (Y-axis zoom: ±10–100 nT).
  ☢ X-ray 24h             GOES X-ray flux on log scale.
  ⚡ Lightning             Live strikes (Blitzortung) + CAPE forecast.
  📡 DX Spots             Live HF cluster spots + heatmap.
  💡 Propagation Advice   12 analysis cards (geo, solar, DX routes…).
  🔔 Alerts               K/band thresholds, X-flare, satellite overhead.
  🕐 Band Schedule        24h heatmap per band (local time).

─── Satellite Tracking (🛰 Sat) ──────────────────────────
  Category filter: All / Amateur / ISS / Weather / CubeSat.
  Toggles: position dot · orbital path · footprint.
  Footprint turns green when QTH is inside coverage.
  Hover satellite dot → lat / lon / altitude / elevation.
  ↻ TLE  fetches fresh orbital data from Celestrak.

─── Spy / Numbers Stations (🕵 Spy) ──────────────────────
  Sortable table · active/inactive filter · hover = schedule.
  Data: hamios_spy_stations.json (editable).

─── Lightning (⚡) ────────────────────────────────────────
  Requires: pip install websocket-client
  Real-time strikes via Blitzortung WebSocket.
  CAPE/LI forecast (Open-Meteo, no API key needed).
  QRN level indicator for HF bands < 15 MHz.

─── Data sources ──────────────────────────────────────────
  Solar / bands     hamqsl.com                  auto interval
  Bz / Kp / Xray   NOAA SWPC                   auto interval
  Storm forecast    NOAA 3-day-geomag-forecast  auto interval
  DX cluster        dxwatch.com                 every 5 min
  WSPR spots        wspr.live                   every 15 min
  Ionosonde foF2    GIRO / LGDC                 auto interval
  TLE (satellite)   Celestrak                   on demand / ↻ TLE
  Lightning         Blitzortung WebSocket       real-time
  Storm forecast    Open-Meteo (CAPE/LI)        every 10 min

─── Keyboard shortcuts ────────────────────────────────────
  F1              This help dialog
  F11             Toggle fullscreen
  Scroll wheel    Zoom world map
  Right-click     Reset map zoom / clear great-circle path

─── Files ─────────────────────────────────────────────────
  HAMIOS.ini                settings (theme, language, QTH, …)
  hamios_layouts.json       panel layout presets
  HAMIOS_history.csv        band history (90 days)
  HAMIOS.log                application log (rotating, max 3 MB)
  hamios_tle.json           TLE cache (satellites)
  hamios_spy_stations.json  spy / numbers stations database
  langs/lang_*.json         language packs
"""

    def __init__(self, root: tk.Tk, ver: str = _APP_VERSION,
                 latest: str = "", release_url: str = ""):
        self._root = root
        self._ver = ver
        self._latest = latest
        self._url = release_url
        self._win: tk.Toplevel | None = None

    def show(self):
        if self._win and self._win.winfo_exists():
            self._win.lift()
            return
        win = tk.Toplevel(self._root)
        self._win = win
        win.title(f"HAMIOS v{self._ver}  —  Help & About")
        win.configure(bg=BG_PANEL)
        win.resizable(True, True)
        win.geometry("620x680")

        tk.Frame(win, bg=ACCENT, height=2).pack(fill=tk.X)

        text_frame = tk.Frame(win, bg=BG_PANEL)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        sb = tk.Scrollbar(text_frame)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        txt = tk.Text(text_frame, bg=BG_SURFACE, fg=TEXT_BODY,
                      font=("Consolas", 9), relief=tk.FLAT,
                      wrap=tk.WORD, yscrollcommand=sb.set,
                      padx=14, pady=10, state=tk.NORMAL,
                      insertbackground=TEXT_H1)
        txt.pack(fill=tk.BOTH, expand=True)
        sb.config(command=txt.yview)

        content = self.CONTENT.format(ver=self._ver)
        if self._latest and self._latest != f"v{self._ver}":
            content += (f"\n─── Update available ─────────────────────────────────\n"
                        f"  Installed: v{self._ver}   Latest: {self._latest}\n"
                        f"  {self._url}\n")
        elif self._latest:
            content += f"\n  ✓  v{self._ver} is up to date.\n"

        txt.insert(tk.END, content)
        txt.config(state=tk.DISABLED)

        tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X)
        btn_row = tk.Frame(win, bg=BG_PANEL)
        btn_row.pack(fill=tk.X, padx=10, pady=6)
        tk.Button(btn_row, text="Close", command=win.destroy,
                  font=("Segoe UI", 9), bg=BG_SURFACE, fg=TEXT_H1,
                  relief=tk.FLAT, padx=12, cursor="hand2").pack(side=tk.RIGHT)
        if self._latest and self._latest != f"v{self._ver}":
            import webbrowser
            tk.Button(btn_row, text=f"Get {self._latest}",
                      command=lambda: webbrowser.open(self._url),
                      font=("Segoe UI", 9, "bold"), bg=ACCENT, fg=BG_ROOT,
                      relief=tk.FLAT, padx=12, cursor="hand2").pack(side=tk.RIGHT, padx=(0, 6))


# ── Entrypoint ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import signal
    import traceback as _tb

    root = tk.Tk()
    # Verplaats root ver buiten beeld (1×1 pixel) zodat geen bare Tk-venster
    # verschijnt, maar Toplevel-kinderen wél getoond kunnen worden.
    root.geometry("1x1-32000-32000")
    root.overrideredirect(True)   # geen titelbalk/rand
    root.update()

    # ── Splash / dependency-check vóór de hoofdapplicatie ────────────────────
    if not _check_and_show_dependencies(root):
        root.destroy()
        sys.exit(0)

    # Herstel root voor normale gebruik
    root.overrideredirect(False)
    root.withdraw()

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

    # Pas opgeslagen venstergeometrie toe vanuit saved default
    _wg = _load_startup_window_geometry()
    if _wg:
        wx, wy, ww, wh = _wg
        root.geometry(f"{ww}x{wh}+{wx}+{wy}")

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
