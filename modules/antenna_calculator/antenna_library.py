"""HAMIOS Antenna Calculator - Antenna Library Manager

Save, load, and manage antenna configurations.
"""

import json
import os
from typing import List, Optional
from pathlib import Path

from .antenna_models import SavedAntenna, AMATEUR_BANDS


class AntennaLibrary:
    """Manage saved antenna configurations."""

    def __init__(self, library_path: Optional[str] = None):
        """
        Initialize antenna library.

        Args:
            library_path: Path to antenna library directory.
                         If None, uses ~/.hamios/antenna_library/
        """
        if library_path is None:
            home = Path.home()
            library_path = home / ".hamios" / "antenna_library"
        else:
            library_path = Path(library_path)

        self.library_path = Path(library_path)
        self.library_path.mkdir(parents=True, exist_ok=True)

    def save_antenna(self, antenna: SavedAntenna) -> bool:
        """
        Save antenna configuration to file.

        Args:
            antenna: SavedAntenna object to save

        Returns:
            True if successful, False otherwise
        """
        try:
            # Sanitize filename
            filename = f"{antenna.name.replace(' ', '_')}.json"
            filepath = self.library_path / filename

            # Write JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(antenna.to_dict(), f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"Error saving antenna: {e}")
            return False

    def load_antenna(self, name: str) -> Optional[SavedAntenna]:
        """
        Load antenna configuration from file.

        Args:
            name: Antenna name (filename without .json)

        Returns:
            SavedAntenna object or None if not found
        """
        try:
            filename = f"{name.replace(' ', '_')}.json"
            filepath = self.library_path / filename

            if not filepath.exists():
                return None

            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return SavedAntenna.from_dict(data)
        except Exception as e:
            print(f"Error loading antenna: {e}")
            return None

    def delete_antenna(self, name: str) -> bool:
        """
        Delete antenna configuration from library.

        Args:
            name: Antenna name (filename without .json)

        Returns:
            True if successful, False otherwise
        """
        try:
            filename = f"{name.replace(' ', '_')}.json"
            filepath = self.library_path / filename

            if filepath.exists():
                filepath.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting antenna: {e}")
            return False

    def list_antennas(self) -> List[str]:
        """
        List all saved antenna names.

        Returns:
            List of antenna names
        """
        antennas = []
        try:
            for filepath in self.library_path.glob("*.json"):
                name = filepath.stem.replace("_", " ")
                antennas.append(name)
        except Exception as e:
            print(f"Error listing antennas: {e}")

        return sorted(antennas)

    def antenna_exists(self, name: str) -> bool:
        """Check if antenna exists in library."""
        filename = f"{name.replace(' ', '_')}.json"
        filepath = self.library_path / filename
        return filepath.exists()

    def duplicate_antenna(self, name: str, new_name: str) -> bool:
        """
        Duplicate an antenna configuration.

        Args:
            name: Original antenna name
            new_name: New antenna name

        Returns:
            True if successful, False otherwise
        """
        try:
            antenna = self.load_antenna(name)
            if antenna is None:
                return False

            # Create duplicate with new name
            antenna.name = new_name
            return self.save_antenna(antenna)
        except Exception as e:
            print(f"Error duplicating antenna: {e}")
            return False
