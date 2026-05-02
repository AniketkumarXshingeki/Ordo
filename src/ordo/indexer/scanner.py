import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional
from ordo.safety.path_guard import is_safe_path


# Allowed extensions (centralized)
ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".txt", ".md", ".rtf",                           # document
    ".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif",                 # image
    ".mp3", ".wav", ".flac", ".m4a", ".aac",                          # audio
    ".mp4", ".mkv", ".avi", ".mov", ".wmv",                           # video
    ".ppt", ".pptx", ".xls", ".xlsx", ".csv", ".json", ".xml",      # data/presentation
    ".py", ".js", ".html", ".css", ".ts", ".cpp", ".c", ".java",  # code
    ".zip", ".rar", ".7z", ".tar", ".gz"                              # archives
}


def _allowed_file(entry_name: str) -> bool:
    return entry_name.lower().endswith(tuple(ALLOWED_EXTENSIONS))


def _scan_directory(directory: Path, allow_outside: bool, max_depth: Optional[int], depth: int):
    results = []

    try:
        for entry in os.scandir(directory):
            try:
                if entry.is_file(follow_symlinks=False):
                    if _allowed_file(entry.name):
                        path = Path(entry.path)
                        if allow_outside or is_safe_path(path):
                            results.append(path)

                elif entry.is_dir(follow_symlinks=False):
                    if max_depth is None or depth < max_depth:
                        results.extend(_scan_directory(Path(entry.path), allow_outside, max_depth, depth + 1))
            except PermissionError:
                continue
            except Exception:
                continue
    except PermissionError:
        return results
    except Exception:
        return results

    return results


def scan_files(root, allow_outside: bool = False, max_depth: Optional[int] = None, max_workers: Optional[int] = None):
    """
    Recursively yield files with allowed extensions.

    Uses `os.scandir` for lower overhead and parallelizes top-level directory scanning.
    """
    root = Path(root).resolve()
    if not root.exists():
        return

    if root.is_file():
        if allow_outside or is_safe_path(root):
            if _allowed_file(root.name):
                yield root
        return

    if max_workers is None:
        max_workers = min(32, (os.cpu_count() or 4) + 2)

    direct_files = []
    directories = []

    try:
        for entry in os.scandir(root):
            try:
                if entry.is_file(follow_symlinks=False):
                    if _allowed_file(entry.name):
                        path = Path(entry.path)
                        if allow_outside or is_safe_path(path):
                            direct_files.append(path)
                elif entry.is_dir(follow_symlinks=False):
                    directories.append(Path(entry.path))
            except PermissionError:
                continue
            except Exception:
                continue
    except PermissionError:
        return
    except Exception:
        return

    for path in direct_files:
        yield path

    if not directories:
        return

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(_scan_directory, directory, allow_outside, max_depth, 1)
                   for directory in directories]

        for future in as_completed(futures):
            for path in future.result():
                yield path