from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_active_admin, get_current_active_user, require_roles
from app.models.outbreak_event import OutbreakEvent
from app.models.user import User
from app.models.zone import AgriZone
from app.schemas.outbreak_event import OutbreakEventCreate, OutbreakEventRead, OutbreakEventValidate
from app.services.alert_engine import evaluate_zone_plague
from app.services.outbreak_event_service import create_anonymous_event, validate_event

router = APIRouter()

TECH_OR_ADMIN = require_roles(["tech", "admin"])


def _event_read(event: OutbreakEvent, zone_name: str | None = None) -> OutbreakEventRead:
    return OutbreakEventRead(
        id=event.id,
        plague=event.plague,
        severity=event.severity,
        zone_id=event.zone_id,
        zone_name=zone_name,
        reported_at=event.reported_at,
        model_version=event.model_version,
        validated=event.validated,
    )


@router.get("", response_model=list[OutbreakEventRead])
def list_outbreak_events(
    plague: str | None = Query(default=None),
    zone_id: int | None = Query(default=None),
    hours: int | None = Query(default=None, ge=1, le=720),
    min_severity: int = Query(default=1, ge=1, le=3),
    validated_only: bool = Query(default=False),
    _current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    query = db.query(OutbreakEvent, AgriZone.name).outerjoin(
        AgriZone, OutbreakEvent.zone_id == AgriZone.id
    )
    if plague:
        query = query.filter(OutbreakEvent.plague == plague.strip().lower())
    if zone_id is not None:
        query = query.filter(OutbreakEvent.zone_id == zone_id)
    if hours is not None:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        query = query.filter(OutbreakEvent.reported_at >= since)
    if min_severity > 1:
        query = query.filter(OutbreakEvent.severity >= min_severity)
    if validated_only:
        query = query.filter(OutbreakEvent.validated.is_(True))
    rows = query.order_by(OutbreakEvent.reported_at.desc()).limit(500).all()
    return [_event_read(event, zone_name) for event, zone_name in rows]


@router.post("", response_model=OutbreakEventRead, status_code=status.HTTP_201_CREATED)
def contribute_outbreak_event(
    data: OutbreakEventCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    zone = db.query(AgriZone).filter(AgriZone.id == data.zone_id).first()
    if not zone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zona SIGPAC no encontrada")

    try:
        event = create_anonymous_event(db, data, contributor_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    try:
        evaluate_zone_plague(db, event.zone_id, event.plague)
    except Exception:
        pass

    return _event_read(event, zone.name if zone else None)


@router.patch("/{event_id}/validate", response_model=OutbreakEventRead)
def set_event_validation(
    event_id: int,
    body: OutbreakEventValidate,
    current_user: User = Depends(TECH_OR_ADMIN),
    db: Session = Depends(get_db),
):
    event = db.query(OutbreakEvent).filter(OutbreakEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado")
    validated = validate_event(db, event, current_user, validated=body.validated)
    zone = db.query(AgriZone).filter(AgriZone.id == validated.zone_id).first()
    return _event_read(validated, zone.name if zone else None)
