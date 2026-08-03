"""Notificaciones in-app para peritos cuando un agricultor comparte un escaneo."""

from sqlalchemy.orm import Session

from app.models.scan import Scan
from app.models.tech_notification import TechNotification
from app.models.user import User
from app.services.notification_service import send_push_to_user


def _tech_recipients(db: Session) -> list[User]:
    return (
        db.query(User)
        .filter(User.role.in_(["tech", "admin"]))
        .order_by(User.id.asc())
        .all()
    )


def notify_scan_pending_validation(db: Session, scan: Scan, farmer: User) -> int:
    """Crea notificación para cada perito/admin. Devuelve cuántas se crearon."""
    plague = scan.plague or "plaga"
    crop = scan.crop or "cultivo"
    title = "Nueva validación pendiente"
    body = f"{farmer.name} compartió un escaneo ({crop} · {plague}) para revisión."

    created = 0
    for recipient in _tech_recipients(db):
        db.add(
            TechNotification(
                recipient_id=recipient.id,
                scan_id=scan.id,
                notification_type="scan_pending",
                title=title,
                body=body,
                is_read=False,
            )
        )
        send_push_to_user(recipient.id, title, body)
        created += 1

    if created:
        db.commit()
    return created


def list_notifications(db: Session, recipient_id: int, *, unread_only: bool = False, limit: int = 50) -> list[TechNotification]:
    q = db.query(TechNotification).filter(TechNotification.recipient_id == recipient_id)
    if unread_only:
        q = q.filter(TechNotification.is_read.is_(False))
    return q.order_by(TechNotification.created_at.desc()).limit(limit).all()


def unread_count(db: Session, recipient_id: int) -> int:
    return (
        db.query(TechNotification)
        .filter(
            TechNotification.recipient_id == recipient_id,
            TechNotification.is_read.is_(False),
        )
        .count()
    )


def mark_read(db: Session, notification_id: int, recipient_id: int) -> TechNotification | None:
    row = (
        db.query(TechNotification)
        .filter(
            TechNotification.id == notification_id,
            TechNotification.recipient_id == recipient_id,
        )
        .first()
    )
    if row is None:
        return None
    row.is_read = True
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def mark_all_read(db: Session, recipient_id: int) -> int:
    rows = (
        db.query(TechNotification)
        .filter(
            TechNotification.recipient_id == recipient_id,
            TechNotification.is_read.is_(False),
        )
        .all()
    )
    for row in rows:
        row.is_read = True
        db.add(row)
    if rows:
        db.commit()
    return len(rows)


def mark_read_for_scan(db: Session, scan_id: int) -> None:
    rows = (
        db.query(TechNotification)
        .filter(
            TechNotification.scan_id == scan_id,
            TechNotification.is_read.is_(False),
        )
        .all()
    )
    for row in rows:
        row.is_read = True
        db.add(row)
    if rows:
        db.commit()
