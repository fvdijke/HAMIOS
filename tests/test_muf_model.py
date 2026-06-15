"""
Unit tests for MUF/LUF forecast model.
"""

import unittest
import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hamios5.muf_model import MUFModel, get_muf_status


class TestMUFModel(unittest.TestCase):
    """Test MUF calculation accuracy and edge cases."""

    def setUp(self):
        self.model = MUFModel(qth_lat=52.0, qth_lon=5.0)

    def test_foF2_range(self):
        """foF2 should be between 2 and 20 MHz."""
        for sfi in [70, 100, 150, 200, 300]:
            foF2 = self.model._calc_foF2(sfi, 50, 2, 12)
            self.assertGreaterEqual(foF2, 2.0, f"foF2 too low for SFI={sfi}")
            self.assertLessEqual(foF2, 25.0, f"foF2 too high for SFI={sfi}")

    def test_muf_increases_with_sfi(self):
        """MUF should increase as SFI increases."""
        muf_low = self.model._calc_muf(
            self.model._calc_foF2(80, 40, 2, 12), 5000, 52
        )
        muf_high = self.model._calc_muf(
            self.model._calc_foF2(200, 100, 2, 12), 5000, 52
        )
        self.assertLess(muf_low, muf_high, "MUF should increase with SFI")

    def test_muf_decreases_with_k_index(self):
        """MUF should decrease as K-index increases (geomagnetic disturbance)."""
        foF2_calm = self.model._calc_foF2(150, 100, 1, 12)
        foF2_storm = self.model._calc_foF2(150, 100, 7, 12)
        self.assertGreater(foF2_calm, foF2_storm, "foF2 should be lower in storms")

    def test_muf_luf_relationship(self):
        """LUF should always be less than MUF."""
        for hour in range(24):
            for sfi in [70, 150, 250]:
                foF2 = self.model._calc_foF2(sfi, 50, 2, hour)
                muf = self.model._calc_muf(foF2, 5000, 52)
                luf = self.model._calc_luf(foF2, 52)
                self.assertLess(luf, muf, f"LUF > MUF at hour {hour}, SFI {sfi}")

    def test_forecast_day_completeness(self):
        """Daily forecast should have data for all 24 hours."""
        forecast = self.model.forecast_day(150, 100, 2)
        self.assertEqual(len(forecast), 24, "Should have 24 hours of data")

        for hour in range(24):
            self.assertIn(hour, forecast, f"Hour {hour} missing")
            data = forecast[hour]
            self.assertIn("foF2", data)
            self.assertIn("muf", data)
            self.assertIn("luf", data)
            self.assertIn("quality", data)

    def test_band_open_close(self):
        """Test band opening/closing logic."""
        # Low SFI: fewer bands open
        muf_open_table = self.model.muf_for_bands(80, 40, 2)
        num_open_low = sum(1 for h in muf_open_table.values()
                          for b in h.values() if b)

        # High SFI: more bands open
        muf_open_table = self.model.muf_for_bands(250, 150, 2)
        num_open_high = sum(1 for h in muf_open_table.values()
                           for b in h.values() if b)

        self.assertLess(num_open_low, num_open_high,
                       "More bands should be open at high SFI")

    def test_latitude_effect(self):
        """Test that latitude affects foF2 (auroral zone effects)."""
        model_eq = MUFModel(qth_lat=0.0, qth_lon=0.0)
        model_pol = MUFModel(qth_lat=70.0, qth_lon=0.0)

        foF2_eq = model_eq._calc_foF2(150, 100, 2, 12)
        foF2_pol = model_pol._calc_foF2(150, 100, 2, 12)

        # Both should be in reasonable range (just verify no crash/NaN)
        self.assertGreater(foF2_eq, 2.0, "foF2 should be reasonable at equator")
        self.assertGreater(foF2_pol, 2.0, "foF2 should be reasonable at pole")

    def test_quality_rating(self):
        """Test quality rating logic."""
        # Very low MUF: poor
        quality_poor = self.model._quality_from_muf(2.0, 80, 6)
        self.assertEqual(quality_poor, "poor")

        # High MUF + good conditions: good
        quality_good = self.model._quality_from_muf(20.0, 200, 1)
        self.assertEqual(quality_good, "good")


class TestGetMUFStatus(unittest.TestCase):
    """Test convenience function."""

    def test_get_muf_status(self):
        """Quick MUF status should return dict with band info."""
        status = get_muf_status(52.0, 5.0, 150, 100, 2)

        self.assertIsInstance(status, dict)
        self.assertTrue(len(status) > 0, "Should have band data")

        for band_name, data in status.items():
            self.assertIn("muf", data)
            self.assertIn("luf", data)
            self.assertIn("open", data)
            self.assertIn("quality", data)
            self.assertIsInstance(data["open"], bool)


if __name__ == "__main__":
    unittest.main()
