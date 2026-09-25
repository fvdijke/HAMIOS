"""Tests: satellietovergangen, D-RAP-raster en propagatiekaart."""
import datetime as dt
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules import charts as C
from modules import propagation as P
from modules import sat_passes as S

# ISS-TLE (epoch 2026-09-24); vaste tijd zodat de test deterministisch is
ISS = ("1 25544U 98067A   26267.50000000  .00012000  00000-0  21000-3 0  9990",
       "2 25544  51.6400 120.0000 0004000  60.0000 300.0000 15.50000000400000")
T0 = dt.datetime(2026, 9, 24, 12, 0, tzinfo=dt.timezone.utc)


class TestSatPasses(unittest.TestCase):

    def test_look_angles_overhead_and_horizon(self):
        r = S.R_EARTH + 400
        self.assertAlmostEqual(S.look_angles((r, 0, 0), 0, 0)[1], 90, places=3)
        # 20° verderop op 400 km hoogte: onder de horizon (horizonstraal ~20°)
        az, el, _ = S.look_angles((0, r, 0), 0, 70)
        self.assertLess(el, 0)
        self.assertAlmostEqual(az, 90, delta=0.5)      # oostelijk

    def test_subpoint_iss_altitude_and_inclination(self):
        for h in range(0, 24, 3):
            lat, lon, alt = S.subpoint(*ISS, T0 + dt.timedelta(hours=h))
            self.assertTrue(380 < alt < 460, alt)
            self.assertLessEqual(abs(lat), 51.7)

    def test_iss_passes_plausible(self):
        passes = S.predict_passes({"ISS": ISS}, 52.0, 5.0, T0, hours=24)
        self.assertTrue(3 <= len(passes) <= 8, len(passes))
        for p in passes:
            self.assertLess(p.aos, p.tca)
            self.assertLess(p.tca, p.los)
            self.assertLess(p.duration_s, 12 * 60)
            self.assertTrue(0 <= p.max_el <= 90)
            # op de randen van de overkomst staat hij (net) op de horizon
            self.assertAlmostEqual(S._elev(*ISS, 52.0, 5.0, p.aos), 0, delta=0.3)
        self.assertEqual(passes, sorted(passes, key=lambda p: p.aos))

    def test_geostationary_skipped(self):
        geo = ("1 99999U 20001A   26267.50000000  .00000000  00000-0  00000-0 0  9990",
               "2 99999   0.0100  90.0000 0001000   0.0000   0.0000  1.00270000 10000")
        self.assertEqual(S.predict_passes({"GEO": geo}, 52, 5, T0, hours=2), [])

    def test_compass(self):
        from modules import i18n
        i18n.set_language("en")
        self.assertEqual([S.compass(a) for a in (0, 44, 90, 180, 315, 359)],
                         ["N", "NE", "E", "S", "NW", "N"])


class TestMapLayers(unittest.TestCase):

    def test_drap_grid_orientation(self):
        drap = {"lats": [89, 0, -89], "lons": [-178, 0, 178],
                "grid": [[0, 0, 35], [0, 7, 0], [0, 0, 0]]}
        grid, w, h = C.drap_grid(drap)
        self.assertEqual((w, h), (3, 3))
        # na het vervagen blijft het maximum in de noordoostcel (35 MHz)
        self.assertEqual(grid.index(max(grid)), 0 * 3 + 2)
        self.assertGreater(sum(grid[0:3]), sum(grid[6:9]))   # noord > zuid
        self.assertEqual(C.drap_colour(0.2)[3], 0)    # geen absorptie → doorzichtig

    def test_band_map_shape_and_values(self):
        e = P.PropagationEngine()
        grid, w, h = e.band_map(52, 5, "40m", T0, step=10)
        self.assertEqual((w, h, len(grid)), (36, 18, 36 * 18))
        self.assertTrue(all(0 <= v <= 255 for v in grid))
        self.assertGreater(max(grid), 0)
        self.assertEqual(C.propmap_colour(5)[3], 0)   # vrijwel dicht → geen kleur


if __name__ == "__main__":
    unittest.main()
