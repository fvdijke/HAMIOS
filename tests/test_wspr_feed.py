"""
Unit tests for WSPR feed integration.
"""

import unittest
import sys
import os
import json
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hamios5.wspr_feed import WSPRFeed, _mock_wspr_data


class TestWSPRFeedMock(unittest.TestCase):
    """Test WSPR mock data generation."""

    def test_mock_data_structure(self):
        """Mock data should have correct structure."""
        data = _mock_wspr_data()

        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0, "Should generate some records")

        for record in data:
            required_fields = [
                "call_sign", "grid", "band", "frequency", "snr",
                "distance", "azimuth", "time"
            ]
            for field in required_fields:
                self.assertIn(field, record, f"Missing field: {field}")

    def test_mock_frequencies(self):
        """Mock data should have realistic HF+VHF frequencies."""
        data = _mock_wspr_data()

        for record in data:
            freq = record["frequency"]
            self.assertGreater(freq, 1.0, "Frequency too low")
            self.assertLess(freq, 60.0, "Frequency too high (HF+6m)")

    def test_mock_snr_range(self):
        """SNR should be realistic (-30 to 0 dB)."""
        data = _mock_wspr_data()

        for record in data:
            snr = record["snr"]
            self.assertGreaterEqual(snr, -30, "SNR too low")
            self.assertLessEqual(snr, 5, "SNR too high")

    def test_mock_distance(self):
        """Distance should be reasonable."""
        data = _mock_wspr_data()

        for record in data:
            dist = record["distance"]
            self.assertGreater(dist, 0, "Distance should be positive")
            self.assertLess(dist, 20000, "Distance unrealistic")


class TestWSPRFeed(unittest.TestCase):
    """Test WSPR feed caching and filtering."""

    def setUp(self):
        self.feed = WSPRFeed(qth_lat=52.0, qth_lon=5.0)

    def test_distance_calculation(self):
        """Test great-circle distance calculation."""
        # Distance from Amsterdam to London (rough 350 km)
        dist = WSPRFeed.compute_distance(52.37, 4.89, 51.51, -0.13)

        self.assertGreater(dist, 300, "Distance should be around 350 km")
        self.assertLess(dist, 400)

    def test_distance_same_point(self):
        """Distance from same point should be ~0."""
        dist = WSPRFeed.compute_distance(52.0, 5.0, 52.0, 5.0)
        self.assertLess(dist, 1, "Same point distance should be ~0")

    def test_update_interval_minimum(self):
        """Update interval should have 30s minimum."""
        self.feed.set_update_interval(10)
        self.assertEqual(self.feed._update_interval, 30, "Should enforce 30s minimum")

    def test_cache_get_recent(self):
        """Test getting recent QSOs from cache."""
        # Manually populate cache with mock data
        mock_records = _mock_wspr_data()
        with self.feed._cache_lock:
            self.feed._cache = mock_records

        # Get all records from last hour
        recent = self.feed.get_recent_qsos(hours=1)
        self.assertIsInstance(recent, list)
        # Should have some records (depending on mock data time)


class TestWSPRDataStructure(unittest.TestCase):
    """Test WSPR data structure consistency."""

    def test_qso_required_fields(self):
        """Each QSO record should have required fields."""
        data = _mock_wspr_data()

        for qso in data:
            # Verify all expected fields exist
            self.assertTrue(isinstance(qso.get("call_sign"), str))
            self.assertTrue(isinstance(qso.get("frequency"), (int, float)))
            self.assertTrue(isinstance(qso.get("snr"), int))
            self.assertTrue(isinstance(qso.get("distance"), int))
            self.assertTrue(isinstance(qso.get("azimuth"), int))


if __name__ == "__main__":
    unittest.main()
