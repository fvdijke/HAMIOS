"""
Unit tests for the WSPR feed (wspr.live). Offline: no network access.
"""

import unittest
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.wspr_feed import (WSPRFeed, build_query, parse_rows,
                               RADIUS_KM, MIN_DISTANCE_KM, BAND_NAMES)

# Rows in the exact shape wspr.live returns (FORMAT JSON → "data")
_ROW_OUT = {"time": "2026-09-24 15:50:00", "band": 14, "frequency": 14097090,
            "tx_sign": "PA0ABC", "tx_loc": "JO22", "rx_sign": "K1XYZ", "rx_loc": "FN42",
            "snr": -18, "drift": 0, "power": 23, "distance": 5480,
            "azimuth": 288, "rx_azimuth": 52, "tx_near": 1}
_ROW_IN = {"time": "2026-09-24 15:48:00", "band": 7, "frequency": 7040110,
           "tx_sign": "VK2AAA", "tx_loc": "QF56", "rx_sign": "PA0ABC", "rx_loc": "JO22",
           "snr": -27, "drift": -1, "power": 37, "distance": 16600,
           "azimuth": 330, "rx_azimuth": 75, "tx_near": 0}


class TestQuery(unittest.TestCase):

    def test_query_filters_region_and_distance(self):
        q = build_query(52.0, 5.0)
        self.assertIn("FROM wspr.rx", q)
        self.assertIn(f"< {RADIUS_KM * 1000}", q)
        self.assertIn(f"distance >= {MIN_DISTANCE_KM}", q)
        self.assertIn("5.0000, 52.0000", q)      # greatCircleDistance(lon, lat)
        self.assertIn("FORMAT JSON", q)


class TestParseRows(unittest.TestCase):

    def test_outgoing_spot(self):
        r = parse_rows([_ROW_OUT])[0]
        self.assertEqual(r["direction"], "out")
        self.assertEqual(r["call_sign"], "K1XYZ")     # remote end = receiver
        self.assertEqual(r["grid"], "FN42")
        self.assertEqual(r["azimuth"], 288)           # bearing from own region
        self.assertEqual(r["band"], "20m")
        self.assertAlmostEqual(r["frequency"], 14.09709)
        self.assertEqual(datetime.fromisoformat(r["time"]).tzinfo is not None, True)

    def test_incoming_spot(self):
        r = parse_rows([_ROW_IN])[0]
        self.assertEqual(r["direction"], "in")
        self.assertEqual(r["call_sign"], "VK2AAA")    # remote end = transmitter
        self.assertEqual(r["grid"], "QF56")
        self.assertEqual(r["azimuth"], 75)            # rx_azimuth: towards VK
        self.assertEqual(r["band"], "40m")

    def test_bad_rows_skipped(self):
        rows = [_ROW_OUT, {"time": "garbage"}, {}]
        self.assertEqual(len(parse_rows(rows)), 1)

    def test_required_fields_and_types(self):
        for r in parse_rows([_ROW_OUT, _ROW_IN]):
            for f in ("call_sign", "grid", "band", "frequency", "snr",
                      "distance", "azimuth", "time", "direction"):
                self.assertIn(f, r)
            self.assertIsInstance(r["snr"], int)
            self.assertIsInstance(r["distance"], int)
            self.assertIsInstance(r["frequency"], float)

    def test_band_names_cover_hf(self):
        for mhz, name in [(1, "160m"), (3, "80m"), (7, "40m"), (14, "20m"),
                          (21, "15m"), (28, "10m"), (50, "6m")]:
            self.assertEqual(BAND_NAMES[mhz], name)


class TestWSPRFeed(unittest.TestCase):

    def setUp(self):
        self.feed = WSPRFeed(qth_lat=52.0, qth_lon=5.0)

    def test_distance_calculation(self):
        dist = WSPRFeed.compute_distance(52.37, 4.89, 51.51, -0.13)   # AMS–LON
        self.assertGreater(dist, 300)
        self.assertLess(dist, 400)

    def test_distance_same_point(self):
        self.assertLess(WSPRFeed.compute_distance(52.0, 5.0, 52.0, 5.0), 1)

    def test_update_interval_minimum(self):
        """At most one request per WSPR cycle (2 min)."""
        self.feed.set_update_interval(10)
        self.assertEqual(self.feed._update_interval, 120)

    def test_no_mock_data_module(self):
        import modules.wspr_feed as wf
        self.assertFalse(hasattr(wf, "_mock_wspr_data"), "fake data must never be shown")

    def test_set_qth_wakes_fetch(self):
        self.feed.set_qth(40.0, -74.0)
        self.assertTrue(self.feed._wake.is_set())
        self.assertEqual((self.feed.qth_lat, self.feed.qth_lon), (40.0, -74.0))


if __name__ == "__main__":
    unittest.main()
