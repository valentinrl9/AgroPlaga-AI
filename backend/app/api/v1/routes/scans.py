from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_active_user
from app.models.farm import Farm
from app.models.scan import Scan
from app.models.user import User
from app.schemas.scan import ScanCreate, ScanRead
from app.services.gamification_service import check_scan_badges

router = APIRouter()


@router.get("", response_model=list[ScanRead])
def read_scans(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Scan)
        .filter(Scan.user_id == current_user.id)
        .order_by(Scan.created_at.desc())
        .all()
    )


@router.post("", response_model=ScanRead, status_code=201)
def create_scan(
    scan_data: ScanCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if scan_data.farm_id is not None:
        farm = db.query(Farm).filter(Farm.id == scan_data.farm_id, Farm.user_id == current_user.id).first()
        if not farm:
            from fastapi import HTTPException, status

            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Finca no válida")

    scan = Scan(
        user_id=current_user.id,
        crop=scan_data.crop,
        plague=scan_data.plague,
        confidence=scan_data.confidence,
        severity=scan_data.severity,
        location=scan_data.location,
        farm_id=scan_data.farm_id,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    check_scan_badges(db, current_user.id)
    return scan
