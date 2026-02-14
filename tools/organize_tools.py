from pathlib import Path
import shutil
from indexer.index_db import fetch_all_files
from safety.path_guard import is_safe_path


def organize_by_type(target_root: str):
    target = Path(target_root)

    if not is_safe_path(target):
        print("Unsafe target path")
        return

    rows = fetch_all_files()

    moved = 0

    for r in rows:
        path = Path(r[1])
        file_type = r[4]

        if not path.exists():
            continue

        dest_dir = target / file_type
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest_path = dest_dir / path.name

        try:
            shutil.move(str(path), str(dest_path))
            moved += 1
        except Exception:
            continue

    print(f"Organized {moved} files by type.")