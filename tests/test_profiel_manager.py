"""Unit tests voor ProfielManager."""

import unittest
import os
import json
import tempfile
from unittest.mock import patch

# Dummy appdir voor testing
_TEST_DIR = tempfile.mkdtemp()


class TestProfielManager(unittest.TestCase):
    """Test profiel-laden/opslaan."""

    def setUp(self):
        """Voor elke test: schone test-directory."""
        self.test_file = os.path.join(_TEST_DIR, "test_profiles.json")
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def _write_test_profiles(self, profiles: dict):
        """Helper: schrijf test-profielen."""
        with open(self.test_file, "w") as f:
            json.dump(profiles, f)

    def test_empty_profiles_on_missing_file(self):
        """Ontbrekend profielbestand geeft lege dict."""
        with patch("hamios5.profiel_manager._PROFILES_FILE", self.test_file):
            from hamios5.profiel_manager import ProfileManager
            profiles = ProfileManager._load_profiles()
            self.assertEqual(profiles, {})

    def test_load_profiles(self):
        """Laad profielen uit bestand."""
        test_data = {
            "__default__": {
                "config": {"callsign": "EA1ABC"},
                "layout": {"__window__": [0, 0, 800, 600]},
                "timestamp": "2024-01-15T14:30:00"
            },
            "DX": {
                "config": {"callsign": "EA1DEF"},
                "layout": {"__window__": [0, 0, 1024, 768]},
                "timestamp": "2024-01-15T15:00:00"
            }
        }
        self._write_test_profiles(test_data)

        with patch("hamios5.profiel_manager._PROFILES_FILE", self.test_file):
            from hamios5.profiel_manager import ProfileManager
            profiles = ProfileManager.get_all_profiles()
            self.assertEqual(len(profiles), 2)
            self.assertIn("__default__", profiles)
            self.assertIn("DX", profiles)
            self.assertEqual(profiles["__default__"].config["callsign"], "EA1ABC")

    def test_save_new_profile(self):
        """Sla nieuw profiel op."""
        with patch("hamios5.profiel_manager._PROFILES_FILE", self.test_file):
            from hamios5.profiel_manager import ProfileManager

            config = {"callsign": "N0CALL", "mode": "SSB"}
            layout = {"__window__": [100, 100, 900, 700]}

            result = ProfileManager.save_profile("TestProfile", config, layout)
            self.assertTrue(result)

            # Verificatie
            profiles = ProfileManager.get_all_profiles()
            self.assertIn("TestProfile", profiles)
            self.assertEqual(profiles["TestProfile"].config["callsign"], "N0CALL")

    def test_cannot_save_reserved_names(self):
        """Kan niet opslaan met '__' voornaam."""
        with patch("hamios5.profiel_manager._PROFILES_FILE", self.test_file):
            from hamios5.profiel_manager import ProfileManager

            result = ProfileManager.save_profile("__forbidden__", {}, {})
            self.assertFalse(result)

    def test_update_profile(self):
        """Overschrijf bestaand profiel."""
        # Maak eerst profiel
        with patch("hamios5.profiel_manager._PROFILES_FILE", self.test_file):
            from hamios5.profiel_manager import ProfileManager

            ProfileManager.save_profile("Test", {"mode": "SSB"}, {})

            # Update
            result = ProfileManager.update_profile("Test", {"mode": "CW"}, {})
            self.assertTrue(result)

            # Verificatie
            profile = ProfileManager.get_profile("Test")
            self.assertEqual(profile.config["mode"], "CW")

    def test_delete_profile(self):
        """Verwijder profiel."""
        with patch("hamios5.profiel_manager._PROFILES_FILE", self.test_file):
            from hamios5.profiel_manager import ProfileManager

            ProfileManager.save_profile("ToDelete", {}, {})
            self.assertIn("ToDelete", ProfileManager.get_all_profiles())

            result = ProfileManager.delete_profile("ToDelete")
            self.assertTrue(result)
            self.assertNotIn("ToDelete", ProfileManager.get_all_profiles())

    def test_cannot_delete_reserved_names(self):
        """Kan niet '__default__' verwijderen."""
        with patch("hamios5.profiel_manager._PROFILES_FILE", self.test_file):
            from hamios5.profiel_manager import ProfileManager

            result = ProfileManager.delete_profile("__default__")
            self.assertFalse(result)

    def test_set_default_profile(self):
        """Stel default-profiel in."""
        with patch("hamios5.profiel_manager._PROFILES_FILE", self.test_file):
            from hamios5.profiel_manager import ProfileManager

            config = {"callsign": "DEFAULT"}
            layout = {"__window__": [0, 0, 1024, 768]}

            ProfileManager.set_default_profile(config, layout)

            profile = ProfileManager.get_default_profile()
            self.assertIsNotNone(profile)
            self.assertEqual(profile.config["callsign"], "DEFAULT")

    def test_get_default_profile(self):
        """Haal default-profiel op."""
        test_data = {
            "__default__": {
                "config": {"callsign": "EA1ABC"},
                "layout": {},
                "timestamp": "2024-01-15T14:30:00"
            }
        }
        self._write_test_profiles(test_data)

        with patch("hamios5.profiel_manager._PROFILES_FILE", self.test_file):
            from hamios5.profiel_manager import ProfileManager

            profile = ProfileManager.get_default_profile()
            self.assertIsNotNone(profile)
            self.assertEqual(profile.config["callsign"], "EA1ABC")

    def test_list_named_profiles(self):
        """Geef lijst van benoemde profielen (geen __default__)."""
        test_data = {
            "__default__": {"config": {}, "layout": {}, "timestamp": ""},
            "Profile1": {"config": {}, "layout": {}, "timestamp": ""},
            "Profile2": {"config": {}, "layout": {}, "timestamp": ""},
        }
        self._write_test_profiles(test_data)

        with patch("hamios5.profiel_manager._PROFILES_FILE", self.test_file):
            from hamios5.profiel_manager import ProfileManager

            named = ProfileManager.list_named_profiles()
            self.assertEqual(named, ["Profile1", "Profile2"])
            self.assertNotIn("__default__", named)

    def test_reset_to_default(self):
        """Haal default config + layout."""
        test_data = {
            "__default__": {
                "config": {"callsign": "EA1ABC", "mode": "SSB"},
                "layout": {"__window__": [100, 100, 800, 600]},
                "timestamp": ""
            }
        }
        self._write_test_profiles(test_data)

        with patch("hamios5.profiel_manager._PROFILES_FILE", self.test_file):
            from hamios5.profiel_manager import ProfileManager

            result = ProfileManager.reset_to_default()
            self.assertIsNotNone(result)
            config, layout = result
            self.assertEqual(config["callsign"], "EA1ABC")
            self.assertEqual(layout["__window__"], [100, 100, 800, 600])

    def test_has_profiles(self):
        """Check of er named profielen zijn."""
        with patch("hamios5.profiel_manager._PROFILES_FILE", self.test_file):
            from hamios5.profiel_manager import ProfileManager

            # Geen profielen
            self.assertFalse(ProfileManager.has_profiles())

            # Met default: nog steeds false
            ProfileManager.set_default_profile({}, {})
            self.assertFalse(ProfileManager.has_profiles())

            # Met named profiel: true
            ProfileManager.save_profile("MyProfile", {}, {})
            self.assertTrue(ProfileManager.has_profiles())


if __name__ == "__main__":
    unittest.main()
