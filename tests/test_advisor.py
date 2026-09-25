"""
Unit tests for the propagation advisor (modules/advisor.py). Offline, fixed inputs.
"""

import datetime as dt
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules import advisor as A
from modules import propagation as P

UTC = dt.timezone.utc
QTH = (52.0, 5.0)
NOW = dt.datetime(2026, 9, 24, 15, 0, tzinfo=UTC)     # middag in Europa
CALM = {"sfi": "121", "ssn": "124", "k_index": "2", "sw_bz": "-1", "sw_speed_jump": 0,
        "noaa_R": 0, "noaa_S": 0, "noaa_G": 0, "noaa_G_tomorrow": 0}


def _engine(ssn=124, k=2, ionosondes=()):
    e = P.PropagationEngine()
    e.sfi, e.ssn, e.k = 121.0, float(ssn), float(k)
    e._ionosondes = list(ionosondes)
    return e


def _wspr(grid, band, km):
    return {"grid": grid, "band": band, "distance": km, "direction": "out"}


def _dx(dx_lat, dx_lon, freq, de=(51.5, 0.0)):
    return (dx_lat, dx_lon, "K1ABC", freq, de[0], de[1], "G4XYZ")


class TestClassification(unittest.TestCase):

    def test_band_of(self):
        self.assertEqual(A.band_of(14074), "20m")
        self.assertEqual(A.band_of(50313), "6m")
        self.assertIsNone(A.band_of(144300))

    def test_region_of(self):
        self.assertEqual(A.region_of((51.0, 4.0), QTH), "local")
        self.assertEqual(A.region_of((42.0, -71.0), QTH), "NA-E")
        self.assertEqual(A.region_of((-33.9, 151.2), QTH), "VK")


class TestObservations(unittest.TestCase):

    def test_counts_per_region_and_band(self):
        wspr = [_wspr("FN42", "20m", 5500)] * 3 + [_wspr("QF56", "40m", 16600)]
        dx = [_dx(42.0, -71.0, 14074)] * 2 + [_dx(42.0, -71.0, 14074, de=(-30, 150))]  # laatste: niet onze regio
        obs = A.collect_observations(QTH, wspr=wspr, dx=dx)
        self.assertEqual(obs[("NA-E", "20m")], 5)
        self.assertEqual(obs[("VK", "40m")], 1)

    def test_short_skip_counted_for_es(self):
        dx = [_dx(40.4, -3.7, 28074, de=(52.3, 4.9))]          # PA → EA, ~1500 km op 10m
        obs = A.collect_observations(QTH, dx=dx)
        self.assertEqual(obs["_es"][0][0], "10m")


