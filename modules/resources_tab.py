"""HAMIOS v5.4 - Resource Manager Tab for Settings"""

import os
import urllib.request as urlreq
import urllib.error as urlerror
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QLineEdit, QPushButton, QMessageBox
)

from .resources_config import ResourceConfig, DEFAULT_RESOURCES, _RESOURCES_FILE
from .i18n import tr
from .theme import BG_PANEL, BG_SURFACE, TEXT_H1, TEXT_BODY, TEXT_DIM, BORDER


class ResourceTestThread(QThread):
    """Background thread voor resource URL testen."""
    test_result = Signal(str, bool, str)  # (resource_key, success, detail)

    def __init__(self, key: str, url: str, method: str = "GET", fallback_url: str = None):
        super().__init__()
        self.key = key
        self.url = url
        self.method = method
        self.fallback_url = fallback_url
        self._timeout = 4

    def run(self):
        """Test resource connectivity using configured method."""
        # Try primary URL
        if self._test_url(self.url, self.method):
            return

        # If primary fails and fallback exists, try fallback
        if self.fallback_url:
            if self._test_url(self.fallback_url, "HEAD"):
                return

        # Both failed
        self.test_result.emit(self.key, False, "All endpoints unavailable")

    def _test_url(self, url: str, method: str) -> bool:
        """Test a single URL. Returns True if successful, False otherwise."""
        try:
            headers = {"User-Agent": "HAMIOS/5.4 (Resource Monitor)"}
            req = urlreq.Request(url, headers=headers)

            # Use configured method (HEAD or GET)
            if method.upper() == "HEAD":
                req.get_method = lambda: "HEAD"
                try:
                    with urlreq.urlopen(req, timeout=self._timeout) as response:
                        self.test_result.emit(self.key, response.status < 400, f"HTTP {response.status}")
                        return True
                except (urlerror.HTTPError, urlerror.URLError):
                    pass

            # Fallback to GET
            req.get_method = lambda: "GET"
            with urlreq.urlopen(req, timeout=self._timeout) as response:
                self.test_result.emit(self.key, response.status < 400, f"HTTP {response.status}")
                return True

        except (urlerror.URLError, Exception):
            return False


