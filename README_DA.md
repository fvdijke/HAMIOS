# 📡 HAMIOS v4.0.1

**KV udbrednings- og DX-monitor til Windows**

> v4.0.1 — Flytbare og skalerbare paneler · Samlet Indstillinger-dialog · Ydeevneoptimeringer · Solhistorikdiagram

*Conceived by Frank van Dijke · Developed with Claude AI*

HAMIOS giver radioamatører realtidsindsigt i KV-udbredning, solaktivitet og DX-muligheder — pakket i en moderne mørk grafisk brugerflade.

---

## ✨ Funktioner

### 🌍 Interaktivt verdenskort *(centreret i vinduet)*
- Ekvirectangulært NASA-kort, downloades automatisk ved første brug
- **Fast højde (380 px)** med korrekt 2:1-rendering — ingen horisontal forvrængning
- **Dag/nat-terminator** med blød overgangszone
- **Grålinje** (ravgult bånd, ~1000 km bredt)
- **Sol- og måneposition** (geocentrisk beregning)
- **QTH-markering** (blåt trådkors) — bredde-/længdegrad konfigurerbar i overskriften
- **Storcirkelvej**: klik på kort → afstand + kurs + **bandkvalitet for den vej**
- **ITU-regionsoverlay** R1/R2/R3 (officiel ITU RR Art. 5)
- **Maidenhead-locatorraster** (20° × 10°, etiketter AA–RR)
- **Kaldesignalspræfiks-lag** (~110 DXCC-enheder)
- **Zoom/panorering**: mushjul 1×–8×, klik+træk for panorering, højreklik for nulstilling
- **Kortoverlejringer grupperet** under kortet:
  - *Display:* Sun · Moon · Gray line · Aurora · Sat
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

### 🖥️ Panelsystem *(v4.0.1)*
- **11 frit bevægelige og skalerbare paneler** placeret på en fri skrivebordsoverflade
- Hvert panel har en ravfarvet 1px-kant, titelbjælke med ✕ lukkeknap og ◢ størrelseshåndtag
- **Fastgør til gitter** (2px) ved slip efter træk/størrelsesjustering for ren justering
- Paneler: KV-bånd pålidelighed · Verdenskort · Solar/Ionosfære · Advarsler · Båndtidsplan · Båndhistorik · Kp 48t · Bz 24t · Røntgen 24t · DX-spots · Udbredningsanbefalinger
- **⚙ Indstillinger-dialog** indeholder al konfiguration: QTH · Sprog · Tema · Værktøjstips · Ticker · Sommertid · Panelsynlighed · Layoutstyring
- **Layoutforudindstillinger**: gem/indlæs/overskriv/slet navngivne profiler i `hamios_layouts.json`
- **Gem som standard**: gemmer det aktuelle layout som startlayout

### 🛰 Satellitsporing *(🛰 Sat-knap i overskrift)*
- TLE-data downloadet fra **Celestrak** (Amateur / ISS / Weather / CubeSat)
- **Kategorifilter**: Alle · Amateur · ISS · Weather · CubeSat
- Per satellit: slå **positionspunkt** (●), **kredsløbssti** (~) og **fodaftryk** til/fra på kortet
- **Fodaftrykket bliver grønt** når QTH er inden for satellittens dækningszone
- **Notifikationspanel** viser satellitter der aktuelt er over QTH med elevationsvinkel
- Banestier vist i lokal tid (CEST / CET)
- **↻ TLE**-knap til manuel opdatering af baneelementer
- Cachet i `hamios_tle.json`

### 🕵 Spion-/talstationer *(🕵 Spy-knap i overskrift)*
- Rulbar tabel med 24 kendte talstationer og spionradiostationer
- Kolonner: status (● aktiv / historisk), navn, land, frekvenser, mode
- **Sorterbare kolonner** — klik på en kolonneoverskrift for at sortere; klik igen for at vende om
- **Filter** efter aktiv/inaktiv status og fritekstsøgning (navn, land, frekvens)
- **Hold musen** over en række for at se fuld beskrivelse + udsendelsesplan
- Datafil: `hamios_spy_stations.json` (redigerbar)

### 🔵 WSPR / PSKReporter Spots on Map
- Live propagation paths from **wspr.rocks** (WSPR) and **pskreporter.info** (FT8/FT4)
- Connection lines: **colour = band**, **thickness = SNR**

### 📍 DX Spot Markers on Map
- Active DX cluster spots: dot at DX location + line to spotter, colour-coded by band
- Click a dot to show callsign, frequency and comment

### 🌞 Sol- og ionosfæredata

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
| 🛰 Satellit over QTH | Altid aktiv | Viser hvilke valgte satellitter er over QTH med elevationsvinkel |

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

