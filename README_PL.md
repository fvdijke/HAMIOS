# 📡 HAMIOS v3.2

**Monitor propagacji KF i DX dla Windows**

> v3.2 — Całkowity przeprojekt interfejsu · Mapa świata wycentrowana · Kolumna DX Spots pełnej wysokości · Paski pasma z gradientem · Wykres Bz jako dedykowany panel · 14 języków przez zewnętrzne pakiety

*Conceived by Frank van Dijke · Developed with Claude AI*

HAMIOS zapewnia krótkofalowcom wgląd w czasie rzeczywistym w propagację KF, aktywność słoneczną i możliwości DX — w nowoczesnym ciemnym interfejsie graficznym.

---

## ✨ Funkcje

### 🌍 Interaktywna mapa świata *(wycentrowana w oknie)*
- Mapa NASA ekwirektangularna, pobierana automatycznie przy pierwszym użyciu
- **Stała wysokość (380 px)** z prawidłowym renderowaniem 2:1 — bez poziomowych zniekształceń
- **Terminator dzień/noc** z miękką strefą przejściową
- **Szara linia** (pas bursztynowy, ~1000 km szerokości)
- **Pozycja słońca i księżyca** (obliczenia geocentryczne)
- **Znacznik QTH** (niebieski celownik) — szer./dług. konfigurowalne w nagłówku
- **Ścieżka ortodromy**: klik na mapie → odległość + namiar + **jakość pasma dla tej trasy**
- **Nakładka regionów ITU** R1/R2/R3 (oficjalny ITU RR Art. 5)
- **Siatka lokatorów Maidenhead** (20° × 10°, oznaczenia AA–RR)
- **Warstwa prefiksów znaków wywoławczych** (~110 podmiotów DXCC)
- **Zoom/panoramowanie**: kółko myszy 1×–8×, klik+przeciągnij, prawy klik aby zresetować
- **Nakładki mapy pogrupowane** poniżej mapy:
  - *Display:* Sun · Moon · Gray line · Aurora
  - *Data:* WSPR · Spots · CS · Locator

### 🛰️ Propagation Path Map
- **Band quality** calculated at the midpoint of the great-circle path
- Day/night correction at the midpoint
- Number of hops estimated (≈ distance / 3500 km)
- Top-5 open bands: `↳  8,847 km / 3 hops / day  ▸  20m 87%  ·  17m 72%  ·  15m 54%  (MUF 24.1 MHz)`
- **Great-circle line colour follows the best band**

### 🌌 Aurora Ring Overlay
- Magnetic aurora oval based on K-index (Feldstein/Holzworth, IGRF-2025)
- **Colour by K-index**: green (K < 3) · yellow (K 3–5) · red (K ≥ 6)

### 🔵 WSPR / PSKReporter Spots on Map
- Live propagation paths from **wspr.rocks** (WSPR) and **pskreporter.info** (FT8/FT4)
- Connection lines: **colour = band**, **thickness = SNR**

### 📍 DX Spot Markers on Map
- Active DX cluster spots: dot at DX location + line to spotter, colour-coded by band
- Click a dot to show callsign, frequency and comment

### 🌞 Dane słoneczne i jonosferyczne

| Parameter | Source | Description |
|-----------|--------|-------------|
| SFI | hamqsl.com | Solar Flux Index (10.7 cm) |
| SSN | hamqsl.com | Sunspot Number |
| A-index | hamqsl.com | Daily geomagnetic activity |
| K-index | hamqsl.com | 3-hour geomagnetic activity (0–9) |
| X-ray | hamqsl.com | GOES X-ray flux (A/B/C/M/X class) |
| MUF | internal model | Maximum Usable Frequency |
| LUF | internal model | Lowest Usable Frequency |
| Solar wind speed | NOAA SWPC | km/s via DSCOVR/ACE |
| Bz | NOAA SWPC | Interplanetary magnetic field Z-component (nT) |
| foF2 | GIRO/LGDC | Measured F2-layer critical frequency (ionosonde) |

