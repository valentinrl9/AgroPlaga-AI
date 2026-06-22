from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_active_admin
from app.models.pilot_invite import PilotInvite
from app.models.user import User
from app.schemas.invite import AdminUserRead, PilotInviteCreate, PilotInviteRead
from app.services.invite_service import create_invite

router = APIRouter()


@router.get("/invites", response_model=list[PilotInviteRead])
def list_invites(
    _admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    return db.query(PilotInvite).order_by(PilotInvite.id.asc()).all()


@router.post("/invites", response_model=PilotInviteRead, status_code=status.HTTP_201_CREATED)
def create_pilot_invite(
    body: PilotInviteCreate,
    _admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    try:
        return create_invite(
            db,
            code=body.code,
            role=body.role,
            label=body.label,
            max_uses=body.max_uses,
            expires_at=body.expires_at,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/invites/{invite_id}/revoke", response_model=PilotInviteRead)
def revoke_invite(
    invite_id: int,
    _admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    invite = db.query(PilotInvite).filter(PilotInvite.id == invite_id).first()
    if invite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitación no encontrada")
    invite.revoked = True
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite


@router.get("/users", response_model=list[AdminUserRead])
def list_users(
    _admin: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    return db.query(User).order_by(User.id.asc()).all()
