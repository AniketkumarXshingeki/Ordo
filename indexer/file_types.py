def classify_file_type(extension: str) -> str:
    ext = extension.lower()

    if ext in [".pdf", ".docx", ".txt", ".md"]:
        return "document"

    if ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
        return "image"

    if ext in [".mp3", ".wav", ".flac"]:
        return "audio"

    if ext in [".mp4", ".mkv", ".avi", ".mov"]:
        return "video"

    if ext in [".exe", ".apk"]:
        return "application"

    if ext in [".zip", ".rar", ".7z"]:
        return "archive"

    return "other"
