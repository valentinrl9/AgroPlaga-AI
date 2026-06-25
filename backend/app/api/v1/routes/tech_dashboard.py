from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import require_roles
from app.models.user import User
from app.schemas.scan import PilotFarmerItem, TechScanQueueItem
from app.schemas.tech_dashboard import TechDashboardResponse
from app.services.tech_dashboard_service import (
    build_events_csv,
    get_critical_alerts,
    get_overview,
    get_timeline,
    get_zone_comparison,
)
from app.services.tech_scan_service import get_pending_scans, get_pilot_farmers

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
