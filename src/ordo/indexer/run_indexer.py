from ordo.indexer.scanner import scan_files
from ordo.indexer.metadata_extractor import extract_basic_metadata
from ordo.indexer.index_db import init_db, upsert_file

ALLOWED_ROOTS = [
    "C:/Users/YourUsername/Documents",]

def run():
    print("Initializing database...")
    init_db()

    total = 0

    for root in ALLOWED_ROOTS:
        print(f"\nScanning: {root}")

        for file in scan_files(root):
            meta = extract_basic_metadata(file)
            if not meta:
                continue

            upsert_file(meta)
            total += 1

            if total % 50 == 0:
                print(f"Indexed {total} files...")

    print(f"\nIndexing complete. Total files indexed: {total}")


if __name__ == "__main__":
    run()
