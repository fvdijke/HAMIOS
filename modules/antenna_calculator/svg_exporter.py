"""HAMIOS Antenna Calculator - SVG Diagram Exporter

Export antenna diagrams to scalable SVG format.
"""

from typing import List, Tuple
import math


class SVGExporter:
    """Export antenna diagrams to SVG format."""

    def __init__(self, width: int = 800, height: int = 400):
        """Initialize SVG document."""
        self.width = width
        self.height = height
        self.elements: List[str] = []

    def _add_element(self, element: str):
        """Add SVG element to document."""
        self.elements.append(element)

    def add_line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        stroke: str = "#C8A84B",
        stroke_width: float = 2.0,
    ):
        """Add line to SVG."""
        self._add_element(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{stroke}" stroke-width="{stroke_width}" />'
        )

    def add_circle(
        self,
        cx: float,
        cy: float,
        r: float,
        fill: str = "#C8A84B",
        stroke: str = "#C8A84B",
        stroke_width: float = 1.0,
    ):
        """Add circle to SVG."""
        self._add_element(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{stroke_width}" />'
        )

    def add_rect(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        fill: str = "none",
        stroke: str = "#C8A84B",
        stroke_width: float = 2.0,
    ):
        """Add rectangle to SVG."""
        self._add_element(
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" />'
        )

    def add_text(
        self,
        x: float,
        y: float,
        text: str,
        font_size: int = 12,
        fill: str = "#FFFFFF",
        font_family: str = "Segoe UI",
        text_anchor: str = "start",
    ):
        """Add text to SVG."""
        escaped_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self._add_element(
            f'<text x="{x}" y="{y}" font-size="{font_size}" fill="{fill}" '
            f'font-family="{font_family}" text-anchor="{text_anchor}">{escaped_text}</text>'
        )

    def add_polygon(
        self,
        points: List[Tuple[float, float]],
        fill: str = "none",
        stroke: str = "#C8A84B",
        stroke_width: float = 2.0,
    ):
        """Add polygon to SVG."""
        points_str = " ".join(f"{x},{y}" for x, y in points)
        self._add_element(
            f'<polygon points="{points_str}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{stroke_width}" />'
        )

    def add_dimension_line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        label: str,
        offset: float = 30,
    ):
        """Add dimension line with label."""
        # Main line
        self.add_line(x1, y1, x2, y2, stroke="#FFFFFF", stroke_width=1.0)

        # Tick marks
        tick_size = 5
        self.add_line(x1 - tick_size, y1 - tick_size, x1 + tick_size, y1 + tick_size)
        self.add_line(x2 - tick_size, y2 - tick_size, x2 + tick_size, y2 + tick_size)

        # Label
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        self.add_text(mid_x, mid_y - 10, label, font_size=10, fill="#FFFFFF")

    def to_string(self) -> str:
        """Convert to SVG document string."""
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}">
<defs>
  <style>
    text {{ font-family: Segoe UI, Arial, sans-serif; }}
  </style>
