# 📡 HAMIOS v2.3
<img width="1743" height="1416" alt="HAMIOS v2 3" src="https://github.com/user-attachments/assets/3045d73a-9008-43d8-9dea-3d3fd5102792" />

**Multilingual + Multi overlay**
<img width="1743" height="1416" alt="HAMIOS-ALL v2 3" src="https://github.com/user-attachments/assets/4250a620-1bac-4867-9d78-0ac172a26e89" />

**HAM-radio propagatie- en DX-monitor voor Windows**

> v2.3 — Propagatiepadkaart · Bz 24h-grafiek · Band-openings-notificatie · CAT-interface · Aurora-ring overlay · WSPR/PSKReporter spots · DX-spot markers · 6 talen

*Bedacht door Frank van Dijke · Ontwikkeld met Claude AI*

HAMIOS geeft radioamateurs realtime inzicht in HF-propagatie, zonne-activiteit en DX-mogelijkheden — verpakt in een moderne donkere GUI die volledig op het scherm past bij opstarten.

---

## ✨ Features

### 🌍 Interactieve Wereldkaart
- Equirectangulaire NASA-kaart, automatisch gedownload bij eerste gebruik
- **Altijd correcte 2:1 verhouding** — geen horizontale vervorming
- **Dag/nacht-terminator** met zachte overgangszone
- **Graylijn** (amber band, ~1000 km breed)
- **Zon- en maanpositie** (geocentrisch berekend)
- **QTH-markering** (blauw kruisje) — lat/lon instelbaar in header
- **Groot-cirkelpad**: klik op kaart → afstand + richting + **band-kwaliteit voor dat traject**
- **ITU-regio overlay** R1/R2/R3 (officieel ITU RR Art. 5)
- **Maidenhead-locatorraster** (20° × 10°, labels AA–RR)
- **Callsign-prefix laag** (~110 DXCC-entiteiten)
- **Zoom/pan**: muiswiel 1×–8×, klik+sleep om te pannen, rechts om te resetten
- Render-cache met low-res maskers voor vloeiende zoom en pan

### 🛰️ Propagatiepadkaart
Klik op een bestemming op de kaart voor een directe padanalyse:
- **Band-kwaliteit** berekend op het midpunt van het groot-cirkelpad
- Dag/nacht correctie op het midpunt (juiste ionosferische condities)
- Aantal hops geschat (≈ afstand / 3500 km)
- Top-5 open banden getoond: `↳  8.847 km / 3 hops / dag  ▸  20m 87%  ·  17m 72%  ·  15m 54%  (MUF 24.1 MHz)`
- **Groot-cirkel lijn kleurt naar de beste band** (groen = 20m, geel = 17m, rood = 10m, …)

### 🌌 Aurora-ring overlay
- Magnetische aurora-ovaal op de kaart op basis van de K-index
- Berekend via **Feldstein/Holzworth** sferische trigonometrie op de geomagnetische dipool-pool (IGRF-2025: Noord 80.65°N/287.35°E, Zuid 80.65°S/107.35°E)
- Beide hemisferen als echte ovaal (niet als simpele breedteband)
- **Kleur op K-index**: groen (K < 3) · geel (K 3–5) · rood (K ≥ 6)
- K=0 → ovaal bij ~67° geomag. breedte · K=9 → ~44° (equatorwaarts)
- Selecteerbaar via **"Aurora"**-checkbox in de kaart-header

### 🔵 WSPR / PSKReporter spots op kaart
- Live propagatiepaden van **wspr.rocks** (WSPR) en **pskreporter.info** (FT8/FT4)
- Verbindingslijnen op de wereldkaart: **kleur = band**, **dikte = SNR**
- Selecteerbaar via checkbox in de kaart-header
- Geeft echte gemeten propagatie in plaats van alleen modelwaarden

### 📍 DX-spot markers op kaart
- Actieve DX-cluster spots als lijnen: stip op DX-locatie (DXCC-centroid) + lijn naar spotter
- Kleurcodering per band
- Toggle via **"Spots"**-checkbox in de kaart-header
- Klikken op een stip toont callsign, frequentie en comment als pop-up

### 🌞 Solar & Ionosfeer Data

| Parameter | Bron | Beschrijving |
|-----------|------|--------------|
| SFI | hamqsl.com | Solar Flux Index (10,7 cm) |
| SSN | hamqsl.com | Sunspot Number |
| A-index | hamqsl.com | Dagelijkse geomagnetische activiteit |
| K-index | hamqsl.com | 3-uurs geomagnetische activiteit (0–9) |
| X-ray | hamqsl.com | GOES röntgenflux (A/B/C/M/X klasse) |
| MUF | intern model | Maximum Usable Frequency (berekend) |
| LUF | intern model | Lowest Usable Frequency (berekend) |
| Solarwindsnelheid | NOAA SWPC | km/s via DSCOVR/ACE |
| Bz | NOAA SWPC | Interplanetair magneetveld Z-component (nT) |

