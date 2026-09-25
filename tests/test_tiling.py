"""
Unit tests for the tile layout (modules/tiling.py): pixel-layout migration,
tree pruning/validation and the TileArea round trip. Offscreen, no config I/O.
"""

import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication

from modules.tiling import (TileArea, layout_from_rects, prune_tree, valid_tree,
                            _leaves, insert_panel, remove_panel, swap_panels)
from modules.layout_presets import preset_tree, PRESETS
from modules.panel import FloatingPanel

_app = QApplication.instance() or QApplication([])

# Realistic 15-panel layout (the user's hand-made one, with 'Bandcondities' and
# 'MUF-prognose' merged into 'Banden nu' / '24 uur vooruit') — guillotine-cuttable
RECTS = {
    "band_rel": (0, 0, 380, 370), "band_sched": (0, 370, 380, 470),
    "storm_fc": (0, 840, 380, 220),
    "band_hist": (0, 1060, 380, 240), "worldmap": (380, 0, 1520, 790),
    "dx_spots": (1900, 0, 620, 400), "alerts": (1900, 400, 620, 390),
    "prop_adv": (380, 790, 900, 270), "kp_48h": (380, 1060, 440, 240),
    "bz_24h": (820, 1060, 460, 240), "lightning": (1280, 790, 360, 120),
    "solar": (1280, 910, 360, 190), "solar_hist": (1280, 1100, 360, 200),
    "xray_24h": (1640, 790, 370, 510),
    "wspr_feed": (2010, 790, 510, 510),
}
ALL_VISIBLE = {p: True for p in RECTS}


def _positions(tree, x=0.0, y=0.0, w=2520.0, h=1300.0, out=None):
    out = {} if out is None else out
    if "p" in tree:
        out[tree["p"]] = (x, y, w, h)
        return out
    off = 0.0
    for c, s in zip(tree["c"], tree["s"]):
        if tree["o"] == "h":
            _positions(c, x + off, y, w * s, h, out); off += w * s
        else:
            _positions(c, x, y + off, w, h * s, out); off += h * s
    return out


class TestMigration(unittest.TestCase):

    def test_exact_reconstruction(self):
        tree = layout_from_rects(RECTS, ALL_VISIBLE)
        self.assertTrue(valid_tree(tree))
        pos = _positions(tree)
        for pid, (x, y, w, h) in RECTS.items():
            px, py, pw, ph = pos[pid]
            for a, b in ((x, px), (y, py), (w, pw), (h, ph)):
                self.assertAlmostEqual(a, b, delta=3, msg=pid)

    def test_hidden_panel_placed_near_overlap(self):
        rects = dict(RECTS)
        rects["extra"] = (400, 20, 300, 300)          # ligt op de kaart
        tree = layout_from_rects(rects, dict(ALL_VISIBLE, extra=False))
        self.assertIn("extra", _leaves(tree))
        # 'extra' en de kaart delen dezelfde splitsing
        def parent_of(node, pid):
            for c in node.get("c", []):
                if c.get("p") == pid:
                    return node
                r = parent_of(c, pid)
                if r:
                    return r
        self.assertIn({"p": "worldmap"}, parent_of(tree, "extra")["c"])

    def test_overlapping_layout_still_gives_tree(self):
        rects = {"a": (0, 0, 500, 500), "b": (100, 100, 500, 500), "c": (50, 600, 300, 100)}
        tree = layout_from_rects(rects, {k: True for k in rects})
        self.assertTrue(valid_tree(tree))
        self.assertEqual(sorted(_leaves(tree)), ["a", "b", "c"])


class TestTreeHelpers(unittest.TestCase):

    def test_prune_unknown_panels(self):
        tree = {"o": "h", "s": [0.5, 0.5], "c": [{"p": "a"},
                {"o": "v", "s": [0.5, 0.5], "c": [{"p": "gone"}, {"p": "b"}]}]}
        pruned = prune_tree(tree, {"a", "b"})
        self.assertEqual(sorted(_leaves(pruned)), ["a", "b"])
        self.assertEqual(pruned["c"][1], {"p": "b"})      # samengevallen splitsing

    def test_valid_tree_rejects_garbage(self):
        self.assertFalse(valid_tree({}))
        self.assertFalse(valid_tree({"o": "x", "s": [1], "c": [{"p": "a"}]}))
        self.assertFalse(valid_tree({"o": "h", "s": [1, 1], "c": [{"p": "a"}]}))
        self.assertTrue(valid_tree({"o": "v", "s": [1], "c": [{"p": "a"}]}))


