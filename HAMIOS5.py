"""
HAMIOS v5.0 — PySide6 versie
by Frank van Dijke · Developed with Claude AI

==================================================================================
TODO:
==================================================================================
- Maak de resolutie van de kaart beter bij inzoomen
v Maak de grote van het icoontje van de zon en maan instelbaar (instellingen/kaart)
v Maak de resize driehoekjes alleen zichtbaar wanneer het paneel actief is.
v Bij opstarten wil ik in het splashscreen de status van de bestanden en aghankelijkheden zien (zoals in instellingen/over).
- Vertaal het gehele programma ook neet Engels en zet in instellingen/over een keuze voor Engels of Nederlands.
v In de header verander de Z (zomertijd) naast DST
v In bandverloop moet de grafiek voor Dag, Week, Maand, Jaar.
v Controleer de werking can het Solar verloop paneel. Ik zie daar weinig gebeuren.
- Laat alleen een Ping horen wanneer een satelliet de QTH zone inkomt. Geef een lage ping als hij de QTH zone verlaat.
v Ik mis de +150 graden op de kaart. Nu zijn de medianen per 30gr. Ik wil dit kunnen instellen in instellingen/kaart (per 10 graden en dynamisch)
v Snap-raster in instellingen/kaart moet naar instellingen/layout
v Verwijder Layout acties in instellingen/kaart
- Kijk nog eens goed naar de footprint bij de polen (bewaar de huidige programmering want deze is bijna goed). Nu lijkt de footprint dichtst bij de polen afgeplat. Ik wil weer terug kunnen naar de huidige code als het niet goed gaat.
v Zet satelliet weergave ook in Overlay paneel (header)
==================================================================================
"""

import sys
import os
import signal
import traceback

# Ctrl+C in terminal: negeer — gebruik de Afsluiten-knop
signal.signal(signal.SIGINT, signal.SIG_IGN)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import (QApplication, QMessageBox, QDialog,
                               QVBoxLayout, QHBoxLayout, QGridLayout,
                               QPushButton, QLabel, QFrame, QWidget)
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QPainterPath, QBrush

from hamios5.mainwindow import HAMIOSMainWindow


# ── Antenne-logo ──────────────────────────────────────────────────────────────

def _draw_logo(p: QPainter, cx: float, cy: float, scale: float = 1.0):
    """Lineart antenne-logo: toren + dipole + propagatie-bogen + aarde."""
    AMBER = QColor("#C8A84B")
    DIM   = QColor("#3A4050")
    s     = scale

    p.setRenderHint(QPainter.Antialiasing)

    # Aarde
    p.setPen(QPen(DIM, max(0.8, 1.2 * s)))
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(QPointF(cx, cy + 52*s), 38*s, 12*s)
    p.setBrush(QBrush(DIM))
    p.setPen(Qt.NoPen)
    p.drawEllipse(QPointF(cx - 14*s, cy + 50*s), 8*s, 5*s)
    p.drawEllipse(QPointF(cx + 10*s, cy + 52*s), 6*s, 4*s)
    p.setBrush(Qt.NoBrush)

    # Mast
    p.setPen(QPen(AMBER, max(1.0, 2.0 * s), Qt.SolidLine, Qt.RoundCap))
    p.drawLine(QPointF(cx, cy + 50*s), QPointF(cx, cy - 52*s))

    # Steunpoten
    p.setPen(QPen(AMBER, max(0.8, 1.5 * s), Qt.SolidLine, Qt.RoundCap))
    p.drawLine(QPointF(cx, cy + 50*s), QPointF(cx - 22*s, cy + 24*s))
    p.drawLine(QPointF(cx, cy + 50*s), QPointF(cx + 22*s, cy + 24*s))
    p.drawLine(QPointF(cx - 22*s, cy + 24*s), QPointF(cx + 22*s, cy + 24*s))
    p.drawLine(QPointF(cx, cy + 24*s), QPointF(cx - 14*s, cy + 6*s))
    p.drawLine(QPointF(cx, cy + 24*s), QPointF(cx + 14*s, cy + 6*s))
    p.drawLine(QPointF(cx - 14*s, cy + 6*s), QPointF(cx + 14*s, cy + 6*s))

    # Dipole
    p.setPen(QPen(AMBER, max(1.0, 2.2 * s), Qt.SolidLine, Qt.RoundCap))
    p.drawLine(QPointF(cx - 30*s, cy - 30*s), QPointF(cx + 30*s, cy - 30*s))

    # Isolatoren
    p.setBrush(QBrush(AMBER))
    p.setPen(Qt.NoPen)
    for dx in (-4, 4):
        p.drawEllipse(QPointF(cx + dx*s, cy - 30*s), 2.5*s, 2.5*s)
    p.setBrush(Qt.NoBrush)

    # Propagatie-bogen
    for i, r in enumerate([30, 52, 75]):
        alpha = max(35, 160 - i * 55)
        clr = QColor(200, 168, 75, alpha)
        rs = r * s
        p.setPen(QPen(clr, max(0.6, (1.6 - i * 0.3) * s), Qt.SolidLine, Qt.RoundCap))
        p.drawArc(QRectF(cx - rs, cy - 30*s - rs, 2*rs, 2*rs), -75 * 16, 150 * 16)
        p.drawArc(QRectF(cx - rs, cy - 30*s - rs, 2*rs, 2*rs), 105 * 16, 150 * 16)


