from pathlib import Path
from ordo.safety.path_guard import is_safe_path


# Allowed extensions (centralized)
ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".txt", ".md",                                   #document
    ".jpg", ".jpeg", ".png", ".bmp", ".webp",                         #image
    ".mp3", ".wav", ".flac",                                          #audio
    ".mp4", ".mkv", ".avi", ".mov",                                   #video
    ".ppt", ".pptx"                                                   #presentation
}


def scan_files(root):
    """
    Recursively yield only safe files with allowed extensions.
    """
    root=Path(root)
    if not root.exists():
        return

    for path in root.rglob("*"):
        try:
            if (
                path.is_file()
                and is_safe_path(path)
                and path.suffix.lower() in ALLOWED_EXTENSIONS
            ):
                yield path

        except Exception:
            continue  # skip inaccessible files