- K-index kleurt **oranje** (K 3–4) of **rood** (K 5+)
- Bz kleurt **oranje** (≤ −10 nT) of **rood** (≤ −20 nT)
- K-index melding bij instelbare drempel (spinbox)
- Band-openings-notificatie bij instelbare kwaliteitsdrempel
- X-flare detectie → SWF-waarschuwing in paneel en systeemtray

### 📊 Bz 24-uurs mini-grafiek
Mini-tijdgrafiek onderaan het solar-paneel:
- **Blauw** = positief Bz (noordwaarts, gunstig)
- **Rood** = negatief Bz (zuidwaarts, geoeffectief)
- Nul-as gestippeld, Y-labels −20 / 0 / +20 nT
- Actuele Bz-waarde rechtsbovenin met kleurcode
- Data van **NOAA SWPC** `mag-1-day.json`, 240 punten over 24 uur

### 📶 HF Band Betrouwbaarheid
- Intern MUF/LUF-model op basis van SFI, SSN, K-index en QTH-breedtegraad
- SNR-budget gecorrigeerd voor **mode**, **vermogen** en **antenne**
- Modes: SSB (0 dB) · CW (+10 dB) · FT8 (+25 dB) · AM (−6 dB)
- Vermogens: 5 W – 1 kW · Antennes: Dipole, EFHW, Yagi, Beam, Quad, …
- Kleurbalken: groen ≥ 60 % · geel 30–59 % · rood 1–29 % · grijs gesloten
- Licentieklasse per band (N = Novice/Basis · F = Full/HAREC)
- FT8-frequentie en aanbevolen modi per band
- **CAT-integratie**: klik op een bandbalk → stuurt startfrequentie naar de radio
- **VFO-A/B markers** op de bandbalken (wit = VFO-A, blauw = VFO-B)

### 🔔 Notificaties & Alarmen
- **K-index alarm**: tray-melding bij overschrijden van instelbare drempel (spinbox 1–9)
- **Band-openings-notificatie**: melding als een band opengaat boven instelbare drempel
  - Spinbox "Band open ≥" (10–90%, stap 5%, standaard 40%)
  - Voorbeeld: `📡 Band geopend — 20m (78%) — kwaliteit ≥ 40%`
- **X-flare waarschuwing**: detectie van M/X-klasse flares met herstelschatting
- **PCA-melding**: Polar Cap Absorption bij verhoogde protonflux
- Alle drempelwaarden opgeslagen in `HAMIOS.ini`

### 🔌 CAT Interface
Directe besturing van de transceiver via serieel USB, instelbaar via de **CAT**-knop in de header.

| Radio type | Protocol | Commando |
|------------|----------|----------|
| Yaesu FT-950 e.a. | Yaesu CAT | `VS0;FA{11 digits};` |
| Kenwood / Elecraft | Kenwood CAT | `FA{11 digits};` |
| Icom | CI-V binair BCD | instelbaar adres (0x70 standaard) |

- **VFO-A en VFO-B** worden elke 2 seconden uitgelezen via `FA;FB;`
- VFO-A/B frequentie zichtbaar onder het HF-betrouwbaarheidspaneel
- **CAT terminal venster**: schakel "Terminal" in naast de VFO-weergave
  - 🟡 Geel `▶` = verzonden commando's
  - 🔵 Blauw `◀` = ontvangen data van de radio
- Poll-lock voorkomt conflicten tussen polling-thread en klik-naar-afstemmen

### 🕐 Bandopenings-schema
- 24-uur heatmap voor alle 11 HF-banden
- Tijdas in lokale tijd (CET/CEST), huidige tijd gemarkeerd
- Hover-tooltip: band · uur · kwaliteit % · FT8-freq · modi

### 📈 Band Verloop
- Tijdgrafiek van alle HF-banden (%) — 90 dagen bewaard in CSV
- Tijdbereik: Uren · Dagen · Weken · Maanden
- Klikbare legenda, hover-tooltip per tijdstip

### 📻 Live DX Spots
- JSON-feed van dxwatch.com, ververst elke 2 minuten
- Gefilterd op HF-banden · Eigen continent toggle
- Kolommen: UTC · Band · DX · MHz · Spotter · Comment
- Scrollbaar met muiswiel

### 💡 Propagatie-analyse & Advies
12 analyse-kaarten in 3 kolommen × 4 rijen, automatisch bijgewerkt.
**Gele stip** rechtsbovenin kaart = nieuwe gegevens beschikbaar.

