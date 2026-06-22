"""HAMIOS Antenna Calculator - SVG Graphics Engine

Generate scalable antenna diagrams with real-time dimension labels, radials, and counter poise specs.
"""

import math


class AntennaSVGGraphics:
    """Generate professional SVG antenna diagrams with dimensions."""

    # Colors
    WIRE_COLOR = "#C8A84B"
    TEXT_COLOR = "#C8D0DC"
    ACCENT_COLOR = "#4A9FD8"
    BG_COLOR = "#1A1D22"
    GRID_COLOR = "#3A4050"

    @staticmethod
    def svg_header(width=800, height=600) -> str:
        """SVG document header."""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
<defs>
    <style>
        .wire {{ stroke: {AntennaSVGGraphics.WIRE_COLOR}; stroke-width: 3; fill: none; stroke-linecap: round; }}
        .radial {{ stroke: {AntennaSVGGraphics.ACCENT_COLOR}; stroke-width: 2; fill: none; stroke-dasharray: 5,5; }}
        .dimension {{ stroke: {AntennaSVGGraphics.TEXT_COLOR}; stroke-width: 1; fill: none; }}
        .text {{ font-family: Consolas, monospace; font-size: 12px; fill: {AntennaSVGGraphics.TEXT_COLOR}; }}
        .label {{ font-family: Consolas, monospace; font-size: 11px; fill: {AntennaSVGGraphics.ACCENT_COLOR}; font-weight: bold; }}
        .dimension-text {{ font-family: Consolas, monospace; font-size: 10px; fill: {AntennaSVGGraphics.TEXT_COLOR}; text-anchor: middle; }}
        .ground {{ stroke: {AntennaSVGGraphics.GRID_COLOR}; stroke-width: 1; fill: none; stroke-dasharray: 3,3; }}
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
        <polygon points="0 0, 10 3, 0 6" fill="{AntennaSVGGraphics.TEXT_COLOR}" />
    </marker>
