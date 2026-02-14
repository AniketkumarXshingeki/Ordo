import sqlite3
import pickle
import numpy as np

conn = sqlite3.connect("data/index.db")
cur = conn.cursor()

cur.execute("SELECT id, name, path, file_type, size_bytes, content, embedding FROM files")
rows = cur.fetchall()

print(f"\nTotal rows: {len(rows)}\n")

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

conn.close()