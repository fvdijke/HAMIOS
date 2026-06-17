"""HAMIOS I/O utilities - consolidated file and JSON operations."""

import json
import os


def safe_json_load(filepath: str, default=None):
    """Safely load JSON from file with default fallback.

    Args:
        filepath: Path to JSON file
        default: Value to return if file doesn't exist or load fails

    Returns:
        Loaded JSON data or default value
    """
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default if default is not None else {}


def safe_json_save(filepath: str, data: dict) -> bool:
    """Safely save data to JSON file.

    Args:
        filepath: Path to JSON file
        data: Data to save

    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def safe_file_read(filepath: str, default: str = "") -> str:
    """Safely read file content with default fallback.

    Args:
        filepath: Path to file
        default: Value to return if read fails

    Returns:
        File content or default value
    """
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
    except Exception:
        pass
    return default


def safe_file_write(filepath: str, content: str) -> bool:
    """Safely write content to file.

    Args:
        filepath: Path to file
        content: Content to write

    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception:
        return False
