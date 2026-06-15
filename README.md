<p align="center">
<img width="692" height="707" alt="2026-06-15 13_51_00-HAMIOS" src="https://github.com/user-attachments/assets/66626bc2-40f5-41aa-a80e-9c3fbd28e76f" />

</p>

# HF Propagation & Atmosphere Monitor

**Real-time HF propagation and DX monitor for amateur radio operators — Windows 10/11**

> v5.3 · June 2026 · Frank van Dijke · *Developed with Claude AI (Anthropic)*

[![Website](https://img.shields.io/badge/website-hamios.space-orange)](https://hamios.space)
[![Release](https://img.shields.io/github/v/release/fvdijke/HAMIOS?label=latest)](https://github.com/fvdijke/HAMIOS/releases/latest)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-blue)](https://github.com/fvdijke/HAMIOS/releases/latest)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![Language](https://img.shields.io/badge/language-EN%20%7C%20NL-green)](https://github.com/fvdijke/HAMIOS)

---
  <img width="3155" height="1683" alt="2026-06-15 13_51_27-HF Propagation   Atmosphere Monitor" src="https://github.com/user-attachments/assets/04fc0a87-3e2d-4600-bc87-eadce8139d6c" />![Uploading 2026-06-15 13_51_00-HAMIOS.png…]()

## Overview

HF Propagation & Atmosphere Monitor gives amateur radio operators real-time insight into HF propagation conditions, solar weather, DX cluster activity, shortwave schedules, satellite tracking, lightning detection, and direct radio control — all in a modern, fully customisable dark-theme GUI built with PySide6/Qt6.

**Fully bilingual** — switch between English and Dutch at any time via Settings → About.

---

## ✨ Features

| Category | Description |
|---|---|
| ☀ **Solar / Ionosphere** | SFI, SSN, Kp, A-index, Bz, solar wind, X-ray class — colour-coded with full parameter names |
| 📶 **HF Band Reliability** | Signal quality bars for 11 HF bands (160m–6m), MUF/LUF, click to tune via CAT |
| 📻 **Band Conditions** | Day/night conditions per band, 24h opening schedule heatmap |
| 🌩 **Storm Forecast** | NOAA 3-day geomagnetic storm probability (G1–G4+) with HAM radio impact tooltips |
| 📈 **Band / Solar History** | 90-day CSV archive, interactive 24h/7d/30d/1y range selector, K-index overlay |
| 📈 **MUF/LUF Forecast** | **NEW**: 24-hour Maximum/Minimum Usable Frequency with band-zone visualization, gridlines, real-time indicator |
| 🛰 **WSPR Live Feed** | **NEW**: Real-time WSPR QSO table with sortable columns (call, grid, distance, time, SNR) |
| 📡 **Live DX Spots** | Real-time DX cluster from DXWatch.com (100 spots), band/continent filter, heatmap, click for info |
| 📡 **PSKReporter** | Real-time FT8/FT4 propagation paths from PSKReporter.info — thousands of paths with SNR |
| 💡 **Propagation Advice** | AI-style analysis cards per band with real-time solar data analysis |
| 🌍 **World Map** | 4096×2048 map with overlays — world map auto-downloaded at first start |
| 🌐 **Bilingual** | Full English / Dutch interface — switch instantly via Settings → About |
| 🛰 **Satellite Tracking** | TLE from CelesTrak, real-time position, orbit paths, footprint, QTH zone ping |
| ⚡ **Lightning Detection** | Live Blitzortung.org feed, animated ripple rings, QRN advice, proximity alert |
| 🔔 **Alerts** | Aggregated solar / propagation / weather / satellite alerts |
| 📻 **EIBI Shortwave** | Searchable schedule, auto AM-mode CAT tuning |
| 📡 **FT8 / Digital** | Reference table for FT8/FT4/WSPR/JS8Call and more |
| 🕵 **SpyStations** | Numbers stations database with CAT tuning |
| 📟 **CAT Interface** | Yaesu, Kenwood/Elecraft, Icom CI-V — live frequency display in header |
| 💾 **Profile Management** | **NEW**: Save complete workspaces (all settings + layout + window geometry) as named profiles or default backup |
| 🪟 **Panel Visibility** | **NEW**: Quick header button to show/hide panels without reopening settings |

---

## 🗺️ Map Overlays

Toggleable via the **🗺 Overlays** button in the header:

- Day/night terminator with grayline band
- Aurora oval (IGRF-2025 geomagnetic dipole model, K-index based)
- Sun and Moon position with live phase icon and QTH horizon indicator (▲/▼)
- Maidenhead locator grid (configurable font size)
- Graticule (configurable 10° / 20° / 30° step)
- Live DX spots with callsign labels and animated connection lines (click for info)
- **PSKReporter** — real-time FT8/FT4 propagation paths coloured by band (click for info)
- **DXCC callsign country codes (extended)** — prefix + country name labels at ~150 DXCC entity positions; click any label for a popup listing all prefixes for that country (configurable font size)
- Satellite positions, orbit paths, footprints
- Lightning strikes with animated ripple rings
- Alert radius circles (warning + beep threshold)

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

- TLE data from CelesTrak (Amateur, ISS, Weather, CubeSat)
- Real-time position, configurable past/future orbit paths
- Footprint: yellow (QTH outside range) / green (QTH in range)
- **Selection filter** — show only your selected satellites
- **Zone ping** — ascending tone when a satellite enters your QTH zone, descending tone on exit

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
