from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.contribution_log import ContributionLog
from app.models.outbreak_event import OutbreakEvent
from app.models.scan import Scan
from app.models.user import User
from app.schemas.outbreak_event import OutbreakEventCreate, OutbreakEventValidate
from app.services.gamification_service import check_contribution_badges, check_validator_badges
from app.services.geo_service import event_geom_for_zone
from app.services.spam_guard import assert_can_contribute


def display_plague_for_event(event: OutbreakEvent) -> str:
    return event.corrected_plague or event.plague


def create_anonymous_event(
    db: Session,
    data: OutbreakEventCreate,
    contributor_id: int | None = None,
) -> OutbreakEvent:
    if contributor_id is not None:
        assert_can_contribute(db, contributor_id, data.zone_id, data.plague)

    if data.source_scan_id is not None:
        scan = db.query(Scan).filter(Scan.id == data.source_scan_id).first()
        if scan is None:
            raise ValueError("Escaneo origen no encontrado")
        if contributor_id is not None and scan.user_id != contributor_id:
            raise ValueError("El escaneo no pertenece al usuario actual")
        already_linked = (
            db.query(OutbreakEvent.id)
            .filter(OutbreakEvent.source_scan_id == data.source_scan_id)
            .first()
        )
        if already_linked is not None:
            raise ValueError("Este escaneo ya fue contribuido al mapa")

    geom = event_geom_for_zone(db, data.zone_id)
    if geom is None:
        raise ValueError("Zona SIGPAC no encontrada")

    plague = data.plague.strip().lower()
    event = OutbreakEvent(
        plague=plague,
        severity=data.severity,
        zone_id=data.zone_id,
        geom=geom,
        model_version=data.model_version,
        source_scan_id=data.source_scan_id,
        original_plague=plague,
        status="pending",
        validated=False,
    )
    db.add(event)

    contributor: User | None = None
    if contributor_id is not None:
        contributor = db.query(User).filter(User.id == contributor_id).first()
        if contributor is not None:
            contributor.contribution_count = (contributor.contribution_count or 0) + 1
            db.add(contributor)
            db.add(
                ContributionLog(
                    user_id=contributor_id,
                    zone_id=data.zone_id,
                    plague=plague,
                )
            )

    db.commit()
    db.refresh(event)

    if contributor is not None:
        check_contribution_badges(db, contributor)

    return event


def _apply_validation(
    event: OutbreakEvent,
    validator: User,
    action: str,
    corrected_plague: str | None = None,
    corrected_severity: int | None = None,
) -> None:
    now = datetime.now(timezone.utc)
    if action == "reject":
        event.status = "rejected"
        event.validated = False
        event.validated_by_id = validator.id
        event.validated_at = now
        return

    if action == "correct":
        if not corrected_plague:
            raise ValueError("Indica la plaga corregida")
        event.corrected_plague = corrected_plague
        event.plague = corrected_plague

    if corrected_severity is not None:
        event.severity = corrected_severity

    event.status = "validated"
    event.validated = True
    event.validated_by_id = validator.id
    event.validated_at = now


def validate_event(
    db: Session,
    event: OutbreakEvent,
    validator: User,
    payload: OutbreakEventValidate,
) -> OutbreakEvent:
    try:
        _apply_validation(
            event,
            validator,
            payload.action or "confirm",
            corrected_plague=payload.corrected_plague,
            corrected_severity=payload.corrected_severity,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    db.add(event)
    db.commit()
    db.refresh(event)

    if event.status == "validated":
        check_validator_badges(db, validator.id)

    return event


def sync_scan_validation_to_outbreak(db: Session, scan: Scan, validator: User) -> list[OutbreakEvent]:
    """Propaga la validación del perito al evento de mapa vinculado."""
    events = db.query(OutbreakEvent).filter(OutbreakEvent.source_scan_id == scan.id).all()
    if not events:
        return []

    now = datetime.now(timezone.utc)
    for event in events:
        if scan.tech_status == "rejected":
            event.status = "rejected"
            event.validated = False
        elif scan.tech_status == "confirmed":
            event.status = "validated"
            event.validated = True
        elif scan.tech_status == "corrected":
            corrected = (scan.corrected_plague or "").strip().lower()
            if corrected:
                event.corrected_plague = corrected
                event.plague = corrected
            event.status = "validated"
            event.validated = True
        event.validated_by_id = validator.id
        event.validated_at = now
        db.add(event)

    db.commit()
    for event in events:
        db.refresh(event)
        if event.status == "validated":
            check_validator_badges(db, validator.id)

    return events
