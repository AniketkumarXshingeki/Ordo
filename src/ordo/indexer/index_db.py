import sqlite3
from pathlib import Path
import pickle

DB_PATH = "data/index.db"


def init_db():
    """
    Create database and table if not exists.
    """
    Path("data").mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

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
        embedding BLOB
    )
    """)

    conn.commit()
    conn.close()


def upsert_file(meta: dict):
    """
    Insert or update file metadata.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    embedding_blob = None
    if meta.get("embedding") is not None:
        embedding_blob = pickle.dumps(meta["embedding"])

    cur.execute("""
    INSERT INTO files (path, name, extension, file_type, size_bytes, created_time, modified_time, content, embedding)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        embedding_blob
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
