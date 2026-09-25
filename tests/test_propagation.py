"""
Unit tests for the central propagation engine (modules/propagation.py). Offline.
"""

import unittest
import sys
import os
import datetime as dt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules import propagation as P

UTC = dt.timezone.utc
T_NOON = dt.datetime(2026, 9, 24, 11, 50, tzinfo=UTC)    # ~zonne-middag 52N 5E
T_NIGHT = dt.datetime(2026, 9, 24, 23, 50, tzinfo=UTC)


def _engine(sfi=121, ssn=124, k=2):
    e = P.PropagationEngine()
    e.sfi, e.ssn, e.k = float(sfi), float(ssn), float(k)
    return e


def _iono(fof2, mufd, t, lat=50.1, lon=4.6, name="Dourbes"):
    return P.Ionosonde(name=name, code="DB049", lat=lat, lon=lon, fof2=fof2,
                       mufd=mufd, foes=None, time=t)


class TestSunGeometry(unittest.TestCase):

    def test_day_and_night(self):
        self.assertTrue(P.is_day(52, 5, T_NOON))
        self.assertFalse(P.is_day(52, 5, T_NIGHT))

    def test_day_night_depends_on_qth_not_utc(self):
        """Same UTC moment: day in Europe, night in Japan."""
        self.assertTrue(P.is_day(52, 5, T_NOON))
        self.assertFalse(P.is_day(36, 138, T_NOON))

    def test_representative_time(self):
        noon = P.representative_time(52, 5, True, T_NOON)
        night = P.representative_time(52, 5, False, T_NOON)
        self.assertTrue(P.is_day(52, 5, noon))
        self.assertFalse(P.is_day(52, 5, night))
        self.assertLessEqual(abs((noon - T_NOON).total_seconds()), 12 * 3600)

    def test_sun_position_matches_almanac(self):
        """NOAA/Meeus-waarden (almanak, ±0,05°): declinatie, tijdvereffening en
        subsolaire lengte incl. tijdvereffening (grayline op de juiste plek)."""
        utc = dt.timezone.utc
        dec, lon, eot = P.sun_position(dt.datetime(2026, 6, 21, 12, 0, tzinfo=utc))
        self.assertAlmostEqual(dec, 23.44, delta=0.05)
        dec, lon, eot = P.sun_position(dt.datetime(2026, 11, 3, 12, 0, tzinfo=utc))
        self.assertAlmostEqual(eot, 16.4, delta=0.2)
        self.assertAlmostEqual(lon, -eot / 4, delta=0.01)   # zon ~4° oostelijker dan 12 UTC
        dec, lon, eot = P.sun_position(dt.datetime(2026, 3, 20, 14, 46, tzinfo=utc))
        self.assertAlmostEqual(dec, 0.0, delta=0.05)          # equinox 20-3-2026 14:46 UTC


class TestModel(unittest.TestCase):

    def test_muf_higher_by_day(self):
        e = _engine()
        self.assertGreater(e.conditions(52, 5, T_NOON, now=T_NOON).muf,
                           e.conditions(52, 5, T_NIGHT, now=T_NIGHT).muf)

    def test_more_sunspots_higher_muf(self):
        lo = _engine(ssn=20).conditions(52, 5, T_NOON, now=T_NOON).muf
        hi = _engine(ssn=180).conditions(52, 5, T_NOON, now=T_NOON).muf
        self.assertGreater(hi, lo)

    def test_storm_lowers_muf(self):
        calm = _engine(k=1).conditions(52, 5, T_NOON, now=T_NOON).muf
        storm = _engine(k=7).conditions(52, 5, T_NOON, now=T_NOON).muf
        self.assertGreater(calm, storm)

    def test_luf_below_muf(self):
        e = _engine()
        for h in range(24):
            t = T_NOON.replace(hour=h)
            c = e.conditions(52, 5, t, now=t)
            self.assertLess(c.luf, c.muf, f"hour {h}")

    def test_band_probability_shape(self):
        """MUF is a median: ~50 % at the MUF, ~90 % at 0.85×MUF, ~10 % at 1.15×MUF."""
        self.assertAlmostEqual(P.band_probability(20.0, 20.0, 2.0), 0.5, delta=0.02)
        self.assertGreater(P.band_probability(17.0, 20.0, 2.0), 0.85)
        self.assertLess(P.band_probability(23.0, 20.0, 2.0), 0.15)
        self.assertLess(P.band_probability(1.8, 20.0, 6.0), 0.05)   # onder LUF

    def test_weak_signal_mode_helps_low_bands_only_a_little(self):
        """D-layer absorption ∝ 1/f²: FT8 must not open 160 m at noon."""
        e = _engine()
        ft8 = e.conditions(52, 5, T_NOON, snr_db=25, now=T_NOON).band_pct
        self.assertLess(ft8["160m"], 20)


