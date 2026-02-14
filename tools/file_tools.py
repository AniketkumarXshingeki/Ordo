from pathlib import Path
import shutil
from safety.path_guard import is_safe_path
from safety.confirmations import confirm_action


def create_folder(path: str):
    p = Path(path)

    if not is_safe_path(p):
        print("Blocked: Unsafe path")
        return False

    p.mkdir(parents=True, exist_ok=True)
    print(f"Folder created: {p}")
    return True


def move_file(src: str, dest: str):
    s = Path(src)
    d = Path(dest)

    if not is_safe_path(s) or not is_safe_path(d.parent):
        print("Blocked: Unsafe path")
        return False

    if not s.exists():
        print("Source file not found")
        return False

    d.parent.mkdir(parents=True, exist_ok=True)

    shutil.move(str(s), str(d))
    print(f"Moved: {s.name} → {d}")
    return True


def rename_file(src: str, new_name: str):
    s = Path(src)

    if not is_safe_path(s):
        print("Blocked: Unsafe path")
        return False

    if not s.exists():
        print("File not found")
        return False

    new_path = s.with_name(new_name)
    s.rename(new_path)

    print(f"Renamed: {s.name} → {new_name}")
    return True


def delete_file(path: str):
    p = Path(path)

    if not is_safe_path(p):
        print("Blocked: Unsafe path")
        return False

    if not p.exists():
        print("File not found")
        return False

    if not confirm_action(f"Delete file {p.name}?"):
        print("Cancelled")
        return False

    p.unlink()
    print(f"Deleted: {p}")
    return True