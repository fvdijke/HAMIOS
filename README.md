<img width="1731" height="1372" alt="HAMIOS v2 0" src="https://github.com/user-attachments/assets/4ca91ba4-1fc0-4541-9c97-348d8c61710c" />
HAMIOS

# 📡 HAMIOS v2.0

**HAMIOS** is een krachtige desktop tool voor radioamateurs die realtime inzicht geeft in HF-propagatie, zonne-activiteit en DX-mogelijkheden — verpakt in een moderne, donkere GUI.

Ontwikkeld door Frank van Dijke.

---

## 🚀 Features

### 🌞 Solar & Ionosfeer Data

* Real-time data van o.a.:

  * Solar Flux Index (SFI)
  * Sunspot Number (SSN)
  * A- en K-index
  * X-ray flux
  * MUF (Maximum Usable Frequency)
* Solarwind data:

  * Snelheid (km/s)
  * Bz-component (geomagnetische impact)
* Automatische updates via externe bronnen (NOAA / HamQSL)

---

### 📡 HF Propagation Analyse

* Slim MUF/LUF-model voor bandvoorspellingen
* Betrouwbaarheidsscore per band (160m t/m 6m)
* Invloed van:

  * Tijd (dag/nacht)
  * Vermogen
  * Mode (SSB / CW / FT8)
  * Antenne-type
* Ondersteuning voor VHF/UHF indicaties

---

### 🌍 Interactieve Wereldkaart

* Equirectangular wereldkaart (NASA)
* Overlays:

  * Dag/nacht terminator
  * Grayline (DX sweet spot)
  * Zon- en maanpositie
  * ITU-regio’s
  * Callsign prefixes (~110 DXCC entiteiten)
* Functionaliteit:

  * Zoom (muiswiel)
  * Pan (klik + drag)
  * Reset (rechtermuisklik)
  * Groot-cirkel routes berekenen

---

### 📊 Band Activiteit & Historie

* Band openingsschema per uur
* Historische grafieken (tot 90 dagen)
* Selecteerbare banden
* Trendanalyse van condities

---

### 📻 DX Cluster Integratie

* Live DX spots van DXWatch
* Filtering op HF-banden
* Callsign → continent mapping
* Frequentie, tijd en commentaar zichtbaar

---

### ⚙️ Configuratie & Opslag

* Instellingen via `HAMIOS.ini`
* Historische data in CSV (`HAMIOS_history.csv`)
* Volledig lokaal draaiend (geen cloud dependency)

---

### 🧠 Slimme Details

* Tooltips met uitleg (ook voor beginners)
* Automatische refresh intervals
* K-index alerts
* Tray ondersteuning (indien beschikbaar)
* Dag/nacht detectie op jouw QTH

---

## 🖥️ Requirements

* Python 3.x
* Vereiste packages:

```bash
pip install pillow
```

Optioneel:

```bash
pip install pystray
```

---

## 📦 Installatie

1. Clone deze repository:

```bash
git clone https://github.com/fvdijke/fvdijke.git
```

2. Ga naar de map:

```bash
cd fvdijke
```

3. Installeer dependencies:

```bash
pip install pillow
```

4. Start de applicatie:

```bash
python HAMIOS.py
```

---

## ⚡ Gebruik

* Stel je QTH in (lat/lon)
* Kies mode, vermogen en antenne
* Bekijk realtime propagatie en DX kansen
* Gebruik de kaart voor visuele analyse
* Check DX spots voor live activiteit

---

## 🔧 Toekomstige ideeën

* SDR integratie
* Logging koppeling (ADIF)
* AI-gegenereerde band voorspellingen
* Satelliet tracking
* Webversie

---

## 📝 Changelog (v2.0 highlights)

* Zoom & pan functionaliteit toegevoegd aan kaart
* Solarwind data geïntegreerd
* Callsign prefix overlay toegevoegd
* Verbeterde tooltips en UI
* Performance optimalisaties (o.a. caching)

---

## 📜 License

Vrij te gebruiken voor persoonlijk gebruik.
Voor commerciële toepassingen: neem contact op.

---

## 🤝 Bijdragen

Pull requests, ideeën en verbeteringen zijn welkom!
Dit project leeft van experimenteren — net als de hobby zelf 😉

---

## 📡 Tot slot

HAMIOS is gebouwd vanuit passie voor radio, propagatie en DX.
Of je nu jaagt op verre stations of gewoon wilt begrijpen wat de ionosfeer vandaag van plan is — deze tool helpt je een stap verder.

*73 en veel DX!*
