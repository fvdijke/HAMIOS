"""HAMIOS Antenna Calculator - Data Models

Dataclasses for antenna types, feedlines, and calculations.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime


# ── Enums ─────────────────────────────────────────────────────────────────────

class AntennaType(Enum):
    """Supported antenna types."""
    DIPOLE = "dipole"
    EFHW = "efhw"
    GROUND_PLANE = "ground_plane"
    FULL_WAVE_LOOP = "full_wave_loop"
    DELTA_LOOP = "delta_loop"
    BEVERAGE = "beverage"
    MAGNETIC_LOOP = "magnetic_loop"


class WireType(Enum):
    """Wire material types with velocity factors."""
    BARE_COPPER = ("Bare Copper", 0.95)
    INSULATED_COPPER = ("Insulated Copper", 0.92)
    SPEAKER_WIRE = ("Speaker Wire", 0.90)
    DX_WIRE = ("DX-Wire", 0.95)
    ALUMINUM = ("Aluminum", 0.95)
    LITZE = ("Litze Wire", 0.95)
    CUSTOM = ("Custom", 0.95)

    def __init__(self, display_name: str, velocity_factor: float):
        self.display_name = display_name
        self.velocity_factor = velocity_factor


class CoaxType(Enum):
    """Coax cable types."""
    RG58 = "RG58"
    RG8X = "RG8X"
    RG213 = "RG213"
    RG214 = "RG214"
    AIRCELL_7 = "Aircell 7"
    AIRCELL_5 = "Aircell 5"
    ECOFLEX_10 = "Ecoflex 10"
    ECOFLEX_15 = "Ecoflex 15"
    LMR240 = "LMR240"
    LMR400 = "LMR400"
    LMR600 = "LMR600"
    H155 = "H155"
    H2000 = "H2000"


class UnunType(Enum):
    """UNUN transformer types."""
    NONE = "None"
    UNUN_1_1 = "1:1 UNUN"
    UNUN_4_1 = "4:1 UNUN"
    UNUN_9_1 = "9:1 UNUN"
    UNUN_49_1 = "49:1 UNUN"
    UNUN_64_1 = "64:1 UNUN"


# ── Frequency Bands ───────────────────────────────────────────────────────────

@dataclass
class FrequencyBand:
    """Amateur radio band definition."""
    name: str
    center_mhz: float
    start_mhz: float
    end_mhz: float

    @property
    def center_hz(self) -> float:
        """Center frequency in Hz."""
        return self.center_mhz * 1e6

    @property
    def wavelength_m(self) -> float:
        """Wavelength in meters at center frequency."""
        return 300 / self.center_mhz


# ── Antenna Calculations ──────────────────────────────────────────────────────

@dataclass
class DipoleCalculation:
    """Dipole antenna calculation results."""
    total_length_m: float          # Total length in meters
    half_length_m: float           # Length per side
    recommended_height_m: float    # Recommended mounting height
    impedance_ohms: int            # Expected feedpoint impedance
    radiation_resistance: float
    efficiency_percent: float


@dataclass
class EfhwCalculation:
    """EFHW (End-Fed Half Wave) calculation results."""
    total_length_m: float          # Total length
    feedpoint_offset_m: float      # Distance from end to feedpoint
    impedance_ohms: int            # Feedpoint impedance
    unun_recommended: UnunType     # Recommended UNUN ratio
    ferriet_type: str              # Recommended ferriet core
    efficiency_percent: float


@dataclass
class GroundPlaneCalculation:
    """Ground Plane vertical antenna calculation results."""
    vertical_length_m: float       # Vertical radiator length
    radial_length_m: float         # Length of each radial
    num_radials: int               # Number of radials (typical 4-8)
    impedance_ohms: int            # Feedpoint impedance
    take_off_angle: float          # Take-off angle in degrees
    efficiency_percent: float


@dataclass
class FullWaveLoopCalculation:
    """Full-wave loop antenna calculation results."""
    perimeter_m: float             # Total loop perimeter
    side_length_m: float            # Length per side (square loop)
    impedance_ohms: int            # Feedpoint impedance
    gain_dbi: float                # Gain relative to isotropic
    efficiency_percent: float


@dataclass
class DeltaLoopCalculation:
    """Delta (triangular) loop antenna calculation results."""
    perimeter_m: float             # Total perimeter
    height_m: float                # Height of triangle
    base_width_m: float            # Base width
    impedance_ohms: int            # Feedpoint impedance
    efficiency_percent: float


@dataclass
class BeverageCalculation:
    """Beverage antenna (traveling wave) calculation results."""
    length_m: float                # Antenna length
    height_m: float                # Height above ground
    termination_ohms: int          # Termination resistance
    impedance_ohms: int            # Feedpoint impedance
    gain_dbi: float                # Gain relative to isotropic
    directivity: str               # End-fire, broadside, etc.


@dataclass
class MagneticLoopCalculation:
    """Magnetic loop antenna calculation results."""
    diameter_m: float              # Loop diameter
    capacitance_min_pf: float      # Capacitor range minimum
    capacitance_max_pf: float      # Capacitor range maximum
    q_factor: float                # Quality factor
    impedance_ohms: int            # Feedpoint impedance
    efficiency_percent: float


# ── Feedline Data ─────────────────────────────────────────────────────────────

@dataclass
class FeedlineSpecs:
    """Feedline cable specifications."""
    name: str
    impedance_ohms: int
    velocity_factor: float
    loss_db_per_10m: dict[float, float]  # Frequency (MHz) -> Loss (dB)

    def get_loss_at_freq(self, freq_mhz: float) -> float:
        """Get cable loss at specific frequency."""
        if not self.loss_db_per_10m:
            return 0.0

        # Find closest frequency
        freqs = sorted(self.loss_db_per_10m.keys())
        if freq_mhz <= freqs[0]:
            return self.loss_db_per_10m[freqs[0]]
        if freq_mhz >= freqs[-1]:
            return self.loss_db_per_10m[freqs[-1]]

        # Linear interpolation
        for i in range(len(freqs) - 1):
            if freqs[i] <= freq_mhz <= freqs[i + 1]:
                f1, f2 = freqs[i], freqs[i + 1]
                loss1, loss2 = self.loss_db_per_10m[f1], self.loss_db_per_10m[f2]
                return loss1 + (loss2 - loss1) * (freq_mhz - f1) / (f2 - f1)

        return 0.0

    def calculate_total_loss(self, length_m: float, freq_mhz: float) -> float:
        """Calculate total cable loss for given length and frequency."""
        loss_per_10m = self.get_loss_at_freq(freq_mhz)
        return (length_m / 10.0) * loss_per_10m


# ── Saved Antenna ──────────────────────────────────────────────────────────────

@dataclass
class SavedAntenna:
    """User-saved antenna configuration."""
    name: str
    description: str
    antenna_type: AntennaType
    frequency_mhz: float
    wire_type: WireType
    velocity_factor: float
    feedline_type: Optional[CoaxType] = None
    feedline_length_m: float = 0.0
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    modified_date: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "antenna_type": self.antenna_type.value,
            "frequency_mhz": self.frequency_mhz,
            "wire_type": self.wire_type.name,
            "velocity_factor": self.velocity_factor,
            "feedline_type": self.feedline_type.value if self.feedline_type else None,
            "feedline_length_m": self.feedline_length_m,
            "created_date": self.created_date,
            "modified_date": self.modified_date,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SavedAntenna":
        """Create from dictionary (JSON deserialization)."""
        return cls(
            name=data["name"],
            description=data["description"],
            antenna_type=AntennaType(data["antenna_type"]),
            frequency_mhz=data["frequency_mhz"],
            wire_type=WireType[data["wire_type"]],
            velocity_factor=data["velocity_factor"],
            feedline_type=CoaxType(data["feedline_type"]) if data.get("feedline_type") else None,
            feedline_length_m=data.get("feedline_length_m", 0.0),
            created_date=data.get("created_date", datetime.now().isoformat()),
            modified_date=data.get("modified_date", datetime.now().isoformat()),
        )


# ── Predefined Bands ───────────────────────────────────────────────────────────

AMATEUR_BANDS = {
    "2200m": FrequencyBand("2200m", 0.1357, 0.1357, 0.1378),
    "630m": FrequencyBand("630m", 0.475, 0.472, 0.479),
    "160m": FrequencyBand("160m", 1.9, 1.8, 2.0),
    "80m": FrequencyBand("80m", 3.65, 3.5, 4.0),
    "60m": FrequencyBand("60m", 5.1, 5.06, 5.45),
    "40m": FrequencyBand("40m", 7.1, 7.0, 7.3),
    "30m": FrequencyBand("30m", 10.1, 10.1, 10.15),
    "20m": FrequencyBand("20m", 14.1, 14.0, 14.35),
    "17m": FrequencyBand("17m", 18.1, 18.068, 18.168),
    "15m": FrequencyBand("15m", 21.1, 21.0, 21.45),
    "12m": FrequencyBand("12m", 24.9, 24.89, 24.99),
    "10m": FrequencyBand("10m", 28.5, 28.0, 29.7),
    "6m": FrequencyBand("6m", 50.1, 50.0, 54.0),
    "4m": FrequencyBand("4m", 70.1, 70.0, 70.5),
    "2m": FrequencyBand("2m", 145.5, 144.0, 148.0),
    "70cm": FrequencyBand("70cm", 432.5, 420.0, 450.0),
    "23cm": FrequencyBand("23cm", 1296.5, 1240.0, 1300.0),
    "CB": FrequencyBand("CB (11m)", 27.0, 26.5, 27.5),
}
