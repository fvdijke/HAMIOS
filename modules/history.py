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
# In config/, net als de overige gegevens (en zoals het opstartscherm controleert)
_FILE      = os.path.join(_HERE, "config", "HAMIOS_history.csv")
_OLD_FILE  = os.path.join(_HERE, "HAMIOS_history.csv")   # t/m v5.8.3
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

# Kolom → sleutel in de solar-dict (Bz heet daar sw_bz)
_SOLAR_KEYS = {"bz": "sw_bz"}

_lock = threading.Lock()


def _migrate_old_file() -> None:
    """Tot en met v5.8.3 stond de historie naast het programma, terwijl het
    opstartscherm een (lege) versie in config/ aanmaakte. Voeg de oude regels
    samen met die in config/ (gesorteerd, zonder dubbelen) en ruim het oude
    bestand op."""
    if not os.path.exists(_OLD_FILE):
        return
    try:
        with _lock:
            rows = {}
            header = None
            for path in (_FILE, _OLD_FILE):
                if not os.path.exists(path):
                    continue
                with open(path, newline="", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    head = next(reader, None)
                    if head != _COLS:
                        continue        # onbekend formaat: niet aanraken
                    header = head
                    for r in reader:
                        if r and r[0]:
                            rows[r[0]] = r
            if header is None:
                return
            os.makedirs(os.path.dirname(_FILE), exist_ok=True)
            tmp = _FILE + ".tmp"
            with open(tmp, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(_COLS)
                for key in sorted(rows):
                    w.writerow(rows[key])
            os.replace(tmp, _FILE)
            os.remove(_OLD_FILE)
    except Exception:
        pass


def load() -> list:
    """Laad CSV; sla regels ouder dan _KEEP_DAYS over.
    Geeft lijst van (datetime, band_dict, solar_dict) terug.
    """
    _migrate_old_file()
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
    _migrate_old_file()
    try:
        with _lock:
            os.makedirs(os.path.dirname(_FILE), exist_ok=True)
            write_header = not os.path.exists(_FILE) or os.path.getsize(_FILE) == 0
            with open(_FILE, "a", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                if write_header:
                    w.writerow(_COLS)
                band_vals  = [band_pct.get(name, 0) for name in _BAND_NAMES]
                solar_vals = [solar.get(_SOLAR_KEYS.get(k, k), 0) for k in _SOLAR_COLS]
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
