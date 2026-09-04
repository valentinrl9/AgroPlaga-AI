from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.community import PilotCollectiveRead
from app.schemas.user_notification import (
    ActivitySummaryRead,
    UserNotificationRead,
    UserNotificationUnreadCount,
)
from app.services.gamification_service import (
    get_pilot_collective_stats,
    get_weekly_streak,
    get_weekly_vigilance,
)
from app.services.notification_reminder_service import count_open_incidents_needing_action
from app.services.user_notification_service import (
    list_notifications,
    mark_all_read,
    mark_read,
    mark_section_read,
    section_counts,
    unread_count,
)

router = APIRouter()


@router.get("/activity-summary", response_model=ActivitySummaryRead)
def activity_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    collective = get_pilot_collective_stats(db)
    vigilance = get_weekly_vigilance(db, current_user)
    return ActivitySummaryRead(
        unread_count=unread_count(db, current_user.id),
        sections=section_counts(db, current_user.id),
        weekly_vigilance=vigilance,
        streak_weeks=get_weekly_streak(db, current_user.id),
        open_incidents_action_count=count_open_incidents_needing_action(db, current_user.id),
        pilot_collective=PilotCollectiveRead(**collective),
    )


@router.get("/notifications", response_model=list[UserNotificationRead])
def list_my_notifications(
    unread_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return list_notifications(db, current_user.id, unread_only=unread_only, limit=limit)


@router.get("/notifications/unread-count", response_model=UserNotificationUnreadCount)
def my_notifications_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return UserNotificationUnreadCount(
        unread_count=unread_count(db, current_user.id),
        sections=section_counts(db, current_user.id),
    )


@router.patch("/notifications/{notification_id}/read", response_model=UserNotificationRead)
def mark_my_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    row = mark_read(db, notification_id, current_user.id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificación no encontrada")
    return row


@router.patch("/notifications/read-all")
def mark_my_notifications_read_all(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    count = mark_all_read(db, current_user.id)
    return {"marked_read": count}


@router.patch("/notifications/sections/{section}/read")
def mark_my_section_read(
    section: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    allowed = {"history", "incidents", "community", "alerts", "home"}
    if section not in allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sección no válida")
    count = mark_section_read(db, current_user.id, section)
    return {"marked_read": count, "section": section}
