from pathlib import Path
from safety.path_guard import is_safe_path


def scan_files(root: Path):
    """
    Recursively yield safe files from a root directory.
    """
    if not root.exists():
        return

    for path in root.rglob("*"):
        if path.is_file() and is_safe_path(path):
            yield path
