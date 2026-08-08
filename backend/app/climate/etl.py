"""ETL Open-Meteo → PostgreSQL (multi-estación)."""

from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.climate.config import ETL_LAST_RUN_JSON, station_csv_paths
from app.climate.openmeteo_client import (
    _ensure_legacy_files_for_poniente,
    fetch_historico,
    fetch_realtime,
    merge_datasets,
)
from app.climate.openmeteo_transform import aggregate_clima
from app.climate.repository import load_aggregates
from app.climate.stations import list_active_stations
from app.models.climate_station import ClimateStation


def _save_etl_state(
    started: datetime,
    elapsed: float,
    success: bool,
    stations_processed: int,
    error: str | None = None,
) -> None:
    ETL_LAST_RUN_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "started_at": started.isoformat(timespec="seconds"),
        "finished_at": datetime.now().isoformat(timespec="seconds"),
        "success": success,
        "elapsed_s": round(elapsed, 1),
        "stations_processed": stations_processed,
        "error": error,
    }
    ETL_LAST_RUN_JSON.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def run_station_etl(db: Session, station: ClimateStation, force_historic: bool = False) -> float:
    started = datetime.now()
    paths = station_csv_paths(station.slug)
    if station.slug == "poniente":
        _ensure_legacy_files_for_poniente()

    historico = fetch_historico(station.lat, station.lon, paths=paths, force=force_historic)
    realtime = fetch_realtime(station.lat, station.lon, paths=paths)
    merged = merge_datasets(historico, realtime, paths=paths)
    diario, semanal, mensual = aggregate_clima(merged)
    load_aggregates(db, station.id, diario, semanal, mensual)
    return (datetime.now() - started).total_seconds()


def run_climate_etl(db: Session, force_historic: bool = False) -> float:
    started = datetime.now()
    stations = list_active_stations(db)
    if not stations:
        raise RuntimeError("No hay estaciones Climate activas")

    for station in stations:
        run_station_etl(db, station, force_historic=force_historic)

    elapsed = (datetime.now() - started).total_seconds()
    _save_etl_state(started, elapsed, success=True, stations_processed=len(stations))
    return elapsed
