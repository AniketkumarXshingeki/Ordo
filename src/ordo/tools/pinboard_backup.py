"""
Pinboard (Quick Access) Module for ORDO
Manages pinned files with categories, ordering, and fast retrieval.
"""

import sqlite3
import subprocess
import platform
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from ordo.safety.path_guard import is_safe_path

DB_PATH = "data/index.db"


def init_pinboard_db():
    """
    Initialize pinboard tables in the SQLite database.
    Creates tables for pinned files and pin categories.
    """
    Path("data").mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Pinboard table - stores pinned file metadata
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pinboard (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id INTEGER UNIQUE,
        file_path TEXT UNIQUE,
        file_name TEXT,
        file_type TEXT,
        pin_order INTEGER,
        pin_category TEXT DEFAULT 'General',
        is_pinned BOOLEAN DEFAULT 1,
        pinned_at REAL,
        last_accessed REAL,
        access_count INTEGER DEFAULT 0,
        FOREIGN KEY(file_id) REFERENCES files(id)
    )
    """)

    # Pin categories table - for grouping
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pin_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        display_order INTEGER,
        color TEXT DEFAULT '#3498db'
    )
    """)

    # Create default categories
    default_categories = [
        ('General', 0, '#3498db'),
        ('Work', 1, '#e74c3c'),
        ('Study', 2, '#2ecc71'),
        ('Personal', 3, '#f39c12'),
    ]

    for cat_name, order, color in default_categories:
        cur.execute(
            "INSERT OR IGNORE INTO pin_categories (name, display_order, color) VALUES (?, ?, ?)",
            (cat_name, order, color)
        )

    # Create index for faster queries
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_pinboard_status ON pinboard(is_pinned)
    """)
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_pinboard_category ON pinboard(pin_category)
    """)

    conn.commit()
    conn.close()


def resolve_file_path(file_path: str) -> Path | None:
    """Resolve a file path or filename from the indexed database."""
    candidate = Path(file_path)

    if candidate.exists():
        return candidate

    # Search indexed files by exact filename when no path exists
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT path FROM files WHERE name = ?", (candidate.name,))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print(f"❌ File not found or not indexed: {file_path}")
        return None

    if len(rows) == 1:
        return Path(rows[0][0])

    print(f"❌ Multiple files found with name '{candidate.name}'. Please specify the full path.")
    for row in rows:
        print(f"  - {row[0]}")
    return None


def guess_file_type(file_path: Path) -> str:
    """Map common file extensions to simple pinboard file types."""
    ext = file_path.suffix.lower()
    if ext in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg"}:
        return "Images"
    if ext in {".mp4", ".mov", ".mkv", ".avi", ".webm"}:
        return "Videos"
    if ext in {".mp3", ".wav", ".ogg", ".flac"}:
        return "Audio"
    if ext in {".zip", ".tar", ".gz", ".rar", ".7z"}:
        return "Archives"
    if ext in {".py", ".js", ".ts", ".java", ".c", ".cpp", ".cs", ".go", ".rb", ".sh"}:
        return "Code"
    if ext in {".csv", ".xlsx", ".xls"}:
        return "Spreadsheets"
    if ext in {".ppt", ".pptx"}:
        return "Presentations"
    if ext == ".pdf":
        return "PDFs"
    if ext in {".txt", ".md", ".rtf"}:
        return "Text"
    if file_path.is_dir():
        return "Folders"
    return "Documents"


