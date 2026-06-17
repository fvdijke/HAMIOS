"""HAMIOS v5.3 - Resource Manager Tab for Settings"""

import urllib.request as urlreq
import urllib.error as urlerror
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QDialog
)

from .resources_config import ResourceConfig, DEFAULT_RESOURCES
from .i18n import tr
from .theme import BG_PANEL, BG_SURFACE, TEXT_H1, TEXT_BODY, TEXT_DIM, BORDER, ACCENT


class ResourceTestThread(QThread):
    """Background thread voor resource URL testen."""
    test_result = Signal(str, bool, str)  # (resource_key, success, detail)

    def __init__(self, key: str, url: str):
        super().__init__()
        self.key = key
        self.url = url
        self._timeout = 4

    def run(self):
        """Test resource connectivity."""
        try:
            headers = {"User-Agent": "HAMIOS/5.3 (Resource Monitor)"}
            req = urlreq.Request(self.url, headers=headers)

            # Probeer HEAD eerst
            req.get_method = lambda: "HEAD"
            try:
                with urlreq.urlopen(req, timeout=self._timeout) as response:
                    status = response.status
                    self.test_result.emit(self.key, status < 400, f"HTTP {status}")
                    return
            except (urlerror.HTTPError, urlerror.URLError):
                pass

            # Fallback naar GET
            req.get_method = lambda: "GET"
            with urlreq.urlopen(req, timeout=self._timeout) as response:
                status = response.status
                self.test_result.emit(self.key, status < 400, f"HTTP {status}")

        except urlerror.URLError as e:
            self.test_result.emit(self.key, False, f"Connection: {str(e)[:20]}")
        except Exception as e:
            self.test_result.emit(self.key, False, f"Error: {str(e)[:20]}")


