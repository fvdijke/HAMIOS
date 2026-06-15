# HAMIOS v5.3 - External Resources Inventory

## All External Services & APIs Used

### 1. SOLAR & IONOSPHERE DATA

#### NOAA SWPC (Space Weather Prediction Center)
- **Solar Wind Speed:** `https://services.swpc.noaa.gov/products/summary/solar-wind-speed.json`
- **Solar Wind Magnetic Field:** `https://services.swpc.noaa.gov/products/summary/solar-wind-mag-field.json`
- **Bz 24h Data:** `https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json`
- **Plasma 1-Day Data:** `https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json`
- **Kp Index:** `https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json`
- **X-Ray Data:** `https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json`
- **Storm Forecast (Text):** `https://services.swpc.noaa.gov/text/3-day-geomag-forecast.txt`
- **Alerts:** `https://services.swpc.noaa.gov/products/alerts.json`
- **Purpose:** Solar activity monitoring, propagation forecasting, K-index, X-ray flux
- **Update Frequency:** Every 5 minutes (configurable)
- **Format:** JSON (XML for alerts)

#### HamQSL
- **Solar Data XML:** `https://www.hamqsl.com/solarxml.php`
- **Purpose:** Solar flux index and other solar parameters
- **Format:** XML
- **Used In:** Solar panel display

---

### 2. SATELLITE DATA

#### CelesTrak (Dr. T.S. Kelso)
- **Amateur Satellites:** `https://celestrak.org/NORAD/elements/gp.php?GROUP=amateur&FORMAT=tle`
- **ISS (ZARYA):** `https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=tle`
- **Weather Satellites:** `https://celestrak.org/NORAD/elements/gp.php?GROUP=weather&FORMAT=tle`
- **CubeSats:** `https://celestrak.org/NORAD/elements/gp.php?GROUP=cubesat&FORMAT=tle`
- **Purpose:** TLE (Two-Line Element) orbital data for satellite tracking
- **Format:** TLE (Two-Line Element)
- **Used In:** Satellite layer, orbit predictions, passes
- **Update Frequency:** On-demand (user-triggered download)

---

### 3. WEAK SIGNAL & PROPAGATION

#### WSPRnet
- **WSPR API v2:** `https://wsprnet.org/drupal/wsprnet/api/v2/spots`
- **Purpose:** Real-time weak-signal propagation QSO records
- **Format:** JSON
- **Data:** Call signs, grid locators, bands, SNR, distance, azimuth
- **Update Frequency:** Every 30 seconds
- **Used In:** WSPR Live Feed panel (v5.3 new feature)

---

### 4. DX CLUSTER & SPOTTING

#### DXWatch
- **DX Spots API:** `https://dxwatch.com/dxsd1/s.php?s=0&r=100&cdxc=0`
- **Purpose:** Real-time DX cluster spots
- **Format:** JSON (custom format)
- **Data:** Frequency, DX call, spotter, comment, UTC timestamp
- **Update Frequency:** Every 5 minutes (configurable)
- **Used In:** Live DX Spots panel

#### PSK Reporter
- **QSO Query API:** `https://pskreporter.info/cgi-bin/pskquery5.pl?encap=0&callback=_&statistics=0&noactive=1&nolocator=1&lastseenminutes=15&rronly=1&flowstart=0&appcontact=HAMIOS5`
- **Purpose:** Digital mode propagation data
- **Format:** JSONP
- **Used In:** Propagation monitoring (historical)

---

### 5. LIGHTNING DETECTION

#### Blitzortung.org
- **WebSocket Server:** `wss://ws1.blitzortung.org:443/`
- **Purpose:** Real-time worldwide lightning detection
- **Protocol:** WebSocket (binary frames with strike data)
- **Data:** Strike location (lat/lon), altitude, multiplicity
- **Update Frequency:** Real-time (as strikes occur)
- **Used In:** Lightning panel
- **Note:** Requires active internet connection, real-time updates
- **Fallback:** Graceful degradation if unavailable

---

### 6. BROADCAST SCHEDULES

