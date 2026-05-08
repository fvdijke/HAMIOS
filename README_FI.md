# 📡 HAMIOS v4.0.1

**LB-etenemis- ja DX-monitori Windowsille**

> v4.0.1 — Siirrettävät ja kokoaan muutettavat paneelit · Yhtenäinen Asetukset-valintaikkuna · Suorituskyvyn optimoinnit · Aurinkohistoriakaavio

*Conceived by Frank van Dijke · Developed with Claude AI*

HAMIOS tarjoaa radioamatööreille reaaliaikaisen näkemyksen LB-etenemisestä, sola-aktiviteetista ja DX-mahdollisuuksista — modernissa tummassa graafisessa käyttöliittymässä.

---

## ✨ Ominaisuudet

### 🌍 Interaktiivinen maailmankartta *(ikkunan keskellä)*
- Ekvirectangulaarinen NASA-kartta, ladataan automaattisesti ensimmäisellä käyttökerralla
- **Kiinteä korkeus (380 px)** oikealla 2:1-renderöinnillä — ei vaakasuoraa vääristymää
- **Päivä/yö-terminaattori** pehmeällä siirtymävyöhykkeellä
- **Harmaasäteily** (meripihkavyöhyke, ~1000 km leveä)
- **Auringon ja kuun sijainti** (geosentrinen laskenta)
- **QTH-merkintä** (sininen tähtäyshiusristikko) — lat/lon muutettavissa otsikossa
- **Suurympyrän reitti**: napsauta karttaa → etäisyys + suunta + **kaistan laatu kyseiselle reitille**
- **ITU-alueen peitto** R1/R2/R3 (virallinen ITU RR Art. 5)
- **Maidenhead-lokaattoriruudukko** (20° × 10°, tunnisteet AA–RR)
- **Kutsutunnusprefiksikerros** (~110 DXCC-kohdetta)
- **Zoomaus/panorointi**: hiirenpyörä 1×–8×, klikkaa+vedä panoroimiseksi, oikeaklikki nollauksen
- **Karttapäällysteet ryhmitelty** kartan alle:
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

### 🖥️ Paneelijärjestelmä *(v4.0.1)*
- **11 vapaasti siirrettävää ja kokoaan muutettavaa paneelia** vapaalla työpöytäalustalla
- Jokaisessa paneelissa on meripihkavärinen 1px-reunus, otsikkorivi ✕-sulkupainikkeella ja ◢ kokoa muuttava kahva
- **Ruudukkoon kohdistus** (2px) vedä/koon muutos vapautettaessa siistiä kohdistusta varten
- Paneelit: LB-kaista luotettavuus · Maailmankartta · Aurinko/Ionosfääri · Hälytykset · Kaistataulu · Kaistahistoria · Kp 48h · Bz 24h · Röntgen 24h · DX-pisteet · Etenemissuositukset
- **⚙ Asetukset-valintaikkuna** sisältää kaiken konfiguraation: QTH · Kieli · Teema · Työkaluvihjeet · Ticker · Kesäaika · Paneelin näkyvyys · Asettelun hallinta
- **Asettelu-esiasetukset**: tallenna/lataa/kirjoita yli/poista nimettyjä profiileja `hamios_layouts.json`-tiedostossa
- **Tallenna oletukseksi**: tallentaa nykyisen asettelun käynnistysasetteluksi

### 🛰 Satelliittiseuranta *(🛰 Sat-painike otsikossa)*
- TLE-data ladattu **Celestrak**-palvelusta (Amateur / ISS / Weather / CubeSat)
- **Kategoriasuodatin**: Kaikki · Amateur · ISS · Weather · CubeSat
- Per satelliitti: vaihda **sijaintipiste** (●), **kiertorata** (~) ja **jalanjälki** kartalla
- **Jalanjälki muuttuu vihreäksi** kun QTH on satelliitin peittoalueen sisällä
- **Ilmoituspaneeli** näyttää satelliitit jotka ovat tällä hetkellä QTH:n yläpuolella elevaatiokulmalla
- Ratareittien ajat näytetään paikallisessa ajassa (CEST / CET)
- **↻ TLE**-painike rataelementtien manuaalista päivitystä varten
- Välimuistissa `hamios_tle.json`

### 🕵 Vakoilu-/numerosasemat *(🕵 Spy-painike otsikossa)*
- Vieritettävä taulukko 24 tunnetusta numeroasemasta ja vakoiluradiosta
- Sarakkeet: tila (● aktiivinen / historiallinen), nimi, maa, taajuudet, tila
- **Lajiteltavat sarakkeet** — napsauta otsikkoa lajitellaksesi; napsauta uudelleen kääntääksesi
- **Suodatin** aktiivinen/inaktiivinen tilan ja vapaan tekstihaun mukaan (nimi, maa, taajuus)
- **Vie hiiri** rivin päälle nähdäksesi täydellinen kuvaus + lähetysaikataulu
- Datatiedosto: `hamios_spy_stations.json` (muokattava)

### 🔵 WSPR / PSKReporter Spots on Map
- Live propagation paths from **wspr.rocks** (WSPR) and **pskreporter.info** (FT8/FT4)
- Connection lines: **colour = band**, **thickness = SNR**

### 📍 DX Spot Markers on Map
- Active DX cluster spots: dot at DX location + line to spotter, colour-coded by band
- Click a dot to show callsign, frequency and comment