def pin_file(file_path: str, category: str = "General") -> bool:
    """
    Pin a file for quick access.
    
    Args:
        file_path: Path to the file to pin
        category: Category name (default: 'General')
    
    Returns:
        True if successful, False otherwise
    """
    resolved_path = resolve_file_path(file_path)
    if not resolved_path:
        return False

    if not is_safe_path(resolved_path):
        print("❌ Unsafe path: Cannot pin this file")
        return False

    file_path = str(resolved_path)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        # Get file info from main files table
        cur.execute(
            "SELECT id, name, file_type FROM files WHERE path = ?",
            (file_path,)
        )
        file_row = cur.fetchone()

        if file_row:
            file_id, file_name, file_type = file_row
        else:
            file_id = None
            file_name = Path(file_path).name
            file_type = guess_file_type(Path(file_path))
            print(f"⚠️ File not indexed: storing pin metadata directly for {file_name}")

        # Get the highest pin_order
        cur.execute("SELECT MAX(pin_order) FROM pinboard WHERE is_pinned = 1")
        result = cur.fetchone()
        next_order = (result[0] or 0) + 1

        # Insert or update pinboard entry
        cur.execute("""
        INSERT INTO pinboard (file_id, file_path, file_name, file_type, pin_order, pin_category, is_pinned, pinned_at)
        VALUES (?, ?, ?, ?, ?, ?, 1, ?)
        ON CONFLICT(file_path) DO UPDATE SET 
            is_pinned = 1,
            pin_category = excluded.pin_category,
            pinned_at = excluded.pinned_at
        """, (file_id, file_path, file_name, file_type, next_order, category, datetime.now().timestamp()))

        conn.commit()
        conn.close()
        print(f"✅ File pinned: {file_name} → {category}")
        return True

    except Exception as e:
        print(f"❌ Error pinning file: {e}")
        conn.close()
        return False


def unpin_file(file_path: str) -> bool:
    """
    Unpin a file from quick access.
    
    Args:
        file_path: Path to the file to unpin
    
    Returns:
        True if successful, False otherwise
    """
    resolved_path = resolve_file_path(file_path)
    if not resolved_path:
        return False

    file_path = str(resolved_path)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute(
            "UPDATE pinboard SET is_pinned = 0 WHERE file_path = ?",
            (file_path,)
        )
        conn.commit()

        if cur.rowcount > 0:
            print(f"✅ File unpinned: {file_path}")
            conn.close()
            return True
        else:
            print(f"❌ File not found in pinboard: {file_path}")
            conn.close()
            return False

    except Exception as e:
        print(f"❌ Error unpinning file: {e}")
        conn.close()
        return False


def get_all_pinned_files() -> List[Dict]:
    """
    Retrieve all pinned files sorted by pin_order.
    
    Returns:
        List of dictionaries with pinned file metadata
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
    SELECT id, file_path, file_name, file_type, pin_category, pinned_at, last_accessed, access_count
    FROM pinboard
    WHERE is_pinned = 1
    ORDER BY pin_order ASC
    """)

    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_pinned_by_category(category: str) -> List[Dict]:
    """
    Retrieve pinned files filtered by category.
    
    Args:
        category: Category name to filter by
    
    Returns:
        List of dictionaries with pinned file metadata
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
    SELECT id, file_path, file_name, file_type, pin_category, pinned_at, last_accessed, access_count
    FROM pinboard
    WHERE is_pinned = 1 AND pin_category = ?
    ORDER BY pin_order ASC
    """, (category,))

    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def update_pin_category(file_path: str, new_category: str) -> bool:
    """
    Move a pinned file to a different category.
    
    Args:
        file_path: Path to the pinned file
        new_category: New category name
    
    Returns:
        True if successful, False otherwise
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute(
            "UPDATE pinboard SET pin_category = ? WHERE file_path = ?",
            (new_category, file_path)
        )
        conn.commit()

        if cur.rowcount > 0:
            print(f"✅ File moved to category: {new_category}")
            conn.close()
            return True
        else:
            print(f"❌ File not found in pinboard: {file_path}")
            conn.close()
            return False

    except Exception as e:
        print(f"❌ Error updating category: {e}")
        conn.close()
        return False


def reorder_pins(pin_ids: List[int]) -> bool:
    """
    Reorder pinned files by updating their pin_order.
    
    Args:
        pin_ids: List of pinboard IDs in desired order
    
    Returns:
        True if successful, False otherwise
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        for order, pin_id in enumerate(pin_ids, 1):
            cur.execute(
                "UPDATE pinboard SET pin_order = ? WHERE id = ?",
                (order, pin_id)
            )
        conn.commit()
        print(f"✅ Reordered {len(pin_ids)} pinned files")
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error reordering pins: {e}")
        conn.close()
        return False


