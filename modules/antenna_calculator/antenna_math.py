"""HAMIOS Antenna Calculator - Math Engine

Pure Python calculations for antenna dimensions and properties.
No GUI dependencies - can be tested independently.
"""

import math
from typing import NamedTuple
from .antenna_models import (
    DipoleCalculation, EfhwCalculation, GroundPlaneCalculation,
    UnunType, WireType
)


class AntennaConstants:
    """Physical constants for antenna calculations."""
    SPEED_OF_LIGHT = 299_792_458  # meters per second
    DIPOLE_FACTOR = 468.0  # MHz to feet conversion factor (for half-wave dipole)
    WAVELENGTH_FACTOR = 300.0  # MHz to meters conversion factor


class DipoleCalculator:
    """Calculate dipole antenna dimensions and characteristics."""

    @staticmethod
    def calculate(
        frequency_mhz: float,
        velocity_factor: float = 0.95,
    ) -> DipoleCalculation:
        """
        Calculate half-wave dipole dimensions.

        Args:
            frequency_mhz: Center frequency in MHz
            velocity_factor: Wire velocity factor (0.90-0.98)

        Returns:
            DipoleCalculation with all results
        """
        # Wavelength at given frequency
        wavelength_m = AntennaConstants.WAVELENGTH_FACTOR / frequency_mhz

        # Half-wave dipole is λ/2, adjusted for velocity factor and end effect
        # End effect correction factor: ~0.95 for typical wire dipole
        end_effect_factor = 0.95
        total_length_m = (wavelength_m / 2.0) * velocity_factor * end_effect_factor

        half_length_m = total_length_m / 2.0

        # Recommended height: 1/4 wavelength above ground minimum
        recommended_height_m = wavelength_m / 4.0

        # Theoretical impedance at resonance
        impedance_ohms = 73  # Real part of dipole impedance at 1/2λ

        # Radiation resistance (dipole)
        radiation_resistance = 73.0

        # Efficiency (typical: 85-95% depending on environment)
        efficiency_percent = 90.0

        return DipoleCalculation(
            total_length_m=round(total_length_m, 3),
            half_length_m=round(half_length_m, 3),
            recommended_height_m=round(recommended_height_m, 3),
            impedance_ohms=impedance_ohms,
            radiation_resistance=radiation_resistance,
            efficiency_percent=efficiency_percent,
        )


class EfhwCalculator:
    """Calculate EFHW (End-Fed Half Wave) antenna dimensions."""

    @staticmethod
    def calculate(
        frequency_mhz: float,
        velocity_factor: float = 0.95,
    ) -> EfhwCalculation:
        """
        Calculate EFHW antenna dimensions and matching requirements.

        Args:
            frequency_mhz: Center frequency in MHz
            velocity_factor: Wire velocity factor

        Returns:
            EfhwCalculation with all results and matching info
        """
        # Wavelength
        wavelength_m = AntennaConstants.WAVELENGTH_FACTOR / frequency_mhz

        # Half-wave resonant length (same as dipole)
        end_effect_factor = 0.95
        total_length_m = (wavelength_m / 2.0) * velocity_factor * end_effect_factor

        # Feedpoint is at the end (hence "End-Fed")
        # Typically 1-2% from the end for matching
        feedpoint_offset_m = total_length_m * 0.02  # 2% from end

        # End-fed half-wave has very high impedance at feedpoint (~2000-3000 ohms)
        # We recommend matching transformer
        raw_impedance = 2500  # Typical EFHW feedpoint impedance

        # Determine UNUN ratio based on impedance
        # 50Ω coax to 2500Ω = 2500/50 = 50:1 ≈ 49:1
        unun_recommended = UnunType.UNUN_49_1

        # Ferriet recommendation based on frequency band
        if frequency_mhz < 4:
            ferriet_type = "FT240-43 (2-4 MHz)"
        elif frequency_mhz < 8:
            ferriet_type = "FT240-43 or FT240-31 (4-8 MHz)"
        elif frequency_mhz < 15:
            ferriet_type = "FT240-31 (8-15 MHz)"
        else:
            ferriet_type = "FT240-31 or FT240-61 (15+ MHz)"

        # EFHW efficiency
        efficiency_percent = 85.0  # Slightly lower due to UNUN losses

        return EfhwCalculation(
            total_length_m=round(total_length_m, 3),
            feedpoint_offset_m=round(feedpoint_offset_m, 3),
            impedance_ohms=50,  # After matching to 50Ω
            unun_recommended=unun_recommended,
            ferriet_type=ferriet_type,
            efficiency_percent=efficiency_percent,
        )


