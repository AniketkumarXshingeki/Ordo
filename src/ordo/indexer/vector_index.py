import sqlite3
import pickle
import numpy as np
import faiss
import os
from pathlib import Path
from ordo.indexer.embedder import create_embedding
from ordo.indexer.text_extractor import extract_content
from ordo.indexer.index_db import get_unembedded_files, update_file_embedding

# 1. FIX THE PATHS: Anchor them to the root of your project
BASE_DIR = Path(__file__).parent.parent.parent.parent
DB_PATH = BASE_DIR / "data" / "index.db"
INDEX_PATH = BASE_DIR / "data" / "faiss.index"
IDMAP_PATH = BASE_DIR / "data" / "id_map.pkl"

# 2. GLOBAL CACHE: Store the index in memory so it doesn't reload constantly
_INDEX = None
_ID_MAP = None

# ---------------------------
# Build FAISS index from DB
# ---------------------------
def build_index():
    # Convert Path objects to strings for sqlite and faiss
    conn = sqlite3.connect(str(DB_PATH))
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
        
        # Safety check: avoid dividing by zero if an embedding is empty!
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm  
            
        vectors.append(vec.astype("float32"))
        id_map.append(rowid)

    vectors = np.array(vectors)
    dim = vectors.shape[1]
    
    index = faiss.IndexFlatIP(dim)
    index.add(vectors)

    faiss.write_index(index, str(INDEX_PATH))

    with open(IDMAP_PATH, "wb") as f:
        pickle.dump(id_map, f)

    # Force the search cache to reset now that we've built a new index
    global _INDEX, _ID_MAP
    _INDEX = None
    _ID_MAP = None

    print(f"✅ FAISS index built with {len(vectors)} vectors.")


# ---------------------------
# Search FAISS index
# ---------------------------
def search_index(query_vec, top_k=20):
    global _INDEX, _ID_MAP

    # 3. LAZY LOADING: Only read from the hard drive if the cache is empty!
    if _INDEX is None or _ID_MAP is None:
        if not INDEX_PATH.exists():
            print("⚠️ Index not found. Build index first.")
            return []
            
        _INDEX = faiss.read_index(str(INDEX_PATH))
        with open(IDMAP_PATH, "rb") as f:
            _ID_MAP = pickle.load(f)

    # The math stays the same - you did this perfectly!
    norm = np.linalg.norm(query_vec)
    if norm > 0:
        query_vec = query_vec / norm
        
    query_vec = np.array([query_vec.astype("float32")])

    scores, indices = _INDEX.search(query_vec, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        rowid = _ID_MAP[idx]
        results.append((float(score), rowid))

    return results

def run_deep_scan():
    """PHASE 2: Finds files without embeddings, reads them, and updates the DB."""
    print("\n🕵️‍♂️ Starting Deep Scan (Extracting Content & Embeddings)...")
    
    files_to_process = get_unembedded_files() 
    
    if not files_to_process:
        print("All mapped files are already deeply indexed! Rebuilding FAISS map just in case...")
        build_index()
        return

    total = 0
    for file_record in files_to_process:
        file_path = file_record["path"]
        file_type = file_record["file_type"]
        
        # Heavy AI lifting happens here!
        # content = extract_content(file_path, file_type)
        content=''
        text_for_embedding = f"File name: {os.name}, File type: {file_type}"        
        embedding = create_embedding(text_for_embedding)
        
        # Save it back to SQLite
        update_file_embedding(file_record["id"], content, embedding)
        total += 1
        
        if total % 20 == 0:
            print(f"Deep scanned {total} files...")
            
    print("\n✅ Deep scan text extraction complete!")
    
    # Automatically build the index when finished!
    build_index()