class TestTileArea(unittest.TestCase):

    def setUp(self):
        self.panels = {p: FloatingPanel(p, panel_id=p) for p in ("a", "b", "c")}
        self.area = TileArea(self.panels)
        self.tree = {"o": "h", "s": [0.25, 0.75],
                     "c": [{"p": "a"}, {"o": "v", "s": [0.5, 0.5], "c": [{"p": "b"}, {"p": "c"}]}]}
        self.area.apply(self.tree, {"a": True, "b": True, "c": True})
        self.area.resize(1000, 600)
        self.area.show()
        _app.processEvents()

    def tearDown(self):
        self.area.close()

    def test_ratios_respected_despite_content_minimum(self):
        a = self.panels["a"]
        self.assertAlmostEqual(a.width() / 1000, 0.25, delta=0.02)

    def test_round_trip(self):
        again = self.area.tree()
        self.assertEqual(_leaves(again), ["a", "b", "c"])
        self.assertAlmostEqual(again["s"][0], 0.25, delta=0.01)

    def test_hidden_column_collapses_and_returns(self):
        w_before = self.panels["a"].width()
        self.panels["b"].hide_panel(); self.panels["c"].hide_panel(); _app.processEvents()
        self.assertGreater(self.panels["a"].width(), 900)          # kolom weg → a vult
        self.panels["b"].show_panel(); self.panels["c"].show_panel(); _app.processEvents()
        self.assertAlmostEqual(self.panels["a"].width(), w_before, delta=3)

    def test_panels_not_draggable_in_tile_mode(self):
        self.assertTrue(all(p._tiled for p in self.panels.values()))


TREE = {"o": "h", "s": [0.25, 0.75],
        "c": [{"p": "a"}, {"o": "v", "s": [0.5, 0.5], "c": [{"p": "b"}, {"p": "c"}]}]}


class TestTreeOps(unittest.TestCase):

    def test_center_makes_tab_group(self):
        t = insert_panel(remove_panel(TREE, "a"), "a", "b", "center")
        self.assertEqual(t["c"][0], {"t": ["b", "a"], "a": "a"})

    def test_edge_same_orientation_becomes_sibling(self):
        """Onder b in een verticale splitsing → broer, geen extra nesting."""
        t = insert_panel(remove_panel(TREE, "a"), "a", "b", "bottom")
        self.assertEqual([c.get("p") for c in t["c"]], ["b", "a", "c"])
        self.assertAlmostEqual(sum(t["s"]), 1.0, places=6)

    def test_edge_other_orientation_nests(self):
        t = insert_panel(TREE, "d", "c", "right")
        sub = t["c"][1]["c"][1]
        self.assertEqual(sub["o"], "h")
        self.assertEqual([x["p"] for x in sub["c"]], ["c", "d"])

    def test_swap(self):
        t = swap_panels(TREE, "a", "c")
        self.assertEqual(_leaves(t), ["c", "b", "a"])

    def test_remove_collapses(self):
        t = remove_panel(TREE, "b")
        self.assertEqual(_leaves(t), ["a", "c"])
        self.assertEqual(t["c"][1], {"p": "c"})

    def test_tab_group_of_one_becomes_panel(self):
        t = {"o": "h", "s": [0.5, 0.5], "c": [{"p": "a"}, {"t": ["b", "c"], "a": "c"}]}
        self.assertEqual(remove_panel(t, "c")["c"][1], {"p": "b"})

    def test_presets_contain_every_panel_once(self):
        for name in PRESETS:
            for w, h in ((2528, 1311), (1366, 700)):
                leaves = _leaves(preset_tree(name, w, h))
                self.assertEqual(sorted(leaves), sorted(RECTS), f"{name} {w}x{h}")
                self.assertTrue(valid_tree(preset_tree(name, w, h)))


if __name__ == "__main__":
    unittest.main()
