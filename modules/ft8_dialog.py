"""
HAMIOS v5 — Digitale modi frequentieoverzicht

Toont de standaard dial-frequenties (USB) voor FT8, FT4, WSPR, JS8Call,
MSK144, Q65 en verwante modi. Klik op een rij → CAT afstemmen.
Gebaseerd op WSJT-X standaardwaarden + IARU-aanbevelingen.
"""

from PySide6.QtCore import Qt, Signal, QSortFilterProxyModel, QTimer
from PySide6.QtGui import QFont, QColor, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableView, QHeaderView, QComboBox,
    QCheckBox
)

from .theme import ACCENT, BG_PANEL, BG_SURFACE, BG_ROOT, TEXT_H1, TEXT_DIM, TEXT_BODY, BORDER
from .geometry import save_geom, restore_geom
from .i18n import tr

# ── Frequentietabel ────────────────────────────────────────────────────────────
# (dial_khz, mode, band, regio, opmerkingen)

_FREQS = [
    # FT8 — standaard (bron: WSJT-X defaults + IARU)
    (1840.000,  "FT8",     "160m", "Wereld",  "Standaard 160m"),
    (3573.000,  "FT8",     "80m",  "Wereld",  "Standaard 80m"),
    (3568.000,  "FT8",     "80m",  "Japan",   "JA regio"),
    (5357.000,  "FT8",     "60m",  "USA/VK",  "5 MHz kanalen"),
    (7074.000,  "FT8",     "40m",  "Wereld",  "Standaard 40m"),
    (7056.000,  "FT8",     "40m",  "Europa",  "Alternatief EU"),
    (10136.000, "FT8",     "30m",  "Wereld",  "Standaard 30m"),
    (14074.000, "FT8",     "20m",  "Wereld",  "Standaard 20m"),
    (14090.000, "FT8",     "20m",  "Wereld",  "Alternatief / DX"),
    (18100.000, "FT8",     "17m",  "Wereld",  "Standaard 17m"),
    (21074.000, "FT8",     "15m",  "Wereld",  "Standaard 15m"),
    (21091.000, "FT8",     "15m",  "Wereld",  "Alternatief"),
    (24915.000, "FT8",     "12m",  "Wereld",  "Standaard 12m"),
    (28074.000, "FT8",     "10m",  "Wereld",  "Standaard 10m"),
    (28180.000, "FT8",     "10m",  "Wereld",  "Alternatief 10m"),
    (50313.000, "FT8",     "6m",   "Wereld",  "Standaard 6m"),
    (50323.000, "FT8",     "6m",   "Wereld",  "Alternatief 6m"),
    (70154.000, "FT8",     "4m",   "Europa",  "4m (EU)"),
    (144174.000,"FT8",     "2m",   "Wereld",  "Standaard 2m"),
    (432174.000,"FT8",     "70cm", "Wereld",  "Standaard 70cm"),
    (1296174.000,"FT8",    "23cm", "Wereld",  "Standaard 23cm"),

    # FT4
    (3575.000,  "FT4",     "80m",  "Wereld",  "Standaard 80m"),
    (7047.500,  "FT4",     "40m",  "Wereld",  "Standaard 40m"),
    (10140.000, "FT4",     "30m",  "Wereld",  "Standaard 30m"),
    (14080.000, "FT4",     "20m",  "Wereld",  "Standaard 20m"),
    (18104.000, "FT4",     "17m",  "Wereld",  "Standaard 17m"),
    (21140.000, "FT4",     "15m",  "Wereld",  "Standaard 15m"),
    (24919.000, "FT4",     "12m",  "Wereld",  "Standaard 12m"),
    (28180.000, "FT4",     "10m",  "Wereld",  "Standaard 10m"),
    (50318.000, "FT4",     "6m",   "Wereld",  "Standaard 6m"),
    (70132.000, "FT4",     "4m",   "Europa",  "4m (EU)"),
    (144170.000,"FT4",     "2m",   "Wereld",  "Standaard 2m"),

    # WSPR (dial USB)
    (136.000,   "WSPR",    "2200m","Wereld",  "LF"),
    (474.200,   "WSPR",    "630m", "Wereld",  "MF"),
    (1836.600,  "WSPR",    "160m", "Wereld",  "Standaard 160m"),
    (3568.600,  "WSPR",    "80m",  "Wereld",  "Standaard 80m"),
    (5287.200,  "WSPR",    "60m",  "Wereld",  "60m"),
    (7038.600,  "WSPR",    "40m",  "Wereld",  "Standaard 40m"),
    (10138.700, "WSPR",    "30m",  "Wereld",  "Standaard 30m"),
    (14095.600, "WSPR",    "20m",  "Wereld",  "Standaard 20m"),
    (18104.600, "WSPR",    "17m",  "Wereld",  "Standaard 17m"),
    (21094.600, "WSPR",    "15m",  "Wereld",  "Standaard 15m"),
    (24924.600, "WSPR",    "12m",  "Wereld",  "Standaard 12m"),
    (28124.600, "WSPR",    "10m",  "Wereld",  "Standaard 10m"),
    (50293.000, "WSPR",    "6m",   "Wereld",  "Standaard 6m"),
    (70091.000, "WSPR",    "4m",   "Europa",  "4m (EU)"),
    (144488.600,"WSPR",    "2m",   "Wereld",  "Standaard 2m"),

    # JS8Call
    (1842.000,  "JS8Call", "160m", "Wereld",  ""),
    (3578.000,  "JS8Call", "80m",  "Wereld",  ""),
    (7078.000,  "JS8Call", "40m",  "Wereld",  "Standaard 40m"),
    (10130.000, "JS8Call", "30m",  "Wereld",  ""),
    (14078.000, "JS8Call", "20m",  "Wereld",  "Standaard 20m"),
    (18104.000, "JS8Call", "17m",  "Wereld",  ""),
    (21078.000, "JS8Call", "15m",  "Wereld",  ""),
    (24922.000, "JS8Call", "12m",  "Wereld",  ""),
    (28078.000, "JS8Call", "10m",  "Wereld",  ""),
    (50318.000, "JS8Call", "6m",   "Wereld",  ""),

    # MSK144 (meteor scatter, 2m)
    (144360.000,"MSK144",  "2m",   "Wereld",  "Meteor scatter"),
    (432360.000,"MSK144",  "70cm", "Wereld",  "Meteor scatter"),

    # Q65 (EME / meteor scatter)
    (50275.000, "Q65",     "6m",   "Wereld",  "EME / scatter"),
    (144175.000,"Q65",     "2m",   "Wereld",  "EME standaard"),
    (144110.000,"Q65",     "2m",   "Wereld",  "EME alternatief"),
    (432100.000,"Q65",     "70cm", "Wereld",  "EME standaard"),
    (1296100.000,"Q65",    "23cm", "Wereld",  "EME standaard"),

    # JT65 (HF EME legacy)
    (14076.000, "JT65",    "20m",  "Wereld",  "HF legacy"),
    (21076.000, "JT65",    "15m",  "Wereld",  "HF legacy"),
    (7076.000,  "JT65",    "40m",  "Wereld",  "HF legacy"),

    # JT9
    (14078.000, "JT9",     "20m",  "Wereld",  "Naast JT65"),
    (7078.000,  "JT9",     "40m",  "Wereld",  "Naast JT65"),
    (10138.000, "JT9",     "30m",  "Wereld",  ""),
]

