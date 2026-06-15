"""Agregaciones B2B para panel de cooperativas (rol tech/admin)."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import Integer, cast, func
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.outbreak_event import OutbreakEvent
from app.models.zone import AgriZone
from app.services.heatmap_service import get_heatmap_grid


def get_overview(db: Session, hours: int = 168) -> dict:
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    recent = db.query(OutbreakEvent).filter(OutbreakEvent.reported_at >= since)
    total_recent = recent.count()
    validated_recent = recent.filter(OutbreakEvent.validated.is_(True)).count()
    active_alerts = db.query(Alert).filter(Alert.active.is_(True)).count()
    active_zones = (
        db.query(func.count(func.distinct(OutbreakEvent.zone_id)))
        .filter(OutbreakEvent.reported_at >= since)
        .scalar()
        or 0
    )
    return {
        "hours": hours,
        "events_recent": total_recent,
        "validated_recent": validated_recent,
        "validation_rate": round(validated_recent / total_recent, 3) if total_recent else 0,
        "active_alerts": active_alerts,
        "active_zones": int(active_zones),
    }


def get_zone_comparison(db: Session, hours: int = 168) -> list[dict]:
    cells = get_heatmap_grid(db, hours=hours)
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    validated_by_zone = dict(
        db.query(
            OutbreakEvent.zone_id,
            func.sum(cast(OutbreakEvent.validated, Integer)),
        )
        .filter(OutbreakEvent.reported_at >= since)
        .group_by(OutbreakEvent.zone_id)
        .all()
    )
    return [
        {
            **cell,
            "validated_count": int(validated_by_zone.get(cell["zone_id"], 0) or 0),
        }
        for cell in cells
    ]


def get_timeline(db: Session, days: int = 30) -> list[dict]:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.query(
            func.date_trunc("day", OutbreakEvent.reported_at).label("day"),
            func.count(OutbreakEvent.id).label("count"),
        )
        .filter(OutbreakEvent.reported_at >= since)
        .group_by("day")
        .order_by("day")
        .all()
    )
    return [
        {"date": row.day.date().isoformat(), "count": int(row.count)}
        for row in rows
        if row.day is not None
    ]


def get_critical_alerts(db: Session, limit: int = 10) -> list[dict]:
    rows = (
        db.query(Alert, AgriZone.name)
        .outerjoin(AgriZone, Alert.zone_id == AgriZone.id)
        .filter(Alert.active.is_(True))
        .order_by(Alert.priority_score.desc().nullslast(), Alert.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": alert.id,
            "zone_id": alert.zone_id,
            "zone_name": zone_name,
            "plague": alert.plague,
            "alert_type": alert.alert_type,
            "description": alert.description,
            "priority_score": alert.priority_score,
            "created_at": alert.created_at,
        }
        for alert, zone_name in rows
    ]


def build_events_csv(db: Session, hours: int = 720) -> str:
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    rows = (
        db.query(OutbreakEvent, AgriZone.name, AgriZone.sigpac_code)
        .join(AgriZone, OutbreakEvent.zone_id == AgriZone.id)
        .filter(OutbreakEvent.reported_at >= since)
        .order_by(OutbreakEvent.reported_at.desc())
        .all()
    )
    lines = ["fecha,zona,sigpac,plaga,severidad,validado,modelo"]
    for event, zone_name, sigpac in rows:
        lines.append(
            ",".join(
                [
                    event.reported_at.isoformat(),
                    _csv_escape(zone_name),
                    sigpac,
                    event.plague,
                    str(event.severity),
                    "si" if event.validated else "no",
                    event.model_version,
                ]
            )
        )
    return "\n".join(lines)


def _csv_escape(value: str) -> str:
    if "," in value or '"' in value:
        return f'"{value.replace(chr(34), chr(34) * 2)}"'
    return value
