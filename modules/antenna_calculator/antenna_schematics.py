"""HAMIOS Antenna Calculator - Simplified Antenna Schematics

Clean, text-based schematic diagrams that are easy to understand and maintain.
"""


class AntennaSchematic:
    """Generate simple ASCII schematics for antennas."""

    @staticmethod
    def dipole(total_m: float, half_m: float) -> str:
        """Half-wave dipole - horizontal."""
        return f"""
╔════════════════════════════════════════════════════════════════════╗
║                         DIPOLE (½λ)                                ║
║                                                                    ║
║                        ◉ Feedpoint (1:1)                          ║
║                        │                                           ║
║  ═══════════════════════○═══════════════════════                  ║
║  │←─ {half_m:.2f}m ─→│                                            ║
║  └─ Coax (50Ω)                                                     ║
║                                                                    ║
║  Total Length: {total_m:.2f}m                                             ║
║  Impedance: ~73Ω (resistive)                                       ║
║  Radiation: Omnidirectional (horizontal)                           ║
║  Best Height: ¼λ or higher above ground                            ║
║  Deployment: Hang horizontally between trees                       ║
╚════════════════════════════════════════════════════════════════════╝
"""

    @staticmethod
    def vertical(elem_m: float, radial_m: float, num_radials: int = 4) -> str:
        """Quarter-wave vertical with radial ground plane."""
        return f"""
╔════════════════════════════════════════════════════════════════════╗
║                       VERTICAL (¼λ)                                ║
║                                                                    ║
║                            ║ Element                               ║
║                            ║ {elem_m:.2f}m                                ║
║                            ║                                       ║
║                            ║                                       ║
║                  ════════════◉════════════                         ║
║                     50Ω Direct Feed (no balun)                     ║
║                                                                    ║
║         ═ Radial {num_radials}× · Length: {radial_m:.2f}m ea.                ║
║                  ═ Angle: 90° spacing ═                           ║
║                                                                    ║
║  Impedance: ~36-50Ω (with radials)                                 ║
║  Radiation: Low-angle omnidirectional (excellent DX)               ║
║  Deployment: Vertical element + radial wires on ground             ║
║  Performance: Better with more radials (4-8 minimum)               ║
╚════════════════════════════════════════════════════════════════════╝
"""

    @staticmethod
    def inverted_v(total_m: float, half_m: float) -> str:
        """Inverted-V dipole."""
        return f"""
╔════════════════════════════════════════════════════════════════════╗
║                        INVERTED-V                                  ║
║                                                                    ║
║                          ▲                                         ║
║                          │ Apex (1:1 Balun)                       ║
║                         ╱│╲                                        ║
║                        ╱ │ ╲                                       ║
║                       ╱  │  ╲  {half_m:.2f}m per leg                    ║
║                      ╱   │   ╲                                     ║
║                     ╱    │    ╲                                    ║
║                    ╱     │     ╲                                   ║
║                   ╱      │      ╲                                  ║
║                  ╱ ~45°  │ ~45°  ╲                                ║
║                 ●                  ●                               ║
║               Ground Stake      Ground Stake                       ║
║                                                                    ║
║  Total Length: {total_m:.2f}m                                             ║
║  Impedance: ~50-75Ω (varies by angle)                               ║
║  Radiation: Low-angle for DX (45° angle)                           ║
║  Advantage: Single support point needed (at apex)                  ║
╚════════════════════════════════════════════════════════════════════╝
"""

    @staticmethod
    def efhw(total_m: float, cp_m: float) -> str:
        """End-Fed Half-Wave with 49:1 UnUn."""
        return f"""
╔════════════════════════════════════════════════════════════════════╗
║                     END-FED HALF-WAVE (EFHW)                       ║
║                                                                    ║
║  Wire element (vertical/sloped): {total_m:.2f}m total                  ║
║                                                                    ║
║  ╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱ Wire                                             ║
║  ↓                                                                 ║
║  ◎  49:1 UnUn  ← Feedpoint                                        ║
║  ║                                                                 ║
║  Coax (50Ω) ─────                                                  ║
║                                                                    ║
║  Counterpoise: {cp_m:.2f}m (5% of wire)                                 ║
║  ─ Horizontal radial from feedpoint                                ║
║                                                                    ║
║  Impedance: ~2400Ω → 50Ω (via 49:1)                               ║
║  Matching: REQUIRES 49:1 UnUn at feedpoint                        ║
║  Deployment: End-fed (one end in tree, other grounded/radial)      ║
║  Config: Vertical (NVIS) or Sloper (DX)                            ║
╚════════════════════════════════════════════════════════════════════╝
"""

    @staticmethod
    def loop(perimeter_m: float, side_m: float) -> str:
        """Full-wave loop (square)."""
        return f"""
╔════════════════════════════════════════════════════════════════════╗
║                      FULL-WAVE LOOP (Square)                       ║
║                                                                    ║
║     ┌──────────────────────────────┐                              ║
║     │ Side: {side_m:.2f}m                    │                              ║
║     │                              │                              ║
║     │                              │                              ║
║     │      Feedpoint (4:1 Balun)   │                              ║
║     ◉                              │                              ║
║     │                              │                              ║
║     │                              │                              ║
║     └──────────────────────────────┘                              ║
║                                                                    ║
║  Perimeter: {perimeter_m:.2f}m (full wavelength)                          ║
║  Feedpoint: At corner (4:1 Balun)                                  ║
║  Impedance: ~100-300Ω → 50Ω (via 4:1)                             ║
║  Radiation: Low-angle to feedpoint side (DX)                       ║
║  Alternate: Feed at center top for NVIS                            ║
║  Gain: ~1-1.5 dB over dipole                                       ║
╚════════════════════════════════════════════════════════════════════╝
"""

    @staticmethod
    def generic(antenna_name: str, formula: str, impedance: str) -> str:
        """Generic schematic for other antenna types."""
        return f"""
╔════════════════════════════════════════════════════════════════════╗
║  {antenna_name:<58}║
║                                                                    ║
║  Formula: {formula:<52}║
║  Impedance: {impedance:<50}║
║                                                                    ║
║  ► Use the Calculated Dimensions above for exact lengths           ║
║  ► Check Field Deployment Notes for specific setup instructions   ║
║  ► See Library for saved antenna configurations                    ║
║                                                                    ║
║  For detailed schematic diagrams, refer to antenna documentation  ║
║  or use the antenna's specific design guide.                       ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
"""
