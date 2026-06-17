## HAMIOS v3.0 — Volledig interface-redesign

### Nieuw in v3.0

**Layout**
- Wereldkaart centraal — vaste hoogte 380 px, zoom/pan intact
- DX Spots als volledige-hoogte rechterkolom (360 px, additioneel — overige panelen houden hun breedte)
- Solar/Ionosfeer links (200 px), HF Betrouwbaarheid rechts (420 px)
- Onderste rij: 3 gelijke panelen — Bandopenings-schema / Bandverloop / Bz 24u grafiek
- Kaartoverlays gegroepeerd in Weergave (Zon/Maan/Graylijn/Aurora) en Data (WSPR/Spots/CS/Locator)
- Alle panelen in dezelfde rij automatisch even hoog

**HF Band Betrouwbaarheid**
- Gradient-balken in band-eigen kleur: licht boven, donker onder, glans-lijn
- Bandnaam vet en in bandkleur (was grijs)
- Balken 22 px hoog (was 13 px)

**Solar paneel**
- Compacter (200 px breed), font 8 pt voor goede leesbaarheid
- PCA/proton-flux en X-flare meldingen vereenvoudigd

**Venstergrootte**
- Standaard 1768 px breed zodat de DX-kolom additioneel is

---

### Meegeleverd

langs_v30.zip: 13 taalbestanden (NL/DE/FR/IT/ES/NO/PL/SV/DA/FI/PT/JA/RU)

Nieuwe taalsleutels in v3.0: map_display_lbl, map_data_lbl

---

### Installatie

1. Download HAMIOS.py of bouw een EXE via pyinstaller HAMIOS.spec
2. Download langs_v30.zip en pak uit naast HAMIOS.py of HAMIOS.exe
3. Vereist: pip install pillow / optioneel: pip install pystray

Zie README.md voor volledige documentatie.

73 de PA3FVD / Developed with Claude AI
