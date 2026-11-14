# HAMIOS v5.8.4 — Update check and code review

**Release Date:** November 2026
**Build:** PyInstaller 6.x | Python 3.10

---

## 🔔 Update check

The splash screen now checks GitHub for a newer HAMIOS version. When one is available it shows a **HAMIOS version** row with the new version number and an **UPDATE AVAILABLE** badge; click the badge to open the download page. Offline, nothing is shown.

## 🔍 Full code review — 18 fixes

Look and feel are unchanged; only what was wrong has been fixed.

**On screen**
- Kp chart: the "current" value was the oldest reading (~45 h ago); the X-ray chart had the same problem with the flare class. Both now show the newest reading
- Settings: a 6-character locator gave coordinates up to ~70 km off the square centre (affecting distances and paths); invalid locators are now rejected
- Moon position: error from ~1.7° to ~0.1°
- Storm forecast follows the NOAA categories: G3–G5 is one probability, so the G4+ row shows "—" instead of a fake 0 %
- Propagation overview: DX routes now come from the propagation model for your own QTH (previously fixed rules that only held for Europe); Sporadic-E season also for the southern hemisphere
- Advice in AM uses phone frequencies (was an FT8 frequency); FM is only advised on 10m and 6m

**Data and background tasks**
- DX cluster: polling started only via a font-size setting, and every settings change triggered an extra fetch
- Band history is now stored in `config/HAMIOS_history.csv`; the old file next to the program is merged automatically. The Bz column is now filled (was always 0)
- One unexpected NOAA message could skip the rest of the fetch round (D-RAP, aurora, outlook)
- Quickly toggling lightning could open two connections (duplicate strikes)
- A new QTH reaches the WSPR feed immediately; cleaner shutdown of background fetches
- Own-continent filter: West Africa, the Middle East and European Russia are now classified correctly

**CAT**
- **FT-817/857/897**: the binary CAT protocol is now implemented (these radios did not work before); preset set to 2 stop bits
- **Kenwood / Elecraft**: mode command fixed (`MD2;` instead of `MD02;`)
- **Icom**: interfaces that echo commands no longer give a wrong frequency; setting the mode now works
- New radio type **Yaesu FT-991/710/DX10/DX101** (9-digit frequency)

---

Also included: everything from v5.8.3 (propagation overview, tab groups).
