# 📡 HAMIOS v4.0.1

**HAM-radio propagatie- en DX-monitor voor Windows**
<img width="2200" height="1521" alt="HAMIOS v3 0" src="https://github.com/user-attachments/assets/ab39f20a-67c5-4819-8b32-96b8fe07e36e" />

> v4.0.1 — Versleepbare panelen · Instellingen-dialoog · Prestatie-verbeteringen · Solar geschiedenissgrafiek

*Bedacht door Frank van Dijke · Ontwikkeld met Claude AI*

HAMIOS geeft radioamateurs realtime inzicht in HF-propagatie, zonne-activiteit en DX-mogelijkheden — verpakt in een moderne donkere GUI.

---

## ✨ Features

### 🌍 Interactieve Wereldkaart *(centraal in het venster)*
- Equirectangulaire NASA-kaart, automatisch gedownload bij eerste gebruik
- **Vaste hoogte (380 px)** met correcte 2:1 rendering — nooit horizontale vervorming
- **Dag/nacht-terminator** met zachte overgangszone
- **Graylijn** (amber band, ~1000 km breed)
- **Zon- en maanpositie** (geocentrisch berekend)
- **QTH-markering** (blauw kruisje) — lat/lon instelbaar in header
- **Groot-cirkelpad**: klik op kaart → afstand + richting + **band-kwaliteit voor dat traject**
- **ITU-regio overlay** R1/R2/R3 (officieel ITU RR Art. 5)
- **Maidenhead-locatorraster** (20° × 10°, labels AA–RR)
- **Callsign-prefix laag** (~110 DXCC-entiteiten)
- **Zoom/pan**: muiswiel 1×–8×, klik+sleep om te pannen, rechts om te resetten
- **Kaart-overlays gegroepeerd** onder de kaart:
  - *Weergave:* Zon · Maan · Graylijn · Aurora · Sat
  - *Data:* WSPR · Spots · CS · Locator

### 🛰️ Propagatiepadkaart
- **Band-kwaliteit** berekend op het midpunt van het groot-cirkelpad
- Dag/nacht correctie op het midpunt
- Aantal hops geschat (≈ afstand / 3500 km)
- Top-5 open banden: `↳  8.847 km / 3 hops / dag  ▸  20m 87%  ·  17m 72%  ·  15m 54%  (MUF 24.1 MHz)`
- **Groot-cirkel lijn kleurt naar de beste band**

### 🌌 Aurora-ring overlay
- Magnetische aurora-ovaal op basis van de K-index (Feldstein/Holzworth, IGRF-2025)
- **Kleur op K-index**: groen (K < 3) · geel (K 3–5) · rood (K ≥ 6)

### 🖥️ Paneel-systeem *(v4.0.1)*
- **11 vrij versleepbare en aanpasbare panelen** op een vrij desktop-canvas
- Elk paneel heeft een amber 1px rand, titelbalk met ✕-knop en ◢ resize-handle
- **Snap-to-grid** (2px) bij loslaten voor nette uitlijning
- Panelen: HF Betrouwbaarheid · Wereldkaart · Solar/Ionosfeer · Meldingen · Band Schema · Band Verloop · Kp 48u · Bz 24u · X-straling 24u · DX Spots · Propagatie Advies
- **⚙ Instellingen-dialoog** bevat alle configuratie: QTH · Taal · Thema · Tooltips · Ticker · Zomertijd · Paneel zichtbaarheid · Indeling beheer
- **Indeling-profielen**: opslaan/laden/overschrijven/verwijderen van named profielen in `hamios_layouts.json`
- **Opslaan als standaard**: bewaart de huidige indeling als startindeling

### 🛰 Satelliet-tracking *(🛰 Sat-knop in header)*
- TLE-data van **Celestrak** (Amateur / ISS / Weather / CubeSat)
- **Categorie-filter**: Alle · Amateur · ISS · Weather · CubeSat
- Per satelliet: **positiestip** (●), **baanpad** (~) en **footprint** op kaart
- **Footprint kleurt groen** als het QTH binnen de dekkingszone valt
- **Meldingen-paneel** toont satellieten boven het QTH met elevatie-hoek
- Padtijden in lokale tijd (CEST / CET)
- **↻ TLE**-knop voor handmatige verversing van baanelementen
- Gecached in `hamios_tle.json`