class TestCalibration(unittest.TestCase):

    def test_measured_muf_used_now(self):
        e = _engine()
        e.set_ionosondes([_iono(6.7, 21.2, T_NOON)])
        c = e.conditions(52, 5, T_NOON, now=T_NOON)
        self.assertEqual(c.source, "Dourbes")
        self.assertAlmostEqual(c.muf, 21.2, delta=2.5)   # QTH ~250 km from Dourbes

    def test_calibration_fades_with_time(self):
        e = _engine()
        e.set_ionosondes([_iono(6.7, 21.2, T_NOON)])
        now_w = e.conditions(52, 5, T_NOON, now=T_NOON).cal_weight
        later_w = e.conditions(52, 5, T_NOON + dt.timedelta(hours=16), now=T_NOON).cal_weight
        self.assertGreater(now_w, 0.95)
        self.assertLess(later_w, 0.3)

    def test_stale_or_far_ionosonde_ignored(self):
        e = _engine()
        e.set_ionosondes([
            _iono(6.7, 21.2, T_NOON - dt.timedelta(hours=3)),                 # te oud
            _iono(9.0, 30.0, T_NOON, lat=-33.0, lon=18.0, name="Far away"),  # te ver
        ])
        c = e.conditions(52, 5, T_NOON, now=T_NOON)
        self.assertEqual(c.source, "model")
        self.assertIsNone(c.measured)

    def test_parse_kc2g_filters_low_confidence(self):
        row = {"station": {"name": "X", "code": "X1", "latitude": "50", "longitude": "355"},
               "fof2": 6.0, "mufd": 20.0, "foes": 3.1, "time": "2026-09-24T11:40:00", "cs": 100}
        bad = dict(row, cs=20)
        manual = dict(row, cs=-1)
        st = P.parse_kc2g([row, bad, manual])
        self.assertEqual(len(st), 2)
        self.assertAlmostEqual(st[0].lon, -5.0)          # 0–360 → −180–180
        self.assertEqual(st[0].foes, 3.1)


class TestDXRoutes(unittest.TestCase):

    def test_routes_exclude_own_continent_and_list_high_bands_first(self):
        e = _engine()
        routes = e.dx_routes(52, 5, t=T_NOON.replace(hour=14))
        names = [r[0] for r in routes]
        self.assertNotIn("EU", names)
        freq = dict(P.BANDS)
        for _, _, bands in routes:
            fs = [freq[b] for b, _ in bands]
            self.assertEqual(fs, sorted(fs, reverse=True))

    def test_routes_depend_on_qth(self):
        e = _engine()
        t = T_NOON.replace(hour=14)
        eu = {r[0] for r in e.dx_routes(52, 5, t=t)}
        ja = {r[0] for r in e.dx_routes(36, 138, t=t)}
        self.assertNotEqual(eu, ja)

    def test_gc_point_midpoint(self):
        lat, lon = P.gc_point(0, 0, 0, 90, 0.5)
        self.assertAlmostEqual(lat, 0, places=5)
        self.assertAlmostEqual(lon, 45, places=5)


if __name__ == "__main__":
    unittest.main()
