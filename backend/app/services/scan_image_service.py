import imghdr
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

MAX_IMAGE_BYTES = 2 * 1024 * 1024
ALLOWED_KINDS = {"jpeg", "png", "webp"}
EXT_BY_KIND = {"jpeg": ".jpg", "png": ".png", "webp": ".webp"}


def ensure_storage_dir() -> Path:
    root = Path(settings.scan_images_dir)
    root.mkdir(parents=True, exist_ok=True)
    return root


async def save_scan_image(scan_id: int, upload: UploadFile) -> str:
    data = await upload.read()
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Imagen vacía")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Imagen demasiado grande (máx. 2 MB)")

    kind = imghdr.what(None, h=data[:32])
    if kind not in ALLOWED_KINDS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato no soportado (JPEG, PNG, WebP)")

    root = ensure_storage_dir()
    filename = f"{scan_id}{EXT_BY_KIND[kind]}"
    path = root / filename
    path.write_bytes(data)
    return filename


def resolve_image_path(image_path: str | None) -> Path | None:
    if not image_path:
        return None
    root = ensure_storage_dir().resolve()
    path = (root / image_path).resolve()
    if not str(path).startswith(str(root)):
        return None
    if not path.is_file():
        return None
    return path
