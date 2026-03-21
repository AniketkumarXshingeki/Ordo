from pathlib import Path
from config.settings import ALLOWED_ROOTS
from config.exclusions import EXCLUDED_DIR_NAMES


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
