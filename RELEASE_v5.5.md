# HAMIOS v5.5 — HAM Antenna Designer, TLE Caching Fix, Faster Startup & Code Cleanup

**Release Date:** July 2, 2026
**Build:** PyInstaller 6.x | Python 3.10
**Size:** ~115 MB

---

## 🎯 Major Fixes & Improvements

### 0. **New Antenna Tool — HAM Antenna Designer** 📡
The built-in antenna calculator has been **replaced** by the standalone
**HAM Antenna Designer** (bundled inside the EXE, launched via the 📡 Antenna
header button in its own window):

- 20+ documented antenna designs: verticals (¼λ, ½λ, ⅝λ, full wave),
  center-fed dipoles, EDZ, EFHW, full-wave loop, Inverted-V, OCF/Windom,
  J-pole, vertical delta loop, 3-el Yagi, cubical quad, Moxon rectangle,
  plus SWL receive antennas (long-wire, discone, loop-on-ground)
- Every formula is a sourced rule of thumb (ARRL, Cebik/W4RNL, Palomar)
- Element/radial/counterpoise lengths, feedpoint impedance,
  balun/unun/choke advice and plain-language build notes
- Schematic drawing with dimensions + SVG export
- SWR table, Smith chart, frequency sweep with bandwidth estimate,
  azimuth radiation pattern, feedline-loss comparison and matching-network advice
- Bilingual (EN/NL), HAMIOS-style dark/amber theme

### 1. **TLE Caching Fixed** 🛰️
The satellite TLE data was re-downloaded from CelesTrak at **every startup** due to a
path mismatch (the startup check looked for `hamios_tle.json` in the application root,
while the cache lives in `config/hamios_tle.json`).

- **Existing cache is now detected correctly** — no download when data is present
- **Download only happens once**, when no cache exists at all (fresh install)
- **TLE age is now displayed**:
  - Splash screen: e.g. `34 KB · 3 d` next to the TLE file check
  - Satellite window: e.g. `87 satellites loaded from cache · data 3 d old`
- **Manual refresh unchanged** — the ↻ Refresh TLE button in the Satellite window
  still fetches fresh data on demand

### 2. **Faster Startup** ⚡
With the splash screen enabled, the main window was built **twice**: once during the
splash phase and again afterwards. The first instance was discarded but kept running
in the background (duplicate Blitzortung WebSocket connection, timers, calculation
threads).

- Main window from the splash phase is now **reused**
- Startup time roughly **halved**
- No more duplicate background connections and timers

### 3. **EiBi Language Codes Corrected** 📻
The language dictionary contained a duplicate `SW` key ("Swedish" silently overwritten
by "Swahili") while the actual EiBi data uses neither:

- `SWA` → Swahili (19 occurrences in current EiBi data)
- `SWE` → Swedish (4 occurrences)
- Both now translate correctly in tooltips; previously they showed nothing

### 4. **Translation Fix** 🌐
- Missing Dutch entry `sat.cache_loaded` added — the Dutch UI showed the raw
  translation key in the Satellite window status line
- New bilingual entry `sat.tle_age` ("data {age} old" / "data {age} oud")

### 5. **Code Quality Pass** 🧹
Full-codebase inspection with pyflakes; all findings resolved:

- ~120 unused imports removed across all modules (autoflake, reviewed per file)
- ~25 unused local variables and dead computations removed
- Duplicate `set_cfg()` method definition removed (panels5)
- Duplicate `VQ9` DXCC entry removed (layers)
- Dead `_ensure_tle_loaded()` method removed (mainwindow)
- Dead coax-loss interpolation block removed (antenna calculator)
- Missing `QDialog` import added for type annotations (mainwindow)
- Unit test suite repaired (old `hamios5.*` package name → `modules.*`);
  **all 39 tests green**

---

## 📋 Behaviour Notes

- No functional changes other than the fixes listed above
- All user-agent strings unified to `HAMIOS/5.5`
- Verified: full compile, import smoke test, 39 unit tests, live application run

---

## 📦 Files

| File | Description |
|---|---|
| `HAMIOS5.exe` | Standalone Windows executable (no Python required) |
| `README.md` / `README_NL.md` | Updated documentation (EN/NL) |

---

*Developed with Claude AI (Anthropic) · Frank van Dijke*