### 📊 Bz 24-hour Chart *(dedicated panel)*
- **Blue** = positive Bz (favourable) · **Red** = negative Bz (geo-effective)
- Y-labels −20 / 0 / +20 nT · scales automatically with the panel

### 📶 HF Band Reliability *(redesigned in v3.0)*
- Internal MUF/LUF model based on SFI, SSN, K-index and QTH latitude
- SNR budget corrected for **mode**, **power** and **antenna**
- **Gradient bars in band-specific colour** (light → dark) with gloss line
- Band name **bold and in band colour** — every band has its own identity
- Columns: start MHz · modes · FT8 frequency

### 🔔 Notifications & Alerts

| Notification | Setting | Description |
|-------------|---------|-------------|
| ⚠️ K-index storm | Checkbox + threshold (1–9) | Alert when K rises above threshold |
| 📡 Band open | Checkbox + threshold (10–90 %) | Alert when band opens |

Thresholds are saved to `HAMIOS.ini`.

### 🔌 CAT Interface *(temporarily disabled)*
> The CAT interface is temporarily disabled pending further development. Code is intact and will be completed in a future release.

### 🕐 Band Opening Schedule
- 24-hour heatmap for all 11 HF bands
- Time axis in local time (CET/CEST), current time highlighted
- Hover tooltip: band · hour · quality · modes · FT8 frequency

### 📈 Band History
- Time graph of all HF bands (%) — 90 days kept in CSV
- Time range: Hours · Days · Weeks · Months
- Clickable legend to toggle individual bands

### 📡 Live DX Spots *(full-height right column)*
- JSON feed from dxwatch.com, refreshed every 5 minutes
- Columns: UTC · Band · DX · MHz · Spotter · Comment
- **Own-continent filter** — show only spots from your own continent
- **Heatmap mode**: band × UTC-hour activity pattern (24h buffer)
- Spots also shown as markers on the world map (toggleable)

### 💡 Propagation Analysis & Advice
12 analysis cards in 3 columns × 4 rows.

| # | Card | Contents |
|---|------|----------|
| 1 | 📡 Best bands | Top-5 open bands with quality percentage |
| 2 | ✅/⚠️ Geo-storm | K + A-index, route advice, severity |
| 3 | ☀️ Solar activity | SFI + SSN, solar cycle phase |
| 4 | 💨 Solar wind | Speed + Bz impact |
| 5 | ☢️ X-flare/SWF | X-ray class, recovery estimate |
| 6 | 📶 Ionosphere | MUF, LUF, F2 layer |
| 7 | 🌅 Day/night | Gray-line time windows |
| 8 | 🔧 Mode advice | FT8 vs SSB/CW based on SNR budget |
| 9 | 🧲 Absorption | Auroral absorption polar routes |
| 10 | 📊 Overall score | Composite propagation rating |

### 🌐 Multilingual
**14 languages** via external language pack system (`langs/*.json`).

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
- **Dynamic themes**: Midnight · DeepOcean · HighContrast
- **System tray**: minimise to tray, tray notifications
- **Tooltips** with explanation per solar parameter
- **Auto-refresh**: Off / 30 s / 1 min / 5 min / 10 min / 30 min / 1 hour
- **Scrolling ticker** with current propagation tips
- All settings saved to `HAMIOS.ini`

---

