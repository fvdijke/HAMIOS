# 📡 HAMIOS v4.0.1

**Monitor de propagación HF y DX para Windows**

> v4.0.1 — Paneles arrastrables y redimensionables · Cuadro de diálogo de Configuración unificado · Optimizaciones de rendimiento · Gráfico histórico solar

*Conceived by Frank van Dijke · Developed with Claude AI*

HAMIOS ofrece a los radioaficionados información en tiempo real sobre la propagación HF, actividad solar y oportunidades DX — en una interfaz gráfica moderna y oscura.

---

## ✨ Características

### 🌍 Mapa mundial interactivo *(centrado en la ventana)*
- Mapa NASA equirectangular, descargado automáticamente en el primer uso
- **Altura fija (380 px)** con renderizado 2:1 correcto — sin distorsión horizontal
- **Terminador día/noche** con zona de transición suave
- **Línea gris** (banda ámbar, ~1000 km de ancho)
- **Posición del sol y la luna** (cálculo geocéntrico)
- **Marcador QTH** (retículo azul) — lat/lon configurable en el encabezado
- **Trayectoria círculo máximo**: clic en mapa → distancia + rumbo + **calidad de banda para esa ruta**
- **Overlay regiones UIT** R1/R2/R3 (oficial UIT RR Art. 5)
- **Cuadrícula localizadores Maidenhead** (20° × 10°, etiquetas AA–RR)
- **Capa prefijos indicativos** (~110 entidades DXCC)
- **Zoom/desplazamiento**: rueda 1×–8×, clic+arrastrar para desplazar, clic derecho para restablecer
- **Superposiciones agrupadas** bajo el mapa:
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

### 🖥️ Sistema de paneles *(v4.0.1)*
- **11 paneles libremente arrastrables y redimensionables** sobre un lienzo de escritorio libre
- Cada panel tiene un borde ámbar de 1px, barra de título con botón ✕ de cierre y controlador ◢ de redimensionamiento
- **Ajuste a cuadrícula** (2px) al soltar tras arrastrar/redimensionar para una alineación limpia
- Paneles: Fiabilidad de bandas HF · Mapa mundial · Solar/Ionosfera · Alertas · Horario de bandas · Historial de bandas · Kp 48h · Bz 24h · Rayos X 24h · Spots DX · Asesoramiento de propagación
- **⚙ Cuadro de diálogo Configuración** contiene toda la configuración: QTH · Idioma · Tema · Información emergente · Ticker · Horario de verano · Visibilidad de paneles · Gestión de diseños
- **Preajustes de diseño**: guardar/cargar/sobrescribir/eliminar perfiles con nombre en `hamios_layouts.json`
- **Guardar como predeterminado**: guarda el diseño actual como diseño de inicio

### 🛰 Seguimiento de satélites *(botón 🛰 Sat en el encabezado)*
- Datos TLE descargados de **Celestrak** (Amateur / ISS / Weather / CubeSat)
- **Filtro por categoría**: Todos · Amateur · ISS · Weather · CubeSat
- Por satélite: activar/desactivar **punto de posición** (●), **trayectoria orbital** (~) y **huella** en el mapa
- **La huella se vuelve verde** cuando el QTH está dentro de la zona de cobertura del satélite
- **Panel de notificaciones** muestra los satélites actualmente sobre el QTH con ángulo de elevación
- Tiempos de trayectoria en hora local (CEST / CET)
- Botón **↻ TLE** para actualización manual de elementos orbitales
- Almacenado en caché en `hamios_tle.json`

### 🕵 Estaciones espía / números *(botón 🕵 Spy en el encabezado)*
- Tabla desplazable de 24 estaciones de números y estaciones de radio espía conocidas
- Columnas: estado (● activo / histórico), nombre, país, frecuencias, modo
- **Columnas ordenables** — clic en cualquier encabezado para ordenar; clic de nuevo para invertir
- **Filtro** por estado activo/inactivo y búsqueda de texto libre (nombre, país, frecuencia)
- **Pasar el ratón** sobre una fila para ver la descripción completa + horario de emisión
- Archivo de datos: `hamios_spy_stations.json` (editable)

### 🔵 WSPR / PSKReporter Spots on Map
- Live propagation paths from **wspr.rocks** (WSPR) and **pskreporter.info** (FT8/FT4)
- Connection lines: **colour = band**, **thickness = SNR**

### 📍 DX Spot Markers on Map
- Active DX cluster spots: dot at DX location + line to spotter, colour-coded by band
- Click a dot to show callsign, frequency and comment

### 🌞 Datos solares e ionosféricos

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
| 🛰 Satélite sobre QTH | Siempre activo | Muestra qué satélites seleccionados están sobre el QTH con elevación |

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

