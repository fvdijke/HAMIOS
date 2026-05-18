"""
HAMIOS v5 — Opstartcontrole

Controleert bij elke start of alle vereiste bestanden aanwezig zijn.
Ontbrekende data-bestanden worden aangemaakt met standaardwaarden.
Ontbrekende assets (worldmap) worden gemeld als fatale fout.

Gebruik vanuit HAMIOS5.py:
    from hamios5.startup import check_files
    warnings, errors = check_files()
"""

import json
import os

from ._appdir import APP_DIR


# ── Bestandsdefinities ────────────────────────────────────────────────────────

_WORLDMAP  = os.path.join(APP_DIR, "worldmap_eq.jpg")
_CONFIG    = os.path.join(APP_DIR, "hamios_config.json")
_LAYOUTS   = os.path.join(APP_DIR, "hamios_layouts.json")
_SPY       = os.path.join(APP_DIR, "hamios_spy_stations.json")
_HISTORY   = os.path.join(APP_DIR, "HAMIOS_history.csv")
_TLE       = os.path.join(APP_DIR, "hamios_tle.json")
_EIBI_CSV  = os.path.join(APP_DIR, "hamios_eibi.csv")
_EIBI_META = os.path.join(APP_DIR, "hamios_eibi_meta.json")


# ── Standaard SpyStations: importeer de volledige lijst uit spy_dialog ────────
def _get_default_spy() -> list:
    try:
        from .spy_dialog import _DEFAULTS
        return list(_DEFAULTS)
    except Exception:
        return []


def check_files() -> tuple[list[str], list[str]]:
    """
    Controleer en herstel alle bestanden die HAMIOS v5 nodig heeft.

    Geeft (warnings, errors) terug:
      warnings — informatief, app kan doorgaan
      errors   — fataal, app kan NIET starten
    """
    warnings: list[str] = []
    errors:   list[str] = []

    # ── Wereldkaart: waarschuwing (wordt automatisch gedownload door mapview) ───
    if not os.path.exists(_WORLDMAP):
        warnings.append("Wereldkaart ontbreekt — wordt automatisch gedownload.")

    # ── Config: aanmaken als afwezig (defaults worden ingevuld door AppConfig) ─
    if not os.path.exists(_CONFIG):
        try:
            with open(_CONFIG, "w", encoding="utf-8") as f:
                json.dump({}, f)
            warnings.append(f"Nieuwe configuratie aangemaakt: {_CONFIG}")
        except Exception as e:
            errors.append(f"Kan configuratie niet aanmaken: {_CONFIG}\n{e}")

    # ── SpyStations: aanmaken met standaardwaarden ───────────────────────────
    if not os.path.exists(_SPY):
        try:
            spy_data = _get_default_spy()
            with open(_SPY, "w", encoding="utf-8") as f:
                json.dump(spy_data, f, ensure_ascii=False, indent=2)
            warnings.append(
                f"SpyStations aangemaakt met {len(spy_data)} stations: {_SPY}")
        except Exception as e:
            warnings.append(f"Kan SpyStations niet aanmaken: {e}")

    # ── Band-history CSV: aanmaken als leeg bestand ───────────────────────────
    if not os.path.exists(_HISTORY):
        try:
            with open(_HISTORY, "w", encoding="utf-8") as f:
                f.write("timestamp,160m,80m,60m,40m,30m,20m,17m,15m,12m,10m,6m,"
                        "sfi,ssn,k_index,a_index,bz,sw_speed,sw_density,xray\n")
            warnings.append(f"Band-history aangemaakt: {_HISTORY}")
        except Exception as e:
            warnings.append(f"Kan band-history niet aanmaken: {e}")

    # ── Optionele bestanden: informatief melden als afwezig ───────────────────
    if not os.path.exists(_TLE):
        warnings.append(
            "Geen TLE satellietdata — wordt gedownload bij eerste gebruik van Satellite.")
    if not os.path.exists(_EIBI_CSV):
        warnings.append(
            "Geen EIBI-cache — wordt gedownload bij eerste gebruik via EIBI → Lijst bijwerken.")

    return warnings, errors


def app_dir() -> str:
    """Geeft de map terug waar alle HAMIOS-bestanden staan."""
    return APP_DIR


def file_status() -> list[dict]:
    """
    Geeft een lijst van alle HAMIOS-bestanden met hun status.
    Gebruikt in Instellingen → Over voor diagnostiek.
    """
    files = [
        (_WORLDMAP,  "worldmap_eq.jpg",       "Vereist"),
        (_CONFIG,    "hamios_config.json",     "Configuratie"),
        (_LAYOUTS,   "hamios_layouts.json",    "Paneel layouts (legacy)"),
        (_SPY,       "hamios_spy_stations.json","SpyStations"),
        (_HISTORY,   "HAMIOS_history.csv",     "Band history"),
        (_TLE,       "hamios_tle.json",        "Satelliet TLE"),
        (_EIBI_CSV,  "hamios_eibi.csv",        "EIBI cache"),
        (_EIBI_META, "hamios_eibi_meta.json",  "EIBI metadata"),
    ]
    result = []
    for path, name, label in files:
        exists = os.path.exists(path)
        size   = os.path.getsize(path) if exists else 0
        result.append({
            "name":   name,
            "label":  label,
            "path":   path,
            "exists": exists,
            "size_kb": round(size / 1024, 1),
        })
    return result
