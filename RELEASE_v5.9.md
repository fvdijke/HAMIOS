# HAMIOS v5.9 — Where am I heard, when can I work it?

**Release Date:** November 2026
**Build:** PyInstaller 6.x | Python 3.10

---

Six new panels (Panels menu; added as tabs to every layout, so your layout does not shift), more radios via Hamlib/flrig, a rotator, and a more realistic propagation model on long paths.

## 📶 My signal
Where your own callsign was heard in the last hour, from **PSKReporter** and **WSPR**: per band the number of receivers, the farthest distance and the best SNR, plus every report. Click a report to see the path on the map. Needs your callsign in Settings → Station.

## 🎯 Path forecast
"When can I work VK?" — the chance per band for the next 24 hours on the path to any place, plus the best windows. The target follows a click on the map, a recommendation or a report in My signal; or type a locator (JO21DN) or a callsign.

## 🔔 Watchlist
Wanted callsigns, prefixes or countries (e.g. `3Y0J`, `VK9`, `Bouvet`). When one is spotted in the DX cluster you get an alert, a Windows notification and a sound — by default only when the band is open on that path. Click: path on the map; double-click: tune via CAT.

## 🧭 Azimuthal map
A great-circle map centred on your QTH: the direction on the map is your antenna heading. Distance rings, bearings and DX spots; hover for bearing and distance, click for the path and its forecast. With a rotator configured the antenna turns along.

## ✅ Model vs reality
How often does the propagation model agree with what is actually heard? Per band: real WSPR/PSKReporter paths, the share the model rated open, and the hours it predicted "open" while the band stayed silent. Kept for 30 days.

## 📡 Doppler
For the satellites you track: their transmitters from the SatNOGS database with the Doppler-corrected downlink and uplink right now. **Tune** sets the downlink on your radio via CAT; **Follow** keeps it tuned during the pass.

## 📻 CAT and rotator
- New radio types **Hamlib rigctld** and **flrig**: CAT for practically every radio. Enter the address in the port field (e.g. `127.0.0.1:4532`)
- **Rotator** (Settings → CAT): Yaesu GS-232 (COM port) or Hamlib rotctld

## 🌍 Better data
- **Full DXCC database (cty.dat)**, updated monthly: DX spots of every prefix land on the map, the own-continent filter and the watchlist use it
- **Propagation model**: on long paths the D-layer absorption near both ends now counts. Low bands to the other side of the world are no longer rated open while it is daytime at either end (e.g. 80m to VK: opens around VK sunrise, closed at European noon). This also improves the advice and the propagation map

## 🧹 Maintenance
- The update badge now also appears in the header (checked every 12 hours) and in Settings → About
- Unused Sporadic-E module removed

---

Also included: everything from v5.8.4 (update check, code review with 18 fixes).
