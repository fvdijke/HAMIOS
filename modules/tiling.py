"""HAMIOS v5 — Tegelindeling voor de panelen.

Het scherm is een boom van splitsingen (QSplitter); de bladeren zijn panelen of
tabgroepen.
  • altijd aansluitend — gaten of overlap zijn structureel onmogelijk
  • verhoudingen i.p.v. pixels — schaalt mee met elk scherm en venster
  • scheidingslijn verslepen past beide buren tegelijk aan
  • paneel verbergen → buren vullen de ruimte; tonen → oude plek en grootte
  • paneel (titelbalk of tab) verslepen naar een ander paneel:
      rand  → ernaast plaatsen        midden → erbij als tabblad
      Ctrl + midden → van plek wisselen
  • vergrendelen: geen slepen, scheidingslijnen vast

Boomformaat (JSON, opgeslagen als "__tree__" in de layout):
    paneel:    {"p": "worldmap"}
    tabgroep:  {"t": ["kp_48h", "bz_24h"], "a": "kp_48h"}   (a = actieve tab)
    splitsing: {"o": "h" | "v", "s": [verhoudingen …], "c": [kinderen …]}
    "h" = naast elkaar (verticale scheidingslijnen), "v" = onder elkaar.

Oude pixel-layouts ({pid: [x, y, w, h, zichtbaar]}) worden bij het laden
automatisch omgezet met guillotine-sneden (layout_from_rects).
"""

from __future__ import annotations

import copy

from PySide6.QtCore import Qt, QRect, QPoint, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (QApplication, QSplitter, QStackedWidget, QTabBar,
                               QVBoxLayout, QWidget)

from .theme import ACCENT, BG_PANEL, BG_ROOT, BG_SURFACE, TEXT_DIM

HANDLE_W = 3          # breedte scheidingslijn (px)
_TOL     = 12         # tolerantie bij het herkennen van sneden (px, ≥ snap-raster)
_EDGE    = 0.25       # randzone (fractie van het doel) voor 'ernaast plaatsen'
PANEL_MIME = "application/x-hamios-panel"


# ── Boom-hulpfuncties ─────────────────────────────────────────────────────────

def _leaves(node) -> list[str]:
    if "p" in node:
        return [node["p"]]
    if "t" in node:
        return list(node["t"])
    return [p for c in node["c"] for p in _leaves(c)]


def valid_tree(node) -> bool:
    try:
        if "p" in node:
            return isinstance(node["p"], str)
        if "t" in node:
            return bool(node["t"]) and all(isinstance(p, str) for p in node["t"])
        return (node["o"] in ("h", "v") and len(node["c"]) == len(node["s"]) >= 1
                and all(valid_tree(c) for c in node["c"]))
    except (KeyError, TypeError):
        return False


def _normalize(node):
    """Tabgroep van één → paneel; splitsing van één → dat kind."""
    if node is None:
        return None
    if "t" in node:
        tabs = list(dict.fromkeys(node["t"]))
        if not tabs:
            return None
        if len(tabs) == 1:
            return {"p": tabs[0]}
        active = node.get("a") if node.get("a") in tabs else tabs[0]
        return {"t": tabs, "a": active}
    if "c" in node:
        kids, ratios = [], []
        for c, r in zip(node["c"], node["s"]):
            nc = _normalize(c)
            if nc is not None:
                kids.append(nc)
                ratios.append(r)
        if not kids:
            return None
        if len(kids) == 1:
            return kids[0]
        tot = sum(ratios) or 1.0
        return {"o": node["o"], "s": [r / tot for r in ratios], "c": kids}
    return node


def prune_tree(node: dict, known) -> dict | None:
    """Verwijder bladeren van onbekende panelen (bijv. uit een andere versie);
    splitsingen/tabgroepen met één overgebleven kind vallen samen."""
    if node is None:
        return None
    if "p" in node:
        return node if node["p"] in known else None
    if "t" in node:
        return _normalize({"t": [p for p in node["t"] if p in known], "a": node.get("a")})
    kids = [prune_tree(c, known) for c in node.get("c", [])]
    return _normalize({"o": node["o"], "s": list(node.get("s", [])), "c": kids})


