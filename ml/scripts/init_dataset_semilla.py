#!/usr/bin/env python3
"""Crea el árbol dataset_semilla/ a partir de plague_registry.json."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "dataset_semilla" / "plague_registry.json"
BASE = ROOT / "dataset_semilla"

META_TEMPLATE = {
    "label_train": "",
    "scientific": "",
    "eppo_code": "",
    "eppo_photos_url": "",
    "subfolders": {},
    "download_notes": "Solo uso educativo EPPO. Registrar fuente en manifest.csv.",
}


def main() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    healthy_crops = data["healthy_crops"]

    # Banco de hojas sanas (fondos para compositing)
    for crop in healthy_crops:
        (BASE / "00_hojas_sanas" / crop).mkdir(parents=True, exist_ok=True)
        _gitkeep(BASE / "00_hojas_sanas" / crop)

    (BASE / "00_hojas_sanas" / "_meta.json").write_text(
        json.dumps(
            {
                "purpose": "Fondos para pegar cromos y mezclas sintéticas",
                "crops": healthy_crops,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    for plague in data["plagues"]:
        folder = BASE / plague["folder"]
        eppo = plague["eppo_code"]
        url = data["eppo_photos_base"].format(eppo_code=eppo)
        meta = {
            **META_TEMPLATE,
            "label_train": plague["label_train"],
            "scientific": plague["scientific"],
            "eppo_code": eppo,
            "eppo_photos_url": url,
            "subfolders": {s: "Coloca aquí fotos EPPO filtradas por tag" for s in plague["subfolders"]},
        }
        if notes := plague.get("notes"):
            meta["notes"] = notes

        for sub in plague["subfolders"]:
            sub_path = folder / sub
            sub_path.mkdir(parents=True, exist_ok=True)
            _gitkeep(sub_path)

        (folder / "_meta.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    manifest = BASE / "manifest.csv"
    if not manifest.exists():
        manifest.write_text(
            "plague_folder,subfolder,filename,eppo_code,source_url,courtesy,tag_eppo,downloaded_at\n",
            encoding="utf-8",
        )

    print(f"OK: estructura creada en {BASE}")
    print(f"  Plagas: {len(data['plagues'])}")
    print(f"  Cultivos sanos: {len(healthy_crops)}")


def _gitkeep(path: Path) -> None:
    keep = path / ".gitkeep"
    if not keep.exists():
        keep.touch()


if __name__ == "__main__":
    main()
