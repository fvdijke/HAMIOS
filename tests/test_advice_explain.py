"""
Tests for the advice explanations (modules/advice_explain.py): every text key used
exists in both languages, and the per-band explanation reflects the numbers.
"""

import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules import advice_explain as X
from modules import advisor as A
from modules import i18n

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _used_keys() -> set:
    keys = set()
    for fn in ("advice_explain.py", "advice_panel.py", "advisor.py"):
        src = open(os.path.join(ROOT, "modules", fn), encoding="utf-8").read()
        keys |= set(re.findall(r'"((?:adv|region)\.[a-z0-9_.\-A-Z]+)"', src))
    # Gebeurtenissen hebben ook een '.why'-uitleg
    ev = {k for k in keys if k.startswith("adv.ev.")}
    keys |= {k + ".why" for k in ev}
    keys |= {f"adv.level.{i}" for i in range(4)}
    keys |= {f"region.{r[0]}" for r in A.P.DX_REGIONS}
    return {k for k in keys if not k.endswith(".")}


def _rec(**kw):
    base = dict(region="NA-E", band="15m", mode="FT8", freq_khz=21074, pct=94, eff=100,
                obs=26, confidence="confirmed", until=None, score=1.0, lat=40, lon=-76,
                dist_km=6063, band_mhz=21.0, path_muf=26.1, path_luf=3.1, hops=2,
                cp_day=(True, False), sources={"PSK": 26})
    base.update(kw)
    return A.Rec(**base)


class TestKeys(unittest.TestCase):

    def test_all_keys_translated_in_both_languages(self):
        missing = {}
        for lang in ("nl", "en"):
            table = i18n._S[lang]
            miss = sorted(k for k in _used_keys() if k not in table)
            if miss:
                missing[lang] = miss
        self.assertEqual(missing, {})


class TestRecExplanation(unittest.TestCase):

    def setUp(self):
        i18n.set_language("nl")

    def test_confirmed_well_below_muf(self):
        t = X.rec_tooltip(_rec(), "N-Amerika (oost)", "FT8 · 100W", 26, "22:00")
        self.assertIn("80%", t)                        # 21.0 / 26.1
        self.assertIn(i18n.tr("adv.x.muf.well_below"), t)
        self.assertIn(i18n.tr("adv.x.obs.confirms"), t)
        self.assertIn("22:00", t)
        self.assertIn("+26 dB", t)
        self.assertIn(i18n.tr("adv.x.cp.mixed"), t)

    def test_observed_beats_model(self):
        r = _rec(band="10m", band_mhz=28.0, path_muf=24.3, pct=10, confidence="observed",
                 obs=8, sources={"PSK": 8})
        t = X.rec_tooltip(r, "Zuid-Amerika", "FT8", 26, "")
        self.assertIn(i18n.tr("adv.x.muf.far_above"), t)
        self.assertIn(i18n.tr("adv.x.obs.beats_model"), t)
        self.assertIn(i18n.tr("adv.x.no_window"), t)

    def test_single_hop_wording(self):
        t = X.rec_tooltip(_rec(hops=1, dist_km=2500), "X", "", 0, "")
        self.assertIn("1 sprong", t)
        self.assertNotIn("sprongen", t.split("<br>")[1])

    def test_luf_levels(self):
        for mhz, luf, key in ((21.0, 3.0, "far"), (7.0, 5.0, "above"),
                              (7.0, 6.5, "near"), (3.5, 5.0, "below")):
            line = X._luf_line(_rec(band_mhz=mhz, path_luf=luf))
            self.assertIn(i18n.tr(f"adv.x.luf.{key}"), line)


class TestGuide(unittest.TestCase):

    def test_guide_both_languages(self):
        for lang in ("nl", "en"):
            i18n.set_language(lang)
            g = X.reading_guide()
            self.assertNotIn("adv.guide", g)           # geen kale sleutels
        i18n.set_language("nl")


if __name__ == "__main__":
    unittest.main()