### 🕵 Spy / Numbers Stations *(🕵 Spy-knop in header)*
- Scrollbare tabel met 24 bekende nummerstations en spy-radiostations
- Kolommen: status (● actief / historisch), naam, land, frequenties, mode
- **Sorteerbare kolommen** — klik kolomkop om te sorteren; nogmaals klikken draait om
- **Filter** op actief/inactief en vrije-tekst zoekveld (naam, land, frequentie)
- **Hover** over een rij voor volledige beschrijving + uitzendschema
- Databestand: `hamios_spy_stations.json` (bewerkbaar)

### 🔵 WSPR / PSKReporter spots op kaart
- Live propagatiepaden van **wspr.rocks** (WSPR) en **pskreporter.info** (FT8/FT4)
- Verbindingslijnen: **kleur = band**, **dikte = SNR**

### 📍 DX-spot markers op kaart
- Actieve DX-cluster spots: stip op DX-locatie + lijn naar spotter, kleurcodering per band
- Klikken op een stip toont callsign, frequentie en comment

### 🌞 Solar & Ionosfeer Data

| Parameter | Bron | Beschrijving |
|-----------|------|--------------|
| SFI | hamqsl.com | Solar Flux Index (10,7 cm) |
| SSN | hamqsl.com | Sunspot Number |
| A-index | hamqsl.com | Dagelijkse geomagnetische activiteit |
| K-index | hamqsl.com | 3-uurs geomagnetische activiteit (0–9) |
| X-ray | hamqsl.com | GOES röntgenflux (A/B/C/M/X klasse) |
| MUF | intern model | Maximum Usable Frequency |
| LUF | intern model | Lowest Usable Frequency |
| Solarwindsnelheid | NOAA SWPC | km/s via DSCOVR/ACE |
| Bz | NOAA SWPC | Interplanetair magneetveld Z-component (nT) |
| foF2 | GIRO/LGDC | Gemeten F2-laag kritische frequentie (ionosonde) |

### 📊 Bz 24-uurs grafiek *(eigen paneel)*
- **Blauw** = positief Bz (gunstig) · **Rood** = negatief Bz (geoeffectief)
- Y-labels −20 / 0 / +20 nT · past automatisch in het paneel

### 📶 HF Band Betrouwbaarheid *(vernieuwd in v3.0)*
- Intern MUF/LUF-model op basis van SFI, SSN, K-index en QTH-breedtegraad
- SNR-budget gecorrigeerd voor **mode**, **vermogen** en **antenne**
- **Gradientbalken in band-eigen kleur** (licht → donker) met glans-lijn
- Bandnaam **vet en in bandkleur** — elke band heeft zijn eigen identiteit
- Kolommen: start-MHz · modi · FT8-frequentie

### 🔔 Meldingen & Alarmen

| Notificatie | Instelling | Beschrijving |
|-------------|-----------|--------------|
| ⚠️ K-index storm | Checkbox + drempel (1–9) | Melding bij stijging boven drempel |
| 📡 Band geopend | Checkbox + drempel (10–90 %) | Melding als band opengaat |
| 🛰 Satelliet boven QTH | Altijd actief | Geeft aan welke geselecteerde satellieten boven het QTH zijn met elevatie |

Drempelwaarden worden opgeslagen in `HAMIOS.ini`.

### 🔌 CAT Interface *(tijdelijk uitgeschakeld)*
> De CAT-interface is tijdelijk uitgeschakeld. De code is intact en wordt in een volgende versie afgerond.

### 🕐 Bandopenings-schema
- 24-uur heatmap voor alle 11 HF-banden
- Tijdas in lokale tijd (CET/CEST), huidige tijd gemarkeerd
- Hover-tooltip: band · uur · kwaliteit · modi · FT8-frequentie

### 📈 Band Verloop
- Tijdgrafiek van alle HF-banden (%) — 90 dagen bewaard in CSV
- Tijdbereik: Uren · Dagen · Weken · Maanden
- Klikbare legenda om banden aan/uit te zetten

