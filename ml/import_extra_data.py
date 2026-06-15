"""
Importa imágenes de PlantDoc (GitHub) e IP102 (manual) a ml/extra_data/.

Uso:
  python ml/import_extra_data.py --plantdoc
  python ml/import_extra_data.py --ip102 --ip102-dir ml/datasets/ip102
  python ml/import_extra_data.py --all --max-per-class 80

PlantDoc: descarga ZIP desde GitHub (CC BY 4.0).
IP102: descarga manual desde https://github.com/xpwu95/IP102 (Google Drive)
       y descomprime en ml/datasets/ip102/
"""

from __future__ import annotations

import argparse
import io
import random
import re
import shutil
import sys
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

ML_DIR = Path(__file__).resolve().parent
ROOT = ML_DIR.parent
EXTRA_DIR = ML_DIR / "extra_data"
DATASETS_DIR = ML_DIR / "datasets"
PLANTDOC_ZIP = "https://github.com/pratikkayal/PlantDoc-Dataset/archive/refs/heads/master.zip"
PLANTDOC_DIR = DATASETS_DIR / "plantdoc"
_WIN_INVALID = re.compile(r'[<>:"/\\|?*]')
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

sys.path.insert(0, str(ML_DIR))
from dataset_mappings import IP102_CLASS_TO_LABEL, PLANTDOC_TO_LABEL  # noqa: E402
from plague_catalog import LABELS  # noqa: E402


def _ensure_label_dirs() -> None:
    for label in LABELS:
        (EXTRA_DIR / label).mkdir(parents=True, exist_ok=True)


def _copy_image(src: Path, dest_dir: Path, prefix: str, counts: dict[str, int], max_per_class: int) -> bool:
    label = dest_dir.name
    if counts[label] >= max_per_class:
        return False
    dest = dest_dir / f"{prefix}{src.stem}{src.suffix.lower()}"
    if dest.exists():
        return False
    shutil.copy2(src, dest)
    counts[label] += 1
    return True


def _sanitize_path_part(name: str) -> str:
    return _WIN_INVALID.sub("_", name)


def download_plantdoc() -> Path:
    """Descarga ZIP de GitHub (evita fallos de git en Windows por '?' en nombres)."""
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    if PLANTDOC_DIR.exists() and (PLANTDOC_DIR / "train").exists():
        print(f"PlantDoc ya presente en {PLANTDOC_DIR}")
        return PLANTDOC_DIR

    print(f"Descargando PlantDoc -> {PLANTDOC_DIR} ...")
    if PLANTDOC_DIR.exists():
        shutil.rmtree(PLANTDOC_DIR)

    with urllib.request.urlopen(PLANTDOC_ZIP, timeout=120) as response:
        data = response.read()

    PLANTDOC_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            parts = Path(info.filename).parts
            if len(parts) < 3:
                continue
            # PlantDoc-Dataset-master/train/Class/file.jpg
            rel_parts = [_sanitize_path_part(p) for p in parts[1:]]
            dest = PLANTDOC_DIR.joinpath(*rel_parts)
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                dest.write_bytes(zf.read(info))
            except OSError:
                continue

    if not (PLANTDOC_DIR / "train").exists():
        raise RuntimeError("No se pudo extraer PlantDoc correctamente.")
    return PLANTDOC_DIR


def import_plantdoc(max_per_class: int, seed: int) -> dict[str, int]:
    plantdoc = download_plantdoc()
    counts: dict[str, int] = defaultdict(int)
    rng = random.Random(seed)
    imported = 0

    for split in ("train", "test"):
        split_dir = plantdoc / split
        if not split_dir.exists():
            continue
        for class_dir in sorted(split_dir.iterdir()):
            if not class_dir.is_dir():
                continue
            label = PLANTDOC_TO_LABEL.get(class_dir.name)
            if label is None:
                continue
            dest_dir = EXTRA_DIR / label
            images = [p for p in class_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS]
            rng.shuffle(images)
            for img in images:
                if _copy_image(img, dest_dir, "plantdoc_", counts, max_per_class):
                    imported += 1

    return dict(counts), imported


def _load_ip102_class_names() -> dict[int, str]:
    classes_file = DATASETS_DIR / "ip102" / "classes.txt"
    if not classes_file.exists():
        classes_file = ML_DIR.parent / "classes.txt"
    if classes_file.exists():
        lines = classes_file.read_text(encoding="utf-8").strip().splitlines()
        return {i + 1: line.strip() for i, line in enumerate(lines)}
    return {}


