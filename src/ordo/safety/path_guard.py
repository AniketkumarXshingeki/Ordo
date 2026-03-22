from pathlib import Path
import json


# Load settings.json
with open("config/settings.json", "r") as f:
    settings = json.load(f)

ALLOWED_ROOTS = [Path(p).resolve() for p in settings["ALLOWED_ROOTS"]]


# Load exclusions.json
with open("config/exclusions.json", "r") as f:
    exclusions = json.load(f)

EXCLUDED_DIR_NAMES = set(exclusions["EXCLUDED_DIR_NAMES"])


def is_excluded(path: Path) -> bool:
    """Check if path contains excluded directory name."""
    return any(part in EXCLUDED_DIR_NAMES for part in path.parts)


def is_safe_path(path: Path) -> bool:
    """
    Allow only paths inside ALLOWED_ROOTS and not excluded.
    """
    try:
        resolved = path.resolve()
    except Exception:
        return False

    if is_excluded(resolved):
        return False

    for root in ALLOWED_ROOTS:
        if root == resolved or root in resolved.parents:
            return True

    return False