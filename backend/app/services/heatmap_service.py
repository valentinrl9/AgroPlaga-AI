"""Agregación por zona SIGPAC para mapa de calor."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.outbreak_event import OutbreakEvent
from app.models.zone import AgriZone

SEVERITY_WEIGHT = {1: 1.0, 2: 1.6, 3: 2.4}
VALIDATED_BOOST = 1.5


def get_heatmap_grid(
    db: Session,
    plague: str | None = None,
    hours: int = 168,
    min_severity: int = 1,
) -> list[dict]:
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    weighted_count = func.sum(
        case((OutbreakEvent.validated.is_(True), VALIDATED_BOOST), else_=1.0)
    ).label("weighted_count")

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
        )
        .join(OutbreakEvent, OutbreakEvent.zone_id == AgriZone.id)
        .filter(OutbreakEvent.reported_at >= since)
        .filter(OutbreakEvent.severity >= min_severity)
        .group_by(
            AgriZone.id,
            AgriZone.sigpac_code,
            AgriZone.name,
            AgriZone.centroid,
        )
    )

    if plague:
        query = query.filter(OutbreakEvent.plague == plague.strip().lower())

    rows = query.all()
    if not rows:
        return []

    scores = []
    for row in rows:
        weight = SEVERITY_WEIGHT.get(int(row.max_severity), 1.0)
        scores.append(float(row.weighted_count) * weight)

    max_score = max(scores) if scores else 1.0

    cells = []
    for row, score in zip(rows, scores):
        cells.append(
            {
                "zone_id": row.zone_id,
                "sigpac_code": row.sigpac_code,
                "zone_name": row.zone_name,
                "lat": float(row.lat),
                "lon": float(row.lon),
                "count": int(row.event_count),
                "max_severity": int(row.max_severity),
                "intensity": round(score / max_score, 3),
            }
        )

    return sorted(cells, key=lambda cell: cell["intensity"], reverse=True)
