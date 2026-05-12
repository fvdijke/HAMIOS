"""
HAMIOS v5 — Header balk (PySide6)
"""
import datetime

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from .theme import ACCENT, BG_PANEL, TEXT_H1, TEXT_DIM, HDR_H, BG_ROOT, BG_SURFACE


class HeaderBar(QWidget):
    """Amber-geaccentueerde header: titelbalk, knoppen, klok."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("header")
        self.setFixedHeight(HDR_H)
        self.setStyleSheet(f"background: {BG_PANEL};")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 6, 0)
        layout.setSpacing(0)

        # Amber accent-balk links
        accent_bar = QFrame()
        accent_bar.setFixedWidth(4)
        accent_bar.setStyleSheet(f"background: {ACCENT};")
        layout.addWidget(accent_bar)

        # Titel
        self._title_lbl = QLabel("📡  HAMIOS v5.0")
        self._title_lbl.setObjectName("title")
        self._title_lbl.setStyleSheet(
            f"color: {ACCENT}; font-size: 13pt; font-weight: bold;"
            f" padding: 0 10px;"
        )
        layout.addWidget(self._title_lbl)

        # Linker knoppen
        self._btn_exit     = self._make_btn("Afsluiten", accent="#5A1010", hover="#8B1A1A")
        self._btn_settings = self._make_btn("⚙  Instellingen", amber=True)
        self._btn_overlay  = self._make_btn("🗺  Overlay",  amber=True)
        self._btn_sat      = self._make_btn("🛰  Sat",      amber=True)
        self._btn_spy      = self._make_btn("🕵  Spy",      amber=True)

        for btn in [self._btn_exit, self._btn_settings,
                    self._btn_overlay, self._btn_sat, self._btn_spy]:
            layout.addWidget(btn)

        layout.addStretch()

        # Rechter knoppen en klok
        self._lbl_local = QLabel("--:--:--")
        self._lbl_local.setStyleSheet(
            f"color: {TEXT_H1}; font-size: 10pt; font-weight: bold;"
        )
        self._lbl_utc = QLabel("UTC --:--")
        self._lbl_utc.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10pt;")

        self._sep = lambda: self._make_sep()

        self._btn_help     = self._make_btn("?",   amber=True)
        self._btn_fs       = self._make_btn("⛶",   amber=True)

        layout.addWidget(self._lbl_utc)
        layout.addWidget(self._make_sep())
        layout.addWidget(self._lbl_local)
        layout.addWidget(self._make_sep())
        layout.addWidget(self._btn_help)
        layout.addWidget(self._btn_fs)

        # Klok-timer
        self._clock = QTimer(self)
        self._clock.timeout.connect(self._tick)
        self._clock.start(1000)
        self._tick()

    # ── helpers ───────────────────────────────────────────────────────────────
    def _make_btn(self, text: str, amber: bool = False,
                  accent: str = None, hover: str = None) -> QPushButton:
        btn = QPushButton(text)
        bg    = accent or BG_SURFACE
        hbg   = hover  or "#32373F"
        color = ACCENT if amber else TEXT_H1
        btn.setStyleSheet(
            f"QPushButton {{ background: {bg}; color: {color}; border: none;"
            f" padding: 2px 8px; }}"
            f"QPushButton:hover {{ background: {hbg}; }}"
        )
        return btn

    def _make_sep(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("color: #383E47;")
        sep.setFixedWidth(1)
        sep.setContentsMargins(8, 8, 8, 8)
        return sep

    def _tick(self):
        now = datetime.datetime.now()
        utc = datetime.datetime.now(datetime.timezone.utc)
        self._lbl_local.setText(now.strftime("%H:%M:%S"))
        self._lbl_utc.setText(f"UTC  {utc.strftime('%H:%M:%S')}")

    # ── publieke interface ─────────────────────────────────────────────────────
    @property
    def btn_exit(self):     return self._btn_exit
    @property
    def btn_settings(self): return self._btn_settings
    @property
    def btn_overlay(self):  return self._btn_overlay
    @property
    def btn_sat(self):      return self._btn_sat
    @property
    def btn_spy(self):      return self._btn_spy
    @property
    def btn_help(self):     return self._btn_help
    @property
    def btn_fullscreen(self): return self._btn_fs
