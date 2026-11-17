"""
HAMIOS — Watchlist: gezochte stations en landen in het DX-cluster.

Een regel in de lijst kan zijn:
  • een roepnaam           VP8PJ        (precies die roepnaam, ook als VP8PJ/P)
  • een prefix (≤ 4 tekens) 3Y, VK9      (roepnamen die zo beginnen)
  • een land (cty.dat)      Bouvet       (deel van de DXCC-naam, ≥ 4 letters)

Wordt een gezocht station gespot, dan volgt een melding — standaard alleen
als de band op het pad QTH → dat land volgens het model open is (≥ 50 %),
want een spot van een gesloten band levert niets op. Per roepnaam en band
hooguit één melding per 30 minuten.
"""

from __future__ import annotations

import time

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QCheckBox, QHBoxLayout, QLabel, QLineEdit, QListWidget,
                               QPushButton, QVBoxLayout, QWidget)

from .extra_panels import _item, _table
from .i18n import tr
from .theme import BG_SURFACE, TEXT_BODY, TEXT_DIM, TEXT_H1

REPEAT_S = 30 * 60
OPEN_PCT = 50


def _norm(entry: str) -> str:
    return " ".join((entry or "").strip().upper().split())


def matches(call: str, entry: str) -> bool:
    """Valt roepnaam `call` onder watchlist-regel `entry`?"""
    from .cty import _base_call, lookup
    e, c = _norm(entry), (call or "").strip().upper()
    if not e or not c:
        return False
    base = _base_call(c)
    if c == e or base == e or c.split("/")[0] == e:
        return True
    if len(e) <= 4 and " " not in e and base.startswith(e):
        return True
    ent = lookup(c)
    if ent is not None:
        if e == ent.prefix.upper():
            return True
        if len(e) >= 4 and not any(ch.isdigit() for ch in e) and e in ent.name.upper():
            return True
    return False


def find_hits(spots: list, entries: list, qth, snr_db: float = 0.0, engine=None) -> list[dict]:
    """Spots die op de watchlist staan, met de modelkans op hun pad."""
    from .cty import lookup
    from .layers import _call_to_latlon
    from .propagation import ENGINE
    eng = engine or ENGINE
    entries = [_norm(e) for e in entries if _norm(e)]
    out, cache = [], {}
    for s in spots:
        call = str(s.get("dx", ""))
        entry = next((e for e in entries if matches(call, e)), None)
        if entry is None:
            continue
        pos = _call_to_latlon(call)
        band = s.get("band", "")
        pct = None
        if pos is not None:
            key = (round(pos[0], 1), round(pos[1], 1))
            if key not in cache:
                cache[key] = eng.path_band_pct(qth[0], qth[1], pos[0], pos[1], None, snr_db)
            pct = cache[key].get(band)
        ent = lookup(call)
        out.append({"call": call, "entry": entry, "band": band,
                    "khz": float(s.get("freq_khz", 0) or 0), "time": s.get("time", ""),
                    "spotter": s.get("spotter", ""), "comment": s.get("comment", ""),
                    "entity": ent.name if ent else "", "pos": pos, "pct": pct})
    return out