## 🖥️ Layout (v3.0)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ HEADER  (title · exit · CAT · interval · lang · QTH · theme · time)     │
├──────────┬──────────────────────────────────┬────────────┬──────────────┤
│  Solar   │      World Map (central)         │    HF      │              │
│ Ionosph. │      380 px tall, zoom/pan       │    Band    │   DX Spots   │
│  200 px  │   Display: Sun Moon Graylijn     │ Reliability│  (full       │
│          │   Data: WSPR Spots CS Locator    │   420 px   │  height)     │
│          ├──────────────────────────────────┤            │   360 px     │
│          │  Schedule │  Band Hist  │  Bz   │            │              │
│          │   (1/3)   │    (1/3)    │ (1/3) │            │              │
├──────────┴──────────────────────────────────┴────────────┤              │
│              Propagation Analysis & Advice                │              │
├───────────────────────────────────────────────────────────┴──────────────┤
│ TICKER                                                                    │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Instalacja

### Krok 1 — Wymagania Python

```bash
pip install pillow
```

Optional for system tray notifications:

```bash
pip install pystray
```

### Krok 2 — Instalacja pakietów językowych

HAMIOS ships with English as the built-in language. All other languages are in separate `.json` files.

**Download:**
Get the language files from the [latest release](https://github.com/fvdijke/HAMIOS/releases) — download `langs.zip`.

**Directory structure:**
```
HAMIOS.exe  (or HAMIOS.py)
langs\
  lang_nl.json    ← Nederlands
  lang_de.json    ← Deutsch
  lang_fr.json    ← Français
  lang_it.json    ← Italiano
  lang_es.json    ← Español
  lang_no.json    ← Norsk
  lang_pl.json    ← Polski
  lang_sv.json    ← Svenska
  lang_da.json    ← Dansk
  lang_fi.json    ← Suomi
  lang_pt.json    ← Português
  lang_ja.json    ← 日本語
  lang_ru.json    ← Русский
```

> The `langs/` folder must be placed **next to** `HAMIOS.exe` or `HAMIOS.py`.

**Creating your own language pack:**
Copy an existing `.json` file, change `meta.code` and `meta.name`, then translate the `strings` and `solar_tips` sections. HAMIOS will detect the new pack automatically on startup.

### Krok 3 — Uruchamianie

```bash
python HAMIOS.py
```

### Samodzielny plik EXE (Windows) — zalecane

Download `HAMIOS.exe` and the `langs/` folder from the [latest release](https://github.com/fvdijke/HAMIOS/releases). No Python required.

Build from source:

```bash
pip install pyinstaller
pyinstaller HAMIOS.spec
# → dist\HAMIOS.exe
# Then copy langs\ next to the EXE
```

---

## 🔭 Model propagacji

```
foF2 = 4.0 + (SFI − 70) × 0.065 + SSN × 0.012
MUF  = foF2 × latitude-factor × day/night-factor × 3.8
LUF  = (3.5 + K × 0.8) × auroral-factor / 10^(SNR/20)
```

**Band quality**: optimum around 55 % of the MUF/LUF window → 100 %.

---

## ⌨️ Interakcja z myszą

| Action | Effect |
|--------|--------|
| Scroll wheel on map | Zoom 1×–8× |
| Click + drag on map | Pan viewport |
| Left-click on map | Great-circle path + path propagation |
| Right-click on map | Reset zoom/pan · clear path |
| Hover on map / bands / chart | Detailed tooltip |
| Click on legend label | Toggle band in history chart |

---

## 💻 Wymagania systemowe

| | Minimum | Recommended |
|-|---------|------------|
| OS | Windows 10 | Windows 11 |
| Screen resolution | 1280 × 900 | 1920 × 1080 or wider |
| Python | 3.10 | 3.12+ |
| Internet | Required (data feeds) | — |

> v3.0 makes best use of a wide display (≥ 1768 px) with the DX column as an additive right panel. On narrower screens the window scales proportionally and all panels remain usable.

---

## 🔧 Przyszłe pomysły

- Stabilise CAT interface (Yaesu/Kenwood/Icom)
- SDR integration
- Logging connection (ADIF/WSJTX)
- Satellite tracking

---

## 📜 Licencja

Bezpłatny do użytku osobistego i niekomercyjnego w krótkofalarstwie.

---

