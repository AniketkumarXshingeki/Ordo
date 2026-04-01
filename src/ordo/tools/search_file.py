import sqlite3
import re
from datetime import datetime
from pathlib import Path

from ordo.indexer.embedder import create_embedding
from ordo.indexer.vector_index import search_index

BASE_DIR = Path(__file__).parent.parent.parent.parent
DB_PATH = BASE_DIR / "data" / "index.db"

# Map human words to categories
TYPE_MAP = {
    "document": [".pdf", ".docx", ".txt", ".md", ".rtf"],
    "audio": [".mp3", ".wav", ".flac", ".m4a", ".aac"],
    "video": [".mp4", ".mkv", ".avi", ".mov", ".wmv"],
    "image": [".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif"],
    "presentation": [".ppt", ".pptx", ".xls", ".xlsx", ".csv", ".json", ".xml"],
    "code": [".py", ".js", ".html", ".css", ".ts", ".cpp", ".c", ".java"],
    "archive": [".zip", ".rar", ".7z", ".tar", ".gz"]
}

def keyword_score(query_words, text):
    """Calculates how many exact query words appear in the text."""
    if not text or not query_words:
        return 0.0
    text = text.lower()
    matches = sum(1 for w in query_words if w in text)
    return matches / max(len(query_words), 1)

def hybrid_search(
    query: str = None, 
    category: str = None,   # e.g., "document", "image", or exact ".pdf"
    start_ts: float = None, # Start time (Unix Timestamp)
    end_ts: float = None,   # End time (Unix Timestamp)
    top_k: int = 5
):
    """
    The Allrounder: Combines FAISS Semantic Search with Time & Type Filters.
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    faiss_scores = {}
    query_words = []

    # ==========================================
    # 1. FAISS SEMANTIC SEARCH (If user provided text)
    # ==========================================
    if query:
        query_vec = create_embedding(query)
        query_words = re.findall(r"\w+", query.lower())
        
        # Get Top 100 to allow room for the time/type filters to cut some out
        candidates = search_index(query_vec, top_k=100)
        if not candidates:
            return []
            
        # Store the FAISS scores (this IS the cosine similarity!)
        for score, rowid in candidates:
            faiss_scores[rowid] = score

    # ==========================================
    # 2. SQLITE FILTERING (Time & Type)
    # ==========================================
    sql = "SELECT rowid as id, name, path, file_type, content, created_time FROM files WHERE 1=1"
    params = []

    # Filter by FAISS candidates if we have a query
    if faiss_scores:
        placeholders = ",".join("?" for _ in faiss_scores.keys())
        sql += f" AND rowid IN ({placeholders})"
        params.extend(faiss_scores.keys())

    # Filter by File Type (e.g., 'document' or '.pdf')
    if category:
        category = category.lower()
        if category in TYPE_MAP:
            # If it's a category name, filter by the file_type column
            sql += " AND file_type = ?"
            params.append(category)
        elif category.startswith("."):
            # If it's an extension, filter by the extension column
            sql += " AND extension = ?"
            params.append(category)
        else:
            # Fallback: check both
            sql += " AND (file_type = ? OR extension = ?)"
            params.extend([category, "." + category if not category.startswith(".") else category])

    # Filter by Time (Using your start/end timestamp logic)
    if start_ts is not None:
        sql += " AND created_time >= ?"
        params.append(start_ts)
    if end_ts is not None:
        sql += " AND created_time <= ?"
        params.append(end_ts)

    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()

    # ==========================================
    # 3. SCORING & SORTING (Your custom formula!)
    # ==========================================
    results = []
    for row in rows:
        name = row["name"]
        content = row["content"] or ""
        
        # If there's no query, just sort by newest files
        if not query:
            results.append((row["created_time"], name, row["path"]))
            continue

        # Use your awesome hybrid formula!
        sem_score = faiss_scores.get(row["id"], 0.0)
        key_score = keyword_score(query_words, name + " " + content)
        filename_boost = 0.15 if any(w in name.lower() for w in query_words) else 0.0
        
        final_score = (sem_score * 0.7) + (key_score * 0.3) + filename_boost
        results.append((final_score, name, row["path"]))

    # Sort descending (Highest score first, or Newest first if no query)
    results.sort(key=lambda x: x[0], reverse=True)
    
    # Return formatted results without the score
    print(results[:top_k])
    return results[:top_k]