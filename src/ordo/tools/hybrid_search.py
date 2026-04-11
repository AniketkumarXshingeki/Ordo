import sqlite3
import pickle
import numpy as np
import re
import difflib
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
STOP_WORDS = {"the", "is", "at", "which", "on", "in", "a", "an", "and", "of", "to"}

def keyword_score(query_words, text):
    if not text or not query_words:
        return 0.0

    text_words = set(re.findall(r"\w+", text.lower()))
    
    matches = 0
    filtered_qw = [w for w in query_words if w not in STOP_WORDS]
    
    for w in filtered_qw:
        if any(t.startswith(w) for t in text_words):
            matches += 1
        elif difflib.get_close_matches(w, text_words, n=1, cutoff=0.8):
            matches += 1
            
    return matches / max(len(filtered_qw), 1)


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
        SELECT name, path, file_type, content, embedding, created_time
        FROM files WHERE rowid=?
        """, (rowid,))
        row = cur.fetchone()
        if not row:
            continue

        name, path, file_type, content, emb_blob, created_time = row
        file_vec = pickle.loads(emb_blob)

        sem_score = cosine_similarity(query_vec, file_vec)
        key_score = keyword_score(query_words, name + " " + (content or ""))
        
        filtered_query_words = [w for w in query_words if w not in STOP_WORDS]
        name_words = set(re.findall(r"\w+", name.lower()))
        filename_boost = 0.0
        for w in filtered_query_words:
            if any(t.startswith(w) for t in name_words) or difflib.get_close_matches(w, name_words, n=1, cutoff=0.8):
                filename_boost = 0.15
                break
                
        if query.lower() in (name.lower() + " " + (content or "").lower()):
            filename_boost += 0.2
            
        type_boost = 0.1 if preferred_type and file_type == preferred_type else 0.0

        final_score = (
            sem_score * 0.7 +
            key_score * 0.3 +
            filename_boost +
            type_boost
        )

        results.append({
            "score": final_score,
            "name": name,
            "path": path,
            "file_type": file_type,
            "created_time": created_time
        })

    conn.close()

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
