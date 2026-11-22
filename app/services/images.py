import io
import uuid
from pathlib import Path

from fastapi import UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError

from app.config import STATIC_DIR, UPLOAD_DIR

MAX_BYTES = 12 * 1024 * 1024


class ImageError(ValueError):
    pass


async def save_upload(file: UploadFile, max_side: int = 1600) -> str:
    """Validate, resize and store an uploaded image as WebP. Returns its URL path."""
    raw = await file.read()
    if not raw:
        raise ImageError("الملف فارغ")
    if len(raw) > MAX_BYTES:
        raise ImageError("حجم الصورة كبير (الحد 12MB)")
    try:
        img = Image.open(io.BytesIO(raw))
        img = ImageOps.exif_transpose(img)
        img.load()
    except (UnidentifiedImageError, OSError):
        raise ImageError("الملف مو صورة صالحة")
    has_alpha = img.mode in ("RGBA", "LA", "P")
    img = img.convert("RGBA" if has_alpha else "RGB")
    img.thumbnail((max_side, max_side), Image.LANCZOS)
    name = f"{uuid.uuid4().hex}.webp"
    img.save(UPLOAD_DIR / name, "WEBP", quality=86, method=4)
    return f"/static/uploads/{name}"


def delete_upload(url: str | None) -> None:
    """Remove a previously uploaded file (never touches demo/static assets)."""
    if not url or not url.startswith("/static/uploads/"):
        return
    path = (STATIC_DIR / url.removeprefix("/static/")).resolve()
    try:
        if UPLOAD_DIR.resolve() in path.parents and path.is_file():
            path.unlink()
    except OSError:
        pass
