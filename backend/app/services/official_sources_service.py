"""Catálogo de fuentes oficiales (RAIF, MAPA, EPPO) para citar en recomendaciones y alertas."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = ROOT / "shared" / "official_sources.json"

KIND_LABELS = {
    "official_protocol": "Protocolo oficial",
    "official_bulletin": "Documento oficial",
    "official_registry": "Registro oficial",
    "community": "Dato comunitario AgroPlaga",
    "orientation": "Orientación AgroPlaga",
}


def _normalize(value: str | None) -> str:
    if not value:
        return ""
    return value.strip().lower().replace("ó", "o").replace("í", "i").replace("á", "a").replace("ú", "u").replace("ñ", "n")


def _matches_tags(entry_tags: list[str], value: str) -> bool:
    if not entry_tags or "*" in entry_tags:
        return True
    norm = _normalize(value)
    return any(_normalize(tag) == norm for tag in entry_tags)


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, Any]:
    if not CATALOG_PATH.exists():
        return {"version": "0", "sources": []}
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def resolve_official_sources(
    *,
    plague: str,
    crop: str | None = None,
    context: str = "recommendation",
    include_orientation: bool = True,
    include_community: bool = False,
) -> list[dict[str, Any]]:
    """Devuelve fuentes aplicables ordenadas: protocolos > boletines > registro > orientación."""
    catalog = load_catalog()
    plague_key = _normalize(plague)
    crop_key = _normalize(crop) if crop else ""

    priority = {
        "official_protocol": 0,
        "official_bulletin": 1,
        "official_registry": 2,
        "community": 3,
        "orientation": 4,
    }

    results: list[dict[str, Any]] = []
    for entry in catalog.get("sources", []):
        kind = entry.get("kind", "orientation")
        if kind == "orientation" and not include_orientation:
            continue
        if kind == "community" and not include_community:
            continue
        contexts = entry.get("contexts") or ["recommendation"]
        if context not in contexts:
            continue
        if not _matches_tags(entry.get("plagues") or [], plague_key):
            continue
        if crop_key and not _matches_tags(entry.get("crops") or [], crop_key):
            continue

        results.append(
            {
                "id": entry["id"],
                "kind": kind,
                "kind_label": KIND_LABELS.get(kind, kind),
                "issuer": entry.get("issuer", ""),
                "title": entry.get("title", ""),
                "url": entry.get("url"),
                "note": entry.get("note"),
            }
        )

    results.sort(key=lambda item: (priority.get(item["kind"], 99), item["title"]))
    return results


def format_official_attribution(sources: list[dict[str, Any]], *, fallback: str | None = None) -> str:
    """Texto corto para mostrar bajo recomendaciones: «Según información oficial de …»."""
    order = ("official_protocol", "official_bulletin", "official_registry")
    for kind in order:
        matches = [entry for entry in sources if entry.get("kind") == kind and (entry.get("issuer") or "").strip()]
        if not matches:
            continue
        preferred = next(
            (entry for entry in matches if "raif" in (entry.get("issuer") or "").lower()),
            matches[0],
        )
        issuer = preferred["issuer"].strip()
        return f"Según información oficial de {issuer}."
    if fallback:
        return fallback
    return "Orientación AgroPlaga. Confirma la acción con tu técnico o cooperativa."


def format_alert_attribution(sources: list[dict[str, Any]]) -> str:
    official = [
        s for s in sources if s.get("kind") in ("official_protocol", "official_bulletin", "official_registry")
    ]
    if official:
        preferred = next(
            (entry for entry in official if "raif" in (entry.get("issuer") or "").lower()),
            official[0],
        )
        issuer = preferred.get("issuer", "RAIF")
        return f"Para medidas oficiales en tu zona, consulta {issuer}."
    return "Alerta automática del mapa comunitario AgroPlaga (no emitida por RAIF)."
