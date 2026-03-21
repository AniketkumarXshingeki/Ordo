from pathlib import Path
from indexer.file_types import classify_file_type


def extract_basic_metadata(path: Path) -> dict:
    try:
        stat = path.stat()
    except Exception:
        return {}

    return {
        "name": path.name,
        "path": str(path),
        "extension": path.suffix.lower(),
        "size_bytes": stat.st_size,
        "created_time": stat.st_ctime,
        "modified_time": stat.st_mtime,
        "file_type": classify_file_type(path.suffix),
    }
