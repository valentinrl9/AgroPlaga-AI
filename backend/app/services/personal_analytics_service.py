"""Analítica personal por usuario, cultivo y finca."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.farm import Farm
from app.models.outbreak_event import OutbreakEvent
from app.models.scan import Scan
from app.models.zone import AgriZone
from app.services.recommendation_service import _severity_level


def _since_days(days: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)


def get_user_summary(db: Session, user_id: int, days: int = 90) -> dict:
    since = _since_days(days)
    scan_list = db.query(Scan).filter(Scan.user_id == user_id, Scan.created_at >= since).all()
    total = len(scan_list)
    crops = (
        db.query(Scan.crop, func.count(Scan.id))
        .filter(Scan.user_id == user_id, Scan.created_at >= since)
        .group_by(Scan.crop)
        .order_by(func.count(Scan.id).desc())
        .all()
    )
    plagues = (
        db.query(Scan.plague, func.count(Scan.id))
        .filter(Scan.user_id == user_id, Scan.created_at >= since)
        .group_by(Scan.plague)
        .order_by(func.count(Scan.id).desc())
        .all()
    )
    high_severity = sum(1 for s in scan_list if _severity_level(s.severity) >= 3)

    return {
        "days": days,
        "total_scans": total,
        "high_severity_count": high_severity,
        "crops": [{"name": name, "count": int(count)} for name, count in crops],
        "plagues": [{"name": name, "count": int(count)} for name, count in plagues],
    }


def get_scan_timeline(db: Session, user_id: int, days: int = 90, crop: str | None = None, farm_id: int | None = None) -> list[dict]:
    since = _since_days(days)
    query = db.query(
        func.date_trunc("day", Scan.created_at).label("day"),
        func.count(Scan.id).label("count"),
    ).filter(Scan.user_id == user_id, Scan.created_at >= since)
    if crop:
        query = query.filter(Scan.crop == crop)
    if farm_id is not None:
        query = query.filter(Scan.farm_id == farm_id)
    rows = query.group_by("day").order_by("day").all()
    return [
        {"date": row.day.date().isoformat(), "count": int(row.count)}
        for row in rows
        if row.day is not None
    ]


def get_farm_breakdown(db: Session, user_id: int, days: int = 90) -> list[dict]:
    since = _since_days(days)
    rows = (
        db.query(
            Farm.id,
            Farm.name,
            Farm.crop,
            Farm.farm_type,
            func.count(Scan.id).label("scan_count"),
        )
        .outerjoin(Scan, (Scan.farm_id == Farm.id) & (Scan.created_at >= since))
        .filter(Farm.user_id == user_id)
        .group_by(Farm.id, Farm.name, Farm.crop, Farm.farm_type)
        .order_by(func.count(Scan.id).desc())
        .all()
    )
    return [
        {
            "farm_id": row.id,
            "name": row.name,
            "crop": row.crop,
            "farm_type": row.farm_type,
            "scan_count": int(row.scan_count or 0),
        }
        for row in rows
    ]


def get_zone_context(db: Session, zone_id: int, days: int = 30) -> dict | None:
    zone = db.query(AgriZone).filter(AgriZone.id == zone_id).first()
    if not zone:
        return None
    since = _since_days(days)
    events = (
        db.query(OutbreakEvent)
        .filter(OutbreakEvent.zone_id == zone_id, OutbreakEvent.reported_at >= since)
        .count()
    )
    top_plague = (
        db.query(OutbreakEvent.plague, func.count(OutbreakEvent.id))
        .filter(OutbreakEvent.zone_id == zone_id, OutbreakEvent.reported_at >= since)
        .group_by(OutbreakEvent.plague)
        .order_by(func.count(OutbreakEvent.id).desc())
        .first()
    )
    return {
        "zone_id": zone.id,
        "zone_name": zone.name,
        "sigpac_code": zone.sigpac_code,
        "events_recent": events,
        "top_plague": top_plague[0] if top_plague else None,
        "top_plague_count": int(top_plague[1]) if top_plague else 0,
    }
