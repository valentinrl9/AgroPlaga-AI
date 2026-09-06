"""Registro y consulta de tokens FCM por usuario."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.device_token import DeviceToken


def _now() -> datetime:
    return datetime.now(timezone.utc)


def upsert_device_token(db: Session, *, user_id: int, token: str, platform: str = "android") -> DeviceToken:
    token = token.strip()
    if not token:
        raise ValueError("token vacío")

    existing = db.query(DeviceToken).filter(DeviceToken.token == token).first()
    if existing is not None:
        existing.user_id = user_id
        existing.platform = platform
        existing.updated_at = _now()
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    row = DeviceToken(user_id=user_id, token=token, platform=platform)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_tokens_for_user(db: Session, user_id: int) -> list[DeviceToken]:
    return db.query(DeviceToken).filter(DeviceToken.user_id == user_id).order_by(DeviceToken.updated_at.desc()).all()


def delete_token(db: Session, token: str) -> None:
    row = db.query(DeviceToken).filter(DeviceToken.token == token).first()
    if row is None:
        return
    db.delete(row)
    db.commit()