def remove_panel(tree: dict, pid: str) -> dict | None:
    return prune_tree(tree, set(_leaves(tree)) - {pid})


def swap_panels(tree: dict, a: str, b: str) -> dict:
    """Wissel twee panelen van plek (ook binnen/tussen tabgroepen)."""
    t = copy.deepcopy(tree)

    def walk(n):
        if "p" in n:
            n["p"] = {a: b, b: a}.get(n["p"], n["p"])
        elif "t" in n:
            n["t"] = [{a: b, b: a}.get(p, p) for p in n["t"]]
            n["a"] = {a: b, b: a}.get(n.get("a"), n.get("a"))
        else:
            for c in n["c"]:
                walk(c)
    walk(t)
    return t


def insert_panel(tree: dict, pid: str, target: str, zone: str) -> dict:
    """Plaats pid bij het blad (paneel of tabgroep) dat target bevat.
    zone: 'center' → als tabblad; 'left'/'right'/'top'/'bottom' → ernaast."""
    t = copy.deepcopy(tree)
    orient = "h" if zone in ("left", "right") else "v"
    before = zone in ("left", "top")

    def is_target(n) -> bool:
        return n.get("p") == target or ("t" in n and target in n["t"])

    def make_new(n) -> dict:
        if zone == "center":
            tabs = [n["p"]] if "p" in n else list(n["t"])
            return {"t": tabs + [pid], "a": pid}
        pair = [{"p": pid}, n] if before else [n, {"p": pid}]
        return {"o": orient, "s": [0.5, 0.5], "c": pair}

    if is_target(t):
        return _normalize(make_new(t))

    def walk(n) -> bool:
        for i, c in enumerate(n["c"]):
            if is_target(c):
                if zone != "center" and n["o"] == orient:
                    # zelfde richting als de ouder → als broer invoegen (geen extra nesting)
                    share = n["s"][i] / 2
                    n["s"][i] = share
                    pos = i if before else i + 1
                    n["c"].insert(pos, {"p": pid})
                    n["s"].insert(pos, share)
                else:
                    n["c"][i] = make_new(c)
                return True
            if "c" in c and walk(c):
                return True
        return False

    walk(t)
    return _normalize(t)


# ── Omzetting pixel-rechthoeken → boom ────────────────────────────────────────

def _cuts(items, axis: int):
    """Posities waarop alle rechthoeken zonder doorsnijden te scheiden zijn.
    axis 0 = x (snede verticaal → 'h'), 1 = y (snede horizontaal → 'v')."""
    lo, hi = (0, 2) if axis == 0 else (1, 3)
    ends = sorted({r[lo] + r[hi] for _, r in items})
    min_start = min(r[lo] for _, r in items)
    max_end = max(r[lo] + r[hi] for _, r in items)
    cuts = []
    for c in ends:
        if c >= max_end - _TOL or c <= min_start + _TOL:
            continue
        if all(r[lo] + r[hi] <= c + _TOL or r[lo] >= c - _TOL for _, r in items):
            if not cuts or c - cuts[-1] > _TOL:
                cuts.append(c)
    return cuts


def _split(items, axis: int, cuts):
    lo, hi = (0, 2) if axis == 0 else (1, 3)
    groups = [[] for _ in range(len(cuts) + 1)]
    for it in items:
        center = it[1][lo] + it[1][hi] / 2
        groups[sum(1 for c in cuts if center > c)].append(it)
    groups = [g for g in groups if g]
    bounds = [min(r[lo] for _, r in items)] + list(cuts) + [max(r[lo] + r[hi] for _, r in items)]
    sizes = [max(1, bounds[i + 1] - bounds[i]) for i in range(len(bounds) - 1)]
    return groups, sizes[:len(groups)]


