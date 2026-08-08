from fastapi import APIRouter, Depends, Query

from app.core.security import get_current_active_user
from app.data.crop_catalog import search_crops
from app.models.user import User
from app.schemas.crop import CropRead

router = APIRouter()


@router.get("", response_model=list[CropRead])
def list_crops(
    q: str | None = Query(default=None, max_length=50),
    limit: int = Query(default=20, ge=1, le=50),
    _current_user: User = Depends(get_current_active_user),
):
    return search_crops(q, limit=limit)
