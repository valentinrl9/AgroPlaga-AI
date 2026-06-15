"""Anti-spam: límites de contribución por usuario."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.contribution_log import ContributionLog

MAX_EVENTS_PER_HOUR = 5
MAX_SAME_ZONE_PLAGUE_PER_DAY = 2


def assert_can_contribute(db: Session, user_id: int, zone_id: int, plague: str) -> None:
    now = datetime.now(timezone.utc)
    hour_ago = now - timedelta(hours=1)
    day_ago = now - timedelta(hours=24)
    plague = plague.strip().lower()

    recent_count = (
        db.query(ContributionLog)
        .filter(
            ContributionLog.user_id == user_id,
            ContributionLog.created_at >= hour_ago,
        )
        .count()
    )
    if recent_count >= MAX_EVENTS_PER_HOUR:
        raise ValueError(
            f"Límite de {MAX_EVENTS_PER_HOUR} contribuciones por hora. Inténtalo más tarde."
        )

    same_combo = (
        db.query(ContributionLog)
        .filter(
            ContributionLog.user_id == user_id,
            ContributionLog.created_at >= day_ago,
            ContributionLog.zone_id == zone_id,
            ContributionLog.plague == plague,
        )
        .count()
    )
    if same_combo >= MAX_SAME_ZONE_PLAGUE_PER_DAY:
        raise ValueError(
            f"Ya reportaste {plague} en esta zona {MAX_SAME_ZONE_PLAGUE_PER_DAY} veces hoy."
        )
