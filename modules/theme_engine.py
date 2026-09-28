"""
HAMIOS — thema-motor

De code van HAMIOS is geschreven met het donkere standaardpalet (thema "night"):
theme.py-constanten én losse kleurliterals in panelen, grafieken en dialogen.
Een ander thema herschrijft die kleuren centraal, op het moment dat ze aan Qt
worden gegeven:

  • setStyleSheet / setText / setToolTip / setHtml — #RRGGBB, rgb(a)(…),
    white/black en font-size in de tekst worden omgezet;
  • QColor / QFont — PySide6.QtGui.QColor en .QFont worden vervangen door een
    subklasse die kleur resp. puntgrootte omzet bij het aanmaken.

Kleuren die precies een palet-token zijn (bv. BG_PANEL of de statuskleur
#EF5350) krijgen de themakleur van dat token. Overige kleuren volgen een regel:
neutrale/donkere kleuren schuiven mee over de lichtheidsas van het palet,
verzadigde kleuren (status, banden, grafieklijnen) worden lichter/donkerder tot
ze genoeg contrast hebben met de paneelachtergrond.

De wereldkaart (mapview, layers) is uitgezonderd: nachtschaduw, grijze lijn en
aurora moeten op de kaartafbeelding blijven zoals ze zijn.

Het thema wordt bij het opstarten gekozen (config "theme"/"custom_theme", of
omgevingsvariabele HAMIOS_THEME); wisselen vraagt een herstart. Voor "night"
wordt niets geïnstalleerd: het standaarduiterlijk blijft exact gelijk.

Dit module moet geïmporteerd worden vóórdat andere modules QColor/QFont uit
PySide6.QtGui importeren (HAMIOS5.py doet dat als eerste).
"""

import colorsys
import json
import os
import re
import sys

from ._appdir import APP_DIR

# ── Tokens: (sleutel, kleur in het night-palet) ──────────────────────────────
# Volgorde = volgorde in de thema-designer.
TOKENS = [
    ("BG_ROOT",    "#1A1C1F"),
    ("BG_PANEL",   "#22252A"),
    ("BG_SURFACE", "#2A2E35"),
    ("BG_HOVER",   "#32373F"),
    ("BORDER",     "#383E47"),
    ("SELECT",     "#2A4060"),
    ("TEXT_H1",    "#F0E6C8"),
    ("TEXT_BODY",  "#B0B8C4"),
    ("TEXT_DIM",   "#606870"),
    ("ACCENT",     "#C8A84B"),
    ("ACCENT_HI",  "#E0C060"),
    ("ACCENT_LO",  "#A88030"),
    ("RED",        "#EF5350"),
    ("ORANGE",     "#FFA726"),
    ("GREEN",      "#4CAF50"),
    ("BLUE",       "#4FC3F7"),
    ("YELLOW",     "#FFF176"),
    ("DANGER_BG",  "#5A1010"),
    ("DANGER_HI",  "#8B1A1A"),
]
TOKEN_KEYS = [k for k, _ in TOKENS]

# Literals in de code die hetzelfde bedoelen als een token
_ALIASES = {"#1A1D22": "BG_ROOT"}

# Tokens die de lichtheidsas voor neutrale kleuren vastleggen
_NEUTRAL_KEYS = ("BG_ROOT", "BG_PANEL", "BG_SURFACE", "BG_HOVER", "BORDER",
                 "TEXT_DIM", "TEXT_BODY", "TEXT_H1")

NIGHT = dict(TOKENS, font_scale=1.0)