class WatchlistWidget(QWidget):
    """Paneel 'Watchlist'."""

    hit = Signal(dict)                   # nieuwe melding (zie find_hits)
    path_requested = Signal(float, float, str)
    tune_requested = Signal(int, str)    # Hz, mode

    def __init__(self, cfg=None, parent=None, save=None):
        super().__init__(parent)
        self._cfg = cfg
        self._save = save                # callable: config opslaan
        self._spots: list = []
        self._hits: list = []
        self._alerted: dict = {}         # (call, band) → tijd
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 4, 6, 4)
        lay.setSpacing(4)

        row = QHBoxLayout()
        self._edit = QLineEdit()
        self._edit.setPlaceholderText(tr("watch.placeholder"))
        self._edit.setToolTip(tr("watch.tip"))
        self._edit.returnPressed.connect(self._add)
        row.addWidget(self._edit, 1)
        add = QPushButton(tr("watch.add"))
        add.clicked.connect(self._add)
        row.addWidget(add)
        rem = QPushButton(tr("watch.remove"))
        rem.clicked.connect(self._remove)
        row.addWidget(rem)
        lay.addLayout(row)

        self._list = QListWidget()
        self._list.setMaximumHeight(80)
        self._list.setStyleSheet(
            f"QListWidget {{ background: {BG_SURFACE}; color: {TEXT_BODY}; border: none;"
            f" font-size: 8pt; }}")
        lay.addWidget(self._list)

        self._open_cb = QCheckBox(tr("watch.open_only"))
        self._open_cb.toggled.connect(self._on_open_only)
        lay.addWidget(self._open_cb)

        self._status = QLabel("")
        self._status.setStyleSheet(f"color: {TEXT_DIM}; font-size: 8pt;")
        lay.addWidget(self._status)
        self._tbl = _table([tr("watch.col.call"), tr("watch.col.band"), "kHz",
                            tr("watch.col.entity"), tr("watch.col.path"), tr("watch.col.time")],
                           stretch=3)
        self._tbl.setToolTip(tr("watch.table_tip"))
        self._tbl.cellClicked.connect(self._on_click)
        self._tbl.cellDoubleClicked.connect(self._on_double)
        lay.addWidget(self._tbl, 1)
        self.set_cfg(cfg)

    # ── configuratie ────────────────────────────────────────────────────────
    def set_cfg(self, cfg):
        self._cfg = cfg
        self._list.clear()
        for e in (getattr(cfg, "watchlist", []) or []):
            self._list.addItem(str(e))
        self._open_cb.blockSignals(True)
        self._open_cb.setChecked(bool(getattr(cfg, "watch_open_only", True)))
        self._open_cb.blockSignals(False)
        self._evaluate(alert=False)

    def _entries(self) -> list:
        return [self._list.item(i).text() for i in range(self._list.count())]

    def _store(self):
        if self._cfg is not None:
            self._cfg.watchlist = self._entries()
            self._cfg.watch_open_only = self._open_cb.isChecked()
            if self._save:
                self._save()

    def _add(self):
        e = _norm(self._edit.text())
        if e and e not in self._entries():
            self._list.addItem(e)
            self._store()
            self._evaluate(alert=False)     # wat er nu al staat: geen meldingenregen
        self._edit.clear()

    def _remove(self):
        for it in self._list.selectedItems():
            self._list.takeItem(self._list.row(it))
        self._store()
        self._evaluate(alert=False)

    def _on_open_only(self, _on):
        self._store()
        self._evaluate(alert=False)

    # ── spots ───────────────────────────────────────────────────────────────
    def set_spots(self, spots: list):
        self._spots = list(spots or [])
        self._evaluate(alert=True)

    def _evaluate(self, alert: bool):
        from .panels5 import _station_snr
        entries = self._entries()
        if not entries or self._cfg is None:
            self._hits = []
            self._render()
            return
        qth = (self._cfg.qth_lat, self._cfg.qth_lon)
        self._hits = find_hits(self._spots, entries, qth, _station_snr(self._cfg))
        self._render()
        if not alert:
            for h in self._hits:              # huidige stand = al gemeld
                self._alerted[(h["call"], h["band"])] = time.time()
            return
        now = time.time()
        self._alerted = {k: t for k, t in self._alerted.items() if now - t < REPEAT_S}
        open_only = self._open_cb.isChecked()
        for h in self._hits:
            key = (h["call"], h["band"])
            if key in self._alerted:
                continue
            if open_only and (h["pct"] is None or h["pct"] < OPEN_PCT):
                continue
            self._alerted[key] = now
            self.hit.emit(h)

    def _render(self):
        n = len(self._hits)
        self._status.setText(tr("watch.status", n=n, m=self._list.count()))
        self._tbl.setRowCount(n)
        for i, h in enumerate(self._hits):
            pct = h["pct"]
            col = (TEXT_DIM if pct is None else "#66BB6A" if pct >= OPEN_PCT
                   else "#FFA726" if pct >= 20 else "#EF5350")
            self._tbl.setItem(i, 0, _item(h["call"], TEXT_H1, bold=True))
            self._tbl.setItem(i, 1, _item(h["band"]))
            self._tbl.setItem(i, 2, _item(f"{h['khz']:.1f}", align=Qt.AlignRight))
            self._tbl.setItem(i, 3, _item(h["entity"] or h["entry"], TEXT_BODY))
            self._tbl.setItem(i, 4, _item("—" if pct is None else f"{pct}%", col,
                                          align=Qt.AlignRight))
            self._tbl.setItem(i, 5, _item(h["time"], TEXT_DIM))

    def _on_click(self, row, _col):
        if 0 <= row < len(self._hits) and self._hits[row]["pos"]:
            h = self._hits[row]
            self.path_requested.emit(h["pos"][0], h["pos"][1], f"{h['call']} · {h['band']}")

    def _on_double(self, row, _col):
        if 0 <= row < len(self._hits) and self._hits[row]["khz"]:
            h = self._hits[row]
            mode = "CW" if "CW" in h["comment"].upper() else (
                "FT8" if "FT8" in h["comment"].upper() else "SSB")
            self.tune_requested.emit(int(round(h["khz"] * 1000)), mode)
