import os
from pathlib import Path
import json


# Anchor config path to the project root
BASE_DIR = Path(__file__).parent.parent.parent.parent
CONFIG_DIR = BASE_DIR / "config"

SETTINGS_PATH = CONFIG_DIR / "settings.json"
EXCLUSIONS_PATH = CONFIG_DIR / "exclusions.json"

# Load settings.json
try:
    with open(SETTINGS_PATH, "r") as f:
        settings = json.load(f)
except Exception as e:
    print(f"Error loading settings: {e}")
    settings = {"ALLOWED_ROOTS": []}

ALLOWED_ROOTS = [Path(p).resolve() for p in settings.get("ALLOWED_ROOTS", [])]


# Load exclusions.json
try:
    with open(EXCLUSIONS_PATH, "r") as f:
        exclusions = json.load(f)
except Exception as e:
    print(f"Error loading exclusions: {e}")
    exclusions = {"EXCLUDED_DIR_NAMES": []}

EXCLUDED_DIR_NAMES = set(exclusions.get("EXCLUDED_DIR_NAMES", []))


def is_excluded(path: Path) -> bool:
    """Check if path contains excluded directory name."""
    # Use case-insensitive check for Windows
    parts = [p.lower() for p in path.parts]
    for excluded in EXCLUDED_DIR_NAMES:
        if excluded.lower() in parts:
            return True
    return False


def is_safe_path(path: Path) -> bool:
    """
    Allow only paths inside ALLOWED_ROOTS and not excluded.
    """
    try:
        # Resolve to handle symbolic links and normalization
        resolved = path.resolve()
    except Exception:
        # Fallback to absolute path if resolve fails (e.g., permission)
        resolved = path.absolute()

    if is_excluded(resolved):
        return False

    # On Windows, path comparison is usually case-insensitive, 
    # but we can make it more explicit.
    for root in ALLOWED_ROOTS:
        try:
            # Check if resolved path is under root
            if root == resolved or root in resolved.parents:
                return True
        except Exception:
            continue

    return False