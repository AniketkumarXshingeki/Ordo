from pathlib import Path
import PyPDF2
from mutagen import File as AudioFile

MAX_TEXT_LENGTH = 4000   # prevent large memory usage


def extract_text_file(path: Path) -> str:
    try:
        return path.read_text(errors="ignore")[:MAX_TEXT_LENGTH]
    except Exception:
        return ""


def extract_pdf(path: Path) -> str:
    text = ""
    try:
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages[:10]:   # limit pages for safety
                page_text = page.extract_text() or ""
                text += page_text
                if len(text) > MAX_TEXT_LENGTH:
                    break
    except Exception:
        return ""

    return " ".join(text.split())[:MAX_TEXT_LENGTH]


def extract_audio_metadata(path: Path) -> str:
    try:
        audio = AudioFile(path)
        if not audio or not audio.tags:
            return ""
        return " ".join([str(v) for v in audio.tags.values()])
    except Exception:
        return ""


def extract_content(path: Path, file_type: str) -> str:
    if file_type == "document":
        if path.suffix.lower() == ".pdf":
            return extract_pdf(path)
        return extract_text_file(path)

    if file_type == "audio":
        return extract_audio_metadata(path)

    return ""
