"""Regressietests voor de fouten uit de codecontrole van november 2026."""

import csv
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication

_app = QApplication.instance() or QApplication([])

from modules import advisor as A                         # noqa: E402
from modules import history as H                         # noqa: E402
from modules.cat_interface import CatInterface           # noqa: E402
from modules.layers import _maidenhead_to_latlon         # noqa: E402
from modules.panels5 import _qth_to_continent            # noqa: E402
from modules.settings_dialog import latlon_to_locator, locator_to_latlon  # noqa: E402


class LocatorTests(unittest.TestCase):

    def test_six_char_is_subsquare_centre(self):
        lat, lon = locator_to_latlon("JO21DN")
        self.assertAlmostEqual(lat, 51.5625, places=3)   # 51° + 13/24 + 1/48
        self.assertAlmostEqual(lon, 4.2917, places=3)
        # Zelfde uitkomst als de kaartlaag (PSKReporter/WSPR)
        mlat, mlon = _maidenhead_to_latlon("JO21DN")
        self.assertAlmostEqual(lat, mlat, places=3)
        self.assertAlmostEqual(lon, mlon, places=3)

    def test_four_char_is_square_centre(self):
        self.assertEqual(locator_to_latlon("JO21"), (51.5, 5.0))

    def test_round_trip(self):
        for loc in ("JO21DN", "FN31PR", "QF56OD", "AA00AA", "RR99XX"):
            lat, lon = locator_to_latlon(loc)
            self.assertEqual(latlon_to_locator(lat, lon), loc)

    def test_invalid_and_edges(self):
        self.assertIsNone(locator_to_latlon("ZZ99"))
        self.assertIsNone(locator_to_latlon("J021"))
        self.assertEqual(latlon_to_locator(90, 180)[:2], "RR")


class HistoryTests(unittest.TestCase):

    def test_bz_column_and_migration(self):
        with tempfile.TemporaryDirectory() as d:
            old, new = os.path.join(d, "old.csv"), os.path.join(d, "config", "new.csv")
            with open(old, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(H._COLS)
                w.writerow(["2026-01-01T00:00:00+00:00"] + ["1"] * (len(H._COLS) - 1))
            saved = H._FILE, H._OLD_FILE
            H._FILE, H._OLD_FILE = new, old
            try:
                H.append({"20m": 77}, {"sfi": 120, "sw_bz": -7.5})
                self.assertFalse(os.path.exists(old))          # opgeruimd
                with open(new, newline="", encoding="utf-8") as f:
                    data = list(csv.DictReader(f))
                self.assertEqual(len(data), 2)                  # oude regel + nieuwe
                self.assertEqual(data[-1]["20m"], "77")
                self.assertEqual(float(data[-1]["bz"]), -7.5)   # was altijd 0
            finally:
                H._FILE, H._OLD_FILE = saved


class CatTests(unittest.TestCase):

    def test_icom_echo_is_skipped(self):
        echo = bytes([0xFE, 0xFE, 0x94, 0xE0, 0x03, 0xFD])
        reply = bytes([0xFE, 0xFE, 0xE0, 0x94, 0x03, 0x00, 0x50, 0x25, 0x14, 0x00, 0xFD])
        self.assertEqual(CatInterface._icom_parse_freq(echo + reply), 14_255_000)
        self.assertIsNone(CatInterface._icom_parse_freq(echo))

    def test_ft817_bcd(self):
        self.assertEqual(CatInterface._bcd_10hz(14_250_000), [0x01, 0x42, 0x50, 0x00])
        self.assertEqual(CatInterface._ft817_parse_freq(bytes([0x01, 0x42, 0x50, 0x00, 0x01])),
                         14_250_000)
        self.assertEqual(CatInterface._ft817_parse_freq(bytes([0xFF, 0, 0, 0])), 0)

    def test_protocol_per_radio_type(self):
        class Cfg:
            cat_radio_type = ""
        cat = CatInterface(Cfg())
        for rtype, kind in (("Yaesu (FT-950/2000/DX/3000/5000)", "yaesu8"),
                            ("Yaesu (FT-991/710/DX10/DX101)", "yaesu9"),
                            ("Yaesu (FT-817/857/897)", "ft817"),
                            ("Kenwood / Elecraft", "kenwood"),
                            ("Icom CI-V", "icom")):
            Cfg.cat_radio_type = rtype
            self.assertEqual(cat._kind(), kind)
            self.assertIn(rtype, CatInterface.RADIO_TYPES)


class AdvisorModeTests(unittest.TestCase):

    def test_am_uses_phone_segment(self):
        mode = A._mode_for("AM", 80, "20m")
        self.assertEqual(mode, "AM")
        self.assertEqual(A._freq_for(mode, "20m"), A.FREQ_KHZ["SSB"]["20m"])

    def test_fm_only_on_10m_and_6m(self):
        self.assertEqual(A._mode_for("FM", 80, "10m"), "FM")
        self.assertEqual(A._freq_for("FM", "10m"), 29600)
        self.assertEqual(A._mode_for("FM", 80, "20m"), "SSB")


class ContinentTests(unittest.TestCase):

    def test_regions(self):
        for (lat, lon), cont in (((51.6, 4.25), "EU"), ((55.7, 37.6), "EU"),
                                 ((14.7, -17.4), "AF"), ((31.8, 35.2), "AS"),
                                 ((-33.9, 151.2), "OC"), ((10.5, -66.9), "SA"),
                                 ((19.4, -99.1), "NA")):
            self.assertEqual(_qth_to_continent(lat, lon), cont, (lat, lon))


if __name__ == "__main__":
    unittest.main()
