"""Insignias, ranking, vigilancia semanal y racha."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import Integer, cast, func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.feedback import Feedback
from app.models.outbreak_event import OutbreakEvent
from app.models.scan import Scan
from app.models.user import User
from app.models.user_badge import UserBadge
from app.models.zone import AgriZone

BADGE_CATALOG: dict[str, str] = {
    "first_contribution": "Primera contribución",
    "contributor_5": "Colaborador activo",
    "contributor_25": "Guardián de zona",
    "weekly_vigilance": "Vigilancia semanal",
    "weekly_challenge": "Reto semanal (antiguo)",
    "feedback_helper": "Ayuda a mejorar la IA",
    "validator_10": "Técnico validador",
}

WEEKLY_SCAN_GOAL = 1


def _week_start() -> datetime:
    now = datetime.now(timezone.utc)
    return now - timedelta(days=now.weekday())


def _badge_label(code: str) -> str:
    if code.startswith("weekly_vigilance_") and "_W" in code:
        week_part = code.rsplit("_W", 1)[-1]
        return f"Vigilante semana {week_part.lstrip('0') or week_part}"
    return BADGE_CATALOG.get(code, code.replace("_", " ").title())


def _award_badge(
    db: Session,
    user_id: int,
    badge_code: str,
    *,
    custom_label: str | None = None,
    notify: bool = True,
) -> UserBadge | None:
    exists = (
        db.query(UserBadge)
        .filter(UserBadge.user_id == user_id, UserBadge.badge_code == badge_code)
        .first()
    )
    if exists:
        return None
    badge = UserBadge(user_id=user_id, badge_code=badge_code)
    db.add(badge)
    db.commit()
    db.refresh(badge)
    if notify:
        from app.services.user_notification_service import notify_badge_earned

        notify_badge_earned(db, user_id, badge_code, custom_label or _badge_label(badge_code))
    return badge


def _weekly_scans(db: Session, user_id: int) -> int:
    return (
        db.query(Scan)
        .filter(Scan.user_id == user_id, Scan.created_at >= _week_start())
        .count()
    )


def get_weekly_streak(db: Session, user_id: int) -> int:
    """Semanas consecutivas con al menos 1 escaneo."""
    now = datetime.now(timezone.utc)
    week_start = _week_start()
    current_has = _weekly_scans(db, user_id) >= WEEKLY_SCAN_GOAL
    offset = 0 if current_has else 1

    streak = 0
    for i in range(offset, 52):
        ws = week_start - timedelta(weeks=i)
        we = ws + timedelta(days=7)
        count = (
            db.query(Scan)
            .filter(
                Scan.user_id == user_id,
                Scan.created_at >= ws,
                Scan.created_at < we,
            )
            .count()
        )
        if count >= WEEKLY_SCAN_GOAL:
            streak += 1
        else:
            break
    return streak


def check_contribution_badges(db: Session, user: User) -> list[str]:
    earned: list[str] = []
    count = user.contribution_count or 0
    for minimum, code in [(1, "first_contribution"), (5, "contributor_5"), (25, "contributor_25")]:
        if count >= minimum and _award_badge(db, user.id, code):
            earned.append(code)
    return earned


def check_scan_badges(db: Session, user_id: int) -> list[str]:
    earned: list[str] = []
    if _weekly_scans(db, user_id) >= WEEKLY_SCAN_GOAL:
        now = datetime.now(timezone.utc)
        year, week, _ = now.isocalendar()
        weekly_code = f"weekly_vigilance_{year}_W{week:02d}"
        label = f"Vigilante semana {week}"
        if _award_badge(db, user_id, weekly_code, custom_label=label):
            earned.append(weekly_code)
        if _award_badge(db, user_id, "weekly_vigilance", notify=False):
            earned.append("weekly_vigilance")
    return earned


def check_feedback_badges(db: Session, user_id: int) -> list[str]:
    count = db.query(Feedback).filter(Feedback.user_id == user_id).count()
    earned: list[str] = []
    if count >= 1 and _award_badge(db, user_id, "feedback_helper"):
        earned.append("feedback_helper")
    return earned


def check_validator_badges(db: Session, validator_id: int) -> list[str]:
    validated_count = (
        db.query(func.count(OutbreakEvent.id))
        .filter(OutbreakEvent.validated_by_id == validator_id)
        .scalar()
        or 0
    )
    earned: list[str] = []
    if validated_count >= 10 and _award_badge(db, validator_id, "validator_10"):
        earned.append("validator_10")
    return earned


def get_user_badges(db: Session, user_id: int) -> list[dict]:
    rows = (
        db.query(UserBadge)
        .filter(UserBadge.user_id == user_id)
        .order_by(UserBadge.earned_at.desc())
        .all()
    )
    return [
        {
            "code": row.badge_code,
            "label": _badge_label(row.badge_code),
            "earned_at": row.earned_at,
        }
        for row in rows
    ]


def get_zone_ranking(db: Session, days: int = 7, limit: int = 10) -> list[dict]:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.query(
            AgriZone.id,
            AgriZone.name,
            func.count(OutbreakEvent.id).label("contributions"),
            func.sum(cast(OutbreakEvent.validated, Integer)).label("validated"),
        )
        .join(OutbreakEvent, OutbreakEvent.zone_id == AgriZone.id)
        .filter(OutbreakEvent.reported_at >= since)
        .group_by(AgriZone.id, AgriZone.name)
        .order_by(func.count(OutbreakEvent.id).desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "zone_id": row.id,
            "zone_name": row.name,
            "contributions": int(row.contributions),
            "validated_count": int(row.validated or 0),
        }
        for row in rows
    ]


def get_weekly_vigilance(db: Session, user: User) -> dict:
    now = datetime.now(timezone.utc)
    week_start = _week_start()
    week_end = week_start + timedelta(days=7)
    current = min(_weekly_scans(db, user.id), WEEKLY_SCAN_GOAL)
    return {
        "goal": WEEKLY_SCAN_GOAL,
        "current": current,
        "completed": current >= WEEKLY_SCAN_GOAL,
        "ends_at": week_end,
        "streak_weeks": get_weekly_streak(db, user.id),
        "description": (
            "Haz al menos 1 escaneo esta semana con PlagaScan "
            "(aunque la hoja esté sana). La vigilancia previene brotes."
        ),
    }


def get_pilot_collective_stats(db: Session) -> dict:
    since = datetime.now(timezone.utc) - timedelta(days=30)
    total_scans = db.query(Scan).count()
    active_farmers = (
        db.query(func.count(func.distinct(Scan.user_id)))
        .filter(Scan.created_at >= since)
        .scalar()
        or 0
    )
    return {
        "total_scans": int(total_scans),
        "active_farmers": int(active_farmers),
        "goal": settings.pilot_scan_goal,
    }