class GroundPlaneCalculator:
    """Calculate Ground Plane vertical antenna dimensions."""

    @staticmethod
    def calculate(
        frequency_mhz: float,
        velocity_factor: float = 0.95,
        num_radials: int = 4,
    ) -> GroundPlaneCalculation:
        """
        Calculate ground plane vertical antenna dimensions.

        Args:
            frequency_mhz: Center frequency in MHz
            velocity_factor: Wire velocity factor
            num_radials: Number of radials (typically 4-8, default 4)

        Returns:
            GroundPlaneCalculation with all results
        """
        # Wavelength
        wavelength_m = AntennaConstants.WAVELENGTH_FACTOR / frequency_mhz

        # Vertical radiator: 1/4 wavelength
        end_effect_factor = 0.95
        vertical_length_m = (wavelength_m / 4.0) * velocity_factor * end_effect_factor

        # Radials: also 1/4 wavelength, slightly longer than vertical
        # (slight droop helps matching and improves ground plane)
        radial_length_m = (wavelength_m / 4.0) * velocity_factor * 1.02

        # Ground plane impedance at feedpoint
        # Quarter-wave vertical: ~36 ohms (with good ground plane)
        # With radials, typically 35-40 ohms
        impedance_ohms = 37

        # Take-off angle (radiation angle)
        # Lower frequency = higher take-off angle
        if frequency_mhz < 4:
            take_off_angle = 35.0
        elif frequency_mhz < 8:
            take_off_angle = 30.0
        elif frequency_mhz < 15:
            take_off_angle = 25.0
        elif frequency_mhz < 30:
            take_off_angle = 20.0
        else:
            take_off_angle = 15.0

        # Efficiency (ground plane quality dependent)
        # Good radial system: 85-90%
        efficiency_percent = 87.0

        return GroundPlaneCalculation(
            vertical_length_m=round(vertical_length_m, 3),
            radial_length_m=round(radial_length_m, 3),
            num_radials=num_radials,
            impedance_ohms=impedance_ohms,
            take_off_angle=take_off_angle,
            efficiency_percent=efficiency_percent,
        )


class FeedlineCalculator:
    """Calculate feedline loss and system efficiency."""

    @staticmethod
    def calculate_loss(
        cable_loss_db_per_10m: float,
        length_m: float,
    ) -> float:
        """
        Calculate total feedline loss.

        Args:
            cable_loss_db_per_10m: Cable loss specification in dB per 10m
            length_m: Cable length in meters

        Returns:
            Total loss in dB
        """
        return (length_m / 10.0) * cable_loss_db_per_10m

    @staticmethod
    def loss_to_efficiency(loss_db: float) -> float:
        """
        Convert dB loss to efficiency percentage.

        Args:
            loss_db: Loss in dB (positive number)

        Returns:
            Efficiency as percentage (0-100)
        """
        # Loss in dB = -10 * log10(efficiency)
        # efficiency = 10^(-loss_db/10)
        efficiency = 10.0 ** (-loss_db / 10.0)
        return efficiency * 100.0


class MiscCalculations:
    """Miscellaneous antenna calculations."""

    @staticmethod
    def wavelength_to_frequency(wavelength_m: float) -> float:
        """Convert wavelength to frequency."""
        if wavelength_m <= 0:
            return 0.0
        return AntennaConstants.WAVELENGTH_FACTOR / wavelength_m

    @staticmethod
    def frequency_to_wavelength(frequency_mhz: float) -> float:
        """Convert frequency to wavelength."""
        if frequency_mhz <= 0:
            return 0.0
        return AntennaConstants.WAVELENGTH_FACTOR / frequency_mhz

    @staticmethod
    def meters_to_feet(meters: float) -> float:
        """Convert meters to feet."""
        return meters * 3.28084

    @staticmethod
    def feet_to_meters(feet: float) -> float:
        """Convert feet to meters."""
        return feet / 3.28084

    @staticmethod
    def calculate_swr(
        antenna_impedance: int,
        feedline_impedance: int = 50,
    ) -> float:
        """
        Calculate SWR (Standing Wave Ratio).

        Args:
            antenna_impedance: Antenna feedpoint impedance in ohms
            feedline_impedance: Feedline impedance (typically 50 or 75 ohms)

        Returns:
            SWR value
        """
        if feedline_impedance <= 0 or antenna_impedance <= 0:
            return 1.0

        ratio = antenna_impedance / feedline_impedance
        if ratio >= 1:
            return ratio
        else:
            return 1.0 / ratio

    @staticmethod
    def impedance_to_return_loss(swr: float) -> float:
        """
        Convert SWR to return loss in dB.

        Args:
            swr: Standing Wave Ratio

        Returns:
            Return loss in dB
        """
        if swr <= 1.0:
            return float('inf')
        return 20.0 * math.log10((swr - 1.0) / (swr + 1.0))
