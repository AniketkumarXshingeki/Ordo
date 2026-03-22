from pathlib import Path

from src.ordo.utils.detect_drivers import get_available_drives

 # Change these to your real folders
 # ALLOWED_ROOTS = [Path(d).resolve() for d in get_available_drives()]
{
  "ALLOWED_ROOTS": ["E:/"]
}
# // # Limits for safety
# // MAX_DELETE_FILES = 20
# // MAX_MOVE_FILES = 100