### 🌞 Aurinko- ja ionosfääridata

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
| 🛰 Satelliitti QTH:n yläpuolella | Aina aktiivinen | Näyttää mitkä valitut satelliitit ovat QTH:n yläpuolella elevaatiokulmalla |

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

### ⚙️ Muut
- **Dynaamiset teemat**: Midnight · DeepOcean · HighContrast
- **Järjestelmäilmaisin**: pienennä ilmaisinalueelle, ilmoitukset
- **Työkaluvihjeet** selityksellä kullekin aurinkoparametrille
- **Automaattinen päivitys**: Pois / 30 s / 1 min / 5 min / 10 min / 30 min / 1 tunti
- **Vierittyvä ticker** nykyisillä etenemisvinkeillä
- **Siirrettävä paneelijärjestelmä**: järjestä ja muuta kaikkien paneelien kokoa vapaasti
- **Asettelu-esiasetukset**: tallenna ja vaihda mukautettujen paneeliasettelujen välillä
- Kaikki asetukset tallennettu `HAMIOS.ini`-tiedostoon

---

## 🖥️ Asettelu (v4.0.1) — Vapaasti kelluvat paneelit

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ⚙ Asetukset  (QTH · Kieli · Teema · Työkaluvihjeet · Ticker · Kesäaika · Paneelit · Asettelut) │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────────────────────┐  ┌──────────────┐  │
│  │Aurinko/Ionosf│  │      Maailmankartta       ✕  │  │LB-kaista ✕  │  │
│  │     ✕    ◢  │  │   zoom/pan · kerrokset    ◢  │  │Luotettavuus◢│  │
│  └──────────────┘  └──────────────────────────────┘  └──────────────┘  │
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │Kaistataulu  │  │Kaistahistoria│  │  Kp 48h  │  │  DX-pisteet  ✕  │  │
│  │    ✕    ◢  │  │    ✕    ◢  │  │  ✕    ◢  │  │             ◢  │  │
│  └─────────────┘  └─────────────┘  └──────────┘  └──────────────────┘  │
│                                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────────────────┐  │
│  │  Bz 24h  │  │Röntgen 24h│  │  Etenemissuositukset             ✕  │  │
│  │  ✕    ◢  │  │  ✕    ◢  │  │                               ◢  │  │
│  └──────────┘  └──────────┘  └──────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Hälytykset  ✕  ◢                                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Kaikki paneelit: meripihkareunус · ✕ sulje · ◢ koko · ruudukko (2px) │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Asennus

### Vaihe 1 — Python-vaatimukset

```bash
pip install pillow
```

Optional for system tray notifications:

```bash
pip install pystray
```

### Vaihe 2 — Asenna kielipaketit

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

### Vaihe 3 — Käynnistä

```bash
python HAMIOS.py
```

### Itsenäinen EXE (Windows) — suositellaan

Download `HAMIOS.exe` and the `langs/` folder from the [latest release](https://github.com/fvdijke/HAMIOS/releases). No Python required.

Build from source:

```bash
pip install pyinstaller
pyinstaller HAMIOS.spec
# → dist\HAMIOS.exe
# Then copy langs\ next to the EXE
```

---

## 📁 Datatiedostot

| Tiedosto | Sisältö |
|----------|---------|
| `HAMIOS.ini` | Kaikki käyttäjäasetukset (QTH, teema, kieli, hälytyskynnykset, …) |
| `hamios_layouts.json` | Paneeliasettelun esiasetukset |
| `hamios_tle.json` | Välimuistissa olevat TLE-rataelementit satelliittiseurantaa varten |
| `hamios_spy_stations.json` | Vakoilu-/numerosasemien tietokanta (muokattava) |
| `langs/*.json` | Kielipaketit |

---

## 🔭 Etenemismalli

```
foF2 = 4.0 + (SFI − 70) × 0.065 + SSN × 0.012
MUF  = foF2 × latitude-factor × day/night-factor × 3.8
LUF  = (3.5 + K × 0.8) × auroral-factor / 10^(SNR/20)
```

**Band quality**: optimum around 55 % of the MUF/LUF window → 100 %.

---

## ⌨️ Hiiren käyttö

| Action | Effect |
|--------|--------|
| Scroll wheel on map | Zoom 1×–8× |
| Click + drag on map | Pan viewport |
| Left-click on map | Great-circle path + path propagation |
| Right-click on map | Reset zoom/pan · clear path |
| Hover on map / bands / chart | Detailed tooltip |
| Click on legend label | Toggle band in history chart |

---

## 💻 Järjestelmävaatimukset

| | Minimum | Recommended |
|-|---------|------------|
| OS | Windows 10 | Windows 11 |
| Screen resolution | 1280 × 900 | 1920 × 1080 or wider |
| Python | 3.10 | 3.12+ |
| Internet | Required (data feeds) | — |

> v4.0.1 käyttää vapaata paneelialuetta. Järjestä paneelit vapaasti millä tahansa näyttökoolla. Leveä näyttö (≥ 1920 px) tarjoaa mukavimman työtilan.

---

## 🔧 Tulevaisuuden ideoita

- Stabilise CAT interface (Yaesu/Kenwood/Icom)
- SDR integration
- Logging connection (ADIF/WSJTX)

---

## 📜 Lisenssi

Ilmainen henkilökohtaiseen, ei-kaupalliseen radioamatöörikäyttöön.

---

