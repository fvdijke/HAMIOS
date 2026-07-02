"""
HAMIOS v5 — EIBI Kortegolf-frequentielijst (PySide6)

Download automatisch de actuele EIBI-planning en toont deze als
doorzoekbare, sorteerbare tabel.

Bron: http://www.eibispace.de/
"""

import csv
import datetime
import io
import json
import os
import urllib.request

from PySide6.QtCore import Qt, QThread, Signal, QSortFilterProxyModel, QTimer, QModelIndex
from PySide6.QtGui import QFont, QColor, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableView, QHeaderView, QProgressBar,
    QComboBox, QCheckBox
)

from .theme import ACCENT, BG_PANEL, BG_SURFACE, BG_ROOT, TEXT_H1, TEXT_DIM, TEXT_BODY, BORDER
from .eibi_codes import enrich_row
from .geometry import save_geom, restore_geom
from .i18n import tr
from .resources_config import get_eibi_url

from ._appdir import APP_DIR as _HERE
_CACHE_FILE = os.path.join(_HERE, "config", "hamios_eibi.csv")
_META_FILE  = os.path.join(_HERE, "config", "hamios_eibi_meta.json")


def _load_cache() -> list[dict]:
    """Laad EIBI uit lokale cache."""
    if not os.path.exists(_CACHE_FILE):
        return []
    rows = []
    try:
        with open(_CACHE_FILE, encoding="latin-1") as f:
            reader = csv.reader(f, delimiter=";")
            for row in reader:
                if len(row) >= 5:
                    rows.append(row)
    except Exception:
        pass
    return rows


