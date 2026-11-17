"""Tests voor de functies van v5.9: cty.dat, Mijn signaal, padvoorspelling,
rigctld/flrig, watchlist, azimutale kaart + rotor, modelcontrole en Doppler."""

import datetime as dt
import os
import socket
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication

_app = QApplication.instance() or QApplication([])

from modules import cty                                   # noqa: E402

CTY_SAMPLE = """Netherlands:              14:  27:  EU:   52.28:    -5.47:    -1.0:  PA:
    PA,PB,PC,PD,PE,PF,PG,PH,PI;
Fed. Rep. of Germany:     14:  28:  EU:   51.00:   -10.00:    -1.0:  DL:
    DA,DB,DC,DD,DE,DF,DG,DH,DI,DJ,DK,DL,DM,DN,DO,DP,DQ,DR,=DL0XYZ(15)[29];
Bouvet:                   38:  67:  AF:  -54.42:    -3.38:    -1.0:  3Y/b:
    =3Y0J,=3Y0Z;
Australia:                30:  59:  OC:  -23.70:  -132.33:   -10.0:  VK:
    AX,VH,VI,VJ,VK,VL,VM,VN,VZ,VK6(29)[58]<-31.95/-115.85>;
"""


def _load_sample():
    text = CTY_SAMPLE + "".join(
        f"Dummy{i}: 1: 1: EU: 0: 0: 0: Q{i:03d}:\n    Q{i:03d};\n" for i in range(120))
    assert cty._DB.load_text(text)


class CtyTests(unittest.TestCase):

    def setUp(self):
        _load_sample()

    def test_prefix_and_longitude_sign(self):
        e = cty.lookup("PA3ABC")
        self.assertEqual((e.name, e.cont), ("Netherlands", "EU"))
        self.assertAlmostEqual(e.lon, 5.47)                 # west-positief omgedraaid

    def test_overrides_and_exact(self):
        self.assertEqual(cty.lookup("VK6ABC").cq, 29)
        self.assertAlmostEqual(cty.lookup("VK6ABC").lon, 115.85)
        self.assertEqual(cty.lookup("DL0XYZ").cq, 15)
        self.assertEqual(cty.lookup("3Y0J").name, "Bouvet")

    def test_portable_calls(self):
        self.assertEqual(cty.lookup("PA/DL1ABC").name, "Netherlands")
        self.assertEqual(cty.lookup("DL1ABC/P").name, "Fed. Rep. of Germany")
        self.assertIsNone(cty.lookup("ZZ9ZZZ"))


class RigNetTests(unittest.TestCase):

    def test_address_parsing(self):
        from modules.rig_net import parse_address
        self.assertEqual(parse_address("", "rigctld"), ("127.0.0.1", 4532))
        self.assertEqual(parse_address("COM3", "flrig"), ("127.0.0.1", 12345))
        self.assertEqual(parse_address("pi.local:4600", "rigctld"), ("pi.local", 4600))
        self.assertEqual(parse_address("", "rotctld"), ("127.0.0.1", 4533))

    def test_rigctld_round_trip(self):
        """Nep-rigctld: f / F / M zoals Hamlib ze beantwoordt."""
        from modules.cat_interface import CatInterface
        srv = socket.socket()
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        port = srv.getsockname()[1]
        state = {"f": 7074000, "mode": ""}

        def serve():
            conn, _ = srv.accept()
            buf = b""
            with conn:
                while True:
                    data = conn.recv(256)
                    if not data:
                        return
                    buf += data
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        cmd = line.decode().strip()
                        if cmd == "f":
                            conn.sendall(f"{state['f']}\n".encode())
                        elif cmd.startswith("F "):
                            state["f"] = int(cmd[2:])
                            conn.sendall(b"RPRT 0\n")
                        elif cmd.startswith("M "):
                            state["mode"] = cmd.split()[1]
                            conn.sendall(b"RPRT 0\n")
                        elif cmd == "q":
                            return
                        else:
                            conn.sendall(b"RPRT -1\n")

        threading.Thread(target=serve, daemon=True).start()

        class Cfg:
            cat_radio_type = "Hamlib rigctld (TCP)"
            cat_port = f"127.0.0.1:{port}"

        cat = CatInterface(Cfg())
        try:
            ok, err = cat.connect()
            self.assertTrue(ok, err)
            cat._stop_polling()
            self.assertEqual(cat._read_freq_hz_raw(), 7074000)
            self.assertEqual(cat.set_freq_hz(14074000), (True, ""))
            self.assertEqual(state["f"], 14074000)
            self.assertEqual(cat.set_mode("PKT-U"), (True, ""))
            self.assertEqual(state["mode"], "PKTUSB")
        finally:
            cat.disconnect()
            srv.close()


