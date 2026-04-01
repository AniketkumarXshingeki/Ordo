import sqlite3
import pickle
import numpy as np
import re
from ordo.indexer.embedder import create_embedding
from ordo.indexer.vector_index import search_index

DB_PATH = "data/index.db"


# ------------------------------
# Cosine similarity (normalized)
# ------------------------------
def cosine_similarity(a, b):
    if a is None or b is None:
        return 0.0

    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)

    return float(np.dot(a, b))


# ------------------------------
# Keyword score
# ------------------------------
def keyword_score(query_words, text):
    if not text:
        return 0.0

    text = text.lower()
    matches = sum(1 for w in query_words if w in text)

    return matches / max(len(query_words), 1)


# ------------------------------
# Detect preferred file type
# ------------------------------
def detect_type_boost(query):
    q = query.lower()

    if "pdf" in q or "document" in q or "text" in q:
        return "document"
    if "song" in q or "audio" in q or "music" in q:
        return "audio"
    if "video" in q or "movie" in q:
        return "video"
    if "image" in q or "photo" in q or "picture" in q:
        return "image"
    if "code" in q or "script" in q or "python" in q or "javascript" in q:
        return "code"
    if "data" in q or "excel" in q or "sheet" in q or "csv" in q:
        return "data"
    if "presentation" in q or "powerpoint" in q or "slides" in q:
        return "presentation"
    if "zip" in q or "archive" in q or "compressed" in q:
        return "archive"

    return None


# ------------------------------
# HYBRID SEARCH
# ------------------------------
def hybrid_search(query, top_k=5):
    query_vec = create_embedding(query)
    query_words = re.findall(r"\w+", query.lower())
    preferred_type = detect_type_boost(query)

    # ---- FAISS candidate retrieval ----
    candidates = search_index(query_vec, top_k=50)
    if not candidates:
        return []

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    results = []

    for faiss_score, rowid in candidates:
        cur.execute("""
        SELECT name, path, file_type, content, embedding
        FROM files WHERE rowid=?
        """, (rowid,))
        row = cur.fetchone()
        if not row:
            continue

        name, path, file_type, content, emb_blob = row
        file_vec = pickle.loads(emb_blob)

        sem_score = cosine_similarity(query_vec, file_vec)
        key_score = keyword_score(query_words, name + " " + (content or ""))
        filename_boost = 0.15 if any(w in name.lower() for w in query_words) else 0.0
        type_boost = 0.1 if preferred_type and file_type == preferred_type else 0.0

        final_score = (
            sem_score * 0.7 +
            key_score * 0.3 +
            filename_boost +
            type_boost
        )

        results.append((final_score, name, path))

    conn.close()

    results.sort(reverse=True)
    return results[:top_k]
