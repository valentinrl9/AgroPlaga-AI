from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import require_roles
from app.models.user import User
from app.schemas.scan import PilotFarmerItem, TechScanQueueItem
from app.schemas.pest_incident import TechIncidentRead
from app.schemas.tech_dashboard import TechDashboardResponse
from app.schemas.tech_notification import TechNotificationRead, TechNotificationUnreadCount
from app.services.tech_dashboard_service import (
    build_events_csv,
    get_critical_alerts,
    get_overview,
    get_timeline,
    get_zone_comparison,
)
from app.services.tech_scan_service import get_pending_scans, get_pilot_farmers
from app.services.pest_incident_service import list_incidents_for_tech
from app.services import tech_notification_service as notif_svc

router = APIRouter()
TECH_OR_ADMIN = require_roles(["tech", "admin"])


@router.get("/dashboard", response_model=TechDashboardResponse)
def tech_dashboard(
    hours: int = Query(default=168, ge=24, le=720),
    timeline_days: int = Query(default=30, ge=7, le=90),
    _current_user: User = Depends(TECH_OR_ADMIN),
    db: Session = Depends(get_db),
):
    return TechDashboardResponse(
        overview=get_overview(db, hours=hours),
        zone_comparison=get_zone_comparison(db, hours=hours),
        timeline=get_timeline(db, days=timeline_days),
        critical_alerts=get_critical_alerts(db),
    )


@router.get("/export/events.csv")
def export_events_csv(
    hours: int = Query(default=720, ge=24, le=720),
    _current_user: User = Depends(TECH_OR_ADMIN),
    db: Session = Depends(get_db),
):
    content = build_events_csv(db, hours=hours)
    return PlainTextResponse(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=eventos_agroplaga.csv"},
    )


@router.get("/pending-scans", response_model=list[TechScanQueueItem])
def list_pending_scans(
    _current_user: User = Depends(TECH_OR_ADMIN),
    db: Session = Depends(get_db),
):
    return get_pending_scans(db)


@router.get("/farmers", response_model=list[PilotFarmerItem])
def list_pilot_farmers(
    _current_user: User = Depends(TECH_OR_ADMIN),
    db: Session = Depends(get_db),
):
    return get_pilot_farmers(db)


@router.get("/incidents", response_model=list[TechIncidentRead])
def list_tech_incidents(
    active_only: bool = Query(default=True),
    _current_user: User = Depends(TECH_OR_ADMIN),
    db: Session = Depends(get_db),
):
    return list_incidents_for_tech(db, active_only=active_only)


@router.get("/notifications", response_model=list[TechNotificationRead])
def list_tech_notifications(
    unread_only: bool = False,
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(TECH_OR_ADMIN),
    db: Session = Depends(get_db),
):
    return notif_svc.list_notifications(db, current_user.id, unread_only=unread_only, limit=limit)


@router.get("/notifications/unread-count", response_model=TechNotificationUnreadCount)
def tech_notifications_unread_count(
    current_user: User = Depends(TECH_OR_ADMIN),
    db: Session = Depends(get_db),
):
    pending = len(get_pending_scans(db))
    return TechNotificationUnreadCount(
        unread_count=notif_svc.unread_count(db, current_user.id),
        pending_scans=pending,
    )


@router.patch("/notifications/{notification_id}/read", response_model=TechNotificationRead)
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(TECH_OR_ADMIN),
    db: Session = Depends(get_db),
):
    row = notif_svc.mark_read(db, notification_id, current_user.id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificación no encontrada")
    return row


@router.patch("/notifications/read-all")
def mark_all_notifications_read(
    current_user: User = Depends(TECH_OR_ADMIN),
    db: Session = Depends(get_db),
):
    count = notif_svc.mark_all_read(db, current_user.id)
    return {"marked_read": count}
