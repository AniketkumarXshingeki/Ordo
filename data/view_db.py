import sqlite3
import pickle
import numpy as np
from datetime import datetime

conn = sqlite3.connect("data/index.db")
cur = conn.cursor()

# Display files table
cur.execute("SELECT id, name, path, file_type, size_bytes, content, embedding FROM files")
rows = cur.fetchall()

print(f"\n=== FILES TABLE ===\nTotal rows: {len(rows)}\n")

for r in rows[:10]:
    print("ID:", r[0])
    print("Name:", r[1])
    print("Path:", r[2])
    print("Type:", r[3])
    print("Size:", r[4])

    content_preview = (r[5] or "")[:120]
    print("Content preview:", content_preview)

    if r[6]:
        emb = pickle.loads(r[6])
        print("Embedding length:", len(emb))
        print("Embedding sample:", emb[:5])

    print("-" * 50)

# Display pinboard table
cur.execute("""
SELECT id, file_id, file_path, file_name, file_type, pin_order, pin_category, 
       is_pinned, pinned_at, last_accessed, access_count 
FROM pinboard 
WHERE is_pinned = 1 
ORDER BY pin_order ASC
""")
pin_rows = cur.fetchall()

print(f"\n=== PINBOARD TABLE ===\nTotal pinned files: {len(pin_rows)}\n")

for r in pin_rows:
    print("Pin ID:", r[0])
    print("File ID:", r[1] or "N/A")
    print("File Path:", r[2])
    print("File Name:", r[3])
    print("File Type:", r[4])
    print("Pin Order:", r[5])
    print("Category:", r[6])
    print("Is Pinned:", bool(r[7]))
    
    if r[8]:
        pinned_time = datetime.fromtimestamp(r[8]).strftime('%Y-%m-%d %H:%M:%S')
        print("Pinned At:", pinned_time)
    
    if r[9]:
        accessed_time = datetime.fromtimestamp(r[9]).strftime('%Y-%m-%d %H:%M:%S')
        print("Last Accessed:", accessed_time)
    
    print("Access Count:", r[10])
    print("-" * 50)

conn.close()