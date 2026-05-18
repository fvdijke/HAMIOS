"""HAMIOS v5 — CAT venster

Indeling:
  • Statuskaart     — verbindingsindicator + Verbinden/Verbreken
  • Seriële params  — poort, baud, bits, pariteit, stop, radiotype, CI-V
  • Terminal toggle — checkbox om seriële terminal in/uit te klappen
  • Sluiten-knop

Thread-safe log: CatInterface roept _queue_entry() aan vanuit elke thread;
QTimer draineert de queue naar de GUI-thread.
"""

import datetime
import threading

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit,
    QFrame, QCheckBox
)

from .theme import ACCENT, BG_PANEL, BG_SURFACE, BG_ROOT, TEXT_H1, TEXT_DIM, BORDER
from .geometry import save_geom, restore_geom

_QSS = f"""
QWidget   {{ background: {BG_PANEL}; }}
QFrame#card {{
    background: {BG_SURFACE};
    border: 1px solid {BORDER};
    border-radius: 3px;
}}
QTextEdit {{
    background: {BG_ROOT}; color: #C8C8C8;
    border: 1px solid {BORDER}; font-family: Consolas; font-size: 9pt;
}}
QLineEdit {{
    background: {BG_ROOT}; color: {TEXT_H1};
    border: 1px solid {BORDER}; padding: 3px 5px; border-radius: 2px;
    font-family: Consolas; font-size: 9pt;
}}
QLineEdit:focus {{ border-color: {ACCENT}; }}
QLabel    {{ color: {TEXT_DIM}; font-size: 8pt; background: transparent; }}
QCheckBox {{ color: {TEXT_H1}; font-size: 8pt; spacing: 5px; }}
QPushButton {{
    background: {BG_SURFACE}; color: {TEXT_H1};
    border: 1px solid {BORDER}; padding: 4px 12px; border-radius: 2px;
}}
QPushButton:hover  {{ background: #32373F; border-color: {ACCENT}; }}
QPushButton#connect    {{ background: {ACCENT}; color: {BG_ROOT}; font-weight: bold; }}
QPushButton#connect:hover  {{ background: #E0C060; }}
QPushButton#disconnect {{ background: #5A1010; color: #EF5350; border-color: #8B1A1A; }}
QPushButton#disconnect:hover {{ background: #8B1A1A; color: white; }}
QPushButton#send   {{ background: {ACCENT}; color: {BG_ROOT}; font-weight: bold; }}
QPushButton#send:hover {{ background: #E0C060; }}
"""

_COL_TX   = "#C8A84B"
_COL_RX   = "#4CAF50"
_COL_INFO = "#607080"
_COL_ERR  = "#EF5350"

_COMPACT_H = 190   # status + terminal-toggle + sluit
_FULL_H    = 480   # + terminal


