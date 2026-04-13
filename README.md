<img width="1726" height="1190" alt="HAMIOS v2 0" src="https://github.com/user-attachments/assets/73c7df2a-fd66-4cc9-a54e-5a0cec279561" />

# 📡 HAMIOS v2.0

**HAMIOS** is een krachtige desktop tool voor radioamateurs die realtime inzicht geeft in HF-propagatie, zonne-activiteit en DX-mogelijkheden — verpakt in een moderne, donkere GUI.

Ontwikkeld door **Frank van Dijke ()**.

---

## 🚀 Features

### 🌍 Interactieve Wereldkaart
- Equirectangulaire NASA-kaart (2048 × 1024, automatisch gedownload)
- Exacte 2:1 verhouding, past zich aan bij vensterbreedte
- **Dag/nacht-terminator** met zachte overgangszone
- **Graylijn** (amber terminator-band, ~1000 km breed)
- **Zon- en maanpositie** (geocentrisch berekend)
- **QTH-markering** (blauw kruisje); lat/lon instelbaar in header
- **Groot-cirkelpad**: klik → afstand en richting; rechtermuisklik wist
- **Auroraal absorptie-ovaal** bij K ≥ 4
- **ITU-regio overlay** R1/R2/R3 (officieel ITU RR Art. 5)
- **Maidenhead-locatorraster** (20° × 10°, labels AA–RR)
- **Callsign-prefix laag** (~110 DXCC-entiteiten)
- **Zoom/pan**: muiswiel 1×–8×, click+drag pant, rechts reset

### 🌞 Solar & Ionosfeer Data

| Parameter | Bron | Beschrijving |
|-----------|------|--------------|
| SFI | hamqsl.com | Solar Flux Index op 10,7 cm |
| SSN | hamqsl.com | Sunspot Number |
| A-index | hamqsl.com | Dagelijkse geomagnetische activiteit |
| K-index | hamqsl.com | 3-uurs geomagnetische activiteit (0–9) |
| X-ray | hamqsl.com | GOES röntgenflux (A/B/C/M/X klasse) |
| MUF | hamqsl.com | Maximum Usable Frequency |
| Solarwindsnelheid | NOAA SWPC | km/s via DSCOVR/ACE |
| Bz | NOAA SWPC | Interplanetair magneetveld Z-component (nT) |

- K-index kleurt **oranje** (K 3–4) of **rood** (K 5+)
- Bz kleurt **oranje** (≤ −10 nT) of **rood** (≤ −20 nT)
- X-flare detectie → SWF-waarschuwing in paneel en systeemtray

### 📶 HF Band Betrouwbaarheid
- Intern MUF/LUF-model (SFI, SSN, K-index, QTH-breedtegraad)
- SNR-budget gecorrigeerd voor **mode**, **vermogen** en **antenne**
- Modes: SSB (0 dB) · CW (+10 dB) · FT8 (+25 dB) · AM (−6 dB)
- Vermogens: 5W – 1 kW · Antennes: Dipole, EFHW, Yagi, Beam, Quad…
- Kleurbalken: groen ≥60% · geel 30–59% · rood 1–29% · grijs dicht
- Licentieklasse per band (N = Novice/Basis, F = Full/HAREC)
- FT8-frequentie en aanbevolen modi per band

### 🕐 Bandopenings-schema
- 24-uur heatmap voor alle 11 HF-banden (160m – 6m)
- Tijdas in lokale tijd (CET/CEST), huidige tijd gemarkeerd
- Hover-tooltip: band, uur, kwaliteit %, FT8-freq, modi

### 📈 Band Verloop (historiek)
- Grafiek van alle HF-banden (%) over tijd — 90 dagen bewaard in CSV
- Tijdbereik: Uren · Dagen · Weken · Maanden
- Toggle: **Banden** of **Solar** (SFI/SSN/K/A)
- Klikbare legenda, hover-tooltip per tijdstip

### 📻 Live DX Spots
- JSON-feed van dxwatch.com, ververst elke 2 minuten
- Gefilterd op HF-banden · Eigen continent toggle
- Kolommen: UTC · Band · DX · MHz · Spotter · Comment
- Scrollbaar met muiswiel

### 💡 Propagatie-analyse & Advies
10 analyse-kaarten in 3 kolommen, automatisch bijgewerkt:

| # | Kaart | Inhoud |
|---|-------|--------|
| 1 | 📡 Beste banden | Top-5 open banden met percentage |
| 2 | ✅/⚠️ Geo-storm | K + A-index, routeadvies, ernst |
| 3 | ☀️ Zonactiviteit | SFI + SSN, zonnecyclus-fase |
| 4 | 💨 Solarwind | Snelheid + Bz-impact |
| 5 | ☢ X-flare/SWF | Xray-klasse, herstelschatting |
| 6 | 📶 Ionosfeer | MUF, LUF-schatting, F2-laag |
| 7 | 🌅 Dag/nacht | Grey-line tijdvensters per uurblok |
| 8 | 🔧 Modus-advies | FT8 vs SSB/CW op basis van SNR-budget |
| 9 | 🧲 Absorptie | Auroraal absorptie poolroutes (QTH-lat) |
| 10 | 📊 Overall score | Samengesteld propagatie-oordeel |

### ⚙️ Overig
- **Systeemtray**: minimaliseren naar tray, band-opening en K-index notificaties
- **Tooltips** met uitleg per solar-parameter (350ms vertraging, schermrand-detectie)
- **Automatische refresh**: Uit / 30s / 1 min / 5 min / 10 min / 30 min / 1 uur
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

### Standalone EXE (Windows)
```bash
pip install pyinstaller
pyinstaller HAMIOS.spec
```
De executable verschijnt in `dist\HAMIOS.exe`.

---

## Propagatiemodel

**MUF** (Maximum Usable Frequency):
```
foF2 = 4.0 + (SFI − 70) × 0.065 + SSN × 0.012
MUF  = foF2 × breedtegraad-factor × dag/nacht-factor × 3.8
```

**LUF** (Lowest Usable Frequency):
```
LUF = (3.5 + K × 0.8) × auroraal-factor / 10^(SNR/20)
```

**Bandkwaliteit**: optimum rond 55% van het MUF/LUF-venster → 100%.

---

## Sneltoetsen & muisinteractie

| Actie | Effect |
|-------|--------|
| Muiswiel op kaart | Zoom 1×–8× (cursor-gecentreerd) |
| Klik + sleep | Pan viewport |
| Linkermuisklik | Groot-cirkelbestemming instellen |
| Rechtermuisklik | Reset zoom/pan of wis groot-cirkelpad |
| Muiswiel op DX-paneel | Scroll door spotlijst |
| Hover op banden/heatmap/grafiek | Gedetailleerde tooltip |
| Klik legenda-label | Band aan/uitzetten in historiekgrafiek |

---

## Systeemvereisten

| | Minimum | Aanbevolen |
|-|---------|-----------|
| OS | Windows 10 | Windows 11 |
| Schermresolutie | 1280 × 768 | 1920 × 1080 |
| Python | 3.10 | 3.12+ |
| Internet | Vereist | — |

---

## 🔧 Toekomstige ideeën

- SDR-integratie
- Logging-koppeling (ADIF)
- Satelliet tracking
- Webversie

---

## 📜 Licentie

Vrij te gebruiken voor persoonlijk, niet-commercieel amateur radio gebruik.
Voor commerciële toepassingen: neem contact op.

---

## 🤝 Bijdragen

Pull requests, ideeën en verbeteringen zijn welkom!
Dit project leeft van experimenteren — net als de hobby zelf 😉

---

*73 en veel DX!*
