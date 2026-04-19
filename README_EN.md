# 📡 HAMIOS v2.3
<img width="1743" height="1416" alt="HAMIOS v2 3" src="https://github.com/user-attachments/assets/3045d73a-9008-43d8-9dea-3d3fd5102792" />

**Multilingual + Multi overlay**
<img width="1743" height="1416" alt="HAMIOS-ALL v2 3" src="https://github.com/user-attachments/assets/4250a620-1bac-4867-9d78-0ac172a26e89" />

**HAM radio propagation and DX monitor for Windows**

> v2.3 — Propagation path map · Bz 24h chart · Band-opening notifications · Aurora ring overlay · WSPR/PSKReporter spots · DX spot markers · 14 languages via external language packs

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
- Render cache with low-res masks for smooth zoom and pan
- **Map checkboxes** (Sun, Moon, Gray line, Aurora, WSPR, Spots, ITU, CS, Locator) shown in a dedicated row **below the map**

### 🛰️ Propagation Path Map
Click a destination on the map for an instant path analysis:
- **Band quality** calculated at the midpoint of the great-circle path
- Day/night correction at the midpoint (correct ionospheric conditions)
- Number of hops estimated (≈ distance / 3500 km)
- Top-5 open bands shown: `↳  8,847 km / 3 hops / day  ▸  20m 87%  ·  17m 72%  ·  15m 54%  (MUF 24.1 MHz)`
- **Great-circle line colour follows the best band** (green = 20m, yellow = 17m, red = 10m, …)

### 🌌 Aurora Ring Overlay
- Magnetic aurora oval on the map based on the K-index
- Calculated via **Feldstein/Holzworth** spherical trigonometry on the geomagnetic dipole pole (IGRF-2025: North 80.65°N/287.35°E, South 80.65°S/107.35°E)
- Both hemispheres as a true oval (not a simple latitude band)
- **Colour by K-index**: green (K < 3) · yellow (K 3–5) · red (K ≥ 6)
- K=0 → oval at ~67° geomag. latitude · K=9 → ~44° (equatorward)
- **Soft glow** (fade effect, 6 layers from wide+transparent to narrow+opaque — same style as gray line)

### 🔵 WSPR / PSKReporter Spots on Map
- Live propagation paths from **wspr.rocks** (WSPR) and **pskreporter.info** (FT8/FT4)
- Connection lines on the world map: **colour = band**, **thickness = SNR**
- Toggleable via checkbox below the map
- Shows real measured propagation rather than model values only

### 📍 DX Spot Markers on Map
- Active DX cluster spots as lines: dot at DX location (DXCC centroid) + line to spotter
- Colour-coded by band
- Toggle via **"Spots"** checkbox below the map
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

- K-index colours **orange** (K 3–4) or **red** (K 5+)
- Bz colours **orange** (≤ −10 nT) or **red** (≤ −20 nT)
- K-index alert at configurable threshold (spinbox)
- Band-opening notification at configurable quality threshold
- X-flare detection → SWF warning in panel and system tray

### 📊 Bz 24-hour Mini Chart
Mini time chart at the bottom of the solar panel:
- **Blue** = positive Bz (northward, favourable)
- **Red** = negative Bz (southward, geo-effective)
- Zero axis dashed, Y-labels −20 / 0 / +20 nT
- Current Bz value top-right with colour code
- Data from **NOAA SWPC** `mag-1-day.json`, 240 points over 24 hours

### 📶 HF Band Reliability
- Internal MUF/LUF model based on SFI, SSN, K-index and QTH latitude
- SNR budget corrected for **mode**, **power** and **antenna**
- Modes: SSB (0 dB) · CW (+10 dB) · FT8 (+25 dB) · AM (−6 dB)
- Power levels: 5 W – 1 kW · Antennas: Dipole, EFHW, Yagi, Beam, Quad, …
- Colour bars: green ≥ 60 % · yellow 30–59 % · red 1–29 % · grey closed
- Licence class per band (N = Novice/Foundation · F = Full/HAREC)
- FT8 frequency and recommended modes per band

### 🔔 Notifications & Alerts
- **K-index alarm**: tray notification when configurable threshold is exceeded (spinbox 1–9)
- **Band-opening notification**: alert when a band opens above configurable threshold
  - Spinbox "Band open ≥" (10–90%, step 5%, default 40%)
  - Example: `📡 Band opened — 20m (78%) — quality ≥ 40%`
- **X-flare warning**: detection of M/X-class flares with recovery estimate
- **PCA alert**: Polar Cap Absorption at elevated proton flux
- All thresholds saved in `HAMIOS.ini`

### 🔌 CAT Interface *(experimental — not yet stable)*

> ⚠️ **Note**: The CAT interface is experimental and may not work reliably with all radios. Use at your own risk. Feedback and test reports are welcome.

Configurable via the **CAT** button in the header. Serial USB only — no TCP.

