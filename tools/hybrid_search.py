import sqlite3
import pickle
import numpy as np
import re
from indexer.embedder import create_embedding

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

    if "pdf" in q or "document" in q:
        return "document"
    if "song" in q or "audio" in q or "music" in q:
        return "audio"
    if "video" in q or "movie" in q:
        return "video"
    if "image" in q or "photo" in q:
        return "image"

    return None


# ------------------------------
# HYBRID SEARCH
# ------------------------------
def hybrid_search(query, top_k=5):
    query_vec = create_embedding(query)
    query_words = re.findall(r"\w+", query.lower())
    preferred_type = detect_type_boost(query)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    SELECT name, path, file_type, content, embedding
    FROM files
    """)

    rows = cur.fetchall()
    conn.close()

    results = []

    for name, path, file_type, content, emb_blob in rows:
        if emb_blob is None:
            continue

        file_vec = pickle.loads(emb_blob)

        # --- Semantic similarity ---
        sem_score = cosine_similarity(query_vec, file_vec)

        # --- Keyword match ---
        key_score = keyword_score(query_words, name + " " + (content or ""))

        # --- Filename boost ---
        filename_boost = 0.15 if any(w in name.lower() for w in query_words) else 0.0

        # --- File type boost ---
        type_boost = 0.1 if preferred_type and file_type == preferred_type else 0.0

        # --- Final hybrid score ---
        final_score = (
            sem_score * 0.7 +
            key_score * 0.3 +
            filename_boost +
            type_boost
        )

        results.append((final_score, name, path))

    results.sort(reverse=True)
    return results[:top_k]
