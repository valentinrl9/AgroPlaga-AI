"""Resolución de estaciones Climate por municipio / zona."""

from __future__ import annotations

import math

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.climate_station import ClimateStation
from app.models.zone import AgriZone


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _zone_lat_lon(db: Session, zone_id: int) -> tuple[float, float] | None:
    row = db.execute(
        text(
            "SELECT ST_Y(centroid::geometry) AS lat, ST_X(centroid::geometry) AS lon "
            "FROM agri_zones WHERE id = :zone_id"
        ),
        {"zone_id": zone_id},
    ).first()
    if row is None:
        return None
    return float(row.lat), float(row.lon)


def list_active_stations(db: Session) -> list[ClimateStation]:
    return (
        db.query(ClimateStation)
        .filter(ClimateStation.active.is_(True))
        .order_by(ClimateStation.id.asc())
        .all()
    )


def get_station(db: Session, station_id: int) -> ClimateStation | None:
    return db.query(ClimateStation).filter(ClimateStation.id == station_id).first()


def get_default_station(db: Session) -> ClimateStation:
    station = db.query(ClimateStation).filter(ClimateStation.slug == "poniente").first()
    if station is None:
        station = db.query(ClimateStation).order_by(ClimateStation.id.asc()).first()
    if station is None:
        raise RuntimeError("No hay estaciones Climate configuradas")
    return station


def resolve_station_with_override(
    db: Session,
    zone_id: int | None = None,
    station_id_override: int | None = None,
) -> tuple[ClimateStation, ClimateStation]:
    """Devuelve (estación activa, estación automática por proximidad)."""
    auto = resolve_station(db, zone_id)
    if station_id_override is None:
        return auto, auto
    manual = get_station(db, station_id_override)
    if manual is None or not manual.active:
        raise ValueError("Estación meteorológica no válida o inactiva")
    return manual, auto


def resolve_station(db: Session, zone_id: int | None = None) -> ClimateStation:
    if zone_id is not None:
        direct = (
            db.query(ClimateStation)
            .filter(ClimateStation.zone_id == zone_id, ClimateStation.active.is_(True))
            .first()
        )
        if direct is not None:
            return direct

        zone = db.query(AgriZone).filter(AgriZone.id == zone_id).first()
        if zone is not None:
            by_name = (
                db.query(ClimateStation)
                .join(AgriZone, ClimateStation.zone_id == AgriZone.id)
                .filter(AgriZone.name == zone.name, ClimateStation.active.is_(True))
                .first()
            )
            if by_name is not None:
                return by_name

            coords = _zone_lat_lon(db, zone_id)
            if coords is not None:
                lat, lon = coords
                stations = list_active_stations(db)
                if stations:
                    return min(stations, key=lambda s: _haversine_km(lat, lon, s.lat, s.lon))

    return get_default_station(db)


def station_to_dict(station: ClimateStation, zone_name: str | None = None) -> dict:
    return {
        "id": station.id,
        "slug": station.slug,
        "name": station.name,
        "zone_id": station.zone_id,
        "zone_name": zone_name,
        "lat": station.lat,
        "lon": station.lon,
        "source": station.source,
    }
