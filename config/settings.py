from pathlib import Path

# Change these to your real folders
ALLOWED_ROOTS = [
    Path("E:/Projects/Ordo/Userdata").resolve(),
    Path("E:/Projects/Ordo/Workspace").resolve(),
]

# Limits for safety
MAX_DELETE_FILES = 20
MAX_MOVE_FILES = 100
