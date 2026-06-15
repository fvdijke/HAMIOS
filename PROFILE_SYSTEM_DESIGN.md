# HAMIOS v5.3 - Profiel-bewaarsysteem (volledige refactor)

## Overzicht

Huidge situatie:
- ❌ Alleen panel-layouts worden bewaard (geometrie + zichtbaarheid)
- ❌ Alle instellingen (callsign, mode, antenna, CAT, enz) gaan verloren tussen sessies
- ❌ Geen manier om volledig "workspace" profielen op te slaan

Nieuw systeem:
- ✅ **Volledig profiel** = ALL AppConfig + panel layout + window geometry
- ✅ **Default profiel** (`__default__`) - automatic backup van huidge instellingen
- ✅ **Named profielen** - gebruiker kan meerdere complete workspaces opslaan/laden
- ✅ **Snelle wisseling** - wisselen tussen profielen zonder dialoog

---

## Architectuur

### 1. Opslag: `hamios_profiles.json`

Nieuwe bestand (naast `hamios_config.json`) met volgende structuur:

```json
{
  "__default__": {
    "config": {
      "callsign": "EA1ABC",
      "qth_lat": 52.0,
      "qth_lon": 5.0,
      "mode": "SSB",
      "power": "100W",
      ... alle AppConfig velden ...
    },
    "layout": {
      "__window__": [100, 100, 1400, 900],
      "panel_wspr": [x, y, w, h, visible],
      "panel_muf": [x, y, w, h, visible],
      ... alle panelen ...
    }
  },
  "DX_Expeditie": {
    "config": { ... },
    "layout": { ... }
  },
  "Satellite_Tracking": {
    "config": { ... },
    "layout": { ... }
  }
}
```

### 2. Kernsysteem (profiel_manager.py)

Nieuw module met functies:

```python
class ProfileManager:
    # Laden/opslaan
    load_profiles() -> dict[str, Profile]
    save_profiles(profiles: dict)
    
    # Profiel-operaties
    get_profile(name: str) -> Profile
    create_profile(name: str, config: AppConfig, layout: dict) -> Profile
    save_current_as_profile(name: str, config: AppConfig, layout: dict)
    update_profile(name: str, config: AppConfig, layout: dict)
    delete_profile(name: str)
    
    # Laden toepassen
    apply_profile(profile: Profile) -> tuple[AppConfig, dict]
    
    # Default-profiel
    ensure_default_profile(config: AppConfig, layout: dict)
    get_default_profile() -> Profile
    reset_to_default()

class Profile:
    name: str
    config: dict  # AppConfig als dict
    layout: dict  # Panel layouts + window geometry
    timestamp: str  # wanneer gemaakt/bewerkt
```

### 3. Integratie in bestaande code

#### config.py
- Geen wijzigingen (AppConfig blijft hetzelfde)
- `load_config()` / `save_config()` ongewijzigd

#### settings_dialog.py
- `_tab_layout()` uitbreiden:
  - **"Default profiel opslaan"** → alle huidge instellingen als default
  - **"Huidge instellingen in profiel opslaan"** → nieuwe profiel of overschrijven
  - **Profielenlijst** → laden, overschrijven, verwijderen
  
#### mainwindow.py
- Bij startup: `ProfileManager.ensure_default_profile()`
- `save_layout()` → ook config opslaan (niet alleen layout)
- `load_layout()` → load config + apply settings
- Nieuw: `apply_profile(name)` → snelle wisseling

---

## Workflow

### 1. Initialisatie (startup)

```
1. load_config() → AppConfig
2. ProfileManager.ensure_default_profile()
   - Kopie van huidge config + layout opslaan als backup
3. load_layout() → herstellen vorige sessie
```

### 2. Setting wijzigen (bijv. callsign)

```
1. User wijzigt callsign in settings-dialog
2. "OK" klikken → save_config()
3. **NIEUW**: save_layout() ook config meenemen
```

### 3. Profiel opslaan (default)

```
1. Settings → Layout tab
2. "Default profiel opslaan" klikken
3. ProfileManager.create_profile("__default__", current_config, current_layout)
4. Volgende keer startup herstelt deze default
```

### 4. Profiel opslaan (named)

```
1. Settings → Layout tab
2. User vult naam in: "Satellite Mode" + klikt "Opslaan"
3. ProfileManager.create_profile("Satellite Mode", current_config, current_layout)
4. Profiel verschijnt in lijst
```

### 5. Profiel laden

```
1. User klikt "Laden" op profiel
2. ProfileManager.apply_profile("Satellite Mode")
   - Laadt config → zet alle instellingen toe
   - Laadt layout → zet panel-posities toe
   - Laadt window-geometry
3. Alle settings + layout weerspiegelen onmiddellijk
```

### 6. Profiel overschrijven

```
1. User wijzigt instellingen (mode, antenna, etc)
2. User klikt "Overschrijven" op bestaand profiel
3. ProfileManager.update_profile("Satellite Mode", ...)
4. Profiel bijgewerkt met huidge instellingen
```

---

## Te implementeren bestanden

### Nieuw:
- `hamios5/profiel_manager.py` - Kern profiel-beheer
- `tests/test_profiel_manager.py` - Unit tests

### Aangepast:
- `hamios5/config.py` - Kleine wijzigingen (helper-functies)
- `hamios5/settings_dialog.py` - UI voor profielen uitbreiden
- `hamios5/mainwindow.py` - Profiel-integratie
- `hamios5/i18n.py` - Nieuwe vertaalkabels

---

## UI Layout (settings → Layout tab)

```
┌─────────────────────────────────────────────┐
│ DEFAULT PROFIEL                             │
├─────────────────────────────────────────────┤
│ [Huidge als default opslaan]                │
│ [Naar default herstellen]                   │
│ Opmerking: auto-backup van huidge settings  │
│                                             │
│ BENOEMDE PROFIELEN                          │
├─────────────────────────────────────────────┤
│ Naam: [__________] [Opslaan als profiel]    │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │ Satellite Mode     [Laden][Overschrijv] │ │
│ │ DX Pedition        [Laden][Overschrijv] │ │
│ │ Field Day          [Laden][Overschrijv] │ │
│ │                         [Verwijderen]   │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ Status: [Profiel 'Satellite Mode' geladen]  │
└─────────────────────────────────────────────┘
```

---

## Implementatievolgorde

1. **profiel_manager.py** - Kernlogica
2. **Unit tests** - Laden/opslaan/toepassen
3. **config.py** - Helper-functies
4. **mainwindow.py** - Integratie
5. **settings_dialog.py** - UI updates
6. **i18n.py** - Vertalingen

---

## Vragen voor implementatie

- [ ] Moeten profielen worden versioned? (timestamp, enz)
- [ ] Mag oude `layouts` dict in config.json vervallen?
- [ ] Moet profiel-wisseling window-state herstellen? (maximized, enz)
- [ ] Moet default-profiel auto-sync gaan? (elke sessie bijwerken)

