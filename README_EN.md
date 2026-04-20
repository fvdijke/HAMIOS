# 📡 HAMIOS v2.3
<img width="1743" height="1416" alt="HAMIOS v2 3" src="https://github.com/user-attachments/assets/3045d73a-9008-43d8-9dea-3d3fd5102792" />

**Multilingual + Multi overlay**
<img width="1743" height="1416" alt="HAMIOS-ALL v2 3" src="https://github.com/user-attachments/assets/4250a620-1bac-4867-9d78-0ac172a26e89" />

**HAM radio propagation and DX monitor for Windows**

> v2.3 — Propagation path map · Bz 24h chart · Selectable notifications · Aurora ring overlay · WSPR/PSKReporter spots · DX spot markers · 14 languages via external language packs

*Conceived by Frank van Dijke · Developed with Claude AI*

HAMIOS gives radio amateurs real-time insight into HF propagation, solar activity and DX opportunities — wrapped in a modern dark GUI that fits the screen on startup.

---

## ✨ Features

### 🌍 Interactive World Map
- Equirectangular NASA map, automatically downloaded on first use
- **Always correct 2:1 aspect ratio** — no horizontal distortion
- **Day/night terminator** with soft transition zone
- **Gray line** (amber band, ~1000 km wide)
- **Sun and moon position** (geocentric calculation)
- **QTH marker** (blue crosshair) — lat/lon configurable in header
- **Great-circle path**: click on map → distance + bearing + **band quality for that path**
- **ITU region overlay** R1/R2/R3 (official ITU RR Art. 5)
- **Maidenhead locator grid** (20° × 10°, labels AA–RR)
- **Callsign prefix layer** (~110 DXCC entities)
- **Zoom/pan**: scroll wheel 1×–8×, click+drag to pan, right-click to reset
- **Map checkboxes** (Sun, Moon, Gray line, Aurora, WSPR, Spots, ITU, CS, Locator) in a dedicated row **below the map**

### 🛰️ Propagation Path Map
Click a destination on the map for an instant path analysis:
- **Band quality** calculated at the midpoint of the great-circle path
- Day/night correction at the midpoint (correct ionospheric conditions)
- Number of hops estimated (≈ distance / 3500 km)
- Top-5 open bands shown: `↳  8,847 km / 3 hops / day  ▸  20m 87%  ·  17m 72%  ·  15m 54%  (MUF 24.1 MHz)`
- **Great-circle line colour follows the best band**

### 🌌 Aurora Ring Overlay
- Magnetic aurora oval based on K-index — Feldstein/Holzworth spherical trigonometry (IGRF-2025)
- Both hemispheres as a true oval
- **Colour by K-index**: green (K < 3) · yellow (K 3–5) · red (K ≥ 6)
- **Soft glow** — fade effect in 6 layers (same style as gray line)

### 🔵 WSPR / PSKReporter Spots on Map
- Live propagation paths from **wspr.rocks** (WSPR) and **pskreporter.info** (FT8/FT4)
- Connection lines: **colour = band**, **thickness = SNR**

### 📍 DX Spot Markers on Map
- Active DX cluster spots: dot at DXCC centroid + line to spotter, colour-coded by band
- Click a dot to show callsign, frequency and comment as a pop-up

### 🌞 Solar & Ionosphere Data

| Parameter | Source | Description |
|-----------|--------|-------------|
| SFI | hamqsl.com | Solar Flux Index (10.7 cm) |
| SSN | hamqsl.com | Sunspot Number |
| A-index | hamqsl.com | Daily geomagnetic activity |
| K-index | hamqsl.com | 3-hour geomagnetic activity (0–9) |
| X-ray | hamqsl.com | GOES X-ray flux (A/B/C/M/X class) |
| MUF | internal model | Maximum Usable Frequency (calculated) |
| LUF | internal model | Lowest Usable Frequency (calculated) |
| Solar wind speed | NOAA SWPC | km/s via DSCOVR/ACE |
| Bz | NOAA SWPC | Interplanetary magnetic field Z-component (nT) |

### 📊 Bz 24-hour Mini Chart
- **Blue** = positive Bz (favourable) · **Red** = negative Bz (geo-effective)
- 240 data points over 24 hours · Y-labels −20 / 0 / +20 nT
- Enlarged chart area for better readability

### 📶 HF Band Reliability
- Internal MUF/LUF model based on SFI, SSN, K-index and QTH latitude
- SNR budget corrected for **mode**, **power** and **antenna**
- Colour bars: green ≥ 60 % · yellow 30–59 % · red 1–29 % · grey closed
- Licence class per band (N = Novice/Foundation · F = Full/HAREC)

### 🔔 Notifications & Alerts — fully selectable

Each notification type can be **individually enabled or disabled** via a checkbox in the solar panel:

