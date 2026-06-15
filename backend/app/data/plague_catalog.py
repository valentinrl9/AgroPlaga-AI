"""Catálogo de 15 plagas prioritarias del Poniente Almeriense."""

from __future__ import annotations

import json
from pathlib import Path

_CATALOG_PATH = Path(__file__).resolve().parents[3] / "shared" / "plague_catalog.json"


def load_catalog() -> dict:
    return json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))


def plague_labels() -> list[str]:
    return load_catalog()["labels"]


def normalize_plague(name: str) -> str:
    return name.strip().lower()


def is_known_plague(name: str) -> bool:
    return normalize_plague(name) in {normalize_plague(label) for label in plague_labels()}


def catalog_entries() -> list[dict]:
    return load_catalog()["plagues"]
