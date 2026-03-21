import sqlite3
import pickle
import numpy as np
from indexer.embedder import create_embedding

DB_PATH = "data/index.db"


def cosine_similarity(a, b):
    if a is None or b is None:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def semantic_search(query, top_k=5):
    query_vec = create_embedding(query)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name, path, embedding FROM files")
    rows = cur.fetchall()
    conn.close()

    results = []

    for name, path, emb_blob in rows:
        if emb_blob is None:
            continue

        file_vec = pickle.loads(emb_blob)
        score = cosine_similarity(query_vec, file_vec)
        results.append((score, name, path))

    results.sort(reverse=True)
    return results[:top_k]