| # | Kaart | Inhoud |
|---|-------|--------|
| 1 | 📡 Beste banden | Top-5 open banden met kwaliteitspercentage |
| 2 | ✅/⚠️ Geo-storm | K + A-index, routeadvies, ernst |
| 3 | ☀️ Zonactiviteit | SFI + SSN, zonnecyclus-fase |
| 4 | 💨 Solarwind | Snelheid + Bz-impact |
| 5 | ☢️ X-flare/SWF | Xray-klasse, herstelschatting |
| 6 | 📶 Ionosfeer | MUF, LUF-schatting, F2-laag |
| 7 | 🌅 Dag/nacht | Grey-line tijdvensters per uurblok |
| 8 | 🔧 Modus-advies | FT8 vs SSB/CW op basis van SNR-budget |
| 9 | 🧲 Absorptie | Auroraal absorptie poolroutes (QTH-lat) |
| 10 | 📊 Overall score | Samengesteld propagatie-oordeel |

### 🌐 Meertalig
Volledig vertaald in **6 talen** — te wisselen in de header:

| Code | Taal |
|------|------|
| NL | Nederlands |
| EN | English |
| DE | Deutsch |
| FR | Français |
| IT | Italiano |
| ES | Español |

Alle interface-teksten, analyses, helpteksten en tooltips zijn vertaald.

### ⚙️ Overig
- **Systeemtray**: minimaliseren naar tray, notificaties voor band-openings en K-index
- **Tooltips** met uitleg per solar-parameter (350 ms vertraging, schermrand-detectie)
- **Automatische refresh**: Uit / 30 s / 1 min / 5 min / 10 min / 30 min / 1 uur
- **Scrollende ticker** onderaan met actuele propagatietips (aan/uit via checkbox)
- **Nieuw-bericht indicator**: gele stip in advieskaart bij verse data
- Alle instellingen opgeslagen in `HAMIOS.ini` — persistent tussen sessies
- Venster past automatisch op schermgrootte bij opstarten

---

## 🖥️ Installatie

### Vereisten
```bash
pip install pillow
```
Optioneel (systeemtray):
```bash
pip install pystray
```
Optioneel (CAT-interface):
```bash
pip install pyserial
```

### Starten
```bash
python HAMIOS.py
```

### Standalone EXE (Windows) — aanbevolen
Download `HAMIOS.exe` uit de [laatste release](https://github.com/fvdijke/HAMIOS/releases) en voer direct uit. Geen Python vereist.

Of zelf bouwen:
```bash
pip install pyinstaller
pyinstaller HAMIOS.spec
# → dist\HAMIOS.exe
```

---

## 🔭 Propagatiemodel

**MUF** (Maximum Usable Frequency):
```
foF2 = 4.0 + (SFI − 70) × 0.065 + SSN × 0.012
MUF  = foF2 × breedtegraad-factor × dag/nacht-factor × 3.8
```

**LUF** (Lowest Usable Frequency):
```
LUF = (3.5 + K × 0.8) × auroraal-factor / 10^(SNR/20)
```

**Bandkwaliteit**: optimum rond 55 % van het MUF/LUF-venster → 100 %.

**Propagatiepad**: midpunt van het groot-cirkelpad gebruikt voor MUF/LUF-berekening, met dag/nacht correctie op dat midpunt.

---

## ⌨️ Muisinteractie

| Actie | Effect |
|-------|--------|
| Muiswiel op kaart | Zoom 1×–8× (cursor-gecentreerd) |
| Klik + sleep op kaart | Pan viewport |
| Linkermuisklik op kaart | Groot-cirkelpad + padpropagatie instellen |
| Rechtermuisklik op kaart | Reset zoom/pan · wis groot-cirkelpad |
| Muiswiel op DX-paneel | Scroll door spotlijst |
| Hover op kaart/banden/grafiek | Gedetailleerde tooltip |
| Klik op legenda-label | Band aan/uitzetten in historiekgrafiek |
| Klik op bandbalk (CAT aan) | Stuur startfrequentie naar radio |

---

## 💻 Systeemvereisten

| | Minimum | Aanbevolen |
|-|---------|-----------|
| OS | Windows 10 | Windows 11 |
| Schermresolutie | 1280 × 800 | 1920 × 1080 |
| Python | 3.10 | 3.12+ |
| Internet | Vereist (data-feeds) | — |

---

## 🔧 Toekomstige ideeën

- SDR-integratie
- Logging-koppeling (ADIF/WSJTX)
- Satelliet tracking
- Webversie

---

## 📜 Licentie

Vrij te gebruiken voor persoonlijk, niet-commercieel amateur radio gebruik.
Voor commerciële toepassingen: neem contact op.

---

## 🤝 Bijdragen

Pull requests, ideeën en verbeteringen zijn welkom.
Dit project leeft van experimenteren — net als de hobby zelf.

---

*73 de PA3FVD · veel DX!*
