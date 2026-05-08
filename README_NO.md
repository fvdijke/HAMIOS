# 📡 HAMIOS v4.0.1

**KV utbredelse og DX-monitor for Windows**

> v4.0.1 — Flyttbare og skalerbare paneler · Samlet Innstillinger-dialog · Ytelsesoptimaliseringer · Solhistorikkdiagram

*Conceived by Frank van Dijke · Developed with Claude AI*

HAMIOS gir radioamatører sanntidsinnsikt i KV-utbredelse, solaraktivitet og DX-muligheter — pakket i et moderne mørkt grafisk grensesnitt.

---

## ✨ Funksjoner

### 🌍 Interaktivt verdenskart *(sentrert i vinduet)*
- Ekvirektangulært NASA-kart, lastes automatisk ned ved første bruk
- **Fast høyde (380 px)** med korrekt 2:1-rendering — ingen horisontal forvrengning
- **Dag/natt-terminator** med myk overgangsone
- **Grålinje** (ravgult bånd, ~1000 km bredt)
- **Sol- og måneposisjon** (geosentrisk beregning)
- **QTH-markering** (blått trådkors) — bredde-/lengdegrad konfigurerbar i overskriften
- **Storkretssti**: klikk på kart → avstand + kurs + **bandkvalitet for den stien**
- **ITU-regionoverlegg** R1/R2/R3 (offisiell ITU RR Art. 5)
- **Maidenhead-locatorruter** (20° × 10°, merker AA–RR)
- **Kallesignalprefiks-lag** (~110 DXCC-enheter)
- **Zoom/panorering**: mushjul 1×–8×, klikk+dra for panorering, høyreklikk for tilbakestilling
- **Kartoverlegg gruppert** under kartet:
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
- **11 fritt bevegelige og skalerbare paneler** plassert på en fri skrivebordsflate
- Hvert panel har en ravfarget 1px-kant, tittelrad med ✕ lukkeknapp og ◢ størrelsesjusteringshåndtak
- **Snap-to-grid** (2px) ved slipp etter dra/størrelsesjustering for ren justering
- Paneler: KV-bånd pålitelighet · Verdenskart · Solar/Ionosfære · Varsler · Båndtidsplan · Båndhistorikk · Kp 48t · Bz 24t · Røntgen 24t · DX-flekker · Utbredelsesanbefalinger
- **⚙ Innstillinger-dialog** inneholder all konfigurasjon: QTH · Språk · Tema · Verktøytips · Ticker · Sommertid · Panelsynlighet · Oppsettbehandling
- **Oppsettforhåndsinnstillinger**: lagre/laste/overskrive/slette navngitte profiler i `hamios_layouts.json`
- **Lagre som standard**: lagrer gjeldende oppsett som oppstartsoppsett

### 🛰 Satellittsporing *(🛰 Sat-knapp i header)*
- TLE-data lastet ned fra **Celestrak** (Amateur / ISS / Weather / CubeSat)
- **Kategorifilter**: Alle · Amateur · ISS · Weather · CubeSat
- Per satellitt: veksle **posisjonspunkt** (●), **banesti** (~) og **fotavtrykk** på kartet
- **Fotavtrykket blir grønt** når QTH er innenfor satellittens dekningsområde
- **Varslingspanel** viser satellitter som er synlige over QTH med elevasjonsvinkel
- Banetider i lokal tid (CEST / CET)
- **↻ TLE**-knapp for manuell oppdatering av banelementer
- Bufret i `hamios_tle.json`

### 🕵 Spion- / tallstasjoner *(🕵 Spy-knapp i header)*
- Rullbar tabell med 24 kjente tallstasjoner og spionradiostationer
- Kolonner: status (● aktiv / historisk), navn, land, frekvenser, modus
- **Sorterbare kolonner** — klikk på kolonneoverskrift for å sortere; klikk igjen for å reversere
- **Filter** etter aktiv/inaktiv status og fritekstsøk (navn, land, frekvens)
- **Hold musepekeren** over en rad for å se full beskrivelse + sendeskjema
- Datafil: `hamios_spy_stations.json` (redigerbar)

### 🔵 WSPR / PSKReporter Spots on Map
- Live propagation paths from **wspr.rocks** (WSPR) and **pskreporter.info** (FT8/FT4)
- Connection lines: **colour = band**, **thickness = SNR**

