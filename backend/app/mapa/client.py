"""Cliente HTTP Registro Fitosanitarios MAPA."""

from __future__ import annotations

import json
from typing import Any

import requests

from app.mapa.config import CEX_EXPORT_URL, CEX_REFERER, HTTP_TIMEOUT_SECONDS, USER_AGENT


class MapaClientError(RuntimeError):
    pass


def fetch_cex_catalog() -> dict[str, Any]:
    """Descarga el JSON oficial para Cuaderno de Explotaciones (tipo CEX)."""
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    session.get(CEX_REFERER, timeout=60)

    response = session.post(
        CEX_EXPORT_URL,
        data={},
        headers={"Referer": CEX_REFERER},
        timeout=HTTP_TIMEOUT_SECONDS,
    )
    if response.status_code != 200 or not response.content:
        raise MapaClientError(
            f"MAPA CEX export falló: HTTP {response.status_code}, {len(response.content)} bytes"
        )

    try:
        payload = response.json()
    except json.JSONDecodeError as exc:
        raise MapaClientError("Respuesta MAPA no es JSON válido") from exc

    if isinstance(payload, str):
        payload = json.loads(payload)

    if not isinstance(payload, dict) or "Contenido" not in payload:
        raise MapaClientError("Estructura JSON MAPA inesperada (falta Contenido)")

    inner = payload["Contenido"]
    if isinstance(inner, str):
        inner = json.loads(inner)

    if not isinstance(inner, dict) or "Productos" not in inner:
        raise MapaClientError("Estructura JSON MAPA inesperada (falta Productos)")

    return {
        "catalog_date": payload.get("Fecha"),
        "tipo": payload.get("Tipo"),
        "productos": inner["Productos"],
        "raw_bytes": len(response.content),
    }
