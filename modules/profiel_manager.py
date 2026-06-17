"""HAMIOS v5.3 - Profiel-bewaarsysteem

Bewaart complete user "workspaces": alle instellingen + panel-layout + window-geometrie.
- Default profiel: automatische backup van huidade instellingen
- Named profielen: gebruiker-gemaakte workspaces
"""

import json
import os
from .datetime import datetime
from .dataclasses import dataclass, asdict
from .typing import Dict, Tuple, Optional

from ._appdir import APP_DIR as _HERE


_PROFILES_FILE = os.path.join(_HERE, "hamios_profiles.json")


@dataclass
class Profile:
    """Compleet profiel: config + layout."""
    name: str
    config: dict  # AppConfig als dict
    layout: dict  # Panel layouts + window geometry
    timestamp: str  # ISO format: 2024-01-15T14:30:00


class ProfileManager:
    """Beheer opgeslagen profielen."""

    @staticmethod
    def _load_profiles() -> dict:
        """Laad alle profielen uit hamios_profiles.json."""
        if not os.path.exists(_PROFILES_FILE):
            return {}
        try:
            with open(_PROFILES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def _save_profiles(profiles: dict):
        """Sla alle profielen op in hamios_profiles.json."""
        try:
            with open(_PROFILES_FILE, "w", encoding="utf-8") as f:
                json.dump(profiles, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Profiel opslaan mislukt: {e}")

    @staticmethod
    def get_all_profiles() -> Dict[str, Profile]:
        """Geef alle beschikbare profielen."""
        data = ProfileManager._load_profiles()
        profiles = {}
        for name, p in data.items():
            try:
                profiles[name] = Profile(
                    name=name,
                    config=p.get("config", {}),
                    layout=p.get("layout", {}),
                    timestamp=p.get("timestamp", "")
                )
            except (KeyError, TypeError):
                pass
        return profiles

    @staticmethod
    def get_profile(name: str) -> Optional[Profile]:
        """Haal specifiek profiel op."""
        data = ProfileManager._load_profiles()
        if name not in data:
            return None
        p = data[name]
        try:
            return Profile(
                name=name,
                config=p.get("config", {}),
                layout=p.get("layout", {}),
                timestamp=p.get("timestamp", "")
            )
        except (KeyError, TypeError):
            return None

    @staticmethod
    def save_profile(name: str, config: dict, layout: dict) -> bool:
        """Sla huidge instellingen op als profiel."""
        if name.startswith("__"):
            return False  # Voorbehouden namen

        profiles = ProfileManager._load_profiles()
        profiles[name] = {
            "config": config,
            "layout": layout,
            "timestamp": datetime.now().isoformat()
        }
        ProfileManager._save_profiles(profiles)
        return True

    @staticmethod
    def update_profile(name: str, config: dict, layout: dict) -> bool:
        """Overschrijf bestaand profiel."""
        if name.startswith("__"):
            return False

        profiles = ProfileManager._load_profiles()
        if name not in profiles:
            return False

        profiles[name] = {
            "config": config,
            "layout": layout,
            "timestamp": datetime.now().isoformat()
        }
        ProfileManager._save_profiles(profiles)
        return True

    @staticmethod
    def delete_profile(name: str) -> bool:
        """Verwijder profiel."""
        if name.startswith("__"):
            return False  # Kan default niet verwijderen

        profiles = ProfileManager._load_profiles()
        if name not in profiles:
            return False

        del profiles[name]
        ProfileManager._save_profiles(profiles)
        return True

    @staticmethod
    def set_default_profile(config: dict, layout: dict):
        """Stel huidge instellingen in als default-profiel."""
        profiles = ProfileManager._load_profiles()
        profiles["__default__"] = {
            "config": config,
            "layout": layout,
            "timestamp": datetime.now().isoformat()
        }
        ProfileManager._save_profiles(profiles)

    @staticmethod
    def get_default_profile() -> Optional[Profile]:
        """Haal default-profiel op."""
        return ProfileManager.get_profile("__default__")

    @staticmethod
    def reset_to_default() -> Optional[Tuple[dict, dict]]:
        """Haal default config + layout op voor herstellen."""
        profile = ProfileManager.get_default_profile()
        if profile:
            return (profile.config, profile.layout)
        return None

    @staticmethod
    def list_named_profiles() -> list:
        """Geef lijst van benoemde profielen (geen __default__)."""
        data = ProfileManager._load_profiles()
        return sorted([k for k in data.keys() if not k.startswith("__")])

    @staticmethod
    def has_profiles() -> bool:
        """Check of er profielen opgeslagen zijn."""
        return len(ProfileManager.list_named_profiles()) > 0