class ResourceManagerTab(QWidget):
    """Tab voor beheer van online resource URLs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._resources = ResourceConfig.load_resources()
        self._test_threads = {}
        self._build_ui()

    def _build_ui(self):
        """Bouw de resource manager UI."""
        # Remove existing layout if any
        old_layout = self.layout()
        if old_layout:
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.setLayout(None)

        vlay = QVBoxLayout(self)
        vlay.setContentsMargins(12, 8, 12, 8)
        vlay.setSpacing(8)

        # Titel
        title = QLabel(tr("set.resources.title"))
        title_font = QFont("Segoe UI", 10)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {TEXT_H1};")
        vlay.addWidget(title)

        # Info tekst
        info = QLabel(tr("set.resources.info"))
        info_font = QFont("Segoe UI", 8)
        info.setFont(info_font)
        info.setStyleSheet(f"color: {TEXT_DIM};")
        info.setWordWrap(True)
        vlay.addWidget(info)

        # Resources tabel in scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ background: {BG_PANEL}; border: 1px solid {BORDER}; }}")

        container = QWidget()
        container_lay = QVBoxLayout(container)
        container_lay.setContentsMargins(0, 0, 0, 0)
        container_lay.setSpacing(4)

        # Per categorie
        categories = ResourceConfig.get_categories()
        for category in categories:
            cat_resources = {k: v for k, v in self._resources.items() if v.get("category") == category}
            if not cat_resources:
                continue

            # Categorie header
            cat_lbl = QLabel(category)
            cat_font = QFont("Segoe UI", 9)
            cat_font.setBold(True)
            cat_lbl.setFont(cat_font)
            cat_lbl.setStyleSheet(f"color: {ACCENT};")
            container_lay.addWidget(cat_lbl)

            # Resources in categorie
            for key, res in cat_resources.items():
                self._add_resource_row(container_lay, key, res)

        container_lay.addStretch()
        scroll.setWidget(container)
        vlay.addWidget(scroll)

        # Buttons
        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(8)

        btn_reset = QPushButton(tr("set.resources.reset"))
        btn_reset.setFixedWidth(120)
        btn_reset.clicked.connect(self._reset_resources)
        btn_lay.addWidget(btn_reset)

        btn_lay.addStretch()
        vlay.addLayout(btn_lay)

    def _add_resource_row(self, parent_lay: QVBoxLayout, key: str, resource: dict):
        """Voeg een resource rij toe."""
        row_lay = QVBoxLayout()
        row_lay.setSpacing(4)
        row_lay.setContentsMargins(8, 4, 8, 4)

        # Header: naam + beschrijving
        header_lay = QHBoxLayout()
        header_lay.setSpacing(8)

        name_lbl = QLabel(resource.get("name", key))
        name_font = QFont("Segoe UI", 8)
        name_font.setBold(True)
        name_lbl.setFont(name_font)
        name_lbl.setStyleSheet(f"color: {TEXT_H1};")
        header_lay.addWidget(name_lbl)

        desc_lbl = QLabel(resource.get("description", ""))
        desc_font = QFont("Segoe UI", 8)
        desc_lbl.setFont(desc_font)
        desc_lbl.setStyleSheet(f"color: {TEXT_DIM};")
        header_lay.addWidget(desc_lbl)

        header_lay.addStretch()
        row_lay.addLayout(header_lay)

        # URL input
        url_lay = QHBoxLayout()
        url_lay.setSpacing(4)

        url_lbl = QLabel("URL:")
        url_lbl.setFont(QFont("Segoe UI", 8))
        url_lbl.setFixedWidth(30)
        url_lay.addWidget(url_lbl)

        url_edit = QLineEdit(resource.get("url", ""))
        url_edit.setFont(QFont("Consolas", 8))
        url_edit.setStyleSheet(
            f"QLineEdit {{ background: {BG_SURFACE}; color: {TEXT_BODY}; "
            f"border: 1px solid {BORDER}; padding: 2px; }}"
        )
        url_lay.addWidget(url_edit)

        # Test button
        btn_test = QPushButton("Test")
        btn_test.setFixedWidth(60)
        btn_test.setFont(QFont("Segoe UI", 8))
        btn_test.clicked.connect(lambda: self._test_resource(key, url_edit.text()))
        url_lay.addWidget(btn_test)

        # Investigate button
        btn_inv = QPushButton("⚙")
        btn_inv.setFixedWidth(40)
        btn_inv.setToolTip(tr("set.resources.investigate"))
        btn_inv.clicked.connect(lambda: self._investigate_resource(key, resource))
        url_lay.addWidget(btn_inv)

        # Save on edit
        url_edit.editingFinished.connect(
            lambda: self._save_url(key, url_edit.text())
        )

        row_lay.addLayout(url_lay)

        # Status label
        status_lbl = QLabel("")
        status_lbl.setFont(QFont("Segoe UI", 7))
        status_lbl.setStyleSheet(f"color: {TEXT_DIM};")
        status_lbl.setObjectName(f"status_{key}")
        row_lay.addWidget(status_lbl)

        # Store references
        setattr(self, f"url_edit_{key}", url_edit)
        setattr(self, f"status_lbl_{key}", status_lbl)

        # Add to parent
        row_widget = QWidget()
        row_widget.setLayout(row_lay)
        row_widget.setStyleSheet(f"background: {BG_SURFACE}; border-radius: 2px;")
        parent_lay.addWidget(row_widget)

    def _test_resource(self, key: str, url: str):
        """Test resource URL."""
        if not url.strip():
            status_lbl = getattr(self, f"status_lbl_{key}", None)
            if status_lbl:
                status_lbl.setText("No URL provided")
                status_lbl.setStyleSheet(f"color: #FFA726;")
            return

        # Kill previous thread
        if key in self._test_threads:
            if self._test_threads[key].isRunning():
                self._test_threads[key].quit()
                self._test_threads[key].wait()

        # Start test
        thread = ResourceTestThread(key, url)
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
        """Open investigate dialog for resource."""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{resource.get('name')} - {tr('set.resources.investigate')}")
        dialog.setGeometry(100, 100, 600, 400)

        lay = QVBoxLayout(dialog)

        # Info
        info = QLabel(
            f"Resource: {resource.get('name')}\n"
            f"Category: {resource.get('category')}\n"
            f"Current URL: {resource.get('url')}"
        )
        info.setFont(QFont("Segoe UI", 8))
        info.setWordWrap(True)
        lay.addWidget(info)

        # Instructions
        instructions = QLabel(
            tr("set.resources.investigate_help")
        )
        instructions.setFont(QFont("Segoe UI", 8))
        instructions.setStyleSheet(f"color: {TEXT_DIM};")
        instructions.setWordWrap(True)
        lay.addWidget(instructions)

        # Common URLs for this resource
        if key in DEFAULT_RESOURCES:
            alt_lbl = QLabel("Alternative URLs:")
            alt_lbl.setFont(QFont("Segoe UI", 9))
            alt_lbl.setStyleSheet(f"color: {TEXT_H1};")
            lay.addWidget(alt_lbl)

            # Hier kunnen we alternative URLs tonen (voor toekomstige uitbreiding)
            alt_info = QLabel(
                "To find the correct URL:\n"
                "1. Visit the resource website\n"
                "2. Look for API documentation\n"
                "3. Check data format and endpoint\n"
                "4. Test the URL in this dialog"
            )
            alt_info.setFont(QFont("Segoe UI", 8))
            alt_info.setStyleSheet(f"color: {TEXT_BODY};")
            alt_info.setWordWrap(True)
            lay.addWidget(alt_info)

        lay.addStretch()

        # Close button
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(dialog.accept)
        lay.addWidget(btn_close)

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
            # Clear current layout
            layout = self.layout()
            if layout:
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
            # Rebuild UI
            self._build_ui()
