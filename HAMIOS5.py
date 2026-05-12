"""
HAMIOS v5.0 — PySide6 versie
by Frank van Dijke · Developed with Claude AI

Sprint 1: Fundament, header, floating panels op desktop-canvas.
"""

import sys
import os

# Voeg parent-map toe zodat hamios5 package gevonden wordt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from hamios5.mainwindow import HAMIOSMainWindow


def main():
    # High-DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    app.setApplicationName("HAMIOS")
    app.setApplicationVersion("5.0")
    app.setOrganizationName("PA3FVD")

    window = HAMIOSMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
