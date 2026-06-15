from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_active_user
from app.models.farm import Farm
from app.models.scan import Scan
from app.models.user import User
from app.schemas.analytics import (
    PersonalAnalyticsResponse,
    RecommendationResponse,
    ZoneContext,
)
from app.services.personal_analytics_service import (
    get_farm_breakdown,
    get_scan_timeline,
    get_user_summary,
    get_zone_context,
)
from app.services.recommendation_service import get_recommendation

router = APIRouter()


@router.get("/me", response_model=PersonalAnalyticsResponse)
def my_analytics(
    days: int = Query(default=90, ge=7, le=365),
    crop: str | None = Query(default=None),
    farm_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if farm_id is not None:
        owned = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
        if not owned:
            farm_id = None

    recent = (
        db.query(Scan)
        .filter(Scan.user_id == current_user.id)
        .order_by(Scan.created_at.desc())
        .limit(20)
        .all()
    )

    return PersonalAnalyticsResponse(
        summary=get_user_summary(db, current_user.id, days=days),
        timeline=get_scan_timeline(db, current_user.id, days=days, crop=crop, farm_id=farm_id),
        farms=get_farm_breakdown(db, current_user.id, days=days),
        recent_scans=recent,
    )


@router.get("/recommendations", response_model=RecommendationResponse)
def recommendations(
    plague: str = Query(..., min_length=2),
    crop: str = Query(default="Tomate"),
    severity: str = Query(default="Moderado"),
    _current_user: User = Depends(get_current_active_user),
):
    return get_recommendation(plague=plague, crop=crop, severity=severity)


@router.get("/zones/{zone_id}", response_model=ZoneContext)
def zone_analytics(
    zone_id: int,
    days: int = Query(default=30, ge=7, le=180),
    _current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    context = get_zone_context(db, zone_id, days=days)
    if not context:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zona no encontrada")
    return context
