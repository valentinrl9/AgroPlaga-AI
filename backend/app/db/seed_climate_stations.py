"""Upsert estaciones Climate sur de Almería vinculadas a municipios SIGPAC."""

import json
from pathlib import Path

from app.db.session import SessionLocal
from app.models.climate_station import ClimateStation
from app.models.zone import AgriZone

_DATA = Path(__file__).resolve().parent / "data" / "climate_stations_sur.json"


def load_climate_station_specs() -> list[dict]:
    return json.loads(_DATA.read_text(encoding="utf-8"))


def seed_climate_stations() -> None:
    specs = load_climate_station_specs()
    db = SessionLocal()
    try:
        for index, spec in enumerate(specs, start=1):
            zone = (
                db.query(AgriZone)
                .filter(AgriZone.name == spec["municipality"])
                .first()
            )
            existing = db.query(ClimateStation).filter(ClimateStation.slug == spec["slug"]).first()
            if existing:
                existing.name = spec["name"]
                existing.lat = spec["lat"]
                existing.lon = spec["lon"]
                existing.zone_id = zone.id if zone else existing.zone_id
                existing.active = True
            else:
                db.add(
                    ClimateStation(
                        id=index,
                        slug=spec["slug"],
                        name=spec["name"],
                        zone_id=zone.id if zone else None,
                        lat=spec["lat"],
                        lon=spec["lon"],
                        source="openmeteo",
                        active=True,
                    )
                )
        db.commit()
    finally:
        db.close()
