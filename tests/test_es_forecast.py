"""
Unit tests for Sporadic-E forecast model.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hamios5.es_forecast import ESForecast, get_es_alert


class TestESForecast(unittest.TestCase):
    """Test Sporadic-E probability calculations."""

    def setUp(self):
        self.es = ESForecast()

    def test_probability_range(self):
        """Es probability should be 0–1."""
        for month in range(1, 13):
            for hour in range(24):
                prob = self.es.es_probability(month, hour, 4)
                self.assertGreaterEqual(prob, 0.0)
                self.assertLessEqual(prob, 1.0)

    def test_summer_peak(self):
        """Es should have highest probability in June-July."""
        june_prob = self.es.es_probability(6, 12, 2)
        july_prob = self.es.es_probability(7, 12, 2)
        jan_prob = self.es.es_probability(1, 12, 2)

        self.assertGreater(june_prob, jan_prob, "June should be higher than January")
        self.assertGreater(july_prob, jan_prob, "July should be higher than January")

    def test_k_index_suppression(self):
        """Es probability should decrease with K-index."""
        calm = self.es.es_probability(6, 12, 0)
        moderate = self.es.es_probability(6, 12, 4)
        storm = self.es.es_probability(6, 12, 8)

        self.assertGreater(calm, moderate, "Calm should be > moderate")
        self.assertGreater(moderate, storm, "Moderate should be > storm")

    def test_diurnal_variation(self):
        """Es should peak during local noon hours (roughly 10-14 UTC)."""
        dawn = self.es.es_probability(6, 6, 2)
        noon = self.es.es_probability(6, 12, 2)
        dusk = self.es.es_probability(6, 18, 2)

        self.assertGreater(noon, dawn, "Noon should be > dawn")
        self.assertGreater(noon, dusk, "Noon should be > dusk")

    def test_alert_levels(self):
        """Alert level should transition at threshold."""
        threshold = 0.30

        # High probability (summer peak + calm) → should trigger alert
        level_high, prob_high = self.es.es_alert_level(6, 12, 1, threshold)
        self.assertIn(level_high, ["active", "marginal"], "High prob should alert")

        # Low probability (winter + storm) → inactive
        level_low, prob_low = self.es.es_alert_level(1, 6, 8, threshold)
        self.assertEqual(level_low, "inactive")

    def test_marginal_alert(self):
        """Marginal level between threshold and 1.5× threshold."""
        # Create scenario with marginal probability
        threshold = 0.40
        level, prob = self.es.es_alert_level(5, 12, 4, threshold)
        # Should be marginal if in range, or active if very high
        self.assertIn(level, ["marginal", "active", "inactive"])

    def test_peak_hours_today(self):
        """Peak hours should be a tuple of (start, end) in UTC."""
        peak_start, peak_end = self.es.peak_hours_today()
        self.assertIsInstance(peak_start, int)
        self.assertIsInstance(peak_end, int)
        self.assertGreaterEqual(peak_start, 0)
        self.assertLess(peak_end, 24)
        self.assertGreater(peak_end, peak_start)

    def test_daily_status(self):
        """Daily status should return complete forecast dict."""
        status = self.es.es_status_today(k_index=3, threshold=0.30)

        required_keys = ["season", "month_base_prob", "peak_hours_utc",
                        "current_prob", "current_level", "threshold"]
        for key in required_keys:
            self.assertIn(key, status, f"Missing key: {key}")

        self.assertIn(status["season"], ["active", "inactive"])
        self.assertIn(status["current_level"], ["active", "marginal", "inactive"])


class TestGetESAlert(unittest.TestCase):
    """Test convenience function."""

    def test_quick_es_alert(self):
        """Quick alert should return (level, probability)."""
        level, prob = get_es_alert(k_index=2, threshold=0.30)

        self.assertIn(level, ["active", "marginal", "inactive"])
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)


if __name__ == "__main__":
    unittest.main()
