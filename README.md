# 📡 HAMIOS v3.2

**HAM-radio propagatie- en DX-monitor voor Windows**
<img width="2200" height="1521" alt="HAMIOS v3 0" src="https://github.com/user-attachments/assets/ab39f20a-67c5-4819-8b32-96b8fe07e36e" />

> v3.2 — Volledig nieuw interface-ontwerp · Wereldkaart centraal · DX Spots volledige-hoogte kolom · Gradientbalken met bandkleuren · Bz-grafiek als eigen paneel · 14 talen via externe taalpakketten

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
  - *Weergave:* Zon · Maan · Graylijn · Aurora
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
- Alle instellingen opgeslagen in `HAMIOS.ini`

---

## 🖥️ Layout (v3.0)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ HEADER  (titel · exit · CAT · interval · taal · QTH · thema · tijd)     │
├──────────┬──────────────────────────────────┬────────────┬──────────────┤
│  Solar   │      Wereldkaart (centraal)      │    HF      │              │
│ Ionosfeer│      380 px hoog, zoom/pan       │    Band    │   DX Spots   │
│  200 px  │   Weergave: Zon Maan Graylijn    │  Betrouw-  │  (volledig   │
│          │   Data: WSPR Spots CS Locator    │  baarheid  │   hoogte)    │
│          ├──────────────────────────────────┤   420 px   │   360 px     │
│          │  Schema  │  Bandverloop  │  Bz   │            │              │
│          │  (1/3)   │    (1/3)      │ (1/3) │            │              │
├──────────┴──────────────────────────────────┴────────────┤              │
│              Propagatie-analyse & Advies                  │              │
├───────────────────────────────────────────────────────────┴──────────────┤
│ TICKER                                                                    │
└──────────────────────────────────────────────────────────────────────────┘
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

> v3.0 maakt optimaal gebruik van een breed scherm (≥ 1768 px) door de DX-kolom als additionele rechterkolom toe te voegen. Op smalle schermen wordt het venster proportioneel smaller maar blijven alle panelen bruikbaar.

---

## 🔧 Toekomstige ideeën

- CAT-interface stabiliseren (Yaesu/Kenwood/Icom)
- SDR-integratie
- Logging-koppeling (ADIF/WSJTX)
- Satelliet tracking

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

