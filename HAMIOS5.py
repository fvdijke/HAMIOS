"""
HAMIOS v5.0 — PySide6 versie
by Frank van Dijke · Developed with Claude AI
"""

import sys
import os
import signal
import traceback

# Ctrl+C in terminal: negeer — gebruik de Afsluiten-knop
signal.signal(signal.SIGINT, signal.SIG_IGN)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import (QApplication, QMessageBox, QDialog,
                               QVBoxLayout, QPushButton, QLabel)
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QPainterPath, QBrush

from hamios5.mainwindow import HAMIOSMainWindow


def _draw_logo(p: QPainter, cx: float, cy: float):
    """Lineart antenne-logo: toren + dipole + propagatie-bogen + aarde."""
    import math
    AMBER  = QColor("#C8A84B")
    AMBER2 = QColor(200, 168, 75, 140)
    AMBER3 = QColor(200, 168, 75, 60)
    DIM    = QColor("#3A4050")

    p.setRenderHint(QPainter.Antialiasing)

    # ── Aarde / grond symbool ─────────────────────────────────────────────────
    p.setPen(QPen(DIM, 1.2))
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(QPointF(cx, cy + 52), 38, 12)   # aardellips
    # continenten-hint: twee vlekken op de ellips
    p.setBrush(QBrush(DIM))
    p.setPen(Qt.NoPen)
    p.drawEllipse(QPointF(cx - 14, cy + 50), 8, 5)
    p.drawEllipse(QPointF(cx + 10, cy + 52), 6, 4)
    p.setBrush(Qt.NoBrush)

    # ── Antenne-mast ──────────────────────────────────────────────────────────
    p.setPen(QPen(AMBER, 2.0, Qt.SolidLine, Qt.RoundCap))
    p.drawLine(QPointF(cx, cy + 50), QPointF(cx, cy - 52))   # mast

    # Steunpoten
    p.setPen(QPen(AMBER, 1.5, Qt.SolidLine, Qt.RoundCap))
    p.drawLine(QPointF(cx, cy + 50), QPointF(cx - 22, cy + 24))
    p.drawLine(QPointF(cx, cy + 50), QPointF(cx + 22, cy + 24))
    p.drawLine(QPointF(cx - 22, cy + 24), QPointF(cx + 22, cy + 24))   # dwarsbalk
    p.drawLine(QPointF(cx, cy + 24), QPointF(cx - 14, cy + 6))
    p.drawLine(QPointF(cx, cy + 24), QPointF(cx + 14, cy + 6))
    p.drawLine(QPointF(cx - 14, cy + 6), QPointF(cx + 14, cy + 6))

    # Dipole element boven de mast
    p.setPen(QPen(AMBER, 2.2, Qt.SolidLine, Qt.RoundCap))
    p.drawLine(QPointF(cx - 30, cy - 30), QPointF(cx + 30, cy - 30))   # dipole

    # Isolator stippen
    p.setBrush(QBrush(AMBER))
    p.setPen(Qt.NoPen)
    for dx in (-4, 4):
        p.drawEllipse(QPointF(cx + dx, cy - 30), 2.5, 2.5)
    p.setBrush(Qt.NoBrush)

    # ── Propagatie-bogen ──────────────────────────────────────────────────────
    for i, r in enumerate([30, 52, 75]):
        alpha = max(35, 160 - i * 55)
        clr = QColor(200, 168, 75, alpha)
        p.setPen(QPen(clr, max(0.8, 1.6 - i * 0.3), Qt.SolidLine, Qt.RoundCap))
        # rechter boog
        p.drawArc(QRectF(cx - r, cy - 30 - r, 2*r, 2*r),
                  -75 * 16, 150 * 16)
        # linker boog
        p.drawArc(QRectF(cx - r, cy - 30 - r, 2*r, 2*r),
                  105 * 16, 150 * 16)