### 📡 Live DX Spots *(volledige-hoogte rechterkolom)*
- JSON-feed van dxwatch.com, ververst elke 5 minuten
- Kolommen: UTC · Band · DX · MHz · Spotter · Comment
- **Eigen-continent filter** — toon alleen spots van je eigen continent
- **Heatmap-modus**: band × UTC-uur activiteitspatroon (24h buffer)
- Spots ook als markers op de wereldkaart (schakelbaar)

### 💡 Propagatie-analyse & Advies
12 analyse-kaarten in 3 kolommen × 4 rijen.

| # | Kaart | Inhoud |
|---|-------|--------|
| 1 | 📡 Beste banden | Top-5 open banden met kwaliteitspercentage |
| 2 | ✅/⚠️ Geo-storm | K + A-index, routeadvies, ernst |
| 3 | ☀️ Zonactiviteit | SFI + SSN, zonnecyclus-fase |
| 4 | 💨 Solarwind | Snelheid + Bz-impact |
| 5 | ☢️ X-flare/SWF | Xray-klasse, herstelschatting |
| 6 | 📶 Ionosfeer | MUF, LUF, F2-laag |
| 7 | 🌅 Dag/nacht | Grey-line tijdvensters |
| 8 | 🔧 Modus-advies | FT8 vs SSB/CW op basis van SNR-budget |
| 9 | 🧲 Absorptie | Auroraal absorptie poolroutes |
| 10 | 📊 Overall score | Samengesteld propagatie-oordeel |

### 🌐 Meertalig
**14 talen** via extern taalpakket-systeem (`langs/*.json`).

| Code | Taal | Code | Taal |
|------|------|------|------|
| EN | English *(ingebouwd)* | NO | Norsk |
| NL | Nederlands | PL | Polski |
| DE | Deutsch | SV | Svenska |
| FR | Français | DA | Dansk |
| IT | Italiano | FI | Suomi |
| ES | Español | PT | Português |
| JA | 日本語 | RU | Русский |

### ⚙️ Overig
- **Dynamische thema's**: Midnight · DeepOcean · HighContrast
- **Systeemtray**: minimaliseren naar tray, tray-notificaties
- **Tooltips** met uitleg per solar-parameter
- **Automatische refresh**: Uit / 30 s / 1 min / 5 min / 10 min / 30 min / 1 uur
- **Scrollende ticker** met actuele propagatietips
- **Versleepbaar paneelsysteem**: rangschik en wijzig de grootte van alle panelen vrij
- **Indeling-profielen**: opslaan en wisselen tussen aangepaste paneelindelingen
- Alle instellingen opgeslagen in `HAMIOS.ini`

---

## 🖥️ Layout (v4.0.1) — Vrij zwevende panelen

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ⚙ Instellingen  (QTH · Taal · Thema · Tooltips · Ticker · Zomertijd · Panelen · Indelingen) │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────────────────────┐  ┌──────────────┐  │
│  │Solar/Ionosfeer│ │        Wereldkaart        ✕  │  │ HF Band  ✕  │  │
│  │     ✕    ◢  │  │   zoom/pan · overlays     ◢  │  │Betrouw.  ◢  │  │
│  └──────────────┘  └──────────────────────────────┘  └──────────────┘  │
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │Band Schema  │  │Band Verloop │  │  Kp 48u  │  │    DX Spots  ✕  │  │
│  │    ✕    ◢  │  │    ✕    ◢  │  │  ✕    ◢  │  │             ◢  │  │
│  └─────────────┘  └─────────────┘  └──────────┘  └──────────────────┘  │
│                                                                         │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────────────────────┐  │
│  │  Bz 24u  │  │X-straling 24u│  │     Propagatie Advies        ✕  │  │
│  │  ✕    ◢  │  │  ✕       ◢  │  │                            ◢  │  │
│  └──────────┘  └──────────────┘  └──────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Meldingen  ✕  ◢                                                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Alle panelen: amber rand · ✕ sluiten · ◢ formaat · snap-to-grid (2px) │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Installatie

### Stap 1 — Python vereisten

