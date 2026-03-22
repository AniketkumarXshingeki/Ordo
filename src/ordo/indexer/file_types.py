def classify_file_type(extension: str) -> str:
    ext = extension.lower()

    if ext in [".pdf", ".docx", ".txt", ".md"]:
        return "document"

    elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
        return "image"

    elif ext in [".mp3", ".wav", ".flac"]:
        return "audio"

    elif ext in [".mp4", ".mkv", ".avi", ".mov"]:
        return "video"
    
    elif ext in [".ppt", ".pptx"]:
        return "presentation"
    else:
        pass

