# HAMIOS v5.7 — Measured Propagation, Smart Advice & Tiled Layout

**Release Date:** September 25, 2026
**Build:** PyInstaller 6.x | Python 3.10

---

## 🎯 Highlights

### 1. **One Propagation Model, Calibrated on the Real Ionosphere** 📡
HAMIOS used three different propagation models that contradicted each other and
reality (one afternoon they gave MUF 29 / – / 9.5 MHz while 21 MHz was measured).

- One central engine used by every panel and the advice
- **Measured ionosphere**: the nearest ionosonde (KC2G / GIRO network, updated every
  15 min) calibrates the model; forecasts gradually return to the model further ahead
- Model accuracy across 27 ionosondes worldwide: median measured/model MUF ratio **1.00**
- **Measured HF absorption** (NOAA D-RAP) raises the LUF where a flare or proton event
  absorbs HF
- Day/night from the real sun elevation **at your QTH** (was a fixed UTC hour)
- DX routes computed per great-circle path **from your QTH** (were hard-coded EU routes)
- K-index from NOAA's 1-minute estimated Kp (was a 3-hourly value)

### 2. **Smart Propagation Advice** 🧭
- **Verdict** with evidence: measured MUF, source ionosonde, number of real observations
- **Up to 5 recommendations**: band → mode + frequency → direction → time window
  ("open until 22:00"), based on the model **and what is actually heard now**
  (WSPR, DX cluster, PSKReporter). Reality beats the model: 👂 "observed" paths are
  recommended even when the model is pessimistic (e.g. TEP)
- Bar = effective probability (model + observations), white tick = model alone
- **Events**: NOAA R/S/G scales (radio blackout, radiation storm, geomagnetic storm),
  solar-wind shock, strongly southward Bz, HF absorption, sporadic-E (measured foEs or
  short-skip spots), meteor showers with meteor-scatter tips, tomorrow's forecast
- **Coming hours** timeline (sunrise/sunset grey line, bands opening/closing) and trends
- **Explanations everywhere**: hover a recommendation for why the band is open
  (position vs. the MUF, LUF, control points in daylight/darkness, observations per
  source, time window, your station); "ⓘ How to read this" guide
- Click a recommendation: **great-circle path on the map** (and CAT tuning if connected)

### 3. **Tiled Panel Layout** 🪟
- Panels always fit together — no gaps or overlaps; proportions scale with any window
- Drag a panel (title or tab) onto another: edge = beside it, centre = as tab,
  Ctrl + centre = swap places; drag the dividers to resize
- Three layouts in the Panels menu: **Map centre**, **Operating**, **Analysis**
  (map height calculated for a 2:1 map); compact variants for small screens
- Lock layout option; your existing layout is converted automatically

### 4. **Merged Band Panels** 📶
- **Bands now**: probability per band now + day/night rating + trend (was two panels)
- **Next 24 hours**: rolling heatmap from now + MUF/LUF curve on the same time axis
  (replaces the band schedule and the separate MUF forecast panel)

### 5. **Data Fixes** 🛠
- **WSPR panel showed invented data**: the WSPRnet API is gone (HTTP 404) and the
  panel silently fell back to random spots. Now real spots via **wspr.live** around
  your QTH (→ your region heard elsewhere, ← distant stations heard in your region)
- **Bz 24h panel was empty**: NOAA retired its solar-wind products; now real-time
  solar wind (RTSW) per minute — solar-wind density works again too
- **Aurora on the map** from NOAA OVATION (measured probability) instead of a K-based oval
- **27-day outlook** strip in the storm-forecast panel
- NOAA data is only downloaded when it can have changed (per-source refresh
  interval) and gzip-compressed: after the first round 3 small downloads instead of 11

### 6. **New Panels & Map Layers** 🛰
- **Propagation map** (Overlays): probability that the chosen band carries the path from
  your QTH to every point on Earth — same calibrated model as the advice, including the
  **skip zone** on short paths (also used by the advice now)
- **HF absorption** (Overlays): NOAA D-RAP — where HF is absorbed after a flare or proton event
- **Ionosondes panel**: your measured ionosphere — foF2 → highest NVIS band, MUF(3000) →
  highest DX band, measured vs model, the 12 nearest stations (★ = used for calibration)
- **Satellite Passes panel**: next 24 hours of your tracked satellites (rise, countdown,
  duration, max elevation, direction) and an **alert 5 minutes before a pass**
  (on/off and minimum elevation in Settings → Alerts)
- **Default** layout button: the classic HAMIOS arrangement, next to the three new layouts
- New panels appear automatically as tabs in your existing layout

### 7. **Accuracy Fixes** 🎯
- **Grey line and day/night terminator** were up to ~6° (≈25 min) too far east (no equation
  of time, coarse drawing grid) — now within ~1° of the NOAA solar calculator, including
  refraction; the map and the propagation model use the same sun position
- **Satellite positions** were 340–1000 km off (no J2 perturbation) — now within ~10 km of
  SGP4 over a day; elevation for the QTH-zone ping corrected
- **Aurora** drawn smoothly (no 1° blocks), in the HAMIOS green → yellow → red colours

### 8. **Performance** ⚡
- CPU use during normal operation down from ~120 % to ~25 % of one core: the PSKReporter
  layer is cached as an image, DX-spot geometry is prepared once per data update and the
  animated DX lines are drawn efficiently
- Propagation model 2.5× faster (map, advice and band panels)

### 9. **Fully Bilingual** 🌐
- Every text in English and Dutch — including EIBI (column headings, ~280 language/region/
  country names), FT8/Dig, SpyStations (all 40 stations), CAT messages, Settings and Help
- Panel titles and header now follow the chosen language from the very start
- Help updated for v5.7: tiled layout, propagation model, ionosondes, grey line/sun/moon,
  satellite passes, map layers, data sources

### 10. **Other** ✨
- Checkboxes with an amber tick instead of a filled box; dropdowns show an arrow again
- Tabs fit their space (inactive tabs show only their icon when narrow); close button on
  the active tab
- Overlays and Panels menus close when you click elsewhere
- Moon icon shows the phase and orientation as seen from your QTH; sun and moon tooltips
  (rise/set, grey-line windows, phase)
- New installation: no map overlays and no lightning connection active; all fonts 9 pt
- History charts no longer draw straight lines across periods when HAMIOS was not running
- WSPR and DX tables fit their content; lightning connection test is thread-safe
- Clicking the map now draws the great-circle path from your QTH with the distance
- FT8/digital CAT tuning uses a selectable data mode (USB or PKT-U/DATA-U)
- One storm threshold (your K setting) for advice and alerts — no duplicate alerts
- HAM Antenna Designer follows the HAMIOS language and is fully translated
  (Smith chart, matching networks, cable loss, pattern, SWR sweep); cable-loss
  "efficiency" showed the lost percentage — fixed
- Settings: CelesTrak replaced by SatNOGS/AMSAT, WSPRnet by wspr.live in the resource list

---

## 📋 Behaviour Notes

- Removed panels "Band conditions" and "MUF forecast" (merged); saved layouts adapt
- The "snap grid" setting is no longer shown (tiles always fit together)
- All user-agent strings unified to `HAMIOS/5.7`
- Verified: full compile, 110 unit tests, full application start-up with live data; orbit model checked against SGP4

---

## 📦 Files

| File | Description |
|---|---|
| `HAMIOS5.exe` | Standalone Windows executable (no Python required) |
| `README.md` / `README_NL.md` | Documentation (EN/NL) |

---

*Developed with Claude AI (Anthropic) · Frank van Dijke*
