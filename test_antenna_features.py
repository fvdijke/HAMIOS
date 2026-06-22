"""Unit tests for Antenna Calculator features"""

from modules.antenna_calculator import (
    DipoleCalculator, EfhwCalculator, GroundPlaneCalculator,
    FeedlineCalculator, MiscCalculations, AntennaLibrary,
    AMATEUR_BANDS, WireType
)
import tempfile
from pathlib import Path

def test_dipole_calculation():
    """Test dipole antenna calculation"""
    result = DipoleCalculator.calculate(7.1, 0.95)
    assert result.total_length_m > 0
    assert result.impedance_ohms == 73
    assert result.efficiency_percent == 90.0
    print("[OK] Dipole calculation works")

def test_efhw_calculation():
    """Test EFHW antenna calculation"""
    result = EfhwCalculator.calculate(7.1, 0.95)
    assert result.total_length_m > 0
    assert result.impedance_ohms == 50
    assert "49:1" in result.unun_recommended.value
    print("[OK] EFHW calculation works")

def test_ground_plane_calculation():
    """Test ground plane antenna calculation"""
    result = GroundPlaneCalculator.calculate(7.1, 0.95, 4)
    assert result.vertical_length_m > 0
    assert result.num_radials == 4
    assert result.impedance_ohms == 37
    print("[OK] Ground Plane calculation works")

def test_feedline_loss():
    """Test feedline loss calculations"""
    loss = FeedlineCalculator.calculate_loss(0.40, 20.0)  # 0.4 dB per 10m, 20m cable
    assert abs(loss - 0.80) < 0.01  # Should be 0.8 dB

    efficiency = FeedlineCalculator.loss_to_efficiency(0.8)
    assert 80 < efficiency < 100
    print("[OK] Feedline loss calculations work")

def test_misc_conversions():
    """Test misc calculations"""
    wavelength = MiscCalculations.frequency_to_wavelength(7.1)
    assert abs(wavelength - 42.25) < 0.1

    freq = MiscCalculations.wavelength_to_frequency(42.25)
    assert abs(freq - 7.1) < 0.1

    feet = MiscCalculations.meters_to_feet(10)
    assert abs(feet - 32.81) < 0.1

    swr = MiscCalculations.calculate_swr(73, 50)
    assert abs(swr - 1.46) < 0.01
    print("[OK] Misc conversions work")

def test_frequency_bands():
    """Test frequency band definitions"""
    assert "40m" in AMATEUR_BANDS
    band = AMATEUR_BANDS["40m"]
    assert band.center_mhz == 7.1
    assert band.center_hz == 7.1e6
    print("[OK] Frequency bands loaded correctly")

def test_wire_types():
    """Test wire type definitions"""
    assert WireType.BARE_COPPER.velocity_factor == 0.95
    assert WireType.DX_WIRE.display_name == "DX-Wire"
    print("[OK] Wire types defined correctly")

def test_antenna_library():
    """Test antenna library save/load/delete"""
    with tempfile.TemporaryDirectory() as tmpdir:
        library = AntennaLibrary(tmpdir)

        from modules.antenna_calculator import SavedAntenna, AntennaType

        antenna = SavedAntenna(
            name="Test 40m Dipole",
            description="Test antenna",
            antenna_type=AntennaType.DIPOLE,
            frequency_mhz=7.1,
            wire_type=WireType.BARE_COPPER,
            velocity_factor=0.95,
        )

        # Save
        assert library.save_antenna(antenna)

        # Check exists
        assert library.antenna_exists("Test 40m Dipole")

        # Load
        loaded = library.load_antenna("Test 40m Dipole")
        assert loaded is not None
        assert loaded.frequency_mhz == 7.1

        # List
        antennas = library.list_antennas()
        assert "Test 40m Dipole" in antennas

        # Delete
        assert library.delete_antenna("Test 40m Dipole")
        assert not library.antenna_exists("Test 40m Dipole")

    print("[OK] Antenna library works (save/load/delete)")

def run_all_tests():
    """Run all tests"""
    print("\n=== ANTENNA CALCULATOR TEST SUITE ===\n")

    test_dipole_calculation()
    test_efhw_calculation()
    test_ground_plane_calculation()
    test_feedline_loss()
    test_misc_conversions()
    test_frequency_bands()
    test_wire_types()
    test_antenna_library()

    print("\n=== ALL TESTS PASSED ===\n")

if __name__ == "__main__":
    run_all_tests()
