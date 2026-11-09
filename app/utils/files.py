"""Upload validation and storage helpers."""
import os
import uuid
from dataclasses import dataclass, field

from werkzeug.utils import secure_filename

SIGNATURES = {
    "pdf": (b"%PDF",),
    "png": (b"\x89PNG",),
    "jpg": (b"\xff\xd8\xff",),
    "jpeg": (b"\xff\xd8\xff",),
    "docx": (b"PK",),
}


@dataclass
class UploadPolicy:
    folder: str = "uploads"
    allowed: set = field(default_factory=lambda: {"pdf", "png", "jpg", "jpeg", "txt", "docx"})
    max_size: int = 5 * 1024 * 1024


def validate_upload(storage, policy):
    """Return an error message, or None when the file is acceptable."""
    name = secure_filename(storage.filename or "")
    if not name or "." not in name:
        return "Attachment must have a valid file name."
    ext = name.rsplit(".", 1)[1].lower()
    if ext not in policy.allowed:
        return f"'{name}': file type .{ext} is not allowed (allowed: {', '.join(sorted(policy.allowed))})."
    head = storage.stream.read(8)
    storage.stream.seek(0, os.SEEK_END)
    size = storage.stream.tell()
    storage.stream.seek(0)
    if size == 0:
        return f"'{name}' is empty."
    if size > policy.max_size:
        return f"'{name}' exceeds the {policy.max_size // (1024 * 1024)} MB limit."
    sigs = SIGNATURES.get(ext)
    if sigs and not any(head.startswith(s) for s in sigs):
        return f"'{name}' does not look like a valid .{ext} file."
    return None


def save_upload(storage, policy):
    """Store a validated file under a random name; returns (original, stored)."""
    original = secure_filename(storage.filename)
    ext = original.rsplit(".", 1)[1].lower()
    stored = f"{uuid.uuid4().hex}.{ext}"
    os.makedirs(policy.folder, exist_ok=True)
    storage.save(os.path.join(policy.folder, stored))
    return original, stored