| Notification | Setting | Description |
|--------------|---------|-------------|
| ⚠️ K-index storm | Checkbox + threshold (spinbox 1–9) | Alert when K rises above threshold |
| 📡 Band opened | Checkbox + threshold (spinbox 10–90 %) | Alert when band opens |
| ☢️ X-flare / SWF | Checkbox | M/X-class flare detection |
| 🟣 PCA / Proton event | Checkbox | Polar Cap Absorption alert |

All thresholds and on/off states are saved in `HAMIOS.ini`.

### 🔌 CAT Interface *(temporarily disabled)*

> ⚠️ The CAT interface is temporarily disabled pending further development and stability testing. The code is intact — functionality will be completed in a future release.

### 🕐 Band Opening Schedule
- 24-hour heatmap for all 11 HF bands
- Time axis in local time (CET/CEST), current time marked

### 📈 Band History
- Time chart of all HF bands (%) — 90 days stored in CSV
- Time range: Hours · Days · Weeks · Months

### 📻 Live DX Spots
- JSON feed from dxwatch.com, refreshed every 2 minutes
- Columns: UTC · Band · DX · MHz · Spotter · Comment

### 💡 Propagation Analysis & Advice
12 analysis cards in 3 columns × 4 rows, automatically updated.

| # | Card | Content |
|---|------|---------|
| 1 | 📡 Best bands | Top-5 open bands with quality percentage |
| 2 | ✅/⚠️ Geo-storm | K + A-index, routing advice, severity |
| 3 | ☀️ Solar activity | SFI + SSN, solar cycle phase |
| 4 | 💨 Solar wind | Speed + Bz impact |
| 5 | ☢️ X-flare/SWF | X-ray class, recovery estimate |
| 6 | 📶 Ionosphere | MUF, LUF estimate, F2-layer |
| 7 | 🌅 Day/night | Gray-line time windows per hour block |
| 8 | 🔧 Mode advice | FT8 vs SSB/CW based on SNR budget |
| 9 | 🧲 Absorption | Auroral absorption polar routes (QTH lat) |
| 10 | 📊 Overall score | Combined propagation assessment |

### 🌐 Multilingual
**14 languages** via external language packs (`langs/*.json`).

| Code | Language | Code | Language |
|------|----------|------|----------|
| EN | English *(built-in)* | NO | Norsk |
| NL | Nederlands | PL | Polski |
| DE | Deutsch | SV | Svenska |
| FR | Français | DA | Dansk |
| IT | Italiano | FI | Suomi |
| ES | Español | PT | Português |
| JA | 日本語 | RU | Русский |

### ⚙️ Other
- **System tray**: minimise to tray, tray notifications
- **Tooltips** explaining each solar parameter
- **Auto-refresh**: Off / 30 s / 1 min / 5 min / 10 min / 30 min / 1 hour
- **Scrolling ticker** with current propagation tips
- All settings saved in `HAMIOS.ini`

---

## 🖥️ Installation

### Requirements
```bash
pip install pillow
```
Optional (system tray):
```bash
pip install pystray
```

### Run
```bash
python HAMIOS.py
```

### Standalone EXE (Windows) — recommended
Download `HAMIOS.exe` from the [latest release](https://github.com/fvdijke/HAMIOS/releases) and run directly. No Python required.

> **Note**: place the `langs/` folder next to the EXE so language packs are available.

---

## 🔭 Propagation Model

```
foF2 = 4.0 + (SFI − 70) × 0.065 + SSN × 0.012
MUF  = foF2 × latitude-factor × day/night-factor × 3.8
LUF  = (3.5 + K × 0.8) × auroral-factor / 10^(SNR/20)
```

**Band quality**: optimum around 55 % of the MUF/LUF window → 100 %.

---

## ⌨️ Mouse Interaction

| Action | Effect |
|--------|--------|
| Scroll wheel on map | Zoom 1×–8× |
| Click + drag on map | Pan viewport |
| Left-click on map | Great-circle path + path propagation |
| Right-click on map | Reset zoom/pan · clear path |
| Hover on map/bands/chart | Detailed tooltip |
| Click legend label | Toggle band in history chart |

---

## 💻 System Requirements

| | Minimum | Recommended |
|-|---------|------------|
| OS | Windows 10 | Windows 11 |
| Screen resolution | 1280 × 800 | 1920 × 1080 |
| Python | 3.10 | 3.12+ |
| Internet | Required (data feeds) | — |

---

## 🔧 Future Ideas

- Stabilise CAT interface (Yaesu/Kenwood/Icom)
- SDR integration
- Logging link (ADIF/WSJTX)
- Satellite tracking

---

## 📜 Licence

Free to use for personal, non-commercial amateur radio use.

---

*73 de PA3FVD · good DX!*
