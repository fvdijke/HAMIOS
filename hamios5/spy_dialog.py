"""HAMIOS v5 — SpyStations dialoog (PySide6) — vergelijkbaar met v4"""

import json
import os

from PySide6.QtCore import Qt, QSortFilterProxyModel, QTimer
from PySide6.QtGui import QFont, QColor, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QTreeWidget, QTreeWidgetItem, QHeaderView,
    QPushButton, QFrame, QTextEdit, QSplitter, QWidget, QScrollArea
)

from .theme import ACCENT, BG_PANEL, BG_SURFACE, BG_ROOT, TEXT_H1, TEXT_DIM, TEXT_BODY, BORDER
from .geometry import save_geom, restore_geom

from ._appdir import APP_DIR as _HERE
_SPY_FILE = os.path.join(_HERE, "hamios_spy_stations.json")

_DEFAULTS = [
    {"name": "UVB-76 (The Buzzer)", "country": "Rusland",
     "frequencies": ["4625 kHz"], "mode": "AM/USB", "active": True,
     "schedule": "Continu 24/7.",
     "info": "Continu brom-toon, af en toe onderbroken door Russische spraakberichten."},
    {"name": "M14a (The Pip)", "country": "Rusland",
     "frequencies": ["3756 kHz", "5448 kHz"], "mode": "USB", "active": True,
     "schedule": "Continu 24/7.",
     "info": "Korte 'pip'-toon elke twee seconden. Russisch militair."},
    {"name": "V24 / Atencion", "country": "Cuba",
     "frequencies": ["7887 kHz", "9955 kHz"], "mode": "AM/USB", "active": True,
     "schedule": "Di/Do/Za 21:30 UTC.",
     "info": "Cubaanse inlichtingendienst (DGI). Spaanstalige 5-cijferige groepen."},
    {"name": "HM01", "country": "Noord-Korea",
     "frequencies": ["6400 kHz", "9100 kHz"], "mode": "AM", "active": True,
     "schedule": "Ma/Wo/Vr 00:00 UTC.",
     "info": "Koreaanse vrouwenstem met nummers, voorafgegaan door muziek."},
    {"name": "M12a (Lincolnshire Poacher)", "country": "Verenigd Koninkrijk",
     "frequencies": ["5765 kHz", "11545 kHz"], "mode": "AM/USB", "active": False,
     "schedule": "Gestopt ca. 2008.",
     "info": "Muziekintro, gevolgd door 5-cijferige Engelse nummers. GCHQ/MI6."},
    {"name": "M03 (Russian Man)", "country": "Rusland",
     "frequencies": ["4583 kHz", "6998 kHz"], "mode": "USB", "active": True,
     "schedule": "Onregelmatig 04:00-08:00 UTC.",
     "info": "Russische mannenstem met 5-cijferige groepen. Vermoedelijk FSB/SVR."},
    {"name": "4XZ (Israëlische marine)", "country": "Israël",
     "frequencies": ["5810 kHz", "8137 kHz", "12157 kHz"], "mode": "CW",
     "active": True, "schedule": "Continu 24/7.",
     "info": "IDF Marine seinstation. Morse-code navigatieberichten."},
    {"name": "RDL (Russische marine)", "country": "Rusland",
     "frequencies": ["12649 kHz", "16432 kHz"], "mode": "CW", "active": True,
     "schedule": "Dagelijks 08:00-10:00 UTC.",
     "info": "Russisch marineseinstation. Verbonden met onderzeebootoperaties."},
]

_QSS = f"""
QDialog   {{ background: {BG_PANEL}; }}
QTreeWidget {{
    background: {BG_SURFACE}; color: {TEXT_BODY};
    border: 1px solid {BORDER}; alternate-background-color: {BG_ROOT};
    font-size: 8pt;
}}
QTreeWidget::item:selected {{ background: #2A4060; }}
QHeaderView::section {{
    background: {BG_PANEL}; color: {ACCENT};
    border: none; padding: 3px; font-size: 8pt; font-weight: bold;
}}
QLineEdit, QComboBox {{
    background: {BG_ROOT}; color: {TEXT_H1};
    border: 1px solid {BORDER}; padding: 3px 6px; border-radius: 2px;
}}
QTextEdit {{
    background: {BG_SURFACE}; color: {TEXT_BODY};
    border: 1px solid {BORDER}; font-size: 8pt;
}}
QLabel   {{ color: {TEXT_DIM}; font-size: 8pt; }}
QPushButton {{
    background: {BG_SURFACE}; color: {TEXT_H1};
    border: 1px solid {BORDER}; padding: 3px 10px; border-radius: 2px;
}}
QPushButton:hover {{ background: #32373F; }}
QPushButton#close {{ background: {ACCENT}; color: {BG_ROOT}; font-weight: bold; }}
"""


