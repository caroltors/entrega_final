import os
from django import template

register = template.Library()

_ICON_MAP = {
    # docs
    "pdf": "bi-filetype-pdf",
    "doc": "bi-filetype-doc",
    "docx": "bi-filetype-docx",
    "txt": "bi-filetype-txt",
    "json": "bi-filetype-json",
    "csv": "bi-filetype-csv",
    "ppt": "bi-filetype-ppt",
    "pptx": "bi-filetype-pptx",
    "xls": "bi-filetype-xls",
    "xlsx": "bi-filetype-xlsx",
    # archives
    "zip": "bi-file-zip",
    "rar": "bi-file-zip",
    "7z":  "bi-file-zip",
    # media
    "mp4": "bi-filetype-mp4",
    "mp3": "bi-filetype-mp3",
    "wav": "bi-filetype-wav",
}

@register.filter
def basename(path: str) -> str:
    try:
        return os.path.basename(path or "")
    except Exception:
        return path

@register.filter
def file_ext(path: str) -> str:
    try:
        return (os.path.splitext(path or "")[1] or "").lower().lstrip(".")
    except Exception:
        return ""

@register.filter
def file_icon(path_or_ext: str) -> str:
    ext = path_or_ext
    if "." in (path_or_ext or ""):
        ext = file_ext(path_or_ext)
    return _ICON_MAP.get(ext or "", "bi-paperclip")

@register.filter
def filesize(num) -> str:
    """Converte bytes -> string legível."""
    try:
        n = int(num)
    except Exception:
        return ""
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while n >= 1024 and i < len(units) - 1:
        n /= 1024.0
        i += 1
    return f"{n:.1f} {units[i]}"
