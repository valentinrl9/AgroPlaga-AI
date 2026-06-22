from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.pilot_invite import PilotInvite


def normalize_invite_code(code: str) -> str:
    return code.strip().upper().replace(" ", "")


def consume_invite(db: Session, code: str) -> PilotInvite:
    normalized = normalize_invite_code(code)
    invite = db.query(PilotInvite).filter(PilotInvite.code == normalized).first()
    if invite is None or invite.revoked:
        raise ValueError("Código de invitación no válido.")
    now = datetime.now(timezone.utc)
    expires_at = invite.expires_at
    if expires_at is not None and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at is not None and expires_at < now:
        raise ValueError("Código de invitación caducado.")
    if invite.uses_count >= invite.max_uses:
        raise ValueError("Código de invitación ya utilizado.")
    invite.uses_count += 1
    db.add(invite)
    return invite


def create_invite(
    db: Session,
    *,
    code: str,
    role: str,
    label: str | None = None,
    max_uses: int = 1,
    expires_at: datetime | None = None,
) -> PilotInvite:
    normalized = normalize_invite_code(code)
    existing = db.query(PilotInvite).filter(PilotInvite.code == normalized).first()
    if existing:
        raise ValueError("Ese código ya existe.")
    role_value = role.strip().lower()
    if role_value not in {"farmer", "tech"}:
        raise ValueError("El rol debe ser farmer o tech.")
    invite = PilotInvite(
        code=normalized,
        role=role_value,
        label=label,
        max_uses=max_uses,
        expires_at=expires_at,
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite
