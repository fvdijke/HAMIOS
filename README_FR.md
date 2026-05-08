# 📡 HAMIOS v4.0.1

**Moniteur de propagation HF et DX pour Windows**

> v4.0.1 — Panneaux déplaçables et redimensionnables · Boîte de dialogue Paramètres unifiée · Optimisations des performances · Graphique historique solaire

*Conceived by Frank van Dijke · Developed with Claude AI*

HAMIOS donne aux radioamateurs un aperçu en temps réel de la propagation HF, de l'activité solaire et des opportunités DX — dans une interface graphique sombre et moderne.

---

## ✨ Fonctionnalités

### 🌍 Carte mondiale interactive *(centrée dans la fenêtre)*
- Carte NASA équirectangulaire, téléchargée automatiquement au premier démarrage
- **Hauteur fixe (380 px)** avec rendu 2:1 correct — pas de distorsion horizontale
- **Terminateur jour/nuit** avec zone de transition douce
- **Ligne grise** (bande ambrée, ~1000 km de large)
- **Position du soleil et de la lune** (calcul géocentrique)
- **Marqueur QTH** (réticule bleu) — lat/lon configurable dans l'en-tête
- **Chemin grand cercle** : clic sur carte → distance + gisement + **qualité de bande pour ce trajet**
- **Superposition régions UIT** R1/R2/R3 (UIT RR Art. 5 officiel)
- **Grille de locateurs Maidenhead** (20° × 10°, labels AA–RR)
- **Couche préfixes indicatifs** (~110 entités DXCC)
- **Zoom/panoramique** : molette 1×–8×, clic+glisser pour panoramique, clic droit pour réinitialiser
- **Superpositions groupées** sous la carte :
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

### 🖥️ Système de panneaux *(v4.0.1)*
- **11 panneaux librement déplaçables et redimensionnables** sur un canevas de bureau libre
- Chaque panneau a une bordure ambrée de 1px, une barre de titre avec bouton ✕ de fermeture et une poignée ◢ de redimensionnement
- **Alignement sur grille** (2px) au relâchement du glisser/redimensionnement pour un alignement propre
- Panneaux : Fiabilité des bandes HF · Carte mondiale · Solaire/Ionosphère · Alertes · Planning des bandes · Historique des bandes · Kp 48h · Bz 24h · Rayons X 24h · Spots DX · Conseils de propagation
- **⚙ Boîte de dialogue Paramètres** contient toute la configuration : QTH · Langue · Thème · Infobulles · Ticker · Heure d'été · Visibilité des panneaux · Gestion de la mise en page
- **Préréglages de mise en page** : sauvegarder/charger/écraser/supprimer des profils nommés dans `hamios_layouts.json`
- **Enregistrer par défaut** : enregistre la mise en page actuelle comme mise en page de démarrage

### 🛰 Suivi de satellites *(bouton 🛰 Sat dans l'en-tête)*
- Données TLE téléchargées depuis **Celestrak** (Amateur / ISS / Weather / CubeSat)
- **Filtre par catégorie** : Tous · Amateur · ISS · Weather · CubeSat
- Par satellite : activer/désactiver **point de position** (●), **trajectoire orbitale** (~) et **empreinte** sur la carte
- **L'empreinte devient verte** quand le QTH est dans la zone de couverture du satellite
- **Panneau de notifications** affiche les satellites actuellement au-dessus du QTH avec l'angle d'élévation
- Horaires de trajectoire en heure locale (CEST / CET)
- Bouton **↻ TLE** pour rafraîchissement manuel des éléments orbitaux
- Mis en cache dans `hamios_tle.json`

### 🕵 Stations espions / à chiffres *(bouton 🕵 Spy dans l'en-tête)*
- Tableau défilant de 24 stations à chiffres et stations radio espions connues
- Colonnes : statut (● actif / historique), nom, pays, fréquences, mode
- **Colonnes triables** — cliquer sur un en-tête pour trier ; cliquer à nouveau pour inverser
- **Filtre** par statut actif/inactif et recherche en texte libre (nom, pays, fréquence)
- **Survol** d'une ligne pour afficher la description complète + programme de diffusion
- Fichier de données : `hamios_spy_stations.json` (modifiable)

### 🔵 WSPR / PSKReporter Spots on Map
- Live propagation paths from **wspr.rocks** (WSPR) and **pskreporter.info** (FT8/FT4)
- Connection lines: **colour = band**, **thickness = SNR**

### 📍 DX Spot Markers on Map
- Active DX cluster spots: dot at DX location + line to spotter, colour-coded by band
- Click a dot to show callsign, frequency and comment

### 🌞 Données solaires et ionosphériques

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
| 🛰 Satellite au-dessus | Toujours actif | Indique quels satellites sélectionnés sont au-dessus du QTH avec l'élévation |

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