class RotorTests(unittest.TestCase):

    def test_commands(self):
        from modules.rotor import gs232_command, rotctld_command, turn
        self.assertEqual(gs232_command(45.4), b"M045\r")
        self.assertEqual(gs232_command(360), b"M000\r")
        self.assertEqual(rotctld_command(271.25), b"P 271.2 0\n")

        class NoRotor:
            rotor_type = ""
        self.assertFalse(turn(NoRotor(), 90))


class WatchlistTests(unittest.TestCase):

    def setUp(self):
        _load_sample()

    def test_matching(self):
        from modules.watchlist import matches
        self.assertTrue(matches("3Y0J", "3Y0J"))
        self.assertTrue(matches("3Y0J/P", "3Y0J"))
        self.assertTrue(matches("VK9NS", "VK9"))
        self.assertTrue(matches("3Y0J", "bouvet"))           # landnaam via cty.dat
        self.assertTrue(matches("PA3ABC", "PA"))             # hoofdprefix
        self.assertFalse(matches("PA3ABC", "VK"))
        self.assertFalse(matches("PA3ABC", "Papua New"))     # geen valse landnaam

    def test_hits_carry_path_chance(self):
        from modules.watchlist import find_hits
        spots = [{"dx": "VK2XYZ", "band": "20m", "freq_khz": 14025.0, "time": "12:00",
                  "spotter": "PA1A", "comment": "CW"},
                 {"dx": "DL1ABC", "band": "40m", "freq_khz": 7010.0}]
        hits = find_hits(spots, ["VK"], (52.0, 5.0))
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["entity"], "Australia")
        self.assertIsInstance(hits[0]["pct"], int)


class PathForecastTests(unittest.TestCase):

    def test_forecast_shape_and_windows(self):
        from modules.path_forecast import BANDS, HOURS, best_windows, forecast
        hours, grid = forecast((52.0, 5.0), (40.7, -74.0))
        self.assertEqual(len(hours), HOURS)
        self.assertEqual(set(grid), set(BANDS))
        self.assertTrue(all(len(v) == HOURS for v in grid.values()))
        t0 = dt.datetime(2026, 1, 1, 0)
        fake_h = [t0 + dt.timedelta(hours=h) for h in range(4)]
        g = {b: [0, 0, 0, 0] for b in BANDS}
        g["20m"] = [10, 60, 80, 20]
        g["40m"] = [55, 0, 0, 0]
        w = best_windows(fake_h, g)
        self.assertEqual(w[0][0], "20m")
        self.assertEqual((w[0][1].hour, w[0][2].hour, w[0][3]), (1, 3, 80))

    def test_resolve_target(self):
        _load_sample()
        from modules.path_forecast import resolve_target
        lat, lon, _ = resolve_target("JO21DN")
        self.assertAlmostEqual(lat, 51.5625, places=3)
        self.assertEqual(resolve_target("VK2ABC")[2], "VK2ABC (Australia)")
        self.assertIsNone(resolve_target("???"))


class EndHopAbsorptionTests(unittest.TestCase):

    def test_low_bands_closed_when_qth_is_in_daylight(self):
        """Lang pad PA → VK om 12 UTC (PA: middag, VK: nacht): 160m/80m dicht,
        ook al liggen de controlepunten (¼ en ¾) deels in het donker."""
        from modules.propagation import PropagationEngine
        eng = PropagationEngine()
        t = dt.datetime(2026, 11, 14, 12, tzinfo=dt.timezone.utc)
        pct = eng.path_band_pct(52.0, 5.0, -33.9, 151.2, t)
        self.assertLess(pct["160m"], 10)
        self.assertLess(pct["80m"], 35)
        # 18 UTC: donker in Europa, zonsopkomst in VK — het klassieke 80m-venster
        dusk = eng.path_band_pct(52.0, 5.0, -33.9, 151.2,
                                 dt.datetime(2026, 11, 14, 18, tzinfo=dt.timezone.utc))
        self.assertGreater(dusk["80m"], 80)
        # 22 UTC: dag in VK — absorptie bij de ontvanger sluit 80m weer
        late = eng.path_band_pct(52.0, 5.0, -33.9, 151.2,
                                 dt.datetime(2026, 11, 14, 22, tzinfo=dt.timezone.utc))
        self.assertLess(late["80m"], 20)


