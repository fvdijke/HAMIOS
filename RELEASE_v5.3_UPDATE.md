# HAMIOS v5.3 - Bugfix Update

## Improvements in this update

### Lightning Panel Enhancements
- **Separate controls**: Lightning enable/disable now controls only WebSocket connection
- **Independent overlay visibility**: Toggle overlay on/off from Overlays menu without affecting connection
- **Configurable font size**: Adjust lightning radius label font size (5-72pt) in Settings

### WSPR Live Feed
- **Fixed sorting**: Numeric columns (frequency, SNR, distance, azimuth, time) now sort correctly
- Previously sorted alphabetically, causing incorrect ordering

### Settings & Profiles
- **Fixed profile loading**: Config now properly updates when loading profiles
- **Enhanced profile system**: Support for lightning_overlay_visible setting

## Technical Details

All changes are backward compatible with existing profiles and settings.

**Files modified:**
- hamios5/config.py - Added lightning_font_size and lightning_overlay_visible
- hamios5/layers.py - Implement font size control for all lightning layers
- hamios5/mainwindow.py - Wire up new settings to map view
- hamios5/mapview.py - Add font size control methods
- hamios5/panels5.py - Fix WSPR numeric sorting
- hamios5/settings_dialog.py - Add lightning font UI control
- hamios5/i18n.py - Add translations for new settings

**Build:** PyInstaller 6.x
**Python:** 3.10
**Size:** ~101 MB

---
**Release Date:** 2026-06-15
**Version:** 5.3 (Updated)
