"""
HAMIOS — versie en update-controle.

VERSION is de enige plek waar het versienummer van HAMIOS staat; de rest van de
code (venstertitel, splash, User-Agent) leest het hier.

Update-controle (zelfde opzet als COHESION): bij het opstarten haalt de splash
version.json van GitHub (main) op en vergelijkt de daar gepubliceerde versie
met VERSION. Is die nieuwer, dan toont de splash UPDATE BESCHIKBAAR.

- Offline, time-out, HTTP-fout, ongeldige JSON: geen melding, de check blijft stil.
- Omgevingsvariabelen (testen):
    HAMIOS_UPDATE_URL   = andere URL of een lokaal bestandspad
    HAMIOS_UPDATE_CHECK = 0  -> nooit online controleren

Bij een release: VERSION hier ophogen, version.json in de repo-root gelijk
zetten (tests/test_version.py bewaakt dat), bouwen, pushen.
"""

from __future__ import annotations

import json
import os
import re

VERSION = "5.8.4"

USER_AGENT = f"HAMIOS/{VERSION}"

VERSION_URL  = "https://raw.githubusercontent.com/fvdijke/HAMIOS/main/version.json"
RELEASES_URL = "https://github.com/fvdijke/HAMIOS/releases/latest"
TIMEOUT_S    = 4

_VALID = re.compile(r"^\d+(\.\d+)*$")


def is_valid_version(v: str) -> bool:
    return isinstance(v, str) and 0 < len(v) < 32 and bool(_VALID.match(v))


def compare_versions(a: str, b: str) -> int:
    """<0 als a ouder is dan b, 0 als gelijk, >0 als a nieuwer is. "5.9" == "5.9.0"."""
    pa = [int(x) for x in a.split(".")]
    pb = [int(x) for x in b.split(".")]
    n = max(len(pa), len(pb))
    pa += [0] * (n - len(pa))
    pb += [0] * (n - len(pb))
    return (pa > pb) - (pa < pb)


def parse_published_version(text: str) -> str:
    """De versie uit een version.json-tekst, of "" bij elk probleem."""
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return ""
    v = data.get("version", "") if isinstance(data, dict) else ""
    v = str(v).strip().lstrip("vV")
    return v if is_valid_version(v) else ""


def update_check_enabled() -> bool:
    return os.environ.get("HAMIOS_UPDATE_CHECK", "1").strip() != "0"


def fetch_published_version(timeout: float = TIMEOUT_S) -> str:
    """Haal de gepubliceerde versie op (blokkerend — draai dit in een thread).
    Geeft "" terug bij elk probleem (offline, time-out, HTTP-fout, rare inhoud)."""
    src = os.environ.get("HAMIOS_UPDATE_URL", "").strip() or VERSION_URL
    try:
        if os.path.isabs(src) and os.path.exists(src):          # lokaal bestand (testen)
            with open(src, "r", encoding="utf-8") as f:
                return parse_published_version(f.read(64 * 1024))
        import urllib.request as _urlreq
        req = _urlreq.Request(src, headers={"User-Agent": USER_AGENT,
                                            "Cache-Control": "no-cache"})
        with _urlreq.urlopen(req, timeout=timeout) as r:
            if r.status != 200:
                return ""
            return parse_published_version(r.read(64 * 1024).decode("utf-8", "replace"))
    except Exception:
        return ""


def newer_version(published: str, current: str = VERSION) -> str:
    """published als die nieuwer is dan current, anders ""."""
    if not is_valid_version(published) or not is_valid_version(current):
        return ""
    return published if compare_versions(published, current) > 0 else ""