#### EiBi Space (Eike Bierwirth)
- **Shortwave Schedule (CSV):** `http://www.eibispace.de/dx/sked-{season}{year}.csv`
  - Example: `http://www.eibispace.de/dx/sked-a26.csv` (April-September 2026)
  - Pattern: sked-[a|b][YY].csv (a=Apr-Sep, b=Oct-Mar)
- **Purpose:** EIBI shortwave broadcast schedule database
- **Format:** CSV
- **Used In:** EIBI dialog (broadcast schedule lookup)
- **Update Frequency:** Seasonal (twice yearly)

---

### 7. MAP DATA

#### Wikimedia Commons (NASA Blue Marble)
- **Standard Resolution (1920px):** `https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Whole_world_-_land_and_oceans_12000.jpg/1920px-Whole_world_-_land_and_oceans_12000.jpg`
- **High Resolution (3840px):** `https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Whole_world_-_land_and_oceans_12000.jpg/3840px-Whole_world_-_land_and_oceans_12000.jpg`
- **Purpose:** World map background (public domain NASA imagery)
- **Format:** JPEG
- **File Size:** ~300KB (std), ~1MB (hires)
- **Used In:** Map view background
- **License:** Public Domain (NASA)
- **Download:** Automatic if missing, user can download high-res variant

---

### 8. ONLINE RESOURCE CHECK (NEW in v5.3)

Currently monitored resources on splash screen:
- **wsprnet.org** - WSPR data availability
- **noaa.gov** - Solar/geomagnetic data availability  
- **celestrak.org** - TLE data availability

---

## Resource Status & Monitoring

### Splash Screen Check
- **New feature:** Online resources section with amber divider line
- **Monitored resources:** wsprnet.org, noaa.gov, celestrak.org
- **Status display:** HTTP response code or error message
- **Behavior:** Non-blocking (warnings don't prevent startup)
- **Timeout:** 5 seconds per resource

### Network Requirements
- **Critical:** NOAA SWPC (propagation data), CelesTrak (TLE data)
- **Important:** WSPRnet, DXWatch, Blitzortung
- **Optional:** PSK Reporter, EIBI (can be cached)

---

## Data Flow Summary

```
┌─────────────────────────────────────────────────────────┐
│                    HAMIOS v5.3                          │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
│  Solar/Ionosphere│ │  Satellites  │ │ Spotting     │
├──────────────────┤ ├──────────────┤ ├──────────────┤
│ NOAA SWPC        │ │ CelesTrak    │ │ WSPRnet      │
│ HamQSL           │ │ (TLE Data)   │ │ DXWatch      │
│ Kp/Bz/Xray/etc   │ │              │ │ PSK Reporter │
└──────────────────┘ └──────────────┘ └──────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
│   Broadcast      │ │   Lightning  │ │   Map        │
├──────────────────┤ ├──────────────┤ ├──────────────┤
│ EIBI Space       │ │ Blitzortung  │ │ Wikimedia    │
│ (Shortwave)      │ │ (WebSocket)  │ │ (NASA)       │
└──────────────────┘ └──────────────┘ └──────────────┘
```

---

## Fallback Mechanisms

| Service | Critical? | Fallback | Behavior |
|---------|-----------|----------|----------|
| NOAA SWPC | Yes | Cached data | 5min old data shown if available |
| CelesTrak | Yes | Cached TLE | Last downloaded TLE set used |
| WSPRnet | No | Mock data | Test data shown, no live feeds |
| Blitzortung | No | Offline | Lightning panel empty |
| DXWatch | No | Offline | DX Spots panel empty |
| EIBI | No | Offline | Download disabled until available |
| Map | No | Offline | Black background shown |

---

## Summary Statistics

- **Total External Services:** 8 major service providers
- **API Endpoints:** 15+ JSON/XML endpoints
- **WebSocket Connections:** 1 (Blitzortung)
- **File Downloads:** 4 primary sources (Map, TLE, EIBI, Wikimedia)
- **Critical Dependencies:** 2 (NOAA SWPC, CelesTrak)
- **Network-Required Features:** 6 panels
- **Cacheable Data:** All current downloads

---

**Version:** 5.3
**Last Updated:** 2026-06-15
**Status:** All resources documented and monitored