def _iter_ip102_images(ip102_dir: Path) -> list[tuple[Path, int]]:
    """Devuelve (ruta_imagen, class_id) desde varios layouts IP102."""
    pairs: list[tuple[Path, int]] = []

    for txt_name in ("train.txt", "val.txt", "test.txt"):
        txt_path = ip102_dir / txt_name
        if not txt_path.exists():
            continue
        for line in txt_path.read_text(encoding="utf-8").splitlines():
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            rel, class_id = parts[0], int(parts[-1])
            img_path = (ip102_dir / rel).resolve()
            if not img_path.exists():
                img_path = (ip102_dir / "images" / Path(rel).name).resolve()
            if img_path.exists():
                pairs.append((img_path, class_id))

    if pairs:
        return pairs

    for class_dir in sorted(ip102_dir.rglob("*")):
        if not class_dir.is_dir():
            continue
        name = class_dir.name
        if name.isdigit():
            class_id = int(name)
            for img in class_dir.iterdir():
                if img.suffix.lower() in IMAGE_EXTS:
                    pairs.append((img, class_id))

    if pairs:
        return pairs

    images_root = ip102_dir / "Images"
    if images_root.exists():
        for img in images_root.rglob("*"):
            if img.suffix.lower() not in IMAGE_EXTS:
                continue
            stem = img.stem
            if stem.isdigit():
                pairs.append((img, int(stem)))

    return pairs


def import_ip102(ip102_dir: Path, max_per_class: int, seed: int) -> tuple[dict[str, int], int]:
    if not ip102_dir.exists():
        raise FileNotFoundError(
            f"No se encontró {ip102_dir}.\n"
            "Descarga IP102 v1.1 desde https://github.com/xpwu95/IP102 (Google Drive)\n"
            "y descomprime en ml/datasets/ip102/ (debe incluir train.txt o carpetas por clase)."
        )

    classes_txt_dest = DATASETS_DIR / "ip102" / "classes.txt"
    if not classes_txt_dest.exists():
        repo_classes = ip102_dir / "classes.txt"
        if repo_classes.exists():
            shutil.copy2(repo_classes, classes_txt_dest)

    pairs = _iter_ip102_images(ip102_dir)
    if not pairs:
        raise RuntimeError(
            f"No se encontraron imágenes en {ip102_dir}. "
            "Estructura esperada: train.txt + images/ o carpetas numéricas por clase."
        )

    rng = random.Random(seed)
    rng.shuffle(pairs)
    counts: dict[str, int] = defaultdict(int)
    imported = 0
    class_names = _load_ip102_class_names()

    for img_path, class_id in pairs:
        label = IP102_CLASS_TO_LABEL.get(class_id)
        if label is None:
            continue
        dest_dir = EXTRA_DIR / label
        prefix = f"ip102_{class_id:03d}_"
        if _copy_image(img_path, dest_dir, prefix, counts, max_per_class):
            imported += 1

    skipped = sorted(set(range(1, 103)) - set(IP102_CLASS_TO_LABEL))
    print(f"IP102: mapeadas {len(IP102_CLASS_TO_LABEL)} de 102 clases hacia AgroPlaga.")
    if class_names:
        print("Clases IP102 importadas:")
        for cid, label in sorted(IP102_CLASS_TO_LABEL.items()):
            print(f"  {cid:3d} {class_names.get(cid, '?')[:40]:40} -> {label}")

    return dict(counts), imported


def print_summary(plantdoc_counts: dict[str, int], ip102_counts: dict[str, int], imported_total: int) -> None:
    merged: dict[str, int] = defaultdict(int)
    for d in (plantdoc_counts, ip102_counts):
        for k, v in d.items():
            merged[k] += v

    print("\n=== Resumen extra_data ===")
    for label in LABELS:
        n = merged.get(label, 0)
        bar = "#" * min(n // 5, 20)
        print(f"  {label:22} {n:4d}  {bar}")
    print(f"\nTotal imágenes nuevas copiadas: {imported_total}")
    print(f"Carpeta destino: {EXTRA_DIR}")
    print("\nSiguiente paso:")
    print("  python ml/train_plagascan.py --epochs 10 --max-per-class 150")


def main() -> None:
    parser = argparse.ArgumentParser(description="Importar PlantDoc/IP102 → ml/extra_data")
    parser.add_argument("--plantdoc", action="store_true", help="Importar desde PlantDoc (descarga ZIP)")
    parser.add_argument("--ip102", action="store_true", help="Importar desde IP102 local")
    parser.add_argument("--all", action="store_true", help="PlantDoc + IP102 si está disponible")
    parser.add_argument("--ip102-dir", type=Path, default=DATASETS_DIR / "ip102")
    parser.add_argument("--max-per-class", type=int, default=80)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if not (args.plantdoc or args.ip102 or args.all):
        parser.error("Indica --plantdoc, --ip102 o --all")

    _ensure_label_dirs()
    plantdoc_counts: dict[str, int] = {}
    ip102_counts: dict[str, int] = {}
    imported_total = 0

    if args.plantdoc or args.all:
        print("\n--- PlantDoc ---")
        plantdoc_counts, n = import_plantdoc(args.max_per_class, args.seed)
        imported_total += n
        print(f"PlantDoc: {n} imágenes copiadas.")

    if args.ip102 or args.all:
        print("\n--- IP102 ---")
        try:
            ip102_counts, n = import_ip102(args.ip102_dir.resolve(), args.max_per_class, args.seed)
            imported_total += n
            print(f"IP102: {n} imágenes copiadas.")
        except FileNotFoundError as exc:
            if args.all:
                print(f"IP102 omitido: {exc}")
            else:
                raise

    print_summary(plantdoc_counts, ip102_counts, imported_total)


if __name__ == "__main__":
    main()