def record_pin_access(file_path: str) -> bool:
    """
    Update last_accessed timestamp and increment access_count.
    Called when a pinned file is opened.
    
    Args:
        file_path: Path to the accessed file
    
    Returns:
        True if successful, False otherwise
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute("""
        UPDATE pinboard 
        SET last_accessed = ?, access_count = access_count + 1
        WHERE file_path = ?
        """, (datetime.now().timestamp(), file_path))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error recording access: {e}")
        conn.close()
        return False


def get_categories() -> List[Dict]:
    """
    Retrieve all available pin categories.
    
    Returns:
        List of category dictionaries
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT name, display_order, color FROM pin_categories ORDER BY display_order ASC")
    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def add_category(name: str, color: str = "#3498db") -> bool:
    """
    Add a new pin category.
    
    Args:
        name: Category name
        color: Hex color code
    
    Returns:
        True if successful, False otherwise
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute("SELECT MAX(display_order) FROM pin_categories")
        result = cur.fetchone()
        next_order = (result[0] or 0) + 1

        cur.execute(
            "INSERT INTO pin_categories (name, display_order, color) VALUES (?, ?, ?)",
            (name, next_order, color)
        )
        conn.commit()
        conn.close()
        print(f"✅ Category created: {name}")
        return True

    except Exception as e:
        print(f"❌ Error creating category: {e}")
        conn.close()
        return False


def get_statistics() -> Dict:
    """
    Get pinboard statistics: total pinned, by category, most accessed, etc.
    
    Returns:
        Dictionary with pinboard statistics
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Total pinned files
    cur.execute("SELECT COUNT(*) FROM pinboard WHERE is_pinned = 1")
    total_pinned = cur.fetchone()[0]

    # By category
    cur.execute("""
    SELECT pin_category, COUNT(*) as count
    FROM pinboard
    WHERE is_pinned = 1
    GROUP BY pin_category
    """)
    by_category = {row['pin_category']: row['count'] for row in cur.fetchall()}

    # Most accessed
    cur.execute("""
    SELECT file_name, access_count
    FROM pinboard
    WHERE is_pinned = 1
    ORDER BY access_count DESC
    LIMIT 5
    """)
    most_accessed = [dict(row) for row in cur.fetchall()]

    conn.close()

    return {
        'total_pinned': total_pinned,
        'by_category': by_category,
        'most_accessed': most_accessed
    }


def suggest_files_to_pin(limit: int = 5) -> List[Dict]:
    """
    AI-powered suggestion: files with high access frequency that aren't pinned.
    
    Args:
        limit: Maximum number of suggestions
    
    Returns:
        List of suggested files to pin
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Find frequently accessed files that aren't pinned
    cur.execute("""
    SELECT f.id, f.name, f.path, f.file_type, COUNT(DISTINCT f.id) as freq
    FROM files f
    WHERE f.id NOT IN (SELECT file_id FROM pinboard WHERE is_pinned = 1 AND file_id IS NOT NULL)
    ORDER BY freq DESC
    LIMIT ?
    """, (limit,))

    suggestions = [dict(row) for row in cur.fetchall()]
    conn.close()

    return suggestions


def natural_language_pin(query: str) -> bool:
    """
    Natural language command to pin files.
    Example: "pin my project file" or "pin documents"
    
    Args:
        query: Natural language query
    
    Returns:
        True if successful, False otherwise
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        # Simple fuzzy matching on file names
        search_term = f"%{query.lower().replace('pin ', '')}%"
        
        cur.execute("""
        SELECT id, path, name FROM files
        WHERE LOWER(name) LIKE ?
        LIMIT 1
        """, (search_term,))

        file_row = cur.fetchone()
        conn.close()

        if file_row:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute(
                "INSERT OR IGNORE INTO pinboard (file_id, file_path, file_name, file_type, pin_order, pin_category, is_pinned, pinned_at) "
                "SELECT id, path, name, file_type, COALESCE((SELECT MAX(pin_order) FROM pinboard WHERE is_pinned = 1), 0) + 1, 'General', 1, ? "
                "FROM files WHERE id = ?",
                (datetime.now().timestamp(), file_row['id'])
            )
            conn.commit()
            conn.close()
            print(f"✅ Pinned via natural language: {file_row['name']}")
            return True
        else:
            print(f"❌ No file found matching: {query}")
            return False

    except Exception as e:
        print(f"❌ Error in natural language pin: {e}")
        return False


