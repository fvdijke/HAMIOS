"""
HAMIOS v5 — FloatingPanel basisklasse (PySide6)

Panelen leven als QWidget-kinderen van het desktop-canvas.
Ze bewegen mee met het hoofdvenster en kunnen gesleept/vergroot worden.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSizeGrip, QFrame
)
from PySide6.QtCore import Qt, QPoint, QSize, QRect
from PySide6.QtGui import QPainter, QColor, QPen

from .theme import (
    ACCENT, BG_PANEL, BG_ROOT, TEXT_H1, TITLE_H, PANEL_GRID,
    BG_SURFACE
)


class PanelTitleBar(QWidget):
    """Amber titelbalk met naam en sluit-knop."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setFixedHeight(TITLE_H)
        self.setObjectName("titlebar")
        self.setCursor(Qt.SizeAllCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 3, 0)
        layout.setSpacing(0)

        self._lbl = QLabel(title)
        self._lbl.setStyleSheet(
            f"color: {ACCENT}; font-weight: bold; font-size: 9pt;"
            f" background: transparent;"
        )
        layout.addWidget(self._lbl, 1)

        self._close = QPushButton("✕")
        self._close.setFixedSize(20, 20)
        self._close.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {ACCENT};"
            f" border: none; font-size: 8pt; }}"
            f"QPushButton:hover {{ background: {ACCENT}; color: {BG_ROOT}; }}"
        )
        self._close.setCursor(Qt.ArrowCursor)
        layout.addWidget(self._close)

        self.setStyleSheet(f"background: {BG_PANEL};")
        self._drag_pos = None

    def set_title(self, title: str):
        self._lbl.setText(title)

    def close_button(self) -> QPushButton:
        return self._close

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            panel = self.parent()
            if panel:
                delta = event.position().toPoint() - self._drag_pos
                new_pos = panel.pos() + delta
                # Begrens binnen het desktop-canvas
                desktop = panel.parent()
                if desktop:
                    max_x = desktop.width()  - panel.width()
                    max_y = desktop.height() - TITLE_H
                    new_pos.setX(max(0, min(new_pos.x(), max_x)))
                    new_pos.setY(max(0, min(new_pos.y(), max_y)))
                panel.move(new_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._drag_pos:
            # Snap naar grid
            panel = self.parent()
            if panel:
                g = PANEL_GRID
                x = round(panel.x() / g) * g
                y = round(panel.y() / g) * g
                panel.move(x, y)
            self._drag_pos = None
        super().mouseReleaseEvent(event)


class FloatingPanel(QWidget):
    """
    Versleepbaar, aanpasbaar paneel als QWidget-kind van het desktop-canvas.
    Panelen leven BINNEN het hoofdvenster en bewegen mee.
    """

    def __init__(self, title: str, panel_id: str = "", parent=None):
        super().__init__(parent)
        self.panel_id = panel_id
        self._visible_flag = True

        # Geen OS-chrome — eigen amber rand
        self.setAutoFillBackground(True)

        # Amber 1px rand via de outer layout
        outer = QVBoxLayout(self)
        outer.setContentsMargins(1, 1, 1, 1)
        outer.setSpacing(0)

        # Container met BG_PANEL achtergrond
        self._inner = QWidget()
        self._inner.setStyleSheet(f"background: {BG_PANEL};")
        inner_layout = QVBoxLayout(self._inner)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(0)

        # Titelbalk
        self._titlebar = PanelTitleBar(title, self)
        self._titlebar.close_button().clicked.connect(self._on_close)
        inner_layout.addWidget(self._titlebar)

        # Dunne amber scheidingslijn onder titelbalk
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background: {ACCENT}; max-height: 1px;")
        inner_layout.addWidget(sep)

        # Content-area
        self.content = QWidget()
        self.content.setStyleSheet(f"background: {BG_PANEL};")
        inner_layout.addWidget(self.content, 1)

        outer.addWidget(self._inner)

        # Amber buitenrand via stylesheet
        self.setStyleSheet(f"FloatingPanel {{ background: {ACCENT}; }}")

        # Resize grip rechtsonder
        self._grip = QSizeGrip(self)
        self._grip.setFixedSize(16, 16)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Resize grip altijd rechtsonder
        self._grip.move(self.width() - 16, self.height() - 16)
        self._grip.raise_()

    def set_title(self, title: str):
        self._titlebar.set_title(title)

    def _on_close(self):
        self.hide_panel()

    def hide_panel(self):
        self.hide()
        self._visible_flag = False

    def show_panel(self):
        self.show()
        self.raise_()
        self._visible_flag = True

    def is_panel_visible(self) -> bool:
        return self._visible_flag

    def place(self, x: int, y: int, w: int, h: int):
        self.setGeometry(x, y, w, h)

    def get_geometry(self) -> tuple:
        g = self.geometry()
        return g.x(), g.y(), g.width(), g.height()
