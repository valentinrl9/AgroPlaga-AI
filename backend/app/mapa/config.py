"""Configuración ETL MAPA."""

import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_DATA = _ROOT / "data" / "mapa"

DATA_DIR = Path(os.getenv("MAPA_DATA_DIR", str(_DEFAULT_DATA)))
ETL_LAST_RUN_JSON = DATA_DIR / "etl_last_run.json"
CEX_CACHE_JSON = DATA_DIR / "productos_autorizados.json"

MAPA_BASE_URL = os.getenv("MAPA_BASE_URL", "https://servicio.mapa.gob.es/regfiweb")
CEX_EXPORT_URL = f"{MAPA_BASE_URL}/Exportaciones/ExportJsonProductosAutorizados"
CEX_REFERER = f"{MAPA_BASE_URL}/Resumenes/Index"

# MAPA actualiza los viernes ~14:00; sincronizamos domingos 03:00 UTC
ETL_CRON_DAY = os.getenv("MAPA_ETL_CRON_DAY", "sun")
ETL_CRON_HOUR = int(os.getenv("MAPA_ETL_CRON_HOUR", "3"))

DEFAULT_CALDO_L_HA = float(os.getenv("MAPA_DEFAULT_CALDO_L_HA", "1000"))
HTTP_TIMEOUT_SECONDS = int(os.getenv("MAPA_HTTP_TIMEOUT_SECONDS", "300"))
USER_AGENT = os.getenv(
    "MAPA_ETL_USER_AGENT",
    "NEXO-Agro-ETL/1.0 (cuaderno digital; contacto@agroplaga-ai.farm)",
)
