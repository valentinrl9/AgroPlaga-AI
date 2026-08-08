"""Catálogo de cultivos MAPA + variantes comunes en Almería."""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path

_CATALOG_CANDIDATES = (
    Path(__file__).resolve().parent / "crop_catalog.json",
    Path(__file__).resolve().parents[3] / "shared" / "crop_catalog.json",
    Path("/shared/crop_catalog.json"),
)


def _catalog_path() -> Path:
    for path in _CATALOG_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("crop_catalog.json no encontrado (shared/ ni backend/app/data/)")


def load_catalog() -> dict:
    return json.loads(_catalog_path().read_text(encoding="utf-8"))


def _strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize_crop(value: str) -> str:
    return _strip_accents(value.strip().lower())


def catalog_entries() -> list[dict]:
    return load_catalog()["crops"]


def search_crops(query: str | None = None, limit: int = 20) -> list[dict]:
    entries = catalog_entries()
    if not query or not query.strip():
        return entries[:limit]

    needle = normalize_crop(query)
    scored: list[tuple[int, dict]] = []
    for entry in entries:
        haystack = {normalize_crop(entry["name"]), normalize_crop(entry["id"])}
        haystack.update(normalize_crop(alias) for alias in entry.get("aliases", []))
        if any(needle in token for token in haystack):
            rank = 0 if any(token.startswith(needle) for token in haystack) else 1
            scored.append((rank, entry))

    scored.sort(key=lambda item: (item[0], item[1]["name"].lower()))
    return [entry for _, entry in scored[:limit]]


def resolve_crop_name(value: str) -> str | None:
    normalized = normalize_crop(value)
    for entry in catalog_entries():
        tokens = {normalize_crop(entry["name"]), normalize_crop(entry["id"])}
        tokens.update(normalize_crop(alias) for alias in entry.get("aliases", []))
        if normalized in tokens:
            return entry["name"]
    return None
