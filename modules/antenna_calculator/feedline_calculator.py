"""HAMIOS Antenna Calculator - Feedline Calculator

Coax cable loss calculations for multiple frequencies.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QSpinBox, QDoubleSpinBox, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt

from .antenna_models import CoaxType, FeedlineSpecs
from .antenna_math import FeedlineCalculator


# ── Predefined Coax Cables ────────────────────────────────────────────────────

COAX_SPECS = {
    CoaxType.RG58: FeedlineSpecs(
        name="RG58",
        impedance_ohms=50,
        velocity_factor=0.66,
        loss_db_per_10m={
            1.9: 0.45,
            3.5: 0.60,
            7.0: 0.85,
            14.0: 1.23,
            28.0: 1.80,
            50.0: 2.40,
            144.0: 5.60,
        }
    ),
    CoaxType.RG8X: FeedlineSpecs(
        name="RG8X",
        impedance_ohms=50,
        velocity_factor=0.82,
        loss_db_per_10m={
            1.9: 0.22,
            3.5: 0.28,
            7.0: 0.40,
            14.0: 0.58,
            28.0: 0.82,
            50.0: 1.10,
            144.0: 2.40,
        }
    ),
    CoaxType.RG213: FeedlineSpecs(
        name="RG213",
        impedance_ohms=50,
        velocity_factor=0.66,
        loss_db_per_10m={
            1.9: 0.20,
            3.5: 0.27,
            7.0: 0.38,
            14.0: 0.55,
            28.0: 0.78,
            50.0: 1.05,
            144.0: 2.40,
        }
    ),
    CoaxType.LMR240: FeedlineSpecs(
        name="LMR240",
        impedance_ohms=50,
        velocity_factor=0.80,
        loss_db_per_10m={
            1.9: 0.22,
            3.5: 0.28,
            7.0: 0.40,
            14.0: 0.58,
            28.0: 0.82,
            50.0: 1.10,
            144.0: 2.40,
        }
    ),
    CoaxType.LMR400: FeedlineSpecs(
        name="LMR400",
        impedance_ohms=50,
        velocity_factor=0.81,
        loss_db_per_10m={
            1.9: 0.10,
            3.5: 0.13,
            7.0: 0.19,
            14.0: 0.28,
            28.0: 0.41,
            50.0: 0.55,
            144.0: 1.20,
        }
    ),
}


class FeedlineCalculatorTab(QWidget):
    """Feedline loss calculator interface."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        """Build the feedline calculator UI."""
        layout = QVBoxLayout(self)

        # ── Input section ──────────────────────────────────────────────────────
        input_group_layout = QGridLayout()
        input_group_layout.setSpacing(10)

        # Cable type
        input_group_layout.addWidget(QLabel("Cable Type:"), 0, 0)
        self.combo_cable = QComboBox()
        self.combo_cable.addItems([spec.name for spec in COAX_SPECS.values()])
        self.combo_cable.currentIndexChanged.connect(self._on_cable_changed)
        input_group_layout.addWidget(self.combo_cable, 0, 1)

        # Cable length
        input_group_layout.addWidget(QLabel("Length:"), 0, 2)
        self.spin_length = QDoubleSpinBox()
        self.spin_length.setMinimum(1.0)
        self.spin_length.setMaximum(1000.0)
        self.spin_length.setValue(10.0)
        self.spin_length.setSingleStep(1.0)
        self.spin_length.setSuffix(" m")
        self.spin_length.valueChanged.connect(self._on_length_changed)
        input_group_layout.addWidget(self.spin_length, 0, 3)

        # Cable specs info
        self.label_cable_info = QLabel("")
        input_group_layout.addWidget(self.label_cable_info, 1, 0, 1, 4)

        layout.addLayout(input_group_layout)

        # ── Loss table ─────────────────────────────────────────────────────────
        layout.addWidget(QLabel("Cable Loss Analysis:"))

        self.table_loss = QTableWidget()
        self.table_loss.setColumnCount(5)
        self.table_loss.setHorizontalHeaderLabels([
            "Frequency", "Loss/10m", "Total Loss", "Efficiency", "Notes"
        ])
        self.table_loss.setColumnWidth(0, 100)
        self.table_loss.setColumnWidth(1, 100)
        self.table_loss.setColumnWidth(2, 100)
        self.table_loss.setColumnWidth(3, 100)
        self.table_loss.setColumnWidth(4, 200)
        layout.addWidget(self.table_loss)

        self._update_table()

    def _connect_signals(self):
        """Connect UI signals."""
        # Already connected in _build_ui
        pass

    def _on_cable_changed(self):
        """Handle cable type change."""
        self._update_table()

    def _on_length_changed(self):
        """Handle cable length change."""
        self._update_table()

    def _get_selected_coax(self) -> FeedlineSpecs:
        """Get currently selected coax specifications."""
        coax_types = list(COAX_SPECS.values())
        return coax_types[self.combo_cable.currentIndex()]

    def _update_table(self):
        """Update loss calculation table."""
        coax = self._get_selected_coax()
        length_m = self.spin_length.value()

        # Update cable info
        info_text = f"Impedance: {coax.impedance_ohms}Ω  |  Velocity Factor: {coax.velocity_factor}"
        self.label_cable_info.setText(info_text)

        # Update table
        self.table_loss.setRowCount(0)

        # Standard frequencies to calculate
        frequencies = [1.9, 3.5, 7.0, 14.0, 28.0, 50.0, 144.0, 432.5]

        for freq in frequencies:
            # Get loss per 10m
            loss_per_10m = coax.get_loss_at_freq(freq)
            if loss_per_10m == 0:
                continue

            # Calculate total loss
            total_loss = FeedlineCalculator.calculate_loss(loss_per_10m, length_m)

            # Convert to efficiency
            efficiency = FeedlineCalculator.loss_to_efficiency(total_loss)

            # Determine band and efficiency note
            if freq < 2:
                band = "160m+"
                efficiency_note = "Excellent" if efficiency > 95 else "Good" if efficiency > 90 else "Fair"
            elif freq < 4:
                band = "80m"
                efficiency_note = "Excellent" if efficiency > 95 else "Good" if efficiency > 90 else "Fair"
            elif freq < 8:
                band = "40m"
                efficiency_note = "Excellent" if efficiency > 95 else "Good" if efficiency > 90 else "Fair"
            elif freq < 15:
                band = "20m"
                efficiency_note = "Excellent" if efficiency > 95 else "Good" if efficiency > 90 else "Fair"
            elif freq < 30:
                band = "10m"
                efficiency_note = "Excellent" if efficiency > 95 else "Good" if efficiency > 90 else "Fair"
            elif freq < 60:
                band = "6m"
                efficiency_note = "Excellent" if efficiency > 95 else "Good" if efficiency > 90 else "Fair"
            elif freq < 200:
                band = "2m"
                efficiency_note = "Good" if efficiency > 90 else "Fair" if efficiency > 80 else "Poor"
            else:
                band = "70cm+"
                efficiency_note = "Fair" if efficiency > 80 else "Poor"

            # Add row
            row = self.table_loss.rowCount()
            self.table_loss.insertRow(row)

            freq_item = QTableWidgetItem(f"{freq} MHz ({band})")
            loss_item = QTableWidgetItem(f"{loss_per_10m:.2f} dB")
            total_item = QTableWidgetItem(f"{total_loss:.2f} dB")
            eff_item = QTableWidgetItem(f"{efficiency:.1f}%")
            note_item = QTableWidgetItem(efficiency_note)

            self.table_loss.setItem(row, 0, freq_item)
            self.table_loss.setItem(row, 1, loss_item)
            self.table_loss.setItem(row, 2, total_item)
            self.table_loss.setItem(row, 3, eff_item)
            self.table_loss.setItem(row, 4, note_item)

            # Color code efficiency
            if efficiency > 95:
                eff_item.setBackground(Qt.green)
            elif efficiency > 90:
                eff_item.setBackground(Qt.yellow)
            elif efficiency > 80:
                eff_item.setBackground(Qt.darkYellow)
            else:
                eff_item.setBackground(Qt.red)
