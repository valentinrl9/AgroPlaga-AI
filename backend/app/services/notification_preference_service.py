"""Preferencias push, horario quieto y anti-spam (Fase 5)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.models.user_notification_preference import NotificationPushLog, UserNotificationPreference

PILOT_TZ = ZoneInfo("Europe/Madrid")
PUSH_GROUP_WINDOW_MINUTES = 10
PUSH_GROUP_THRESHOLD = 2

PUSH_FIELD_BY_TYPE: dict[str, str] = {
    "scan_confirmed": "push_scan_validation",
    "scan_corrected": "push_scan_validation",
    "scan_rejected": "push_scan_validation",
    "incident_reminder": "push_incidents",
    "incident_carencia": "push_incidents",
    "incident_carencia_done": "push_carencia",
    "badge_earned": "push_badges",
    "weekly_vigilance": "push_weekly",
    "alert_comarcal": "push_alerts_comarcal",
    "scan_pending": "push_tech_pending",
}

CRITICAL_PUSH_TYPES = frozenset(
    {
        "scan_confirmed",
        "scan_corrected",
        "scan_rejected",
        "incident_carencia_done",
        "scan_pending",
    }
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def get_or_create_preferences(db: Session, user_id: int) -> UserNotificationPreference:
    row = db.query(UserNotificationPreference).filter(UserNotificationPreference.user_id == user_id).first()
    if row is not None:
        return row
    row = UserNotificationPreference(user_id=user_id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_preferences(db: Session, user_id: int, **fields) -> UserNotificationPreference:
    row = get_or_create_preferences(db, user_id)
    allowed = {
        "push_scan_validation",
        "push_incidents",
        "push_carencia",
        "push_alerts_comarcal",
        "push_badges",
        "push_weekly",
        "push_tech_pending",
        "quiet_hours_enabled",
        "quiet_hours_start",
        "quiet_hours_end",
    }
    for key, value in fields.items():
        if key not in allowed:
            continue
        if key in {"quiet_hours_start", "quiet_hours_end"}:
            hour = int(value)
            if 0 <= hour <= 23:
                setattr(row, key, hour)
            continue
        setattr(row, key, bool(value))
    row.updated_at = _now()
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def push_enabled_for_type(prefs: UserNotificationPreference, notification_type: str) -> bool:
    field = PUSH_FIELD_BY_TYPE.get(notification_type)
    if field is None:
        return True
    return bool(getattr(prefs, field, True))


def in_quiet_hours(prefs: UserNotificationPreference, now_local: datetime | None = None) -> bool:
    if not prefs.quiet_hours_enabled:
        return False
    local = now_local or datetime.now(PILOT_TZ)
    hour = local.hour
    start = prefs.quiet_hours_start
    end = prefs.quiet_hours_end
    if start == end:
        return False
    if start < end:
        return start <= hour < end
    return hour >= start or hour < end


def _recent_push_count(db: Session, user_id: int, *, minutes: int) -> int:
    since = _now() - timedelta(minutes=minutes)
    return (
        db.query(NotificationPushLog)
        .filter(
            NotificationPushLog.user_id == user_id,
            NotificationPushLog.sent_at >= since,
            NotificationPushLog.is_grouped.is_(False),
        )
        .count()
    )


def _has_recent_grouped_push(db: Session, user_id: int, *, minutes: int) -> bool:
    since = _now() - timedelta(minutes=minutes)
    return (
        db.query(NotificationPushLog.id)
        .filter(
            NotificationPushLog.user_id == user_id,
            NotificationPushLog.is_grouped.is_(True),
            NotificationPushLog.sent_at >= since,
        )
        .first()
        is not None
    )


def log_push(db: Session, user_id: int, notification_type: str | None, *, is_grouped: bool = False) -> None:
    db.add(
        NotificationPushLog(
            user_id=user_id,
            notification_type=notification_type,
            is_grouped=is_grouped,
        )
    )
    db.commit()


def should_send_push(
    db: Session,
    user_id: int,
    notification_type: str,
) -> tuple[bool, str | None]:
    """Devuelve (enviar, motivo_skip)."""
    prefs = get_or_create_preferences(db, user_id)
    if not push_enabled_for_type(prefs, notification_type):
        return False, "preference_disabled"
    if notification_type not in CRITICAL_PUSH_TYPES and in_quiet_hours(prefs):
        return False, "quiet_hours"
    return True, None


def maybe_group_push(
    db: Session,
    user_id: int,
    notification_type: str,
    unread_count: int,
) -> bool:
    """True si debe enviarse push agrupado en lugar del individual."""
    if notification_type in CRITICAL_PUSH_TYPES:
        return False
    if _recent_push_count(db, user_id, minutes=PUSH_GROUP_WINDOW_MINUTES) < PUSH_GROUP_THRESHOLD:
        return False
    return not _has_recent_grouped_push(db, user_id, minutes=PUSH_GROUP_WINDOW_MINUTES)
