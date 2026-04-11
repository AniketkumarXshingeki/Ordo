import sqlite3
from pathlib import Path
import pickle

DB_PATH = "data/index.db"


def init_db():
    """
    Create database and table if not exists.
    Initializes both main index and pinboard databases.
    """
    Path("data").mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT UNIQUE,
    name TEXT,
    parent_path TEXT
)
""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE,
        name TEXT,
        extension TEXT,
        file_type TEXT,
        size_bytes INTEGER,
        created_time REAL,
        modified_time REAL,
        content TEXT,
        embedding BLOB,
        folder_id INTEGER,
        FOREIGN KEY(folder_id) REFERENCES folders(id)
    )
    """)

    conn.commit()
    conn.close()
    
    # Initialize pinboard database
    try:
        from ordo.tools.pinboard import init_pinboard_db
        init_pinboard_db()
    except Exception as e:
        print(f"Note: Pinboard initialization skipped ({e})")

def get_or_create_folder(path: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    folder_path = str(Path(path).parent)
    folder_name = Path(folder_path).name
    parent_path = str(Path(folder_path).parent)

    cur.execute("SELECT id FROM folders WHERE path=?", (folder_path,))
    row = cur.fetchone()

    if row:
        folder_id = row[0]
    else:
        cur.execute("""
        INSERT INTO folders (path, name, parent_path)
        VALUES (?, ?, ?)
        """, (folder_path, folder_name, parent_path))

        folder_id = cur.lastrowid
        conn.commit()

    conn.close()
    return folder_id

def upsert_file(meta: dict):
    """
    Insert or update file metadata.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    embedding_blob = None
    if meta.get("embedding") is not None:
        embedding_blob = pickle.dumps(meta["embedding"])

    folder_id = get_or_create_folder(meta["path"])

    cur.execute("""
    INSERT INTO files (path, name, extension, file_type, size_bytes, created_time, modified_time, content, embedding, folder_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(path) DO UPDATE SET
        name=excluded.name,
        extension=excluded.extension,
        file_type=excluded.file_type,
        size_bytes=excluded.size_bytes,
        created_time=excluded.created_time,
        modified_time=excluded.modified_time,
        content=excluded.content,
        embedding=excluded.embedding
    """, (
        meta["path"],
        meta["name"],
        meta["extension"],
        meta["file_type"],
        meta["size_bytes"],
        meta["created_time"],
        meta["modified_time"],
        meta.get("content", ""),
        embedding_blob,
        folder_id
    ))

    conn.commit()
    conn.close()


def fetch_all_files():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM files")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_unembedded_files():
    """
    Finds all files in the database that don't have an AI embedding yet.
    Returns a list of dictionaries with the file's ID, name, path, and type.
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # This lets us access columns by name (like a dictionary)
    cur = conn.cursor()
    
    # Grab only the files missing their embeddings
    cur.execute("SELECT rowid as id, name, path, file_type FROM files WHERE embedding IS NULL")
    rows = cur.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def update_file_embedding(file_id, content, embedding_vector):
    """
    Saves the extracted text and the FAISS-ready math back to the file's row.
    """
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    
    # Convert your array of numbers into a binary blob so SQLite can store it safely
    emb_blob = pickle.dumps(embedding_vector)
    
    cur.execute(
        "UPDATE files SET content = ?, embedding = ? WHERE rowid = ?",
        (content, emb_blob, file_id)
    )
    
    conn.commit()
    conn.close()