### ⚙️ Autres
- **Thèmes dynamiques** : Midnight · DeepOcean · HighContrast
- **Barre des tâches** : réduire dans la barre, notifications
- **Infobulles** avec explication par paramètre solaire
- **Actualisation automatique** : Désactivé / 30 s / 1 min / 5 min / 10 min / 30 min / 1 heure
- **Ticker défilant** avec conseils de propagation actuels
- **Système de panneaux déplaçables** : arrangez et redimensionnez librement tous les panneaux
- **Préréglages de mise en page** : enregistrez et basculez entre des arrangements de panneaux personnalisés
- Tous les paramètres sauvegardés dans `HAMIOS.ini`

---

## 🖥️ Mise en page (v4.0.1) — Panneaux flottants libres

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ⚙ Paramètres  (QTH · Langue · Thème · Infobulles · Ticker · Heure d'été · Panneaux · Mises en page) │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────────────────────┐  ┌──────────────┐  │
│  │Solar/Ionosph.│  │      Carte mondiale       ✕  │  │Bandes HF ✕  │  │
│  │     ✕    ◢  │  │   zoom/pan · overlays     ◢  │  │Fiabilité  ◢ │  │
│  └──────────────┘  └──────────────────────────────┘  └──────────────┘  │
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │Planning band│  │Historiq.band│  │  Kp 48h  │  │  Spots DX    ✕  │  │
│  │    ✕    ◢  │  │    ✕    ◢  │  │  ✕    ◢  │  │             ◢  │  │
│  └─────────────┘  └─────────────┘  └──────────┘  └──────────────────┘  │
│                                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────────────────┐  │
│  │  Bz 24h  │  │Rayons X24h│  │  Conseils de propagation        ✕  │  │
│  │  ✕    ◢  │  │  ✕    ◢  │  │                               ◢  │  │
│  └──────────┘  └──────────┘  └──────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Alertes  ✕  ◢                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Tous les panneaux : bordure ambrée · ✕ fermer · ◢ taille · grille(2px)│
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Installation

### Étape 1 — Prérequis Python

```bash
pip install pillow
```

Optional for system tray notifications:

```bash
pip install pystray
```

### Étape 2 — Installer les packs de langue

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

### Étape 3 — Lancer

```bash
python HAMIOS.py
```

### EXE autonome (Windows) — recommandé

Download `HAMIOS.exe` and the `langs/` folder from the [latest release](https://github.com/fvdijke/HAMIOS/releases). No Python required.

Build from source:

```bash
pip install pyinstaller
pyinstaller HAMIOS.spec
# → dist\HAMIOS.exe
# Then copy langs\ next to the EXE
```

---

## 📁 Fichiers de données

| Fichier | Contenu |
|---------|---------|
| `HAMIOS.ini` | Tous les paramètres utilisateur (QTH, thème, langue, seuils d'alerte, …) |
| `hamios_layouts.json` | Préréglages de mise en page des panneaux |
| `hamios_tle.json` | Éléments orbitaux TLE en cache pour le suivi des satellites |
| `hamios_spy_stations.json` | Base de données stations espions/à chiffres (modifiable) |
| `langs/*.json` | Packs de langue |

---

## 🔭 Modèle de propagation

```
foF2 = 4.0 + (SFI − 70) × 0.065 + SSN × 0.012
MUF  = foF2 × latitude-factor × day/night-factor × 3.8
LUF  = (3.5 + K × 0.8) × auroral-factor / 10^(SNR/20)
```

**Band quality**: optimum around 55 % of the MUF/LUF window → 100 %.

---

## ⌨️ Interaction souris

| Action | Effect |
|--------|--------|
| Scroll wheel on map | Zoom 1×–8× |
| Click + drag on map | Pan viewport |
| Left-click on map | Great-circle path + path propagation |
| Right-click on map | Reset zoom/pan · clear path |
| Hover on map / bands / chart | Detailed tooltip |
| Click on legend label | Toggle band in history chart |

---

## 💻 Configuration requise

| | Minimum | Recommended |
|-|---------|------------|
| OS | Windows 10 | Windows 11 |
| Screen resolution | 1280 × 900 | 1920 × 1080 or wider |
| Python | 3.10 | 3.12+ |
| Internet | Required (data feeds) | — |

> v4.0.1 utilise un canevas de panneaux libre. Arrangez les panneaux librement sur n'importe quelle taille d'écran. Un écran large (≥ 1920 px) offre l'espace de travail le plus confortable.

---

## 🔧 Idées futures

- Stabilise CAT interface (Yaesu/Kenwood/Icom)
- SDR integration
- Logging connection (ADIF/WSJTX)

---

## 📜 Licence

Gratuit pour usage personnel et non commercial en radioamateurisme.

---

