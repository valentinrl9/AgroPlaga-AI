"""Catálogo de 15 plagas prioritarias del Poniente Almeriense."""

from __future__ import annotations

import json
from pathlib import Path

_CATALOG_CANDIDATES = (
    Path(__file__).resolve().parent / "plague_catalog.json",
    Path(__file__).resolve().parents[3] / "shared" / "plague_catalog.json",
    Path("/shared/plague_catalog.json"),
)


def _catalog_path() -> Path:
    for path in _CATALOG_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("plague_catalog.json no encontrado (shared/ ni backend/app/data/)")


def load_catalog() -> dict:
    return json.loads(_catalog_path().read_text(encoding="utf-8"))


def plague_labels() -> list[str]:
    return load_catalog()["labels"]


def normalize_plague(name: str) -> str:
    return name.strip().lower()


def is_known_plague(name: str) -> bool:
    return normalize_plague(name) in {normalize_plague(label) for label in plague_labels()}


def catalog_entries() -> list[dict]:
    return load_catalog()["plagues"]