### ⚙️ Otros
- **Temas dinámicos**: Midnight · DeepOcean · HighContrast
- **Bandeja del sistema**: minimizar a la bandeja, notificaciones
- **Información emergente** con explicación por parámetro solar
- **Actualización automática**: Desactivado / 30 s / 1 min / 5 min / 10 min / 30 min / 1 hora
- **Ticker desplazable** con consejos de propagación actuales
- **Sistema de paneles arrastrables**: organiza y redimensiona libremente todos los paneles
- **Preajustes de diseño**: guarda y cambia entre disposiciones de paneles personalizadas
- Toda la configuración guardada en `HAMIOS.ini`

---

## 🖥️ Diseño (v4.0.1) — Paneles flotantes libres

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ⚙ Configuración  (QTH · Idioma · Tema · Infoemergente · Ticker · Hora verano · Paneles · Diseños) │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────────────────────┐  ┌──────────────┐  │
│  │Solar/Ionosfr.│  │      Mapa mundial         ✕  │  │Bandas HF ✕  │  │
│  │     ✕    ◢  │  │   zoom/pan · superpos.    ◢  │  │Fiabilidad ◢ │  │
│  └──────────────┘  └──────────────────────────────┘  └──────────────┘  │
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │HorarioBandas│  │HistorialBand│  │  Kp 48h  │  │  Spots DX    ✕  │  │
│  │    ✕    ◢  │  │    ✕    ◢  │  │  ✕    ◢  │  │             ◢  │  │
│  └─────────────┘  └─────────────┘  └──────────┘  └──────────────────┘  │
│                                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────────────────┐  │
│  │  Bz 24h  │  │Rayos X24h│  │  Asesoramiento propagación       ✕  │  │
│  │  ✕    ◢  │  │  ✕    ◢  │  │                               ◢  │  │
│  └──────────┘  └──────────┘  └──────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Alertas  ✕  ◢                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Todos los paneles: borde ámbar · ✕ cerrar · ◢ tamaño · cuadrícula(2px) │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Instalación

### Paso 1 — Requisitos de Python

```bash
pip install pillow
```

Optional for system tray notifications:

```bash
pip install pystray
```

### Paso 2 — Instalar paquetes de idioma

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

### Paso 3 — Ejecutar

```bash
python HAMIOS.py
```

### EXE autónomo (Windows) — recomendado

Download `HAMIOS.exe` and the `langs/` folder from the [latest release](https://github.com/fvdijke/HAMIOS/releases). No Python required.

Build from source:

```bash
pip install pyinstaller
pyinstaller HAMIOS.spec
# → dist\HAMIOS.exe
# Then copy langs\ next to the EXE
```

---

## 📁 Archivos de datos

| Archivo | Contenido |
|---------|-----------|
| `HAMIOS.ini` | Todos los ajustes de usuario (QTH, tema, idioma, umbrales de alerta, …) |
| `hamios_layouts.json` | Preajustes de diseño de paneles |
| `hamios_tle.json` | Elementos orbitales TLE en caché para seguimiento de satélites |
| `hamios_spy_stations.json` | Base de datos de estaciones espía/números (editable) |
| `langs/*.json` | Paquetes de idioma |

---

## 🔭 Modelo de propagación

```
foF2 = 4.0 + (SFI − 70) × 0.065 + SSN × 0.012
MUF  = foF2 × latitude-factor × day/night-factor × 3.8
LUF  = (3.5 + K × 0.8) × auroral-factor / 10^(SNR/20)
```

**Band quality**: optimum around 55 % of the MUF/LUF window → 100 %.

---

## ⌨️ Interacción con el ratón

| Action | Effect |
|--------|--------|
| Scroll wheel on map | Zoom 1×–8× |
| Click + drag on map | Pan viewport |
| Left-click on map | Great-circle path + path propagation |
| Right-click on map | Reset zoom/pan · clear path |
| Hover on map / bands / chart | Detailed tooltip |
| Click on legend label | Toggle band in history chart |

---

## 💻 Requisitos del sistema

| | Minimum | Recommended |
|-|---------|------------|
| OS | Windows 10 | Windows 11 |
| Screen resolution | 1280 × 900 | 1920 × 1080 or wider |
| Python | 3.10 | 3.12+ |
| Internet | Required (data feeds) | — |

> v4.0.1 utiliza un lienzo de paneles libre. Organiza los paneles libremente en cualquier tamaño de pantalla. Una pantalla ancha (≥ 1920 px) ofrece el espacio de trabajo más cómodo.

---

## 🔧 Ideas futuras

- Stabilise CAT interface (Yaesu/Kenwood/Icom)
- SDR integration
- Logging connection (ADIF/WSJTX)

---

## 📜 Licencia

Gratuito para uso personal y no comercial en radioafición.

---

