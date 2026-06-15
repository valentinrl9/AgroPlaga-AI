from datetime import datetime

from sqlalchemy.orm import Session

from app.models.contribution_log import ContributionLog
from app.models.outbreak_event import OutbreakEvent
from app.models.user import User
from app.schemas.outbreak_event import OutbreakEventCreate
from app.services.gamification_service import check_contribution_badges, check_validator_badges
from app.services.geo_service import event_geom_for_zone
from app.services.spam_guard import assert_can_contribute


def create_anonymous_event(
    db: Session,
    data: OutbreakEventCreate,
    contributor_id: int | None = None,
) -> OutbreakEvent:
    if contributor_id is not None:
        assert_can_contribute(db, contributor_id, data.zone_id, data.plague)

    geom = event_geom_for_zone(db, data.zone_id)
    if geom is None:
        raise ValueError("Zona SIGPAC no encontrada")

    event = OutbreakEvent(
        plague=data.plague,
        severity=data.severity,
        zone_id=data.zone_id,
        geom=geom,
        model_version=data.model_version,
    )
    db.add(event)

    contributor: User | None = None
    if contributor_id is not None:
        contributor = db.query(User).filter(User.id == contributor_id).first()
        if contributor is not None:
            contributor.contribution_count = (contributor.contribution_count or 0) + 1
            db.add(contributor)
            db.add(
                ContributionLog(
                    user_id=contributor_id,
                    zone_id=data.zone_id,
                    plague=data.plague,
                )
            )

    db.commit()
    db.refresh(event)

    if contributor is not None:
        check_contribution_badges(db, contributor)

    return event


def validate_event(
    db: Session,
    event: OutbreakEvent,
    validator: User,
    validated: bool = True,
) -> OutbreakEvent:
    event.validated = validated
    event.validated_by_id = validator.id if validated else None
    event.validated_at = datetime.utcnow() if validated else None
    db.add(event)
    db.commit()
    db.refresh(event)

    if validated:
        check_validator_badges(db, validator.id)

    return event
