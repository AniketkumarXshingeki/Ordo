from config.settings import ALLOWED_ROOTS
from indexer.scanner import scan_files
from indexer.metadata_extractor import extract_basic_metadata
from indexer.text_extractor import extract_content
from indexer.index_db import init_db, upsert_file


def run():
    print("Initializing DB...")
    init_db()

    total = 0

    for root in ALLOWED_ROOTS:
        print(f"\nScanning: {root}")

        for file in scan_files(root):
            meta = extract_basic_metadata(file)
            if not meta:
                continue

            content = extract_content(file, meta["file_type"])
            meta["content"] = content

            upsert_file(meta)
            total += 1

            if total % 20 == 0:
                print(f"Processed {total} files...")

    print(f"\nContent indexing complete: {total} files")


if __name__ == "__main__":
    run()