class AzimuthalTests(unittest.TestCase):

    def test_projection_round_trip(self):
        from modules.azimuthal import project, unproject
        for lat, lon in ((40.7, -74.0), (-33.9, 151.2), (35.7, 139.7), (-54.4, 3.4)):
            x, y = project(52.0, 5.0, lat, lon)
            back = unproject(52.0, 5.0, x, y)
            self.assertAlmostEqual(back[0], lat, places=4)
            self.assertAlmostEqual(back[1], lon, places=4)
        x, y = project(52.0, 5.0, 80.0, 5.0)                   # recht naar het noorden
        self.assertAlmostEqual(x, 0.0, places=6)
        self.assertLess(y, 0)
        self.assertIsNone(unproject(52.0, 5.0, 0.9, 0.9))      # buiten de schijf

    def test_bearing(self):
        from modules.propagation import bearing_deg
        self.assertAlmostEqual(bearing_deg(0, 0, 10, 0), 0.0, places=6)
        self.assertAlmostEqual(bearing_deg(0, 0, 0, 10), 90.0, places=6)
        self.assertAlmostEqual(bearing_deg(52, 5, 40.7, -74), 291.1, delta=0.5)   # PA → NYC (~291°)


class VerifyTests(unittest.TestCase):

    def test_stats(self):
        from modules.verify import Verifier
        with tempfile.TemporaryDirectory() as d:
            v = Verifier(path=os.path.join(d, "v.json"))
            qth = (52.0, 5.0)
            now = dt.datetime.now(dt.timezone.utc)
            v.add(("a",), now, "20m", (40.7, -74.0), qth)
            v.add(("a",), now, "20m", (40.7, -74.0), qth)       # dubbel: telt niet
            v.add(("b",), now, "20m", (51.0, 4.0), qth)          # te dichtbij: telt niet
            v.add(("c",), now, "40m", (-33.9, 151.2), qth)
            st = v.stats(1)
            self.assertEqual(st["20m"]["n"], 1)
            self.assertEqual(st["40m"]["n"], 1)
            self.assertEqual(st["_total"]["n"], 2)
            v.save()
            self.assertEqual(Verifier(path=os.path.join(d, "v.json")).stats(1)["_total"]["n"], 2)


class DopplerTests(unittest.TestCase):

    ISS = ("1 25544U 98067A   26318.50000000  .00010000  00000-0  18000-3 0  9990",
           "2 25544  51.6400 120.0000 0005000  80.0000 280.0000 15.50000000400000")

    def test_math(self):
        from modules.doppler import downlink, norad_of, uplink
        self.assertEqual(norad_of(self.ISS[0]), 25544)
        f = 145_800_000
        self.assertGreater(downlink(f, -7.0), f)        # nadert: hoger ontvangen
        self.assertLess(downlink(f, 7.0), f)
        self.assertAlmostEqual(downlink(f, -7.0) - f, f * 7.0 / 299_792.458, places=3)
        self.assertLess(uplink(f, -7.0), f)             # nadert: lager zenden

    def test_range_rate_is_plausible(self):
        from modules.doppler import range_rate
        t = dt.datetime(2026, 11, 14, 12, tzinfo=dt.timezone.utc)
        rr, az, el = range_rate(*self.ISS, 52.0, 5.0, t)
        self.assertLess(abs(rr), 8.0)                   # LEO: max ~7,5 km/s
        self.assertTrue(0 <= az < 360 and -90 <= el <= 90)


class MySignalTests(unittest.TestCase):

    def test_summary_and_clean_call(self):
        from modules.my_signal import _clean_call, summarize
        self.assertEqual(_clean_call("pa3abc'; drop"), "PA3ABCDROP")
        reps = [{"band": "20m", "rx": "K1A", "km": 5800, "snr": -12},
                {"band": "20m", "rx": "K1A", "km": 5800, "snr": -8},
                {"band": "20m", "rx": "W2B", "km": 6100, "snr": None},
                {"band": "40m", "rx": "G3C", "km": 450, "snr": 3}]
        self.assertEqual(summarize(reps), [("40m", 1, 450, 3), ("20m", 2, 6100, -8)])


if __name__ == "__main__":
    unittest.main()
