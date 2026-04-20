# 📡 HAMIOS v2.3
<img width="1743" height="1416" alt="HAMIOS v2 3" src="https://github.com/user-attachments/assets/3045d73a-9008-43d8-9dea-3d3fd5102792" />

**Multilingual + Multi overlay**
<img width="1743" height="1416" alt="HAMIOS-ALL v2 3" src="https://github.com/user-attachments/assets/4250a620-1bac-4867-9d78-0ac172a26e89" />

**HAM-radio propagatie- en DX-monitor voor Windows**

> v2.3 — Propagatiepadkaart · Bz 24h-grafiek · Selecteerbare notificaties · Aurora-ring overlay · WSPR/PSKReporter spots · DX-spot markers · 14 talen via externe taalpakketten

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
- **Kaart-selectievakjes** (Zon, Maan, Graylijn, Aurora, WSPR, Spots, ITU, CS, Locator) in een eigen balk **onder de kaart**

### 🛰️ Propagatiepadkaart
Klik op een bestemming op de kaart voor een directe padanalyse:
- **Band-kwaliteit** berekend op het midpunt van het groot-cirkelpad
- Dag/nacht correctie op het midpunt (juiste ionosferische condities)
- Aantal hops geschat (≈ afstand / 3500 km)
- Top-5 open banden getoond: `↳  8.847 km / 3 hops / dag  ▸  20m 87%  ·  17m 72%  ·  15m 54%  (MUF 24.1 MHz)`
- **Groot-cirkel lijn kleurt naar de beste band** (groen = 20m, geel = 17m, rood = 10m, …)

### 🌌 Aurora-ring overlay
- Magnetische aurora-ovaal op de kaart op basis van de K-index
- Berekend via **Feldstein/Holzworth** sferische trigonometrie (IGRF-2025)
- Beide hemisferen als echte ovaal
- **Kleur op K-index**: groen (K < 3) · geel (K 3–5) · rood (K ≥ 6)
- **Zachte gloed** — fade-effect in 6 lagen (zelfde stijl als graylijn)

### 🔵 WSPR / PSKReporter spots op kaart
- Live propagatiepaden van **wspr.rocks** (WSPR) en **pskreporter.info** (FT8/FT4)
- Verbindingslijnen op de wereldkaart: **kleur = band**, **dikte = SNR**

### 📍 DX-spot markers op kaart
- Actieve DX-cluster spots: stip op DX-locatie + lijn naar spotter, kleurcodering per band
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

### 📊 Bz 24-uurs mini-grafiek
- **Blauw** = positief Bz (gunstig) · **Rood** = negatief Bz (geoeffectief)
- 240 datapunten over 24 uur · Y-labels −20 / 0 / +20 nT
- Vergroot grafiekgebied voor betere leesbaarheid

### 📶 HF Band Betrouwbaarheid
- Intern MUF/LUF-model op basis van SFI, SSN, K-index en QTH-breedtegraad
- SNR-budget gecorrigeerd voor **mode**, **vermogen** en **antenne**
- Kleurbalken: groen ≥ 60 % · geel 30–59 % · rood 1–29 % · grijs gesloten
- Licentieklasse per band (N = Novice/Basis · F = Full/HAREC)

### 🔔 Notificaties & Alarmen — volledig selecteerbaar

Elk notificatietype is **afzonderlijk aan/uit te zetten** via een checkbox in het solar-paneel:

| Notificatie | Instelling | Beschrijving |
|-------------|-----------|--------------|
| ⚠️ K-index storm | Checkbox + drempel (spinbox 1–9) | Melding bij stijging boven drempel |
| 📡 Band geopend | Checkbox + drempel (spinbox 10–90 %) | Melding als band opengaat |
| ☢️ X-flare / SWF | Checkbox | M/X-klasse flare detectie |
| 🟣 PCA / Proton event | Checkbox | Polar Cap Absorption melding |

Alle drempelwaarden en aan/uit-staten worden opgeslagen in `HAMIOS.ini`.

### 🔌 CAT Interface *(tijdelijk uitgeschakeld)*

> ⚠️ De CAT-interface is tijdelijk uitgeschakeld in afwachting van verdere ontwikkeling en stabiliteitstests. De code is intact — de functionaliteit wordt in een volgende versie afgerond.

### 🕐 Bandopenings-schema
- 24-uur heatmap voor alle 11 HF-banden
- Tijdas in lokale tijd (CET/CEST), huidige tijd gemarkeerd

### 📈 Band Verloop
- Tijdgrafiek van alle HF-banden (%) — 90 dagen bewaard in CSV
- Tijdbereik: Uren · Dagen · Weken · Maanden

### 📻 Live DX Spots
- JSON-feed van dxwatch.com, ververst elke 2 minuten
- Kolommen: UTC · Band · DX · MHz · Spotter · Comment

### 💡 Propagatie-analyse & Advies
12 analyse-kaarten in 3 kolommen × 4 rijen, automatisch bijgewerkt.

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
- **Systeemtray**: minimaliseren naar tray, tray-notificaties
- **Tooltips** met uitleg per solar-parameter
- **Automatische refresh**: Uit / 30 s / 1 min / 5 min / 10 min / 30 min / 1 uur
- **Scrollende ticker** met actuele propagatietips
- Alle instellingen opgeslagen in `HAMIOS.ini`

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

### Starten
```bash
python HAMIOS.py
```

### Standalone EXE (Windows) — aanbevolen
Download `HAMIOS.exe` uit de [laatste release](https://github.com/fvdijke/HAMIOS/releases) en voer direct uit. Geen Python vereist.

> **Let op**: zorg dat de `langs/`-map naast de EXE staat zodat de taalpakketten beschikbaar zijn.

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
| Schermresolutie | 1280 × 800 | 1920 × 1080 |
| Python | 3.10 | 3.12+ |
| Internet | Vereist (data-feeds) | — |

---

## 🔧 Toekomstige ideeën

- CAT-interface stabiliseren (Yaesu/Kenwood/Icom)
- SDR-integratie
- Logging-koppeling (ADIF/WSJTX)
- Satelliet tracking

---

## 📜 Licentie

Vrij te gebruiken voor persoonlijk, niet-commercieel amateur radio gebruik.

---

*73*
