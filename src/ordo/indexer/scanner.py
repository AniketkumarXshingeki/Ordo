from pathlib import Path
from ordo.safety.path_guard import is_safe_path


# Allowed extensions (centralized)
ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".txt", ".md", ".rtf",                           #document
    ".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif",                 #image
    ".mp3", ".wav", ".flac", ".m4a", ".aac",                          #audio
    ".mp4", ".mkv", ".avi", ".mov", ".wmv",                           #video
    ".ppt", ".pptx", ".xls", ".xlsx", ".csv", ".json", ".xml",        #data/presentation
    ".py", ".js", ".html", ".css", ".ts", ".cpp", ".c", ".java",      #code
    ".zip", ".rar", ".7z", ".tar", ".gz"                              #archives
}


def scan_files(root, allow_outside: bool = False):
    """
    Recursively yield files with allowed extensions.

    By default only yields files that pass `is_safe_path` (inside ALLOWED_ROOTS).
    If `allow_outside=True`, the safety check is skipped (useful for explicit
    user-provided paths).
    """
    root = Path(root).resolve()
    if not root.exists():
        return

    for path in root.rglob("*"):
        try:
            if not path.is_file():
                continue
            
            if not allow_outside:
                if not is_safe_path(path):
                    continue

            if path.suffix.lower() in ALLOWED_EXTENSIONS:
                yield path

        except Exception:
            continue  # skip inaccessible files