def _make_splash_pixmap() -> QPixmap:
    """Render de splash-afbeelding (zonder knop)."""
    W, H = 580, 300
    pix = QPixmap(W, H)
    pix.fill(QColor("#1A1D22"))
    p = QPainter(pix)

    AMBER = QColor("#C8A84B")
    DIM   = QColor("#404850")
    SUB   = QColor("#7080A0")
    LIGHT = QColor("#C0CAD8")

    p.fillRect(0, 0, 4, H, AMBER)
    _draw_logo(p, 88, H // 2 - 10)

    p.setPen(QPen(QColor("#2A3040"), 1))
    p.drawLine(172, 20, 172, H - 20)

    TX = 188
    p.setFont(QFont("Segoe UI", 26, QFont.Bold))
    p.setPen(AMBER)
    p.drawText(TX, 18, W - TX - 12, 50, Qt.AlignLeft | Qt.AlignVCenter, "HAMIOS")

    p.setFont(QFont("Segoe UI", 12))
    p.setPen(QColor(200, 168, 75, 160))
    p.drawText(TX + 152, 18, 80, 50, Qt.AlignLeft | Qt.AlignVCenter, "v5.0")

    p.setFont(QFont("Segoe UI", 10))
    p.setPen(LIGHT)
    p.drawText(TX, 68, W - TX - 12, 22, Qt.AlignLeft,
               "HF Propagation & DX Monitor")

    p.setPen(QPen(QColor("#2A3040"), 1))
    p.drawLine(TX, 96, W - 16, 96)

    features = [
        ("📡", "Live solar data  ·  band propagatie  ·  Kp / Bz / X-straling"),
        ("🌍", "Real-time wereldkaart  ·  dag/nacht  ·  DX cluster"),
        ("🛰", "Satelliet tracking  ·  orbitpaden  ·  footprint"),
        ("⚡", "Live bliksem (Blitzortung)  ·  onweer-detectie"),
        ("📟", "CAT radio-interface  ·  EIBI kortegolf  ·  FT8/digitaal"),
    ]
    p.setFont(QFont("Segoe UI", 8))
    fy = 104
    for icon, text in features:
        p.setPen(AMBER)
        p.drawText(TX, fy, 18, 16, Qt.AlignCenter, icon)
        p.setPen(SUB)
        p.drawText(TX + 20, fy, W - TX - 32, 16, Qt.AlignLeft, text)
        fy += 17

    p.setPen(QPen(QColor("#2A3040"), 1))
    p.drawLine(TX, H - 36, W - 16, H - 36)

    p.setFont(QFont("Segoe UI", 7))
    p.setPen(DIM)
    p.drawText(TX, H - 30, W - TX - 12, 14,
               Qt.AlignLeft, "by PA3FVD · Frank van Dijke")
    p.drawText(TX, H - 18, W - TX - 12, 14,
               Qt.AlignLeft, "Developed with Claude AI (Anthropic) · PySide6 · Python")
    p.end()
    return pix


class SplashDialog(QDialog):
    """Frameless welkomstscherm met 'Doorgaan' knop."""

    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setModal(True)

        pix = _make_splash_pixmap()
        W, H = pix.width(), pix.height()

        # Achtergrond-canvas
        canvas = QLabel(self)
        canvas.setPixmap(pix)
        canvas.setFixedSize(W, H)

        # "Doorgaan" knop bovenop de canvas
        self._btn = QPushButton("Doorgaan  →", self)
        self._btn.setFixedSize(130, 30)
        self._btn.move(W - 146, H - 48)
        self._btn.setStyleSheet(
            "QPushButton {"
            "  background: #C8A84B; color: #1A1D22;"
            "  font-weight: bold; font-size: 9pt;"
            "  border: none; border-radius: 3px;"
            "}"
            "QPushButton:hover { background: #E0C060; }"
            "QPushButton:pressed { background: #A88030; }")
        self._btn.clicked.connect(self.accept)

        # Statuslabel (links onderin, boven de credits-regel)
        self._status = QLabel("Initialiseren…", self)
        self._status.setFixedWidth(360)
        self._status.move(188, H - 52)
        self._status.setStyleSheet(
            "color: #C8A84B; font-size: 8pt; background: transparent;")

        self.setFixedSize(W, H)

    def set_status(self, text: str):
        self._status.setText(text)
        QApplication.processEvents()

    def enable_button(self):
        self._btn.setEnabled(True)
        self._btn.setText("Doorgaan  →")
        self._btn.setStyleSheet(
            "QPushButton {"
            "  background: #C8A84B; color: #1A1D22;"
            "  font-weight: bold; font-size: 9pt;"
            "  border: none; border-radius: 3px;"
            "}"
            "QPushButton:hover { background: #E0C060; }"
            "QPushButton:pressed { background: #A88030; }")
        QApplication.processEvents()


def _show_error(title: str, text: str):
    """Toon foutmelding als Qt-dialoog (ook zonder hoofdvenster)."""
    try:
        box = QMessageBox()
        box.setWindowTitle(title)
        box.setIcon(QMessageBox.Critical)
        box.setText(text[:300])
        box.setDetailedText(text)
        box.exec()
    except Exception:
        print(text, file=sys.stderr)


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    app.setApplicationName("HAMIOS")
    app.setApplicationVersion("5.0")
    app.setOrganizationName("PA3FVD")

    # Onderschep alle onverwerkte exceptions — toon dialoog i.p.v. stil afsluiten
    def _excepthook(exc_type, exc_value, exc_tb):
        msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print(msg, file=sys.stderr)
        _show_error("HAMIOS — Onverwachte fout", msg)
    sys.excepthook = _excepthook

    # Genereer pijl-images voor QSpinBox en QComboBox, voeg toe aan globale QSS
    from hamios5.theme import generate_spinbox_arrows, QSS as _QSS
    _up, _dn = generate_spinbox_arrows()
    _arrow_qss = f"""
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
    image: url("{_up}"); width: 10px; height: 6px;
}}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow,
QComboBox::down-arrow {{
    image: url("{_dn}"); width: 10px; height: 6px;
}}
"""
    app.setStyleSheet(_QSS.replace("COMBO_ARROW_PLACEHOLDER", _dn) + _arrow_qss)

    # Laad config voor splash-beslissing
    from hamios5.config import load_config as _load_cfg
    _boot_cfg = _load_cfg()

    if _boot_cfg.show_splash:
        splash = SplashDialog()
        # Knop alvast uitschakelen; inschakelen na laden
        splash._btn.setEnabled(False)
        splash._btn.setText("Laden…")
        splash._btn.setStyleSheet(
            "QPushButton { background: #404850; color: #606870;"
            " font-size: 9pt; border: none; border-radius: 3px; }")
        splash.show()
        app.processEvents()

        # Laad het hoofdvenster terwijl het splash-scherm zichtbaar is
        try:
            splash.set_status("Kaart en lagen laden…")
            window = HAMIOSMainWindow()
            splash.set_status("Klaar — klik Doorgaan om te starten")
        except Exception:
            msg = traceback.format_exc()
            print(msg, file=sys.stderr)
            splash.close()
            _show_error("HAMIOS — Startfout", msg)
            sys.exit(1)

        splash.enable_button()
        splash.exec()          # blokkeert tot gebruiker op Doorgaan klikt
        splash.close()

    else:
        try:
            window = HAMIOSMainWindow()
        except Exception:
            msg = traceback.format_exc()
            print(msg, file=sys.stderr)
            _show_error("HAMIOS — Startfout", msg)
            sys.exit(1)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
