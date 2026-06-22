"""HAMIOS Antenna Calculator - Main GUI Dialog

Complete antenna calculator window with realtime calculations and graphics.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QSpinBox, QDoubleSpinBox, QPushButton,
    QTabWidget, QWidget, QGroupBox, QScrollArea, QGraphicsView, QGraphicsScene,
    QInputDialog, QMessageBox, QFileDialog, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
from pathlib import Path

from .antenna_models import (
    AntennaType, WireType, AMATEUR_BANDS, FrequencyBand,
    DipoleCalculation, EfhwCalculation, GroundPlaneCalculation,
    FullWaveLoopCalculation, DeltaLoopCalculation, BeverageCalculation,
    MagneticLoopCalculation, SavedAntenna
)
from .antenna_math import (
    DipoleCalculator, EfhwCalculator, GroundPlaneCalculator,
    FullWaveLoopCalculator, DeltaLoopCalculator, BeverageCalculator,
    MagneticLoopCalculator, MiscCalculations
)
from .antenna_graphics import AntennaGraphicsEngine
from .feedline_calculator import FeedlineCalculatorTab
from .antenna_library import AntennaLibrary
from .pdf_generator import PdfGenerator
from .antenna_record import AntennaRecord, FieldExpeditentSWRCheck


class AntennaCalculatorDialog(QDialog):
    """Main antenna calculator window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Antenna Calculator")
        self.setMinimumSize(QSize(1400, 900))

        # Current state
        self._current_antenna_type = AntennaType.DIPOLE
        self._current_frequency_mhz = 7.1
        self._current_velocity_factor = 0.95
        self._current_wire_type = WireType.BARE_COPPER

        # Initialize library
        self._library = AntennaLibrary()

        # Build UI
        self._build_ui()
        self._connect_signals()
        self._update_all_calculations()

    def _build_ui(self):
        """Build the user interface."""
        main_layout = QVBoxLayout(self)

        # ── Title ──────────────────────────────────────────────────────────────
        title = QLabel("Antenna Calculator")
        title_font = QFont("Segoe UI", 12, QFont.Bold)
        title.setFont(title_font)
        main_layout.addWidget(title)

        # ── Tabs ───────────────────────────────────────────────────────────────
        tabs = QTabWidget()
        tabs.addTab(self._build_calculator_tab(), "Calculator")
        tabs.addTab(self._build_feedline_tab(), "Feedline")
        tabs.addTab(self._build_library_tab(), "Library")
        tabs.addTab(self._build_field_record_tab(), "Field Record")
        main_layout.addWidget(tabs)

        # ── Buttons ────────────────────────────────────────────────────────────
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        btn_save = QPushButton("Save Antenna")
        btn_save.clicked.connect(self._on_save_antenna)
        button_layout.addWidget(btn_save)

        btn_pdf = QPushButton("Generate PDF")
        btn_pdf.clicked.connect(self._on_generate_pdf)
        button_layout.addWidget(btn_pdf)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        button_layout.addWidget(btn_close)

        main_layout.addLayout(button_layout)

    def _build_calculator_tab(self) -> QWidget:
        """Build the main calculator tab."""
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # ── Left panel: Inputs ─────────────────────────────────────────────────
        left_layout = QVBoxLayout()

        # Antenna type selection
        group_type = self._create_group("Antenna Type")
        type_layout = QVBoxLayout(group_type)
        self.combo_antenna_type = QComboBox()
        self.combo_antenna_type.addItems([
            "Dipole",
            "EFHW (End-Fed Half Wave)",
            "Ground Plane Vertical",
            "Full-Wave Loop",
            "Delta Loop",
            "Beverage",
            "Magnetic Loop",
        ])
        self.combo_antenna_type.currentIndexChanged.connect(self._on_antenna_type_changed)
        type_layout.addWidget(self.combo_antenna_type)
        left_layout.addWidget(group_type)

        # Frequency selection
        group_freq = self._create_group("Frequency Selection")
        freq_layout = QGridLayout(group_freq)

        freq_layout.addWidget(QLabel("Band:"), 0, 0)
        self.combo_band = QComboBox()
        self.combo_band.addItems(["Custom"] + list(AMATEUR_BANDS.keys()))
        self.combo_band.currentIndexChanged.connect(self._on_band_changed)
        freq_layout.addWidget(self.combo_band, 0, 1)

        freq_layout.addWidget(QLabel("Frequency (MHz):"), 1, 0)
        self.spin_frequency = QDoubleSpinBox()
        self.spin_frequency.setMinimum(0.1)
        self.spin_frequency.setMaximum(10000.0)
        self.spin_frequency.setValue(7.1)
        self.spin_frequency.setDecimals(3)
        self.spin_frequency.setSingleStep(0.1)
        self.spin_frequency.valueChanged.connect(self._on_frequency_changed)
        freq_layout.addWidget(self.spin_frequency, 1, 1)

        left_layout.addWidget(group_freq)

        # Wire/material properties
        group_wire = self._create_group("Wire Properties")
        wire_layout = QGridLayout(group_wire)

        wire_layout.addWidget(QLabel("Wire Type:"), 0, 0)
        self.combo_wire_type = QComboBox()
        self.combo_wire_type.addItems([wt.display_name for wt in WireType])
        self.combo_wire_type.currentIndexChanged.connect(self._on_wire_type_changed)
        wire_layout.addWidget(self.combo_wire_type, 0, 1)

        wire_layout.addWidget(QLabel("Velocity Factor:"), 1, 0)
        self.spin_velocity_factor = QDoubleSpinBox()
        self.spin_velocity_factor.setMinimum(0.60)
        self.spin_velocity_factor.setMaximum(1.00)
        self.spin_velocity_factor.setValue(0.95)
        self.spin_velocity_factor.setDecimals(3)
        self.spin_velocity_factor.setSingleStep(0.01)
        self.spin_velocity_factor.valueChanged.connect(self._on_velocity_factor_changed)
        wire_layout.addWidget(self.spin_velocity_factor, 1, 1)

        left_layout.addWidget(group_wire)
        left_layout.addStretch()

        # ── Right panel: Results + Graphics ────────────────────────────────────
        right_layout = QVBoxLayout()

        # Results display
        self.scroll_results = QScrollArea()
        self.scroll_results.setWidgetResizable(True)
        results_widget = QWidget()
        self.results_layout = QVBoxLayout(results_widget)
        self.scroll_results.setWidget(results_widget)
        right_layout.addWidget(self.scroll_results)

        # Graphics view
        self.graphics_view = QGraphicsView()
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.setMinimumHeight(300)
        right_layout.addWidget(QLabel("Antenna Diagram:"))
        right_layout.addWidget(self.graphics_view)

        # Combine left and right
        layout.addLayout(left_layout, 1)
        layout.addLayout(right_layout, 2)

        return widget

    def _build_feedline_tab(self) -> QWidget:
        """Build the feedline calculator tab."""
        return FeedlineCalculatorTab()

    def _build_library_tab(self) -> QWidget:
        """Build the antenna library tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Library list
        list_layout = QHBoxLayout()
        layout.addWidget(QLabel("Saved Antennas:"))

        self.list_antennas = QListWidget()
        self.list_antennas.itemDoubleClicked.connect(self._on_antenna_loaded)
        list_layout.addWidget(self.list_antennas, 1)

        # Control buttons
        btn_layout = QVBoxLayout()
        btn_load = QPushButton("Load")
        btn_load.clicked.connect(self._on_antenna_loaded)
        btn_layout.addWidget(btn_load)

        btn_delete = QPushButton("Delete")
        btn_delete.clicked.connect(self._on_delete_antenna)
        btn_layout.addWidget(btn_delete)

        btn_duplicate = QPushButton("Duplicate")
        btn_duplicate.clicked.connect(self._on_duplicate_antenna)
        btn_layout.addWidget(btn_duplicate)

        btn_layout.addStretch()
        list_layout.addLayout(btn_layout)

        layout.addLayout(list_layout)
        self._refresh_antenna_list()

        return widget

    def _build_field_record_tab(self) -> QWidget:
        """Build the field record / antenna birth certificate tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Scrollable form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        form_widget = QWidget()
        form_layout = QGridLayout(form_widget)

        row = 0

        # Callsign
        form_layout.addWidget(QLabel("Callsign:"), row, 0)
        self.field_callsign = QComboBox()
        self.field_callsign.setEditable(True)
        form_layout.addWidget(self.field_callsign, row, 1)
        row += 1

        # Antenna Type
        form_layout.addWidget(QLabel("Antenna Type:"), row, 0)
        self.field_antenna_type = QComboBox()
        form_layout.addWidget(self.field_antenna_type, row, 1)
        row += 1

        # Date Built
        form_layout.addWidget(QLabel("Date Built:"), row, 0)
        self.field_date = QComboBox()
        self.field_date.setEditable(True)
        self.field_date.setCurrentText(__import__("datetime").date.today().strftime("%Y-%m-%d"))
        form_layout.addWidget(self.field_date, row, 1)
        row += 1

        # Location/Grid
        form_layout.addWidget(QLabel("Location/Grid:"), row, 0)
        self.field_location = QComboBox()
        self.field_location.setEditable(True)
        form_layout.addWidget(self.field_location, row, 1)
        row += 1

        # Target Frequency
        form_layout.addWidget(QLabel("Target Frequency (MHz):"), row, 0)
        self.field_freq = QDoubleSpinBox()
        self.field_freq.setValue(7.1)
        self.field_freq.setMaximum(10000)
        form_layout.addWidget(self.field_freq, row, 1)
        row += 1

        # Calculated Length
        form_layout.addWidget(QLabel("Calculated Length (m):"), row, 0)
        self.field_calc_length = QDoubleSpinBox()
        self.field_calc_length.setMaximum(1000)
        form_layout.addWidget(self.field_calc_length, row, 1)
        row += 1

        # === AS-BUILT SECTION ===
        form_layout.addWidget(QLabel(""), row, 0)  # Spacer
        row += 1
        as_built_label = QLabel("AS-BUILT (Measured in Field)")
        as_built_label.setStyleSheet("font-weight: bold; background: #f0f0f0; padding: 5px;")
        form_layout.addWidget(as_built_label, row, 0, 1, 2)
        row += 1

        # Final Tuned Length
        form_layout.addWidget(QLabel("Final Tuned Length (m):"), row, 0)
        self.field_final_length = QDoubleSpinBox()
        self.field_final_length.setMaximum(1000)
        form_layout.addWidget(self.field_final_length, row, 1)
        row += 1

        # Resonant Frequency
        form_layout.addWidget(QLabel("Resonant Frequency (MHz):"), row, 0)
        self.field_res_freq = QDoubleSpinBox()
        self.field_res_freq.setMaximum(10000)
        form_layout.addWidget(self.field_res_freq, row, 1)
        row += 1

        # Measured SWR
        form_layout.addWidget(QLabel("Measured SWR:"), row, 0)
        self.field_swr = QDoubleSpinBox()
        self.field_swr.setMinimum(1.0)
        self.field_swr.setMaximum(50.0)
        self.field_swr.setSingleStep(0.1)
        form_layout.addWidget(self.field_swr, row, 1)
        row += 1

        # Impedance
        form_layout.addWidget(QLabel("Feedpoint Impedance (Ω):"), row, 0)
        self.field_impedance = QSpinBox()
        self.field_impedance.setMaximum(1000)
        form_layout.addWidget(self.field_impedance, row, 1)
        row += 1

        # === RADIALS / GROUND PLANE ===
        form_layout.addWidget(QLabel(""), row, 0)
        row += 1
        radial_label = QLabel("Ground Plane / Radials (for verticals)")
        radial_label.setStyleSheet("font-weight: bold; background: #f0f0f0; padding: 5px;")
        form_layout.addWidget(radial_label, row, 0, 1, 2)
        row += 1

        # Number of Radials
        form_layout.addWidget(QLabel("Number of Radials:"), row, 0)
        self.field_num_radials = QSpinBox()
        self.field_num_radials.setValue(4)
        self.field_num_radials.setMaximum(32)
        form_layout.addWidget(self.field_num_radials, row, 1)
        row += 1

        # Radial Length
        form_layout.addWidget(QLabel("Radial Length (m):"), row, 0)
        self.field_radial_length = QDoubleSpinBox()
        self.field_radial_length.setMaximum(1000)
        form_layout.addWidget(self.field_radial_length, row, 1)
        row += 1

        # Counter Poise
        form_layout.addWidget(QLabel("Counter Poise System:"), row, 0)
        self.field_counter_poise = QComboBox()
        self.field_counter_poise.setEditable(True)
        self.field_counter_poise.addItems(["None", "Wire on ground", "Elevated radials", "Copper mesh"])
        form_layout.addWidget(self.field_counter_poise, row, 1)
        row += 1

        # === FIELD NOTES ===
        form_layout.addWidget(QLabel(""), row, 0)
        row += 1
        notes_label = QLabel("Field Notes & Observations")
        notes_label.setStyleSheet("font-weight: bold; background: #f0f0f0; padding: 5px;")
        form_layout.addWidget(notes_label, row, 0, 1, 2)
        row += 1

        # Field Notes Text
        form_layout.addWidget(QLabel("Field Notes:"), row, 0, 1, 2)
        row += 1
        self.field_notes_text = QComboBox()
        self.field_notes_text.setEditable(True)
        form_layout.addWidget(self.field_notes_text, row, 0, 1, 2)
        row += 1

        # Buttons
        button_layout = QHBoxLayout()
        btn_export_html = QPushButton("Export as HTML")
        btn_export_html.clicked.connect(self._on_export_antenna_record)
        button_layout.addWidget(btn_export_html)

        btn_swr_check = QPushButton("SWR Check Guide")
        btn_swr_check.clicked.connect(self._on_show_swr_checklist)
        button_layout.addWidget(btn_swr_check)

        button_layout.addStretch()

        scroll.setWidget(form_widget)
        layout.addWidget(scroll)
        layout.addLayout(button_layout)

        return widget

    def _on_export_antenna_record(self):
        """Export antenna record as HTML birth certificate."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Antenna Record", "", "HTML Files (*.html)"
        )
        if not filename:
            return

        record = AntennaRecord(
            callsign=self.field_callsign.currentText() or "N0CALL",
            antenna_type=self._current_antenna_type.value,
            date_built=self.field_date.currentText(),
            location_grid=self.field_location.currentText(),
            target_frequency_mhz=self.field_freq.value(),
            calculated_length_m=self.field_calc_length.value(),
            final_tuned_length_m=self.field_final_length.value() or None,
            resonant_frequency_mhz=self.field_res_freq.value() or None,
            measured_swr=self.field_swr.value() or None,
            impedance_ohms=self.field_impedance.value() or None,
            num_radials=self.field_num_radials.value(),
            radial_length_m=self.field_radial_length.value() or None,
            counter_poise_system=self.field_counter_poise.currentText(),
            field_notes=self.field_notes_text.currentText(),
        )

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(record.to_html())
            QMessageBox.information(self, "Success", f"Antenna record exported to:\n{filename}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to export:\n{str(e)}")

    def _on_show_swr_checklist(self):
        """Show field expedient SWR check checklist."""
        checklist = FieldExpeditentSWRCheck.field_check_checklist()
        msg = "\n".join(checklist)
        QMessageBox.information(self, "Field Expedient SWR Check", msg)

    def _create_group(self, title: str) -> QGroupBox:
        """Create a styled group box."""
        group = QGroupBox(title)
        font = group.font()
        font.setBold(True)
        group.setFont(font)
        return group

    def _connect_signals(self):
        """Connect all signals to calculation updates."""
        # Already connected in _build_ui
        pass

    def _on_antenna_type_changed(self):
        """Handle antenna type change."""
        index = self.combo_antenna_type.currentIndex()
        antenna_types = [
            AntennaType.DIPOLE, AntennaType.EFHW, AntennaType.GROUND_PLANE,
            AntennaType.FULL_WAVE_LOOP, AntennaType.DELTA_LOOP,
            AntennaType.BEVERAGE, AntennaType.MAGNETIC_LOOP
        ]
        self._current_antenna_type = antenna_types[index]
        self._update_all_calculations()

    def _on_band_changed(self):
        """Handle band selection change."""
        band_name = self.combo_band.currentText()
        if band_name in AMATEUR_BANDS:
            band = AMATEUR_BANDS[band_name]
            self.spin_frequency.blockSignals(True)
            self.spin_frequency.setValue(band.center_mhz)
            self.spin_frequency.blockSignals(False)
            self._current_frequency_mhz = band.center_mhz
            self._update_all_calculations()

    def _on_frequency_changed(self):
        """Handle frequency change."""
        self._current_frequency_mhz = self.spin_frequency.value()
        self._update_all_calculations()

    def _on_wire_type_changed(self):
        """Handle wire type change."""
        index = self.combo_wire_type.currentIndex()
        wire_types = list(WireType)
        self._current_wire_type = wire_types[index]
        self.spin_velocity_factor.blockSignals(True)
        self.spin_velocity_factor.setValue(wire_types[index].velocity_factor)
        self.spin_velocity_factor.blockSignals(False)
        self._on_velocity_factor_changed()

    def _on_velocity_factor_changed(self):
        """Handle velocity factor change."""
        self._current_velocity_factor = self.spin_velocity_factor.value()
        self._update_all_calculations()

    def _update_all_calculations(self):
        """Calculate and display all results."""
        # Clear results
        while self.results_layout.count():
            self.results_layout.takeAt(0).widget().deleteLater()

        # Calculate based on antenna type
        if self._current_antenna_type == AntennaType.DIPOLE:
            result = DipoleCalculator.calculate(
                self._current_frequency_mhz,
                self._current_velocity_factor,
            )
            self._display_dipole_results(result)
            self._draw_dipole_diagram(result)

        elif self._current_antenna_type == AntennaType.EFHW:
            result = EfhwCalculator.calculate(
                self._current_frequency_mhz,
                self._current_velocity_factor,
            )
            self._display_efhw_results(result)
            self._draw_efhw_diagram(result)

        elif self._current_antenna_type == AntennaType.GROUND_PLANE:
            result = GroundPlaneCalculator.calculate(
                self._current_frequency_mhz,
                self._current_velocity_factor,
                num_radials=4,
            )
            self._display_ground_plane_results(result)
            self._draw_ground_plane_diagram(result)

        elif self._current_antenna_type == AntennaType.FULL_WAVE_LOOP:
            result = FullWaveLoopCalculator.calculate(
                self._current_frequency_mhz,
                self._current_velocity_factor,
            )
            self._display_full_wave_loop_results(result)
            self._draw_generic_diagram("Full-Wave Loop")

        elif self._current_antenna_type == AntennaType.DELTA_LOOP:
            result = DeltaLoopCalculator.calculate(
                self._current_frequency_mhz,
                self._current_velocity_factor,
            )
            self._display_delta_loop_results(result)
            self._draw_generic_diagram("Delta Loop")

        elif self._current_antenna_type == AntennaType.BEVERAGE:
            result = BeverageCalculator.calculate(
                self._current_frequency_mhz,
                self._current_velocity_factor,
            )
            self._display_beverage_results(result)
            self._draw_generic_diagram("Beverage Antenna")

        elif self._current_antenna_type == AntennaType.MAGNETIC_LOOP:
            result = MagneticLoopCalculator.calculate(
                self._current_frequency_mhz,
                self._current_velocity_factor,
            )
            self._display_magnetic_loop_results(result)
            self._draw_generic_diagram("Magnetic Loop")

    def _display_dipole_results(self, result: DipoleCalculation):
        """Display dipole calculation results."""
        results_widget = self._create_results_widget([
            ("Total Length", f"{result.total_length_m:.2f} m ({MiscCalculations.meters_to_feet(result.total_length_m):.2f} ft)"),
            ("Per Side", f"{result.half_length_m:.2f} m ({MiscCalculations.meters_to_feet(result.half_length_m):.2f} ft)"),
            ("Height", f"{result.recommended_height_m:.2f} m ({MiscCalculations.meters_to_feet(result.recommended_height_m):.2f} ft)"),
            ("Impedance", f"{result.impedance_ohms} Ω"),
            ("Efficiency", f"{result.efficiency_percent}%"),
        ])
        self.results_layout.addWidget(results_widget)

    def _display_efhw_results(self, result: EfhwCalculation):
        """Display EFHW calculation results."""
        results_widget = self._create_results_widget([
            ("Total Length", f"{result.total_length_m:.2f} m ({MiscCalculations.meters_to_feet(result.total_length_m):.2f} ft)"),
            ("Feedpoint", f"{result.feedpoint_offset_m:.2f} m from end"),
            ("Impedance", f"{result.impedance_ohms} Ω (matched)"),
            ("UNUN", result.unun_recommended.value),
            ("Ferriet", result.ferriet_type),
            ("Efficiency", f"{result.efficiency_percent}%"),
        ])
        self.results_layout.addWidget(results_widget)

    def _display_ground_plane_results(self, result: GroundPlaneCalculation):
        """Display ground plane calculation results."""
        results_widget = self._create_results_widget([
            ("Vertical", f"{result.vertical_length_m:.2f} m ({MiscCalculations.meters_to_feet(result.vertical_length_m):.2f} ft)"),
            ("Radials", f"{result.num_radials} × {result.radial_length_m:.2f} m"),
            ("Impedance", f"{result.impedance_ohms} Ω"),
            ("Take-off Angle", f"{result.take_off_angle:.1f}°"),
            ("Efficiency", f"{result.efficiency_percent}%"),
        ])
        self.results_layout.addWidget(results_widget)

    def _display_full_wave_loop_results(self, result: FullWaveLoopCalculation):
        """Display full-wave loop calculation results."""
        results_widget = self._create_results_widget([
            ("Perimeter", f"{result.perimeter_m:.2f} m ({MiscCalculations.meters_to_feet(result.perimeter_m):.2f} ft)"),
            ("Per Side", f"{result.side_length_m:.2f} m"),
            ("Impedance", f"{result.impedance_ohms} Ω"),
            ("Gain", f"{result.gain_dbi:.1f} dBi"),
            ("Efficiency", f"{result.efficiency_percent}%"),
        ])
        self.results_layout.addWidget(results_widget)

    def _display_delta_loop_results(self, result: DeltaLoopCalculation):
        """Display delta loop calculation results."""
        results_widget = self._create_results_widget([
            ("Perimeter", f"{result.perimeter_m:.2f} m ({MiscCalculations.meters_to_feet(result.perimeter_m):.2f} ft)"),
            ("Height", f"{result.height_m:.2f} m"),
            ("Base Width", f"{result.base_width_m:.2f} m"),
            ("Impedance", f"{result.impedance_ohms} Ω"),
            ("Efficiency", f"{result.efficiency_percent}%"),
        ])
        self.results_layout.addWidget(results_widget)

    def _display_beverage_results(self, result: BeverageCalculation):
        """Display beverage antenna calculation results."""
        results_widget = self._create_results_widget([
            ("Length", f"{result.length_m:.2f} m ({MiscCalculations.meters_to_feet(result.length_m):.2f} ft)"),
            ("Height", f"{result.height_m:.2f} m"),
            ("Impedance", f"{result.impedance_ohms} Ω"),
            ("Termination", f"{result.termination_ohms} Ω"),
            ("Gain", f"{result.gain_dbi:.1f} dBi"),
            ("Directivity", result.directivity),
        ])
        self.results_layout.addWidget(results_widget)

    def _display_magnetic_loop_results(self, result: MagneticLoopCalculation):
        """Display magnetic loop calculation results."""
        results_widget = self._create_results_widget([
            ("Diameter", f"{result.diameter_m:.3f} m ({MiscCalculations.meters_to_feet(result.diameter_m):.2f} ft)"),
            ("Capacitor Range", f"{result.capacitance_min_pf}-{result.capacitance_max_pf} pF"),
            ("Q Factor", f"{result.q_factor:.0f}"),
            ("Impedance", f"{result.impedance_ohms} Ω"),
            ("Efficiency", f"{result.efficiency_percent}%"),
        ])
        self.results_layout.addWidget(results_widget)

    def _create_results_widget(self, items: list[tuple[str, str]]) -> QWidget:
        """Create a formatted results display widget."""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setSpacing(8)

        for row, (label, value) in enumerate(items):
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: bold;")
            layout.addWidget(label_widget, row, 0)

            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #C8A84B; font-size: 11pt;")
            layout.addWidget(value_widget, row, 1)

        layout.addWidget(QLabel(""), len(items), 0)  # Spacer
        return widget

    def _draw_dipole_diagram(self, result: DipoleCalculation):
        """Draw dipole antenna diagram."""
        AntennaGraphicsEngine.draw_dipole(self.graphics_scene, result)

    def _draw_efhw_diagram(self, result: EfhwCalculation):
        """Draw EFHW antenna diagram."""
        AntennaGraphicsEngine.draw_efhw(self.graphics_scene, result)

    def _draw_ground_plane_diagram(self, result: GroundPlaneCalculation):
        """Draw ground plane antenna diagram."""
        AntennaGraphicsEngine.draw_ground_plane(self.graphics_scene, result)

    def _draw_generic_diagram(self, antenna_name: str):
        """Draw generic placeholder diagram for antenna types without specific graphics."""
        self.graphics_scene.clear()
        text = self.graphics_scene.addText(f"{antenna_name}\n\nDetailed diagram coming soon")
        from PySide6.QtGui import QColor
        text.setDefaultTextColor(QColor("#C8A84B"))
        text.setFont(QFont("Segoe UI", 12))

    def _on_save_antenna(self):
        """Save current antenna configuration."""
        name, ok = QInputDialog.getText(self, "Save Antenna", "Antenna name:")
        if not ok or not name:
            return

        antenna = SavedAntenna(
            name=name,
            description=f"{self._current_antenna_type.value} at {self._current_frequency_mhz} MHz",
            antenna_type=self._current_antenna_type,
            frequency_mhz=self._current_frequency_mhz,
            wire_type=self._current_wire_type,
            velocity_factor=self._current_velocity_factor,
        )

        if self._library.save_antenna(antenna):
            QMessageBox.information(self, "Success", f"Antenna '{name}' saved successfully!")
            self._refresh_antenna_list()
        else:
            QMessageBox.warning(self, "Error", "Failed to save antenna.")

    def _on_generate_pdf(self):
        """Generate PDF report."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save PDF Report", "", "PDF Files (*.pdf)"
        )
        if not filename:
            return

        try:
            generator = PdfGenerator(filename)

            if self._current_antenna_type == AntennaType.DIPOLE:
                result = DipoleCalculator.calculate(
                    self._current_frequency_mhz,
                    self._current_velocity_factor,
                )
                success = generator.generate_dipole_report(
                    f"{self._current_antenna_type.value} @ {self._current_frequency_mhz} MHz",
                    self._current_frequency_mhz,
                    result,
                    self._current_wire_type.display_name,
                    self._current_velocity_factor,
                )
            elif self._current_antenna_type == AntennaType.EFHW:
                result = EfhwCalculator.calculate(
                    self._current_frequency_mhz,
                    self._current_velocity_factor,
                )
                success = generator.generate_efhw_report(
                    f"{self._current_antenna_type.value} @ {self._current_frequency_mhz} MHz",
                    self._current_frequency_mhz,
                    result,
                    self._current_wire_type.display_name,
                    self._current_velocity_factor,
                )
            else:
                result = GroundPlaneCalculator.calculate(
                    self._current_frequency_mhz,
                    self._current_velocity_factor,
                )
                success = generator.generate_ground_plane_report(
                    f"{self._current_antenna_type.value} @ {self._current_frequency_mhz} MHz",
                    self._current_frequency_mhz,
                    result,
                    self._current_wire_type.display_name,
                    self._current_velocity_factor,
                )

            if success:
                QMessageBox.information(self, "Success", f"PDF saved to:\n{filename}")
            else:
                QMessageBox.warning(self, "Error", "Failed to generate PDF.")

        except ImportError:
            QMessageBox.warning(
                self, "Missing Dependency",
                "reportlab is required for PDF generation.\nInstall with: pip install reportlab"
            )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to generate PDF:\n{str(e)}")

    def _refresh_antenna_list(self):
        """Refresh antenna list from library."""
        self.list_antennas.clear()
        for name in self._library.list_antennas():
            self.list_antennas.addItem(name)

    def _on_antenna_loaded(self):
        """Load selected antenna from library."""
        item = self.list_antennas.currentItem()
        if not item:
            return

        antenna = self._library.load_antenna(item.text())
        if antenna:
            self.combo_antenna_type.setCurrentIndex([
                AntennaType.DIPOLE, AntennaType.EFHW, AntennaType.GROUND_PLANE
            ].index(antenna.antenna_type))
            self.spin_frequency.setValue(antenna.frequency_mhz)
            self.combo_wire_type.setCurrentIndex(list(WireType).index(antenna.wire_type))
            self.spin_velocity_factor.setValue(antenna.velocity_factor)

    def _on_delete_antenna(self):
        """Delete selected antenna from library."""
        item = self.list_antennas.currentItem()
        if not item:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete '{item.text()}'?"
        )
        if reply == QMessageBox.Yes:
            if self._library.delete_antenna(item.text()):
                self._refresh_antenna_list()

    def _on_duplicate_antenna(self):
        """Duplicate selected antenna."""
        item = self.list_antennas.currentItem()
        if not item:
            return

        new_name, ok = QInputDialog.getText(
            self, "Duplicate Antenna",
            f"New name for '{item.text()}':"
        )
        if ok and new_name:
            if self._library.duplicate_antenna(item.text(), new_name):
                self._refresh_antenna_list()
