"""Tests voor modules/version.py (versienummer + update-controle)."""

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules import version as v

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class VersionTests(unittest.TestCase):

    def test_version_json_matches_code(self):
        with open(os.path.join(_ROOT, "version.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["version"], v.VERSION)

    def test_compare_versions(self):
        self.assertEqual(v.compare_versions("5.8.3", "5.8.3"), 0)
        self.assertEqual(v.compare_versions("5.9", "5.9.0"), 0)
        self.assertGreater(v.compare_versions("5.10.0", "5.9.9"), 0)
        self.assertLess(v.compare_versions("5.8.2", "5.8.3"), 0)

    def test_parse_published_version(self):
        self.assertEqual(v.parse_published_version('{"version": "5.9.0"}'), "5.9.0")
        self.assertEqual(v.parse_published_version('{"version": "v5.9"}'), "5.9")
        self.assertEqual(v.parse_published_version('{"version": "5.9-beta"}'), "")
        self.assertEqual(v.parse_published_version("<html>404</html>"), "")
        self.assertEqual(v.parse_published_version("[]"), "")

    def test_newer_version(self):
        self.assertEqual(v.newer_version("99.0.0"), "99.0.0")
        self.assertEqual(v.newer_version(v.VERSION), "")
        self.assertEqual(v.newer_version("0.1"), "")
        self.assertEqual(v.newer_version(""), "")

    def test_fetch_from_local_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "version.json")
            with open(p, "w", encoding="utf-8") as f:
                f.write('{"version": "6.0.0"}')
            with mock.patch.dict(os.environ, {"HAMIOS_UPDATE_URL": p}):
                self.assertEqual(v.fetch_published_version(), "6.0.0")

    def test_fetch_failure_is_silent(self):
        with mock.patch.dict(os.environ, {"HAMIOS_UPDATE_URL": "http://127.0.0.1:9/version.json"}):
            self.assertEqual(v.fetch_published_version(timeout=1), "")

    def test_check_can_be_disabled(self):
        with mock.patch.dict(os.environ, {"HAMIOS_UPDATE_CHECK": "0"}):
            self.assertFalse(v.update_check_enabled())


if __name__ == "__main__":
    unittest.main()