PRESETS = {
    "night": NIGHT,
    "day": {
        "BG_ROOT":    "#D5D2CA",
        "BG_PANEL":   "#F5F3EE",
        "BG_SURFACE": "#E7E4DC",
        "BG_HOVER":   "#DAD6CC",
        "BORDER":     "#B5AFA3",
        "SELECT":     "#C6D9F0",
        "TEXT_H1":    "#1C1F24",
        "TEXT_BODY":  "#383E46",
        "TEXT_DIM":   "#6A7079",
        "ACCENT":     "#8A6810",
        "ACCENT_HI":  "#A47C14",
        "ACCENT_LO":  "#6C510C",
        "RED":        "#C62828",
        "ORANGE":     "#C75000",
        "GREEN":      "#2E7D32",
        "BLUE":       "#0271B0",
        "YELLOW":     "#8A6E00",
        "DANGER_BG":  "#F2D4D4",
        "DANGER_HI":  "#E6B0B0",
        "font_scale": 1.0,
    },
    "contrast": {
        "BG_ROOT":    "#08090B",
        "BG_PANEL":   "#121417",
        "BG_SURFACE": "#20242A",
        "BG_HOVER":   "#2E333B",
        "BORDER":     "#6A7380",
        "SELECT":     "#1F4C85",
        "TEXT_H1":    "#FFFFFF",
        "TEXT_BODY":  "#E6E9EE",
        "TEXT_DIM":   "#AEB6C1",
        "ACCENT":     "#FFC83D",
        "ACCENT_HI":  "#FFD970",
        "ACCENT_LO":  "#E0A820",
        "RED":        "#FF6B6B",
        "ORANGE":     "#FFB547",
        "GREEN":      "#5FD068",
        "BLUE":       "#6FD3FF",
        "YELLOW":     "#FFF38A",
        "DANGER_BG":  "#6A1414",
        "DANGER_HI":  "#A02020",
        "font_scale": 1.15,
    },
}
PRESET_ORDER = ("night", "day", "contrast", "custom")

# Modules waarvan QColor/QFont onveranderd blijven (tekenen op de wereldkaart)
_EXEMPT_MODULES = {"modules.mapview", "modules.layers"}


# ── Kleurhulpjes ──────────────────────────────────────────────────────────────

def _hex_to_rgb(h: str):
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _rgb_to_hex(r, g, b) -> str:
    return f"#{int(r):02X}{int(g):02X}{int(b):02X}"


def _lum(rgb) -> float:
    """Relatieve luminantie (WCAG)."""
    def ch(c):
        c /= 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b) -> float:
    """WCAG-contrastverhouding tussen twee (r,g,b)-kleuren."""
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def _hls(rgb):
    return colorsys.rgb_to_hls(*(c / 255.0 for c in rgb))


def _from_hls(h, l, s):
    return tuple(max(0, min(255, round(c * 255))) for c in colorsys.hls_to_rgb(h, l, s))


def is_light(palette: dict) -> bool:
    return _hls(_hex_to_rgb(palette["BG_PANEL"]))[1] > 0.5


def complete_palette(base: dict) -> dict:
    """Vul ontbrekende/ongeldige sleutels aan vanuit het night-palet."""
    pal = dict(NIGHT)
    for k in TOKEN_KEYS:
        v = str(base.get(k, "")).strip()
        if re.fullmatch(r"#[0-9A-Fa-f]{6}", v):
            pal[k] = v.upper()
    try:
        pal["font_scale"] = max(0.8, min(1.6, float(base.get("font_scale", 1.0))))
    except (TypeError, ValueError):
        pal["font_scale"] = 1.0
    return pal


# ── Omzetting ─────────────────────────────────────────────────────────────────

