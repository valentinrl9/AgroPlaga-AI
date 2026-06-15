import random
from typing import TYPE_CHECKING

from geoalchemy2.elements import WKTElement
from sqlalchemy import func
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from app.models.zone import AgriZone

# ~150–400 m de jitter en grados (aprox. Poniente Almeriense)
_JITTER_MIN_DEG = 0.0015
_JITTER_MAX_DEG = 0.0040


def apply_jitter(lon: float, lat: float) -> tuple[float, float]:
    jitter_lon = random.uniform(-_JITTER_MAX_DEG, _JITTER_MAX_DEG)
    jitter_lat = random.uniform(-_JITTER_MIN_DEG, _JITTER_MIN_DEG)
    if abs(jitter_lon) < _JITTER_MIN_DEG:
        jitter_lon = _JITTER_MIN_DEG if jitter_lon >= 0 else -_JITTER_MIN_DEG
    if abs(jitter_lat) < _JITTER_MIN_DEG:
        jitter_lat = _JITTER_MIN_DEG if jitter_lat >= 0 else -_JITTER_MIN_DEG
    return lon + jitter_lon, lat + jitter_lat


def point_wkt(lon: float, lat: float) -> WKTElement:
    return WKTElement(f"POINT({lon} {lat})", srid=4326)


def get_zone_centroid(db: Session, zone_id: int) -> tuple[float, float] | None:
    from app.models.zone import AgriZone

    row = (
        db.query(
            func.ST_X(AgriZone.centroid).label("lon"),
            func.ST_Y(AgriZone.centroid).label("lat"),
        )
        .filter(AgriZone.id == zone_id)
        .first()
    )
    if row is None:
        return None
    return float(row.lon), float(row.lat)


def event_geom_for_zone(db: Session, zone_id: int) -> WKTElement | None:
    centroid = get_zone_centroid(db, zone_id)
    if centroid is None:
        return None
    lon, lat = apply_jitter(*centroid)
    return point_wkt(lon, lat)
