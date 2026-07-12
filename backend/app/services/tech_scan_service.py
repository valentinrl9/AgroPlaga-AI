from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.farm import Farm
from app.models.scan import Scan
from app.models.user import User
from app.schemas.scan import PilotFarmerItem, ScanValidateRequest, TechScanQueueItem
from app.services.outbreak_event_service import sync_scan_validation_to_outbreak


def get_pending_scans(db: Session) -> list[TechScanQueueItem]:
    rows = (
        db.query(Scan, User, Farm.name)
        .join(User, Scan.user_id == User.id)
        .outerjoin(Farm, Scan.farm_id == Farm.id)
        .filter(
            Scan.share_with_tech.is_(True),
            Scan.tech_status == "pending",
            Scan.image_path.isnot(None),
        )
        .order_by(Scan.created_at.asc())
        .all()
    )
    return [
        TechScanQueueItem(
            id=scan.id,
            crop=scan.crop,
            plague=scan.plague,
            confidence=scan.confidence,
            severity=scan.severity,
            farm_id=scan.farm_id,
            farm_name=farm_name,
            farmer_id=user.id,
            farmer_name=user.name,
            farmer_email=user.email,
            created_at=scan.created_at,
            share_with_tech=scan.share_with_tech,
            tech_status=scan.tech_status,
            has_image=True,
        )
        for scan, user, farm_name in rows
    ]


def get_pilot_farmers(db: Session) -> list[PilotFarmerItem]:
    farmers = db.query(User).filter(User.role == "farmer").order_by(User.name.asc()).all()
    items: list[PilotFarmerItem] = []
    for farmer in farmers:
        shared = (
            db.query(Scan)
            .filter(Scan.user_id == farmer.id, Scan.share_with_tech.is_(True))
            .count()
        )
        pending = (
            db.query(Scan)
            .filter(
                Scan.user_id == farmer.id,
                Scan.share_with_tech.is_(True),
                Scan.tech_status == "pending",
            )
            .count()
        )
        if shared == 0:
            farmer_status = "inactive"
        elif pending > 0:
            farmer_status = "pending"
        else:
            farmer_status = "ok"
        items.append(
            PilotFarmerItem(
                id=farmer.id,
                name=farmer.name,
                email=farmer.email,
                shared_scans=shared,
                pending_scans=pending,
                status=farmer_status,
            )
        )
    return items


def validate_scan(
    db: Session,
    scan: Scan,
    validator: User,
    payload: ScanValidateRequest,
) -> Scan:
    if not scan.share_with_tech or scan.tech_status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El escaneo no está pendiente de validación técnica",
        )

    now = datetime.now(timezone.utc)
    if payload.action == "confirm":
        scan.tech_status = "confirmed"
    elif payload.action == "correct":
        if not payload.corrected_plague:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Indica la plaga corregida",
            )
        scan.tech_status = "corrected"
        scan.corrected_plague = payload.corrected_plague
    else:
        scan.tech_status = "rejected"

    scan.tech_notes = payload.tech_notes.strip() if payload.tech_notes else None
    scan.validated_by_id = validator.id
    scan.validated_at = now
    db.add(scan)
    db.commit()
    db.refresh(scan)
    sync_scan_validation_to_outbreak(db, scan, validator)
    return scan


def user_can_view_scan_image(scan: Scan, user: User) -> bool:
    if scan.user_id == user.id:
        return scan.image_path is not None
    if user.role in {"tech", "admin"} and scan.share_with_tech and scan.image_path:
        return True
    return False
