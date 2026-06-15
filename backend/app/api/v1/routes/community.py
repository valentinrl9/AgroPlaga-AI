from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.community import CommunityProfileRead
from app.services.gamification_service import (
    get_user_badges,
    get_weekly_vigilance,
    get_zone_ranking,
)

router = APIRouter()


@router.get("/profile", response_model=CommunityProfileRead)
def community_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    ranking_days: int = Query(default=7, ge=1, le=30),
):
    return CommunityProfileRead(
        contribution_count=current_user.contribution_count or 0,
        badges=get_user_badges(db, current_user.id),
        weekly_vigilance=get_weekly_vigilance(db, current_user),
        zone_ranking=get_zone_ranking(db, days=ranking_days),
    )
