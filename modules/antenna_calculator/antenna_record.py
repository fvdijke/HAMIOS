"""HAMIOS Antenna Calculator - Field Record & Birth Certificate

Document antenna builds, measurements, and field notes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class AntennaRecord:
    """Complete antenna birth certificate and field record."""

    callsign: str                          # Amateur radio callsign
    antenna_type: str                      # Type of antenna
    date_built: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    location_grid: str = ""               # Grid square or location

    # Calculated/Theoretical
    target_frequency_mhz: float = 7.0
    wire_type: str = "Bare Copper"
    velocity_factor: float = 0.95
    calculated_length_m: float = 0.0

    # As-Built/Measured
    final_tuned_length_m: Optional[float] = None
    resonant_frequency_mhz: Optional[float] = None
    measured_swr: Optional[float] = None
    impedance_ohms: Optional[int] = None

    # Ground Plane specifics (for verticals)
    num_radials: int = 4
    radial_length_m: Optional[float] = None
    counter_poise_system: str = ""        # Description of counter poise

    # Feedline details
    feedline_type: str = ""               # RG-58, LMR-400, etc.
    feedline_length_m: float = 0.0
    feedline_swr_loss_db: Optional[float] = None

    # Field notes and observations
    field_notes: str = ""
    construction_notes: str = ""
    performance_notes: str = ""

    # Environmental conditions
    weather_conditions: str = ""
    ground_conditions: str = ""
    nearby_obstacles: str = ""

    def to_html(self) -> str:
        """Generate HTML antenna birth certificate."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Antenna Record - {self.callsign} - {self.antenna_type} - {self.date_built}</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            max-width: 700px;
            margin: 40px auto;
            padding: 20px;
            color: #000;
            background: #fff;
        }}
        h1 {{
            font-size: 18px;
            letter-spacing: 3px;
            text-transform: uppercase;
            border-bottom: 2px solid #000;
            padding-bottom: 8px;
            margin-bottom: 4px;
        }}
        .sub {{
            font-size: 10px;
            letter-spacing: 2px;
            color: #444;
            margin-bottom: 20px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 16px;
        }}
        .field {{
            border: 1px solid #ccc;
            padding: 8px 10px;
            border-radius: 2px;
        }}
        .label {{
            font-size: 9px;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #666;
            margin-bottom: 3px;
        }}
        .value {{
            font-size: 13px;
            font-weight: bold;
        }}
        .highlight {{
            border-color: #000;
            background: #f5f5f5;
        }}
        .notes-box {{
            border: 1px solid #ccc;
            padding: 10px;
            min-height: 80px;
            white-space: pre-wrap;
            font-size: 11px;
            line-height: 1.6;
        }}
        .footer {{
            margin-top: 24px;
            font-size: 9px;
            color: #888;
            letter-spacing: 1px;
            border-top: 1px solid #ccc;
            padding-top: 8px;
        }}
        h2 {{
            font-size: 11px;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin: 16px 0 8px;
        }}
        @media print {{
            body {{ margin: 20px; }}
        }}
    </style>
</head>
<body>

<h1>{self.callsign} &mdash; Antenna Birth Certificate</h1>
<div class="sub">ANTENNA RECORD v1.0 &mdash; {self.antenna_type.upper()}</div>

<h2>Antenna Details</h2>
<div class="grid">
    <div class="field"><div class="label">Callsign</div><div class="value">{self.callsign}</div></div>
    <div class="field"><div class="label">Date Built</div><div class="value">{self.date_built}</div></div>
    <div class="field"><div class="label">Location / Grid</div><div class="value">{self.location_grid or '—'}</div></div>
    <div class="field"><div class="label">Wire Type</div><div class="value">{self.wire_type}</div></div>
</div>

<h2>Antenna Configuration (Calculated)</h2>
<div class="grid">
    <div class="field"><div class="label">Antenna Type</div><div class="value">{self.antenna_type}</div></div>
    <div class="field"><div class="label">Target Frequency</div><div class="value">{self.target_frequency_mhz} MHz</div></div>
    <div class="field"><div class="label">Wire Velocity Factor</div><div class="value">{self.velocity_factor:.3f}</div></div>
    <div class="field"><div class="label">Calculated Length</div><div class="value">{self.calculated_length_m:.2f} m</div></div>
</div>

<h2>As-Built (After Field Tuning)</h2>
<div class="grid">
    <div class="field highlight"><div class="label">Final Tuned Length</div><div class="value">{self.final_tuned_length_m or '[NOT RECORDED]'} m</div></div>
    <div class="field highlight"><div class="label">Resonant Frequency</div><div class="value">{self.resonant_frequency_mhz or '[NOT RECORDED]'} MHz</div></div>
    <div class="field highlight"><div class="label">Measured SWR</div><div class="value">{self.measured_swr or '[NOT RECORDED]'}</div></div>
    <div class="field highlight"><div class="label">Feedpoint Impedance</div><div class="value">{self.impedance_ohms or '[NOT RECORDED]'} Ω</div></div>
</div>
"""

        # Ground plane section (if applicable)
        if "vertical" in self.antenna_type.lower() or "ground" in self.antenna_type.lower():
            html += f"""
