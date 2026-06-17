"""HAMIOS v5 — Satelliet-selectie dialoog (PySide6) — v4 stijl

Kolommen: Satelliet | Positie | Pad | Footprint
Categorie-filter, uren-knoppen, Clear all, TLE vernieuwen.
"""

import threading

from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QProgressBar, QWidget, QFrame,
    QButtonGroup, QRadioButton, QCheckBox, QSpinBox, QSizePolicy,
    QAbstractItemView
)

from .theme import (
    ACCENT, BG_PANEL, BG_SURFACE, BG_ROOT, TEXT_H1, TEXT_DIM,
    TEXT_BODY, BORDER
)
from .geometry import save_geom, restore_geom
from .layers import TLE_GROUPS, fetch_tle_group, load_tle_cache, save_tle_cache, TleFetchThread
from .i18n import tr

_QSS = f"""
QDialog {{ background: {BG_PANEL}; }}
QTreeWidget {{
    background: {BG_SURFACE}; color: {TEXT_BODY};
    border: 1px solid {BORDER};
    alternate-background-color: {BG_ROOT};
    font-size: 8pt;
}}
QTreeWidget::item:selected  {{ background: #2A4060; }}
QTreeWidget::item           {{ height: 20px; }}
QHeaderView::section {{
    background: {BG_PANEL}; color: {ACCENT};
    border: none; padding: 3px; font-size: 8pt; font-weight: bold;
}}
QRadioButton {{ color: {TEXT_BODY}; spacing: 4px; font-size: 8pt; }}
QRadioButton::indicator {{ width: 12px; height: 12px; }}
QTreeWidget::indicator {{
    width: 14px;
    height: 14px;
    background: #000000;
    border: 1px solid #666666;
    border-radius: 1px;
}}
QTreeWidget::indicator:checked {{
    background: #C8A84B;
    border: 1px solid #A88A3A;
}}
QTreeWidget::indicator:hover {{
    border: 1px solid #888888;
}}
QTreeWidget::indicator:indeterminate {{
    background: {BG_SURFACE};
    border: 1px solid {BORDER};
}}
QLabel       {{ color: {TEXT_DIM}; font-size: 8pt; }}
QPushButton  {{
    background: {BG_SURFACE}; color: {TEXT_H1};
    border: none; padding: 3px 10px; border-radius: 2px;
}}
QPushButton:hover  {{ background: #32373F; }}
QPushButton#ok     {{ background: {ACCENT}; color: {BG_ROOT}; font-weight: bold; }}
QPushButton#ok:hover {{ background: #E0C060; }}
QPushButton#danger {{ background: #5A1010; }}
QProgressBar {{
    background: {BG_ROOT}; border: 1px solid {BORDER};
    height: 6px; border-radius: 3px;
}}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 3px; }}
"""

_COL_NAME = 0
_COL_POS  = 1
_COL_PATH = 2
_COL_FP   = 3