def _build(items) -> dict:
    if len(items) == 1:
        return {"p": items[0][0]}
    best = None
    for axis in (0, 1):
        cuts = _cuts(items, axis)
        if cuts and (best is None or len(cuts) > len(best[1])):
            best = (axis, cuts)
    if best is None:
        # Niet te snijden (overlap): splits op middelpunt langs de langste as
        xs = [r[0] + r[2] / 2 for _, r in items]
        ys = [r[1] + r[3] / 2 for _, r in items]
        axis = 0 if (max(xs) - min(xs)) >= (max(ys) - min(ys)) else 1
        key = (lambda it: it[1][0] + it[1][2] / 2) if axis == 0 else \
              (lambda it: it[1][1] + it[1][3] / 2)
        srt = sorted(items, key=key)
        half = len(srt) // 2
        groups = [srt[:half], srt[half:]]
        ext = 2 if axis == 0 else 3
        sizes = [max(1, sum(r[ext] for _, r in g) / len(g)) for g in groups]
    else:
        axis, cuts = best
        groups, sizes = _split(items, axis, cuts)
    total = float(sum(sizes))
    return {"o": "h" if axis == 0 else "v",
            "s": [round(s / total, 4) for s in sizes],
            "c": [_build(g) for g in groups]}


def _insert_near(tree: dict, pid: str, rect, rects: dict) -> dict:
    """Voeg (verborgen) paneel pid in naast het blad waar het het meest mee
    overlapt — bij tonen verschijnt het dan op een logische plek."""
    def overlap(a, b):
        w = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
        h = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
        return max(0, w) * max(0, h)

    candidates = [p for p in _leaves(tree) if p in rects]
    if not candidates:
        return {"o": "h", "s": [0.8, 0.2], "c": [tree, {"p": pid}]}
    host = max(candidates, key=lambda p: (overlap(rect, rects[p]),
                                          -abs(rect[0] - rects[p][0]) - abs(rect[1] - rects[p][1])))
    hr = rects[host]
    return insert_panel(tree, pid, host, "right" if hr[2] >= hr[3] else "bottom")


def layout_from_rects(rects: dict, visible: dict) -> dict:
    """Pixel-layout {pid: (x, y, w, h)} → boom. Zichtbare panelen bepalen de
    structuur; verborgen panelen worden bij hun meest overlappende buur gezet."""
    vis_items = [(p, r) for p, r in rects.items() if visible.get(p, True) and r[2] > 0 and r[3] > 0]
    if not vis_items:
        vis_items = list(rects.items())[:1]
    tree = _build(vis_items)
    placed = set(_leaves(tree))
    for p, r in rects.items():
        if p not in placed:
            tree = _insert_near(tree, p, r, rects)
            placed.add(p)
    return tree


# ── Tabgroep ──────────────────────────────────────────────────────────────────

_TAB_QSS = f"""
QTabBar {{ background: {BG_PANEL}; }}
QTabBar::tab {{
    background: {BG_SURFACE}; color: {TEXT_DIM};
    border: 1px solid {ACCENT}; border-bottom: none;
    padding: 3px 8px; margin-right: 2px; font-size: 8pt; font-weight: bold;
    border-top-left-radius: 3px; border-top-right-radius: 3px;
}}
QTabBar::tab:selected {{ background: {BG_PANEL}; color: {ACCENT}; }}
QTabBar::tab:hover    {{ color: {ACCENT}; }}
QTabBar::close-button {{ subcontrol-position: right; }}
"""


