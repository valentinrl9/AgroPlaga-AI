#!/usr/bin/env python3
"""Copia imágenes de dataset_semilla → ml/extra_data/{label}/."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ML_DIR = Path(__file__).resolve().parents[1]
ROOT = ML_DIR.parent
sys.path.insert(0, str(ML_DIR))

from plague_catalog import LABELS  # noqa: E402

SEMILLA_DIR = ML_DIR / "dataset_semilla"
EXTRA_DIR = ML_DIR / "extra_data"
REGISTRY = SEMILLA_DIR / "plague_registry.json"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def main() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    label_set = set(LABELS)
    copied = 0
    skipped_class = 0
    skipped_exists = 0

    for entry in registry.get("plagues", []):
        label = entry["label_train"]
        if label not in label_set:
            skipped_class += 1
            print(f"Omitida clase fuera del catalogo v1.5: {entry['folder']} -> {label}")
            continue
        src_root = SEMILLA_DIR / entry["folder"]
        if not src_root.exists():
            continue
        dest_dir = EXTRA_DIR / label
        dest_dir.mkdir(parents=True, exist_ok=True)

        for path in sorted(src_root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            dest_name = f"semilla_{entry['folder']}_{path.parent.name}_{path.name}"
            dest_path = dest_dir / dest_name
            if dest_path.exists():
                skipped_exists += 1
                continue
            shutil.copy2(path, dest_path)
            copied += 1

    # Hojas sanas
    healthy_root = SEMILLA_DIR / "00_hojas_sanas"
    if healthy_root.exists():
        dest_dir = EXTRA_DIR / "sana"
        dest_dir.mkdir(parents=True, exist_ok=True)
        for path in sorted(healthy_root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            dest_name = f"semilla_hojas_sanas_{path.parent.name}_{path.name}"
            dest_path = dest_dir / dest_name
            if dest_path.exists():
                skipped_exists += 1
                continue
            shutil.copy2(path, dest_path)
            copied += 1

    print(f"Copiadas: {copied}")
    print(f"Ya existían: {skipped_exists}")
    print(f"Carpetas omitidas (clase v2): {skipped_class}")


if __name__ == "__main__":
    main()