</defs>
<rect width="{self.width}" height="{self.height}" fill="#1A1A1A"/>
'''
        svg += "\n".join(self.elements)
        svg += "\n</svg>"
        return svg

    def save(self, filename: str) -> bool:
        """Save SVG to file."""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.to_string())
            return True
        except Exception as e:
            print(f"Error saving SVG: {e}")
            return False


class AntennaSVGDiagrams:
    """Generate antenna diagrams as SVG."""

    @staticmethod
    def dipole_svg(
        total_length_m: float,
        half_length_m: float,
        recommended_height_m: float,
    ) -> str:
        """Generate dipole antenna SVG diagram."""
        svg = SVGExporter(800, 400)

        center_x, center_y = 400, 200
        max_antenna_px = 400
        scale_px_per_m = max_antenna_px / total_length_m
        half_length_px = half_length_m * scale_px_per_m

        # Antenna wire
        svg.add_line(
            center_x - half_length_px,
            center_y,
            center_x + half_length_px,
            center_y,
            stroke="#C8A84B",
            stroke_width=3,
        )

        # Feedpoint
        svg.add_circle(center_x, center_y, 6, fill="#FF6B6B", stroke="#FF6B6B")

        # Ground
        ground_y = center_y + 80
        svg.add_line(center_x - half_length_px - 20, ground_y,
                    center_x + half_length_px + 20, ground_y, stroke="#666666")

        # Dimension: total length
        svg.add_dimension_line(
            center_x - half_length_px,
            center_y - 50,
            center_x + half_length_px,
            center_y - 50,
            f"{total_length_m:.2f}m",
        )

        # Dimension: height
        dim_x = center_x + half_length_px + 50
        height_px = recommended_height_m * scale_px_per_m
        svg.add_line(dim_x, center_y, dim_x, center_y - height_px, stroke="#FFFFFF")
        svg.add_text(dim_x + 10, center_y - height_px / 2, f"H={recommended_height_m:.2f}m", font_size=10)

        return svg.to_string()

    @staticmethod
    def full_wave_loop_svg(perimeter_m: float, side_length_m: float) -> str:
        """Generate full-wave loop antenna SVG diagram."""
        svg = SVGExporter(600, 500)

        center_x, center_y = 300, 250
        max_size_px = 200
        scale_px_per_m = max_size_px / side_length_m

        side_px = side_length_m * scale_px_per_m

        # Square loop
        points = [
            (center_x - side_px / 2, center_y - side_px / 2),
            (center_x + side_px / 2, center_y - side_px / 2),
            (center_x + side_px / 2, center_y + side_px / 2),
            (center_x - side_px / 2, center_y + side_px / 2),
        ]
        svg.add_polygon(points, fill="none", stroke="#C8A84B", stroke_width=2.5)

        # Feedpoint
        svg.add_circle(center_x - side_px / 2, center_y, 6, fill="#FF6B6B")

        # Feedline
        svg.add_line(
            center_x - side_px / 2,
            center_y,
            center_x - side_px / 2 - 50,
            center_y,
            stroke="#666666",
            stroke_width=2,
        )
        svg.add_text(
            center_x - side_px / 2 - 80,
            center_y + 15,
            "50Ω",
            font_size=10,
            fill="#FFFFFF",
        )

        # Dimensions
        svg.add_text(center_x, center_y + side_px / 2 + 30,
                    f"Side: {side_length_m:.2f}m", font_size=11, fill="#C8A84B", text_anchor="middle")
        svg.add_text(center_x, 30,
                    f"Full-Wave Loop - Perimeter: {perimeter_m:.2f}m", font_size=14,
                    fill="#C8A84B", text_anchor="middle")

        return svg.to_string()

    @staticmethod
    def delta_loop_svg(perimeter_m: float, height_m: float, base_width_m: float) -> str:
        """Generate delta loop antenna SVG diagram."""
        svg = SVGExporter(600, 500)

        center_x, center_y = 300, 300
        max_height_px = 200
        scale_px_per_m = max_height_px / height_m

        height_px = height_m * scale_px_per_m
        base_px = base_width_m * scale_px_per_m

        # Triangle (delta)
        points = [
            (center_x, center_y - height_px),  # Top
            (center_x - base_px / 2, center_y),  # Bottom left
            (center_x + base_px / 2, center_y),  # Bottom right
        ]
        svg.add_polygon(points, fill="none", stroke="#C8A84B", stroke_width=2.5)

        # Feedpoint (bottom center)
        svg.add_circle(center_x, center_y, 6, fill="#FF6B6B")

        # Title and specs
        svg.add_text(center_x, 30, "Delta (Triangular) Loop", font_size=14,
                    fill="#C8A84B", text_anchor="middle")
        svg.add_text(center_x, center_y + 50,
                    f"Height: {height_m:.2f}m | Base: {base_width_m:.2f}m", font_size=11,
                    fill="#FFFFFF", text_anchor="middle")

        return svg.to_string()
