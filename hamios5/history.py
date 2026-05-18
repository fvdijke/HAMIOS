"""
HAMIOS v5 — Bandverloop geschiedenis (CSV)

Formaat gelijk aan v4: HAMIOS_history.csv
Kolommen: timestamp + bandpercentages (11 HF-banden) + solar-indices

Functies:
  load()    → lijst van (datetime, band_dict, solar_dict)
  append()  → voeg huidig datapunt toe
  prune()   → verwijder records ouder dan _KEEP_DAYS
"""

import csv
import datetime
import os
import threading

from ._appdir import APP_DIR as _HERE
_FILE      = os.path.join(_HERE, "HAMIOS_history.csv")
_KEEP_DAYS = 90

# Bandnamen (alleen HF, zelfde volgorde als v4)
_BAND_NAMES = [
    "160m", "80m", "60m", "40m", "30m",
    "20m",  "17m", "15m", "12m", "10m", "6m",
]

# Solar-kolommen
_SOLAR_COLS = ["sfi", "ssn", "k_index", "a_index",
               "bz", "sw_speed", "sw_density", "xray"]

_COLS = ["timestamp"] + _BAND_NAMES + _SOLAR_COLS

_lock = threading.Lock()


def load() -> list:
    """Laad CSV; sla regels ouder dan _KEEP_DAYS over.
    Geeft lijst van (datetime, band_dict, solar_dict) terug.
    """
    if not os.path.exists(_FILE):
        return []
    cutoff = (datetime.datetime.now(datetime.timezone.utc)
              - datetime.timedelta(days=_KEEP_DAYS))
    rows = []
    try:
        with open(_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    ts = datetime.datetime.fromisoformat(row["timestamp"])
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=datetime.timezone.utc)
                    if ts < cutoff:
                        continue
                    bp  = {name: int(float(row.get(name, 0)))
                           for name in _BAND_NAMES}
                    sol = {}
                    for k in _SOLAR_COLS:
                        try:
                            sol[k] = float(row[k]) if k in row else 0.0
                        except (ValueError, TypeError):
                            sol[k] = 0.0
                    rows.append((ts, bp, sol))
                except (ValueError, KeyError):
                    continue
    except Exception:
        pass
    return rows


def append(band_pct: dict, solar: dict) -> None:
    """Voeg huidig datapunt toe aan de CSV (header als nieuw bestand)."""
    ts = datetime.datetime.now(datetime.timezone.utc)
    write_header = not os.path.exists(_FILE)
    try:
        with _lock:
            with open(_FILE, "a", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                if write_header:
                    w.writerow(_COLS)
                band_vals  = [band_pct.get(name, 0) for name in _BAND_NAMES]
                solar_vals = [solar.get(k, 0)        for k  in _SOLAR_COLS]
                w.writerow([ts.isoformat()] + band_vals + solar_vals)
    except Exception:
        pass


def prune() -> None:
    """Herschrijf CSV zonder regels ouder dan _KEEP_DAYS."""
    rows = load()
    try:
        with _lock:
            with open(_FILE, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(_COLS)
                for ts, bp, sol in rows:
                    band_vals  = [bp.get(name, 0)  for name in _BAND_NAMES]
                    solar_vals = [sol.get(k, 0)     for k    in _SOLAR_COLS]
                    w.writerow([ts.isoformat()] + band_vals + solar_vals)
    except Exception:
        pass


def get_range(hours: float) -> list:
    """Laad alleen de laatste N uur.
    Geeft lijst van (datetime, band_dict, solar_dict), nieuwste laatste.
    """
    all_rows = load()
    cutoff = (datetime.datetime.now(datetime.timezone.utc)
              - datetime.timedelta(hours=hours))
    return [(ts, bp, sol) for ts, bp, sol in all_rows if ts >= cutoff]
