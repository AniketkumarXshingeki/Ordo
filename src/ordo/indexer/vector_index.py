import sqlite3
import pickle
import numpy as np
import faiss
import os

DB_PATH = "data/index.db"
INDEX_PATH = "data/faiss.index"
IDMAP_PATH = "data/id_map.pkl"


# ---------------------------
# Build FAISS index from DB
# ---------------------------
def build_index():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT rowid, embedding FROM files WHERE embedding IS NOT NULL")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("No embeddings found.")
        return

    vectors = []
    id_map = []

    for rowid, emb_blob in rows:
        vec = pickle.loads(emb_blob)
        vec = vec / np.linalg.norm(vec)   # normalize
        vectors.append(vec.astype("float32"))
        id_map.append(rowid)

    vectors = np.array(vectors)

    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)   # cosine via inner product
    index.add(vectors)

    faiss.write_index(index, INDEX_PATH)

    with open(IDMAP_PATH, "wb") as f:
        pickle.dump(id_map, f)

    print(f"FAISS index built with {len(vectors)} vectors.")

def search_index(query_vec, top_k=20):
    if not os.path.exists(INDEX_PATH):
        print("Index not found. Build index first.")
        return []

    index = faiss.read_index(INDEX_PATH)

    with open(IDMAP_PATH, "rb") as f:
        id_map = pickle.load(f)

    query_vec = query_vec / np.linalg.norm(query_vec)
    query_vec = np.array([query_vec.astype("float32")])

    scores, indices = index.search(query_vec, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        rowid = id_map[idx]
        results.append((float(score), rowid))

    return results

