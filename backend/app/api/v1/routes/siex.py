from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_active_user, require_roles
from app.models.user import User
from app.schemas.siex import SiexAccessRead, SiexEntryRead, SiexEntryValidate, SiexExportPreview
from app.siex.config import SIEX_PREVIEW_OPEN
from app.siex import service as siex_service

router = APIRouter()

TECH_OR_ADMIN = require_roles(["tech", "admin"])


def _require_siex(user: User = Depends(get_current_active_user)) -> User:
    if not siex_service.user_has_siex_access(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Módulo NEXO SIEX no activo para esta cuenta.",
        )
    return user


@router.get("/access", response_model=SiexAccessRead)
def siex_access(user: User = Depends(get_current_active_user)):
    return SiexAccessRead(
        has_access=siex_service.user_has_siex_access(user),
        has_module=user.has_siex_module,
        has_enterprise=user.has_siex_enterprise,
        preview_open=SIEX_PREVIEW_OPEN,
    )


@router.get("/entries", response_model=list[SiexEntryRead])
def my_entries(
    user: User = Depends(_require_siex),
    db: Session = Depends(get_db),
):
    return siex_service.list_my_entries(db, user.id)


@router.get("/entries/pending", response_model=list[SiexEntryRead])
def pending_entries(
    _tech: User = Depends(TECH_OR_ADMIN),
    db: Session = Depends(get_db),
):
    return siex_service.list_pending_for_tech(db)


@router.patch("/entries/{entry_id}/validate", response_model=SiexEntryRead)
def validate_entry(
    entry_id: int,
    payload: SiexEntryValidate,
    tech: User = Depends(TECH_OR_ADMIN),
    db: Session = Depends(get_db),
):
    return siex_service.validate_entry(db, entry_id, tech, payload)


@router.get("/entries/export", response_model=SiexExportPreview)
def export_entries(
    user: User = Depends(_require_siex),
    db: Session = Depends(get_db),
):
    data = siex_service.export_validated(db, user)
    exported_at = datetime.now(timezone.utc)
    if data.get("exported_at"):
        try:
            exported_at = datetime.fromisoformat(data["exported_at"].replace("Z", "+00:00"))
        except ValueError:
            pass
    return SiexExportPreview(
        exported_at=exported_at,
        count=data["count"],
        entries=data["entries"],
    )
