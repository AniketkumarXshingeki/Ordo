import sqlite3
import pickle
import numpy as np
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "index.db"

# Database file size
db_size_mb = DB_PATH.stat().st_size / (1024 * 1024)
print(f"\n{'='*70}")
print(f"DATABASE SIZE: {db_size_mb:.2f} MB")
print(f"{'='*70}\n")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Display files table
cur.execute("SELECT id, name, path, file_type, size_bytes, content, embedding FROM files")
rows = cur.fetchall()

print(f"=== FILES TABLE ===")
print(f"Total files indexed: {len(rows)}\n")

for i, r in enumerate(rows, 1):
    print(f"[{i}/{len(rows)}] ID: {r[0]}")
    print(f"    Name: {r[1]}")
    print(f"    Path: {r[2]}")
    print(f"    Type: {r[3]}")
    print(f"    Size: {r[4]} bytes")

    content_preview = (r[5] or "")[:120]
    if content_preview:
        print(f"    Content preview: {content_preview}...")

    if r[6]:
        emb = pickle.loads(r[6])
        print(f"    Embedding: {len(emb)} dimensions")

    print("-" * 70)

# Display pinboard table
cur.execute("""
SELECT id, file_id, file_path, file_name, file_type, pin_order, pin_category, 
       is_pinned, pinned_at, last_accessed, access_count 
FROM pinboard 
WHERE is_pinned = 1 
ORDER BY pin_order ASC
""")
pin_rows = cur.fetchall()

print(f"\n=== PINBOARD TABLE ===")
print(f"Total pinned files: {len(pin_rows)}\n")

if pin_rows:
    for i, r in enumerate(pin_rows, 1):
        print(f"[{i}/{len(pin_rows)}] Pin ID: {r[0]}")
        print(f"     File ID: {r[1] or 'N/A'}")
        print(f"     File Path: {r[2]}")
        print(f"     File Name: {r[3]}")
        print(f"     File Type: {r[4]}")
        print(f"     Pin Order: {r[5]}")
        print(f"     Category: {r[6]}")
        print(f"     Is Pinned: {bool(r[7])}")
        
        if r[8]:
            pinned_time = datetime.fromtimestamp(r[8]).strftime('%Y-%m-%d %H:%M:%S')
            print(f"     Pinned At: {pinned_time}")
        
        if r[9]:
            accessed_time = datetime.fromtimestamp(r[9]).strftime('%Y-%m-%d %H:%M:%S')
            print(f"     Last Accessed: {accessed_time}")
        
        print(f"     Access Count: {r[10]}")
        print("-" * 70)
else:
    print("No pinned files found.\n")

conn.close()

print(f"\n{'='*70}")
print("DATABASE SUMMARY COMPLETE")
print(f"{'='*70}\n")