class _TabBar(QTabBar):
    """Tabbalk waarvan tabs naar een andere plek versleept kunnen worden."""

    def __init__(self, group: "TabGroup"):
        super().__init__(group)
        self._group = group
        self._press: QPoint | None = None
        self._press_idx = -1
        self.setTabsClosable(True)
        self.setExpanding(False)
        self.setElideMode(Qt.ElideRight)
        self.setUsesScrollButtons(True)
        self.setDocumentMode(True)
        self.setStyleSheet(_TAB_QSS)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._press = event.position().toPoint()
            self._press_idx = self.tabAt(self._press)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (self._press is not None and self._press_idx >= 0
                and event.buttons() & Qt.LeftButton
                and (event.position().toPoint() - self._press).manhattanLength()
                >= QApplication.startDragDistance()):
            pid = self.tabData(self._press_idx)
            self._press = None
            panel = self._group.panel(pid)
            if panel is not None:
                from .panel import start_panel_drag
                start_panel_drag(self, panel)
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._press = None
        super().mouseReleaseEvent(event)


class TabGroup(QWidget):
    """Meerdere panelen op één plek, als tabbladen (titel op de tab)."""

    def __init__(self, pids: list[str], active: str | None, panels: dict, parent=None):
        super().__init__(parent)
        self._pids = list(pids)
        self._panels = panels
        self._active = active if active in pids else pids[0]
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self._bar = _TabBar(self)
        self._stack = QStackedWidget()
        lay.addWidget(self._bar)
        lay.addWidget(self._stack, 1)
        for pid in self._pids:
            p = panels[pid]
            p.set_in_tabs(True)
            self._stack.addWidget(p)
        self._bar.currentChanged.connect(self._on_current)
        self._bar.tabCloseRequested.connect(self._on_close)
        self.sync()

    # ── API ──────────────────────────────────────────────────────────────────
    def pids(self) -> list[str]:
        return list(self._pids)

    def active(self) -> str:
        return self._active

    def panel(self, pid):
        return self._panels.get(pid)

    def any_visible(self) -> bool:
        return any(self._panels[p].is_panel_visible() for p in self._pids)

    def sync(self, prefer: str | None = None):
        """Tabs = zichtbare panelen. prefer: net getoond paneel wordt actief."""
        visible = [p for p in self._pids if self._panels[p].is_panel_visible()]
        if prefer in visible:
            self._active = prefer
        elif self._active not in visible and visible:
            self._active = visible[0]
        self._bar.blockSignals(True)
        while self._bar.count():
            self._bar.removeTab(0)
        for pid in visible:
            i = self._bar.addTab(self._panels[pid].title())
            self._bar.setTabData(i, pid)
            if pid == self._active:
                self._bar.setCurrentIndex(i)
        self._bar.blockSignals(False)
        if self._active in visible:
            self._stack.setCurrentWidget(self._panels[self._active])
            self._panels[self._active].show()

    # ── signalen ─────────────────────────────────────────────────────────────
    def _on_current(self, idx: int):
        pid = self._bar.tabData(idx)
        if pid:
            self._active = pid
            self._stack.setCurrentWidget(self._panels[pid])

    def _on_close(self, idx: int):
        pid = self._bar.tabData(idx)
        if pid:
            self._panels[pid].hide_panel()

    def set_title(self, pid: str, title: str):
        for i in range(self._bar.count()):
            if self._bar.tabData(i) == pid:
                self._bar.setTabText(i, title)


# ── Sleep-overlay ─────────────────────────────────────────────────────────────

