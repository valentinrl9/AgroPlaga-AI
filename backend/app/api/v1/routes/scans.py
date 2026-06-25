from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_active_user, require_roles
from app.models.farm import Farm
from app.models.scan import Scan
from app.models.user import User
from app.schemas.scan import ScanCreate, ScanRead, ScanValidateRequest
from app.services.gamification_service import check_scan_badges
from app.services.scan_image_service import resolve_image_path, save_scan_image
from app.services.tech_scan_service import user_can_view_scan_image, validate_scan

router = APIRouter()
TECH_OR_ADMIN = require_roles(["tech", "admin"])


def _scan_to_read(scan: Scan) -> ScanRead:
    return ScanRead(
        id=scan.id,
        crop=scan.crop,
        plague=scan.plague,
        confidence=scan.confidence,
        severity=scan.severity,
        location=scan.location,
        farm_id=scan.farm_id,
        created_at=scan.created_at,
        share_with_tech=scan.share_with_tech,
        tech_status=scan.tech_status,
        corrected_plague=scan.corrected_plague,
        tech_notes=scan.tech_notes,
        validated_at=scan.validated_at,
        has_image=scan.image_path is not None,
    )


def _validate_farm(db: Session, farm_id: int | None, user_id: int) -> None:
    if farm_id is None:
        return
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == user_id).first()
    if not farm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Finca no válida")


@router.get("", response_model=list[ScanRead])
def read_scans(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    scans = (
        db.query(Scan)
        .filter(Scan.user_id == current_user.id)
        .order_by(Scan.created_at.desc())
        .all()
    )
    return [_scan_to_read(scan) for scan in scans]


@router.post("", response_model=ScanRead, status_code=201)
def create_scan(
    scan_data: ScanCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _validate_farm(db, scan_data.farm_id, current_user.id)
    if scan_data.share_with_tech:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Para compartir con el técnico usa POST /scans/with-image con la foto",
        )

    scan = Scan(
        user_id=current_user.id,
        crop=scan_data.crop,
        plague=scan_data.plague,
        confidence=scan_data.confidence,
        severity=scan_data.severity,
        location=scan_data.location,
        farm_id=scan_data.farm_id,
        share_with_tech=False,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    check_scan_badges(db, current_user.id)
    return _scan_to_read(scan)


@router.post("/with-image", response_model=ScanRead, status_code=201)
async def create_scan_with_image(
    crop: str = Form(...),
    plague: str = Form(...),
    confidence: float = Form(...),
    severity: str = Form(...),
    share_with_tech: bool = Form(...),
    location: str | None = Form(None),
    farm_id: int | None = Form(None),
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if not share_with_tech:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="share_with_tech debe ser true al subir imagen para el técnico",
        )

    _validate_farm(db, farm_id, current_user.id)

    scan = Scan(
        user_id=current_user.id,
        crop=crop,
        plague=plague,
        confidence=confidence,
        severity=severity,
        location=location,
        farm_id=farm_id,
        share_with_tech=True,
        tech_status="pending",
    )
    db.add(scan)
    db.flush()

    scan.image_path = await save_scan_image(scan.id, image)
    db.add(scan)
    db.commit()
    db.refresh(scan)
    check_scan_badges(db, current_user.id)
    return _scan_to_read(scan)


@router.get("/{scan_id}/image")
def get_scan_image(
    scan_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escaneo no encontrado")
    if not user_can_view_scan_image(scan, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin acceso a esta imagen")

    path = resolve_image_path(scan.image_path)
    if path is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imagen no disponible")

    media_type = "image/jpeg"
    if path.suffix == ".png":
        media_type = "image/png"
    elif path.suffix == ".webp":
        media_type = "image/webp"
    return FileResponse(path, media_type=media_type)


@router.patch("/{scan_id}/validate", response_model=ScanRead)
def validate_scan_endpoint(
    scan_id: int,
    payload: ScanValidateRequest,
    current_user: User = Depends(TECH_OR_ADMIN),
    db: Session = Depends(get_db),
):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escaneo no encontrado")
    scan = validate_scan(db, scan, current_user, payload)
    return _scan_to_read(scan)