# Kolomkoppen
_COLS = ["kHz", "Mode", "Band", "Regio", "Opmerkingen"]

# Kleurcodering per mode
_MODE_COLORS = {
    "FT8":     "#C8A84B",   # amber
    "FT4":     "#4CAF50",   # groen
    "WSPR":    "#64B5F6",   # lichtblauw
    "JS8Call": "#FF8A65",   # oranje
    "MSK144":  "#CE93D8",   # lichtpaars
    "Q65":     "#80CBC4",   # teal
    "JT65":    "#A5D6A7",   # lichtgroen
    "JT9":     "#FFE082",   # geel
}

_QSS = f"""
QDialog   {{ background: {BG_PANEL}; }}
QTableView {{
    background: {BG_SURFACE}; color: {TEXT_BODY};
    border: 1px solid {BORDER}; alternate-background-color: {BG_ROOT};
    gridline-color: {BORDER}; font-size: 8pt;
}}
QTableView::item:selected {{ background: #2A4060; color: white; }}
QHeaderView::section {{
    background: {BG_PANEL}; color: {ACCENT};
    border: none; padding: 3px 6px;
    font-size: 8pt; font-weight: bold;
}}
QLineEdit, QComboBox {{
    background: {BG_ROOT}; color: {TEXT_H1};
    border: 1px solid {BORDER}; padding: 3px 6px; border-radius: 2px;
}}
QLineEdit:focus, QComboBox:focus {{ border-color: {ACCENT}; }}
QLabel    {{ color: {TEXT_DIM}; font-size: 8pt; }}
QPushButton {{
    background: {BG_SURFACE}; color: {TEXT_H1};
    border: 1px solid {BORDER}; padding: 3px 10px; border-radius: 2px;
}}
QPushButton:hover {{ background: #32373F; border-color: {ACCENT}; }}
"""

