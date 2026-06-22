"""HAMIOS Antenna Calculator Module

Complete antenna design calculator with:
- Dipole, EFHW, and Ground Plane antenna types
- Realtime calculations with dynamic graphics
- Feedline loss calculator
- Antenna library management (save/load/delete)
- PDF report generation
"""

from .antenna_calculator_dialog import AntennaCalculatorDialog
from .antenna_models import (
    AntennaType, WireType, CoaxType, UnunType,
    FrequencyBand, DipoleCalculation, EfhwCalculation, GroundPlaneCalculation,
    SavedAntenna, AMATEUR_BANDS
)
from .antenna_math import (
    DipoleCalculator, EfhwCalculator, GroundPlaneCalculator,
    FeedlineCalculator, MiscCalculations
)
from .antenna_graphics import AntennaGraphicsEngine
from .feedline_calculator import FeedlineCalculatorTab, COAX_SPECS
from .antenna_library import AntennaLibrary
from .pdf_generator import PdfGenerator

__all__ = [
    "AntennaCalculatorDialog",
    "AntennaType",
    "WireType",
    "CoaxType",
    "UnunType",
    "FrequencyBand",
    "DipoleCalculation",
    "EfhwCalculation",
    "GroundPlaneCalculation",
    "SavedAntenna",
    "AMATEUR_BANDS",
    "DipoleCalculator",
    "EfhwCalculator",
    "GroundPlaneCalculator",
    "FeedlineCalculator",
    "MiscCalculations",
    "AntennaGraphicsEngine",
    "FeedlineCalculatorTab",
    "AntennaLibrary",
    "PdfGenerator",
    "COAX_SPECS",
]
