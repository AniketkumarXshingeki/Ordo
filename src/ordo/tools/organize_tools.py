from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import shutil
from ordo.indexer.index_db import iterate_all_files
from ordo.safety.path_guard import is_safe_path


def organize_by_type(target_root: str, dry_run: bool = False, max_workers: int = 4):
    target = Path(target_root)

    if not is_safe_path(target):
        print("Unsafe target path")
        return

    moved = 0

    def move_item(row):
        path = Path(row[0])
        file_type = row[1]

        if not path.exists():
            return False

        dest_dir = target / file_type
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest_path = dest_dir / path.name
        if dry_run:
            return True

        try:
            shutil.move(str(path), str(dest_path))
            return True
        except Exception:
            return False

    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for row in iterate_all_files():
            futures.append(executor.submit(move_item, row))
            if len(futures) >= max_workers * 2:
                for future in as_completed(futures):
                    if future.result():
                        moved += 1
                futures = []

        for future in as_completed(futures):
            if future.result():
                moved += 1

    if dry_run:
        print(f"Dry run complete. {moved} files would be organized by type.")
    else:
        print(f"Organized {moved} files by type.")
