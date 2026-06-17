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
    from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QFont
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
    width: 18px;
}}
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    width: 18px;
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
/* QComboBox::down-arrow: Use platform default */
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
QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    background: #000000;
    border: 1px solid #666666;
    border-radius: 1px;
}}
QCheckBox::indicator:hover {{
    border: 1px solid #888888;
}}
QCheckBox::indicator:checked {{
    background: #C8A84B;
    border: 1px solid #A88A3A;
}}
"""