</defs>
<rect width="{width}" height="{height}" fill="{AntennaSVGGraphics.BG_COLOR}"/>
'''

    @staticmethod
    def svg_footer() -> str:
        """SVG document footer."""
        return '</svg>'

    @staticmethod
    def dipole_diagram(total_m: float, half_m: float, freq_mhz: float, vf: float, wave_frac: float) -> str:
        """Half-wave dipole with real dimensions."""
        width, height = 800, 400
        cx, cy = 400, 200

        svg = AntennaSVGGraphics.svg_header(width, height)

        # Ground line
        svg += f'<line x1="50" y1="{cy+80}" x2="750" y2="{cy+80}" class="ground"/>\n'
        svg += f'<text x="400" y="{cy+100}" class="dimension-text">Ground Level</text>\n'

        # Feedpoint center line
        svg += f'<line x1="{cx}" y1="50" x2="{cx}" y2="{cy+80}" class="dimension" stroke-dasharray="2,2"/>\n'

        # Dipole elements
        left_x = cx - 150
        right_x = cx + 150
        svg += f'<line x1="{left_x}" y1="{cy-50}" x2="{cx}" y2="{cy-50}" class="wire" stroke-width="4"/>\n'
        svg += f'<line x1="{cx}" y1="{cy-50}" x2="{right_x}" y2="{cy-50}" class="wire" stroke-width="4"/>\n'

        # Feedpoint
        svg += f'<circle cx="{cx}" cy="{cy-50}" r="5" fill="{AntennaSVGGraphics.WIRE_COLOR}"/>\n'
        svg += f'<text x="{cx+20}" y="{cy-55}" class="label">◉ Feed (50Ω)</text>\n'

        # Balun
        svg += f'<circle cx="{cx}" cy="{cy}" r="12" fill="none" stroke="{AntennaSVGGraphics.ACCENT_COLOR}" stroke-width="2"/>\n'
        svg += f'<text x="{cx-15}" y="{cy+5}" class="label">1:1</text>\n'

        # Coax
        svg += f'<line x1="{cx}" y1="{cy+12}" x2="{cx}" y2="{cy+60}" class="wire" stroke-dasharray="4,4" stroke-width="2"/>\n'

        # Dimension lines and labels
        # Left leg
        svg += f'<line x1="{left_x-20}" y1="{cy-50}" x2="{left_x-20}" y2="{cy-70}" class="dimension"/>\n'
        svg += f'<line x1="{left_x-25}" y1="{cy-70}" x2="{left_x-15}" y2="{cy-70}" class="dimension"/>\n'
        svg += f'<text x="{left_x-50}" y="{cy-40}" class="dimension-text">{half_m:.2f}m</text>\n'

        # Right leg
        svg += f'<line x1="{right_x+20}" y1="{cy-50}" x2="{right_x+20}" y2="{cy-70}" class="dimension"/>\n'
        svg += f'<line x1="{right_x+15}" y1="{cy-70}" x2="{right_x+25}" y2="{cy-70}" class="dimension"/>\n'
        svg += f'<text x="{right_x+40}" y="{cy-40}" class="dimension-text">{half_m:.2f}m</text>\n'

        # Title and specs
        svg += f'<text x="50" y="30" style="font-size: 16px; font-weight: bold; fill: {AntennaSVGGraphics.WIRE_COLOR};">DIPOLE (½λ)</text>\n'
        svg += f'<text x="50" y="55" class="text">Frequency: {freq_mhz} MHz | VF: {vf} | Wave: {wave_frac}</text>\n'
        svg += f'<text x="50" y="75" class="text">Total Length: {total_m:.2f}m | Each Leg: {half_m:.2f}m</text>\n'

        svg += AntennaSVGGraphics.svg_footer()
        return svg

    @staticmethod
    def vertical_diagram(elem_m: float, radial_m: float, num_radials: int, freq_mhz: float, vf: float, wave_frac: float) -> str:
        """Quarter-wave vertical with radials and dimensions."""
        width, height = 800, 500
        cx, cy = 400, 300

        svg = AntennaSVGGraphics.svg_header(width, height)

        # Ground
        svg += f'<line x1="50" y1="{cy+100}" x2="750" y2="{cy+100}" class="ground"/>\n'
        svg += f'<text x="400" y="{cy+120}" class="dimension-text">Ground Level</text>\n'

        # Vertical element
        elem_top = cy + 100 - (elem_m * 20)  # Scale for display
        svg += f'<line x1="{cx}" y1="{elem_top}" x2="{cx}" y2="{cy+100}" class="wire" stroke-width="4"/>\n'

        # Element dimension
        svg += f'<line x1="{cx-60}" y1="{elem_top}" x2="{cx-60}" y2="{cy+100}" class="dimension"/>\n'
        svg += f'<line x1="{cx-65}" y1="{elem_top}" x2="{cx-55}" y2="{elem_top}" class="dimension"/>\n'
        svg += f'<line x1="{cx-65}" y1="{cy+100}" x2="{cx-55}" y2="{cy+100}" class="dimension"/>\n'
        svg += f'<text x="{cx-90}" y="{(elem_top+cy+100)/2}" class="dimension-text">{elem_m:.2f}m</text>\n'

        # Radials (4-way)
        angles = [0, 90, 180, 270]
        radial_pixels = 100
        for i, angle in enumerate(angles):
            rad = math.radians(angle)
            x2 = cx + radial_pixels * math.cos(rad)
            y2 = cy + 100 + radial_pixels * math.sin(rad)
            svg += f'<line x1="{cx}" y1="{cy+100}" x2="{x2}" y2="{y2}" class="radial" stroke-width="2"/>\n'

            # Radial labels
            label_x = cx + (radial_pixels + 30) * math.cos(rad)
            label_y = cy + 100 + (radial_pixels + 30) * math.sin(rad)
            svg += f'<text x="{label_x}" y="{label_y}" class="dimension-text">{radial_m:.2f}m</text>\n'

        # Feedpoint
        svg += f'<circle cx="{cx}" cy="{cy+100}" r="6" fill="{AntennaSVGGraphics.WIRE_COLOR}"/>\n'
        svg += f'<text x="{cx+15}" y="{cy+105}" class="label">◉ Direct 50Ω</text>\n'

        # Title and specs
        svg += f'<text x="50" y="30" style="font-size: 16px; font-weight: bold; fill: {AntennaSVGGraphics.WIRE_COLOR};">VERTICAL (¼λ)</text>\n'
        svg += f'<text x="50" y="55" class="text">Frequency: {freq_mhz} MHz | VF: {vf} | Wave: {wave_frac}</text>\n'
        svg += f'<text x="50" y="75" class="text">Element: {elem_m:.2f}m | Radials: {num_radials} × {radial_m:.2f}m</text>\n'

        svg += AntennaSVGGraphics.svg_footer()
        return svg

    @staticmethod
    def efhw_diagram(total_m: float, cp_m: float, freq_mhz: float, vf: float, wave_frac: float) -> str:
        """End-Fed Half-Wave with UnUn and counterpoise."""
        width, height = 800, 500
        cx, cy = 200, 150

        svg = AntennaSVGGraphics.svg_header(width, height)

        # Wire element (vertical then sloped)
        svg += f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy-200}" class="wire" stroke-width="4"/>\n'
        svg += f'<line x1="{cx}" y1="{cy-200}" x2="600" y2="100" class="wire" stroke-width="4"/>\n'

        # End feedpoint
        svg += f'<circle cx="600" cy="100" r="6" fill="{AntennaSVGGraphics.WIRE_COLOR}"/>\n'
        svg += f'<text x="610" y="105" class="label">◉ End Feed</text>\n'

        # 49:1 UnUn (toroid representation)
        svg += f'<circle cx="590" cy="140" r="15" fill="none" stroke="{AntennaSVGGraphics.ACCENT_COLOR}" stroke-width="2"/>\n'
        svg += f'<text x="575" y="145" class="label">49:1</text>\n'

        # Coax from UnUn
        svg += f'<line x1="590" y1="155" x2="590" y2="300" class="wire" stroke-dasharray="4,4" stroke-width="2"/>\n'

        # Ground
        svg += f'<line x1="50" y1="300" x2="750" y2="300" class="ground"/>\n'

        # Counterpoise (horizontal radial)
        svg += f'<line x1="590" y1="300" x2="{590-cp_m*50}" y2="300" class="radial" stroke-width="2"/>\n'
        svg += f'<circle cx="590" cy="300" r="4" fill="{AntennaSVGGraphics.WIRE_COLOR}"/>\n'

        # Counterpoise dimension
        svg += f'<line x1="590" y1="315" x2="{590-cp_m*50}" y2="315" class="dimension"/>\n'
        svg += f'<text x="{590-cp_m*25}" y="335" class="dimension-text">CP: {cp_m:.2f}m</text>\n'

        # Element dimension
        svg += f'<line x1="{cx-40}" y1="{cy}" x2="{cx-40}" y2="{cy-200}" class="dimension"/>\n'
        svg += f'<text x="{cx-70}" y="{cy-100}" class="dimension-text">{total_m:.2f}m</text>\n'

        # Title and specs
        svg += f'<text x="50" y="30" style="font-size: 16px; font-weight: bold; fill: {AntennaSVGGraphics.WIRE_COLOR};">EFHW (END-FED)</text>\n'
        svg += f'<text x="50" y="55" class="text">Frequency: {freq_mhz} MHz | VF: {vf} | Wave: {wave_frac}</text>\n'
        svg += f'<text x="50" y="75" class="text">Wire: {total_m:.2f}m | Counterpoise: {cp_m:.2f}m (5% of wire)</text>\n'

        svg += AntennaSVGGraphics.svg_footer()
        return svg

    @staticmethod
    def loop_diagram(perimeter_m: float, side_m: float, freq_mhz: float, vf: float, wave_frac: float) -> str:
        """Full-wave loop with dimensions."""
        width, height = 700, 600
        cx, cy = 350, 250
        loop_size = 120

        svg = AntennaSVGGraphics.svg_header(width, height)

        # Ground
        svg += f'<line x1="50" y1="{cy+200}" x2="650" y2="{cy+200}" class="ground"/>\n'

        # Loop square
        corners = [
            (cx - loop_size, cy - loop_size),
            (cx + loop_size, cy - loop_size),
            (cx + loop_size, cy + loop_size),
            (cx - loop_size, cy + loop_size),
        ]

        for i in range(4):
            x1, y1 = corners[i]
            x2, y2 = corners[(i + 1) % 4]
            svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="wire" stroke-width="3"/>\n'

        # Feedpoint at corner
        feed_x, feed_y = corners[0]
        svg += f'<circle cx="{feed_x}" cy="{feed_y}" r="6" fill="{AntennaSVGGraphics.WIRE_COLOR}"/>\n'

        # 4:1 Balun
        svg += f'<circle cx="{feed_x-25}" cy="{feed_y+25}" r="12" fill="none" stroke="{AntennaSVGGraphics.ACCENT_COLOR}" stroke-width="2"/>\n'
        svg += f'<text x="{feed_x-32}" y="{feed_y+30}" class="label">4:1</text>\n'

        # Coax
        svg += f'<line x1="{feed_x-25}" y1="{feed_y+37}" x2="{feed_x-25}" y2="{cy+200}" class="wire" stroke-dasharray="4,4" stroke-width="2"/>\n'

        # Side dimensions
        svg += f'<text x="{cx}" y="{cy-loop_size-30}" class="dimension-text">{side_m:.2f}m</text>\n'
        svg += f'<text x="{cx+loop_size+40}" y="{cy}" class="dimension-text">{side_m:.2f}m</text>\n'

        # Title and specs
        svg += f'<text x="50" y="30" style="font-size: 16px; font-weight: bold; fill: {AntennaSVGGraphics.WIRE_COLOR};">FULL-WAVE LOOP</text>\n'
        svg += f'<text x="50" y="55" class="text">Frequency: {freq_mhz} MHz | VF: {vf} | Wave: {wave_frac}</text>\n'
        svg += f'<text x="50" y="75" class="text">Perimeter: {perimeter_m:.2f}m | Side: {side_m:.2f}m</text>\n'

        svg += AntennaSVGGraphics.svg_footer()
        return svg
