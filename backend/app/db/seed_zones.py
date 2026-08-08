"""Municipios de la provincia de Almería (INE/SIGPAC)."""

from __future__ import annotations

import json
from pathlib import Path

_DATA_FILE = Path(__file__).resolve().parent / "data" / "almeria_municipalities.json"


def load_almeria_municipalities() -> list[dict]:
    return json.loads(_DATA_FILE.read_text(encoding="utf-8"))


# Compatibilidad con imports antiguos (Poniente).
SIGPAC_ZONES = load_almeria_municipalities()
