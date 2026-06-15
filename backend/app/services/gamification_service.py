"""Insignias, ranking y vigilancia semanal."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import Integer, cast, func
from sqlalchemy.orm import Session

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


def _award_badge(db: Session, user_id: int, badge_code: str) -> UserBadge | None:
    if badge_code not in BADGE_CATALOG:
        return None
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
    return badge


def _weekly_scans(db: Session, user_id: int) -> int:
    return (
        db.query(Scan)
        .filter(Scan.user_id == user_id, Scan.created_at >= _week_start())
        .count()
    )


def check_contribution_badges(db: Session, user: User) -> list[str]:
    earned: list[str] = []
    count = user.contribution_count or 0
    for minimum, code in [(1, "first_contribution"), (5, "contributor_5"), (25, "contributor_25")]:
        if count >= minimum and _award_badge(db, user.id, code):
            earned.append(code)
    return earned


def check_scan_badges(db: Session, user_id: int) -> list[str]:
    earned: list[str] = []
    if _weekly_scans(db, user_id) >= WEEKLY_SCAN_GOAL and _award_badge(db, user_id, "weekly_vigilance"):
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
            "label": BADGE_CATALOG.get(row.badge_code, row.badge_code),
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
        "description": (
            "Haz al menos 1 escaneo esta semana con PlagaScan "
            "(aunque la hoja esté sana). La vigilancia previene brotes."
        ),
    }
