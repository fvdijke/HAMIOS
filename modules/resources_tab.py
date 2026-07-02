"""HAMIOS - Simple Resource Manager Tab for Settings"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QLineEdit, QPushButton
)

from .resources_config import ResourceConfig, DEFAULT_RESOURCES
from .theme import BG_PANEL, BG_SURFACE, TEXT_H1, TEXT_BODY, TEXT_DIM, BORDER


class ResourceManagerTab(QWidget):
    """Simple resource manager - show and edit resource URLs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._resources = ResourceConfig()
        self._editors = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Title
        title = QLabel("Online Resources")
        title.setStyleSheet(f"color: {TEXT_H1}; font-weight: bold; font-size: 11pt;")
        layout.addWidget(title)

        # Scrollable area for resources
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"background: {BG_PANEL}; border: 1px solid {BORDER};")

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(12)
        scroll_layout.setContentsMargins(8, 8, 8, 8)

        # Add each resource
        for key, config in DEFAULT_RESOURCES.items():
            row = QHBoxLayout()
            row.setSpacing(8)

            # Resource name + description
            left = QVBoxLayout()
            name_lbl = QLabel(config["name"])
            name_lbl.setStyleSheet(f"color: {TEXT_H1}; font-weight: bold;")
            left.addWidget(name_lbl)

            desc_lbl = QLabel(config.get("description", ""))
            desc_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 8pt;")
            left.addWidget(desc_lbl)
            row.addLayout(left, 0)

            # URL input field
            url_edit = QLineEdit()
            url_edit.setText(getattr(self._resources, key, config["url"]))
            url_edit.setStyleSheet(
                f"QLineEdit {{ background: {BG_SURFACE}; color: {TEXT_BODY}; "
                f"border: 1px solid {BORDER}; padding: 4px; }}"
            )
            url_edit.setMinimumWidth(300)
            self._editors[key] = url_edit
            row.addWidget(url_edit, 1)

            scroll_layout.addLayout(row)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, 1)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton("Save")
        save_btn.setFixedWidth(80)
        save_btn.clicked.connect(self._save_resources)
        btn_layout.addWidget(save_btn)

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setFixedWidth(120)
        reset_btn.clicked.connect(self._reset_defaults)
        btn_layout.addWidget(reset_btn)

        layout.addLayout(btn_layout)

    def _save_resources(self):
        """Save edited URLs to config."""
        for key, url_edit in self._editors.items():
            setattr(self._resources, key, url_edit.text())
        self._resources.save()

    def _reset_defaults(self):
        """Reset all URLs to defaults."""
        for key, config in DEFAULT_RESOURCES.items():
            self._editors[key].setText(config["url"])
