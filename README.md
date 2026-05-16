# 📡 HAMIOS v5.0

**HF Propagation & DX Monitor for Windows — rebuilt from scratch in PySide6**

> v5.0 · May 2026 · by PA3FVD / Frank van Dijke · *Developed with Claude AI (Anthropic)*

HAMIOS gives amateur radio operators real-time insight into HF propagation conditions, solar weather, DX cluster activity, shortwave schedules, satellite tracking, lightning detection, and direct radio control — all wrapped in a modern, fully customisable dark-theme GUI.

---

## ✨ What's new in v5.0

- Complete rewrite from **tkinter/PIL → PySide6 / Qt6** — hardware-accelerated, smooth, scalable
- 15 **freely floating, draggable and resizable panels** on a virtual desktop canvas
- **CAT radio interface** — tune your transceiver directly from EIBI, FT8 or SpyStations
- **Live Blitzortung lightning overlay** with QRN advice, distance alert, and proximity alarm
- **Satellite tracker** — real-time position, orbit paths, footprint, EME support
- **EIBI shortwave frequency browser** — searchable, sortable, one-click CAT tuning
- **FT8 / digital mode frequency reference** — all bands, all modes
- **SpyStations** — numbers station database with CAT tuning
- **Band history charts** (CSV) — 90-day archive, all 11 HF bands
- **Splash screen** with interactive "Continue" button

---

## 🖥️ Panels

| Panel | Description |
|-------|-------------|
| 🌍 World Map | Equirectangular map with overlays |
| ☀ Solar / Ionosphere | SFI, SSN, Kp, Bz, X-ray, solar wind |
| 📶 HF Band Reliability | Signal quality bars for 11 HF bands |
| 📻 Band Conditions | Colour-coded HF band overview |
| 🌩 Storm Forecast | Geomagnetic storm probability |
| 🗓 Band Opening Schedule | Band-by-band propagation times |
| 📈 Band History | 90-day HF band chart (all 11 bands) |
| ☀ Solar History | SFI / Kp trend chart |
| 🧲 Kp 48h | Geomagnetic index chart |
| ⚡ Bz 24h | IMF Bz chart |
| ☢ X-ray 24h | Solar X-ray flux chart |
| ⚡ Lightning | Blitzortung live feed · QRN level · proximity alert |
| 🔔 Alerts | Aggregated solar/propagation/weather alerts |
| 📡 Live DX Spots | DX cluster with band filter and heatmap |
| 💡 Propagation Advice | AI-style analysis cards per band |

---

## 🗺️ Map Overlays *(toggleable from header)*

- **Day/night terminator** with smooth transition
- **Gray line** (~1000 km twilight band)
- **Aurora oval** (IGRF-2025 geomagnetic dipole model, K-index based)
- **Sun position** with ray icon
- **Moon position** with live phase icon and QTH horizon visibility (▲/▼)
- **Maidenhead locator grid** (20° × 10°)
- **Live DX spots** on map (callsigns, colour by band)
- **Satellite positions**, orbit paths, footprints
- **Lightning strike overlay** (Blitzortung, fade animation)
- **Lightning radius circles** — red (alert threshold), orange (beep threshold)

---

## 📡 CAT Radio Interface

- Supports **Yaesu FT-950/2000/DX series** (8-digit FA command — confirmed working)
- Supports **Kenwood / Elecraft** (11-digit FA command)
- Supports **Icom CI-V** (binary BCD)
- Direct tuning from **EIBI** (AM mode), **FT8/digital** (USB mode), **SpyStations**
- **Serial monitor** with TX/RX log, manual command input, diagnostics
- **Radio identification** via `ID;` command (shows model name)
- Live **frequency display** in header from continuous FA polling
- Configurable **serial parameters** in CAT window and Settings

---

## 🛰️ Satellite Tracker

- TLE data from CelesTrak (Amateur, ISS, Weather, CubeSat)
- Real-time position, orbit paths (past + future, each independently configurable)
- **Footprint visualisation** — fills yellow (outside QTH), green (within range)
- Polar footprint rendered as single QPainterPath (no alpha artefacts)
- **"Geselecteerd" filter** — instantly show only your tracked satellites
- Selections and filter state saved automatically

---

## ⚡ Lightning / QRN

