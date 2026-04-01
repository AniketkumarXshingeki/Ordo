from pathlib import Path
from ordo.safety.path_guard import ALLOWED_ROOTS
from ordo.indexer.scanner import scan_files
from ordo.indexer.metadata_extractor import extract_basic_metadata
from ordo.indexer.index_db import init_db, upsert_file


def run():
    print("Initializing database...")
    init_db()

    total = 0

    for root in ALLOWED_ROOTS:
        root_path = Path(root).resolve()
        if not root_path.exists():
            print(f"Warning: scan root does not exist: {root_path}")
            continue

        print(f"\nScanning: {root_path}")

        found_any = False
        for file in scan_files(root_path):
            found_any = True
            meta = extract_basic_metadata(file)
            if not meta:
                continue

            upsert_file(meta)
            total += 1

            if total % 50 == 0:
                print(f"Indexed {total} files...")

        if not found_any:
            print(f"No files found under {root_path}.")

    print(f"\nIndexing complete. Total files indexed: {total}")


if __name__ == "__main__":
    run()
