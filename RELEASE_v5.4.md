# HAMIOS v5.4 — Resources Manager & Lightning Improvements

**Release Date:** June 15, 2026  
**Build:** PyInstaller 6.x | Python 3.10  
**Size:** ~101 MB

---

## 🎯 Major Features

### 1. **Resources Manager Tab** 🌐
Centralized management of all online resources used by HAMIOS.
- **9 resource categories**: Solar & Ionosphere, Satellites, WSPR, DX Spotting, Lightning, Broadcast Schedules, Map Data
- **Per-resource controls**:
  - Editable URL field
  - **Test button** → immediate connectivity check with HTTP status
  - **Investigate button** → guidelines for finding mirror servers & backup APIs
- **Auto-save** on URL changes (no restart needed)
- **Reset to defaults** button for quick recovery
- **Bilingual interface** (English/Dutch)

**Use Cases:**
- Service failover (main API down → use mirror server)
- Privacy (use alternative endpoints)
- Debugging (replace slow services with test servers)
- Maintenance (quickly update changed API endpoints)

### 2. **Lightning Panel Improvements** ⚡
Complete separation of concerns:
- **Enable/Disable Lightning** (Settings) → Controls **WebSocket connection** to Blitzortung
- **Show/Hide Overlay** (Overlays menu) → Controls **map display visibility** only
- **Both independent**: Can have connection active without displaying overlay

### 3. **Configurable Lightning Label Font Size** 📝
- New setting in Settings → Lightning → "Lightning labels"
- Range: 5–72 pt
- Applies to radius circle labels (alert & beep radius)
- Saves automatically to profile

### 4. **WSPR Numeric Sorting Fixes** 🛰️
Implemented custom NumericTableItem class:
- **Frequency, SNR, Distance, Azimuth, Time** columns now sort numerically
- Previously sorted alphabetically (800 after 1000)
- Now sorts correctly (800 before 1000)

### 5. **Profile Loading Improvements** 💾
- Fixed AppConfig update when loading profiles
- Proper _save_cfg() implementation
- Lightning overlay visibility now part of profiles

---

## 📋 Complete Changelog

### New Files
- `hamios5/resources_config.py` — Central resource URL management
- `hamios5/resources_tab.py` — Resources Manager UI with test/investigate features

### Modified Files
- `hamios5/config.py` — Added `lightning_font_size` and `lightning_overlay_visible` fields
- `hamios5/mainwindow.py` — Wire up new lightning controls, initialize Resources Manager
- `hamios5/settings_dialog.py` — Add Resources tab, fix profile loading
- `hamios5/layers.py` — Implement font size control for all lightning layers
- `hamios5/mapview.py` — Add `set_lightning_font_size()` method
- `hamios5/panels5.py` — Implement NumericTableItem for proper WSPR sorting
- `hamios5/i18n.py` — Add all Resources Manager translations (NL/EN)
- `hamios5/help_dialog.py` — Add comprehensive Resources Manager documentation (NL/EN)
- `README.md` — Updated with v5.4 features and changelog
- `README_NL.md` — Dutch version updated
- `HAMIOS5.py` — Version strings updated to 5.4
- `HAMIOS5.spec` — Version comment updated to 5.4

### Bugfixes
- ✅ WSPR numeric sorting (800 < 1000 now correct)
- ✅ Profile loading (config properly updated)
- ✅ Lightning panel controls (separate enable/visibility)

---

## 🌐 Resources Monitored (9 Categories)

### Solar & Ionosphere
- **NOAA SWPC**: Solar wind, magnetic field, Kp index, X-ray, storm forecast
- **HamQSL**: Solar flux index and parameters

### Satellites
- **CelesTrak**: TLE data for amateur, ISS, weather, cubesat satellites

### Weak Signal Propagation
- **WSPRnet**: Website connectivity check (API endpoint)

### DX Spotting
- **DXWatch**: Real-time DX cluster spots
- **PSK Reporter**: Digital mode propagation reports

### Lightning
- **Blitzortung**: Real-time worldwide lightning detection

### Broadcast Schedules
- **EIBI Space**: Shortwave broadcast schedules

### Map Data
- **Wikimedia**: NASA Blue Marble world map

---

## 🧪 Testing
- ✅ All 9 resources tested and verified working
- ✅ NumericTableItem sorting validated (800 < 1000)
- ✅ Lightning controls independent (enable ≠ visibility)
- ✅ Profile loading with new fields working
- ✅ Bilingual Help complete (NL/EN)
- ✅ All files compile without errors
- ✅ No breaking changes to existing profiles/config

---

## 📦 Installation

Download **HAMIOS5.exe** from the release and run. No installation needed.

**System Requirements:**
- Windows 10/11 (64-bit)
- ~150 MB disk space
- Stable internet connection (for resource monitoring)

---

## 🔗 Related Documentation

- **Help** → Resources Manager section (fully bilingual)
- **Settings** → 🌐 Resources tab
- **README.md** → Changelog & feature table

---

## 🙏 Thanks

- **Claude AI (Anthropic)** — Development assistance
- **Data Sources**: NOAA SWPC, CelesTrak, Blitzortung, DXWatch, PSK Reporter, EIBI Space, Wikimedia
- **Amateur Radio Community** — Feedback and use cases

---

**v5.4** is a feature-complete release focused on:
- Service resilience (failover via Resources Manager)
- User control (independent lightning settings)
- Data accuracy (numeric sorting in WSPR)
- Documentation (bilingual help for all features)

Enjoy! 📡

---

*HAMIOS v5.4 · Developed with Claude AI · PySide6 · Python 3.10+*
