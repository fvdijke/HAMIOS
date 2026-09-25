"""HAMIOS v5 — TLE-bronnen met blokkadebescherming.

Bronnen (in volgorde van voorkeur):
  SatNOGS DB  — één request, ~1500 actieve satellieten → ISS, Weather, CubeSat
  AMSAT       — één request, actieve amateursatellieten (bekende namen) → Amateur
  CelesTrak   — alleen noodreserve als SatNOGS én AMSAT niets opleveren

Blokkadebescherming (CelesTrak blokkeert IP's die te vaak downloaden):
  - per bron een minimale interval tussen requests (ook bij handmatig vernieuwen)
  - een poging wordt vastgelegd VÓÓR het request: snel herhaald klikken,
    meerdere vensters of een crash leveren nooit extra requests op
  - na een mislukking exponentiële back-off; bij HTTP 403/429 of een
    time-out (typisch voor een firewall-blokkade) minimaal 24 uur
  - Retry-After van de server wordt gerespecteerd
  - nooit twee refreshes tegelijk (globale lock)

Cacheformaat blijft {groep: [[naam, line1, line2], ...]} zodat kaart, dialoog
en hoofdvenster ongewijzigd werken. Mislukte groepen behouden hun oude data.
"""

import datetime
import gzip
import json
import os
import re
import socket
import threading
import time
import urllib.error
import urllib.request

from ._appdir import APP_DIR

_META_FILE = os.path.join(APP_DIR, "config", "hamios_tle_meta.json")
_UA = "HAMIOS/5.7 (+https://hamios.space; amateur radio propagation monitor)"

SATNOGS_URL = "https://db.satnogs.org/api/tle/?format=json"
AMSAT_URL   = "https://www.amsat.org/tle/current/nasabare.txt"
CELESTRAK_GROUPS = {
    "Amateur": "https://celestrak.org/NORAD/elements/gp.php?GROUP=amateur&FORMAT=tle",
    "ISS":     "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=tle",
    "Weather": "https://celestrak.org/NORAD/elements/gp.php?GROUP=weather&FORMAT=tle",
    "CubeSat": "https://celestrak.org/NORAD/elements/gp.php?GROUP=cubesat&FORMAT=tle",
}

SOURCE_NAMES = {"satnogs": "SatNOGS", "amsat": "AMSAT", "celestrak": "CelesTrak"}

_H = 3600
_POLICY = {
    #             min. interval   eerste back-off   max. back-off
    "satnogs":   (6 * _H,         1 * _H,           24 * _H),
    "amsat":     (6 * _H,         1 * _H,           24 * _H),
    "celestrak": (24 * _H,        24 * _H,          7 * 24 * _H),
}
_HARD_BLOCK_WAIT = 24 * _H      # 403/429/time-out
_MAX_WAIT        = 30 * 24 * _H # bovengrens (ook voor Retry-After)
_MAX_TLE_AGE_DAYS = 30          # oudere SatNOGS-TLE's = satelliet niet meer actief
_ISS_NORAD = 25544

# TLE-data ouder dan dit → waarschuwing tonen (nooit automatisch downloaden)
STALE_DAYS = 14
_WEATHER_RE = re.compile(
    r"^(NOAA[ -]?\d+|METEOR[ -]?M|METOP|FENGYUN|FY-?\d|GOES|ELEKTRO|ARKTIKA)", re.I)

_refresh_lock = threading.Lock()
_meta_lock    = threading.Lock()


# ── Rate-limiter (persistent) ─────────────────────────────────────────────────

def _load_meta() -> dict:
    try:
        with open(_META_FILE, encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_meta(meta: dict):
    try:
        os.makedirs(os.path.dirname(_META_FILE), exist_ok=True)
        tmp = _META_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=1)
        os.replace(tmp, _META_FILE)
    except OSError:
        pass