class SatelliteDialog(QDialog):
    """Satelliet-selectie dialoog — v4 stijl."""

    # Emitteert bij OK (volledige selectie)
    selection_changed = Signal(list, list, list, int, int)
    # Live signalen — direct toepassen bij elke wijziging
    hours_changed     = Signal(int, int)       # (back_h, fwd_h)
    live_pos_changed  = Signal(set)            # geselecteerde posities
    live_path_changed = Signal(set)            # geselecteerde paden
    live_fp_changed   = Signal(set)            # geselecteerde footprints

    def __init__(self, sat_selected: list, sat_path: list,
                 sat_fp: list = None, back_h: int = 1, fwd_h: int = 1,
                 filter_sel: bool = False, cfg=None, parent=None):
        super().__init__(parent)
        self._selected = set(sat_selected)
        self._path     = set(sat_path)
        self._fp       = set(sat_fp or [])
        self._back_h   = back_h
        self._fwd_h    = fwd_h
        self._cfg      = cfg          # voor auto-save bij sluiten
        self._tle_data: dict = {}
        self._cat_filter = tr("sat.filter.all")
        self.setWindowTitle(tr("sat.title"))
        self.setMinimumSize(580, 600)
        self.setStyleSheet(_QSS)
        self._build_ui()
        # Herstel filter-staat
        self._sel_toggle.setChecked(filter_sel)
        restore_geom(self, "SatelliteDialog")
        self._load_cache()

    # ── UI bouw ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(10, 10, 10, 10)
        v.setSpacing(6)

        f8b = QFont("Segoe UI", 8); f8b.setBold(True)
        f8  = QFont("Segoe UI", 8)

        # ── Status + TLE-refresh ──────────────────────────────────────────
        top = QHBoxLayout()
        self._status_lbl = QLabel(tr("sat.tle_loading"))
        self._status_lbl.setFont(f8)
        top.addWidget(self._status_lbl, 1)
        self._refresh_btn = QPushButton(tr("sat.tle_refresh"))
        self._refresh_btn.setFont(f8)
        self._refresh_btn.clicked.connect(self._refresh_tle)
        top.addWidget(self._refresh_btn)
        v.addLayout(top)

        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.hide()
        v.addWidget(self._progress)

        # ── Categorie-filter ──────────────────────────────────────────────
        cat_row = QHBoxLayout()
        cat_row.setSpacing(8)
        lbl_cat = QLabel(tr("sat.cat_lbl"))
        lbl_cat.setFont(f8)
        cat_row.addWidget(lbl_cat)
        self._cat_group = QButtonGroup(self)
        self._cat_btns: dict[str, QRadioButton] = {}
        for cat in [tr("sat.filter.all")] + sorted(TLE_GROUPS.keys()):
            rb = QRadioButton(cat)
            rb.setFont(f8)
            rb.setChecked(cat == tr("sat.filter.all"))
            # Gebruik toggled (betrouwbaar bij exclusieve QButtonGroup):
            # on=True alleen als deze knop net geselecteerd wordt
            rb.pressed.connect(lambda c=cat: self._set_cat(c))
            self._cat_group.addButton(rb)
            self._cat_btns[cat] = rb
            cat_row.addWidget(rb)
        cat_row.addStretch()
        # Vinkje: NIET in de exclusieve radiogroep — zelfstandig aan/uit
        self._sel_toggle = QCheckBox(tr("sat.filter.sel"))
        self._sel_toggle.setFont(f8)
        self._sel_toggle.setChecked(False)  # standaard: toon alle satellieten
        self._sel_toggle.setToolTip(tr("sat.sel_tip"))
        self._sel_toggle.toggled.connect(self._on_sel_toggle)
        cat_row.addWidget(self._sel_toggle)
        v.addLayout(cat_row)

        # ── Satelliet tabel ───────────────────────────────────────────────
        self._tree = QTreeWidget()
        self._tree.setColumnCount(4)
        self._tree.setHeaderLabels([tr("sat.col.name"), tr("sat.col.pos"), tr("sat.col.path"), tr("sat.col.fp")])
        self._tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        for col in (1, 2, 3):
            self._tree.header().setSectionResizeMode(col, QHeaderView.Fixed)
            self._tree.setColumnWidth(col, 68)
        self._tree.setAlternatingRowColors(True)
        self._tree.setUniformRowHeights(True)
        self._tree.setRootIsDecorated(True)
        self._tree.itemChanged.connect(self._on_item_changed)
        v.addWidget(self._tree, 1)

        # ── Uren-knoppen ──────────────────────────────────────────────────
        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background: {BORDER}; max-height: 1px;")
        v.addWidget(sep)

        hrs = QHBoxLayout()
        hrs.setSpacing(10)
        for lbl_txt, attr, spin_attr in [
            (tr("sat.back"), "_back_h", "_back_spin"),
            (tr("sat.fwd"),  "_fwd_h",  "_fwd_spin"),
        ]:
            hrs.addWidget(QLabel(lbl_txt))
            spin = QSpinBox()
            spin.setRange(0, 24)
            spin.setValue(getattr(self, attr))
            spin.setFixedWidth(56)
            setattr(self, spin_attr, spin)
            hrs.addWidget(spin)
        hrs.addStretch()
        v.addLayout(hrs)
        # Live toepassen bij wijziging
        self._back_spin.valueChanged.connect(self._on_hours_changed)
        self._fwd_spin.valueChanged.connect(self._on_hours_changed)

        # ── Knoppen onderaan ──────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_clear = QPushButton(tr("alerts.clear"))
        btn_clear.setFont(f8)
        btn_clear.setObjectName("danger")
        btn_clear.clicked.connect(self._clear_all)
        btn_row.addWidget(btn_clear)
        btn_row.addStretch()
        btn_ok     = QPushButton(tr("app.close_btn")); btn_ok.setObjectName("ok")
        btn_cancel = QPushButton(tr("app.cancel"));   btn_cancel.setObjectName("cancel")
        btn_ok.setFont(f8b)
        btn_cancel.setFont(f8)
        btn_ok.clicked.connect(self._on_ok)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        v.addLayout(btn_row)

    # ── TLE laden / vernieuwen ────────────────────────────────────────────────
    def _load_cache(self):
        cache = load_tle_cache()
        if cache:
            self._tle_data = cache
            self._populate_tree()
            n = sum(len(v) for v in cache.values())
            self._status_lbl.setText(tr("sat.cache_loaded", n=n))
        else:
            self._status_lbl.setText(tr("sat.tle_loading"))

    def _refresh_tle(self):
        self._refresh_btn.setEnabled(False)
        self._progress.show()
        t = TleFetchThread(self)
        t.progress.connect(self._status_lbl.setText)
        t.done.connect(self._on_tle_done)
        t.finished.connect(t.deleteLater)
        t.start()

    def _on_tle_done(self, cache: dict):
        self._tle_data = cache
        self._populate_tree()
        self._progress.hide()
        self._refresh_btn.setEnabled(True)
        n = sum(len(v) for v in cache.values())
        self._status_lbl.setText(f"{n} {tr('sat.tle_ok')}")

    # ── Boom bouwen ───────────────────────────────────────────────────────────
    def _on_sel_toggle(self, on: bool):
        """Toggle-knop: AAN = alleen geselecteerd, UIT = categorie-filter."""
        self._populate_tree()
        # Onmiddellijk opslaan zodat de staat bewaard blijft
        if self._cfg is not None:
            self._cfg.sat_filter_sel = on
            try:
                from .config import save_config
                save_config(self._cfg)
            except Exception:
                pass

    def _set_cat(self, cat: str):
        """Categorie-filter; schakelt de toggle-knop niet uit."""
        self._cat_filter = cat
        self._populate_tree()

    def _populate_tree(self):
        self._tree.blockSignals(True)
        self._tree.clear()

        f8b = QFont("Segoe UI", 8); f8b.setBold(True)
        f8  = QFont("Segoe UI", 8)

        show_sel_only = self._sel_toggle.isChecked()
        all_selected  = self._selected | self._path | self._fp

        for group, sats in sorted(self._tle_data.items()):
            # Categorie-filter (geldt ook in "Geselecteerd"-modus)
            if self._cat_filter != tr("sat.filter.all") and group != self._cat_filter:
                continue

            # Bepaal welke satellieten in deze groep zichtbaar zijn
            candidates = sorted(sats, key=lambda r: r[0] if isinstance(r, list) else r)
            if show_sel_only:
                candidates = [r for r in candidates
                              if (r[0] if isinstance(r, list) else r) in all_selected]
            if not candidates:
                continue   # groep overslaan — geen zichtbare items

            # Groep-header pas toevoegen nadat we weten dat er items zijn
            grp_item = QTreeWidgetItem([group])
            grp_item.setFont(0, f8b)
            grp_item.setForeground(0, QColor(ACCENT))
            grp_item.setFlags(grp_item.flags() & ~Qt.ItemIsSelectable)
            self._tree.addTopLevelItem(grp_item)

            for row in candidates:
                name = row[0] if isinstance(row, list) else row
                item = QTreeWidgetItem([""] * 4)
                item.setText(0, name)
                item.setFont(0, f8)
                item.setData(0, Qt.UserRole, name)

                cs_pos = Qt.Checked if name in self._selected else Qt.Unchecked
                item.setCheckState(_COL_POS, cs_pos)

                cs_path = Qt.Checked if name in self._path else Qt.Unchecked
                item.setCheckState(_COL_PATH, cs_path)

                if cs_pos == Qt.Unchecked:
                    item.setForeground(0, QColor(TEXT_DIM))

                cs_fp = Qt.Checked if name in self._fp else Qt.Unchecked
                item.setCheckState(_COL_FP, cs_fp)

                grp_item.addChild(item)

            grp_item.setExpanded(show_sel_only or group == "ISS")

        if show_sel_only and self._tree.topLevelItemCount() == 0:
            placeholder = QTreeWidgetItem(
                ["Geen satellieten geselecteerd — kies via 'Alle'"])
            placeholder.setForeground(0, QColor(TEXT_DIM))
            placeholder.setFlags(placeholder.flags() & ~Qt.ItemIsEnabled)
            self._tree.addTopLevelItem(placeholder)

        self._tree.blockSignals(False)

    def _on_item_changed(self, item: QTreeWidgetItem, col: int):
        name = item.data(0, Qt.UserRole)
        if not name:
            return
        self._tree.blockSignals(True)

        if col == _COL_POS:
            on = item.checkState(_COL_POS) == Qt.Checked
            if on:
                self._selected.add(name)
                item.setForeground(0, QColor(TEXT_BODY))
            else:
                self._selected.discard(name)
                self._path.discard(name)
                self._fp.discard(name)
                # Pad en footprint automatisch uitvinken
                item.setCheckState(_COL_PATH, Qt.Unchecked)
                item.setCheckState(_COL_FP,   Qt.Unchecked)
                item.setForeground(0, QColor(TEXT_DIM))

        elif col == _COL_PATH:
            if item.checkState(_COL_PATH) == Qt.Checked:
                if name not in self._selected:
                    item.setCheckState(_COL_PATH, Qt.Unchecked)
                else:
                    self._path.add(name)
            else:
                self._path.discard(name)

        elif col == _COL_FP:
            if item.checkState(_COL_FP) == Qt.Checked:
                if name not in self._selected:
                    item.setCheckState(_COL_FP, Qt.Unchecked)
                else:
                    self._fp.add(name)
            else:
                self._fp.discard(name)

        self._tree.blockSignals(False)
        # Direct live toepassen
        self.live_pos_changed.emit(set(self._selected))
        self.live_path_changed.emit(set(self._path))
        self.live_fp_changed.emit(set(self._fp))

    def _clear_all(self):
        self._selected.clear()
        self._path.clear()
        self._fp.clear()
        self._populate_tree()

    def _on_hours_changed(self):
        """Live toepassen van uren-wijziging."""
        self.hours_changed.emit(self._back_spin.value(), self._fwd_spin.value())

    # ── Selectie uitlezen ─────────────────────────────────────────────────────
    def _save_state(self):
        """Sla alle instellingen op in cfg — wordt aangeroepen bij OK én bij sluiten."""
        if self._cfg is None:
            return
        self._cfg.sat_selected   = list(self._selected)
        self._cfg.sat_path       = list(self._path)
        self._cfg.sat_fp         = list(self._fp)
        self._cfg.sat_back_h     = self._back_spin.value()
        self._cfg.sat_fwd_h      = self._fwd_spin.value()
        self._cfg.sat_filter_sel = self._sel_toggle.isChecked()
        try:
            from .config import save_config
            save_config(self._cfg)
        except Exception:
            pass

    def _on_ok(self):
        back_h = self._back_spin.value()
        fwd_h  = self._fwd_spin.value()
        self._save_state()   # sla filterstand op vóór accept()
        self.selection_changed.emit(
            list(self._selected), list(self._path),
            list(self._fp), back_h, fwd_h)
        self.accept()

    def done(self, result):
        save_geom(self, "SatelliteDialog")
        self._save_state()
        super().done(result)

    @property
    def tle_data(self) -> dict:
        return self._tle_data
