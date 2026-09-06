#!/usr/bin/env python3
"""
Importa datasets Roboflow Universe -> recortes clasificacion en ml/extra_data/{label}/.

Roboflow exporta detección (YOLO). Este script recorta cada bounding box y guarda
JPEG con prefijo roboflow_{proyecto}_ para entrenar PlagaScan en modo --roboflow-only.

Uso:
  # Descargar proyecto público (clave gratis en https://app.roboflow.com/settings/api)
  set ROBOFLOW_API_KEY=tu_clave
  python ml/scripts/import_roboflow.py --project tomato-pest

  # Varios proyectos del catálogo
  python ml/scripts/import_roboflow.py --all-catalog --max-per-class 80

  # ZIP/carpeta exportada manualmente desde Roboflow (formato YOLOv8)
  python ml/scripts/import_roboflow.py --source-dir ml/datasets/roboflow/tomato-pest --project-id tomato-pest

  # Auditar sin importar
  python ml/scripts/import_roboflow.py --source-dir ... --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image

ML_DIR = Path(__file__).resolve().parents[1]
ROOT = ML_DIR.parent
EXTRA_DIR = ML_DIR / "extra_data"
DATASETS_DIR = ML_DIR / "datasets" / "roboflow"
CATALOG_FILE = DATASETS_DIR / "catalog.json"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

sys.path.insert(0, str(ML_DIR))
from dataset_mappings import map_roboflow_class  # noqa: E402
from plague_catalog import LABELS  # noqa: E402

MIN_CROP_PX = 48
PAD_RATIO = 0.08


def _ensure_label_dirs() -> None:
    for label in LABELS:
        (EXTRA_DIR / label).mkdir(parents=True, exist_ok=True)


def _load_catalog() -> dict:
    return json.loads(CATALOG_FILE.read_text(encoding="utf-8"))


def _load_api_key() -> str:
    key = os.environ.get("ROBOFLOW_API_KEY", "").strip()
    if key:
        return key
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("ROBOFLOW_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def _ensure_roboflow_sdk() -> None:
    try:
        import roboflow  # noqa: F401
    except ImportError:
        print("Instalando roboflow...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "roboflow", "-q"])


def download_project(entry: dict, dest: Path, api_key: str) -> Path:
    _ensure_roboflow_sdk()
    from roboflow import Roboflow

    workspace = entry["workspace"]
    project_slug = entry["project"]
    version = int(entry.get("version", 1))
    fmt = entry.get("format", "yolov8")

    dest.mkdir(parents=True, exist_ok=True)
    has_data = any(dest.rglob("data.yaml"))
    if has_data and any(dest.rglob("images")):
        print(f"  Ya descargado en {dest}")
        return dest

    print(f"  Descargando {workspace}/{project_slug} v{version} ({fmt})...")
    rf = Roboflow(api_key=api_key)
    project = rf.workspace(workspace).project(project_slug)
    dataset = project.version(version).download(
        model_format=fmt,
        location=str(dest),
        overwrite=not has_data,
    )
    location = Path(getattr(dataset, "location", dest))
    if not any(location.rglob("data.yaml")):
        for child in location.iterdir():
            if child.is_dir() and any(child.rglob("data.yaml")):
                return child
    return location


def _parse_data_yaml(root: Path) -> list[str]:
    yaml_path = next(root.rglob("data.yaml"), None)
    if yaml_path is None:
        return []

    names: list[str] = []
    in_names = False
    for line in yaml_path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("names:"):
            inline = stripped.split(":", 1)[1].strip()
            if inline.startswith("["):
                try:
                    names = json.loads(inline.replace("'", '"'))
                except json.JSONDecodeError:
                    pass
            in_names = True
            continue
        if in_names:
            if stripped.startswith("- "):
                names.append(stripped[2:].strip().strip('"').strip("'"))
            elif re.match(r"^\d+:", stripped):
                names.append(stripped.split(":", 1)[1].strip().strip('"').strip("'"))
            elif stripped and not stripped.startswith("#"):
                in_names = False
    return names


def _find_image_label_pairs(root: Path) -> list[tuple[Path, Path | None, str]]:
    """Devuelve (imagen, etiqueta_yolo|None, split) por cada imagen."""
    pairs: list[tuple[Path, Path | None, str]] = []
    for images_dir in root.rglob("images"):
        if not images_dir.is_dir():
            continue
        split = images_dir.parent.name
        labels_dir = images_dir.parent / "labels"
        for img_path in sorted(images_dir.iterdir()):
            if img_path.suffix.lower() not in IMAGE_EXTS:
                continue
            label_path = labels_dir / f"{img_path.stem}.txt" if labels_dir.exists() else None
            if label_path is not None and not label_path.exists():
                label_path = None
            pairs.append((img_path, label_path, split))

    if pairs:
        return pairs

    # Clasificación por carpetas: train/clase/img.jpg
    for split in ("train", "valid", "test", "val"):
        split_dir = root / split
        if not split_dir.is_dir():
            continue
        for class_dir in split_dir.iterdir():
            if not class_dir.is_dir() or class_dir.name in {"images", "labels"}:
                continue
            for img_path in class_dir.rglob("*"):
                if img_path.is_file() and img_path.suffix.lower() in IMAGE_EXTS:
                    pairs.append((img_path, None, split))
    return pairs


def _yolo_to_box(line: str, width: int, height: int) -> tuple[int, int, int, int] | None:
    parts = line.split()
    if len(parts) < 5:
        return None
    try:
        _, xc, yc, bw, bh = parts[:5]
        xc_f, yc_f, bw_f, bh_f = float(xc), float(yc), float(bw), float(bh)
    except ValueError:
        return None

    x1 = int((xc_f - bw_f / 2) * width)
    y1 = int((yc_f - bh_f / 2) * height)
    x2 = int((xc_f + bw_f / 2) * width)
    y2 = int((yc_f + bh_f / 2) * height)

    pad_x = int((x2 - x1) * PAD_RATIO)
    pad_y = int((y2 - y1) * PAD_RATIO)
    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(width, x2 + pad_x)
    y2 = min(height, y2 + pad_y)
    if x2 - x1 < MIN_CROP_PX or y2 - y1 < MIN_CROP_PX:
        return None
    return x1, y1, x2, y2


def import_yolo_dataset(
    root: Path,
    project_id: str,
    *,
    max_per_class: int,
    dry_run: bool,
    seed: int,
) -> dict[str, int | dict]:
    import random

    class_names = _parse_data_yaml(root)
    pairs = _find_image_label_pairs(root)
    if not pairs:
        raise RuntimeError(f"No se encontraron imágenes/labels en {root}")

    counts: dict[str, int] = defaultdict(int)
    skipped_class: dict[str, int] = defaultdict(int)
    imported = 0
    rng = random.Random(seed)

    stats = {
        "project_id": project_id,
        "images_seen": len(pairs),
        "class_names": class_names,
        "imported": 0,
        "per_class": {},
        "skipped_unmapped": dict(skipped_class),
    }

    rng.shuffle(pairs)
    for img_path, label_path, split in pairs:
        try:
            image = Image.open(img_path).convert("RGB")
        except OSError:
            continue
        width, height = image.size

        crops: list[tuple[Image.Image, str]] = []

        if label_path and label_path.exists():
            for line in label_path.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                cls_id = int(parts[0])
                raw_name = class_names[cls_id] if cls_id < len(class_names) else str(cls_id)
                label = map_roboflow_class(raw_name)
                if label is None:
                    skipped_class[raw_name] += 1
                    continue
                box = _yolo_to_box(line, width, height)
                if box is None:
                    continue
                crops.append((image.crop(box), label))
        else:
            # Carpeta = nombre de clase
            raw_name = img_path.parent.name
            label = map_roboflow_class(raw_name)
            if label is None:
                skipped_class[raw_name] += 1
                continue
            crops.append((image, label))

        for crop, label in crops:
            if counts[label] >= max_per_class:
                continue
            stem = f"roboflow_{project_id}_{split}_{img_path.stem}_{counts[label]:04d}"
            dest = EXTRA_DIR / label / f"{stem}.jpg"
            if dest.exists():
                continue
            if dry_run:
                counts[label] += 1
                imported += 1
                continue
            crop.save(dest, format="JPEG", quality=92)
            counts[label] += 1
            imported += 1

    stats["imported"] = imported
    stats["per_class"] = dict(counts)
    stats["skipped_unmapped"] = dict(skipped_class)
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Importar Roboflow Universe a extra_data/")
    parser.add_argument("--project", action="append", help="ID del catálogo (ej. tomato-pest)")
    parser.add_argument("--all-catalog", action="store_true", help="Importar todos los proyectos del catálogo")
    parser.add_argument(
        "--source-dir",
        type=Path,
        help="Carpeta o ZIP ya exportado (YOLOv8). Requiere --project-id",
    )
    parser.add_argument("--project-id", type=str, default="manual", help="Prefijo roboflow_{id}_")
    parser.add_argument("--max-per-class", type=int, default=80)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    catalog = _load_catalog()
    by_id = {p["id"]: p for p in catalog.get("projects", [])}

    if args.all_catalog:
        project_ids = list(by_id)
    elif args.project:
        project_ids = args.project
    elif args.source_dir:
        project_ids = []
    else:
        project_ids = ["tomato-pest"]

    _ensure_label_dirs()
    all_stats: list[dict] = []

    if args.source_dir:
        source = args.source_dir.resolve()
        if source.suffix.lower() == ".zip":
            extract_dir = DATASETS_DIR / args.project_id
            extract_dir.mkdir(parents=True, exist_ok=True)
            import zipfile

            with zipfile.ZipFile(source, "r") as zf:
                zf.extractall(extract_dir)
            source = extract_dir
        stats = import_yolo_dataset(
            source,
            args.project_id,
            max_per_class=args.max_per_class,
            dry_run=args.dry_run,
            seed=args.seed,
        )
        all_stats.append(stats)
    else:
        api_key = _load_api_key()
        if not api_key:
            print(
                "ERROR: falta ROBOFLOW_API_KEY.\n"
                "  1. Regístrate en https://app.roboflow.com (gratis)\n"
                "  2. Copia la API key en .env: ROBOFLOW_API_KEY=...\n"
                "  3. O exporta YOLOv8 manualmente y usa --source-dir\n"
            )
            sys.exit(1)

        for pid in project_ids:
            entry = by_id.get(pid)
            if entry is None:
                print(f"Proyecto desconocido: {pid}")
                continue
            print(f"\n=== {pid} ({entry.get('url', '')}) ===")
            dest = DATASETS_DIR / pid
            try:
                download_project(entry, dest, api_key)
            except Exception as exc:
                print(f"  Falló descarga: {exc}")
                continue
            # Roboflow suele crear subcarpeta con el nombre del proyecto
            root = dest
            if not any(dest.rglob("data.yaml")):
                for child in dest.iterdir():
                    if child.is_dir() and any(child.rglob("data.yaml")):
                        root = child
                        break
            stats = import_yolo_dataset(
                root,
                pid,
                max_per_class=args.max_per_class,
                dry_run=args.dry_run,
                seed=args.seed,
            )
            all_stats.append(stats)

    print("\n=== Resumen import Roboflow ===")
    total = 0
    merged: dict[str, int] = defaultdict(int)
    for stats in all_stats:
        print(f"\n{stats['project_id']}: {stats['imported']} recortes")
        print(f"  Clases Roboflow: {stats.get('class_names')}")
        print(f"  Por etiqueta AgroPlaga: {stats.get('per_class')}")
        unmapped = stats.get("skipped_unmapped") or {}
        if unmapped:
            print(f"  Sin mapeo (omitidas): {unmapped}")
        total += int(stats["imported"])
        for label, count in (stats.get("per_class") or {}).items():
            merged[label] += count

    print(f"\nTotal importado: {total}")
    print(f"Agregado por clase: {dict(merged)}")
    if args.dry_run:
        print("(dry-run: no se escribieron archivos)")

    report_path = ML_DIR / "reports" / "roboflow_import.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps({"stats": all_stats, "total": total, "per_class": dict(merged)}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Informe: {report_path}")


if __name__ == "__main__":
    main()
