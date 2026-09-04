"""Notificaciones in-app para agricultores (Fases 1–3, sin FCM)."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user_notification import NotificationReminderLog, UserNotification
from app.services.notification_service import send_push_to_user

SECTION_BY_TYPE: dict[str, str] = {
    "scan_confirmed": "history",
    "scan_corrected": "history",
    "scan_rejected": "history",
    "incident_reminder": "incidents",
    "incident_carencia": "incidents",
    "incident_carencia_done": "incidents",
    "weekly_vigilance": "community",
    "badge_earned": "community",
    "alert_comarcal": "alerts",
}

REMINDER_COOLDOWN_HOURS = 24
WEEKLY_REMINDER_COOLDOWN_DAYS = 6


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _notifications_enabled() -> bool:
    return settings.notifications_enabled


def _badge_label(code: str) -> str:
    if code.startswith("weekly_vigilance_"):
        parts = code.split("_W")
        if len(parts) == 2:
            return f"Vigilante semana {parts[1]}"
    return code.replace("_", " ").title()


def create_user_notification(
    db: Session,
    *,
    user_id: int,
    notification_type: str,
    title: str,
    body: str,
    section: str | None = None,
    reference_type: str | None = None,
    reference_id: int | None = None,
    dedupe_key: str | None = None,
    skip_dedupe: bool = False,
) -> UserNotification | None:
    if not _notifications_enabled():
        return None

    if dedupe_key and not skip_dedupe:
        recent = (
            db.query(UserNotification)
            .filter(
                UserNotification.user_id == user_id,
                UserNotification.dedupe_key == dedupe_key,
            )
            .order_by(UserNotification.created_at.desc())
            .first()
        )
        if recent is not None:
            return None

    row = UserNotification(
        user_id=user_id,
        notification_type=notification_type,
        section=section or SECTION_BY_TYPE.get(notification_type, "home"),
        title=title,
        body=body,
        reference_type=reference_type,
        reference_id=reference_id,
        dedupe_key=dedupe_key,
        is_read=False,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    send_push_to_user(user_id, title, body)
    return row


def _record_reminder_sent(db: Session, user_id: int, dedupe_key: str) -> bool:
    """Registra recordatorio si no existe. Devuelve True si es nuevo."""
    exists = (
        db.query(NotificationReminderLog)
        .filter(
            NotificationReminderLog.user_id == user_id,
            NotificationReminderLog.dedupe_key == dedupe_key,
        )
        .first()
    )
    if exists is not None:
        sent_at = exists.sent_at
        if sent_at.tzinfo is None:
            sent_at = sent_at.replace(tzinfo=timezone.utc)
        if _now() - sent_at < timedelta(hours=REMINDER_COOLDOWN_HOURS):
            return False
        exists.sent_at = _now()
        db.add(exists)
        db.commit()
        return True

    db.add(NotificationReminderLog(user_id=user_id, dedupe_key=dedupe_key))
    db.commit()
    return True


def notify_scan_validated(
    db: Session,
    *,
    farmer_id: int,
    scan_id: int,
    action: str,
    plague: str,
    corrected_plague: str | None = None,
) -> UserNotification | None:
    if action == "confirm":
        title = "Escaneo confirmado"
        body = f"Tu técnico confirmó: {plague}"
        ntype = "scan_confirmed"
    elif action == "correct":
        title = "Plaga corregida por técnico"
        body = f"Tu técnico indica: {corrected_plague or plague} (no {plague})"
        ntype = "scan_corrected"
    else:
        title = "Escaneo no válido"
        body = "Tu técnico no pudo validar la foto — repite el escaneo o consulta."
        ntype = "scan_rejected"

    return create_user_notification(
        db,
        user_id=farmer_id,
        notification_type=ntype,
        title=title,
        body=body,
        reference_type="scan",
        reference_id=scan_id,
        dedupe_key=f"scan_validated:{scan_id}:{action}",
        skip_dedupe=True,
    )


def notify_badge_earned(db: Session, user_id: int, badge_code: str, label: str | None = None) -> UserNotification | None:
    display = label or _badge_label(badge_code)
    return create_user_notification(
        db,
        user_id=user_id,
        notification_type="badge_earned",
        title="Nueva insignia",
        body=display,
        reference_type="badge",
        dedupe_key=f"badge:{badge_code}",
        skip_dedupe=True,
    )


def notify_incident_reminder(
    db: Session,
    *,
    user_id: int,
    incident_id: int,
    title: str,
    body: str,
    reminder_kind: str,
) -> UserNotification | None:
    dedupe_key = f"incident:{incident_id}:{reminder_kind}"
    if not _record_reminder_sent(db, user_id, dedupe_key):
        return None
    return create_user_notification(
        db,
        user_id=user_id,
        notification_type="incident_reminder",
        title=title,
        body=body,
        section="incidents",
        reference_type="incident",
        reference_id=incident_id,
        dedupe_key=dedupe_key,
        skip_dedupe=True,
    )


def notify_carencia_done(
    db: Session,
    *,
    user_id: int,
    incident_id: int,
    product_name: str,
) -> UserNotification | None:
    dedupe = f"carencia_done:{incident_id}"
    if not _record_reminder_sent(db, user_id, dedupe):
        return None
    return create_user_notification(
        db,
        user_id=user_id,
        notification_type="incident_carencia_done",
        title="Carencia cumplida",
        body=f"APTO PARA CORTE · {product_name}",
        section="incidents",
        reference_type="incident",
        reference_id=incident_id,
        dedupe_key=dedupe,
        skip_dedupe=True,
    )


def list_notifications(
    db: Session,
    user_id: int,
    *,
    unread_only: bool = False,
    limit: int = 50,
) -> list[UserNotification]:
    q = db.query(UserNotification).filter(UserNotification.user_id == user_id)
    if unread_only:
        q = q.filter(UserNotification.is_read.is_(False))
    return q.order_by(UserNotification.created_at.desc()).limit(limit).all()


def unread_count(db: Session, user_id: int) -> int:
    return (
        db.query(UserNotification)
        .filter(
            UserNotification.user_id == user_id,
            UserNotification.is_read.is_(False),
        )
        .count()
    )


def section_counts(db: Session, user_id: int) -> dict[str, int]:
    rows = (
        db.query(UserNotification.section, UserNotification.id)
        .filter(
            UserNotification.user_id == user_id,
            UserNotification.is_read.is_(False),
        )
        .all()
    )
    counts: dict[str, int] = {"history": 0, "incidents": 0, "community": 0, "alerts": 0, "home": 0}
    for section, _ in rows:
        key = section if section in counts else "home"
        counts[key] = counts.get(key, 0) + 1
    return counts


def mark_read(db: Session, notification_id: int, user_id: int) -> UserNotification | None:
    row = (
        db.query(UserNotification)
        .filter(
            UserNotification.id == notification_id,
            UserNotification.user_id == user_id,
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


def mark_all_read(db: Session, user_id: int) -> int:
    rows = (
        db.query(UserNotification)
        .filter(
            UserNotification.user_id == user_id,
            UserNotification.is_read.is_(False),
        )
        .all()
    )
    for row in rows:
        row.is_read = True
        db.add(row)
    if rows:
        db.commit()
    return len(rows)


def mark_section_read(db: Session, user_id: int, section: str) -> int:
    rows = (
        db.query(UserNotification)
        .filter(
            UserNotification.user_id == user_id,
            UserNotification.section == section,
            UserNotification.is_read.is_(False),
        )
        .all()
    )
    for row in rows:
        row.is_read = True
        db.add(row)
    if rows:
        db.commit()
    return len(rows)