<h2>Ground Plane / Radial System</h2>
<div class="grid">
    <div class="field"><div class="label">Number of Radials</div><div class="value">{self.num_radials}</div></div>
    <div class="field"><div class="label">Radial Length</div><div class="value">{self.radial_length_m or '[NOT RECORDED]'} m</div></div>
    <div class="field"><div class="label">Counter Poise System</div><div class="value">{self.counter_poise_system or '[NONE]'}</div></div>
</div>
"""

        # Feedline section
        if self.feedline_type:
            html += f"""
<h2>Feedline Details</h2>
<div class="grid">
    <div class="field"><div class="label">Cable Type</div><div class="value">{self.feedline_type}</div></div>
    <div class="field"><div class="label">Cable Length</div><div class="value">{self.feedline_length_m:.2f} m</div></div>
    <div class="field"><div class="label">Feedline Loss (@ freq)</div><div class="value">{self.feedline_swr_loss_db or '[NOT RECORDED]'} dB</div></div>
</div>
"""

        html += f"""
<h2>Field Notes & Observations</h2>
<div class="notes-box">{self.field_notes or '(none)'}</div>

<h2>Construction Notes</h2>
<div class="notes-box">{self.construction_notes or '(none)'}</div>

<h2>Performance Notes</h2>
<div class="notes-box">{self.performance_notes or '(none)'}</div>

<h2>Environmental Conditions</h2>
<div class="grid">
    <div class="field"><div class="label">Weather</div><div class="value">{self.weather_conditions or '—'}</div></div>
    <div class="field"><div class="label">Ground Type</div><div class="value">{self.ground_conditions or '—'}</div></div>
    <div class="field"><div class="label">Nearby Obstacles</div><div class="value">{self.nearby_obstacles or '—'}</div></div>
</div>

<div class="footer">
Generated by HAMIOS Antenna Calculator v1.0 — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
Store this record with your antenna components for future reference.
</div>

</body>
</html>
"""
        return html

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON storage."""
        return {
            "callsign": self.callsign,
            "antenna_type": self.antenna_type,
            "date_built": self.date_built,
            "location_grid": self.location_grid,
            "target_frequency_mhz": self.target_frequency_mhz,
            "wire_type": self.wire_type,
            "velocity_factor": self.velocity_factor,
            "calculated_length_m": self.calculated_length_m,
            "final_tuned_length_m": self.final_tuned_length_m,
            "resonant_frequency_mhz": self.resonant_frequency_mhz,
            "measured_swr": self.measured_swr,
            "impedance_ohms": self.impedance_ohms,
            "num_radials": self.num_radials,
            "radial_length_m": self.radial_length_m,
            "counter_poise_system": self.counter_poise_system,
            "feedline_type": self.feedline_type,
            "feedline_length_m": self.feedline_length_m,
            "feedline_swr_loss_db": self.feedline_swr_loss_db,
            "field_notes": self.field_notes,
            "construction_notes": self.construction_notes,
            "performance_notes": self.performance_notes,
            "weather_conditions": self.weather_conditions,
            "ground_conditions": self.ground_conditions,
            "nearby_obstacles": self.nearby_obstacles,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AntennaRecord":
        """Create from dictionary."""
        return cls(**data)


class FieldExpeditentSWRCheck:
    """Simple field expedient SWR check methods (no expensive equipment)."""

    @staticmethod
    def estimate_swr_from_impedance(antenna_impedance: int, feedline_impedance: int = 50) -> float:
        """Estimate SWR from antenna impedance."""
        if feedline_impedance <= 0 or antenna_impedance <= 0:
            return 1.0
        ratio = antenna_impedance / feedline_impedance
        return max(ratio, 1.0 / ratio) if ratio >= 1 else 1.0 / ratio

    @staticmethod
    def impedance_from_swr(swr: float, feedline_impedance: int = 50) -> tuple[int, int]:
        """
        Estimate possible antenna impedances from SWR reading.
        Returns (resistive, reactive) component estimates.
        """
        if swr <= 1.0:
            return (feedline_impedance, 0)

        # For simplification, assume purely resistive load
        # R_ant = Z0 * ((SWR + 1) / (SWR - 1)) or Z0 * ((SWR - 1) / (SWR + 1))
        r_high = feedline_impedance * ((swr + 1) / (swr - 1))
        r_low = feedline_impedance * ((swr - 1) / (swr + 1))

        return (int(r_high), int(r_low))

    @staticmethod
    def field_check_checklist() -> list[str]:
        """Return a field expedient SWR check checklist."""
        return [
            "1. Disconnect coax from transmitter",
            "2. Connect antenna to 50Ω dummy load (if available)",
            "3. Measure with SWR meter or impedance analyzer",
            "4. Record frequency and SWR reading",
            "5. If SWR > 2.0, antenna is far from resonance",
            "6. Adjust antenna length incrementally and recheck",
            "7. Record final resonant frequency and SWR",
            "8. Verify feedline is dry and connections are secure",
            "9. Store antenna record with photographs",
            "10. Test on air with low power before full operation",
        ]
