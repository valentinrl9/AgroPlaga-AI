"""Agregación por zona SIGPAC para mapa de calor."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.outbreak_event import OutbreakEvent
from app.models.zone import AgriZone

SEVERITY_WEIGHT = {1: 1.0, 2: 1.6, 3: 2.4}
VALIDATED_BOOST = 1.5
PENDING_WEIGHT = 0.35


def get_heatmap_grid(
    db: Session,
    plague: str | None = None,
    hours: int = 168,
    min_severity: int = 1,
    validated_only: bool = False,
) -> list[dict]:
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    weighted_count = func.sum(
        case(
            (OutbreakEvent.status == "validated", VALIDATED_BOOST),
            (OutbreakEvent.status == "pending", PENDING_WEIGHT),
            else_=0.0,
        )
    ).label("weighted_count")

    validated_count = func.sum(
        case((OutbreakEvent.status == "validated", 1), else_=0)
    ).label("validated_count")

    pending_count = func.sum(
        case((OutbreakEvent.status == "pending", 1), else_=0)
    ).label("pending_count")

    query = (
        db.query(
            AgriZone.id.label("zone_id"),
            AgriZone.sigpac_code,
            AgriZone.name.label("zone_name"),
            func.ST_Y(AgriZone.centroid).label("lat"),
            func.ST_X(AgriZone.centroid).label("lon"),
            func.count(OutbreakEvent.id).label("event_count"),
            func.max(OutbreakEvent.severity).label("max_severity"),
            weighted_count,
            validated_count,
            pending_count,
        )
        .join(OutbreakEvent, OutbreakEvent.zone_id == AgriZone.id)
        .filter(OutbreakEvent.reported_at >= since)
        .filter(OutbreakEvent.severity >= min_severity)
        .filter(OutbreakEvent.status != "rejected")
        .group_by(
            AgriZone.id,
            AgriZone.sigpac_code,
            AgriZone.name,
            AgriZone.centroid,
        )
    )

    if plague:
        query = query.filter(OutbreakEvent.plague == plague.strip().lower())
    if validated_only:
        query = query.filter(OutbreakEvent.status == "validated")

    rows = query.all()
    if not rows:
        return []

    scores = []
    for row in rows:
        weight = SEVERITY_WEIGHT.get(int(row.max_severity), 1.0)
        scores.append(float(row.weighted_count or 0) * weight)

    max_score = max(scores) if scores else 1.0

    cells = []
    for row, score in zip(rows, scores):
        validated = int(row.validated_count or 0)
        pending = int(row.pending_count or 0)
        cells.append(
            {
                "zone_id": row.zone_id,
                "sigpac_code": row.sigpac_code,
                "zone_name": row.zone_name,
                "lat": float(row.lat),
                "lon": float(row.lon),
                "count": int(row.event_count),
                "max_severity": int(row.max_severity),
                "intensity": round(score / max_score, 3) if max_score else 0.0,
                "validated_count": validated,
                "pending_count": pending,
            }
        )

    return sorted(cells, key=lambda cell: cell["intensity"], reverse=True)
