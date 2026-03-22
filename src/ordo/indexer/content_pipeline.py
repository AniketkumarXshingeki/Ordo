from ordo.indexer.scanner import scan_files
from ordo.indexer.metadata_extractor import extract_basic_metadata
from ordo.indexer.text_extractor import extract_content
from ordo.indexer.index_db import init_db, upsert_file
from ordo.indexer.embedder import create_embedding
import json
from pathlib import Path

# Load settings.json
with open("config/settings.json", "r") as f:
    settings = json.load(f)

# Convert to Path objects
ALLOWED_ROOTS = [Path(p).resolve() for p in settings["ALLOWED_ROOTS"]]


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



            text_for_embedding = meta["name"] + " " + (meta["content"] or "")
            embedding = create_embedding(text_for_embedding)
            meta["embedding"] = embedding

            upsert_file(meta)
            total += 1

            if total % 20 == 0:
                print(f"Processed {total} files...")

    print(f"\nContent + Embedding indexing complete: {total} files")


def scan_with_path(path):
    print("Initializing DB...")
    init_db()
    print(f"Scanning: {path}")
    total = 0

    for file in scan_files(path):
        meta = extract_basic_metadata(file)
        if not meta:
            continue

        content = extract_content(file, meta["file_type"])
        meta["content"] = content

        text_for_embedding = meta["name"] + " " + (meta["content"] or "")
        embedding = create_embedding(text_for_embedding)
        meta["embedding"] = embedding

        upsert_file(meta)
        total += 1
        if total % 20 == 0:
            print(f"Processed {total} files...")

    print(f"Finished scanning {path} with {total} files")


if __name__ == "__main__":
    run()