def open_file_default(file_path: str) -> bool:
    """
    Open a file with the default system application.
    
    Args:
        file_path: Path to the file
    
    Returns:
        True if successful, False otherwise
    """
    file_obj = Path(file_path)
    
    if not file_obj.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    if not is_safe_path(file_obj):
        print("❌ Unsafe path: Cannot open this file")
        return False
    
    try:
        system = platform.system()
        
        if system == "Windows":
            import os
            os.startfile(file_path)
        elif system == "Darwin":  # macOS
            subprocess.Popen(["open", file_path])
        else:  # Linux and others
            subprocess.Popen(["xdg-open", file_path])
        
        # Record the access
        record_pin_access(file_path)
        print(f"✅ Opened: {file_obj.name}")
        return True
    
    except Exception as e:
        print(f"❌ Error opening file: {e}")
        return False


def interactive_pinboard() -> None:
    """
    Interactive pinboard menu where users can select files to open by number.
    Shows pinned files with numbers and waits for user to select which one to open.
    """
    pinned = get_all_pinned_files()
    
    if not pinned:
        print("📌 No pinned files yet.")
        return
    
    print("\n" + "=" * 100)
    print("📌 INTERACTIVE PINBOARD - SELECT A FILE TO OPEN")
    print("=" * 100 + "\n")
    
    # Display files with numbers
    for idx, file_info in enumerate(pinned, 1):
        name = file_info['file_name']
        category = file_info.get('pin_category', 'General')
        path = file_info['file_path']
        
        # Get file type emoji
        file_type = file_info.get('file_type', 'Documents')
        icons = {
            'Documents': '📄',
            'Images': '🖼️',
            'Videos': '🎬',
            'Audio': '🎵',
            'Archives': '📦',
            'Code': '💻',
            'Spreadsheets': '📊',
            'Presentations': '📽️',
            'PDFs': '📕',
            'Text': '📝',
            'Folders': '📁',
        }
        icon = icons.get(file_type, '📄')
        
        print(f"  {idx:2}. {icon} {name}")
        print(f"      📍 {path}")
        print(f"      🏷️  {category}\n")
    
    print("-" * 100)
    print(f"Total: {len(pinned)} pinned file(s)")
    print("\nEnter the file number to open (or 'q' to quit): ", end="")
    
    try:
        user_input = input().strip().lower()
        
        if user_input == 'q' or user_input == 'quit':
            print("👋 Goodbye!")
            return
        
        try:
            file_num = int(user_input)
            if 1 <= file_num <= len(pinned):
                selected_file = pinned[file_num - 1]
                file_path = selected_file['file_path']
                file_name = selected_file['file_name']
                
                print(f"\n🔓 Opening: {file_name}...")
                open_file_default(file_path)
            else:
                print(f"❌ Invalid number. Please enter a number between 1 and {len(pinned)}")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Pinboard closed.")
    except Exception as e:
        print(f"❌ Error: {e}")


def interactive_category_pinboard(category: str) -> None:
    """
    Interactive pinboard for a specific category.
    
    Args:
        category: Category name to display
    """
    pinned = get_pinned_by_category(category)
    
    if not pinned:
        print(f"📌 No pinned files in '{category}' category.")
        return
    
    print("\n" + "=" * 100)
    print(f"📌 PINBOARD - {category.upper()}")
    print("=" * 100 + "\n")
    
    # Display files
    for idx, file_info in enumerate(pinned, 1):
        name = file_info['file_name']
        path = file_info['file_path']
        
        file_type = file_info.get('file_type', 'Documents')
        icons = {
            'Documents': '📄',
            'Images': '🖼️',
            'Videos': '🎬',
            'Audio': '🎵',
            'Archives': '📦',
            'Code': '💻',
            'Spreadsheets': '📊',
            'Presentations': '📽️',
            'PDFs': '📕',
            'Text': '📝',
            'Folders': '📁',
        }
        icon = icons.get(file_type, '📄')
        
        print(f"  {idx:2}. {icon} {name}")
        print(f"      📍 {path}\n")
    
    print("-" * 100)
    print(f"Total: {len(pinned)} file(s)")
    print("\nEnter the file number to open (or 'q' to quit): ", end="")
    
    try:
        user_input = input().strip().lower()
        
        if user_input == 'q' or user_input == 'quit':
            print("👋 Goodbye!")
            return
        
        try:
            file_num = int(user_input)
            if 1 <= file_num <= len(pinned):
                selected_file = pinned[file_num - 1]
                file_path = selected_file['file_path']
                file_name = selected_file['file_name']
                
                print(f"\n🔓 Opening: {file_name}...")
                open_file_default(file_path)
            else:
                print(f"❌ Invalid number. Please enter a number between 1 and {len(pinned)}")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Pinboard closed.")
    except Exception as e:
        print(f"❌ Error: {e}")

