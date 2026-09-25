<p align="center">
<img width="692" height="707" alt="2026-06-15 13_51_00-HAMIOS" src="https://github.com/user-attachments/assets/66626bc2-40f5-41aa-a80e-9c3fbd28e76f" />

</p>

# HF Propagation & Atmosphere Monitor

**Real-time HF propagation and DX monitor for amateur radio operators — Windows 10/11**

> v5.8 · September 2026 · Frank van Dijke · *Developed with Claude AI (Anthropic)*

[![Website](https://img.shields.io/badge/website-hamios.space-orange)](https://hamios.space)
[![Release](https://img.shields.io/github/v/release/fvdijke/HAMIOS?label=latest)](https://github.com/fvdijke/HAMIOS/releases/latest)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-blue)](https://github.com/fvdijke/HAMIOS/releases/latest)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![Language](https://img.shields.io/badge/language-EN%20%7C%20NL-green)](https://github.com/fvdijke/HAMIOS)

---
  <img width="3155" height="1683" alt="2026-06-15 13_51_27-HF Propagation   Atmosphere Monitor" src="https://github.com/user-attachments/assets/04fc0a87-3e2d-4600-bc87-eadce8139d6c" />

## Overview

HF Propagation & Atmosphere Monitor gives amateur radio operators real-time insight into HF propagation conditions, solar weather, DX cluster activity, shortwave schedules, satellite tracking, lightning detection, and direct radio control — all in a modern, fully customisable dark-theme GUI built with PySide6/Qt6.

**Fully bilingual** — switch between English and Dutch at any time via Settings → About.

---

## ✨ Features

| Category | Description |
|---|---|
| 💡 **Propagation Advice** | Verdict with evidence and up to five recommendations (band → mode + frequency → direction → time window), confirmed by real WSPR, DX-cluster and PSKReporter spots; events (NOAA R/S/G, shock, Bz, sporadic-E, meteor showers), coming hours, explanatory tooltips; click → great-circle path on the map and CAT tuning |
| 📡 **Measured propagation** | One central model calibrated on the nearest ionosonde (KC2G/GIRO) and NOAA D-RAP absorption, with skip zone, day/night from the real sun at your QTH |
| 📶 **Bands now** | Probability per band (160m–6m) right now, day/night rating and trend, MUF/LUF, click to tune via CAT |
| 🗓 **Next 24 hours** | Rolling band heatmap from now with the MUF/LUF curve on the same time axis |
| 📡 **Ionosondes** | Measured ionosphere near your QTH: foF2 → highest NVIS band, MUF(3000) → highest DX band, measured vs model, 12 nearest stations |
| 🛰 **Satellite Passes** | Passes of your tracked satellites for the next 24 h (rise, duration, max elevation, direction) with an alert 5 minutes before each pass |
| ☀ **Solar / Ionosphere** | SFI, SSN, K/A index, X-ray class, real-time solar wind (speed, density, Bz) |
| 🌩 **Storm Forecast** | NOAA 3-day geomagnetic storm probability (G1–G4+) and the 27-day outlook |
| 📈 **Charts** | Kp 48 h, Bz 24 h, GOES X-ray 24 h, solar and band history (24h/7d/30d/1y) |
| 🛰 **WSPR Live** | Real WSPR spots around your QTH via wspr.live (→ your region heard elsewhere, ← distant stations heard in your region) |
| 📡 **Live DX Spots** | DX cluster, band/continent filter, heatmap, click to tune |
| 📡 **PSKReporter** | FT8/FT4 reception reports as paths on the map |
| 🌍 **World Map** | 4096×2048 map with overlays (see below) |
| 🪟 **Tiled layout** | Panels always fit together; four layouts (Map centre, Operating, Analysis, Default), drag to rearrange, layout lock |
| ⚡ **Lightning** | Live Blitzortung.org feed, QRN advice, proximity alert |
| 🔔 **Alerts** | Solar, propagation, weather and satellite alerts |
| 📻 **EIBI / FT8 / SpyStations** | Shortwave schedule, digital-mode reference, numbers stations — all with CAT tuning |
| 📟 **CAT Interface** | Yaesu, Kenwood/Elecraft, Icom CI-V — live frequency in the header |
| 📐 **HAM Antenna Designer** | Bundled antenna designer v3.0.1: lengths, matching, cable loss, SWR sweep, radiation patterns and schematic drawings; follows the HAMIOS language |
| 💾 **Profiles** | Save complete workspaces (settings + layout + window geometry) |
| 🌐 **Bilingual** | English / Dutch, switch via Settings → About |

---

## 🗺️ Map Overlays

Toggleable via the **🗺 Overlays** button in the header:

- Day/night terminator and grey line (NOAA solar calculator, incl. refraction — within ~1°)
- **Aurora** — NOAA OVATION measured probability, smooth green → yellow → red
- **Propagation map** — probability that the chosen band carries the path from your QTH to every point on Earth (same model as the advice, incl. skip zone)
- **HF absorption** — NOAA D-RAP: where HF is absorbed after a flare or proton event
- Sun and Moon position with live phase icon and QTH horizon indicator (▲/▼)
- Maidenhead locator grid — hover shows the sub-squares and the 6-character locator
- **DXCC callsign country codes** — hover a country for all its prefixes
- Graticule (10° / 20° / 30° step)
- Live DX spots and **PSKReporter** paths coloured by band
- Satellite positions, orbit paths, footprints
- Lightning strikes with ripple rings and alert radius circles
- Great-circle path from your QTH (click the map or a recommendation)

---

## 🚀 Installation

### Ready-to-use EXE (Windows, no Python needed)

1. Download **[HAMIOS5.exe](https://github.com/fvdijke/HAMIOS/releases/latest)** from the latest release
2. Place in an empty folder
3. Run — the world map is **automatically downloaded** on first start (~1–4 MB)

### From source

```bash
git clone https://github.com/fvdijke/HAMIOS.git
cd HAMIOS
pip install PySide6
pip install pyserial websocket-client   # optional
python HAMIOS5.py
```

### Dependencies

| Package | Required | Purpose |
|---|---|---|
| PySide6 | ✅ Yes | GUI framework (Qt6) |
| pyserial | Optional | CAT radio interface |
| websocket-client | Optional | Live lightning detection |

---

## ⚙️ Configuration

All settings are stored in `hamios_config.json` (auto-created on first run) and applied live without restart:

- **Station** — callsign, QTH (lat/lon or Maidenhead), mode, power, antenna
- **Map** — graticule step, Maidenhead / overlay font sizes, sun/moon icon sizes
- **Lightning** — fade duration, alert radii, animation scale, beep settings
- **Alerts** — K-index threshold, X-flare alert, satellite zone ping
- **CAT** — serial port, radio type presets (FT-950, FT-817, TS-590, K3…)
- **Layout** — save/load named profiles, snap-grid

---

## 📟 CAT Radio Interface

Configure via **⚙ Settings → CAT**. Supports:

- **Yaesu FT-950 / 2000 / DX series** — 8-digit FA command, default 38400 baud
- **Yaesu FT-817 / 857 / 897** — FA command
- **Kenwood / Elecraft** — 11-digit FA command
- **Icom CI-V** — binary BCD protocol

Live frequency displayed in the header bar. Click any frequency in the DX, EIBI, FT8, or SpyStations panel to tune directly.

---

## 🛰️ Satellite Tracking

- TLE data from SatNOGS DB and AMSAT (Amateur, ISS, Weather, CubeSat), with protection against download blocks and a warning when the data is outdated
- Orbit model: Kepler + J2 perturbation — within ~10 km of SGP4 over a day
- Real-time position, configurable past/future orbit paths, footprint
- **Satellite Passes panel** — next 24 hours: rise time, countdown, duration, max elevation, direction
- **Pass alert** — 5 minutes before a pass (on/off and minimum elevation in Settings → Alerts)
- **Zone ping** — tone when a satellite rises above / sets below your horizon

---

## ⚡ Lightning / QRN

- Live WebSocket feed from Blitzortung.org
- Animated ripple rings: central flash + 2 expanding rings (white → yellow → orange)
- QRN level based on strikes within 2000 km of QTH
- Configurable animation scale in **Settings → Lightning**
- Header alert + acoustic tick when storms are within threshold distance

---

## 📁 File Structure

```
HAMIOS/
├── HAMIOS5.py              ← Entry point
├── HAMIOS5.spec            ← PyInstaller build spec
├── hamios.ico
│
└── hamios5/                ← Python package
    ├── mainwindow.py       ← Main window + panel layout
    ├── mapview.py          ← Hardware-accelerated map (4096×2048)
    ├── layers.py           ← Lightning / Satellite / DX overlay layers
    ├── panels5.py          ← All floating panel widgets
    ├── charts.py           ← NOAA data manager + chart widgets
    ├── config.py           ← AppConfig dataclass (JSON persistence)
    ├── cat_interface.py    ← CAT serial protocol implementation
    ├── cat_monitor.py      ← CAT terminal window
    ├── settings_dialog.py  ← Settings dialog
    ├── sat_dialog.py       ← Satellite tracking dialog
    ├── spy_dialog.py       ← SpyStations dialog
    ├── eibi_dialog.py      ← EIBI shortwave browser
    ├── ft8_dialog.py       ← FT8/digital frequency reference
    ├── help_dialog.py      ← Searchable help
    └── theme.py            ← Dark theme constants
```

Auto-created runtime files (not in repository):

| File | Description |
|---|---|
| `hamios_config.json` | All settings, panel positions, CAT config |
| `worldmap_eq.jpg` | Standard resolution world map (auto-downloaded) |
| `worldmap_eq_hires.jpg` | 4K world map (auto-downloaded) |
| `hamios_tle.json` | Satellite TLE data (refreshed from CelesTrak) |
| `HAMIOS_history.csv` | 90-day band reliability history |

---

## 🙏 Data Sources

| Source | Data |
|---|---|
| [NOAA SWPC](https://www.swpc.noaa.gov/) | Solar data, K-index, Bz, X-ray, storm forecast |
| [DXWatch.com](https://dxwatch.com/) | Live DX cluster |
| [Blitzortung.org](https://www.blitzortung.org/) | Worldwide lightning detection (WebSocket) |
| [eibispace.de](https://www.eibispace.de/) | EIBI shortwave schedules (Eike Bierwirth) |
| [CelesTrak](https://celestrak.org/) | Satellite TLE data (Dr. T.S. Kelso) |
| [Wikimedia Commons](https://commons.wikimedia.org/) | NASA Blue Marble world map |

All connections use standard HTTPS/WebSocket. No personal data is transmitted.

---

## 📋 Changelog

### v5.8 — September 2026
- **HAM Antenna Designer v3.0.1** (📐 button), fully reviewed:
  - **Correct wire lengths**: insulation is applied relative to bare wire; earlier versions cut wire antennas 2–5 % too short
  - **IARU Region 1 or 2** band plan, 60 m added
  - **SWR** from the complex impedance, taken behind the balun/unun
  - **Matching networks** for real and complex loads, each verified, with E12 values
  - **Cable loss** for all 44 cables, including the extra loss from SWR on the line
  - **SWR sweep** of the antenna as built, and **radiation patterns** computed from the geometry over real ground
- **New antenna drawings**: radiator, counterpoise, feed line, balun/unun and ground point clearly marked, with no text over the drawing; day/night theme, 2D/3D, printable SVG export
- **New Smith-chart logo** for the antenna designer

### v5.7 — September 2026
- **One propagation model, calibrated on the real ionosphere**: nearest ionosonde (KC2G/GIRO) and NOAA D-RAP absorption; skip zone on short paths; day/night from the real sun at your QTH
- **Smart propagation advice**: recommendations confirmed by real WSPR, DX-cluster and PSKReporter spots, events, coming hours, explanatory tooltips, path on the map
- **Tiled panel layout**: four layouts (Map centre, Operating, Analysis, Default) and a layout lock
- **New panels**: Ionosondes (measured ionosphere) and Satellite Passes with an alert before each pass
- **New map layers**: propagation map from your QTH per band and NOAA D-RAP HF absorption; smooth OVATION aurora
- **Accuracy**: grey line and day/night terminator were up to ~6° (≈25 min) too far east — now within ~1°; satellite positions were hundreds of km off — now ~10 km
- **Data**: real WSPR spots via wspr.live, real-time solar wind (Bz), 27-day outlook; NOAA data only downloaded when it can have changed
- **UI**: checkboxes with an amber tick, dropdown arrows, remaining Dutch texts translated, HAM Antenna Designer follows the HAMIOS language
- **Performance and polish**: CPU use during operation ~120 % → ~25 %, propagation model 2.5× faster; fully bilingual (EIBI, FT8, SpyStations, CAT, Help); moon phase as seen from your QTH; menus close on outside click; new installations start without overlays

### v5.6 — September 2026
- Satellite TLE data from SatNOGS and AMSAT with protection against download blocks and a warning when outdated
- Map renders about twice as fast; mouse-over for DXCC prefixes and Maidenhead squares; FT8 frequencies in MHz

### v5.5 — July 2026
- **New antenna tool — HAM Antenna Designer**: the built-in antenna calculator has been replaced by the standalone HAM Antenna Designer (📡 Antenna button) — 20+ documented antenna designs (verticals, dipoles, EFHW, loops, Yagi, Moxon, quad, J-pole, SWL receive antennas), sourced formulas, build notes, schematic drawings, SWR table, Smith chart, radiation patterns and feedline-loss comparison
- **TLE caching fixed**: satellite TLE data is no longer re-downloaded at every startup — an existing cache is now detected correctly and only downloaded once when missing
- **TLE age display**: splash screen and Satellite window now show how old the cached TLE data is (e.g. "34 KB · 3 d"); manual refresh via ↻ button unchanged
- **Faster startup**: main window is no longer built twice when the splash screen is enabled — roughly halves startup time and removes duplicate background connections (Blitzortung WebSocket, timers)
- **EiBi language codes corrected**: `SWA` (Swahili) and `SWE` (Swedish) now translate correctly (previously dead `SW` entries)
- **Translation fix**: missing Dutch text for satellite cache status ("{n} satellieten uit cache")
- **Code quality**: large cleanup pass — unused imports, dead code and duplicate definitions removed across all modules; unit test suite repaired (39 tests green)

### v5.4 — June 2026
- **Resources Manager Tab**: New Settings tab to manage all online resource URLs (9 categories: Solar, Satellites, WSPR, DX, Lightning, Schedules, Map)
- **Resource Testing**: Per-URL connectivity test button showing HTTP status and timeout errors
- **Resource Investigation**: Discover alternative endpoints (mirror servers, backup APIs) with built-in guidelines
- **Automatic URL Saving**: Resource URL changes saved instantly without restart
- **Reset to Defaults**: Quick button to restore all URLs to HAMIOS defaults
- **Lightning Panel Improvements**: 
  - Separate enable/disable (WebSocket connection) from overlay visibility (map display)
  - Configurable font size for radius labels (5-72pt in Settings)
  - Independent control of connection vs. visibility
- **WSPR Sorting Fixes**: Numeric columns (frequency, SNR, distance, azimuth, time) now sort correctly with proper numeric comparison
- **Profile Loading**: Fixed config update when loading profiles; proper _save_cfg() implementation
- **Full Bilingual Documentation**: Help section covers all Resources Manager features in English & Dutch

### v5.3 — June 2026
- **Profile Management System**: Save/load complete workspaces (config + panel layout + window geometry) as named profiles or default backup
- **MUF/LUF Forecast Panel**: 24-hour Maximum/Minimum Usable Frequency visualization with gridlines, band-zone colors, and real-time indicator
- **WSPR Live Feed**: Real-time WSPR QSO table with sortable columns (callsign, grid, frequency, SNR, distance, path, UTC time)
- **Panel Visibility Button**: Quick 🪟 header button to toggle panel visibility without opening settings
- **Online Resource Monitoring**: 9-category connectivity check on splash screen (NOAA, CelesTrak, WSPRnet, DXWatch, PSK Reporter, Blitzortung, EIBI, Wikimedia, HamQSL)
- **Improved Headers**: Better contrast and organization across all panels
- **Graph Improvements**: MUF/LUF forecast now with band-zone background coloring, gridlines, and clean minimal design

### v5.2 — June 2026
- **EIBI**: list now sorted by kHz (numeric) by default; station name moved to second column
- **Satellite tracking**: configurable orbit path line width (Settings → Map)
- **Settings / Map tab**: all controls now apply live (no restart needed); labels fully translated EN/NL

### v5.1 — May 2026
- Header clock timezone derived automatically from QTH coordinates (via `timezonefinder`)
- Graceful fallback to OS system timezone if `timezonefinder` is not installed
- Splash screen checks: folder access (create/write/read/delete) + internet connectivity

### v5.0 — May 2026
- Complete rewrite to PySide6 / Qt6
- Hardware-accelerated world map — no PIL/Pillow dependency
- Ready-to-use EXE — no Python installation required

---

## 🤝 Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

*© 2026 Frank van Dijke · Open-source amateur radio software*
*Developed with [Claude AI](https://claude.ai) (Anthropic) · PySide6 · Python 3.10+*
