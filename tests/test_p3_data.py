"""
Tests for the P3 data sources: D-RAP absorption, 27-day outlook, OVATION aurora
raster and the meteor shower calendar. Offline, fixed NOAA-format samples.
"""

import datetime as dt
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules import charts as C
from modules import propagation as P
from modules import advisor as A

UTC = dt.timezone.utc
NOW = dt.datetime(2026, 9, 24, 12, 0, tzinfo=UTC)

DRAP = """# DRAP Tabular Values
# Product Valid At : 2026-09-24 12:00 UTC
#
# Estimated Recovery Time : 1 hour
#
#  X-RAY Message : M5 flare in progress
#
#  Proton Message : Normal Proton Background
#
# Frequency (MHz) as a function of Latitude and Longitude
#
        -2    2    6
------------------
  53 |  4.0 12.0  3.0
  51 |  2.0 11.0  1.0
 -89 |  0.0  0.0  0.0
"""

OUTLOOK = """:Product: 27-day Space Weather Outlook Table 27DO.txt
:Issued: 2026 Sep 21 0317 UTC
#   UTC      Radio Flux   Planetary   Largest
#  Date       10.7 cm      A Index    Kp Index
2026 Sep 21     105           5          2
2026 Sep 22     110          20          5
"""


class TestParsers(unittest.TestCase):

    def test_parse_drap(self):
        d = C.parse_drap(DRAP)
        self.assertEqual(d["lons"], [-2.0, 2.0, 6.0])
        self.assertEqual(d["lats"], [53.0, 51.0, -89.0])
        self.assertEqual(d["grid"][0][1], 12.0)
        self.assertEqual(d["valid"], NOW)
        self.assertEqual(d["xray_msg"], "M5 flare in progress")
        self.assertEqual(d["recovery"], "1 hour")

    def test_parse_drap_garbage(self):
        self.assertIsNone(C.parse_drap("nonsense\n1 | 2 3"))

    def test_parse_outlook(self):
        rows = C.parse_outlook(OUTLOOK)
        self.assertEqual(rows, [(dt.date(2026, 9, 21), 105, 5, 2),
                                (dt.date(2026, 9, 22), 110, 20, 5)])

    def test_ovation_rgba(self):
        data = {"coordinates": [[0, 90, 0], [180, 60, 80], [359, -90, 10]]}
        rgba = C.ovation_rgba(data)
        self.assertEqual(len(rgba), 360 * 181 * 4)
        # lon 180 → kolom 0 (−180°), lat 60 → rij 30; kans 80 → rood, zichtbaar
        i = (30 * 360 + 0) * 4
        self.assertEqual(rgba[i:i + 3], bytes((240, 80, 40)))
        self.assertGreater(rgba[i + 3], 0)
        # kans 0 → volledig doorzichtig
        self.assertEqual(rgba[(0 * 360 + 180) * 4 + 3], 0)

    def test_ovation_equator_seam_ignored(self):
        """OVATION heeft op 0° een naad met kans 4 % — mag niet als lijn verschijnen."""
        rgba = C.ovation_rgba({"coordinates": [[10, 0, 4], [10, 20, 30]]})
        self.assertEqual(rgba[(90 * 360 + 190) * 4 + 3], 0)
        self.assertEqual(rgba[(70 * 360 + 190) * 4 + 3], 0)


class TestAbsorptionInModel(unittest.TestCase):

    def _engine(self):
        e = P.PropagationEngine()
        e.sfi, e.ssn, e.k = 121.0, 124.0, 2.0
        e.set_drap(C.parse_drap(DRAP))
        return e

    def test_luf_raised_by_measured_absorption(self):
        e = self._engine()
        c = e.conditions(52.0, 2.0, NOW, now=NOW)       # cel 53/2 of 51/2 → 12 / 11 MHz
        self.assertGreaterEqual(c.luf, 11.0)
        self.assertGreaterEqual(c.absorption, 11.0)
        self.assertLess(c.band_pct["40m"], 10)            # 40m onder de absorptiegrens

    def test_absorption_expires(self):
        e = self._engine()
        later = NOW + dt.timedelta(hours=3)
        self.assertEqual(e.drap_haf(52.0, 2.0, later), 0.0)

    def test_advisor_event(self):
        e = self._engine()
        solar = {"sfi": "121", "ssn": "124", "k_index": "2"}
        adv = A.build_advice((52.0, 2.0), solar, engine=e, now=NOW)
        ev = [x for x in adv.events if x.key == "adv.ev.absorption"]
        self.assertTrue(ev)
        self.assertEqual(ev[0].level, "red")             # ≥ 10 MHz


class TestMeteorShowers(unittest.TestCase):

    def test_perseids_active_around_peak(self):
        self.assertEqual(A.active_meteor_shower(dt.date(2026, 8, 13))[0], "PER")
        self.assertIsNone(A.active_meteor_shower(dt.date(2026, 9, 24)))

    def test_quadrantids_across_new_year(self):
        # 2 januari valt in het venster van de piek op 3 januari
        self.assertEqual(A.active_meteor_shower(dt.date(2027, 1, 2))[0], "QUA")

    def test_highest_zhr_wins_when_overlapping(self):
        # 8 juni: Arietiden (ZHR 30) én zeta-Perseïden (ZHR 20) actief
        self.assertEqual(A.active_meteor_shower(dt.date(2026, 6, 8))[0], "ARI")


if __name__ == "__main__":
    unittest.main()