def gui_pinboard() -> None:
    """
    GUI-based pinboard where users can view and click to open pinned files.
    Shows pinned files in a scrollable window with buttons for each file.
    """
    pinned = get_all_pinned_files()

    if not pinned:
        messagebox.showinfo("Ordo Pinboard", "📌 No pinned files yet.\n\nStart pinning files with: ordo pin <file_path>")
        return

    # Create main window
    root = tk.Tk()
    root.title("📌 Ordo Pinboard - Quick Access")
    root.geometry("800x600")
    root.configure(bg='#f0f0f0')

    # Title label
    title_label = tk.Label(root, text="📌 Ordo Pinboard", font=("Arial", 16, "bold"), bg='#f0f0f0')
    title_label.pack(pady=10)

    # Create main frame with scrollbar
    main_frame = tk.Frame(root, bg='#f0f0f0')
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    # Canvas and scrollbar for scrolling
    canvas = tk.Canvas(main_frame, bg='#f0f0f0')
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # File type icons
    icons = {
        'Documents': '📄',
        'Images': '🖼️',
        'Videos': '🎬',
        'Audio': '🎵',
        'Archives': '📦',
        'Code': '💻',
        'Spreadsheets': '📊',
        'Presentations': '📽️',
        'PDFs': '📕',
        'Text': '📝',
        'Folders': '📁',
    }

    def open_file(file_path, file_name):
        """Callback to open a file when button is clicked."""
        try:
            root.destroy()  # Close GUI first
            print(f"🔓 Opening: {file_name}...")
            open_file_default(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {e}")

    # Group files by category
    files_by_category = {}
    for file_info in pinned:
        category = file_info.get('pin_category', 'General')
        if category not in files_by_category:
            files_by_category[category] = []
        files_by_category[category].append(file_info)

    # Display files grouped by category
    for category, files in files_by_category.items():
        # Category header
        cat_frame = tk.Frame(scrollable_frame, bg='#e0e0e0', relief='raised', borderwidth=1)
        cat_frame.pack(fill=tk.X, pady=5, padx=5)

        cat_label = tk.Label(cat_frame, text=f"🏷️ {category} ({len(files)} files)",
                           font=("Arial", 12, "bold"), bg='#e0e0e0')
        cat_label.pack(anchor='w', padx=10, pady=5)

        # Files in this category
        for file_info in files:
            file_frame = tk.Frame(scrollable_frame, bg='white', relief='ridge', borderwidth=1)
            file_frame.pack(fill=tk.X, pady=2, padx=10)

            # File icon and name
            icon = icons.get(file_info.get('file_type', 'Documents'), '📄')
            name = file_info['file_name']
            path = file_info['file_path']

            # Button to open file
            open_btn = tk.Button(file_frame, text=f"{icon} {name}",
                               font=("Arial", 10), bg='white', relief='flat',
                               command=lambda fp=path, fn=name: open_file(fp, fn))
            open_btn.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)

            # File info
            info_text = f"📍 {path}"
            if 'last_accessed' in file_info and file_info['last_accessed']:
                last_access = datetime.fromtimestamp(file_info['last_accessed']).strftime("%Y-%m-%d %H:%M")
                info_text += f"\n⏰ Last accessed: {last_access}"

            info_label = tk.Label(file_frame, text=info_text, font=("Arial", 8),
                                bg='white', fg='gray', justify=tk.LEFT)
            info_label.pack(side=tk.RIGHT, padx=10, pady=5, anchor='e')

    # Status bar
    status_frame = tk.Frame(root, bg='#f0f0f0')
    status_frame.pack(fill=tk.X, padx=10, pady=5)

    status_label = tk.Label(status_frame, text=f"Total pinned files: {len(pinned)}",
                          font=("Arial", 9), bg='#f0f0f0')
    status_label.pack(side=tk.LEFT)

    close_btn = tk.Button(status_frame, text="Close", command=root.destroy,
                         font=("Arial", 9), bg='#ff6b6b', fg='white')
    close_btn.pack(side=tk.RIGHT)

    # Bind mousewheel to canvas
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # Start the GUI event loop
    root.mainloop()

