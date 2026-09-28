"""
HAMIOS — thema-designer

Stel een eigen palet samen (achtergronden, tekst, accent, statuskleuren en
lettergrootte) met een live voorbeeld. Het voorbeeld tekent met de ruwe
kleuren (theme_engine.raw_color), dus los van het thema dat nu actief is.
"""

from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QLabel, QPushButton, QComboBox, QLineEdit,
                               QDoubleSpinBox, QScrollArea, QWidget,
                               QColorDialog, QSizePolicy)

from . import theme_engine as E
from .i18n import tr
from .theme import BG_PANEL, TEXT_DIM

_GROUPS = [
    ("td.grp.bg",     ("BG_ROOT", "BG_PANEL", "BG_SURFACE", "BG_HOVER", "BORDER", "SELECT")),
    ("td.grp.text",   ("TEXT_H1", "TEXT_BODY", "TEXT_DIM")),
    ("td.grp.accent", ("ACCENT", "ACCENT_HI", "ACCENT_LO")),
    ("td.grp.status", ("GREEN", "YELLOW", "ORANGE", "RED", "BLUE", "DANGER_BG", "DANGER_HI")),
]


class _Swatch(QPushButton):
    """Kleurvlakje dat met de ruwe kleur getekend wordt."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hex = "#000000"
        self.setFixedSize(38, 20)
        self.setCursor(Qt.PointingHandCursor)

    def set_hex(self, h: str):
        self._hex = h
        self.update()

    def paintEvent(self, _ev):
        p = QPainter(self)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        p.setPen(QPen(E.raw_color("#808080"), 1))
        p.setBrush(E.raw_color(self._hex))
        p.drawRoundedRect(r, 3, 3)
        p.end()


class _Preview(QWidget):
    """Mini-HAMIOS: header, paneel met titelbalk, tekst, selectie, knoppen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pal = E.complete_palette(E.NIGHT)
        self.setMinimumSize(320, 380)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_palette(self, pal: dict):
        self.pal = pal
        self.update()

    def _font(self, pt: float, bold=False):
        f = E.raw_font("Segoe UI", pt * self.pal.get("font_scale", 1.0))
        f.setBold(bold)
        return f

    def paintEvent(self, _ev):
        c = lambda k: E.raw_color(self.pal[k])
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()
        p.fillRect(0, 0, W, H, c("BG_ROOT"))

        # Header
        p.fillRect(0, 0, W, 34, c("BG_PANEL"))
        p.fillRect(0, 33, W, 1, c("BORDER"))
        p.setFont(self._font(12, True))
        p.setPen(c("ACCENT"))
        p.drawText(QRectF(10, 0, W - 20, 34), Qt.AlignVCenter | Qt.AlignLeft, "HAMIOS")
        p.setFont(self._font(10, True))
        p.setPen(c("TEXT_H1"))
        p.drawText(QRectF(10, 0, W - 20, 34), Qt.AlignVCenter | Qt.AlignRight,
                   tr("td.pv.header").split("·")[-1].strip())

        # Paneel
        x, y, w, h = 10, 44, W - 20, H - 54
        p.setPen(QPen(c("BORDER"), 1))
        p.setBrush(c("BG_PANEL"))
        p.drawRect(QRectF(x + .5, y + .5, w - 1, h - 1))
        p.fillRect(x + 1, y + 1, w - 2, 24, c("BG_SURFACE"))
        p.setFont(self._font(9, True))
        p.setPen(c("ACCENT"))
        p.drawText(QRectF(x + 8, y, w - 16, 26), Qt.AlignVCenter, tr("td.pv.panel"))

        ty = y + 36
        for key, text, size, bold in (("TEXT_H1", tr("td.pv.title"), 10, True),
                                      ("TEXT_BODY", tr("td.pv.body"), 9, False),
                                      ("TEXT_DIM", tr("td.pv.dim"), 8, False)):
            p.setFont(self._font(size, bold))
            p.setPen(c(key))
            lh = p.fontMetrics().height()
            p.drawText(QRectF(x + 10, ty, w - 20, lh + 4), Qt.AlignVCenter, text)
            ty += lh + 6

        # Selectie-rij
        p.setFont(self._font(9))
        lh = p.fontMetrics().height() + 6
        p.fillRect(QRectF(x + 6, ty, w - 12, lh), c("SELECT"))
        p.setPen(c("TEXT_H1"))
        p.drawText(QRectF(x + 12, ty, w - 24, lh), Qt.AlignVCenter, tr("td.pv.select"))
        ty += lh + 10

        # Statuskleuren: balkjes + woorden
        keys = ("GREEN", "YELLOW", "ORANGE", "RED", "BLUE")
        words = [s.strip() for s in tr("td.pv.status").split("·")]
        bw = (w - 20) / len(keys)
        for i, k in enumerate(keys):
            bh = 14 + 10 * i
            p.fillRect(QRectF(x + 10 + i * bw + 3, ty + 44 - bh, bw - 6, bh), c(k))
        ty += 52
        p.setFont(self._font(8, True))
        for i, k in enumerate(keys):
            p.setPen(c(k))
            p.drawText(QRectF(x + 10 + i * bw, ty, bw, 18), Qt.AlignCenter,
                       words[i] if i < len(words) else "")
        ty += 30

        # Knoppen
        p.setFont(self._font(9, True))
        bh = p.fontMetrics().height() + 10
        specs = (("BG_SURFACE", "TEXT_H1", None, tr("td.pv.button")),
                 ("BG_HOVER", "TEXT_H1", None, tr("td.pv.button") + " ▸"),
                 ("ACCENT", "BG_ROOT", None, tr("td.pv.ok")),
                 ("DANGER_BG", "RED", "DANGER_HI", tr("td.pv.danger")))
        bx, gap = x + 10, 6
        bwid = (w - 20 - gap * 3) / 4
        for bg, fg, border, text in specs:
            r = QRectF(bx, ty, bwid, bh)
            p.setPen(QPen(c(border), 1) if border else Qt.NoPen)
            p.setBrush(c(bg))
            p.drawRoundedRect(r, 3, 3)
            p.setPen(c(fg))
            p.drawText(r, Qt.AlignCenter, text)
            bx += bwid + gap
        p.end()