def _load_meta() -> dict:
    try:
        with open(_META_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_meta(meta: dict):
    try:
        with open(_META_FILE, "w", encoding="utf-8") as f:
            json.dump(meta, f)
    except Exception:
        pass


# ── Downloadthread ────────────────────────────────────────────────────────────

class _EibiDownloadThread(QThread):
    progress = Signal(str)
    done     = Signal(list)   # list of rows (list of str)
    error    = Signal(str)

    def run(self):
        try:
            url = get_eibi_url()
            self.progress.emit(f"Downloaden: {url} …")
            req = urllib.request.Request(url, headers={"User-Agent": "HAMIOS/5.5"})
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read().decode("latin-1", errors="replace")
            self.progress.emit("Verwerken …")

            # Opslaan in cache
            with open(_CACHE_FILE, "w", encoding="latin-1") as f:
                f.write(raw)

            # Sla meta (tijdstip, URL) op
            _save_meta({
                "updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "url": url,
            })

            # Parseer
            rows = []
            reader = csv.reader(io.StringIO(raw), delimiter=";")
            for row in reader:
                if len(row) >= 5:
                    rows.append(row)
            self.done.emit(rows)
        except Exception as e:
            self.error.emit(str(e))


# ── Numerieke proxy (sorteert kHz-kolom als float) ───────────────────────────

class _EibiSortProxy(QSortFilterProxyModel):
    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        if left.column() == 0:
            try:
                return float(left.data() or 0) < float(right.data() or 0)
            except (ValueError, TypeError):
                pass
        return super().lessThan(left, right)


# ── Dialoog ───────────────────────────────────────────────────────────────────

_COL_HEADERS = ["kHz", "Station", "Tijd (UTC)", "Dagen", "Land",
                 "Taal", "Doelgebied", "Opmerkingen"]
_COL_WIDTHS  = [72, 200, 95, 60, 45, 45, 80, 160]

# Mapping display-kolom → CSV-kolom (0=kHz,1=Tijd,2=Dagen,3=Land,4=Station,5=Taal,6=Doel,7=Opm)
_DISPLAY_ORDER = [0, 4, 1, 2, 3, 5, 6, 7]

_QSS = f"""
QDialog   {{ background: {BG_PANEL}; }}
QTableView {{
    background: {BG_SURFACE}; color: {TEXT_BODY};
    border: 1px solid {BORDER}; alternate-background-color: {BG_ROOT};
    gridline-color: {BORDER}; font-size: 8pt;
}}
QTableView::item:selected {{ background: #2A4060; }}
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
QCheckBox {{ color: {TEXT_H1}; spacing: 4px; }}
QLabel    {{ color: {TEXT_DIM}; font-size: 8pt; }}
QPushButton {{
    background: {BG_SURFACE}; color: {TEXT_H1};
    border: 1px solid {BORDER}; padding: 3px 10px; border-radius: 2px;
}}
QPushButton:hover {{ background: #32373F; border-color: {ACCENT}; }}
QPushButton#dl {{ background: {ACCENT}; color: {BG_ROOT}; font-weight: bold; }}
QPushButton#dl:hover {{ background: #E0C060; }}
QProgressBar {{
    background: {BG_ROOT}; border: 1px solid {BORDER};
    height: 5px; border-radius: 2px;
}}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 2px; }}
"""


class EibiDialog(QDialog):
    """EIBI kortegolf-frequentielijst — doorzoekbaar en sorteerbaar."""

    freq_selected = Signal(int)   # Hz — emitted bij klik op rij (voor CAT)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_rows: list[list[str]] = []
        self.setWindowTitle(tr("eibi.title"))
        self.setMinimumSize(920, 600)
        self.setStyleSheet(_QSS)
        self._build_ui()
        restore_geom(self, "EibiDialog")
        self._load_from_cache()

    # ── UI bouw ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(10, 10, 10, 8)
        v.setSpacing(6)

        f8 = QFont("Segoe UI", 8)

        # ── Filterrij ─────────────────────────────────────────────────────────
        flt = QHBoxLayout(); flt.setSpacing(6)

        self._search = QLineEdit()
        self._search.setPlaceholderText(tr("eibi.search"))
        self._search.setFont(f8)
        self._search.textChanged.connect(self._apply_filter)
        flt.addWidget(self._search, 1)

        flt.addWidget(QLabel(tr("eibi.band_lbl")))
        self._band_cb = QComboBox(); self._band_cb.setFont(f8)
        self._band_cb.addItems([
            "Alle", "LF/MF (< 1600 kHz)", "60m (4–5 MHz)",
            "49m (5.7–6.3 MHz)", "41m (7.1–7.5 MHz)",
            "31m (9.3–10 MHz)", "25m (11.5–12.2 MHz)",
            "22m (13.5–13.9 MHz)", "19m (15.1–15.8 MHz)",
            "16m (17.4–17.9 MHz)", "15m (18.9–19.0 MHz)",
            "13m (21.4–21.9 MHz)", "11m (25.6–26.1 MHz)",
        ])
        self._band_cb.currentIndexChanged.connect(self._apply_filter)
        self._band_cb.setFixedWidth(160)
        flt.addWidget(self._band_cb)

        self._now_cb = QCheckBox(tr("eibi.now_active"))
        self._now_cb.setFont(f8)
        self._now_cb.toggled.connect(self._apply_filter)
        flt.addWidget(self._now_cb)

        self._translate_cb = QCheckBox(tr("eibi.full_names"))
        self._translate_cb.setFont(f8)
        self._translate_cb.setChecked(True)
        self._translate_cb.setToolTip(
            "Vertaal taal- en doelgebied-codes naar volledige namen.\n"
            "De originele EIBI-data wordt niet gewijzigd.")
        self._translate_cb.toggled.connect(self._apply_filter)
        flt.addWidget(self._translate_cb)

        self._am_cb = QCheckBox(tr("eibi.am_cb"))
        self._am_cb.setFont(f8)
        self._am_cb.setChecked(True)
        self._am_cb.setToolTip(
            "Stel automatisch AM in op de radio bij het klikken op een frequentie.\n"
            "Kortegolf-omroepen zenden uit in AM (Amplitude Modulatie).")
        flt.addWidget(self._am_cb)

        v.addLayout(flt)

        # ── Tabel ─────────────────────────────────────────────────────────────
        self._model = QStandardItemModel(0, len(_COL_HEADERS))
        self._model.setHorizontalHeaderLabels([
            tr("eibi.col.freq"), tr("eibi.col.station"), tr("eibi.col.time"), "Dagen",
            "Land", tr("eibi.col.lang"), tr("eibi.col.target"), "Opmerkingen",
        ])

        self._proxy = _EibiSortProxy()
        self._proxy.setSourceModel(self._model)
        self._proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self._proxy.setFilterKeyColumn(-1)   # zoek in alle kolommen

        self._table = QTableView()
        self._table.setModel(self._proxy)
        self._table.setSortingEnabled(True)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableView.SelectRows)
        self._table.setEditTriggers(QTableView.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.verticalHeader().setDefaultSectionSize(18)
        self._table.setShowGrid(False)
        self._table.clicked.connect(self._on_row_clicked)

        hdr = self._table.horizontalHeader()
        # Kolomkoppen links uitlijnen
        hdr.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        # Kolommen interactief (gebruiker kan breedte aanpassen)
        for i in range(len(_COL_HEADERS)):
            hdr.setSectionResizeMode(i, QHeaderView.Interactive)
        # Laatste kolom vult de rest
        hdr.setStretchLastSection(True)
        # Na laden data kolombreedte aanpassen (zie _resize_columns)
        v.addWidget(self._table, 1)

        # ── Statusrij + knoppen ───────────────────────────────────────────────
        bot = QHBoxLayout(); bot.setSpacing(8)
        self._status_lbl = QLabel(tr("eibi.status.loading"))
        bot.addWidget(self._status_lbl, 1)
        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.setFixedWidth(100)
        self._progress.hide()
        bot.addWidget(self._progress)
        btn_dl = QPushButton(tr("eibi.update")); btn_dl.setObjectName("dl")
        btn_dl.setFont(f8)
        btn_dl.clicked.connect(self._download)
        bot.addWidget(btn_dl)
        btn_close = QPushButton(tr("app.close_btn")); btn_close.setObjectName("close")
        btn_close.setFont(f8)
        btn_close.clicked.connect(self.accept)
        bot.addWidget(btn_close)
        v.addLayout(bot)

    # ── Data laden ────────────────────────────────────────────────────────────
    def _load_from_cache(self):
        rows = _load_cache()
        if rows:
            meta = _load_meta()
            upd  = meta.get("updated", "onbekend")
            self._populate(rows)
            self._status_lbl.setText(
                f"{len(rows):,} frequenties  ·  bijgewerkt {upd}  ·  "
                f"Bron: eibispace.de")
        else:
            self._status_lbl.setText(tr("eibi.status.no_cache"))

    def _download(self):
        self._progress.show()
        self._status_lbl.setText(tr("eibi.status.dl"))
        t = _EibiDownloadThread(self)
        t.progress.connect(self._status_lbl.setText)
        t.done.connect(self._on_downloaded)
        t.error.connect(lambda e: (
            self._status_lbl.setText(f"Fout: {e}"),
            self._progress.hide()))
        t.finished.connect(t.deleteLater)
        t.start()

    def _on_downloaded(self, rows: list):
        self._progress.hide()
        meta = _load_meta()
        upd  = meta.get("updated", "zojuist")
        self._populate(rows)
        self._status_lbl.setText(
            f"{len(rows):,} frequenties  ·  bijgewerkt {upd}  ·  "
            f"Bron: eibispace.de")

    def _resize_columns(self):
        """Pas kolombreedtes aan op inhoud (max 300px per kolom)."""
        hdr = self._table.horizontalHeader()
        for i in range(self._model.columnCount() - 1):  # niet laatste (stretch)
            hdr.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self._table.resizeColumnsToContents()
        # Zet terug op Interactive zodat gebruiker kan aanpassen
        for i in range(self._model.columnCount() - 1):
            w = self._table.columnWidth(i)
            hdr.setSectionResizeMode(i, QHeaderView.Interactive)
            self._table.setColumnWidth(i, min(w, 320))

    def _populate(self, rows: list):
        self._all_rows = rows
        self._apply_filter()
        self._resize_columns()
        self._table.sortByColumn(0, Qt.AscendingOrder)

    # ── Filteren ──────────────────────────────────────────────────────────────
    def _apply_filter(self):
        q         = self._search.text().strip().lower()
        band      = self._band_cb.currentText()
        now       = self._now_cb.isChecked()
        translate = self._translate_cb.isChecked()

        self._model.removeRows(0, self._model.rowCount())
        f_mono = QFont("Consolas", 8)
        f8     = QFont("Segoe UI", 8)

        now_utc = datetime.datetime.now(datetime.timezone.utc)
        now_min = now_utc.hour * 100 + now_utc.minute

        _BAND_RANGES = {
            "LF/MF (< 1600 kHz)":    (0,       1600),
            "60m (4–5 MHz)":          (4000,    5000),
            "49m (5.7–6.3 MHz)":      (5700,    6300),
            "41m (7.1–7.5 MHz)":      (7100,    7500),
            "31m (9.3–10 MHz)":       (9300,   10000),
            "25m (11.5–12.2 MHz)":    (11500,  12200),
            "22m (13.5–13.9 MHz)":    (13500,  13900),
            "19m (15.1–15.8 MHz)":    (15100,  15800),
            "16m (17.4–17.9 MHz)":    (17400,  17900),
            "15m (18.9–19.0 MHz)":    (18900,  19000),
            "13m (21.4–21.9 MHz)":    (21400,  21900),
            "11m (25.6–26.1 MHz)":    (25600,  26100),
        }
        freq_range = _BAND_RANGES.get(band)

        for row in self._all_rows:
            fields = (row + [""] * 8)[:8]
            kHz_str = fields[0].strip()
            time_str = fields[1].strip()    # "0600-0800"

            # Band-filter
            if freq_range:
                try:
                    f = float(kHz_str)
                    if not (freq_range[0] <= f < freq_range[1]):
                        continue
                except (ValueError, TypeError):
                    continue

            # Tijdfilter
            if now:
                try:
                    start, end = time_str.split("-")
                    s = int(start); e = int(end)
                    if e < s:  # over middernacht
                        active = now_min >= s or now_min < e
                    else:
                        active = s <= now_min < e
                    if not active:
                        continue
                except (ValueError, TypeError, AttributeError):
                    pass

            # Tekstfilter
            if q:
                combined = " ".join(f.lower() for f in fields)
                if q not in combined:
                    continue

            # Vertalingen berekenen (originele data onaangetast)
            tr = enrich_row(row)
            lang_full   = tr["lang_full"]
            target_full = tr["target_full"]
            itu_full    = tr["itu_full"]

            items = []
            for csv_j in _DISPLAY_ORDER:
                raw_val = fields[csv_j].strip()

                # Vertaalde weergave voor Land (csv 3), Taal (csv 5), Doelgebied (csv 6)
                if translate and csv_j == 3 and itu_full:
                    display = f"{raw_val} – {itu_full}"
                elif translate and csv_j == 5 and lang_full:
                    display = f"{raw_val} – {lang_full}"
                elif translate and csv_j == 6 and target_full:
                    display = f"{raw_val} – {target_full}"
                else:
                    display = raw_val

                item = QStandardItem(display)
                item.setFont(f_mono if csv_j == 0 else f8)
                item.setForeground(QColor(TEXT_BODY))

                # Tooltip: altijd de volledige naam, ook als niet vertaald
                if csv_j == 3 and itu_full:
                    item.setToolTip(itu_full)
                elif csv_j == 5 and lang_full:
                    item.setToolTip(lang_full)
                elif csv_j == 6 and target_full:
                    item.setToolTip(target_full)

                items.append(item)
            self._model.appendRow(items)

        n = self._model.rowCount()
        self._status_lbl.setText(
            f"{n:,} van {len(self._all_rows):,} frequenties  ·  "
            f"Bron: eibispace.de")

    def _on_row_clicked(self, proxy_index):
        """Emitteer freq_selected (Hz) bij klik en stuur naar CAT als verbonden."""
        src_index = self._proxy.mapToSource(proxy_index)
        item = self._model.item(src_index.row(), 0)  # kolom 0 = kHz
        if not item:
            return
        try:
            khz = float(item.text().split()[0].replace(",", "."))
            hz  = int(khz * 1000)
            self.freq_selected.emit(hz)
            self._cat_feedback(hz, khz)
        except (ValueError, TypeError):
            pass

    def _cat_feedback(self, hz: int, khz: float):
        """Stuur frequentie (en optioneel AM-modus) naar radio via CAT."""
        from .cat_interface import get_instance
        cat = get_instance()
        if cat is None:
            return

        ok, msg = cat.set_freq_hz(hz)
        if not ok:
            if "geweigerd" in msg or "?" in msg:
                self._status_lbl.setText(
                    f"📟  {khz:.0f} kHz geweigerd door radio  "
                    f"(buiten bereik of CAT niet actief)")
                self._status_lbl.setStyleSheet(f"color: #FFA726; font-size: 8pt;")
            else:
                self._status_lbl.setText(f"📟  CAT fout: {msg}")
                self._status_lbl.setStyleSheet(f"color: #EF5350; font-size: 8pt;")
            QTimer.singleShot(5000, self._reset_status)
            return

        # Stel modus in op AM (indien aangevinkt)
        mode_note = ""
        if self._am_cb.isChecked():
            m_ok, m_msg = cat.set_mode("AM")
            mode_note = "  AM ✔" if m_ok else f"  (modus: {m_msg})"

        self._status_lbl.setText(f"📟  CAT → {khz:.3f} kHz{mode_note}")
        self._status_lbl.setStyleSheet(f"color: #4CAF50; font-size: 8pt;")
        QTimer.singleShot(5000, self._reset_status)

    def _reset_status(self):
        n = self._model.rowCount()
        self._status_lbl.setText(
            f"{n:,} van {len(self._all_rows):,} frequenties  ·  Bron: eibispace.de")
        self._status_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 8pt;")

    def done(self, result):
        """Overschrijf done() — wordt aangeroepen door accept(), reject() én X-knop."""
        save_geom(self, "EibiDialog")
        super().done(result)
