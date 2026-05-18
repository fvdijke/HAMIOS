"""
HAMIOS v5 — FloatingPanel basisklasse (PySide6)

Panelen leven als QWidget-kinderen van het desktop-canvas.
Ze bewegen mee met het hoofdvenster en kunnen gesleept/vergroot worden.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QColor, QPen

from . import theme as _theme
from .theme import (
    ACCENT, BG_PANEL, BG_ROOT, TEXT_H1, TITLE_H, BG_SURFACE
)


# ── Resize grip ───────────────────────────────────────────────────────────────

class _ResizeGrip(QWidget):
    """Amber driehoekje rechtsonder — past FloatingPanel direct aan."""

    SIZE = 14

    def __init__(self, panel: "FloatingPanel"):
        super().__init__(panel)
        self._panel = panel
        self._start_global: QPoint | None = None
        self._start_w = self._start_h = 0
        self._resizing = False
        self.setFixedSize(self.SIZE, self.SIZE)
        self.setCursor(Qt.SizeFDiagCursor)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.raise_()
        self.hide()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(ACCENT))
        # Driehoekje rechtsboven→linksonder→rechtsonder
        from PySide6.QtGui import QPolygon
        from PySide6.QtCore import QPoint
        tri = QPolygon([QPoint(self.SIZE, 0),
                        QPoint(self.SIZE, self.SIZE),
                        QPoint(0, self.SIZE)])
        p.drawPolygon(tri)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._resizing = True
            self._start_global = event.globalPosition().toPoint()
            self._start_w = self._panel.width()
            self._start_h = self._panel.height()

    def mouseMoveEvent(self, event):
        if self._start_global is None:
            return
        delta = event.globalPosition().toPoint() - self._start_global
        new_w = max(120, self._start_w + delta.x())
        new_h = max(60,  self._start_h + delta.y())
        self._panel.resize(new_w, new_h)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._start_global is not None:
            g = _theme.PANEL_GRID
            self._panel.resize(
                max(120, round(self._panel.width()  / g) * g),
                max(60,  round(self._panel.height() / g) * g))
            self._start_global = None
            self._resizing = False
            # Verberg grip als muis het paneel heeft verlaten
            local = self._panel.mapFromGlobal(event.globalPosition().toPoint())
            if not self._panel.rect().contains(local):
                self.hide()


# ── Titelbalk ─────────────────────────────────────────────────────────────────

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
            f" background: transparent;")
        layout.addWidget(self._lbl, 1)

        self._close = QPushButton("✕")
        self._close.setFixedSize(20, 20)
        self._close.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {ACCENT};"
            f" border: none; font-size: 8pt; }}"
            f"QPushButton:hover {{ background: {ACCENT}; color: {BG_ROOT}; }}")
        self._close.setCursor(Qt.ArrowCursor)
        layout.addWidget(self._close)

        self.setStyleSheet(f"background: {BG_PANEL};")
        self._drag_pos: QPoint | None = None

    def set_title(self, title: str):
        self._lbl.setText(title)

    def close_button(self) -> QPushButton:
        return self._close

    def _floating_panel(self) -> "FloatingPanel | None":
        """2 niveaus omhoog: titlebar → _inner → FloatingPanel."""
        inner = self.parent()
        return inner.parent() if inner is not None else None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.position().toPoint()
            fp = self._floating_panel()
            if fp:
                fp.raise_()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            panel = self._floating_panel()
            if panel:
                delta   = event.position().toPoint() - self._drag_pos
                new_pos = panel.pos() + delta
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
            panel = self._floating_panel()
            if panel:
                g = _theme.PANEL_GRID
                panel.move(round(panel.x() / g) * g,
                           round(panel.y() / g) * g)
            self._drag_pos = None
        super().mouseReleaseEvent(event)


# ── Floating panel ────────────────────────────────────────────────────────────

class FloatingPanel(QWidget):
    """
    Versleepbaar, aanpasbaar paneel als QWidget-kind van het desktop-canvas.
    Amber 1px rand via paintEvent. Resize via custom _ResizeGrip.
    """

    def __init__(self, title: str, panel_id: str = "", parent=None):
        super().__init__(parent)
        self.panel_id = panel_id
        self._visible_flag = True

        # Geen autoFillBackground — paintEvent tekent rand + achtergrond zelf

        # Hoofd-layout: 1px marge = amber rand (via paintEvent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(1, 1, 1, 1)
        outer.setSpacing(0)

        # Inner container
        self._inner = QWidget()
        self._inner.setStyleSheet(f"background: {BG_PANEL};")
        inner_layout = QVBoxLayout(self._inner)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(0)

        # Titelbalk
        self._titlebar = PanelTitleBar(title, self)
        self._titlebar.close_button().clicked.connect(self._on_close)
        inner_layout.addWidget(self._titlebar)

        # Amber scheidingslijn onder titelbalk — QWidget geeft exact 1px
        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {ACCENT};")
        inner_layout.addWidget(sep)

        # Content-area
        self.content = QWidget()
        self.content.setStyleSheet(f"background: {BG_PANEL};")
        inner_layout.addWidget(self.content, 1)

        outer.addWidget(self._inner)

        # Custom resize grip (vervangt QSizeGrip)
        self._grip = _ResizeGrip(self)

    def paintEvent(self, event):
        """Teken achtergrond en 1px amber rand via fillRect (altijd zichtbaar)."""
        p = QPainter(self)
        W, H = self.width(), self.height()
        # Achtergrond (binnenste gedeelte — _inner bedekt dit toch)
        p.fillRect(0, 0, W, H, QColor(BG_PANEL))
        # 1px amber rand via 4 individuele rechthoeken (betrouwbaarder dan drawRect)
        a = QColor(ACCENT)
        p.fillRect(0,     0,     W,  1, a)  # boven
        p.fillRect(0,     H - 1, W,  1, a)  # onder
        p.fillRect(0,     0,     1,  H, a)  # links
        p.fillRect(W - 1, 0,     1,  H, a)  # rechts

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._grip.move(self.width()  - _ResizeGrip.SIZE,
                        self.height() - _ResizeGrip.SIZE)
        self._grip.raise_()

    def enterEvent(self, event):
        self._grip.show()
        self._grip.raise_()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self._grip._resizing:
            self._grip.hide()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Breng paneel naar voor bij klik."""
        self.raise_()
        super().mousePressEvent(event)

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
