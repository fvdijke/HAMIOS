# HAMIOS Roadmap

## Version 5.3+ — Ionosphere & Propagation Enhancements

### Priority 1 — High Impact (v5.4)

#### 1. FOF2 / MUF Hourly Forecast per Zone
- **Impact**: Direct, actionable band prediction
- **Data source**: IRI-2016 model (free, open-source) or NOAA Space Weather Prediction Center
- **UI**: New panel "MUF/LUF Forecast" alongside band schedule
- **Shows**: Predicted Maximum Usable Frequency (MUF) & Lowest Usable Frequency (LUF) per hour
- **Value**: More accurate than current algorithm; zone-specific (not global)
- **Effort**: Medium (model integration + UI panel)

#### 2. Sporadic-E (Es) Seasonal Forecast
- **Impact**: Critical for 6m/4m/2m operators (major subset of amateur radio)
- **Logic**: 
  - Seasonal probability (May–Aug peak, Dec–Feb secondary)
  - Correlation with K-index and local time
  - Temperature-based enhancement (when available)
- **UI**: Overlay on calendar + alert threshold in settings
- **Data**: Empirical from monthly patterns + real-time Kp
- **Effort**: Low (pattern-based, no external API required)
- **Priority reason**: VHF community feedback; high engagement

#### 3. WSPR/JT-Alert Live Integration
- **Impact**: Real-time weak-signal propagation data (much more accurate than DX-spots)
- **Data source**: wsprnet.org API (public, free)
- **UI**: Live table similar to DX-spots; propagation heatmap overlay
- **Shows**: Actual QSO paths working right now (vs. reported spots)
- **Value**: Data-driven propagation + swl/QRP relevance
- **Effort**: Medium (API integration + data streaming)

---

### Priority 2 — Scientific Value (v5.5)

#### 4. TEC (Total Electron Content) Realtime Map
- **Impact**: High-resolution ionosphere electron density heatmap
- **Data source**: NASA/NOAA SWPC (15 min updates, public)
- **UI**: Heatmap overlay on map (similar to night overlay)
- **Shows**: Electron density per lat/lon → predicts HF absorption & path quality
- **Effort**: Medium–High (data parsing + real-time updates)

#### 5. Great Circle Paths (GCP) Multi-Hop Router
- **Impact**: Visual routing tool for DX planning
- **Features**:
  - Click on map → auto-compute GCP to your QTH
  - Show primary + secondary skip zones
  - Mode-dependent frequency ranges (80m vs 10m)
  - Distance/bearing/azimuth annotations
- **UI**: Interactive path drawing on map + info panel
- **Effort**: Medium (spherical math + UI interaction)

#### 6. Geomagnetic Substorm Alerts (Substorm Onset)
- **Impact**: More granular than just K-index; predicts sudden absorption events
- **Data source**: NOAA SWPC Substorm Onset Probability (SSOE)
- **Shows**: 1–6 hour substorm risk; polar region affected
- **UI**: Alert panel + map shading of affected auroral zones
- **Effort**: Low (data integration only)

---

### Priority 3 — Niche/Advanced (v5.6+)

#### 7. Polar Aurora Forecast by Latitude Zone
- **Impact**: EU→CA, EU→Japan path forecasts (already using Kp, but per-zone)
- **Logic**: Kp + observer latitude → absorption prediction
- **UI**: Separate overlay showing "red zones" per 2-hour window
- **Effort**: Low (calculation layer only)

#### 8. QSO Predictor (Statistical)
- **Impact**: "What are my odds on 20m SSB to NA right now?"
- **Inputs**: Your QTH + rig (mode/power/antenna) + current solar data + target distance
- **Output**: Success probability % + confidence interval
- **Data**: Empirical from past WSPR/CQWW contest data (optional ML model)
- **Effort**: High (requires training data or advanced modeling)

#### 9. Sunset/Sunrise Grayline Overlay (Enhanced)
- **Impact**: Already have night overlay; this adds sharp grayline with timing
- **UI**: Animated grayline following sun with time overlay
- **Shows**: Opens when grayline hits your antenna (optimal timing visualization)
- **Effort**: Low (mostly Sun ephemeris already in code)

#### 10. Ionosonde Local Data Integration
- **Impact**: Real measured F2, F1, E-layer heights at nearest digisonde site
- **Data source**: NOAA/JRO/SAO digisonde network (public HTTP)
- **UI**: Real-time graphs in "Solar/Ionosphere" panel
- **Shows**: Measured vs. predicted → can refine forecasts
- **Effort**: Medium–High (site location lookup + parsing)

---

## Implementation Strategy

### v5.3 (Priority 1 Features) ✅ **COMPLETED**
- ✅ Version bump (5.2 → 5.3)
- ✅ MUF/LUF Forecast panel (IRI-2016 model + UI heatmap)
- ✅ Sporadic-E Seasonal alert (K-index + seasonal + diurnal)
- ✅ WSPR Live Feed (wsprnet.org API integration + live table)
- ✅ Internationalization (NL + EN for all 3 features)
- ✅ Unit tests (15 MUF + 10 ES + 8 WSPR tests)
- ✅ Bug fixes (overlay panel modeless, band schedule resizing)
- ✅ Documentation (CHANGES_v5.3.md + inline comments)
- 📋 Manual QA (pending final testing)

### v5.4 (Priority 1 — Q4 2026)
1. **FOF2/MUF Forecast** (2–3 weeks)
2. **Sporadic-E Alert** (1 week)
3. **WSPR Integration** (2–3 weeks)

### v5.5 (Priority 2 — Q1 2027)
1. **TEC Heatmap** (2 weeks)
2. **GCP Router** (3–4 weeks)
3. **Substorm Alerts** (1 week)

### v5.6+ (Nice-to-Have)
- Polar aurora zones
- QSO predictor
- Grayline enhancement
- Digisonde data

---

## Dependencies & Data Sources

| Feature | Source | Cost | License | Notes |
|---------|--------|------|---------|-------|
| FOF2/MUF | IRI-2016 | Free | Open | Local Python library |
| Es Forecast | Empirical | Free | — | No external API |
| WSPR | wsprnet.org | Free | CC-BY | Public API |
| TEC | NOAA SWPC | Free | Public Domain | 15 min updates |
| Substorm | NOAA SWPC | Free | Public Domain | Text-based feed |
| Digisonde | NOAA/JRO | Free | Public | Multiple sites, HTTP JSON |

---

## Success Metrics

- **Adoption**: % of users enabling new features
- **Engagement**: Time spent in new panels
- **Accuracy**: QSO prediction vs. actual logs (if WSPR data available)
- **Feedback**: Community feature requests on new additions
