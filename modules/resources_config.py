"""HAMIOS v5.8 - Online Resource Configuration

Central definition of all monitored resources with customizable URLs.
Used by splash screen, resource monitor, and settings resource tab.
"""

import json
import os
import datetime
from ._appdir import APP_DIR as _HERE

_RESOURCES_FILE = os.path.join(_HERE, "config", "hamios_resources.json")
_DEFAULTS_FILE = os.path.join(_HERE, "config", "hamios_resources_defaults.json")


def get_eibi_url() -> str:
    """Get current EIBI schedule URL based on season (A=summer/B=winter) and year."""
    now = datetime.datetime.now()
    season = "a" if 4 <= now.month <= 9 else "b"
    year = str(now.year)[2:]
    return f"http://www.eibispace.de/dx/sked-{season}{year}.csv"

# Default resources matching splash screen checks
# Uses "web_" prefix keys to match HAMIOS5.py splash screen resource keys
DEFAULT_RESOURCES = {
    # Solar & Ionosphere
    "web_noaa_swpc": {
        "name": "NOAA SWPC",
        "category": "Solar & Ionosphere",
        "url": "https://services.swpc.noaa.gov/products/summary/solar-wind-speed.json",
        "description": "Solar wind speed, magnetic field, Kp index",
        "method": "GET",
    },
    "web_hamqsl": {
        "name": "HamQSL",
        "category": "Solar & Ionosphere",
        "url": "https://www.hamqsl.com/solarxml.php",
        "description": "Solar flux index and parameters",
        "method": "GET",
    },
    # Satellites — TLE-bronnen (zie tle_sources.py). Niet in de opstartcontrole:
    # TLE wordt alleen handmatig (↻) en rate-limited opgehaald.
    "web_satnogs": {
        "name": "SatNOGS DB",
        "category": "Satellites",
        "url": "https://db.satnogs.org/",
        "description": "TLE data: ISS, weather satellites, CubeSats",
        "method": "HEAD",
    },
    "web_amsat": {
        "name": "AMSAT",
        "category": "Satellites",
        "url": "https://www.amsat.org/",
        "description": "TLE data: active amateur satellites",
        "method": "HEAD",
    },
    # Weak Signal Propagation
    "web_wsprnet": {
        # Sleutel ongewijzigd (opstartscherm); data komt sinds v5.7 van wspr.live
        "name": "wspr.live",
        "category": "Weak Signal Propagation",
        "url": "https://db1.wspr.live/?query=SELECT%201",
        "description": "WSPR spots (database of all WSPRnet spots)",
        "method": "GET",
    },
    # DX Spotting
    "web_dxwatch": {
        "name": "DXWatch",
        "category": "DX Spotting",
        "url": "https://dxwatch.com/dxsd1/s.php?s=0&r=100&cdxc=0",
        "description": "Real-time DX cluster spots",
        "method": "GET",
    },
    "web_pskreporter": {
        "name": "PSK Reporter",
        "category": "DX Spotting",
        "url": "https://pskreporter.info/cgi-bin/pskquery5.pl?encap=0&callback=_",
        "description": "Digital mode propagation reports",
        "method": "GET",
    },
    # Lightning
    "web_blitzortung": {
        "name": "Blitzortung",
        "category": "Lightning",
        "url": "https://www.blitzortung.org/",
        "description": "Real-time worldwide lightning detection",
        "method": "HEAD",
    },
    # Broadcast Schedules
    "web_eibi": {
        "name": "EIBI Space",
        "category": "Broadcast Schedules",
        "url": get_eibi_url(),
        "description": "Shortwave broadcast schedules (seasonal schedule)",
        "method": "GET",
    },
    # Map Data
    "web_wikimedia": {
        "name": "Wikimedia",
        "category": "Map Data",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Whole_world_-_land_and_oceans_12000.jpg/1920px-Whole_world_-_land_and_oceans_12000.jpg",
        "description": "NASA Blue Marble world map",
        "method": "GET",
    },
}


class ResourceConfig:
    """Manage custom resource URLs."""

    @staticmethod
    def save_defaults():
        """Save current DEFAULT_RESOURCES to defaults file."""
        try:
            with open(_DEFAULTS_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_RESOURCES, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save defaults: {e}")

    @staticmethod
    def load_resources() -> dict:
        """Laad custom resource URLs of gebruik defaults."""
        try:
            if os.path.exists(_RESOURCES_FILE):
                with open(_RESOURCES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return DEFAULT_RESOURCES.copy()

    @staticmethod
    def save_resources(resources: dict):
        """Sla custom resource URLs op."""
        try:
            with open(_RESOURCES_FILE, "w", encoding="utf-8") as f:
                json.dump(resources, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save resources: {e}")

    @staticmethod
    def get_resource(key: str) -> dict:
        """Haal specifieke resource op."""
        resources = ResourceConfig.load_resources()
        return resources.get(key, {})

    @staticmethod
    def update_resource(key: str, url: str) -> bool:
        """Update resource URL."""
        resources = ResourceConfig.load_resources()
        if key not in resources:
            return False
        resources[key]["url"] = url
        ResourceConfig.save_resources(resources)
        return True

    @staticmethod
    def reset_to_defaults() -> bool:
        """Reset alle resources naar defaults."""
        ResourceConfig.save_resources(DEFAULT_RESOURCES.copy())
        return True

    @staticmethod
    def get_categories() -> list:
        """Geef lijst van unieke categorieën."""
        resources = ResourceConfig.load_resources()
        categories = sorted(set(r.get("category", "") for r in resources.values()))
        return categories
