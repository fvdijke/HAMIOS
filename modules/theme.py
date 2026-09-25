"""
HAMIOS v5 — Thema & kleurconstanten (PySide6)
Gebaseerd op de Midnight-stijl van v4.
"""
import os as _os
import tempfile as _tmp

# Tijdelijke pijl-images worden bij app-start aangemaakt
_ARROW_UP_PATH   = _os.path.join(_tmp.gettempdir(), "config/hamios_arrow_up.png")
_ARROW_DOWN_PATH = _os.path.join(_tmp.gettempdir(), "config/hamios_arrow_dn.png")

_CHECKMARK_PATH = _os.path.join(_tmp.gettempdir(), "config/hamios_checkmark.png")


class CheckBox:
    """QCheckBox with text-based checkmarks (like splash screen)."""
    @staticmethod
    def format_text(label: str, checked: bool) -> str:
        """Format checkbox text with checkmark symbol."""
        symbol = "✓ " if checked else "○ "
        return symbol + label


def create_checkbox(text: str) -> object:
    """Create a QCheckBox with text-based checkmark indicator.

    Usage: checkbox = create_checkbox("My Option")
    The checkbox will show "○ My Option" when unchecked and "✓ My Option" when checked.
    """
    from PySide6.QtWidgets import QCheckBox

    class TextCheckBox(QCheckBox):
        def __init__(self, label: str):
            super().__init__(CheckBox.format_text(label, False))
            self._label = label
            self.toggled.connect(self._update_text)

        def _update_text(self, checked: bool):
            super().setText(CheckBox.format_text(self._label, checked))

    return TextCheckBox(text)


def make_checkmark_path() -> str:
    """Generate amber checkmark indicator (14x14). Returns file path."""
    from PySide6.QtGui import QPixmap, QPainter, QColor, QFont
    from PySide6.QtCore import Qt

    # Create 14x14 transparent pixmap
    pix = QPixmap(14, 14)
    pix.fill(Qt.transparent)

    # Draw checkmark using text - simpler and more reliable
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)

    # Draw amber checkmark character
    font = QFont("Arial", 11, QFont.Bold)
    p.setFont(font)
    p.setPen(QColor(ACCENT))  # Amber color
    p.drawText(pix.rect(), Qt.AlignCenter, "✓")

    p.end()
    pix.save(_CHECKMARK_PATH, "PNG")
    return _CHECKMARK_PATH.replace("\\", "/")


def generate_spinbox_arrows():
    """Genereer kleine pijl-PNG's voor QSpinBox na QApplication-start."""
    from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QPolygon
    from PySide6.QtCore import Qt, QPoint

    def _arrow(path: str, up: bool):
        pix = QPixmap(10, 6)
        pix.fill(QColor(0, 0, 0, 0))
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing)
        clr = QColor(TEXT_H1)
        pen = QPen(clr, 1.6)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        p.setBrush(clr)
        if up:
            tri = QPolygon([QPoint(1, 5), QPoint(5, 1), QPoint(9, 5)])
        else:
            tri = QPolygon([QPoint(1, 1), QPoint(5, 5), QPoint(9, 1)])
        p.drawPolyline(tri)
        p.end()
        pix.save(path, "PNG")

    _arrow(_ARROW_UP_PATH,   True)
    _arrow(_ARROW_DOWN_PATH, False)
    # Vervang backslashes voor Qt
    up   = _ARROW_UP_PATH.replace("\\", "/")
    down = _ARROW_DOWN_PATH.replace("\\", "/")
    return up, down

# Kleuren (hex strings voor Qt stylesheets)
BG_ROOT    = "#1A1C1F"
BG_PANEL   = "#22252A"
BG_SURFACE = "#2A2E35"
BG_HOVER   = "#32373F"
ACCENT     = "#C8A84B"
TEXT_H1    = "#F0E6C8"
TEXT_BODY  = "#B0B8C4"
TEXT_DIM   = "#606870"
BORDER     = "#383E47"

