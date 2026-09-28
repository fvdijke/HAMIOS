# HAMIOS v5.8.2 — Faster map, clearer HF absorption

**Release Date:** September 28, 2026
**Build:** PyInstaller 6.x | Python 3.10

---

## ⚡ Much lower CPU use

Measured over a normal session: idle CPU use dropped from **~16 % to ~4 %** of one core.

- Lightning strikes arrive from all over the world every few seconds, so the ring animation practically never stopped — and every frame redrew the whole map, including all fading strike dots.
- The fading dots are now cached (new strikes are added within 2 s; the fade is refreshed every 10 s).
- Only the small areas around the growing rings are redrawn, instead of the whole map.
- The panel behind the map is no longer repainted with every frame.

## 🌐 HF absorption (NOAA D-RAP) status

While the HF absorption overlay is on, a status line in the bottom-left corner of the map shows the time of the NOAA data and the peak absorption:
- quiet sun: *no significant absorption — max 0.2 MHz*
- flare or proton event: *up to 18.0 MHz*

Before, the layer was simply empty on a quiet sun, which looked as if it did not work.

---

Also included: **Themes** (v5.8.1) and **HAM Antenna Designer v3.0.1** (v5.8).
