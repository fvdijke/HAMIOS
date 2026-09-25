# HAMIOS v5.8 — New HAM Antenna Designer

**Release Date:** September 25, 2026
**Build:** PyInstaller 6.x | Python 3.10

---

## 🎯 Highlights

### 📐 HAM Antenna Designer v3.0.1 (bundled, 📐 button)
A full review of every calculation, and completely new drawings.

- **Correct wire lengths** — the rules of thumb (468/f, 234/f, …) are bare-wire values that already include the
  end effect; insulation is now applied *relative* to bare wire (PVC ≈ 0.97, PTFE ≈ 0.99). Earlier versions cut
  wire antennas 2–5 % too short. Yagi and quad spacings stay free-space values.
- **IARU Region 1 or 2** band plan (Region 1 default), 60 m added; wide listening ranges only for receive antennas
- **SWR** from the complex impedance, as the coax sees it behind the balun/unun (an EFHW behind its 49:1 unun now
  shows 1:1)
- **Matching networks** for real and complex loads (e.g. `36-j20`): every L-network, a Pi and a T, each verified by
  recomputing Zin, with E12 standard values
- **Cable loss** for all 44 cables from datasheet values, plus the extra loss caused by SWR on the line (ARRL)
- **SWR sweep** of the antenna as built, with a realistic bandwidth
- **Radiation patterns** computed from the antenna geometry, at your height over real ground
- Receive antennas (longwire, loop-on-ground, discone) and the balun/unun guide corrected

### 🖊 New antenna drawings
- Radiator, counterpoise/radials, feed line, balun/unun/choke (at the feedpoint), masts and ground point, each in
  its own colour and line style
- All labels beside the drawing — no text over the drawing
- **Night** and **Day** themes, **2D** and **3D**; a light, printable SVG export

### ✨ Other
- New Smith-chart logo for the antenna designer; the designer follows the HAMIOS language as before
- The designer is also available on its own: https://hamios.space/antenna-designer.html

---

## 📦 Files

| File | Description |
|---|---|
| `HAMIOS5.exe` | Standalone Windows executable (no Python required) |
| `README.md` / `README_NL.md` | Documentation (EN/NL) |

---

*Developed with Claude AI (Anthropic) · Frank van Dijke*
