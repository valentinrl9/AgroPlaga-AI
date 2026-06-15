from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.heatmap import HeatmapResponse
from app.services.heatmap_service import get_heatmap_grid

router = APIRouter()


@router.get("", response_model=HeatmapResponse)
def read_heatmap(
    plague: str | None = Query(default=None),
    hours: int = Query(default=168, ge=1, le=720),
    min_severity: int = Query(default=1, ge=1, le=3),
    _current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    cells = get_heatmap_grid(db, plague=plague, hours=hours, min_severity=min_severity)
    return HeatmapResponse(
        hours=hours,
        min_severity=min_severity,
        plague=plague.strip().lower() if plague else None,
        cells=cells,
    )
