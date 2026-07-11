"""Configuración del módulo NEXO Climate."""

import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_DATA = _ROOT / "data" / "climate"

DATA_DIR = Path(os.getenv("CLIMATE_DATA_DIR", str(_DEFAULT_DATA)))
HISTORICO_CSV = DATA_DIR / "openmeteo_historico.csv"
REALTIME_CSV = DATA_DIR / "openmeteo_realtime.csv"
DATASET_FINAL_CSV = DATA_DIR / "openmeteo_dataset_final.csv"
ETL_LAST_RUN_JSON = DATA_DIR / "etl_last_run.json"

ETL_INTERVAL_SECONDS = int(os.getenv("CLIMATE_ETL_INTERVAL_SECONDS", "900"))
LAT = float(os.getenv("OPENMETEO_LAT", "36.77"))
LON = float(os.getenv("OPENMETEO_LON", "-2.81"))
HISTORICO_START = os.getenv("OPENMETEO_HISTORICO_START", "2020-01-01")
DEFAULT_PRESSURE_HPA = float(os.getenv("DEFAULT_PRESSURE_HPA", "1013.25"))
CLIMATE_PREVIEW_OPEN = os.getenv("CLIMATE_PREVIEW_OPEN", "true").strip().lower() in ("1", "true", "yes")