### ⚙️ Andet
- **Dynamiske temaer**: Midnight · DeepOcean · HighContrast
- **Systembakke**: minimer til bakke, bakkenotifikationer
- **Værktøjstips** med forklaring per solarparameter
- **Automatisk opdatering**: Fra / 30 s / 1 min / 5 min / 10 min / 30 min / 1 time
- **Rullende ticker** med aktuelle udbredningstips
- **Bevægeligt panelsystem**: arrangér og ændr størrelse på alle paneler frit
- **Layoutforudindstillinger**: gem og skift mellem brugerdefinerede panelarrangementer
- Alle indstillinger gemt i `HAMIOS.ini`

---

## 🖥️ Layout (v4.0.1) — Frit svævende paneler

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ⚙ Indstillinger  (QTH · Sprog · Tema · Værktøjstips · Ticker · Sommertid · Paneler · Layouts) │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────────────────────┐  ┌──────────────┐  │
│  │Solar/Ionosfæ.│  │      Verdenskort          ✕  │  │KV-bånd   ✕  │  │
│  │     ✕    ◢  │  │   zoom/pan · overlejring  ◢  │  │Pålidelighed◢│  │
│  └──────────────┘  └──────────────────────────────┘  └──────────────┘  │
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │Båndtidsplan │  │ Båndhistorik│  │  Kp 48t  │  │  DX-spots    ✕  │  │
│  │    ✕    ◢  │  │    ✕    ◢  │  │  ✕    ◢  │  │             ◢  │  │
│  └─────────────┘  └─────────────┘  └──────────┘  └──────────────────┘  │
│                                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────────────────┐  │
│  │  Bz 24t  │  │Røntgen 24t│  │  Udbredningsanbefalinger        ✕  │  │
│  │  ✕    ◢  │  │  ✕    ◢  │  │                               ◢  │  │
│  └──────────┘  └──────────┘  └──────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Advarsler  ✕  ◢                                                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Alle paneler: ravfarvet kant · ✕ luk · ◢ størrelse · gitter (2px)    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Installation

### Trin 1 — Python-krav

```bash
pip install pillow
```

Optional for system tray notifications:

```bash
pip install pystray
```

### Trin 2 — Installer sprogpakker

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

### Trin 3 — Start

```bash
python HAMIOS.py
```

### Selvstændig EXE (Windows) — anbefalet

Download `HAMIOS.exe` and the `langs/` folder from the [latest release](https://github.com/fvdijke/HAMIOS/releases). No Python required.

Build from source:

```bash
pip install pyinstaller
pyinstaller HAMIOS.spec
# → dist\HAMIOS.exe
# Then copy langs\ next to the EXE
```

---

## 📁 Datafiler

| Fil | Indhold |
|-----|---------|
| `HAMIOS.ini` | Alle brugerindstillinger (QTH, tema, sprog, advarselstærskler, …) |
| `hamios_layouts.json` | Panel-layout forudindstillinger |
| `hamios_tle.json` | Cachelagrede TLE-banelementer til satellitsporing |
| `hamios_spy_stations.json` | Spion-/talstationsdatabase (redigerbar) |
| `langs/*.json` | Sprogpakker |

---

## 🔭 Udbredningsmodel

```
foF2 = 4.0 + (SFI − 70) × 0.065 + SSN × 0.012
MUF  = foF2 × latitude-factor × day/night-factor × 3.8
LUF  = (3.5 + K × 0.8) × auroral-factor / 10^(SNR/20)
```

**Band quality**: optimum around 55 % of the MUF/LUF window → 100 %.

---

## ⌨️ Museinteraktion

| Action | Effect |
|--------|--------|
| Scroll wheel on map | Zoom 1×–8× |
| Click + drag on map | Pan viewport |
| Left-click on map | Great-circle path + path propagation |
| Right-click on map | Reset zoom/pan · clear path |
| Hover on map / bands / chart | Detailed tooltip |
| Click on legend label | Toggle band in history chart |

---

## 💻 Systemkrav

| | Minimum | Recommended |
|-|---------|------------|
| OS | Windows 10 | Windows 11 |
| Screen resolution | 1280 × 900 | 1920 × 1080 or wider |
| Python | 3.10 | 3.12+ |
| Internet | Required (data feeds) | — |

> v4.0.1 bruger et frit panel-lærred. Arrangér paneler frit på enhver skærmstørrelse. Et bredt skærm (≥ 1920 px) giver det mest komfortable arbejdsområde.

---

## 🔧 Fremtidige ideer

- Stabilise CAT interface (Yaesu/Kenwood/Icom)
- SDR integration
- Logging connection (ADIF/WSJTX)

---

## 📜 Licens

Gratis til personlig, ikke-kommerciel amatørradiobrug.

---