- Live WebSocket feed from **Blitzortung.org**
- Smooth 20 fps animation with quadratic fade
- **QRN level** based on strikes within 2000 km of QTH (not global count)
- **Red radius circle** on map — header alert when storms are within threshold
- **Orange radius circle** — configurable acoustic alert radius
- **Geiger-counter tick sound** (2800 Hz / 5 ms) — Windows, configurable
- QRN level changes forwarded to Alerts panel

---

## 🔊 EIBI & Digital Mode Frequencies

- **EIBI shortwave schedules** — downloaded from eibispace.de, filtered by band/time/language
- Auto-sets **AM mode** via CAT on EIBI click
- **FT8 / FT4 / WSPR / JS8Call / MSK144 / Q65 / JT65 / JT9** reference table — 70 entries
- Auto-sets **USB mode** via CAT on FT8 click
- **SpyStations** — 8+ pre-loaded numbers stations with CAT tuning per frequency

---

## ⚙️ Settings

- **Station** — callsign, QTH (lat/lon/locator), mode, power, antenna
- **Panels** — visibility toggle per panel
- **Map** — overlay toggles (also accessible via header button), font sizes, snap grid
- **Lightning** — enable/disable, fade, QRN radius, beep radius, update interval
- **Alerts** — K-index threshold, X-flare alert, FIFO limit
- **CAT** — port (auto-detected), baud, bits, parity, stop, radio type, CI-V address, presets
- **Layout** — save/load named profiles, reset to default
- **About** — dependency status, splash toggle

---

## 🚀 Requirements

| Package | Required | Install |
|---------|----------|---------|
| PySide6 | ✅ Yes | `pip install PySide6` |
| pyserial | Optional | `pip install pyserial` (CAT interface) |
| websocket-client | Optional | `pip install websocket-client` (lightning) |

**Python 3.10+** · **Windows 10/11** (primary platform)

---

## 📦 Installation

```bash
# Clone or download to a local folder
git clone https://github.com/PA3FVD/HAMIOS.git
cd HAMIOS

# Install dependencies
pip install -r requirements.txt

# Run
python HAMIOS5.py
```

Or simply double-click **`start.bat`** in the `HAMIOS5/` distribution folder.

---

## 📁 File structure

```
HAMIOS5/
├── HAMIOS5.py              ← Entry point
├── start.bat               ← Windows launcher
├── requirements.txt
├── worldmap_eq.jpg         ← World map (required)
├── hamios.ico
│
├── hamios5/                ← Python package
│   ├── mainwindow.py       ← HAMIOSMainWindow
│   ├── mapview.py          ← Map + overlay layers
│   ├── layers.py           ← Lightning / Satellite / DX layers
│   ├── panels5.py          ← All floating panel widgets
│   ├── charts.py           ← NOAA data manager + chart widgets
│   ├── config.py           ← AppConfig dataclass
│   ├── cat_interface.py    ← CAT serial protocol
│   ├── cat_monitor.py      ← CAT serial monitor window
│   ├── eibi_dialog.py      ← EIBI shortwave browser
│   ├── ft8_dialog.py       ← FT8/digital frequency reference
│   ├── sat_dialog.py       ← Satellite tracking dialog
│   ├── spy_dialog.py       ← SpyStations dialog
│   ├── settings_dialog.py  ← Settings dialog
│   ├── geometry.py         ← Window geometry persistence
│   ├── history.py          ← Band history CSV
│   ├── theme.py            ← Dark theme + QSS
│   └── ...
│
└── (auto-created on first run)
    ├── hamios_config.json
    ├── hamios_layouts.json
    ├── HAMIOS_history.csv
    └── hamios_tle.json
```

---

## 📜 Changelog

See [`changelog_v5.txt`](changelog_v5.txt) for the full v5 change log.

---

## 🙏 Credits

- **Solar data** — NOAA SWPC (Space Weather Prediction Center)
- **Lightning** — Blitzortung.org community network
- **EIBI schedules** — eibispace.de (Eike Bierwirth)
- **DX cluster** — DXWatch.com
- **Satellite TLE** — CelesTrak (Dr. T.S. Kelso)
- **World map** — NASA Blue Marble equirectangular
- **Developed with** — Claude AI (Anthropic), PySide6, Python

---

*© 2026 Frank van Dijke (PA3FVD) · HAMIOS is open-source amateur radio software*