# ── Splash header pixmap (logo + titel, geen features) ───────────────────────

_SW = 560   # splash breedte

def _make_header_pixmap() -> QPixmap:
    W, H = _SW, 120
    pix = QPixmap(W, H)
    pix.fill(QColor("#1A1D22"))
    p = QPainter(pix)

    AMBER = QColor("#C8A84B")
    LIGHT = QColor("#C8D0DC")
    DIM   = QColor("#505860")

    # Logo gecentreerd in de linker kolom (geen amber balk links)
    _draw_logo(p, 80, H // 2, scale=0.62)

    p.setPen(QPen(QColor("#2A3040"), 1))
    p.drawLine(156, 10, 156, H - 10)

    TX = 172
    p.setFont(QFont("Segoe UI", 24, QFont.Bold))
    p.setPen(AMBER)
    p.drawText(TX, 10, W - TX - 12, 46, Qt.AlignLeft | Qt.AlignVCenter, "HAMIOS")

    p.setFont(QFont("Segoe UI", 11))
    p.setPen(QColor(200, 168, 75, 130))
    p.drawText(TX + 134, 10, 50, 46, Qt.AlignLeft | Qt.AlignVCenter, "v5.0")

    p.setFont(QFont("Segoe UI", 9))
    p.setPen(LIGHT)
    p.drawText(TX, 60, W - TX - 12, 20, Qt.AlignLeft | Qt.AlignVCenter,
               "HF Propagation & Atmosphere Monitor")

    p.setFont(QFont("Segoe UI", 7))
    p.setPen(DIM)
    p.drawText(TX, 86, W - TX - 12, 14, Qt.AlignLeft,
               "PA3FVD · Frank van Dijke  ·  Developed with Claude AI  ·  PySide6")

    p.end()
    return pix


# ── Check-definities ──────────────────────────────────────────────────────────
# (key, weergave-label, initiële detail-tekst)
_FILE_CHECKS = [
    ("worldmap",  "worldmap_eq.jpg",          "kaartafbeelding"),
    ("hires",     "worldmap_eq_hires.jpg",    "4K kaart"),
    ("config",    "hamios_config.json",        "configuratie"),
    ("history",   "HAMIOS_history.csv",        "bandverloop"),
    ("tle",       "hamios_tle.json",           "satelliet TLE"),
    ("spy",       "hamios_spy_stations.json",  "SpyStations"),
]

_DEP_CHECKS = [
    ("pyside6",   "PySide6",           "GUI framework"),
    ("pyserial",  "pyserial",          "CAT interface"),
    ("websocket", "websocket-client",  "bliksemdetectie"),
    ("app",       "Applicatie",        "modules laden"),
]

_CHECKS = _FILE_CHECKS + _DEP_CHECKS

# state → (kleur, symbool)
_STATE = {
    "pending": ("#3A4050", "○"),
    "loading": ("#C8A84B", "…"),
    "ok":      ("#4CAF50", "✓"),
    "warn":    ("#FFA726", "○"),
    "error":   ("#EF5350", "✗"),
}


# ── SplashDialog ──────────────────────────────────────────────────────────────

class SplashDialog(QDialog):
    """Frameless welkomstscherm: header + controle-rijen + statusbalk + knop."""

    _BTN_ACTIVE = (
        "QPushButton { background:#C8A84B; color:#1A1D22; font-weight:bold;"
        " font-size:9pt; border:none; border-radius:4px; }"
        "QPushButton:hover  { background:#E0C060; }"
        "QPushButton:pressed{ background:#A88030; }")
    _BTN_WAIT = (
        "QPushButton { background:#252830; color:#404850; font-size:9pt;"
        " border:1px solid #353A44; border-radius:4px; }")

    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setModal(True)
        self.setFixedWidth(_SW)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._rows: dict[str, tuple[QLabel, QLabel]] = {}

        # ── Header (geen amber strepen) ───────────────────────────────────────
        hdr_lbl = QLabel()
        hdr_lbl.setPixmap(_make_header_pixmap())
        root.addWidget(hdr_lbl)

        # ── Amber lijn → Bestanden → Amber lijn → Afhankelijkheden ───────────
        root.addWidget(self._amber_line())
        root.addWidget(self._section("Bestanden", _FILE_CHECKS))
        root.addWidget(self._amber_line())
        root.addWidget(self._section("Afhankelijkheden", _DEP_CHECKS))

        # Initieel alle rijen op pending
        for key, _, detail in _CHECKS:
            self._apply(key, "pending", detail)

        # ── Statusbalk + Doorgaan-knop ────────────────────────────────────────
        bar = QWidget()
        bar.setStyleSheet("background:#1A1D22;")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(16, 8, 16, 8)

        self._status_lbl = QLabel("")
        self._status_lbl.setStyleSheet(
            "color:#C8A84B; font-size:8pt; background:transparent;")
        bl.addWidget(self._status_lbl, 1)

        self._btn = QPushButton("Laden…")
        self._btn.setFixedSize(120, 28)
        self._btn.setEnabled(False)
        self._btn.setStyleSheet(self._BTN_WAIT)
        self._btn.clicked.connect(self.accept)
        bl.addWidget(self._btn)

        root.addWidget(bar)
        self.adjustSize()

    # ── bouw-helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _amber_line() -> QFrame:
        f = QFrame()
        f.setFixedHeight(1)
        f.setStyleSheet("background:#C8A84B;")
        return f

    def _section(self, title: str, checks: list) -> QWidget:
        """Bouw één sectie (bestanden of afhankelijkheden) met een 2-koloms grid."""
        w = QWidget()
        w.setStyleSheet("background:#141820;")
        v = QVBoxLayout(w)
        v.setContentsMargins(16, 8, 16, 8)
        v.setSpacing(3)

        lbl = QLabel(title)
        lbl.setStyleSheet(
            "color:#C8A84B; font-size:7pt; font-weight:bold;"
            " letter-spacing:1px; background:transparent;")
        v.addWidget(lbl)

        # Grid: twee kolommen (naam + detail) × (naam + detail)
        half     = (len(checks) + 1) // 2
        name_w   = 148   # breedte naam-kolom
        det_w    = 88    # breedte detail-kolom

        grid_w = QWidget()
        grid_w.setStyleSheet("background:transparent;")
        grid = QGridLayout(grid_w)
        grid.setContentsMargins(0, 2, 0, 0)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(1)

        for idx, (key, _, detail) in enumerate(checks):
            col_base = (idx // half) * 2
            row      = idx % half

            name_lbl = QLabel()
            name_lbl.setFixedWidth(name_w)
            name_lbl.setStyleSheet("background:transparent;")

            det_lbl = QLabel(detail)
            det_lbl.setFixedWidth(det_w)
            det_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            det_lbl.setStyleSheet("color:#3A4050; font-size:7pt; background:transparent;")

            self._rows[key] = (name_lbl, det_lbl)
            grid.addWidget(name_lbl, row, col_base)
            grid.addWidget(det_lbl,  row, col_base + 1)

        v.addWidget(grid_w)
        return w

    # ── interne helper ────────────────────────────────────────────────────────

    def _apply(self, key: str, state: str, detail: str):
        if key not in self._rows:
            return
        clr, sym = _STATE.get(state, _STATE["pending"])
        icon_name, det = self._rows[key]
        label = next((c[1] for c in _CHECKS if c[0] == key), key)
        icon_name.setText(
            f'<span style="color:{clr};font-size:10pt;font-weight:bold;">{sym}</span>'
            f'<span style="color:#B0BAC8;font-size:8pt;"> {label}</span>')
        det.setText(detail)
        det.setStyleSheet(
            f"color:{clr}; font-size:7pt; background:transparent;")

    # ── publiek ───────────────────────────────────────────────────────────────

    def set_check(self, key: str, state: str, detail: str = ""):
        self._apply(key, state, detail)
        QApplication.processEvents()

    def connect_download(self, key: str, thread):
        """Verbind download-thread signals voor voortgang en voltooiing."""
        thread.progress.connect(
            lambda recv, tot, k=key: self._on_progress(k, recv, tot))
        thread.done.connect(
            lambda k=key: self._apply(k, "ok", "klaar"))
        thread.failed.connect(
            lambda k=key: self._apply(k, "error", "mislukt"))

    def _on_progress(self, key: str, received: int, total: int):
        if total > 0:
            pct = min(99, int(received * 100 / total))
            self._apply(key, "loading", f"{pct}%")
        else:
            mb = received / 1_048_576
            self._apply(key, "loading", f"{mb:.1f} MB")
        QApplication.processEvents()

    def set_status(self, text: str):
        self._status_lbl.setText(text)
        QApplication.processEvents()

    def enable_button(self):
        self._btn.setEnabled(True)
        self._btn.setText("Doorgaan  →")
        self._btn.setStyleSheet(self._BTN_ACTIVE)
        QApplication.processEvents()


# ── Foutdialoog ───────────────────────────────────────────────────────────────

def _show_error(title: str, text: str):
    try:
        box = QMessageBox()
        box.setWindowTitle(title)
        box.setIcon(QMessageBox.Critical)
        box.setText(text[:300])
        box.setDetailedText(text)
        box.exec()
    except Exception:
        print(text, file=sys.stderr)


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    app.setApplicationName("HAMIOS")
    app.setApplicationVersion("5.0")
    app.setOrganizationName("PA3FVD")

    # Opstartcontrole
    from hamios5.startup import check_files
    _, _err = check_files()
    if _err:
        _show_error("HAMIOS — Opstartfout", "\n\n".join(_err))
        sys.exit(1)

    def _excepthook(exc_type, exc_value, exc_tb):
        msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print(msg, file=sys.stderr)
        _show_error("HAMIOS — Onverwachte fout", msg)
    sys.excepthook = _excepthook

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

    from hamios5.config import load_config as _load_cfg
    _boot_cfg = _load_cfg()

    if _boot_cfg.show_splash:
        splash = SplashDialog()
        splash.show()
        app.processEvents()

        # ── Bestand-checks ────────────────────────────────────────────────────
        from hamios5.startup import file_status as _file_status
        _fmap = {f["name"]: f for f in _file_status()}
        # worldmap_eq.jpg is niet meer verplicht — wordt automatisch gedownload
        _req  = {"hamios_config.json"}

        from hamios5.mapview import _HIRES_FILE
        _file_keys = {
            "worldmap":  "worldmap_eq.jpg",
            "config":    "hamios_config.json",
            "history":   "HAMIOS_history.csv",
            "tle":       "hamios_tle.json",
            "spy":       "hamios_spy_stations.json",
        }
        for key, fname in _file_keys.items():
            info = _fmap.get(fname)
            if info and info["exists"]:
                sz = info["size_kb"]
                detail = f"{sz} KB" if sz >= 1 else "aanwezig"
                splash.set_check(key, "ok", detail)
            elif fname in _req:
                splash.set_check(key, "error", "ontbreekt!")
            else:
                splash.set_check(key, "warn", "wordt gedownload…")

        # 4K kaart: apart checken (niet in startup file_status)
        import os as _os
        if _os.path.exists(_HIRES_FILE):
            sz = round(_os.path.getsize(_HIRES_FILE) / 1024, 0)
            splash.set_check("hires", "ok", f"{int(sz)} KB")
        else:
            splash.set_check("hires", "loading", "wordt gedownload…")

        # ── Afhankelijkheden ──────────────────────────────────────────────────
        def _dep(mod):
            try:
                m = __import__(mod)
                v = getattr(m, "__version__", "")
                return True, (f"v{v}" if v else "ok")
            except ImportError:
                return False, "niet gevonden"

        ok6,  d6  = _dep("PySide6")
        okser, dser = _dep("serial")
        okws,  dws  = _dep("websocket")

        splash.set_check("pyside6",   "ok"   if ok6  else "error", d6)
        splash.set_check("pyserial",  "ok"   if okser else "warn",  dser)
        splash.set_check("websocket", "ok"   if okws  else "warn",  dws)

        # ── Applicatie laden ──────────────────────────────────────────────────
        splash.set_check("app", "loading", "laden…")
        splash.set_status("Kaart en lagen laden…")

        try:
            window = HAMIOSMainWindow()
            splash.set_check("app", "ok", "klaar")
            splash.set_status("")
        except Exception:
            msg = traceback.format_exc()
            print(msg, file=sys.stderr)
            splash.set_check("app", "error", "fout!")
            splash.close()
            _show_error("HAMIOS — Startfout", msg)
            sys.exit(1)

        # ── Kaartdownloads starten NÁ signal-verbinding (geeft percentage) ────
        dl_threads = window._map_view.download_missing_maps()
        started = set()
        for key, thread in dl_threads:
            splash.connect_download(key, thread)
            if id(thread) not in started:
                thread.start()          # start elke thread slechts één keer
                started.add(id(thread))

        splash.enable_button()
        splash.exec()
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