def seconds_until_allowed(source: str, now: float | None = None) -> float:
    """0 als de bron nu benaderd mag worden, anders resterende wachttijd."""
    now = time.time() if now is None else now
    with _meta_lock:
        st = _load_meta().get(source, {})
    nxt = float(st.get("next_allowed", 0))
    # Klok teruggezet of corrupte waarde? Nooit langer dan 30 dagen wachten
    nxt = min(nxt, now + _MAX_WAIT)
    return max(0.0, nxt - now)


def _record_attempt(source: str):
    """Vastleggen vóór het request — ook een crash telt als poging."""
    now = time.time()
    with _meta_lock:
        meta = _load_meta()
        st = meta.setdefault(source, {})
        st["last_attempt"] = now
        st["next_allowed"] = now + _POLICY[source][0]
        _save_meta(meta)


def _record_result(source: str, ok: bool, hard: bool = False,
                   retry_after: float = 0.0, error: str = ""):
    now = time.time()
    min_iv, backoff, max_backoff = _POLICY[source]
    with _meta_lock:
        meta = _load_meta()
        st = meta.setdefault(source, {})
        if ok:
            st["fails"] = 0
            st["last_ok"] = now
            st["last_error"] = ""
            wait = min_iv
        else:
            fails = int(st.get("fails", 0)) + 1
            st["fails"] = fails
            st["last_error"] = error[:200]
            wait = min(backoff * 2 ** (fails - 1), max_backoff)
            if hard:
                wait = max(wait, _HARD_BLOCK_WAIT)
        wait = min(max(wait, retry_after), _MAX_WAIT)
        st["next_allowed"] = now + wait
        _save_meta(meta)


# ── HTTP ──────────────────────────────────────────────────────────────────────

class _FetchError(Exception):
    def __init__(self, msg: str, hard: bool = False, retry_after: float = 0.0):
        super().__init__(msg)
        self.hard = hard
        self.retry_after = retry_after


