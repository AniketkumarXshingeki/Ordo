import json
from pathlib import Path

from ordo.indexer.scanner import scan_files
from ordo.indexer.metadata_extractor import extract_basic_metadata
from ordo.indexer.index_db import init_db, upsert_file

# 1. FIX THE CONFIG PATH: Anchor it to the project root
BASE_DIR = Path(__file__).parent.parent.parent.parent
CONFIG_PATH = BASE_DIR / "config" / "settings.json"

with open(CONFIG_PATH, "r") as f:
    settings = json.load(f)

ALLOWED_ROOTS = [Path(p).resolve() for p in settings["ALLOWED_ROOTS"]]

def run():
    """PHASE 1: Scans all ALLOWED_ROOTS quickly."""
    print("Initializing DB...")
    init_db()

    total = 0
    for root in ALLOWED_ROOTS:
        print(f"\n⚡ Fast Scanning: {root}")

        for file in scan_files(root):
            meta = extract_basic_metadata(file)
            if not meta:
                continue

            # NO heavy AI math here! Just set to None.
            meta["content"] = None
            meta["embedding"] = None

            upsert_file(meta)
            total += 1

            if total % 100 == 0:
                print(f"Processed {total} files...")

    print(f"\n✅ Fast scan complete: Mapped {total} files.")


def scan_with_path(path):
    """PHASE 1: Scans a specific user-provided path quickly."""
    print("Initializing DB...")
    init_db()
    print(f"\n⚡ Fast Scanning: {path}")
    
    total = 0

    for file in scan_files(path):
        meta = extract_basic_metadata(file)
        if not meta:
            continue

        meta["content"] = None
        meta["embedding"] = None

        upsert_file(meta)
        total += 1
        
        if total % 10 == 0:
            print(f"Processed {total} files...")

    print(f"✅ Finished fast scanning '{path}' with {total} files mapped.")

if __name__ == "__main__":
    run()