class Remapper:
    """Zet kleuren uit het night-palet om naar een ander palet."""

    def __init__(self, palette: dict):
        self.pal = complete_palette(palette)
        self.scale = self.pal["font_scale"]
        self.exact = {night.upper(): self.pal[k] for k, night in TOKENS}
        for lit, k in _ALIASES.items():
            self.exact[lit] = self.pal[k]
        # Lichtheidsas: (L in night, themakleur), oplopend in L
        pts = {}
        for k in _NEUTRAL_KEYS:
            pts.setdefault(round(_hls(_hex_to_rgb(NIGHT[k]))[1], 4),
                           _hex_to_rgb(self.pal[k]))
        self.axis = sorted(pts.items())
        self.light = is_light(self.pal)
        self.bg = _hex_to_rgb(self.pal["BG_PANEL"])
        self.min_contrast = 3.2 if self.light else (4.5 if self.scale > 1.05 else 3.0)
        self._cache = {}
        self._css_cache = {}

    # (r,g,b) → (r,g,b)
    def rgb(self, r, g, b):
        key = (r, g, b)
        hit = self._cache.get(key)
        if hit is None:
            hit = self._cache[key] = self._map(key)
        return hit

    def hex(self, h: str) -> str:
        return _rgb_to_hex(*self.rgb(*_hex_to_rgb(h)))

    def _map(self, rgb):
        ex = self.exact.get(_rgb_to_hex(*rgb))
        if ex:
            return _hex_to_rgb(ex)
        h, l, s = _hls(rgb)
        if s < 0.35 or l < 0.30:
            return self._neutral(rgb, h, l, s)
        return self._saturated(h, l, s)

    def _neutral(self, rgb, h, l, s):
        ax = self.axis
        if l <= ax[0][0]:
            out = ax[0][1]
        elif l >= ax[-1][0]:
            out = ax[-1][1]
        else:
            for (l0, c0), (l1, c1) in zip(ax, ax[1:]):
                if l0 <= l <= l1:
                    t = (l - l0) / (l1 - l0) if l1 > l0 else 0.0
                    out = tuple(round(a + (b - a) * t) for a, b in zip(c0, c1))
                    break
        if s > 0.2:
            # Getinte kleur (selectie, gevaar-rood): tint behouden
            _, lo, so = _hls(out)
            out = _from_hls(h, lo, max(so, s * (0.7 if self.light else 1.0)))
        return out

    def _saturated(self, h, l, s):
        out = _from_hls(h, l, s)
        step = -0.02 if self.light else 0.02
        n = 0
        while contrast(out, self.bg) < self.min_contrast and 0.05 < l < 0.95 and n < 45:
            l += step
            out = _from_hls(h, l, s)
            n += 1
        return out

    # ── Tekst (QSS / HTML) ────────────────────────────────────────────────────
    _RE_HEX = re.compile(r"#([0-9A-Fa-f]{6})(?![0-9A-Za-z_-])")
    _RE_RGB = re.compile(r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(,[^)]*)?\)")
    # white/black: in stylesheets overal als los woord, in HTML alleen na ':'
    _RE_NAMED_QSS = re.compile(r"()(?<![\w#-])(white|black)(?![\w-])", re.I)
    _RE_NAMED = re.compile(r"(:\s*)(white|black)(?![\w-])", re.I)
    _RE_FONT = re.compile(r"(font-size\s*:\s*)(\d+(?:\.\d+)?)(pt|px)", re.I)

    def css(self, text: str, sheet: bool = False) -> str:
        """Zet kleuren en lettergroottes in QSS (sheet=True) of HTML om."""
        if not text:
            return text
        hit = self._css_cache.get((text, sheet))
        if hit is not None:
            return hit
        out = self._RE_HEX.sub(lambda m: self.hex(m.group(0)), text)

        def _rgb(m):
            r, g, b = self.rgb(*(min(255, int(x)) for x in m.group(1, 2, 3)))
            if m.group(4):
                return f"rgba({r},{g},{b}{m.group(4)})"
            return f"rgb({r},{g},{b})"
        out = self._RE_RGB.sub(_rgb, out)
        out = (self._RE_NAMED_QSS if sheet else self._RE_NAMED).sub(
            lambda m: m.group(1) + self.hex("#FFFFFF" if m.group(2).lower() == "white"
                                            else "#000000"), out)
        if self.scale != 1.0:
            def _fs(m):
                v = float(m.group(2)) * self.scale
                v = f"{v:.1f}".rstrip("0").rstrip(".")
                return f"{m.group(1)}{v}{m.group(3)}"
            out = self._RE_FONT.sub(_fs, out)
        if len(self._css_cache) > 4000:
            self._css_cache.clear()
        self._css_cache[(text, sheet)] = out
        # Idempotent: al omgezette tekst (bv. styleSheet() teruggelezen) blijft gelijk
        self._css_cache[(out, sheet)] = out
        return out


# ── Actief thema ──────────────────────────────────────────────────────────────

ACTIVE_NAME = "night"
ACTIVE_PALETTE = dict(NIGHT)
REMAP = None            # Remapper, of None bij het standaardthema
_QColorBase = None      # originele PySide6-klassen (voor de designer-preview)
_QFontBase = None
_RAW_PSF = None         # originele QFont.setPointSizeF (bij tekstschaal ≠ 1)