class _DropOverlay(QWidget):
    """Doorzichtige laag over het tegelgebied tijdens het slepen: ontvangt de
    drop en toont de doelzone (rand = ernaast, midden = tabblad)."""

    def __init__(self, area: "TileArea"):
        super().__init__(area)
        self._area = area
        self._hint: tuple[QRect, str, bool] | None = None
        self.setAcceptDrops(True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.hide()

    def _zone(self, pos: QPoint):
        target = self._area.leaf_at(pos)
        if target is None:
            return None
        key, rect = target
        fx = (pos.x() - rect.x()) / max(1, rect.width())
        fy = (pos.y() - rect.y()) / max(1, rect.height())
        d = {"left": fx, "right": 1 - fx, "top": fy, "bottom": 1 - fy}
        edge = min(d, key=d.get)
        zone = edge if d[edge] < _EDGE else "center"
        return key, rect, zone

    @staticmethod
    def _zone_rect(rect: QRect, zone: str) -> QRect:
        w, h = rect.width(), rect.height()
        if zone == "left":
            return QRect(rect.x(), rect.y(), w // 2, h)
        if zone == "right":
            return QRect(rect.x() + w // 2, rect.y(), w - w // 2, h)
        if zone == "top":
            return QRect(rect.x(), rect.y(), w, h // 2)
        if zone == "bottom":
            return QRect(rect.x(), rect.y() + h // 2, w, h - h // 2)
        return rect.adjusted(6, 6, -6, -6)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(PANEL_MIME):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if not event.mimeData().hasFormat(PANEL_MIME):
            event.ignore()
            return
        z = self._zone(event.position().toPoint())
        swap = bool(event.modifiers() & Qt.ControlModifier)
        self._hint = (self._zone_rect(z[1], z[2]), z[2], swap) if z else None
        self.update()
        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self._hint = None
        self.update()

    def dropEvent(self, event):
        pid = bytes(event.mimeData().data(PANEL_MIME)).decode("utf-8")
        z = self._zone(event.position().toPoint())
        swap = bool(event.modifiers() & Qt.ControlModifier)
        self._hint = None
        self.update()
        if z:
            self._area.drop_panel(pid, z[0], z[2], swap)
        event.acceptProposedAction()

    def paintEvent(self, event):
        if not self._hint:
            return
        rect, zone, swap = self._hint
        p = QPainter(self)
        c = QColor(ACCENT)
        c.setAlpha(60)
        p.fillRect(rect, c)
        p.setPen(QPen(QColor(ACCENT), 2, Qt.DashLine if zone == "center" else Qt.SolidLine))
        p.drawRect(rect.adjusted(1, 1, -1, -1))
        p.setPen(QColor(ACCENT))
        label = {"center": "⇄" if swap else "▭ +", "left": "◀", "right": "▶",
                 "top": "▲", "bottom": "▼"}[zone]
        f = p.font()
        f.setPointSize(18)
        f.setBold(True)
        p.setFont(f)
        p.drawText(rect, Qt.AlignCenter, label)


# ── Tegelgebied ───────────────────────────────────────────────────────────────

_SPLITTER_QSS = (
    f"QSplitter {{ background: {BG_ROOT}; }}"
    f"QSplitter::handle {{ background: {BG_ROOT}; }}"
    f"QSplitter::handle:hover {{ background: {ACCENT}; }}"
)
_SPLITTER_QSS_LOCKED = (
    f"QSplitter {{ background: {BG_ROOT}; }}"
    f"QSplitter::handle {{ background: {BG_ROOT}; }}"
)


class TileArea(QWidget):
    """Vult het desktop-canvas met een splitsingsboom van panelen/tabgroepen."""

    layout_changed = Signal()     # na slepen/wisselen (niet bij scheidingslijnen)

    def __init__(self, panels: dict, parent=None):
        super().__init__(parent)
        self._panels = panels                # pid → FloatingPanel
        self._root: QWidget | None = None
        self._groups: list[TabGroup] = []
        self._locked = False
        self._dragging: str | None = None
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(0)
        self.setStyleSheet(f"background: {BG_ROOT};")
        self._overlay = _DropOverlay(self)
        for p in panels.values():
            p.set_tiled(True, self)
            p.visibility_changed.connect(self._on_panel_visibility)
            p.title_changed.connect(self._on_panel_title)   # één keer; routeert naar tabgroep

    # ── opbouwen ─────────────────────────────────────────────────────────────
    def apply(self, tree: dict, visible: dict):
        """Bouw de boom op. Panelen die niet in de boom staan komen rechts erbij."""
        tree = prune_tree(copy.deepcopy(tree), self._panels) or {"p": next(iter(self._panels))}
        for pid in [p for p in self._panels if p not in _leaves(tree)]:
            tree = {"o": "h", "s": [0.85, 0.15], "c": [tree, {"p": pid}]}
        old = self._root
        # panelen eerst loskoppelen, zodat ze niet met de oude boom verdwijnen
        for p in self._panels.values():
            p.setParent(self)
            p.hide()
            p.set_in_tabs(False)
        if old is not None:
            self._lay.removeWidget(old)
            old.deleteLater()
        self._groups = []
        for pid, p in self._panels.items():
            p.set_panel_visible(visible.get(pid, True), notify=False)
        self._root = self._make(tree)
        self._lay.addWidget(self._root)
        for pid, p in self._panels.items():
            if not p._in_tabs:
                p.setVisible(p.is_panel_visible())
        for g in self._groups:
            g.sync()
        self._apply_lock()
        self._sync_containers()
        self._overlay.raise_()

    def _make(self, node) -> QWidget:
        if "p" in node:
            return self._panels[node["p"]]
        if "t" in node:
            g = TabGroup(node["t"], node.get("a"), self._panels)
            self._groups.append(g)
            return g
        sp = QSplitter(Qt.Horizontal if node["o"] == "h" else Qt.Vertical)
        sp.setHandleWidth(HANDLE_W)
        sp.setChildrenCollapsible(False)
        sp.setStyleSheet(_SPLITTER_QSS)
        for child in node["c"]:
            sp.addWidget(self._make(child))
        # Verhoudingen: QSplitter schaalt relatieve getallen naar de werkelijke ruimte
        sp.setSizes([max(1, int(r * 10000)) for r in node["s"]])
        sp._ratios = list(node["s"])          # onthouden voor verborgen kinderen
        return sp

    # ── uitlezen ─────────────────────────────────────────────────────────────
    def tree(self) -> dict:
        return self._tree_of(self._root) if self._root is not None else {}

    def _tree_of(self, w) -> dict:
        if isinstance(w, TabGroup):
            return {"t": w.pids(), "a": w.active()}
        if not isinstance(w, QSplitter):
            return {"p": w.panel_id}
        n = w.count()
        sizes = w.sizes()
        old = getattr(w, "_ratios", [1.0 / n] * n)
        vis = [self._node_visible(w.widget(i)) for i in range(n)]
        vis_total = sum(s for i, s in enumerate(sizes) if vis[i])
        old_vis = sum(old[i] for i in range(n) if vis[i]) or 1.0
        ratios = []
        for i in range(n):
            if vis[i] and vis_total > 0:
                # zichtbaar: huidige grootte, geschaald naar het oude aandeel van
                # de zichtbare kinderen (zo houden verborgen kinderen hun deel)
                ratios.append(sizes[i] / vis_total * old_vis)
            else:
                ratios.append(old[i])
        tot = sum(ratios) or 1.0
        ratios = [round(r / tot, 4) for r in ratios]
        w._ratios = ratios
        return {"o": "h" if w.orientation() == Qt.Horizontal else "v",
                "s": ratios, "c": [self._tree_of(w.widget(i)) for i in range(n)]}

    def rects(self) -> dict:
        """Paneelgeometrie in coördinaten van dit gebied (voor oude layouts)."""
        out = {}
        for pid, p in self._panels.items():
            if p.isVisible():
                out[pid] = QRect(p.mapTo(self, QPoint(0, 0)), p.size())
            else:
                out[pid] = p.geometry()
        return out

    def leaf_at(self, pos: QPoint):
        """(sleutel-paneel, rechthoek) van het zichtbare blad onder pos."""
        def walk(w):
            if not w.isVisible():
                return None
            r = QRect(w.mapTo(self, QPoint(0, 0)), w.size())
            if not r.contains(pos):
                return None
            if isinstance(w, TabGroup):
                return w.active(), r
            if isinstance(w, QSplitter):
                for i in range(w.count()):
                    hit = walk(w.widget(i))
                    if hit:
                        return hit
                return None
            return w.panel_id, r
        return walk(self._root) if self._root is not None else None

    # ── slepen ───────────────────────────────────────────────────────────────
    def is_locked(self) -> bool:
        return self._locked

    def set_locked(self, locked: bool):
        self._locked = bool(locked)
        self._apply_lock()

    def _apply_lock(self):
        def walk(w):
            if isinstance(w, QSplitter):
                w.setStyleSheet(_SPLITTER_QSS_LOCKED if self._locked else _SPLITTER_QSS)
                for i in range(w.count()):
                    h = w.handle(i)
                    if h is not None:
                        h.setEnabled(not self._locked)
                    walk(w.widget(i))
        if self._root is not None:
            walk(self._root)
        for p in self._panels.values():
            p.set_drag_enabled(not self._locked)

    def begin_drag(self, pid: str):
        self._dragging = pid
        self._overlay.setGeometry(self.rect())
        self._overlay.raise_()
        self._overlay.show()

    def end_drag(self):
        self._dragging = None
        self._overlay.hide()

    def drop_panel(self, pid: str, target: str, zone: str, swap: bool = False):
        """Verwerk een drop: pid naar target (rand/midden), of wisselen."""
        if pid not in self._panels:
            return
        # Op zichzelf neerzetten doet niets — behalve een tab uit de eigen groep
        # naar de rand slepen (dan wordt hij losgemaakt)
        if pid == target and (zone == "center" or not self._in_group_with_others(pid)):
            return
        tree = self.tree()
        visible = {p: w.is_panel_visible() for p, w in self._panels.items()}
        if swap and zone == "center" and target != pid:
            new = swap_panels(tree, pid, target)
        else:
            if target == pid:
                # uit de eigen tabgroep naar de rand: ander groepslid is het doel
                others = [p for p in self._group_of(pid) if p != pid]
                if not others:
                    return
                target = others[0]
            new = remove_panel(tree, pid)
            if new is None or target not in _leaves(new):
                return
            new = insert_panel(new, pid, target, zone)
        self.apply(new, visible)
        self.layout_changed.emit()

    def _group_of(self, pid: str) -> list[str]:
        for g in self._groups:
            if pid in g.pids():
                return g.pids()
        return [pid]

    def _in_group_with_others(self, pid: str) -> bool:
        return len(self._group_of(pid)) > 1

    # ── zichtbaarheid ────────────────────────────────────────────────────────
    def _node_visible(self, w) -> bool:
        if isinstance(w, TabGroup):
            return w.any_visible()
        if isinstance(w, QSplitter):
            return any(self._node_visible(w.widget(i)) for i in range(w.count()))
        return w.is_panel_visible()

    def _on_panel_title(self, pid: str, title: str):
        for g in self._groups:
            if pid in g.pids():
                g.set_title(pid, title)

    def _on_panel_visibility(self, pid: str, visible: bool):
        for g in self._groups:
            if pid in g.pids():
                g.sync(prefer=pid if visible else None)
        self._sync_containers()

    def _sync_containers(self):
        """Een splitsing of tabgroep zonder zichtbare panelen verbergt zichzelf,
        zodat de buren de ruimte krijgen; bij tonen komt ze op haar plek terug."""
        def walk(w) -> bool:
            if isinstance(w, TabGroup):
                vis = w.any_visible()
                w.setVisible(vis)
                return vis
            if not isinstance(w, QSplitter):
                return w.is_panel_visible()
            any_vis = False
            for i in range(w.count()):
                any_vis = walk(w.widget(i)) or any_vis
            w.setVisible(any_vis)
            return any_vis
        if self._root is not None:
            walk(self._root)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._overlay.setGeometry(self.rect())
