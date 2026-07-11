"""ETL Open-Meteo → PostgreSQL."""

from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.climate.config import ETL_LAST_RUN_JSON
from app.climate.openmeteo_client import fetch_historico, fetch_realtime, merge_datasets
from app.climate.openmeteo_transform import aggregate_clima
from app.climate.repository import load_aggregates


def _save_etl_state(started: datetime, elapsed: float, success: bool, error: str | None = None) -> None:
    ETL_LAST_RUN_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "started_at": started.isoformat(timespec="seconds"),
        "finished_at": datetime.now().isoformat(timespec="seconds"),
        "success": success,
        "elapsed_s": round(elapsed, 1),
        "error": error,
    }
    ETL_LAST_RUN_JSON.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def run_climate_etl(db: Session, force_historic: bool = False) -> float:
    started = datetime.now()
    historico = fetch_historico(force=force_historic)
    realtime = fetch_realtime()
    merged = merge_datasets(historico, realtime)
    diario, semanal, mensual = aggregate_clima(merged)
    load_aggregates(db, diario, semanal, mensual)
    elapsed = (datetime.now() - started).total_seconds()
    _save_etl_state(started, elapsed, success=True)
    return elapsed
