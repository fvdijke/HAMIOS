# HAMIOS v5.9.1 — Lighter, faster, fully documented

**Release Date:** November 2026
**Build:** PyInstaller 6.x | Python 3.10

---

## ⚡ Much lighter and faster

Measured on the same PC, with live data:

| | v5.9 | v5.9.1 |
|---|---|---|
| CPU while idle | ~33 % of one core | **~3 %** |
| Start-up | ~10 s | **~4 s** |
| Applying a setting | ~4.6 s | **~0.1 s** |
| Opening the EIBI window | 2–5 s | **< 1 s** |
| Panning the map | ~18 fps | **~22 fps** |

- Tables (satellite passes, Doppler, DX, WSPR, …) are filled in one go and only changed cells are updated — this was most of the idle CPU
- The time zone of your QTH is loaded once in the background and remembered
- The propagation map is only recalculated when band, QTH or station margin changes
- Hidden tabs no longer rebuild their content in the background
- Map: labels and satellite icons are cached; faster scaling while panning and zooming (the final image is unchanged)

Nothing changes in how HAMIOS looks.

## 📖 Help fully updated

- **Panels and layout**: resizing, splitting a spot by dropping on an edge, making tab groups, moving tabs out of a group, swapping with Ctrl, closing and restoring panels, locking, ready-made layouts
- All v5.9 features: My signal, Path forecast, Watchlist, Azimuthal map and rotator, Model vs reality, Doppler, DXCC database
- Start screen and update check, storm forecast and 27-day outlook, Kp/Bz/X-ray charts, propagation overview
- CAT: all radio types including Hamlib rigctld and flrig, data mode, rotator
- HAM Antenna Designer, settings overview, files and data sources brought up to date

## 🐞 Fixes

- **No more HTTP 429 from Wikimedia and PSK Reporter** on the start screen: HAMIOS now identifies itself with a contact address (required by Wikimedia's User-Agent policy), and the start-up check uses a light request — the PSKReporter homepage instead of a real query (which counted against its once-per-5-minutes limit and could block the real fetch right after), and only the headers of the Wikimedia map instead of downloading it every start
- EIBI: the header line of the schedule file ("kHz:75") is no longer listed as a station

---

Also included: everything from v5.9.
