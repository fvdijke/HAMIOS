"""HAMIOS Antenna Calculator - PDF Report Generator

Generate PDF reports with antenna specs and diagrams.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch, mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from .antenna_models import (
    SavedAntenna, DipoleCalculation, EfhwCalculation, GroundPlaneCalculation,
    AntennaType
)
from .antenna_math import MiscCalculations


class PdfGenerator:
    """Generate PDF reports for antenna configurations."""

    # Colors
    COLOR_ACCENT = colors.HexColor("#C8A84B")  # Amber
    COLOR_DARK = colors.HexColor("#1A1A1A")
    COLOR_LIGHT = colors.HexColor("#F5F5F5")

    def __init__(self, filename: Optional[str] = None):
        """
        Initialize PDF generator.

        Args:
            filename: Output PDF filename. If None, uses antenna_report_{timestamp}.pdf
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required for PDF generation. Install with: pip install reportlab")

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"antenna_report_{timestamp}.pdf"

        self.filename = filename

    def generate_dipole_report(
        self,
        antenna_name: str,
        frequency_mhz: float,
        result: DipoleCalculation,
        wire_type: str = "Bare Copper",
        velocity_factor: float = 0.95,
    ) -> bool:
        """
        Generate PDF report for dipole antenna.

        Args:
            antenna_name: Name of antenna configuration
            frequency_mhz: Operating frequency in MHz
            result: DipoleCalculation object
            wire_type: Wire type used
            velocity_factor: Velocity factor

        Returns:
            True if successful
        """
        try:
            doc = SimpleDocTemplate(
                self.filename,
                pagesize=letter,
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch,
            )

            story = []
            styles = getSampleStyleSheet()

            # ── Title ──────────────────────────────────────────────────────────
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=self.COLOR_ACCENT,
                spaceAfter=12,
                alignment=TA_CENTER,
            )
            story.append(Paragraph(f"Dipole Antenna Calculator Report", title_style))
            story.append(Spacer(1, 0.2*inch))

            # ── Antenna Info ───────────────────────────────────────────────────
            info_data = [
                ["Antenna Name:", antenna_name],
                ["Type:", "Half-Wave Dipole"],
                ["Center Frequency:", f"{frequency_mhz} MHz"],
                ["Wire Type:", wire_type],
                ["Velocity Factor:", f"{velocity_factor:.3f}"],
                ["Report Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ]

            info_table = Table(info_data, colWidths=[2*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), self.COLOR_LIGHT),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.COLOR_DARK),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 0.3*inch))

            # ── Dimensions ─────────────────────────────────────────────────────
            story.append(Paragraph("Antenna Dimensions", styles['Heading2']))

            dims_data = [
                ["Parameter", "Meters", "Feet"],
                ["Total Length", f"{result.total_length_m:.3f}", f"{MiscCalculations.meters_to_feet(result.total_length_m):.2f}"],
                ["Per Side", f"{result.half_length_m:.3f}", f"{MiscCalculations.meters_to_feet(result.half_length_m):.2f}"],
                ["Recommended Height", f"{result.recommended_height_m:.3f}", f"{MiscCalculations.meters_to_feet(result.recommended_height_m):.2f}"],
            ]

            dims_table = Table(dims_data, colWidths=[2.5*inch, 2*inch, 2*inch])
            dims_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_ACCENT),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            story.append(dims_table)
            story.append(Spacer(1, 0.3*inch))

            # ── Performance ────────────────────────────────────────────────────
            story.append(Paragraph("Performance Characteristics", styles['Heading2']))

            perf_data = [
                ["Characteristic", "Value"],
                ["Feedpoint Impedance", f"{result.impedance_ohms} Ω"],
                ["Radiation Resistance", f"{result.radiation_resistance:.1f} Ω"],
                ["Efficiency", f"{result.efficiency_percent:.1f}%"],
            ]

            perf_table = Table(perf_data, colWidths=[3*inch, 3*inch])
            perf_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_ACCENT),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            story.append(perf_table)
            story.append(Spacer(1, 0.3*inch))

            # ── Notes ──────────────────────────────────────────────────────────
            story.append(Paragraph("Design Notes", styles['Heading2']))
            notes = (
                "This dipole is designed for operation at the specified center frequency. "
                "The recommended height of λ/4 is the minimum suggested height above ground for optimal performance. "
                "For best results, position the antenna away from nearby conductors and in clear sky areas."
            )
            story.append(Paragraph(notes, styles['BodyText']))

            # ── Footer ─────────────────────────────────────────────────────────
            story.append(Spacer(1, 0.5*inch))
            footer = "HAMIOS Antenna Calculator © 2026"
            story.append(Paragraph(footer, ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER,
            )))

            # Build PDF
            doc.build(story)
            return True

        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False

    def generate_efhw_report(
        self,
        antenna_name: str,
        frequency_mhz: float,
        result: EfhwCalculation,
        wire_type: str = "Bare Copper",
        velocity_factor: float = 0.95,
    ) -> bool:
        """Generate PDF report for EFHW antenna."""
        # Similar structure to dipole report
        # Abbreviated for space
        try:
            doc = SimpleDocTemplate(self.filename, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()

            story.append(Paragraph("EFHW Antenna Report", styles['Heading1']))
            story.append(Spacer(1, 0.2*inch))

            info = f"""
            <b>Antenna:</b> {antenna_name}<br/>
            <b>Type:</b> End-Fed Half Wave<br/>
            <b>Frequency:</b> {frequency_mhz} MHz<br/>
            <b>Total Length:</b> {result.total_length_m:.3f} m ({MiscCalculations.meters_to_feet(result.total_length_m):.2f} ft)<br/>
            <b>Feedpoint Offset:</b> {result.feedpoint_offset_m:.3f} m from end<br/>
            <b>Impedance:</b> {result.impedance_ohms} Ω (matched)<br/>
            <b>UNUN Recommended:</b> {result.unun_recommended.value}<br/>
            <b>Ferriet:</b> {result.ferriet_type}<br/>
            <b>Efficiency:</b> {result.efficiency_percent:.1f}%<br/>
            <b>Generated:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            """

            story.append(Paragraph(info, styles['BodyText']))
            doc.build(story)
            return True

        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False

    def generate_ground_plane_report(
        self,
        antenna_name: str,
        frequency_mhz: float,
        result: GroundPlaneCalculation,
        wire_type: str = "Bare Copper",
        velocity_factor: float = 0.95,
    ) -> bool:
        """Generate PDF report for Ground Plane antenna."""
        # Similar structure to dipole report
        try:
            doc = SimpleDocTemplate(self.filename, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()

            story.append(Paragraph("Ground Plane Antenna Report", styles['Heading1']))
            story.append(Spacer(1, 0.2*inch))

            info = f"""
            <b>Antenna:</b> {antenna_name}<br/>
            <b>Type:</b> Ground Plane Vertical<br/>
            <b>Frequency:</b> {frequency_mhz} MHz<br/>
            <b>Vertical Length:</b> {result.vertical_length_m:.3f} m ({MiscCalculations.meters_to_feet(result.vertical_length_m):.2f} ft)<br/>
            <b>Radials:</b> {result.num_radials} × {result.radial_length_m:.3f} m each<br/>
            <b>Impedance:</b> {result.impedance_ohms} Ω<br/>
            <b>Take-off Angle:</b> {result.take_off_angle:.1f}°<br/>
            <b>Efficiency:</b> {result.efficiency_percent:.1f}%<br/>
            <b>Generated:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            """

            story.append(Paragraph(info, styles['BodyText']))
            doc.build(story)
            return True

        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False