class CatMonitorWindow(QWidget):
    """CAT status + seriële parameters + optionele terminal."""

    def __init__(self, cat_interface, parent=None):
        super().__init__(parent, Qt.Window | Qt.WindowStaysOnTopHint)
        self._cat   = cat_interface
        self._queue: list[tuple[str, str]] = []
        self._qlock = threading.Lock()

        self.setWindowTitle("📟  CAT — HF Propagation & Atmosphere Monitor")
        self.setMinimumWidth(420)
        self.resize(480, _COMPACT_H)
        restore_geom(self, "CatMonitorWindow")
        self.setStyleSheet(_QSS)
        self._build_ui()

        self._cat._log_callback = self._queue_entry

        self._drain_timer = QTimer(self)
        self._drain_timer.timeout.connect(self._drain)
        self._drain_timer.start(50)

        self._status_timer = QTimer(self)
        self._status_timer.timeout.connect(self._refresh_status)
        self._status_timer.start(1000)

        self._log_info("CAT venster geopend")
        self._refresh_status()

    # ── UI opbouw ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        f8  = QFont("Segoe UI", 8)
        f8c = QFont("Consolas", 8)

        # ── 1. Statuskaart ────────────────────────────────────────────────────
        card_status = QFrame(); card_status.setObjectName("card")
        cs = QVBoxLayout(card_status)
        cs.setContentsMargins(12, 8, 12, 8); cs.setSpacing(5)

        top = QHBoxLayout()
        self._dot_lbl  = QLabel("⬤")
        self._dot_lbl.setStyleSheet(
            f"color:{TEXT_DIM}; font-size:14pt; background:transparent;")
        self._conn_lbl = QLabel("Niet verbonden")
        self._conn_lbl.setStyleSheet(
            f"color:{TEXT_DIM}; font-size:10pt; font-weight:bold; background:transparent;")
        top.addWidget(self._dot_lbl)
        top.addWidget(self._conn_lbl)
        top.addStretch()
        self._btn_connect    = QPushButton("Verbinden")
        self._btn_connect.setObjectName("connect")
        self._btn_disconnect = QPushButton("Verbreken")
        self._btn_disconnect.setObjectName("disconnect")
        self._btn_connect.clicked.connect(self._do_connect)
        self._btn_disconnect.clicked.connect(self._do_disconnect)
        top.addWidget(self._btn_connect)
        top.addWidget(self._btn_disconnect)
        cs.addLayout(top)

        sep0 = QFrame(); sep0.setFrameShape(QFrame.HLine)
        sep0.setStyleSheet(f"background:{BORDER}; max-height:1px;")
        cs.addWidget(sep0)

        info = QHBoxLayout()
        self._lbl_port  = QLabel("—"); self._lbl_port.setFont(f8c)
        self._lbl_baud  = QLabel("—"); self._lbl_baud.setFont(f8)
        self._lbl_type  = QLabel("—"); self._lbl_type.setFont(f8)
        for hdr, w in [("Poort:", self._lbl_port),
                        ("Baud:", self._lbl_baud),
                        ("Type:", self._lbl_type)]:
            info.addWidget(QLabel(hdr))
            info.addWidget(w)
            info.addSpacing(10)
        info.addStretch()
        cs.addLayout(info)
        root.addWidget(card_status)

        # Seriële parameters staan in ⚙ Instellingen → CAT
        note = QLabel("Seriële instellingen: ⚙  Instellingen → CAT")
        note.setStyleSheet(f"color:{TEXT_DIM}; font-size:7pt; padding: 0 2px;")
        root.addWidget(note)

        # ── 2. Terminal toggle ────────────────────────────────────────────────
        toggle_row = QHBoxLayout()
        self._term_cb = QCheckBox("Seriële terminal tonen")
        self._term_cb.setFont(f8)
        self._term_cb.toggled.connect(self._toggle_terminal)
        toggle_row.addWidget(self._term_cb)
        toggle_row.addStretch()
        root.addLayout(toggle_row)

        # ── 4. Terminal sectie ────────────────────────────────────────────────
        self._term_widget = QWidget()
        tw = QVBoxLayout(self._term_widget)
        tw.setContentsMargins(0, 0, 0, 0); tw.setSpacing(4)

        log_top = QHBoxLayout()
        log_top.addWidget(QLabel("Log:"))
        log_top.addStretch()
        btn_clr = QPushButton("Wis"); btn_clr.setFixedWidth(50)
        log_top.addWidget(btn_clr)
        tw.addLayout(log_top)

        self._log_view = QTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.document().setMaximumBlockCount(500)
        tw.addWidget(self._log_view, 1)
        btn_clr.clicked.connect(self._log_view.clear)

        sep2 = QFrame(); sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet(f"background:{BORDER}; max-height:1px;")
        tw.addWidget(sep2)

        cmd_row = QHBoxLayout()
        cmd_row.addWidget(QLabel("Commando:"))
        self._cmd_edit = QLineEdit()
        self._cmd_edit.setPlaceholderText("bijv.  IF;   of   FA00014225000;")
        self._cmd_edit.returnPressed.connect(self._send_manual)
        btn_send = QPushButton("Stuur"); btn_send.setObjectName("send")
        btn_send.clicked.connect(self._send_manual)
        cmd_row.addWidget(self._cmd_edit, 1)
        cmd_row.addWidget(btn_send)
        tw.addLayout(cmd_row)

        quick = QHBoxLayout()
        quick.addWidget(QLabel("Snel:"))
        for label, cmd in [("IF;","IF;"),("FA;","FA;"),("MD;","MD;"),("ID;","ID;")]:
            b = QPushButton(label); b.setFixedWidth(44)
            b.setFont(QFont("Consolas", 8))
            b.setToolTip(f"Stuur: {cmd}")
            b.clicked.connect(lambda _=0, c=cmd: self._send_raw(c))
            quick.addWidget(b)
        quick.addStretch()
        tw.addLayout(quick)

        self._term_widget.hide()
        root.addWidget(self._term_widget, 1)

        # ── 5. Sluiten-knop ───────────────────────────────────────────────────
        bot = QHBoxLayout()
        bot.addStretch()
        btn_close = QPushButton("Sluiten"); btn_close.setObjectName("close")
        btn_close.clicked.connect(self.close)
        bot.addWidget(btn_close)
        root.addLayout(bot)

    # ── Verbinden / verbreken ────────────────────────────────────────────────

    def _do_connect(self):
        """Verbind via de instellingen in ⚙ Instellingen → CAT."""
        ok, msg = self._cat.connect()
        if ok:
            self._log_info("Verbinding tot stand gebracht")
        else:
            self._queue_entry("ERR", f"Verbinden mislukt: {msg}")
        self._refresh_status()

    def _do_disconnect(self):
        self._cat.disconnect()
        if self._cat._cfg:
            self._cat._cfg.cat_enabled = False
        self._log_info("Verbinding verbroken")
        self._refresh_status()

    # ── Status bijwerken ─────────────────────────────────────────────────────

    def _refresh_status(self):
        cfg   = self._cat._cfg
        port  = getattr(cfg, "cat_port",       "—") if cfg else "—"
        baud  = str(getattr(cfg, "cat_baud",   "—")) if cfg else "—"
        rtype = getattr(cfg, "cat_radio_type", "—") if cfg else "—"
        self._lbl_port.setText(port or "—")
        self._lbl_baud.setText(baud)
        self._lbl_type.setText(rtype.split("(")[0].strip() if rtype else "—")

        if self._cat.connected:
            self._dot_lbl.setStyleSheet(
                "color:#4CAF50; font-size:14pt; background:transparent;")
            self._conn_lbl.setText("Verbonden")
            self._conn_lbl.setStyleSheet(
                "color:#4CAF50; font-size:10pt; font-weight:bold; background:transparent;")
            self._btn_connect.setEnabled(False)
            self._btn_disconnect.setEnabled(True)
        else:
            self._dot_lbl.setStyleSheet(
                f"color:{TEXT_DIM}; font-size:14pt; background:transparent;")
            self._conn_lbl.setText("Niet verbonden")
            self._conn_lbl.setStyleSheet(
                f"color:{TEXT_DIM}; font-size:10pt; font-weight:bold; background:transparent;")
            self._btn_connect.setEnabled(True)
            self._btn_disconnect.setEnabled(False)

    # ── Terminal tonen/verbergen ──────────────────────────────────────────────

    def _toggle_terminal(self, show: bool):
        self._term_widget.setVisible(show)
        self.setMaximumHeight(16777215)   # verwijder eerst eventuele begrenzing
        if show:
            self.resize(self.width(), _FULL_H)
        else:
            # Krip venster in: begrens eerst, resize dan
            self.setMaximumHeight(_COMPACT_H)
            self.resize(self.width(), _COMPACT_H)
            # Verwijder de begrenzing na verwerking zodat venster weer vrij schaalbaar is
            from PySide6.QtCore import QTimer as _QT
            _QT.singleShot(50, lambda: self.setMaximumHeight(16777215))

    # ── Logging ───────────────────────────────────────────────────────────────

    def _queue_entry(self, direction: str, data):
        ts = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        if isinstance(data, (bytes, bytearray)):
            text    = data.decode("ascii", errors="replace").rstrip("\r\n")
            hex_str = " ".join(f"{b:02X}" for b in data)
            line    = f"[{ts}] {direction:3s}  {text}  ({hex_str})"
        else:
            line = f"[{ts}] {direction:3s}  {data}"
        color = {"TX": _COL_TX, "RX": _COL_RX,
                 "INFO": _COL_INFO, "ERR": _COL_ERR}.get(direction, _COL_INFO)
        with self._qlock:
            self._queue.append((color, line))

    def _log_info(self, msg: str):
        self._queue_entry("INFO", msg)

    def _drain(self):
        with self._qlock:
            items, self._queue = self._queue, []
        if not items:
            return
        cur = self._log_view.textCursor()
        cur.movePosition(QTextCursor.End)
        fmt = QTextCharFormat()
        for color, line in items:
            fmt.setForeground(QColor(color))
            cur.insertText(line + "\n", fmt)
        self._log_view.setTextCursor(cur)
        self._log_view.ensureCursorVisible()

    # ── Handmatige commando's ─────────────────────────────────────────────────

    def _send_manual(self):
        txt = self._cmd_edit.text().strip()
        if txt:
            self._send_raw(txt)
            self._cmd_edit.clear()

    def _send_raw(self, cmd: str):
        if not self._cat.connected:
            ok, err = self._cat.connect()
            if not ok:
                self._queue_entry("ERR", f"Verbinden mislukt: {err}")
                self._refresh_status()
                return
        try:
            data = cmd.encode("ascii")
            with self._cat._lock:
                self._cat._serial.write(data)
                self._cat._serial.flush()
                import time; time.sleep(0.12)
                rx = b""
                while self._cat._serial.in_waiting:
                    rx += self._cat._serial.read(self._cat._serial.in_waiting)
                    time.sleep(0.02)
            self._queue_entry("TX", data)
            if rx:
                self._queue_entry("RX", rx)
        except Exception as e:
            self._queue_entry("ERR", str(e))
        self._refresh_status()

    # ── Sluiten ───────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        save_geom(self, "CatMonitorWindow")
        self._drain_timer.stop()
        self._status_timer.stop()
        if self._cat._log_callback is self._queue_entry:
            self._cat._log_callback = None
        super().closeEvent(event)

