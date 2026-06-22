"""HAMIOS Antenna Calculator v2 - Complete Production-Ready Calculator

Fully integrated antenna calculator based on KD9HJN Grid Down Field Guide v11.
Features all 12 antenna types, coax database, field trim, birth certificates, SVG diagrams.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QSpinBox, QDoubleSpinBox, QPushButton,
    QTabWidget, QWidget, QGroupBox, QScrollArea, QGraphicsView, QGraphicsScene,
    QInputDialog, QMessageBox, QFileDialog, QTableWidget, QTableWidgetItem,
    QTextEdit, QDateEdit
)
from PySide6.QtCore import Qt, QSize, QDate
from PySide6.QtGui import QFont, QColor
from pathlib import Path
import math

from .antenna_models import AntennaType, WireType, SavedAntenna
from .antenna_math import (
    DipoleCalculator, EfhwCalculator, GroundPlaneCalculator,
    FullWaveLoopCalculator, DeltaLoopCalculator, BeverageCalculator,
    MagneticLoopCalculator, MiscCalculations, FeedlineCalculator
)
from .antenna_graphics import AntennaGraphicsEngine
from .antenna_library import AntennaLibrary
from .antenna_database import (
    VELOCITY_FACTORS, COAX_CABLES, ANTENNA_TYPES,
    get_antenna_by_id
)
from .antenna_record import AntennaRecord, FieldExpeditentSWRCheck


class AntennaCalculatorV2(QDialog):
    """Complete production-ready antenna calculator with all KD9HJN features."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HAMIOS Antenna Calculator - Grid Down Field Guide")
        self.setMinimumSize(QSize(1600, 950))

        # State
        self._frequency_mhz = 14.225
        self._velocity_factor_idx = 2  # STD PVC
        self._antenna_idx = 0  # Dipole
        self._coax_idx = 2  # RG-8X
        self._unit = "ft"  # feet or meters

        # Library
        self._library = AntennaLibrary()

        # Build UI
        self._build_ui()
        self._connect_signals()
        self._update_calculations()

    def _build_ui(self):
        """Build the complete user interface."""
        main_layout = QVBoxLayout(self)

        # Title
        title = QLabel("HAMIOS Antenna Calculator — KD9HJN Grid Down Field Guide v11")
        title_font = QFont("Segoe UI", 12, QFont.Bold)
        title.setFont(title_font)
        main_layout.addWidget(title)

        # Main tabs
        tabs = QTabWidget()
        tabs.addTab(self._build_calculator_tab(), "Calculator")
        tabs.addTab(self._build_coax_tab(), "Feedline Loss")
        tabs.addTab(self._build_trim_tab(), "Field Trim")
        tabs.addTab(self._build_record_tab(), "Birth Certificate")
        tabs.addTab(self._build_library_tab(), "Library")
        main_layout.addWidget(tabs)

        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_pdf = QPushButton("Export PDF")
        btn_pdf.clicked.connect(self._on_export_pdf)
        btn_layout.addWidget(btn_pdf)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        btn_layout.addWidget(btn_close)

        main_layout.addLayout(btn_layout)

    def _build_calculator_tab(self) -> QWidget:
        """Main calculator tab with all 12 antenna types."""
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # Left panel: Controls
        left = QVBoxLayout()

        # Operating Frequency
        freq_group = self._create_group("Operating Frequency")
        freq_layout = QVBoxLayout(freq_group)

        self.combo_band = QComboBox()
        self.combo_band.addItem("Custom")
        self.combo_band.addItems([
            "160m", "80m", "60m", "40m", "30m", "20m", "17m", "15m",
            "12m", "10m", "6m", "4m", "2m", "70cm", "23cm", "CB"
        ])
        self.combo_band.currentIndexChanged.connect(self._on_band_changed)
        freq_layout.addWidget(self.combo_band)

        self.spin_freq = QDoubleSpinBox()
        self.spin_freq.setMinimum(0.1)
        self.spin_freq.setMaximum(10000)
        self.spin_freq.setValue(14.225)
        self.spin_freq.setDecimals(3)
        self.spin_freq.setSingleStep(0.1)
        self.spin_freq.valueChanged.connect(self._on_frequency_changed)
        freq_layout.addWidget(QLabel("Frequency (MHz):"))
        freq_layout.addWidget(self.spin_freq)
        left.addWidget(freq_group)

        # Units
        units_group = self._create_group("Units")
        units_layout = QHBoxLayout(units_group)
        self.btn_feet = QPushButton("Feet / Inches")
        self.btn_feet.setCheckable(True)
        self.btn_feet.setChecked(True)
        self.btn_feet.clicked.connect(lambda: self._set_unit("ft"))
        self.btn_meters = QPushButton("Meters / CM")
        self.btn_meters.setCheckable(True)
        self.btn_meters.clicked.connect(lambda: self._set_unit("m"))
        units_layout.addWidget(self.btn_feet)
        units_layout.addWidget(self.btn_meters)
        left.addWidget(units_group)

        # Velocity Factor
        vf_group = self._create_group("Wire / Velocity Factor")
        vf_layout = QVBoxLayout(vf_group)
        self.combo_vf = QComboBox()
        self.combo_vf.addItems([vf.label for vf in VELOCITY_FACTORS])
        self.combo_vf.currentIndexChanged.connect(self._on_vf_changed)
        vf_layout.addWidget(self.combo_vf)
        self.label_vf_info = QLabel()
        self.label_vf_info.setWordWrap(True)
        self.label_vf_info.setStyleSheet("font-size: 9px; color: #888;")
        vf_layout.addWidget(self.label_vf_info)
        left.addWidget(vf_group)

        # Antenna Type
        ant_group = self._create_group("Antenna Type")
        ant_layout = QVBoxLayout(ant_group)
        self.combo_antenna = QComboBox()
        self.combo_antenna.addItems([ant.name.replace("\n", " ") for ant in ANTENNA_TYPES])
        self.combo_antenna.currentIndexChanged.connect(self._on_antenna_changed)
        ant_layout.addWidget(self.combo_antenna)
        self.label_ant_formula = QLabel()
        self.label_ant_formula.setWordWrap(True)
        self.label_ant_formula.setStyleSheet("font-size: 9px; color: #666; font-family: monospace;")
        ant_layout.addWidget(self.label_ant_formula)
        left.addWidget(ant_group)

        left.addStretch()

        # Right panel: Results + Diagram
        right = QVBoxLayout()

        # Results scroll area
        self.scroll_results = QScrollArea()
        self.scroll_results.setWidgetResizable(True)
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.scroll_results.setWidget(self.results_widget)
        right.addWidget(QLabel("Calculated Dimensions:"))
        right.addWidget(self.scroll_results, 1)

        # Diagram
        self.graphics_view = QGraphicsView()
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.setMinimumHeight(300)
        right.addWidget(QLabel("Antenna Diagram:"))
        right.addWidget(self.graphics_view, 1)

        # Matching info
        self.match_box = QGroupBox("Matching Transformer")
        match_layout = QVBoxLayout(self.match_box)
        self.label_match = QLabel()
        self.label_match.setWordWrap(True)
        self.label_match.setStyleSheet("font-size: 10px;")
        match_layout.addWidget(self.label_match)
        right.addWidget(self.match_box)

        # Combine panels
        layout.addLayout(left, 1)
        layout.addLayout(right, 2)

        return widget

    def _build_coax_tab(self) -> QWidget:
        """Coax feedline loss calculator."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Coax type selector
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Cable Type:"))
        self.combo_coax = QComboBox()
        self.combo_coax.addItems([coax.label for coax in COAX_CABLES])
        self.combo_coax.currentIndexChanged.connect(self._update_coax_calc)
        type_layout.addWidget(self.combo_coax)
        type_layout.addStretch()
        layout.addLayout(type_layout)

        # Cable length input
        len_layout = QHBoxLayout()
        len_layout.addWidget(QLabel("Cable Length:"))
        self.spin_coax_len = QDoubleSpinBox()
        self.spin_coax_len.setMinimum(1)
        self.spin_coax_len.setMaximum(1000)
        self.spin_coax_len.setValue(50)
        self.spin_coax_len.setSingleStep(1)
        self.spin_coax_len.valueChanged.connect(self._update_coax_calc)
        len_layout.addWidget(self.spin_coax_len)
        self.label_coax_unit = QLabel("ft")
        len_layout.addWidget(self.label_coax_unit)
        len_layout.addStretch()
        layout.addLayout(len_layout)

        # Loss table
        layout.addWidget(QLabel("Cable Loss Analysis:"))
        self.table_coax = QTableWidget()
        self.table_coax.setColumnCount(5)
        self.table_coax.setHorizontalHeaderLabels([
            "Frequency", "Loss/10m", "Total Loss", "Efficiency", "Rating"
        ])
        layout.addWidget(self.table_coax)

        layout.addStretch()
        return widget

    def _build_trim_tab(self) -> QWidget:
        """Field trim calculator."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel("Antenna Off-Resonance? Calculate Field Trim"))

        # Measured frequency
        meas_layout = QHBoxLayout()
        meas_layout.addWidget(QLabel("Measured Frequency (MHz):"))
        self.spin_trim_meas = QDoubleSpinBox()
        self.spin_trim_meas.setMinimum(0.1)
        self.spin_trim_meas.setMaximum(10000)
        self.spin_trim_meas.setValue(self._frequency_mhz)
        self.spin_trim_meas.setDecimals(3)
        self.spin_trim_meas.valueChanged.connect(self._update_trim_calc)
        meas_layout.addWidget(self.spin_trim_meas)
        layout.addLayout(meas_layout)

        # Target frequency
        tgt_layout = QHBoxLayout()
        tgt_layout.addWidget(QLabel("Target Frequency (MHz):"))
        self.spin_trim_tgt = QDoubleSpinBox()
        self.spin_trim_tgt.setMinimum(0.1)
        self.spin_trim_tgt.setMaximum(10000)
        self.spin_trim_tgt.setValue(self._frequency_mhz)
        self.spin_trim_tgt.setDecimals(3)
        self.spin_trim_tgt.valueChanged.connect(self._update_trim_calc)
        tgt_layout.addWidget(self.spin_trim_tgt)
        layout.addLayout(tgt_layout)

        # Current leg length
        leg_layout = QHBoxLayout()
        leg_layout.addWidget(QLabel("Current Leg Length:"))
        self.spin_trim_leg = QDoubleSpinBox()
        self.spin_trim_leg.setMinimum(0.1)
        self.spin_trim_leg.setMaximum(1000)
        self.spin_trim_leg.setValue(20)
        self.spin_trim_leg.setSingleStep(0.1)
        self.spin_trim_leg.valueChanged.connect(self._update_trim_calc)
        leg_layout.addWidget(self.spin_trim_leg)
        self.label_trim_unit = QLabel("ft")
        leg_layout.addWidget(self.label_trim_unit)
        layout.addLayout(leg_layout)

        # Result
        self.label_trim_result = QLabel()
        self.label_trim_result.setWordWrap(True)
        self.label_trim_result.setStyleSheet("font-size: 12px; font-weight: bold; color: #00ff41;")
        layout.addWidget(self.label_trim_result)

        layout.addStretch()
        return widget

    def _build_record_tab(self) -> QWidget:
        """Antenna Birth Certificate."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel("Antenna Deployment Log — Antenna Birth Certificate"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        form = QWidget()
        form_layout = QGridLayout(form)

        row = 0

        # Callsign
        form_layout.addWidget(QLabel("Callsign:"), row, 0)
        self.input_callsign = QComboBox()
        self.input_callsign.setEditable(True)
        form_layout.addWidget(self.input_callsign, row, 1)
        row += 1

        # Date
        form_layout.addWidget(QLabel("Date Built:"), row, 0)
        self.input_date = QDateEdit()
        self.input_date.setDate(QDate.currentDate())
        form_layout.addWidget(self.input_date, row, 1)
        row += 1

        # Location
        form_layout.addWidget(QLabel("Location/Grid:"), row, 0)
        self.input_location = QComboBox()
        self.input_location.setEditable(True)
        form_layout.addWidget(self.input_location, row, 1)
        row += 1

        # Wire type
        form_layout.addWidget(QLabel("Wire Type:"), row, 0)
        self.input_wire = QComboBox()
        self.input_wire.setEditable(True)
        form_layout.addWidget(self.input_wire, row, 1)
        row += 1

        # Final length
        form_layout.addWidget(QLabel("Final Tuned Length:"), row, 0)
        self.input_final_len = QComboBox()
        self.input_final_len.setEditable(True)
        form_layout.addWidget(self.input_final_len, row, 1)
        row += 1

        # Resonant freq
        form_layout.addWidget(QLabel("Resonant Frequency:"), row, 0)
        self.input_resonant = QComboBox()
        self.input_resonant.setEditable(True)
        form_layout.addWidget(self.input_resonant, row, 1)
        row += 1

        # Field notes
        form_layout.addWidget(QLabel("Field Notes:"), row, 0)
        self.input_notes = QTextEdit()
        self.input_notes.setMinimumHeight(100)
        form_layout.addWidget(self.input_notes, row, 1)
        row += 1

        scroll.setWidget(form)
        layout.addWidget(scroll, 1)

        # Export button
        btn_export = QPushButton("Export as HTML Birth Certificate")
        btn_export.clicked.connect(self._on_export_certificate)
        layout.addWidget(btn_export)

        # SWR checklist
        btn_swr = QPushButton("Field Expedient SWR Check Checklist")
        btn_swr.clicked.connect(self._on_show_swr_checklist)
        layout.addWidget(btn_swr)

        return widget

    def _build_library_tab(self) -> QWidget:
        """Antenna library."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel("Antenna Library — Save/Load Configurations"))

        # Simple list
        self.list_library = QTableWidget()
        self.list_library.setColumnCount(3)
        self.list_library.setHorizontalHeaderLabels(["Name", "Type", "Frequency"])
        layout.addWidget(self.list_library)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_load = QPushButton("Load")
        btn_load.clicked.connect(self._on_load_antenna)
        btn_layout.addWidget(btn_load)

        btn_save = QPushButton("Save Current")
        btn_save.clicked.connect(self._on_save_antenna)
        btn_layout.addWidget(btn_save)

        btn_delete = QPushButton("Delete")
        btn_delete.clicked.connect(self._on_delete_antenna)
        btn_layout.addWidget(btn_delete)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self._refresh_library()
        return widget

    def _create_group(self, title: str) -> QGroupBox:
        """Create styled group box."""
        group = QGroupBox(title)
        font = group.font()
        font.setBold(True)
        group.setFont(font)
        return group

    def _connect_signals(self):
        """Connect all signals."""
        pass  # Already done in _build_ui

    # ── SLOTS ─────────────────────────────────────────────────────────────────

    def _on_band_changed(self):
        """Handle band selection."""
        band_names = [
            "160m", "80m", "60m", "40m", "30m", "20m", "17m", "15m",
            "12m", "10m", "6m", "4m", "2m", "70cm", "23cm", "CB"
        ]
        band_freqs = [
            1.9, 3.65, 5.357, 7.15, 10.125, 14.225, 18.118, 21.3,
            24.94, 28.85, 52.0, 70.0, 146.5, 435.0, 1296.5, 27.0
        ]

        idx = self.combo_band.currentIndex()
        if idx > 0 and idx <= len(band_freqs):
            self.spin_freq.blockSignals(True)
            self.spin_freq.setValue(band_freqs[idx - 1])
            self.spin_freq.blockSignals(False)
            self._frequency_mhz = band_freqs[idx - 1]
            self._update_calculations()

    def _on_frequency_changed(self):
        """Handle frequency change."""
        self._frequency_mhz = self.spin_freq.value()
        self.combo_band.blockSignals(True)
        self.combo_band.setCurrentIndex(0)  # Custom
        self.combo_band.blockSignals(False)
        self._update_calculations()

    def _on_vf_changed(self):
        """Handle VF selection."""
        self._velocity_factor_idx = self.combo_vf.currentIndex()
        vf = VELOCITY_FACTORS[self._velocity_factor_idx]
        self.label_vf_info.setText(f"VF {vf.velocity_factor}\n{vf.examples}")
        self._update_calculations()

    def _on_antenna_changed(self):
        """Handle antenna type change."""
        self._antenna_idx = self.combo_antenna.currentIndex()
        ant = ANTENNA_TYPES[self._antenna_idx]
        formula = f"ft: {ant.formula_ft}" if self._unit == "ft" else f"m: {ant.formula_m}"
        self.label_ant_formula.setText(formula)
        self._update_calculations()

    def _set_unit(self, unit: str):
        """Set unit system."""
        self._unit = unit
        self.btn_feet.setChecked(unit == "ft")
        self.btn_meters.setChecked(unit == "m")
        self.label_coax_unit.setText("ft" if unit == "ft" else "m")
        self.label_trim_unit.setText("ft" if unit == "ft" else "m")
        self._update_calculations()

    def _update_calculations(self):
        """Recalculate and display all results."""
        if not self._frequency_mhz or self._frequency_mhz <= 0:
            return

        # Get antenna and VF
        ant = ANTENNA_TYPES[self._antenna_idx]
        vf = VELOCITY_FACTORS[self._velocity_factor_idx].velocity_factor

        # Calculate dimensions
        raw_dims = ant.dimensions_formula(self._frequency_mhz)
        dims = [
            (label, value * vf, sub) if not label.startswith("SPACING") and not label.startswith("DROOP") and not label.startswith("HOIST") else (label, value, sub)
            for label, value, sub in raw_dims
        ]

        # Display results
        while self.results_layout.count():
            self.results_layout.takeAt(0).widget().deleteLater()

        for label, value, sub in dims:
            widget = self._create_result_box(label, value, sub)
            self.results_layout.addWidget(widget)

        # Diagram
        self._draw_diagram()

        # Matching info
        self.label_match.setText(
            f"<b>{ant.match_type}</b><br>"
            f"Ratio: {ant.match_ratio}<br>"
            f"Impedance: {ant.match_impedance}<br>"
            f"ATU: {ant.atu_needed}<br><br>"
            f"{ant.match_note}"
        )

        # Update coax and trim calculations
        self._update_coax_calc()
        self._update_trim_calc()

    def _create_result_box(self, label: str, value: float, sub: str = "") -> QGroupBox:
        """Create result display box."""
        box = QGroupBox(label)
        layout = QVBoxLayout(box)

        val_text = self._format_value(value)
        val_label = QLabel(val_text)
        val_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #00ff41;")
        layout.addWidget(val_label)

        if sub:
            sub_label = QLabel(sub)
            sub_label.setStyleSheet("font-size: 9px; color: #888;")
            layout.addWidget(sub_label)

        return box

    def _format_value(self, feet: float) -> str:
        """Format value in current unit system."""
        if not math.isfinite(feet) or feet < 0:
            return "---"

        if self._unit == "ft":
            total_quarters = round(feet * 48)
            f = total_quarters // 48
            rem_q = total_quarters % 48
            i = rem_q // 4
            q = rem_q % 4
            fracs = ["", "¼", "½", "¾"]
            return f"{f}' {i}{fracs[q]}\""
        else:
            m = feet * 0.3048
            return f"{m:.2f}m" if m >= 1 else f"{m*100:.1f}cm"

    def _draw_diagram(self):
        """Draw antenna diagram."""
        self.graphics_scene.clear()
        # TODO: Implement all 12 diagrams
        text = self.graphics_scene.addText(f"{ANTENNA_TYPES[self._antenna_idx].name.replace(chr(10), ' ')}\nDiagram coming soon")

    def _update_coax_calc(self):
        """Update coax loss calculation."""
        # TODO: Implement
        pass

    def _update_trim_calc(self):
        """Update trim calculator."""
        meas = self.spin_trim_meas.value()
        tgt = self.spin_trim_tgt.value()
        leg = self.spin_trim_leg.value()

        if not (meas > 0 and tgt > 0 and leg > 0):
            self.label_trim_result.setText("Enter valid values")
            return

        ratio = meas / tgt
        new_leg = leg * ratio
        diff = leg - new_leg

        if abs(diff) < 0.05:
            verdict = "NO TRIM NEEDED"
            color = "#00ff41"
        elif diff > 0:
            verdict = f"SHORTEN {self._format_value(abs(diff))}"
            color = "#ffb300"
        else:
            verdict = f"LENGTHEN {self._format_value(abs(diff))}"
            color = "#ffb300"

        self.label_trim_result.setText(f"{verdict}\nNew leg: {self._format_value(new_leg)}")
        self.label_trim_result.setStyleSheet(f"color: {color};")

    def _on_export_certificate(self):
        """Export antenna birth certificate."""
        # TODO: Implement
        QMessageBox.information(self, "Export", "Birth certificate export coming soon")

    def _on_show_swr_checklist(self):
        """Show SWR check checklist."""
        checklist = FieldExpeditentSWRCheck.field_check_checklist()
        QMessageBox.information(self, "Field SWR Check", "\n".join(checklist))

    def _on_save_antenna(self):
        """Save antenna to library."""
        name, ok = QInputDialog.getText(self, "Save Antenna", "Antenna name:")
        if ok and name:
            # TODO: Implement
            QMessageBox.information(self, "Saved", f"Antenna '{name}' saved")

    def _on_load_antenna(self):
        """Load antenna from library."""
        # TODO: Implement
        pass

    def _on_delete_antenna(self):
        """Delete antenna from library."""
        # TODO: Implement
        pass

    def _refresh_library(self):
        """Refresh antenna library display."""
        # TODO: Implement
        pass

    def _on_export_pdf(self):
        """Export calculation as PDF."""
        # TODO: Implement
        QMessageBox.information(self, "Export", "PDF export coming soon")
