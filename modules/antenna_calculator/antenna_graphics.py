"""HAMIOS Antenna Calculator - Graphics Engine

Draw antenna diagrams using QGraphicsScene with dimensions and labels.
"""

from PySide6.QtGui import QPen, QBrush, QColor, QFont
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtWidgets import QGraphicsScene, QGraphicsLineItem, QGraphicsTextItem, QGraphicsEllipseItem

from .antenna_models import (
    DipoleCalculation, EfhwCalculation, GroundPlaneCalculation
)


class AntennaGraphicsEngine:
    """Render antenna diagrams to QGraphicsScene."""

    # Colors
    COLOR_WIRE = QColor("#C8A84B")  # Amber
    COLOR_GROUND = QColor("#666666")  # Gray
    COLOR_DIMENSION = QColor("#FFFFFF")  # White
    COLOR_LABEL = QColor("#FFFFFF")  # White
    COLOR_FEEDPOINT = QColor("#FF6B6B")  # Red

    # Sizes
    WIRE_WIDTH = 2.0
    DIMENSION_WIDTH = 1.0
    GRID_SPACING = 50  # pixels per unit

    @staticmethod
    def draw_dipole(scene: QGraphicsScene, result: DipoleCalculation):
        """Draw horizontal dipole antenna."""
        scene.clear()

        # Canvas dimensions
        width, height = 800, 400
        center_x, center_y = width / 2, height / 2

        # Scale: fit antenna length in view (max 400px for antenna)
        max_antenna_px = 400
        scale_px_per_m = max_antenna_px / result.total_length_m

        half_length_px = result.half_length_m * scale_px_per_m

        # ── Draw antenna wire ──────────────────────────────────────────────────
        pen_wire = QPen(AntennaGraphicsEngine.COLOR_WIRE, AntennaGraphicsEngine.WIRE_WIDTH)

        # Left arm
        left_line = scene.addLine(
            center_x - half_length_px, center_y,
            center_x, center_y,
            pen_wire
        )

        # Right arm
        right_line = scene.addLine(
            center_x, center_y,
            center_x + half_length_px, center_y,
            pen_wire
        )

        # ── Draw feedpoint ────────────────────────────────────────────────────
        feedpoint_brush = QBrush(AntennaGraphicsEngine.COLOR_FEEDPOINT)
        feedpoint = scene.addEllipse(
            center_x - 5, center_y - 5, 10, 10,
            QPen(AntennaGraphicsEngine.COLOR_FEEDPOINT), feedpoint_brush
        )

        # ── Draw ground line ───────────────────────────────────────────────────
        ground_y = center_y + 100
        pen_ground = QPen(AntennaGraphicsEngine.COLOR_GROUND, 2.0)
        scene.addLine(center_x - half_length_px - 20, ground_y,
                     center_x + half_length_px + 20, ground_y, pen_ground)

        # Ground symbols
        for x_offset in [-100, 0, 100]:
            x = center_x + x_offset
            for i in range(3):
                scene.addLine(x - 15 + i*10, ground_y, x - 10 + i*8, ground_y + 10, pen_ground)

        # ── Draw dimensions ────────────────────────────────────────────────────
        pen_dim = QPen(AntennaGraphicsEngine.COLOR_DIMENSION, AntennaGraphicsEngine.DIMENSION_WIDTH)

        # Total length dimension line
        dim_y_top = center_y - 60
        scene.addLine(center_x - half_length_px, dim_y_top,
                     center_x + half_length_px, dim_y_top, pen_dim)
        scene.addLine(center_x - half_length_px, dim_y_top - 5,
                     center_x - half_length_px, dim_y_top + 5, pen_dim)
        scene.addLine(center_x + half_length_px, dim_y_top - 5,
                     center_x + half_length_px, dim_y_top + 5, pen_dim)

        # Total length label
        total_text = scene.addText(f"{result.total_length_m:.2f}m")
        total_text.setDefaultTextColor(AntennaGraphicsEngine.COLOR_DIMENSION)
        total_text.setFont(QFont("Segoe UI", 10, QFont.Bold))
        total_text.setPos(center_x - 40, dim_y_top - 30)

        # Half length dimensions (left and right)
        dim_y = center_y + 30
        scene.addLine(center_x - half_length_px, dim_y,
                     center_x, dim_y, pen_dim)

        left_text = scene.addText(f"½ = {result.half_length_m:.2f}m")
        left_text.setDefaultTextColor(AntennaGraphicsEngine.COLOR_DIMENSION)
        left_text.setFont(QFont("Segoe UI", 9))
        left_text.setPos(center_x - half_length_px - 80, dim_y)

        # Height dimension
        height_px = result.recommended_height_m * scale_px_per_m
        dim_x = center_x + half_length_px + 50
        scene.addLine(dim_x, center_y, dim_x, center_y - height_px, pen_dim)
        scene.addLine(dim_x - 5, center_y, dim_x + 5, center_y, pen_dim)
        scene.addLine(dim_x - 5, center_y - height_px, dim_x + 5, center_y - height_px, pen_dim)

        height_text = scene.addText(f"H≈{result.recommended_height_m:.2f}m")
        height_text.setDefaultTextColor(AntennaGraphicsEngine.COLOR_DIMENSION)
        height_text.setFont(QFont("Segoe UI", 9))
        height_text.setPos(dim_x + 10, center_y - height_px / 2)

        # ── Add specs ──────────────────────────────────────────────────────────
        specs_y = height + 20
        specs = f"Impedance: {result.impedance_ohms}Ω  |  Efficiency: {result.efficiency_percent}%"
        specs_text = scene.addText(specs)
        specs_text.setDefaultTextColor(AntennaGraphicsEngine.COLOR_LABEL)
        specs_text.setFont(QFont("Segoe UI", 9))
        specs_text.setPos(20, specs_y)

        # Set scene rect
        scene.setSceneRect(0, 0, width, height + 50)

    @staticmethod
    def draw_efhw(scene: QGraphicsScene, result: EfhwCalculation):
        """Draw end-fed half-wave antenna."""
        scene.clear()

        width, height = 800, 400
        center_x, center_y = 100, height / 2

        # Scale
        max_antenna_px = 600
        scale_px_per_m = max_antenna_px / result.total_length_m
        total_length_px = result.total_length_m * scale_px_per_m

        # ── Draw antenna wire ──────────────────────────────────────────────────
        pen_wire = QPen(AntennaGraphicsEngine.COLOR_WIRE, AntennaGraphicsEngine.WIRE_WIDTH)
        scene.addLine(center_x, center_y - total_length_px/2,
                     center_x, center_y + total_length_px/2, pen_wire)

        # ── Draw feedpoint (not at the end) ────────────────────────────────────
        feedpoint_y = center_y + total_length_px/2 - (result.feedpoint_offset_m * scale_px_per_m)

        # Feedpoint circle
        feedpoint = scene.addEllipse(
            center_x - 8, feedpoint_y - 8, 16, 16,
            QPen(AntennaGraphicsEngine.COLOR_FEEDPOINT),
            QBrush(AntennaGraphicsEngine.COLOR_FEEDPOINT)
        )

        # ── Draw UNUN transformer ──────────────────────────────────────────────
        unun_x = center_x + 50
        pen_unun = QPen(QColor("#4CAF50"), 2.0)  # Green
        scene.addRect(unun_x - 15, feedpoint_y - 15, 30, 30, pen_unun)

        unun_text = scene.addText("UNUN\n49:1")
        unun_text.setDefaultTextColor(QColor("#4CAF50"))
        unun_text.setFont(QFont("Segoe UI", 8, QFont.Bold))
        unun_text.setPos(unun_x - 20, feedpoint_y - 10)

        # ── Draw coax feedline ─────────────────────────────────────────────────
        pen_coax = QPen(QColor("#666666"), 2.0)
        scene.addLine(unun_x + 15, feedpoint_y,
                     width - 50, feedpoint_y, pen_coax)

        coax_text = scene.addText("50Ω Coax")
        coax_text.setDefaultTextColor(QColor("#999999"))
        coax_text.setFont(QFont("Segoe UI", 8))
        coax_text.setPos(width - 150, feedpoint_y - 15)

        # ── Draw dimensions ────────────────────────────────────────────────────
        pen_dim = QPen(AntennaGraphicsEngine.COLOR_DIMENSION, 1.0)

        # Total length
        dim_x_left = center_x - 60
        scene.addLine(dim_x_left, center_y - total_length_px/2,
                     dim_x_left, center_y + total_length_px/2, pen_dim)
        scene.addLine(dim_x_left - 5, center_y - total_length_px/2,
                     dim_x_left + 5, center_y - total_length_px/2, pen_dim)
        scene.addLine(dim_x_left - 5, center_y + total_length_px/2,
                     dim_x_left + 5, center_y + total_length_px/2, pen_dim)

        total_text = scene.addText(f"{result.total_length_m:.2f}m")
        total_text.setDefaultTextColor(AntennaGraphicsEngine.COLOR_DIMENSION)
        total_text.setFont(QFont("Segoe UI", 10, QFont.Bold))
        total_text.setPos(dim_x_left - 50, center_y - 20)

        # Feedpoint offset
        offset_text = scene.addText(f"Feedpoint\n2% from end")
        offset_text.setDefaultTextColor(AntennaGraphicsEngine.COLOR_FEEDPOINT)
        offset_text.setFont(QFont("Segoe UI", 9))
        offset_text.setPos(center_x + 80, feedpoint_y - 40)

        # ── Add specs ──────────────────────────────────────────────────────────
        specs_y = height - 40
        specs = f"Matched 50Ω  |  Ferriet: {result.ferriet_type}  |  Efficiency: {result.efficiency_percent}%"
        specs_text = scene.addText(specs)
        specs_text.setDefaultTextColor(AntennaGraphicsEngine.COLOR_LABEL)
        specs_text.setFont(QFont("Segoe UI", 9))
        specs_text.setPos(20, specs_y)

        scene.setSceneRect(0, 0, width, height)

    @staticmethod
    def draw_ground_plane(scene: QGraphicsScene, result: GroundPlaneCalculation):
        """Draw ground plane vertical antenna with radials."""
        scene.clear()

        width, height = 800, 400
        center_x, center_y = width / 2, 200

        # Scale
        max_antenna_px = 300
        scale_px_per_m = max_antenna_px / result.vertical_length_m
        vertical_px = result.vertical_length_m * scale_px_per_m
        radial_px = result.radial_length_m * scale_px_per_m

        # ── Draw ground plane (circle) ─────────────────────────────────────────
        pen_ground = QPen(AntennaGraphicsEngine.COLOR_GROUND, 2.0)
        ground_radius = radial_px + 20
        scene.addEllipse(center_x - ground_radius, center_y - 5,
                        ground_radius * 2, 10, pen_ground)

        # ── Draw radials ───────────────────────────────────────────────────────
        pen_radial = QPen(AntennaGraphicsEngine.COLOR_WIRE, 1.5)

        import math
        num_radials = result.num_radials
        for i in range(num_radials):
            angle = (2 * math.pi * i) / num_radials
            x_end = center_x + radial_px * math.cos(angle)
            y_end = center_y + radial_px * math.sin(angle)
            scene.addLine(center_x, center_y, x_end, y_end, pen_radial)

        # ── Draw vertical radiator ─────────────────────────────────────────────
        pen_wire = QPen(AntennaGraphicsEngine.COLOR_WIRE, AntennaGraphicsEngine.WIRE_WIDTH)
        scene.addLine(center_x, center_y, center_x, center_y - vertical_px, pen_wire)

        # ── Draw feedpoint ────────────────────────────────────────────────────
        feedpoint_brush = QBrush(AntennaGraphicsEngine.COLOR_FEEDPOINT)
        feedpoint = scene.addEllipse(
            center_x - 6, center_y - 6, 12, 12,
            QPen(AntennaGraphicsEngine.COLOR_FEEDPOINT), feedpoint_brush
        )

        # ── Draw dimensions ────────────────────────────────────────────────────
        pen_dim = QPen(AntennaGraphicsEngine.COLOR_DIMENSION, 1.0)

        # Vertical length
        dim_x = center_x + ground_radius + 30
        scene.addLine(dim_x, center_y, dim_x, center_y - vertical_px, pen_dim)
        scene.addLine(dim_x - 5, center_y, dim_x + 5, center_y, pen_dim)
        scene.addLine(dim_x - 5, center_y - vertical_px, dim_x + 5, center_y - vertical_px, pen_dim)

        vert_text = scene.addText(f"{result.vertical_length_m:.2f}m")
        vert_text.setDefaultTextColor(AntennaGraphicsEngine.COLOR_DIMENSION)
        vert_text.setFont(QFont("Segoe UI", 10, QFont.Bold))
        vert_text.setPos(dim_x + 10, center_y - vertical_px / 2)

        # Radial length
        radial_text = scene.addText(f"Radials: {result.num_radials}×{result.radial_length_m:.2f}m")
        radial_text.setDefaultTextColor(AntennaGraphicsEngine.COLOR_DIMENSION)
        radial_text.setFont(QFont("Segoe UI", 9))
        radial_text.setPos(center_x - 100, center_y + 80)

        # ── Add specs ──────────────────────────────────────────────────────────
        specs = f"Impedance: {result.impedance_ohms}Ω  |  Take-off: {result.take_off_angle:.0f}°  |  Efficiency: {result.efficiency_percent}%"
        specs_text = scene.addText(specs)
        specs_text.setDefaultTextColor(AntennaGraphicsEngine.COLOR_LABEL)
        specs_text.setFont(QFont("Segoe UI", 9))
        specs_text.setPos(20, height - 40)

        scene.setSceneRect(0, 0, width, height)
