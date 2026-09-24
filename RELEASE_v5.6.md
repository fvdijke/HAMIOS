# HAMIOS v5.6 — Reliable Satellite Data, Faster Map & Mouse-over Info

**Release Date:** September 24, 2026
**Build:** PyInstaller 6.x | Python 3.10

---

## 🎯 Major Fixes & Improvements

### 1. **New TLE Sources — No More Blocked Downloads** 🛰️
Satellite TLE data could no longer be refreshed: CelesTrak blocks IP addresses that
download too often, after which every request times out.

- TLE data now comes from **SatNOGS DB** (ISS, weather satellites, all other active
  satellites — one request) and **AMSAT** (active amateur satellites, familiar names
  such as AO-91, SO-50, RS-44 — one request)
- CelesTrak is only used as a last-resort fallback (no cache and both sources down)
- **Built-in block protection**:
  - at most one download per source per 6 hours — the ↻ button cannot bypass this
    and simply reports when the next update is possible
  - every attempt is recorded *before* the request, so rapid clicking, multiple
    windows or a crash never cause extra requests; only one refresh runs at a time
  - growing back-off after a failure; at least 24 hours after HTTP 403/429 or a
    time-out; the server's `Retry-After` is respected
- **No more data loss on partial failures** — a group that cannot be refreshed keeps
  its previous data (previously a single successful group overwrote the whole cache)
- **Your satellite selection is preserved** when a satellite has a different name in
  the new source (matched by NORAD number or normalised name, e.g.
  `METEOR-M2 2` → `METEOR M2-2`), including path and footprint settings
- The status line shows which source succeeded or failed and when a retry is possible
- The map updates immediately after a refresh
- Still no automatic downloads — only via ↻ Refresh TLE in the Satellite window
- **Outdated-data warning**: when TLE data is older than 14 days, HAMIOS warns
  (without downloading) in the splash screen, once in the Alerts panel when
  satellites are selected, and in the Satellite window status line

### 2. **Faster Map Rendering** ⚡
- Night overlay and grayline are baked into the base map (every 30 s) instead of
  three full-map blends per frame
- Static layers (base map, graticule, Maidenhead, DXCC labels, satellites, lightning
  radius) are cached; the 20 fps DX-spot and lightning animations no longer redraw them
- Satellite orbits drawn as single polylines instead of ~1500 line segments each
- Animations pause while the window is minimised or the layer is hidden
- Measured: **~45 ms → ~20 ms per frame** with satellites, DX spots and labels active

### 3. **Faster Startup** 🚀
- The recoloured world map is cached (`config/worldmap_colored.png`) and refreshed
  automatically when the map file changes — map load **~0.7 s → ~0.15 s**
- No more freeze of up to ~6 s after pressing **Continue** on the splash screen;
  background checks finish without blocking the UI
- Startup internet check uses lightweight connectivity endpoints with fallbacks

### 4. **Mouse-over Information on the Map** 🖱️
- **DXCC callsign prefixes** appear when hovering over a country dot (previously
  click); clicking now places the great-circle marker as elsewhere on the map
- **Maidenhead squares**: hovering over a field shows its 100 squares (00–99) with
  the square under the cursor highlighted, plus a label with the full 6-character
  locator (e.g. **JO22**ph); square codes appear once zoomed in far enough to be legible

### 5. **FT8 / Digital Modes Panel** 📻
- Frequencies shown in **MHz** (e.g. `14,0740`)
- Frequency column now sorts **numerically** (previously as text, placing 14 MHz
  before 3.5 MHz); the band column sorts by frequency (2200m … 23cm)
- Search accepts kHz and MHz (`14074`, `14.074`, `14,074`)

### 6. **Stability** 🧱
- Satellite position/path calculations no longer touch the map from a worker thread
  (possible sporadic crash)
- Map recolouring now uses thread-safe `QImage` instead of `QPixmap`

---

## 📋 Behaviour Notes

- New runtime file `config/hamios_tle_meta.json` stores per-source rate-limit state
- The Satellite window category "CubeSat" now contains all other active satellites
  from SatNOGS (~1300)
- All user-agent strings unified to `HAMIOS/5.6`
- Verified: full compile, unit tests, offline rate-limiter tests, offscreen UI tests,
  live TLE refresh, full application start-up

---

## 📦 Files

| File | Description |
|---|---|
| `HAMIOS5.exe` | Standalone Windows executable (no Python required) |
| `README.md` / `README_NL.md` | Updated documentation (EN/NL) |

---

*Developed with Claude AI (Anthropic) · Frank van Dijke*
