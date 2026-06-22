"""HAMIOS Antenna Calculator - Complete SVG Antenna Diagrams

Full schematics with measurements, radials, baluns, and deployment info.
"""

import math


class AntennaDiagrams:
    """Generate SVG diagrams for all 12 antenna types."""

    # Color scheme
    WIRE = "#C8A84B"
    COPPER = "#D4A574"
    RADIAL = "#8B6914"
    TEXT = "#C8D0DC"
    BG = "#2A2D32"
    BALUN = "#4A7BA7"

    @staticmethod
    def svg_header(width=600, height=500) -> str:
        """SVG header."""
        return f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
<defs>
    <style>
        text {{ font-family: Consolas, monospace; font-size: 11px; fill: {AntennaDiagrams.TEXT}; }}
        .label {{ font-size: 10px; fill: {AntennaDiagrams.TEXT}; }}
        .dim {{ font-size: 9px; fill: #999; }}
        .wire {{ stroke: {AntennaDiagrams.WIRE}; stroke-width: 2.5; fill: none; stroke-linecap: round; }}
        .radial {{ stroke: {AntennaDiagrams.RADIAL}; stroke-width: 1.8; fill: none; stroke-linecap: round; }}
        .balun {{ stroke: {AntennaDiagrams.BALUN}; stroke-width: 2; fill: none; }}
        .ground {{ stroke: {AntennaDiagrams.TEXT}; stroke-width: 1; fill: none; }}
        .dimension {{ stroke: {AntennaDiagrams.TEXT}; stroke-width: 0.8; fill: none; marker-end: url(#arrowhead); }}
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
        <polygon points="0 0, 10 3, 0 6" fill="{AntennaDiagrams.TEXT}" />
    </marker>
</defs>
<rect width="{width}" height="{height}" fill="{AntennaDiagrams.BG}"/>
'''

    @staticmethod
    def dipole_diagram(total_m: float, half_m: float) -> str:
        """Horizontal dipole with center feedpoint and ground."""
        svg = AntennaDiagrams.svg_header()

        # Ground
        svg += f'<line x1="50" y1="450" x2="550" y2="450" class="ground" stroke-dasharray="5,5"/>\n'
        svg += f'<text x="280" y="470" class="dim">Ground Level</text>\n'

        # Mast
        svg += f'<line x1="300" y1="450" x2="300" y2="250" class="wire"/>\n'

        # Dipole elements
        left_x = 300 - 150
        right_x = 300 + 150
        svg += f'<line x1="{left_x}" y1="200" x2="{right_x}" y2="200" class="wire"/>\n'

        # Feedpoint
        svg += f'<circle cx="300" cy="200" r="4" fill="{AntennaDiagrams.WIRE}"/>\n'

        # Balun
        svg += f'<circle cx="300" cy="230" r="8" class="balun"/>\n'
        svg += f'<text x="310" y="235" class="label">1:1</text>\n'

        # Coax
        svg += f'<line x1="300" y1="238" x2="300" y2="450" class="wire" stroke-dasharray="3,3"/>\n'

        # Dimensions
        svg += f'<line x1="{left_x}" y1="180" x2="{left_x}" y2="160" class="dimension"/>\n'
        svg += f'<line x1="{left_x}" y1="170" x2="300" y2="170" class="dimension"/>\n'
        svg += f'<text x="{left_x-30}" y="165" class="label">{half_m:.2f}m</text>\n'
        svg += f'<text x="320" y="165" class="label">{half_m:.2f}m</text>\n'

        # Labels
        svg += f'<text x="50" y="30" style="font-size: 14px; font-weight: bold; fill: {AntennaDiagrams.WIRE}">Dipole (½λ)</text>\n'
        svg += f'<text x="50" y="50" class="label">Total: {total_m:.2f}m</text>\n'
        svg += f'<text x="50" y="65" class="label">Feed: Center (1:1 Balun)</text>\n'

        svg += '</svg>'
        return svg

    @staticmethod
    def vertical_diagram(elem_m: float, radial_m: float, num_radials: int = 4) -> str:
        """Quarter-wave vertical with radial ground plane."""
        svg = AntennaDiagrams.svg_header()

        # Ground
        svg += f'<line x1="50" y1="400" x2="550" y2="400" class="ground" stroke-dasharray="5,5"/>\n'

        # Mast/Element
        svg += f'<line x1="300" y1="400" x2="300" y2="100" class="wire"/>\n'

        # Radials (4-way)
        angles = [0, 90, 180, 270]
        radial_pixels = 120
        for angle in angles:
            rad = math.radians(angle)
            x2 = 300 + radial_pixels * math.cos(rad)
            y2 = 400 + radial_pixels * math.sin(rad)
            svg += f'<line x1="300" y1="400" x2="{x2}" y2="{y2}" class="radial"/>\n'

        # Feedpoint
        svg += f'<circle cx="300" cy="400" r="4" fill="{AntennaDiagrams.WIRE}"/>\n'

        # Balun (direct feed)
        svg += f'<text x="280" y="420" class="label">50Ω Direct</text>\n'

        # Dimensions
        svg += f'<line x1="270" y1="100" x2="270" y2="400" class="dimension"/>\n'
        svg += f'<text x="220" y="260" class="label">{elem_m:.2f}m</text>\n'

        # Radial dimension
        svg += f'<line x1="300" y1="415" x2="420" y2="415" class="dimension"/>\n'
        svg += f'<text x="340" y="430" class="label">{radial_m:.2f}m ea.</text>\n'

        # Labels
        svg += f'<text x="50" y="30" style="font-size: 14px; font-weight: bold; fill: {AntennaDiagrams.WIRE}">Vertical (¼λ)</text>\n'
        svg += f'<text x="50" y="50" class="label">Element: {elem_m:.2f}m</text>\n'
        svg += f'<text x="50" y="65" class="label">Radials: {num_radials} × {radial_m:.2f}m</text>\n'

        svg += '</svg>'
        return svg

    @staticmethod
    def invv_diagram(total_m: float, half_m: float, angle: int = 45) -> str:
        """Inverted-V dipole with droop angle."""
        svg = AntennaDiagrams.svg_header()

        # Ground
        svg += f'<line x1="50" y1="420" x2="550" y2="420" class="ground" stroke-dasharray="5,5"/>\n'

        # Apex
        apex_x, apex_y = 300, 120

        # Calculate droop based on angle
        half_span = 150 * math.cos(math.radians(angle))
        drop = 150 * math.sin(math.radians(angle))

        left_x = apex_x - half_span
        right_x = apex_x + half_span
        base_y = apex_y + drop

        # Legs
        svg += f'<line x1="{left_x}" y1="{base_y}" x2="{apex_x}" y2="{apex_y}" class="wire"/>\n'
        svg += f'<line x1="{apex_x}" y1="{apex_y}" x2="{right_x}" y2="{base_y}" class="wire"/>\n'

        # Feedpoint at apex
        svg += f'<circle cx="{apex_x}" cy="{apex_y}" r="4" fill="{AntennaDiagrams.WIRE}"/>\n'

        # Balun
        svg += f'<circle cx="{apex_x}" cy="{apex_y+25}" r="7" class="balun"/>\n'
        svg += f'<text x="{apex_x+8}" y="{apex_y+28}" class="label">1:1</text>\n'

        # Coax
        svg += f'<line x1="{apex_x}" y1="{apex_y+32}" x2="{apex_x}" y2="420" class="wire" stroke-dasharray="3,3"/>\n'

        # Ground stakes
        for x in [left_x, right_x]:
            svg += f'<circle cx="{x}" cy="420" r="3" fill="{AntennaDiagrams.WIRE}"/>\n'

        # Dimensions
        svg += f'<text x="{left_x-40}" y="{apex_y+drop/2-20}" class="label">{half_m:.2f}m</text>\n'
        svg += f'<text x="{right_x+10}" y="{apex_y+drop/2-20}" class="label">{half_m:.2f}m</text>\n'

        # Labels
        svg += f'<text x="50" y="30" style="font-size: 14px; font-weight: bold; fill: {AntennaDiagrams.WIRE}">Inverted-V</text>\n'
        svg += f'<text x="50" y="50" class="label">Total: {total_m:.2f}m</text>\n'
        svg += f'<text x="50" y="65" class="label">Droop: {angle}° from horizontal</text>\n'

        svg += '</svg>'
        return svg

    @staticmethod
    def efhw_diagram(total_m: float, cp_m: float) -> str:
        """End-Fed Half-Wave with 49:1 UnUn and counterpoise."""
        svg = AntennaDiagrams.svg_header()

        # Ground
        svg += f'<line x1="50" y1="400" x2="550" y2="400" class="ground" stroke-dasharray="5,5"/>\n'

        # Wire element (vertical then sloping)
        svg += f'<line x1="150" y1="400" x2="150" y2="150" class="wire"/>\n'
        svg += f'<line x1="150" y1="150" x2="450" y2="250" class="wire"/>\n'

        # End feedpoint
        svg += f'<circle cx="450" cy="250" r="4" fill="{AntennaDiagrams.WIRE}"/>\n'

        # 49:1 UnUn (toroid representation)
        svg += f'<circle cx="440" cy="280" r="12" class="balun"/>\n'
        svg += f'<text x="425" y="285" class="label">49:1</text>\n'

        # Coax from UnUn
        svg += f'<line x1="440" y1="292" x2="440" y2="400" class="wire" stroke-dasharray="3,3"/>\n'

        # Counterpoise radial
        svg += f'<line x1="440" y1="400" x2="300" y2="400" class="radial"/>\n'
        svg += f'<circle cx="440" cy="400" r="3" fill="{AntennaDiagrams.WIRE}"/>\n'

        # Dimensions
        svg += f'<line x1="110" y1="150" x2="110" y2="400" class="dimension"/>\n'
        svg += f'<text x="60" y="280" class="label">{total_m:.2f}m</text>\n'

        svg += f'<line x1="440" y1="415" x2="300" y2="415" class="dimension"/>\n'
        svg += f'<text x="340" y="430" class="label">CP: {cp_m:.2f}m</text>\n'

        # Labels
        svg += f'<text x="50" y="30" style="font-size: 14px; font-weight: bold; fill: {AntennaDiagrams.WIRE}">EFHW (½λ)</text>\n'
        svg += f'<text x="50" y="50" class="label">Wire: {total_m:.2f}m (one end feed)</text>\n'
        svg += f'<text x="50" y="65" class="label">Matching: 49:1 UnUn + CP</text>\n'

        svg += '</svg>'
        return svg

    @staticmethod
    def loop_diagram(perimeter_m: float, side_m: float) -> str:
        """Full-wave loop (square configuration)."""
        svg = AntennaDiagrams.svg_header()

        # Ground
        svg += f'<line x1="50" y1="420" x2="550" y2="420" class="ground" stroke-dasharray="5,5"/>\n'

        # Square loop (centered)
        loop_size = 140
        cx, cy = 300, 200

        corners = [
            (cx - loop_size, cy - loop_size),
            (cx + loop_size, cy - loop_size),
            (cx + loop_size, cy + loop_size),
            (cx - loop_size, cy + loop_size),
        ]

        # Draw loop
        for i in range(4):
            x1, y1 = corners[i]
            x2, y2 = corners[(i + 1) % 4]
            svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="wire"/>\n'

        # Feedpoint at corner
        feed_x, feed_y = corners[0]
        svg += f'<circle cx="{feed_x}" cy="{feed_y}" r="4" fill="{AntennaDiagrams.WIRE}"/>\n'

        # 4:1 Balun
        svg += f'<circle cx="{feed_x-20}" cy="{feed_y+20}" r="10" class="balun"/>\n'
        svg += f'<text x="{feed_x-28}" y="{feed_y+24}" class="label">4:1</text>\n'

        # Coax
        svg += f'<line x1="{feed_x-20}" y1="{feed_y+30}" x2="{feed_x-20}" y2="420" class="wire" stroke-dasharray="3,3"/>\n'

        # Dimensions
        svg += f'<text x="200" y="180" class="label">{side_m:.2f}m</text>\n'
        svg += f'<text x="320" y="280" class="label">{side_m:.2f}m</text>\n'

        # Labels
        svg += f'<text x="50" y="30" style="font-size: 14px; font-weight: bold; fill: {AntennaDiagrams.WIRE}">Full-Wave Loop</text>\n'
        svg += f'<text x="50" y="50" class="label">Perimeter: {perimeter_m:.2f}m</text>\n'
        svg += f'<text x="50" y="65" class="label">Feed: Corner (4:1 Balun)</text>\n'

        svg += '</svg>'
        return svg

    @staticmethod
    def delta_diagram(side_m: float, height_m: float) -> str:
        """Delta loop (triangular configuration)."""
        svg = AntennaDiagrams.svg_header()

        # Ground
        svg += f'<line x1="50" y1="420" x2="550" y2="420" class="ground" stroke-dasharray="5,5"/>\n'

        # Triangle (apex at top)
        apex_x, apex_y = 300, 100
        base_y = 350
        half_base = 120

        # Sides
        svg += f'<line x1="{apex_x-half_base}" y1="{base_y}" x2="{apex_x}" y2="{apex_y}" class="wire"/>\n'
        svg += f'<line x1="{apex_x}" y1="{apex_y}" x2="{apex_x+half_base}" y2="{base_y}" class="wire"/>\n'
        svg += f'<line x1="{apex_x+half_base}" y1="{base_y}" x2="{apex_x-half_base}" y2="{base_y}" class="wire"/>\n'

        # Apex support
        svg += f'<line x1="{apex_x}" y1="{apex_y}" x2="{apex_x}" y2="60" class="radial" stroke-width="1" stroke-dasharray="2,2"/>\n'

        # Feedpoint at bottom corner
        feed_x, feed_y = apex_x - half_base, base_y
        svg += f'<circle cx="{feed_x}" cy="{feed_y}" r="4" fill="{AntennaDiagrams.WIRE}"/>\n'

        # 4:1 Balun
        svg += f'<circle cx="{feed_x-20}" cy="{feed_y+20}" r="10" class="balun"/>\n'
        svg += f'<text x="{feed_x-28}" y="{feed_y+24}" class="label">4:1</text>\n'

        # Coax
        svg += f'<line x1="{feed_x-20}" y1="{feed_y+30}" x2="{feed_x-20}" y2="420" class="wire" stroke-dasharray="3,3"/>\n'

        # Dimensions
        svg += f'<text x="{apex_x-80}" y="{(apex_y+base_y)/2-10}" class="label">{side_m:.2f}m</text>\n'
        svg += f'<text x="{apex_x}" y="85" class="label">{height_m:.2f}m</text>\n'

        # Labels
        svg += f'<text x="50" y="30" style="font-size: 14px; font-weight: bold; fill: {AntennaDiagrams.WIRE}">Delta Loop</text>\n'
        svg += f'<text x="50" y="50" class="label">Each side: {side_m:.2f}m</text>\n'
        svg += f'<text x="50" y="65" class="label">Height: {height_m:.2f}m</text>\n'

        svg += '</svg>'
        return svg