class ThemeDesignerDialog(QDialog):
    """Bewerk een palet; saved(dict) bij Opslaan."""

    saved = Signal(dict)

    def __init__(self, palette: dict = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("td.title"))
        self.setMinimumSize(760, 560)
        self._pal = E.complete_palette(palette or E.ACTIVE_PALETTE)
        self._swatches, self._edits = {}, {}
        self._build()
        self._refresh()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        body = QHBoxLayout()
        outer.addLayout(body, 1)

        # ── Links: startpunt + kleuren + lettergrootte ───────────────────────
        left = QVBoxLayout()
        body.addLayout(left, 0)
        base_row = QHBoxLayout()
        base_row.addWidget(QLabel(tr("td.base")))
        self._base = QComboBox()
        for key in ("night", "day", "contrast"):
            self._base.addItem(tr(f"theme.{key}"), key)
        base_row.addWidget(self._base, 1)
        btn_load = QPushButton(tr("td.load"))
        btn_load.clicked.connect(self._load_base)
        base_row.addWidget(btn_load)
        left.addLayout(base_row)

        form_w = QWidget()
        form_w.setObjectName("tdform")
        form_w.setStyleSheet(f"QWidget#tdform {{ background: {BG_PANEL}; }}")
        grid = QGridLayout(form_w)
        grid.setContentsMargins(0, 4, 8, 4)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(3)
        row = 0
        for grp, keys in _GROUPS:
            hdr = QLabel(tr(grp))
            hdr.setObjectName("title")
            hdr.setStyleSheet("font-size: 10pt;")
            grid.addWidget(hdr, row, 0, 1, 3)
            row += 1
            for k in keys:
                grid.addWidget(QLabel(tr(f"td.tok.{k}")), row, 0)
                sw = _Swatch()
                sw.clicked.connect(lambda _=False, key=k: self._pick(key))
                grid.addWidget(sw, row, 1)
                ed = QLineEdit()
                ed.setFixedWidth(78)
                ed.setMaxLength(7)
                ed.editingFinished.connect(lambda key=k: self._hex_edited(key))
                grid.addWidget(ed, row, 2)
                self._swatches[k], self._edits[k] = sw, ed
                row += 1
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setWidget(form_w)
        scroll.setMinimumWidth(340)
        left.addWidget(scroll, 1)

        fs_row = QHBoxLayout()
        fs_row.addWidget(QLabel(tr("td.font_scale")))
        self._fs = QDoubleSpinBox()
        self._fs.setRange(0.8, 1.6)
        self._fs.setSingleStep(0.05)
        self._fs.setDecimals(2)
        self._fs.setSuffix(" ×")
        self._fs.valueChanged.connect(self._fs_changed)
        fs_row.addWidget(self._fs)
        fs_row.addStretch()
        left.addLayout(fs_row)

        # ── Rechts: voorbeeld + contrast ─────────────────────────────────────
        right = QVBoxLayout()
        body.addLayout(right, 1)
        pv_lbl = QLabel(tr("td.preview"))
        pv_lbl.setObjectName("title")
        right.addWidget(pv_lbl)
        self._preview = _Preview()
        right.addWidget(self._preview, 1)
        self._contrast = QLabel()
        self._contrast.setWordWrap(True)
        self._contrast.setStyleSheet(f"color: {TEXT_DIM};")
        right.addWidget(self._contrast)

        # ── Knoppen ──────────────────────────────────────────────────────────
        btns = QHBoxLayout()
        btns.addStretch()
        cancel = QPushButton(tr("app.cancel"))
        cancel.setObjectName("cancel")
        cancel.clicked.connect(self.reject)
        save = QPushButton(tr("td.save"))
        save.setObjectName("ok")
        save.clicked.connect(self._save)
        btns.addWidget(cancel)
        btns.addWidget(save)
        outer.addLayout(btns)

    # ── Acties ────────────────────────────────────────────────────────────────
    def _refresh(self):
        for k in E.TOKEN_KEYS:
            self._swatches[k].set_hex(self._pal[k])
            if not self._edits[k].hasFocus():
                self._edits[k].setText(self._pal[k])
        self._fs.blockSignals(True)
        self._fs.setValue(self._pal["font_scale"])
        self._fs.blockSignals(False)
        self._preview.set_palette(dict(self._pal))
        rgb = E._hex_to_rgb
        bg = rgb(self._pal["BG_PANEL"])
        cb = E.contrast(rgb(self._pal["TEXT_BODY"]), bg)
        cd = E.contrast(rgb(self._pal["TEXT_DIM"]), bg)
        txt = tr("td.contrast", body=f"{cb:.1f}:1", dim=f"{cd:.1f}:1")
        if cb < 4.5 or cd < 3.0:
            txt += "   " + tr("td.contrast_low")
        self._contrast.setText(txt)

    def _load_base(self):
        self._pal = E.complete_palette(E.PRESETS[self._base.currentData()])
        self._refresh()

    def _pick(self, key: str):
        col = QColorDialog.getColor(E.raw_color(self._pal[key]), self,
                                    tr("td.pick", name=tr(f"td.tok.{key}")))
        if col.isValid():
            self._pal[key] = col.name().upper()
            self._refresh()

    def _hex_edited(self, key: str):
        v = self._edits[key].text().strip()
        if not v.startswith("#"):
            v = "#" + v
        pal = E.complete_palette({**self._pal, key: v})
        self._pal = pal
        self._edits[key].setText(pal[key])
        self._refresh()

    def _fs_changed(self, v: float):
        self._pal["font_scale"] = round(v, 2)
        self._preview.set_palette(dict(self._pal))

    def _save(self):
        self.saved.emit(dict(self._pal))
        self.accept()

    def palette(self) -> dict:
        return dict(self._pal)