class TestAdvice(unittest.TestCase):

    def test_confirmed_recommendation(self):
        wspr = [_wspr("FN42", "20m", 5500)] * 12
        adv = A.build_advice(QTH, CALM, snr_db=25, cfg_mode="FT8", wspr=wspr,
                             engine=_engine(), now=NOW)
        na = [r for r in adv.recs if r.region == "NA-E"]
        self.assertTrue(na)
        self.assertEqual(na[0].confidence, "confirmed")
        self.assertEqual(na[0].freq_khz, A.FREQ_KHZ["FT8"][na[0].band])
        self.assertLessEqual(len(adv.recs), 5)

    def test_reality_beats_model(self):
        """Veel spots op een band die het model dicht acht → toch aanbevolen ('observed')."""
        eng = _engine(ssn=10)                                   # zwak model
        wspr = [_wspr("FN42", "10m", 5500)] * 10
        adv = A.build_advice(QTH, CALM, wspr=wspr, engine=eng, now=NOW)
        na = [r for r in adv.recs if r.region == "NA-E" and r.band == "10m"]
        self.assertTrue(na)
        self.assertEqual(na[0].confidence, "observed")
        self.assertGreaterEqual(na[0].eff, 60)             # balkje toont effectieve kans
        self.assertLess(na[0].pct, na[0].eff)              # model lager (wit streepje)

    def test_weak_path_prefers_digital_for_ssb_operator(self):
        eng = _engine(ssn=30)
        adv = A.build_advice(QTH, CALM, cfg_mode="SSB", engine=eng, now=NOW)
        for r in adv.recs:
            if r.pct < 60:
                self.assertEqual(r.mode, "FT8")

    def test_no_ssb_on_30m(self):
        self.assertEqual(A._mode_for("SSB", 100, "30m"), "FT8")
        self.assertEqual(A._mode_for("CW", 100, "30m"), "CW")
        self.assertEqual(A._mode_for("SSB", 100, "20m"), "SSB")

    def test_open_until_in_future(self):
        adv = A.build_advice(QTH, CALM, engine=_engine(), now=NOW)
        for r in adv.recs:
            if r.until is not None:
                self.assertGreater(r.until, NOW)

    def test_events_from_noaa_scales(self):
        solar = dict(CALM, noaa_R=2, noaa_S=1, noaa_G=1, sw_speed_jump=180,
                     sw_bz="-14", noaa_G_tomorrow=2)
        adv = A.build_advice(QTH, solar, engine=_engine(), now=NOW)
        keys = {e.key: e.level for e in adv.events}
        self.assertEqual(keys["adv.ev.radio_blackout"], "red")      # dag op QTH
        self.assertEqual(keys["adv.ev.radiation"], "amber")
        self.assertIn("adv.ev.geomag", keys)
        self.assertIn("adv.ev.shock", keys)
        self.assertIn("adv.ev.bz_south", keys)
        self.assertIn("adv.ev.g_tomorrow", keys)
        self.assertLessEqual(adv.level, 1)                          # rood → hooguit matig

    def test_k_threshold_from_settings(self):
        solar = dict(CALM, k_index="4")
        keys4 = {e.key for e in A.build_advice(QTH, solar, engine=_engine(), now=NOW, k_alert=4).events}
        keys_off = {e.key for e in A.build_advice(QTH, solar, engine=_engine(), now=NOW, k_alert=99).events}
        self.assertIn("adv.ev.geomag_unsettled", keys4)
        self.assertNotIn("adv.ev.geomag_unsettled", keys_off)
        storm = {e.key for e in A.build_advice(QTH, dict(CALM, k_index="5"), engine=_engine(),
                                               now=NOW, k_alert=99).events}
        self.assertIn("adv.ev.geomag", storm)          # G1 altijd, ongeacht drempel

    def test_blackout_at_night_is_mild(self):
        night = dt.datetime(2026, 9, 24, 23, 0, tzinfo=UTC)
        adv = A.build_advice(QTH, dict(CALM, noaa_R=1), engine=_engine(), now=night)
        self.assertIn("adv.ev.radio_blackout_night", {e.key for e in adv.events})

    def test_es_from_ionosonde(self):
        iono = P.Ionosonde("Dourbes", "DB049", 50.1, 4.6, 6.7, 21.0, 10.5, NOW)
        adv = A.build_advice(QTH, CALM, engine=_engine(ionosondes=[iono]), now=NOW)
        self.assertTrue(adv.es["active"])
        self.assertEqual(adv.es["bands"], ["6m", "10m"])

    def test_es_not_from_two_spots_with_low_foes(self):
        iono = P.Ionosonde("Dourbes", "DB049", 50.1, 4.6, 6.7, 21.0, 2.0, NOW)
        dx = [_dx(40.4, -3.7, 28074, de=(52.3, 4.9))] * 2
        adv = A.build_advice(QTH, CALM, dx=dx, engine=_engine(ionosondes=[iono]), now=NOW)
        self.assertFalse(adv.es["active"])

    def test_timeline_sorted_within_horizon(self):
        adv = A.build_advice(QTH, CALM, engine=_engine(), now=NOW)
        times = [it.time for it in adv.timeline]
        self.assertEqual(times, sorted(times))
        self.assertTrue(all(NOW < t <= NOW + dt.timedelta(hours=A.HORIZON_H) for t in times))
        self.assertIn("adv.tl.sunset", {it.key for it in adv.timeline})

    def test_trends_cover_all_bands(self):
        adv = A.build_advice(QTH, CALM, engine=_engine(), now=NOW)
        self.assertEqual(set(adv.trends), {b for b, _, _ in A.BAND_KHZ})


if __name__ == "__main__":
    unittest.main()