def _http_get(url: str, timeout: float) -> bytes:
    req = urllib.request.Request(url, headers={
        "User-Agent": _UA, "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            if r.headers.get("Content-Encoding", "").lower() == "gzip":
                body = gzip.decompress(body)
            return body
    except urllib.error.HTTPError as e:
        retry = 0.0
        try:
            retry = float(e.headers.get("Retry-After", 0) or 0)
        except (TypeError, ValueError):
            pass
        raise _FetchError(f"HTTP {e.code}", hard=e.code in (403, 429),
                          retry_after=retry) from None
    except (socket.timeout, TimeoutError) as e:
        raise _FetchError("time-out", hard=True) from e
    except urllib.error.URLError as e:
        hard = isinstance(e.reason, (socket.timeout, TimeoutError))
        raise _FetchError(str(e.reason)[:80], hard=hard) from None
    except OSError as e:
        raise _FetchError(str(e)[:80]) from None


# ── Parsers ───────────────────────────────────────────────────────────────────

def norad_of(line1: str) -> int | None:
    try:
        return int(line1[2:7])
    except (ValueError, IndexError):
        return None


def _valid_tle(l1: str, l2: str) -> bool:
    return (l1.startswith("1 ") and l2.startswith("2 ")
            and len(l1) >= 68 and len(l2) >= 68
            and l1[2:7] == l2[2:7])


def parse_tle_text(text: str) -> list[tuple[str, str, str]]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    sats, i = [], 0
    while i + 2 < len(lines):
        name, l1, l2 = lines[i], lines[i + 1], lines[i + 2]
        if _valid_tle(l1, l2):
            sats.append((name, l1, l2))
            i += 3
        else:
            i += 1
    return sats


def _tle_age_days(line1: str) -> float:
    try:
        ep = line1[18:32].strip()
        yy = int(ep[:2])
        year = 2000 + yy if yy < 57 else 1900 + yy
        epoch = (datetime.datetime(year, 1, 1, tzinfo=datetime.timezone.utc)
                 + datetime.timedelta(days=float(ep[2:]) - 1))
        return (datetime.datetime.now(datetime.timezone.utc) - epoch).total_seconds() / 86400
    except (ValueError, IndexError):
        return 1e9


def _parse_satnogs(body: bytes) -> list[tuple[str, str, str]]:
    data = json.loads(body.decode("utf-8", errors="replace"))
    best: dict[int, tuple[float, tuple]] = {}   # NORAD → (leeftijd, tle); nieuwste wint
    for row in data if isinstance(data, list) else []:
        name = str(row.get("tle0", "")).strip()
        if name.startswith("0 "):
            name = name[2:].strip()
        l1 = str(row.get("tle1", "")).strip()
        l2 = str(row.get("tle2", "")).strip()
        if not (name and _valid_tle(l1, l2)):
            continue
        age = _tle_age_days(l1)
        nr  = norad_of(l1)
        if age <= _MAX_TLE_AGE_DAYS and (nr not in best or age < best[nr][0]):
            best[nr] = (age, (name, l1, l2))
    return [tle for _, tle in best.values()]


# ── Groepen samenstellen ──────────────────────────────────────────────────────

def _build_groups(satnogs: list | None, amsat: list | None) -> dict:
    """Nieuwe groepen uit de geslaagde bronnen. Ontbrekende groepen = niet
    bijgewerkt (de aanroeper behoudt dan de oude data)."""
    groups: dict[str, list] = {}
    amsat_by_norad = {norad_of(l1): (n, l1, l2) for n, l1, l2 in (amsat or [])}

    if amsat:
        groups["Amateur"] = [list(s) for nr, s in amsat_by_norad.items()
                             if nr != _ISS_NORAD]

    if satnogs:
        iss, weather, cube = [], [], []
        for name, l1, l2 in satnogs:
            nr = norad_of(l1)
            if nr in amsat_by_norad and nr != _ISS_NORAD:
                continue                        # al in Amateur (AMSAT-naam)
            if nr in amsat_by_norad:
                name = amsat_by_norad[nr][0]    # "ISS" i.p.v. "ISS (ZARYA)"
            if nr == _ISS_NORAD:
                iss.append([name, l1, l2])
            elif _WEATHER_RE.match(name) and "DEB" not in name.upper():
                weather.append([name, l1, l2])
            else:
                cube.append([name, l1, l2])
        groups["ISS"], groups["Weather"], groups["CubeSat"] = iss, weather, cube
    elif amsat and _ISS_NORAD in amsat_by_norad:
        groups["ISS"] = [list(amsat_by_norad[_ISS_NORAD])]

    return {g: _unique_names(rows) for g, rows in groups.items() if rows}


def _unique_names(rows: list) -> list:
    """Dubbele namen binnen een groep onderscheiden met het NORAD-nummer."""
    counts: dict[str, int] = {}
    for r in rows:
        counts[r[0]] = counts.get(r[0], 0) + 1
    for r in rows:
        if counts[r[0]] > 1:
            r[0] = f"{r[0]} [{norad_of(r[1])}]"
    return rows


# ── Publieke refresh ──────────────────────────────────────────────────────────

def refresh(old_cache: dict, progress=None) -> tuple[dict, dict]:
    """Ververs TLE-data binnen de rate-limits.

    Geeft (cache, rapport) terug. Rapport per bron:
      {"status": "ok"|"fail"|"wait"|"unused", "wait": sec, "error": str}
    plus "_busy": True als er al een refresh liep. De cache is altijd bruikbaar:
    groepen die niet bijgewerkt konden worden behouden hun oude data.
    """
    report: dict = {}
    if not _refresh_lock.acquire(blocking=False):
        return old_cache, {"_busy": True}
    try:
        results: dict = {}

        def _try(source: str, fn):
            wait = seconds_until_allowed(source)
            if wait > 0:
                report[source] = {"status": "wait", "wait": wait}
                return None
            if progress:
                progress(SOURCE_NAMES[source])
            _record_attempt(source)
            try:
                data = fn()
                if not data:
                    raise _FetchError("geen geldige TLE's ontvangen")
            except _FetchError as e:
                _record_result(source, False, e.hard, e.retry_after, str(e))
                report[source] = {"status": "fail", "error": str(e),
                                  "wait": seconds_until_allowed(source)}
                return None
            except Exception as e:                       # parsefout e.d.
                _record_result(source, False, error=str(e))
                report[source] = {"status": "fail", "error": str(e)[:80],
                                  "wait": seconds_until_allowed(source)}
                return None
            _record_result(source, True)
            report[source] = {"status": "ok", "count": len(data)}
            return data

        satnogs = _try("satnogs", lambda: _parse_satnogs(_http_get(SATNOGS_URL, 30)))
        amsat   = _try("amsat",   lambda: parse_tle_text(
            _http_get(AMSAT_URL, 20).decode("utf-8", errors="replace")))
        new_groups = _build_groups(satnogs, amsat)

        # CelesTrak alleen als noodreserve: beide primaire bronnen leverden
        # niets op én er is geen bruikbare cache
        if not new_groups and not old_cache:
            def _celestrak():
                got = {}
                for group, url in CELESTRAK_GROUPS.items():
                    # Eerste fout (bijv. blokkade) → direct stoppen, niet
                    # de overige groepen ook nog proberen
                    sats = parse_tle_text(
                        _http_get(url, 10).decode("utf-8", errors="replace"))
                    if sats:
                        got[group] = [list(s) for s in sats]
                return got
            ct = _try("celestrak", _celestrak)
            if ct:
                new_groups = {g: _unique_names(r) for g, r in ct.items()}
        else:
            report.setdefault("celestrak", {"status": "unused"})

        if not new_groups:
            return old_cache, report

        cache = dict(old_cache)
        cache.update(new_groups)
        return cache, report
    finally:
        _refresh_lock.release()


def next_refresh_wait() -> float:
    """Kortste wachttijd tot een primaire bron weer benaderd mag worden."""
    return min(seconds_until_allowed("satnogs"), seconds_until_allowed("amsat"))


# ── Namen migreren (selecties behouden bij bronwissel) ────────────────────────

def _name_keys(name: str) -> list[str]:
    """Genormaliseerde varianten: 'METEOR-M2 2' en 'METEOR M2-2' → 'METEORM22';
    'AO-91 (FOX-1B)' → ook 'AO91' en 'FOX1B'."""
    def norm(s):
        return re.sub(r"[^0-9A-Z]", "", s.upper())
    keys = [norm(name)]
    base = re.sub(r"\(.*?\)|\[.*?\]", "", name)
    keys.append(norm(base))
    keys += [norm(p) for p in re.findall(r"\((.*?)\)", name)]
    return [k for k in dict.fromkeys(keys) if k]


def migrate_names(names, new_cache: dict, old_cache: dict | None = None) -> list:
    """Vertaal opgeslagen satellietnamen naar de namen in new_cache.
    Eerst via NORAD-nummer (uit old_cache), anders via genormaliseerde naam.
    Onbekende namen blijven staan (kunnen na een latere update terugkomen)."""
    rows = [r for sats in new_cache.values() for r in sats if len(r) == 3]
    new_names = {r[0] for r in rows}
    by_norad = {norad_of(r[1]): r[0] for r in rows}
    alias: dict[str, str | None] = {}
    for r in rows:
        for k in _name_keys(r[0]):
            alias[k] = r[0] if alias.get(k, r[0]) == r[0] else None  # None = dubbelzinnig
    old_norad = {}
    for sats in (old_cache or {}).values():
        for r in sats:
            if len(r) == 3:
                old_norad[r[0]] = norad_of(r[1])

    out = []
    for n in names:
        new = n if n in new_names else None
        if new is None and old_norad.get(n) in by_norad:
            new = by_norad[old_norad[n]]
        if new is None:
            for k in _name_keys(n):
                if alias.get(k):
                    new = alias[k]
                    break
        out.append(new or n)
    return list(dict.fromkeys(out))
