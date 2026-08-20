#!/usr/bin/env python3
"""Actualiza centroides SIGPAC en PostgreSQL desde almeria_municipalities.json."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.db.init_db import seed_sigpac_zones  # noqa: E402


def main() -> None:
    seed_sigpac_zones()
    print("Centroides SIGPAC actualizados desde almeria_municipalities.json")


if __name__ == "__main__":
    main()
