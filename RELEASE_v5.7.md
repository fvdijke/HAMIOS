# HAMIOS v5.7 — Measured Propagation, Smart Advice & Tiled Layout

**Release Date:** September 24, 2026
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

### 6. **Other** ✨
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
- Verified: full compile, 98 unit tests, full application start-up with live data

---

## 📦 Files

| File | Description |
|---|---|
| `HAMIOS5.exe` | Standalone Windows executable (no Python required) |
| `README.md` / `README_NL.md` | Documentation (EN/NL) |

---

*Developed with Claude AI (Anthropic) · Frank van Dijke*
