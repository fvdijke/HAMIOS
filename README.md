<img width="1743" height="1416" alt="HAMIOS v2 3" src="https://github.com/user-attachments/assets/3045d73a-9008-43d8-9dea-3d3fd5102792" />

# 📡 HAMIOS v2.3

**HAM-radio propagatie- en DX-monitor voor Windows**

> v2.3 — timestamp weg uit solar-paneel · twee scheidingslijnen in solar (params/band, band/waarschuwingen) · X-flare en PCA volledig zichtbaar · advieskaarten 4 rijen altijd volledig zichtbaar

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
- **Groot-cirkelpad**: klik op kaart → afstand + richting; rechtsmuisklik wist
- **Auroraal absorptie-ovaal** bij K-index ≥ 4
- **ITU-regio overlay** R1/R2/R3 (officieel ITU RR Art. 5)
- **Maidenhead-locatorraster** (20° × 10°, labels AA–RR)
- **Callsign-prefix laag** (~110 DXCC-entiteiten)
- **Zoom/pan**: muiswiel 1×–8×, klik+sleep om te pannen, rechts om te resetten
- Render-cache met low-res maskers voor vloeiende zoom en pan

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
- Melding bij K ≥ instelbare drempel (spinbox naast K-index)
- X-flare detectie → SWF-waarschuwing in paneel en systeemtray

### 📶 HF Band Betrouwbaarheid
- Intern MUF/LUF-model op basis van SFI, SSN, K-index en QTH-breedtegraad
- SNR-budget gecorrigeerd voor **mode**, **vermogen** en **antenne**
- Modes: SSB (0 dB) · CW (+10 dB) · FT8 (+25 dB) · AM (−6 dB)
- Vermogens: 5 W – 1 kW · Antennes: Dipole, EFHW, Yagi, Beam, Quad, …
- Kleurbalken: groen ≥ 60 % · geel 30–59 % · rood 1–29 % · grijs gesloten
- Licentieklasse per band (N = Novice/Basis · F = Full/HAREC)
- FT8-frequentie en aanbevolen modi per band
- Alleen HF-banden (160 m – 6 m)

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
12 analyse-kaarten in 3 kolommen × 4 rijen, automatisch bijgewerkt:

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

### ⚙️ Overig
- **Systeemtray**: minimaliseren naar tray, notificaties voor band-openings en K-index
- **Tooltips** met uitleg per solar-parameter (350 ms vertraging, schermrand-detectie)
- **Automatische refresh**: Uit / 30 s / 1 min / 5 min / 10 min / 30 min / 1 uur
- **Scrollende ticker** onderaan met actuele propagatietips
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

---

## ⌨️ Muisinteractie & sneltoetsen

| Actie | Effect |
|-------|--------|
| Muiswiel op kaart | Zoom 1×–8× (cursor-gecentreerd) |
| Klik + sleep op kaart | Pan viewport |
| Linkermuisklik op kaart | Groot-cirkelbestemming instellen |
| Rechtermuisklik op kaart | Reset zoom/pan · wis groot-cirkelpad |
| Muiswiel op DX-paneel | Scroll door spotlijst |
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

- Meerdere talen (NL / EN / DE / FR)
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