def _load_stations() -> list:
    if not os.path.exists(_SPY_FILE):
        try:
            with open(_SPY_FILE, "w", encoding="utf-8") as f:
                json.dump(_DEFAULTS, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        return list(_DEFAULTS)
    try:
        with open(_SPY_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return list(_DEFAULTS)


class SpyStationsDialog(QDialog):
    """SpyStations — overzicht van nummerstations en spy-uitzendingen."""

    _SORT_KEYS = {"●": "active", "Naam": "name", "Land": "country",
                  "Freq.": "freq", "Mode": "mode"}

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stations  = _load_stations()
        self._sort_col  = "Naam"
        self._sort_asc  = True
        self.setWindowTitle("🕵  SpyStations — HAMIOS v5")
        self.setMinimumSize(700, 520)
        self.setStyleSheet(_QSS)
        self._build_ui()
        self._refresh()
        restore_geom(self, "SpyStationsDialog")

    def _build_ui(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(10, 10, 10, 8)
        v.setSpacing(6)

        f8 = QFont("Segoe UI", 8)

        # Filterrij
        flt = QHBoxLayout()
        flt.setSpacing(8)
        self._search = QLineEdit()
        self._search.setPlaceholderText("Zoeken op naam, land of frequentie…")
        self._search.setFont(f8)
        self._search.textChanged.connect(self._refresh)
        flt.addWidget(self._search, 1)

        self._filter_cb = QComboBox()
        self._filter_cb.setFont(f8)
        self._filter_cb.addItems(["Alle", "Actief", "Inactief"])
        self._filter_cb.currentTextChanged.connect(self._refresh)
        flt.addWidget(self._filter_cb)
        v.addLayout(flt)

        # Splitter: tabel boven, details onder
        splitter = QSplitter(Qt.Vertical)

        # Tabel
        self._tree = QTreeWidget()
        self._tree.setColumnCount(5)
        self._tree.setHeaderLabels(["●", "Naam", "Land", "Freq.", "Mode"])
        hdr = self._tree.header()
        hdr.setSectionResizeMode(0, QHeaderView.Fixed);  self._tree.setColumnWidth(0, 24)
        hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.Fixed);  self._tree.setColumnWidth(2, 130)
        hdr.setSectionResizeMode(3, QHeaderView.Fixed);  self._tree.setColumnWidth(3, 160)
        hdr.setSectionResizeMode(4, QHeaderView.Fixed);  self._tree.setColumnWidth(4, 70)
        self._tree.setAlternatingRowColors(True)
        self._tree.setRootIsDecorated(False)
        hdr.setSectionsClickable(True)
        self._tree.itemClicked.connect(self._on_click)
        self._tree.header().sectionClicked.connect(self._on_header_click)
        splitter.addWidget(self._tree)

        # Detail-tekstvak
        self._detail = QTextEdit()
        self._detail.setReadOnly(True)
        self._detail.setMaximumHeight(120)
        splitter.addWidget(self._detail)
        splitter.setSizes([380, 110])
        v.addWidget(splitter, 1)

        # Statusregel + sluiten
        bot = QHBoxLayout()
        self._status_lbl = QLabel("")
        bot.addWidget(self._status_lbl)
        bot.addStretch()
        self._cat_lbl = QLabel("")
        self._cat_lbl.setStyleSheet(f"color: #4CAF50; font-size: 8pt;")
        bot.addWidget(self._cat_lbl)
        btn_close = QPushButton("Sluiten"); btn_close.setObjectName("close")
        btn_close.clicked.connect(self.accept)
        bot.addWidget(btn_close)
        v.addLayout(bot)

    def _filtered(self) -> list:
        q    = self._search.text().lower().strip()
        show = self._filter_cb.currentText()
        out  = []
        for s in self._stations:
            active = s.get("active", False)
            if show == "Actief"   and not active: continue
            if show == "Inactief" and active:     continue
            if q and not (
                q in s.get("name",    "").lower() or
                q in s.get("country", "").lower() or
                any(q in f.lower() for f in s.get("frequencies", []))
            ):
                continue
            out.append(s)
        key = self._sort_col
        rev = not self._sort_asc
        if key == "●":
            out.sort(key=lambda s: 0 if s.get("active") else 1, reverse=rev)
        elif key == "Freq.":
            out.sort(key=lambda s: s.get("frequencies", [""])[0], reverse=rev)
        elif key == "Mode":
            out.sort(key=lambda s: s.get("mode", ""), reverse=rev)
        else:
            col = {"Naam": "name", "Land": "country"}.get(key, "name")
            out.sort(key=lambda s: s.get(col, "").lower(), reverse=rev)
        return out

    def _refresh(self, *_):
        stations = self._filtered()
        self._tree.clear()
        f8b = QFont("Consolas", 8)
        for s in stations:
            active = s.get("active", False)
            dot    = "●" if active else "○"
            clr    = QColor("#4CAF50") if active else QColor(TEXT_DIM)
            freq   = "  ".join(s.get("frequencies", []))
            item   = QTreeWidgetItem(["", s.get("name",""), s.get("country",""),
                                      freq, s.get("mode","")])
            item.setText(0, dot)
            item.setForeground(0, clr)
            item.setData(0, Qt.UserRole, s)
            item.setFont(3, f8b)
            self._tree.addTopLevelItem(item)
        n = len(stations)
        t = len(self._stations)
        self._status_lbl.setText(f"{n} van {t} stations")
        # Sorteerindicatoren in kolomkoppen
        labels = ["●", "Naam", "Land", "Freq.", "Mode"]
        arrow  = " ↑" if self._sort_asc else " ↓"
        for i, lbl in enumerate(labels):
            self._tree.headerItem().setText(
                i, lbl + arrow if lbl == self._sort_col else lbl)

    def _on_click(self, item: QTreeWidgetItem, col: int):
        s = item.data(0, Qt.UserRole)
        if not s:
            return
        active = "🟢 Actief" if s.get("active") else "🔴 Inactief"
        freqs  = s.get("frequencies", [])
        sched  = s.get("schedule", "—")
        info   = s.get("info", "")
        mode   = s.get("mode", "—")

        # Bouw detail-HTML + CAT-knoppen
        html = (
            f"<b style='color:{ACCENT}'>{s.get('name','')}</b>"
            f"&nbsp;&nbsp;<span style='color:#888'>{active}</span><br>"
            f"<span style='color:{TEXT_DIM}'>Land:</span> {s.get('country','—')}"
            f"&nbsp;&nbsp;<span style='color:{TEXT_DIM}'>Mode:</span> {mode}<br>"
            f"<span style='color:{TEXT_DIM}'>Schema:</span> {sched}<br><br>"
            f"{info}")
        self._detail.setHtml(html)

        # CAT-knoppen per frequentie in de statusbalk-rij
        self._cat_lbl.setText("")
        # Verwijder oude freq-knoppen
        if hasattr(self, "_freq_btns_widget") and self._freq_btns_widget:
            self._freq_btns_widget.setParent(None)
        f8 = QFont("Consolas", 8)
        w = QWidget()
        row = QHBoxLayout(w); row.setContentsMargins(0,0,0,0); row.setSpacing(4)
        row.addWidget(QLabel("CAT →"))
        for freq_str in freqs:
            btn = QPushButton(freq_str)
            btn.setFont(f8)
            btn.setFixedHeight(20)
            btn.setToolTip(f"Stem radio af op {freq_str}")
            btn.clicked.connect(
                lambda _=0, fs=freq_str, m=mode: self._send_cat(fs, m))
            row.addWidget(btn)
        row.addStretch()
        self._freq_btns_widget = w
        # Voeg in aan de layout net boven de statusbalk
        self.layout().insertWidget(self.layout().count() - 1, w)

    def _send_cat(self, freq_str: str, mode_str: str):
        """Stuur frequentie + modus naar radio via CAT."""
        from .cat_interface import get_instance
        cat = get_instance()
        if cat is None:
            self._cat_lbl.setText("Geen CAT")
            self._cat_lbl.setStyleSheet("color: #EF5350; font-size: 8pt;")
            return
        # Parseer "4625 kHz" → Hz
        try:
            khz = float(freq_str.lower().replace("khz","").replace("mhz","").strip())
            if "mhz" in freq_str.lower():
                khz *= 1000
            hz = int(khz * 1000)
        except ValueError:
            self._cat_lbl.setText(f"Ongeldige freq: {freq_str}")
            return
        ok, msg = cat.set_freq_hz(hz)
        if ok:
            # Stel modus in op basis van mode_str
            cat_mode = "USB"
            m = mode_str.upper()
            if "AM" in m:   cat_mode = "AM"
            elif "CW" in m: cat_mode = "CW"
            elif "FM" in m: cat_mode = "FM"
            cat.set_mode(cat_mode)
            self._cat_lbl.setText(f"✔  {freq_str}  {cat_mode}")
            self._cat_lbl.setStyleSheet("color: #4CAF50; font-size: 8pt;")
        else:
            self._cat_lbl.setText(f"✘  {msg[:40]}")
            self._cat_lbl.setStyleSheet("color: #EF5350; font-size: 8pt;")
        QTimer.singleShot(4000, lambda: self._cat_lbl.setText(""))

    def _on_header_click(self, col: int):
        labels = ["●", "Naam", "Land", "Freq.", "Mode"]
        if col < len(labels):
            lbl = labels[col]
            if lbl == self._sort_col:
                self._sort_asc = not self._sort_asc
            else:
                self._sort_col = lbl
                self._sort_asc = True
            self._refresh()

    def closeEvent(self, event):
        save_geom(self, "SpyStationsDialog")
        super().closeEvent(event)
