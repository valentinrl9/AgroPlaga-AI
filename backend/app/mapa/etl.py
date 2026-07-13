"""ETL MAPA CEX → PostgreSQL."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.mapa.client import MapaClientError, fetch_cex_catalog
from app.mapa.config import CEX_CACHE_JSON, DATA_DIR, ETL_LAST_RUN_JSON
from app.mapa.repository import replace_mapa_catalog
from app.mapa.transform import transform_cex_productos


def _save_etl_state(
    *,
    started: datetime,
    elapsed: float,
    success: bool,
    products_total: int = 0,
    usos_indexed: int = 0,
    catalog_date: str | None = None,
    error: str | None = None,
) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "started_at": started.isoformat(timespec="seconds"),
        "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "success": success,
        "elapsed_s": round(elapsed, 1),
        "products_total": products_total,
        "usos_indexed": usos_indexed,
        "catalog_date": catalog_date,
        "source": "mapa_cex",
        "error": error,
    }
    ETL_LAST_RUN_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def get_etl_status() -> dict:
    if not ETL_LAST_RUN_JSON.exists():
        return {"success": None, "message": "ETL MAPA aún no ejecutado"}
    return json.loads(ETL_LAST_RUN_JSON.read_text(encoding="utf-8"))


def run_mapa_etl(db: Session, *, use_cache: bool = False) -> dict:
    started = datetime.now(timezone.utc)
    try:
        if use_cache and CEX_CACHE_JSON.exists():
            outer = json.loads(CEX_CACHE_JSON.read_text(encoding="utf-8"))
            if isinstance(outer, str):
                outer = json.loads(outer)
            inner = json.loads(outer["Contenido"])
            catalog = {
                "catalog_date": outer.get("Fecha"),
                "tipo": outer.get("Tipo"),
                "productos": inner["Productos"],
                "raw_bytes": CEX_CACHE_JSON.stat().st_size,
            }
        else:
            catalog = fetch_cex_catalog()
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            # Guardar caché local para reintentos / desarrollo offline
            cache_payload = {
                "Id": 0,
                "Tipo": catalog.get("tipo"),
                "Fecha": catalog.get("catalog_date"),
                "Contenido": json.dumps({"Productos": catalog["productos"]}, ensure_ascii=False),
            }
            CEX_CACHE_JSON.write_text(json.dumps(cache_payload, ensure_ascii=False), encoding="utf-8")

        rows = transform_cex_productos(catalog["productos"], synced_at=started)
        if not rows:
            raise MapaClientError("No se indexaron usos MAPA para el catálogo NEXO")

        indexed = replace_mapa_catalog(db, rows)
        elapsed = (datetime.now(timezone.utc) - started).total_seconds()
        _save_etl_state(
            started=started,
            elapsed=elapsed,
            success=True,
            products_total=len(catalog["productos"]),
            usos_indexed=indexed,
            catalog_date=str(catalog.get("catalog_date")),
        )
        return {
            "success": True,
            "elapsed_s": round(elapsed, 1),
            "products_total": len(catalog["productos"]),
            "usos_indexed": indexed,
            "catalog_date": catalog.get("catalog_date"),
            "catalog_tipo": catalog.get("tipo"),
        }
    except Exception as exc:
        elapsed = (datetime.now(timezone.utc) - started).total_seconds()
        _save_etl_state(started=started, elapsed=elapsed, success=False, error=str(exc))
        raise
