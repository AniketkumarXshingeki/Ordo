# def classify_file_type(extension: str) -> str:
#     ext = extension.lower()

#     if ext in [".pdf", ".docx", ".txt", ".md"]:
#         return "document"

#     elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
#         return "image"

#     elif ext in [".mp3", ".wav", ".flac"]:
#         return "audio"

#     elif ext in [".mp4", ".mkv", ".avi", ".mov"]:
#         return "video"
    
#     elif ext in [".ppt", ".pptx"]:
#         return "presentation"
#     else:
#         pass

def classify_file_type(extension: str) -> str:
    ext = extension.lower()

    if ext in [".pdf", ".docx", ".txt", ".md", ".rtf"]:
        return "document"

    elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif",".heic"]:
        return "image"

    elif ext in [".mp3", ".wav", ".flac", ".m4a", ".aac"]:
        return "audio"

    elif ext in [".mp4", ".mkv", ".avi", ".mov", ".wmv"]:
        return "video"
    
    elif ext in [".ppt", ".pptx", ".xls", ".xlsx", ".csv", ".json", ".xml"]:
        return "data/presentation"
    
    elif ext in [".py", ".js", ".html", ".css", ".ts", ".cpp", ".c", ".java"]:
        return "code"
    
    elif ext in [".zip", ".rar", ".7z", ".tar", ".gz"]:
        return "archive"
    
    else:

        return "other"