def read_setting():
    """(naam, custom-palet) uit omgeving of config/hamios_config.json."""
    name, custom = "night", {}
    try:
        path = os.path.join(APP_DIR, "config", "hamios_config.json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            name = str(data.get("theme", "night") or "night")
            custom = data.get("custom_theme") or {}
    except Exception:
        pass
    env = os.environ.get("HAMIOS_THEME", "").strip().lower()
    if env:
        name = env
    if name not in PRESET_ORDER:
        name = "night"
    return name, custom if isinstance(custom, dict) else {}


def palette_for(name: str, custom: dict) -> dict:
    if name == "custom":
        return complete_palette(custom or {})
    return complete_palette(PRESETS.get(name, NIGHT))


def _caller_exempt(depth: int = 2) -> bool:
    try:
        return sys._getframe(depth).f_globals.get("__name__") in _EXEMPT_MODULES
    except ValueError:
        return False


def _install(remap: Remapper):
    """Vervang QColor/QFont en haak de tekst-setters van Qt aan."""
    global _QColorBase, _QFontBase
    from PySide6 import QtGui, QtWidgets

    _QColorBase = QtGui.QColor
    _QFontBase = QtGui.QFont
    base_color, base_font = _QColorBase, _QFontBase

    class QColor(base_color):
        def __init__(self, *a):
            if a and not _caller_exempt():
                a0 = a[0]
                if isinstance(a0, str):
                    if len(a0) == 7 and a0[0] == "#":
                        try:
                            a = (remap.hex(a0),) + a[1:]
                        except ValueError:
                            pass
                elif len(a) in (3, 4) and all(type(x) is int for x in a):
                    r, g, b = remap.rgb(*(max(0, min(255, x)) for x in a[:3]))
                    a = (r, g, b) + a[3:]
            super().__init__(*a)

    QColor.__name__ = QColor.__qualname__ = "QColor"
    QtGui.QColor = QColor

    sc = remap.scale
    if sc != 1.0:
        class QFont(base_font):
            def __init__(self, *a):
                if (len(a) >= 2 and isinstance(a[0], str) and type(a[1]) is int
                        and a[1] > 0 and not _caller_exempt()):
                    a = (a[0], max(1, round(a[1] * sc))) + a[2:]
                super().__init__(*a)

        QFont.__name__ = QFont.__qualname__ = "QFont"
        QtGui.QFont = QFont

        # Ook fonts die niet via de constructor komen (bv. painter.font())
        orig_ps, orig_psf = base_font.setPointSize, base_font.setPointSizeF

        def setPointSize(self, size):
            if size > 0 and not _caller_exempt():
                size = max(1, round(size * sc))
            orig_ps(self, size)

        def setPointSizeF(self, size):
            if size > 0 and not _caller_exempt():
                size = size * sc
            orig_psf(self, size)
        base_font.setPointSize = setPointSize
        base_font.setPointSizeF = setPointSizeF
        global _RAW_PSF
        _RAW_PSF = orig_psf

    css = remap.css

    def _wrap(cls, meth, rich_only=False, sheet=False):
        orig = getattr(cls, meth)

        def f(self, text, *rest):
            if isinstance(text, str) and (not rich_only or "<" in text):
                text = css(text, sheet)
            return orig(self, text, *rest)
        f.__name__ = meth
        setattr(cls, meth, f)

    _wrap(QtWidgets.QWidget, "setStyleSheet", sheet=True)
    _wrap(QtWidgets.QApplication, "setStyleSheet", sheet=True)
    _wrap(QtWidgets.QWidget, "setToolTip", rich_only=True)
    _wrap(QtWidgets.QLabel, "setText", rich_only=True)
    _wrap(QtWidgets.QTextEdit, "setHtml")
    _wrap(QtWidgets.QTextEdit, "setText", rich_only=True)
    _wrap(QtWidgets.QTextEdit, "insertHtml")
    _wrap(QtWidgets.QGraphicsTextItem, "setHtml")


def activate():
    """Lees de thema-instelling en installeer de omzetting (eenmalig)."""
    global ACTIVE_NAME, ACTIVE_PALETTE, REMAP
    if REMAP is not None:
        return
    name, custom = read_setting()
    pal = palette_for(name, custom)
    ACTIVE_NAME, ACTIVE_PALETTE = name, pal
    if name == "night" or pal == complete_palette(NIGHT):
        return
    REMAP = Remapper(pal)
    try:
        _install(REMAP)
    except Exception as e:          # thema mag het opstarten nooit blokkeren
        print(f"Thema '{name}' niet geïnstalleerd: {e}", file=sys.stderr)
        REMAP = None
        ACTIVE_NAME, ACTIVE_PALETTE = "night", dict(NIGHT)


def raw_color(hex_str: str):
    """QColor zonder thema-omzetting (voor previews in de designer)."""
    from PySide6 import QtGui
    return (_QColorBase or QtGui.QColor)(hex_str)


def raw_font(family: str, size: float):
    """QFont met exact deze puntgrootte (zonder thema-schaal)."""
    from PySide6 import QtGui
    f = (_QFontBase or QtGui.QFont)(family)
    (_RAW_PSF or QtGui.QFont.setPointSizeF)(f, float(size))
    return f