# ── Checkbox-vakjes: zwart vakje, amber rand + amber V als aangevinkt ────────
# Als PNG's getekend (4× resolutie → scherp bij elke schermschaal); QSS verwijst
# ernaar. Tekenen op een QImage werkt al vóór de QApplication bestaat.
_CHECK_DIR = _os.path.join(_tmp.gettempdir(), "hamios_ui")


def _make_check_images() -> dict:
    from PySide6.QtCore import QPointF, QRectF, Qt
    from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath, QPen

    S = 56
    os_ok = True
    try:
        _os.makedirs(_CHECK_DIR, exist_ok=True)
    except OSError:
        os_ok = False

    def draw(name, border, mark=None, mark_color=ACCENT):
        img = QImage(S, S, QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        p = QPainter(img)
        p.setRenderHint(QPainter.Antialiasing)
        bw = S * 0.07
        p.setPen(QPen(QColor(border), bw))
        p.setBrush(QColor("#000000"))
        p.drawRoundedRect(QRectF(bw / 2, bw / 2, S - bw, S - bw), S * 0.08, S * 0.08)
        if mark:
            p.setPen(QPen(QColor(mark_color), S * 0.13, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.setBrush(Qt.NoBrush)
            path = QPainterPath()
            if mark == "v":
                path.moveTo(QPointF(S * .22, S * .52))
                path.lineTo(QPointF(S * .42, S * .72))
                path.lineTo(QPointF(S * .78, S * .28))
            else:   # "-" : deels aangevinkt
                path.moveTo(QPointF(S * .28, S * .50))
                path.lineTo(QPointF(S * .72, S * .50))
            p.drawPath(path)
        p.end()
        path = _os.path.join(_CHECK_DIR, f"check_{name}.png")
        if os_ok:
            img.save(path, "PNG")
        return path.replace("\\", "/")

    def chevron(name, colour):
        img = QImage(S, S, QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        p = QPainter(img)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor(colour), S * 0.13, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        path = QPainterPath()
        path.moveTo(QPointF(S * .18, S * .36))
        path.lineTo(QPointF(S * .50, S * .66))
        path.lineTo(QPointF(S * .82, S * .36))
        p.drawPath(path)
        p.end()
        path_s = _os.path.join(_CHECK_DIR, f"chevron_{name}.png")
        if os_ok:
            img.save(path_s, "PNG")
        return path_s.replace("\\", "/")

    return {
        "arrow":      chevron("down", "#C8C8D0"),
        "arrow_on":   chevron("down_on", ACCENT),
        "arrow_dis":  chevron("down_dis", "#555555"),
        "off":       draw("off",       "#666666"),
        "off_hover": draw("off_hover", ACCENT),
        "on":        draw("on",        ACCENT, "v"),
        "part":      draw("part",      ACCENT, "-"),
        "off_dis":   draw("off_dis",   "#3A3A3A"),
        "on_dis":    draw("on_dis",    "#4A4A4A", "v", "#6A6A6A"),
    }


try:
    CHECK_IMG = _make_check_images()
except Exception:   # zonder Qt-GUI (bv. tests): QSS verwijst naar niet-bestaande bestanden
    CHECK_IMG = {k: "" for k in ("off", "off_hover", "on", "part", "off_dis", "on_dis",
                                 "arrow", "arrow_on", "arrow_dis")}


def check_indicator_qss(selector: str) -> str:
    """QSS voor de ::indicator van een checkbox-achtige widget (stijl 3)."""
    i = CHECK_IMG
    return f"""
{selector}::indicator {{ width: 14px; height: 14px; border: none; background: transparent; image: url("{i['off']}"); }}
{selector}::indicator:hover {{ image: url("{i['off_hover']}"); }}
{selector}::indicator:checked {{ image: url("{i['on']}"); }}
{selector}::indicator:indeterminate {{ image: url("{i['part']}"); }}
{selector}::indicator:disabled {{ image: url("{i['off_dis']}"); }}
{selector}::indicator:checked:disabled {{ image: url("{i['on_dis']}"); }}
"""


# Afmetingen
HDR_H      = 42     # header hoogte in pixels
PANEL_GRID = 10     # snap-raster
TITLE_H    = 26     # paneel-titelbalk hoogte

# Globaal Qt stylesheet
QSS = f"""
* {{
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 9pt;
    color: {TEXT_BODY};
}}
QMainWindow, QWidget#desktop {{
    background-color: {BG_ROOT};
}}
QWidget#header {{
    background-color: {BG_PANEL};
    border-bottom: 1px solid {BORDER};
}}
QPushButton {{
    background-color: {BG_SURFACE};
    color: {TEXT_H1};
    border: none;
    padding: 3px 10px;
    border-radius: 2px;
}}
QPushButton:hover {{
    background-color: {BG_HOVER};
}}
QPushButton#accent {{
    color: {ACCENT};
}}
QPushButton#exit {{
    background-color: #5A1010;
    color: {TEXT_H1};
}}
QPushButton#exit:hover {{
    background-color: #8B1A1A;
}}
/* Standaard dialoog-knoppen */
QPushButton#ok, QPushButton#close, QPushButton#send, QPushButton#dl,
QPushButton#connect {{
    background-color: {ACCENT};
    color: {BG_ROOT};
    font-weight: bold;
    border: none;
    padding: 4px 14px;
    border-radius: 3px;
}}
QPushButton#ok:hover, QPushButton#close:hover, QPushButton#send:hover,
QPushButton#dl:hover, QPushButton#connect:hover {{
    background-color: #E0C060;
}}
QPushButton#cancel {{
    background-color: {BG_PANEL};
    color: {TEXT_DIM};
    border: 1px solid {BORDER};
    padding: 4px 14px;
    border-radius: 3px;
}}
QPushButton#cancel:hover {{
    background-color: #32373F;
    color: {TEXT_H1};
}}
QPushButton#danger, QPushButton#disconnect {{
    background-color: #5A1010;
    color: #EF5350;
    border: 1px solid #8B1A1A;
    padding: 4px 14px;
    border-radius: 3px;
}}
QPushButton#danger:hover, QPushButton#disconnect:hover {{
    background-color: #8B1A1A;
    color: white;
}}
QLabel {{
    background: transparent;
}}
QLabel#title {{
    color: {ACCENT};
    font-size: 13pt;
    font-weight: bold;
}}
QLabel#time_local {{
    color: {TEXT_H1};
    font-size: 10pt;
    font-weight: bold;
}}
QLabel#time_utc {{
    color: {TEXT_DIM};
    font-size: 10pt;
}}
/* Global simple spinbox styling for all dialogs and panels */
QSpinBox, QDoubleSpinBox {{
    background: {BG_ROOT};
    color: {TEXT_H1};
    border: 1px solid {BORDER};
    padding-right: 2px;
    min-width: 70px;
}}
QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 1px solid {ACCENT};
}}
QSpinBox::up-button, QDoubleSpinBox::up-button {{
    width: 20px;
}}
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    width: 20px;
}}
QComboBox {{
    background: {BG_ROOT};
    color: {TEXT_H1};
    border: 1px solid {BORDER};
    border-radius: 2px;
    padding: 2px 20px 2px 6px;
    min-width: 52px;
}}
QComboBox:focus {{ border: 1px solid {ACCENT}; }}
QComboBox::drop-down {{
    width: 20px;
    background: {BG_SURFACE};
    border-left: 1px solid {BORDER};
    border-top-right-radius: 2px;
    border-bottom-right-radius: 2px;
}}
QComboBox::down-arrow {{ image: url("{CHECK_IMG['arrow']}"); width: 10px; height: 10px; }}
QComboBox::down-arrow:on {{ image: url("{CHECK_IMG['arrow_on']}"); }}
QComboBox::down-arrow:disabled {{ image: url("{CHECK_IMG['arrow_dis']}"); }}
QComboBox:hover {{ border: 1px solid {ACCENT}; }}
QLineEdit {{
    background: {BG_ROOT};
    color: {TEXT_H1};
    border: 1px solid {BORDER};
    border-radius: 2px;
    padding: 2px 6px;
}}
QLineEdit:focus {{ border: 1px solid {ACCENT}; }}
QCheckBox {{
    color: {TEXT_H1};
    spacing: 6px;
}}
{check_indicator_qss("QCheckBox")}
{check_indicator_qss("QAbstractItemView")}
"""
