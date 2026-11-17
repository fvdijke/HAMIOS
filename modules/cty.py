"""
HAMIOS — DXCC-database uit cty.dat (AD1C, country-files.com)

Roepnaam → land (DXCC-entiteit), continent, CQ-/ITU-zone en positie. Vervangt
de kleine handgemaakte prefixtabellen: daarmee kwamen spots van onbekende
prefixen niet op de kaart en kregen ze '??' als continent.

- cty.dat wordt in config/ bewaard en hooguit eens per 30 dagen ververst
  (op de achtergrond; zonder internet blijft de bewaarde versie gelden).
- Zolang er (nog) geen cty.dat is, valt lookup() terug op None en gebruiken
  de aanroepers hun eigen kleine tabel.

Formaat (per entiteit):
  Naam: CQ: ITU: Cont: Lat: Lon(west +): UTC: Hoofdprefix:
      prefix,prefix,=EXACTE_ROEPNAAM,prefix(cq)[itu]<lat/lon>{cont}~tz~;
"""

from __future__ import annotations

import os
import re
import threading
import time
import urllib.request
from dataclasses import dataclass, replace

from ._appdir import APP_DIR
from .version import USER_AGENT

CTY_URL   = "https://www.country-files.com/cty/cty.dat"
CTY_FILE  = os.path.join(APP_DIR, "config", "cty.dat")
MAX_AGE_S = 30 * 86400


@dataclass(frozen=True)
class Entity:
    name: str
    cq: int
    itu: int
    cont: str
    lat: float
    lon: float              # oost positief (cty.dat gebruikt west positief)
    prefix: str             # hoofdprefix (bv. 'PA', 'VK9N')


_OVR = re.compile(r"\((\d+)\)|\[(\d+)\]|<([-\d.]+)/([-\d.]+)>|\{(\w+)\}|~[-\d.]+~")


def parse(text: str) -> tuple[dict, dict]:
    """cty.dat-tekst → (prefixen {prefix: Entity}, exacte roepnamen {call: Entity})."""
    prefixes: dict[str, Entity] = {}
    exact: dict[str, Entity] = {}
    cur: Entity | None = None
    buf = ""
    for line in text.splitlines():
        if not line.strip():
            continue
        if not line[:1].isspace():
            parts = [p.strip() for p in line.split(":")]
            if len(parts) < 8:
                cur = None
                continue
            try:
                cur = Entity(name=parts[0], cq=int(parts[1]), itu=int(parts[2]),
                             cont=parts[3], lat=float(parts[4]), lon=-float(parts[5]),
                             prefix=parts[7].lstrip("*"))
            except ValueError:
                cur = None
            buf = ""
            continue
        if cur is None:
            continue
        buf += line.strip()
        if not buf.endswith(";"):
            continue
        for tok in buf[:-1].split(","):
            tok = tok.strip()
            if not tok:
                continue
            ent = cur
            for m in _OVR.finditer(tok):
                cq, itu, la, lo, cont = m.groups()
                if cq:
                    ent = replace(ent, cq=int(cq))
                elif itu:
                    ent = replace(ent, itu=int(itu))
                elif la:
                    ent = replace(ent, lat=float(la), lon=-float(lo))
                elif cont:
                    ent = replace(ent, cont=cont)
            key = _OVR.sub("", tok).upper()
            if key.startswith("="):
                exact[key[1:]] = ent
            elif key:
                prefixes[key] = ent
        buf = ""
    return prefixes, exact


class _Db:
    def __init__(self):
        self.prefixes: dict = {}
        self.exact: dict = {}
        self.maxlen = 0
        self._lock = threading.Lock()
        self._loading = False

    def load_text(self, text: str) -> bool:
        p, e = parse(text)
        if len(p) < 100:                 # geen (volledig) cty.dat
            return False
        with self._lock:
            self.prefixes, self.exact = p, e
            self.maxlen = max(len(k) for k in p)
        return True

    @property
    def loaded(self) -> bool:
        return bool(self.prefixes)


_DB = _Db()


def _base_call(call: str) -> str:
    """Het deel van de roepnaam dat het land bepaalt: bij 'PA/DL1ABC' en
    'DL1ABC/PA' is dat PA (uitgezonden vanuit PA); '/P', '/M', '/QRP' en een
    los cijfer (ander roepgebied) worden genegeerd."""
    call = call.strip().upper()
    parts = [p for p in call.split("/") if p]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    junk = {"P", "M", "MM", "AM", "QRP", "A", "B", "LH", "R", "T"}
    parts = [p for p in parts if p not in junk and not p.isdigit()] or parts[:1]
    if len(parts) == 1:
        return parts[0]
    # Kortste deel met een cijfer of ≤ 3 tekens is meestal het landprefix
    short = min(parts, key=len)
    return short if len(short) <= 4 else parts[0]


def lookup(call: str) -> Entity | None:
    """Entiteit voor een roepnaam (langste prefix-match), of None."""
    if not _DB.loaded or not call:
        return None
    c = call.strip().upper()
    with _DB._lock:
        ent = _DB.exact.get(c)
        if ent:
            return ent
        base = _base_call(c)
        ent = _DB.exact.get(base)
        if ent:
            return ent
        for n in range(min(len(base), _DB.maxlen), 0, -1):
            ent = _DB.prefixes.get(base[:n])
            if ent:
                return ent
    return None


def load_cached() -> bool:
    """Bewaarde cty.dat inlezen (snel, bij het opstarten)."""
    try:
        with open(CTY_FILE, encoding="utf-8", errors="replace") as f:
            return _DB.load_text(f.read())
    except OSError:
        return False


def _download() -> bool:
    req = urllib.request.Request(CTY_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as r:
        text = r.read().decode("utf-8", errors="replace")
    if not _DB.load_text(text):
        return False
    os.makedirs(os.path.dirname(CTY_FILE), exist_ok=True)
    tmp = CTY_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, CTY_FILE)
    return True


def ensure_loaded_async(on_ready=None) -> None:
    """Bewaarde versie meteen laden; op de achtergrond verversen als hij
    ontbreekt of ouder is dan 30 dagen. on_ready() na een geslaagde download."""
    load_cached()
    try:
        age = time.time() - os.path.getmtime(CTY_FILE)
    except OSError:
        age = None
    if (age is not None and age < MAX_AGE_S) or _DB._loading:
        return
    _DB._loading = True

    def run():
        try:
            if _download() and on_ready:
                on_ready()
        except Exception:
            pass
        finally:
            _DB._loading = False

    threading.Thread(target=run, daemon=True, name="cty-download").start()