class ResourceManagerTab(QWidget):
    """Tab voor beheer van online resource URLs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._resources = ResourceConfig.load_resources()
        self._test_threads = {}
        self._build_ui()

    def _build_ui(self):
        """Build clean resource manager UI with only amber bars."""
        old_layout = self.layout()
        if old_layout is not None:
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        vlay = QVBoxLayout(self)
        vlay.setContentsMargins(12, 8, 12, 8)
        vlay.setSpacing(12)

        # ── File location section ──────────────────────────────────────────
        file_section = self._build_file_section()
        vlay.addWidget(file_section)

        vlay.addSpacing(4)

        # ── Resources list (amber bars only) ───────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ background: {BG_PANEL}; border: 1px solid {BORDER}; }}")

        container = QWidget()
        container_lay = QVBoxLayout(container)
        container_lay.setContentsMargins(0, 0, 0, 0)
        container_lay.setSpacing(2)

        # Add all resources
        for key, res in self._resources.items():
            self._add_resource_bar(container_lay, key, res)

        container_lay.addStretch()
        scroll.setWidget(container)
        vlay.addWidget(scroll, 1)

        # ── Buttons ────────────────────────────────────────────────────────
        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(8)

        btn_reset = QPushButton(tr("set.resources.reset"))
        btn_reset.setFixedWidth(120)
        btn_reset.clicked.connect(self._reset_resources)
        btn_lay.addWidget(btn_reset)

        btn_lay.addStretch()
        vlay.addLayout(btn_lay)

    def _build_file_section(self) -> QWidget:
        """Build file location info section."""
        widget = QWidget()
        lay = QVBoxLayout(widget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        # Title
        title = QLabel(tr("set.resources.title"))
        title_font = QFont("Segoe UI", 10)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {TEXT_H1};")
        lay.addWidget(title)

        # File path section
        file_lay = QHBoxLayout()
        file_lay.setSpacing(4)

        file_lbl = QLabel("Config file:")
        file_lbl.setFont(QFont("Segoe UI", 8))
        file_lbl.setStyleSheet(f"color: {TEXT_DIM};")
        file_lay.addWidget(file_lbl)

        file_path = QLineEdit(_RESOURCES_FILE)
        file_path.setFont(QFont("Consolas", 8))
        file_path.setReadOnly(True)
        file_path.setStyleSheet(f"QLineEdit {{ background: {BG_SURFACE}; color: {TEXT_BODY}; border: 1px solid {BORDER}; padding: 2px; }}")
        file_lay.addWidget(file_path)

        btn_copy = QPushButton("Copy")
        btn_copy.setFixedWidth(50)
        btn_copy.setFont(QFont("Segoe UI", 8))
        btn_copy.clicked.connect(lambda: self._copy_to_clipboard(_RESOURCES_FILE))
        file_lay.addWidget(btn_copy)

        lay.addLayout(file_lay)

        return widget

    def _add_resource_bar(self, parent_lay: QVBoxLayout, key: str, resource: dict):
        """Add single resource as amber bar."""
        # Main container
        bar = QWidget()
        bar_lay = QVBoxLayout(bar)
        bar_lay.setContentsMargins(8, 4, 8, 4)
        bar_lay.setSpacing(3)

        # Header: name + description (amber with black text)
        header_lay = QHBoxLayout()
        header_lay.setSpacing(8)

        name_lbl = QLabel(resource.get("name", key))
        name_font = QFont("Segoe UI", 9)
        name_font.setBold(True)
        name_lbl.setFont(name_font)
        name_lbl.setStyleSheet("color: #000000;")
        header_lay.addWidget(name_lbl)

        desc_lbl = QLabel(resource.get("description", ""))
        desc_font = QFont("Segoe UI", 8)
        desc_lbl.setFont(desc_font)
        desc_lbl.setStyleSheet("color: #1a1a1a;")
        header_lay.addWidget(desc_lbl)

        header_lay.addStretch()

        # Method indicator
        method = resource.get("method", "GET")
        method_lbl = QLabel(f"[{method}]")
        method_font = QFont("Segoe UI", 7)
        method_lbl.setFont(method_font)
        method_lbl.setStyleSheet("color: #1a1a1a; font-weight: bold;")
        header_lay.addWidget(method_lbl)

        bar_lay.addLayout(header_lay)

        # URL input + buttons
        url_lay = QHBoxLayout()
        url_lay.setSpacing(4)

        url_edit = QLineEdit(resource.get("url", ""))
        url_edit.setFont(QFont("Consolas", 8))
        url_edit.setStyleSheet(f"QLineEdit {{ background: {BG_SURFACE}; color: {TEXT_BODY}; border: 1px solid {BORDER}; padding: 2px; }}")
        url_lay.addWidget(url_edit)

        btn_test = QPushButton("Test")
        btn_test.setFixedWidth(50)
        btn_test.setFont(QFont("Segoe UI", 8))
        btn_test.clicked.connect(lambda: self._test_resource(key, url_edit.text(), resource.get("method", "GET")))
        url_lay.addWidget(btn_test)

        btn_inv = QPushButton("⚙")
        btn_inv.setFixedWidth(35)
        btn_inv.setFont(QFont("Segoe UI", 8))
        btn_inv.setToolTip(tr("set.resources.investigate"))
        btn_inv.clicked.connect(lambda: self._investigate_resource(key, resource))
        url_lay.addWidget(btn_inv)

        bar_lay.addLayout(url_lay)

        # Status label
        status_lbl = QLabel("")
        status_lbl.setFont(QFont("Segoe UI", 7))
        status_lbl.setStyleSheet(f"color: {TEXT_DIM};")
        status_lbl.setObjectName(f"status_{key}")
        bar_lay.addWidget(status_lbl)

        # Store references
        setattr(self, f"url_edit_{key}", url_edit)
        setattr(self, f"status_lbl_{key}", status_lbl)

        # Save on edit
        url_edit.editingFinished.connect(lambda: self._save_url(key, url_edit.text()))

        # Style bar with amber background
        bar.setStyleSheet("background: #C8A84B; border-radius: 2px;")
        parent_lay.addWidget(bar)

    def _test_resource(self, key: str, url: str, method: str):
        """Test resource URL."""
        if not url.strip():
            status_lbl = getattr(self, f"status_lbl_{key}", None)
            if status_lbl:
                status_lbl.setText("No URL provided")
                status_lbl.setStyleSheet("color: #FFA726;")
            return

        if key in self._test_threads:
            if self._test_threads[key].isRunning():
                self._test_threads[key].quit()
                self._test_threads[key].wait()

        # Get fallback URL if available
        resource = self._resources.get(key, {})
        fallback_url = resource.get("fallback_url", None)

        thread = ResourceTestThread(key, url, method, fallback_url)
        thread.test_result.connect(self._on_test_result)
        self._test_threads[key] = thread
        thread.start()

        status_lbl = getattr(self, f"status_lbl_{key}", None)
        if status_lbl:
            status_lbl.setText("Testing...")
            status_lbl.setStyleSheet(f"color: {TEXT_DIM};")

    def _on_test_result(self, key: str, success: bool, detail: str):
        """Handle test result."""
        status_lbl = getattr(self, f"status_lbl_{key}", None)
        if status_lbl:
            color = "#4CAF50" if success else "#EF5350"
            icon = "✓" if success else "✗"
            status_lbl.setText(f"{icon} {detail}")
            status_lbl.setStyleSheet(f"color: {color};")

    def _save_url(self, key: str, url: str):
        """Save URL change."""
        if ResourceConfig.update_resource(key, url):
            self._resources = ResourceConfig.load_resources()

    def _investigate_resource(self, key: str, resource: dict):
        """Open investigate dialog."""
        dialog = QMessageBox(self)
        dialog.setWindowTitle(f"{resource.get('name')} - {tr('set.resources.investigate')}")
        dialog.setText(
            f"Resource: {resource.get('name')}\n"
            f"Category: {resource.get('category')}\n"
            f"Current URL: {resource.get('url')}\n\n"
            f"{tr('set.resources.investigate_help')}"
        )
        dialog.exec()

    def _reset_resources(self):
        """Reset resources to defaults."""
        reply = QMessageBox.question(
            self,
            tr("set.resources.reset"),
            tr("set.resources.reset_confirm"),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            ResourceConfig.reset_to_defaults()
            self._resources = ResourceConfig.load_resources()
            for key, resource in self._resources.items():
                url_edit = getattr(self, f"url_edit_{key}", None)
                if url_edit:
                    url_edit.blockSignals(True)
                    url_edit.setText(resource.get("url", ""))
                    url_edit.blockSignals(False)
            QMessageBox.information(self, tr("set.resources.reset"), "Resources reset to defaults.")

    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copied", "File path copied to clipboard.")