```bash
pip install pillow
```

Optioneel voor systeemtray-notificaties:

```bash
pip install pystray
```

### Stap 2 — Taalbestanden installeren

HAMIOS wordt geleverd met Engels als ingebouwde taal. Alle andere talen staan in losse `.json`-bestanden.

**Downloaden:**
Haal de taalbestanden op uit de [laatste release](https://github.com/fvdijke/HAMIOS/releases) — download `langs.zip`.

**Mapstructuur:**
```
HAMIOS.exe  (of HAMIOS.py)
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

> De `langs/`-map moet **naast** `HAMIOS.exe` of `HAMIOS.py` staan.

**Eigen taalbestand maken:**
Kopieer een bestaand `.json`-bestand, pas `meta.code` en `meta.name` aan en vertaal de `strings`- en `solar_tips`-secties.

### Stap 3 — Starten

```bash
python HAMIOS.py
```

### Standalone EXE (Windows) — aanbevolen

Download `HAMIOS.exe` én de `langs/`-map uit de [laatste release](https://github.com/fvdijke/HAMIOS/releases). Geen Python vereist.

Zelf bouwen:

```bash
pip install pyinstaller
pyinstaller HAMIOS.spec
# → dist\HAMIOS.exe
# Kopieer daarna langs\ naast de EXE
```

---

## 📁 Gegevensbestanden

| Bestand | Inhoud |
|---------|--------|
| `HAMIOS.ini` | Alle gebruikersinstellingen (QTH, thema, taal, drempelwaarden, …) |
| `hamios_layouts.json` | Paneel-indeling profielen |
| `hamios_tle.json` | Gecachte TLE-baanelementen voor satelliettracking |
| `hamios_spy_stations.json` | Spy-/nummerstationsdatabase (bewerkbaar) |
| `langs/*.json` | Taalpakketten |

---

## 🔭 Propagatiemodel

```
foF2 = 4.0 + (SFI − 70) × 0.065 + SSN × 0.012
MUF  = foF2 × breedtegraad-factor × dag/nacht-factor × 3.8
LUF  = (3.5 + K × 0.8) × auroraal-factor / 10^(SNR/20)
```

**Bandkwaliteit**: optimum rond 55 % van het MUF/LUF-venster → 100 %.

---

## ⌨️ Muisinteractie

| Actie | Effect |
|-------|--------|
| Muiswiel op kaart | Zoom 1×–8× |
| Klik + sleep op kaart | Pan viewport |
| Linkermuisklik op kaart | Groot-cirkelpad + padpropagatie |
| Rechtermuisklik op kaart | Reset zoom/pan · wis pad |
| Hover op kaart/banden/grafiek | Gedetailleerde tooltip |
| Klik op legenda-label | Band aan/uitzetten in historiekgrafiek |

---

## 💻 Systeemvereisten

| | Minimum | Aanbevolen |
|-|---------|-----------|
| OS | Windows 10 | Windows 11 |
| Schermresolutie | 1280 × 900 | 1920 × 1080 of groter |
| Python | 3.10 | 3.12+ |
| Internet | Vereist (data-feeds) | — |

> v4.0.1 gebruikt een vrij zwevend paneelcanvas. Rangschik panelen vrij op elk schermformaat. Een breed scherm (≥ 1920 px) biedt de meest comfortabele werkruimte.

---

## 🔧 Toekomstige ideeën

- CAT-interface stabiliseren (Yaesu/Kenwood/Icom)
- SDR-integratie
- Logging-koppeling (ADIF/WSJTX)

---

## 👨‍💻 Bijdragen / Contributing

Bijdragen zijn welkom! Zie [CONTRIBUTING.md](CONTRIBUTING.md) voor richtlijnen.

```bash
git clone https://github.com/fvdijke/HAMIOS.git
cd HAMIOS
pip install pillow pystray
python HAMIOS.py
```

Bugs melden of functies voorstellen via [GitHub Issues](https://github.com/fvdijke/HAMIOS/issues).

---

## 📜 Licentie

Vrij te gebruiken voor persoonlijk, niet-commercieel amateur radio gebruik.

---

*73 de PA3FVD*