### 📍 DX Spot Markers on Map
- Active DX cluster spots: dot at DX location + line to spotter, colour-coded by band
- Click a dot to show callsign, frequency and comment

### 🌞 Solar- og ionosfæredata

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
| 🛰 Satellitt over QTH | Alltid aktiv | Viser hvilke valgte satellitter er over QTH med elevasjonsvinkel |

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

### ⚙️ Annet
- **Dynamiske temaer**: Midnight · DeepOcean · HighContrast
- **Systemskuff**: minimer til skuff, skuffvarsler
- **Verktøytips** med forklaring per solarparameter
- **Automatisk oppdatering**: Av / 30 s / 1 min / 5 min / 10 min / 30 min / 1 time
- **Rullende ticker** med aktuelle utbredelsesstips
- **Bevegelig panelsystem**: organiser og endre størrelse på alle paneler fritt
- **Oppsettforhåndsinnstillinger**: lagre og bytt mellom tilpassede paneloppsett
- Alle innstillinger lagret i `HAMIOS.ini`

---

## 🖥️ Layout (v4.0.1) — Fritt flytende paneler

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ⚙ Innstillinger  (QTH · Språk · Tema · Verktøytips · Ticker · Sommertid · Paneler · Oppsett) │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────────────────────┐  ┌──────────────┐  │
│  │Solar/Ionosfæ.│  │      Verdenskart          ✕  │  │KV-band   ✕  │  │
│  │     ✕    ◢  │  │   zoom/pan · overlegg     ◢  │  │Pålitelighet◢│  │
│  └──────────────┘  └──────────────────────────────┘  └──────────────┘  │
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │Båndtidsplan │  │Båndhistorikk│  │  Kp 48t  │  │ DX-flekker   ✕  │  │
│  │    ✕    ◢  │  │    ✕    ◢  │  │  ✕    ◢  │  │             ◢  │  │
│  └─────────────┘  └─────────────┘  └──────────┘  └──────────────────┘  │
│                                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────────────────┐  │
│  │  Bz 24t  │  │Røntgen 24t│  │  Utbredningsanbefalinger        ✕  │  │
│  │  ✕    ◢  │  │  ✕    ◢  │  │                               ◢  │  │
│  └──────────┘  └──────────┘  └──────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Varsler  ✕  ◢                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Alle paneler: ravkant · ✕ lukk · ◢ størrelse · rutenett (2px)         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Installasjon

### Trinn 1 — Python-krav

```bash
pip install pillow
```

Optional for system tray notifications:

```bash
pip install pystray
```

### Trinn 2 — Installer språkpakker

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

### Trinn 3 — Start

```bash
python HAMIOS.py
```

### Frittstående EXE (Windows) — anbefalt

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

| Fil | Innhold |
|-----|---------|
| `HAMIOS.ini` | Alle brukerinnstillinger (QTH, tema, språk, varselterskler, …) |
| `hamios_layouts.json` | Panel-oppsett forhåndsinnstillinger |
| `hamios_tle.json` | Bufrede TLE-banelementer for satellittsporing |
| `hamios_spy_stations.json` | Spion-/tallstasjons-database (redigerbar) |
| `langs/*.json` | Språkpakker |

---

## 🔭 Utbredelsesmodell

```
foF2 = 4.0 + (SFI − 70) × 0.065 + SSN × 0.012
MUF  = foF2 × latitude-factor × day/night-factor × 3.8
LUF  = (3.5 + K × 0.8) × auroral-factor / 10^(SNR/20)
```

**Band quality**: optimum around 55 % of the MUF/LUF window → 100 %.

---

## ⌨️ Museinteraksjon

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

> v4.0.1 bruker et fritt panel-lerret. Ordne paneler fritt på enhver skjermstørrelse. Et bredt skjerm (≥ 1920 px) gir det mest komfortable arbeidsområdet.

---

## 🔧 Fremtidige ideer

- Stabilise CAT interface (Yaesu/Kenwood/Icom)
- SDR integration
- Logging connection (ADIF/WSJTX)

---

## 📜 Lisens

Gratis for personlig, ikke-kommersiell amatørradiobruk.

---