| Radio type | Protocol | Command |
|------------|----------|---------|
| Yaesu FT-950 etc. | Yaesu CAT | `FA{9 digits};` |
| Kenwood / Elecraft | Kenwood CAT | `FA{11 digits};` |
| Icom | CI-V binary BCD | configurable address (0x70 default) |

- Click a band bar → sends the start frequency to the radio (when CAT is enabled)
- VFO-A/B are read **once** at startup and after saving settings
- VFO-A/B frequency shown below the band bars
- **CAT terminal window**: enable "Terminal" next to the VFO display
  - 🟡 Yellow `▶` = sent commands
  - 🔵 Blue `◀` = received data from the radio

### 🕐 Band Opening Schedule
- 24-hour heatmap for all 11 HF bands
- Time axis in local time (CET/CEST), current time marked
- Hover tooltip: band · hour · quality % · FT8 freq · modes

### 📈 Band History
- Time chart of all HF bands (%) — 90 days stored in CSV
- Time range: Hours · Days · Weeks · Months
- Clickable legend, hover tooltip per timestamp

### 📻 Live DX Spots
- JSON feed from dxwatch.com, refreshed every 2 minutes
- Filtered by HF bands · Own continent toggle
- Columns: UTC · Band · DX · MHz · Spotter · Comment
- Scrollable with mouse wheel

### 💡 Propagation Analysis & Advice
12 analysis cards in 3 columns × 4 rows, automatically updated.
**Yellow dot** top-right of card = new data available.

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
**14 languages** supported via an external language pack system — switchable in the header.

English is the built-in default. All other languages are automatically loaded from `langs/*.json` files at startup. Installed language packs appear directly in the language menu; extra packs can easily be added or downloaded.

| Code | Language |
|------|----------|
| EN | English *(built-in)* |
| NL | Nederlands |
| DE | Deutsch |
| FR | Français |
| IT | Italiano |
| ES | Español |
| NO | Norsk |
| PL | Polski |
| SV | Svenska |
| DA | Dansk |
| FI | Suomi |
| PT | Português |
| JA | 日本語 |
| RU | Русский |

All interface texts, analyses, help texts and tooltips are fully translated per language.

**Create your own language pack**: copy an existing `.json` file from `langs/`, adjust `meta.code` and `meta.name`, and translate the `strings` and `solar_tips` sections. HAMIOS detects the pack automatically on next start.

### ⚙️ Other
- **System tray**: minimise to tray, notifications for band openings and K-index
- **Tooltips** explaining each solar parameter (350 ms delay, screen-edge detection)
- **Auto-refresh**: Off / 30 s / 1 min / 5 min / 10 min / 30 min / 1 hour
- **Scrolling ticker** at the bottom with current propagation tips (on/off via checkbox)
- **New data indicator**: yellow dot in advice card when fresh data arrives
- All settings saved in `HAMIOS.ini` — persistent between sessions
- Window automatically fits screen size on startup

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
Optional (CAT interface):
```bash
pip install pyserial
```

### Run
```bash
python HAMIOS.py
```

### Standalone EXE (Windows) — recommended
Download `HAMIOS.exe` from the [latest release](https://github.com/fvdijke/HAMIOS/releases) and run directly. No Python required.

Or build yourself:
```bash
pip install pyinstaller
pyinstaller HAMIOS.spec
# → dist\HAMIOS.exe
```

> **Note**: make sure the `langs/` folder is placed next to the EXE so language packs are available.

---

## 🔭 Propagation Model

**MUF** (Maximum Usable Frequency):
```
foF2 = 4.0 + (SFI − 70) × 0.065 + SSN × 0.012
MUF  = foF2 × latitude-factor × day/night-factor × 3.8
```

**LUF** (Lowest Usable Frequency):
```
LUF = (3.5 + K × 0.8) × auroral-factor / 10^(SNR/20)
```

**Band quality**: optimum around 55 % of the MUF/LUF window → 100 %.

**Propagation path**: midpoint of the great-circle path used for MUF/LUF calculation, with day/night correction at that midpoint.

---

## ⌨️ Mouse Interaction

| Action | Effect |
|--------|--------|
| Scroll wheel on map | Zoom 1×–8× (cursor-centred) |
| Click + drag on map | Pan viewport |
| Left-click on map | Set great-circle path + path propagation |
| Right-click on map | Reset zoom/pan · clear great-circle path |
| Scroll wheel on DX panel | Scroll through spot list |
| Hover on map/bands/chart | Detailed tooltip |
| Click legend label | Toggle band in history chart |
| Click band bar (CAT on) | Send start frequency to radio |

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

- Stabilise CAT interface (full Yaesu/Kenwood/Icom support)
- SDR integration
- Logging link (ADIF/WSJTX)
- Satellite tracking
- Web version

---

## 📜 Licence

Free to use for personal, non-commercial amateur radio use.
For commercial applications: please get in touch.

---

## 🤝 Contributing

Pull requests, ideas and improvements are welcome.
This project thrives on experimentation — just like the hobby itself.

---

*73 de PA3FVD · good DX!*
