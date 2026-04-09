
# import json
# from pathlib import Path

from ordo.safety.path_guard import ALLOWED_ROOTS
from ordo.indexer.scanner import scan_files
from ordo.indexer.metadata_extractor import extract_basic_metadata
from ordo.indexer.index_db import init_db, upsert_file
from ordo.indexer import vector_index

from ordo.safety.path_guard import ALLOWED_ROOTS
from ordo.indexer import vector_index
# 1. FIX THE CONFIG PATH: Anchor it to the project root
# BASE_DIR = Path(__file__).parent.parent.parent.parent
# CONFIG_PATH = BASE_DIR / "config" / "settings.json"

# with open(CONFIG_PATH, "r") as f:
#     settings = json.load(f)

# ALLOWED_ROOTS = [Path(p).resolve() for p in settings["ALLOWED_ROOTS"]]


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


    # Phase 2: Run deep scan to extract content and compute embeddings
    print("\nStarting deep scan to extract content and create embeddings...")
    vector_index.run_deep_scan()



def scan_with_path(path):
    """PHASE 1: Scans a specific user-provided path quickly."""
    print("Initializing DB...")
    init_db()
    print(f"\n⚡ Fast Scanning: {path}")
    
    total = 0

    for file in scan_files(path, allow_outside=True):
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
    print("\n✅ Fast scan complete. Run deep scan separately if you want embeddings and content extraction.")

if __name__ == "__main__":
    run()