# Geordende bandlijst voor filter
_BANDS = ["Alle", "2200m", "630m", "160m", "80m", "60m", "40m", "30m",
          "20m", "17m", "15m", "12m", "10m", "6m", "4m", "2m", "70cm", "23cm"]
_MODES_FILTER = ["Alle", "FT8", "FT4", "WSPR", "JS8Call", "MSK144", "Q65", "JT65", "JT9"]


class Ft8Dialog(QDialog):
    """Overzicht digitale modi frequenties — doorzoekbaar, sorteerbaar, CAT-klikbaar."""

    freq_selected = Signal(int)   # Hz — voor CAT

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("ft8.title"))
        self.setMinimumSize(700, 500)
        self.resize(760, 560)
        self.setStyleSheet(_QSS)
        self._build_ui()
        self._populate()
        restore_geom(self, "Ft8Dialog")

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(10, 10, 10, 8)
        v.setSpacing(6)

        f8 = QFont("Segoe UI", 8)

        # ── Filterrij ─────────────────────────────────────────────────────────
        flt = QHBoxLayout(); flt.setSpacing(6)

        self._search = QLineEdit()
        self._search.setPlaceholderText(tr("ft8.search"))
        self._search.setFont(f8)
        self._search.textChanged.connect(self._apply_filter)
        flt.addWidget(self._search, 1)

        flt.addWidget(QLabel(tr("ft8.band_lbl")))
        self._band_cb = QComboBox(); self._band_cb.setFont(f8)
        self._band_cb.addItems(_BANDS)
        self._band_cb.setFixedWidth(72)
        self._band_cb.currentIndexChanged.connect(self._apply_filter)
        flt.addWidget(self._band_cb)

        flt.addWidget(QLabel(tr("ft8.mode_lbl")))
        self._mode_cb = QComboBox(); self._mode_cb.setFont(f8)
        self._mode_cb.addItems(_MODES_FILTER)
        self._mode_cb.setFixedWidth(90)
        self._mode_cb.currentIndexChanged.connect(self._apply_filter)
        flt.addWidget(self._mode_cb)

        self._usb_cb = QCheckBox(tr("ft8.usb_mode"))
        self._usb_cb.setFont(f8)
        self._usb_cb.setChecked(True)
        self._usb_cb.setToolTip(
            "Stel automatisch USB in op de radio bij het klikken op een frequentie.\n"
            "Alle digitale modi (FT8, FT4, WSPR, …) gebruiken USB als draaggolf.")
        flt.addWidget(self._usb_cb)

        v.addLayout(flt)

        # ── Legenda (kleurcodering) ────────────────────────────────────────────
        leg = QHBoxLayout(); leg.setSpacing(10)
        leg.addWidget(QLabel(tr("ft8.color_lbl")))
        for mode, color in _MODE_COLORS.items():
            dot = QLabel(f"⬤ {mode}")
            dot.setStyleSheet(f"color: {color}; font-size: 7pt; background: transparent;")
            leg.addWidget(dot)
        leg.addStretch()
        v.addLayout(leg)

        # ── Tabel ─────────────────────────────────────────────────────────────
        self._model = QStandardItemModel(0, len(_COLS))
        self._model.setHorizontalHeaderLabels([
            tr("ft8.col.freq"), tr("ft8.col.mode"), tr("ft8.col.band"),
            "Regio", tr("ft8.col.note"),
        ])

        self._proxy = QSortFilterProxyModel()
        self._proxy.setSourceModel(self._model)
        self._proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self._proxy.setFilterKeyColumn(-1)

        self._table = QTableView()
        self._table.setModel(self._proxy)
        self._table.setSortingEnabled(True)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableView.SelectRows)
        self._table.setEditTriggers(QTableView.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.verticalHeader().setDefaultSectionSize(20)
        self._table.setShowGrid(False)
        self._table.clicked.connect(self._on_row_clicked)

        hdr = self._table.horizontalHeader()
        hdr.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        hdr.setSectionResizeMode(0, QHeaderView.Fixed);   self._table.setColumnWidth(0, 110)
        hdr.setSectionResizeMode(1, QHeaderView.Fixed);   self._table.setColumnWidth(1, 80)
        hdr.setSectionResizeMode(2, QHeaderView.Fixed);   self._table.setColumnWidth(2, 58)
        hdr.setSectionResizeMode(3, QHeaderView.Fixed);   self._table.setColumnWidth(3, 80)
        hdr.setSectionResizeMode(4, QHeaderView.Stretch)
        self._table.sortByColumn(0, Qt.AscendingOrder)
        v.addWidget(self._table, 1)

        # ── Statusrij + sluiten ───────────────────────────────────────────────
        bot = QHBoxLayout(); bot.setSpacing(8)
        self._status_lbl = QLabel("")
        self._status_lbl.setFont(f8)
        bot.addWidget(self._status_lbl, 1)

        self._cat_lbl = QLabel("")
        self._cat_lbl.setFont(f8)
        bot.addWidget(self._cat_lbl)

        btn_close = QPushButton(tr("app.close_btn")); btn_close.setObjectName("close")
        btn_close.setFont(f8)
        btn_close.clicked.connect(self.accept)
        bot.addWidget(btn_close)
        v.addLayout(bot)

    # ── Data ──────────────────────────────────────────────────────────────────

    def _populate(self):
        self._apply_filter()

    def _apply_filter(self):
        q    = self._search.text().strip().lower()
        band = self._band_cb.currentText()
        mode = self._mode_cb.currentText()

        self._model.removeRows(0, self._model.rowCount())
        f_mono = QFont("Consolas", 8)
        f8     = QFont("Segoe UI", 8)

        count = 0
        for khz, m, b, reg, note in _FREQS:
            if band != "Alle" and b != band:
                continue
            if mode != "Alle" and m != mode:
                continue
            if q:
                haystack = f"{khz} {m} {b} {reg} {note}".lower()
                if q not in haystack:
                    continue

            color = QColor(_MODE_COLORS.get(m, TEXT_BODY))

            # kHz met 3 decimalen (Dutch: period=thousands, comma=decimal)
            khz_str = f"{khz:,.3f}".replace(',', 'X').replace('.', ',').replace('X', '.')

            items = [
                QStandardItem(khz_str),
                QStandardItem(m),
                QStandardItem(b),
                QStandardItem(reg),
                QStandardItem(note),
            ]
            items[0].setFont(f_mono)
            items[0].setData(khz, Qt.UserRole)   # numerieke waarde voor sorteren
            for it in items:
                it.setFont(f8 if it != items[0] else f_mono)
                it.setForeground(color)
            self._model.appendRow(items)
            count += 1

        total = len(_FREQS)
        self._status_lbl.setText(
            f"{count} van {total} frequenties  ·  klik op rij om CAT af te stemmen")
        self._status_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 8pt;")

    # ── CAT ───────────────────────────────────────────────────────────────────

    def _on_row_clicked(self, proxy_index):
        src = self._proxy.mapToSource(proxy_index)
        item = self._model.item(src.row(), 0)
        if not item:
            return
        khz = item.data(Qt.UserRole)
        if khz is None:
            return
        hz = int(round(khz * 1000))
        self.freq_selected.emit(hz)
        self._send_cat(hz, khz)

    def _send_cat(self, hz: int, khz: float):
        from .cat_interface import get_instance
        cat = get_instance()
        if cat is None:
            self._cat_status("📟  Geen CAT verbinding", "#EF5350")
            return

        # Stel frequentie in
        ok, msg = cat.set_freq_hz(hz)
        if not ok:
            if "geweigerd" in msg or "?" in msg:
                self._cat_status(f"📟  {khz:.0f} kHz geweigerd (buiten HAM-band?)", "#FFA726")
            else:
                self._cat_status(f"📟  {msg}", "#EF5350")
            QTimer.singleShot(4000, self._reset_cat_lbl)
            return

        # Stel modus in op USB (indien aangevinkt)
        mode_note = ""
        if self._usb_cb.isChecked():
            m_ok, m_msg = cat.set_mode("USB")
            mode_note = "  USB ✔" if m_ok else f"  (modus: {m_msg})"

        khz_str = f"{khz:,.3f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        self._cat_status(f"📟  CAT → {khz_str} kHz{mode_note}", "#4CAF50")
        QTimer.singleShot(4000, self._reset_cat_lbl)

    def _cat_status(self, txt: str, color: str):
        self._cat_lbl.setText(txt)
        self._cat_lbl.setStyleSheet(f"color: {color}; font-size: 8pt;")

    def _reset_cat_lbl(self):
        self._cat_lbl.setText("")

    def done(self, result):
        save_geom(self, "Ft8Dialog")
        super().done(result)
