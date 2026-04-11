import sqlite3
import re
import difflib
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

STOP_WORDS = {"the", "is", "at", "which", "on", "in", "a", "an", "and", "of", "to"}

def keyword_score(query_words, text):
    """Calculates keyword match score using prefix matching (stemming) and fuzzy matching (typos)."""
    if not text or not query_words:
        return 0.0
        
    text_words = set(re.findall(r"\w+", text.lower()))
    
    matches = 0
    filtered_qw = [w for w in query_words if w not in STOP_WORDS]
    
    for w in filtered_qw:
        # Check prefix matching (stemming) or exact match
        if any(t.startswith(w) for t in text_words):
            matches += 1
        # Check fuzzy matching for spelling mistakes
        elif difflib.get_close_matches(w, text_words, n=1, cutoff=0.8):
            matches += 1
            
    return matches / max(len(filtered_qw), 1)

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
    
    filtered_query_words = [w for w in query_words if w not in STOP_WORDS]
    
    for row in rows:
        name = row["name"]
        content = row["content"] or ""
        
        # If there's no query, just sort by newest files
        if not query:
            results.append({
                "score": 1.0,  # default score
                "name": name,
                "path": row["path"],
                "created_time": row["created_time"],
                "file_type": row["file_type"]
            })
            continue

        # Use your awesome hybrid formula!
        sem_score = faiss_scores.get(row["id"], 0.0)
        key_score = keyword_score(query_words, name + " " + content)
        
        # Boost if word is in filename (exact or typo prefix)
        name_words = set(re.findall(r"\w+", name.lower()))
        filename_boost = 0.0
        for w in filtered_query_words:
            if any(t.startswith(w) for t in name_words) or difflib.get_close_matches(w, name_words, n=1, cutoff=0.8):
                filename_boost = 0.15
                break
                
        # Exact Phrase Match Boost
        if query.lower() in (name.lower() + " " + content.lower()):
            filename_boost += 0.2
        
        final_score = (sem_score * 0.7) + (key_score * 0.3) + filename_boost
        
        results.append({
            "score": final_score,
            "name": name,
            "path": row["path"],
            "created_time": row["created_time"],
            "file_type": row["file_type"]
        })

    # Sort descending (Highest score first, or Newest first if no query)
    # The key needs to handle both scenarios safely
    if query:
        results.sort(key=lambda x: x["score"], reverse=True)
    else:
        results.sort(key=lambda x: x["created_time"], reverse=True)
    
    # Return formatted results
    return results[:top_k]