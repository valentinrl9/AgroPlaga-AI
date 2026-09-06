"""
Importa datasets públicos (Mendeley, Zenodo) → ml/extra_data/{label}/.

Fuentes:
  - Mendeley s62zm6djd2: 8 plagas tomate (4263 img augmentadas)
  - Mendeley ysk546n9np: 6 plagas tomate (compilación 2026)
  - Zenodo TomatoEbola: daño tuta absoluta (si hay archivos publicados)

Uso:
  python ml/scripts/import_public_datasets.py --all
  python ml/scripts/import_public_datasets.py --mendeley8 --max-per-class 80
"""

from __future__ import annotations

import argparse
import io
import json
import re
import shutil
import sys
import urllib.error
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

ML_DIR = Path(__file__).resolve().parents[1]
DATASETS_DIR = ML_DIR / "datasets"
EXTRA_DIR = ML_DIR / "extra_data"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
USER_AGENT = "AgroPlaga-AI/1.0 (educational; ml/import_public_datasets)"

sys.path.insert(0, str(ML_DIR))
from dataset_mappings import MENDELEY8_TO_LABEL, MENDELEY6_TO_LABEL  # noqa: E402
from plague_catalog import LABELS  # noqa: E402

MENDELEY8_DATASET_ID = "s62zm6djd2"
MENDELEY6_DATASET_ID = "ysk546n9np"
ZENODO_TOMATOEBOLA_ID = "13324917"


def _ensure_dirs() -> None:
    for label in LABELS:
        (EXTRA_DIR / label).mkdir(parents=True, exist_ok=True)


def _download(url: str, dest: Path, timeout: int = 300) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        data = response.read()
    if len(data) < 2048:
        raise ValueError(f"Descarga demasiado pequeña ({len(data)} bytes): {url}")
    dest.write_bytes(data)


def _mendeley_file_urls(dataset_id: str) -> list[str]:
    """Intenta obtener URLs de descarga desde la página pública de Mendeley."""
    draft_url = f"https://data.mendeley.com/public-files/datasets/{dataset_id}/draft"
    req = urllib.request.Request(draft_url, headers={"User-Agent": USER_AGENT})
    try:
        html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Mendeley {dataset_id}: HTTP {exc.code}") from exc

    pattern = re.compile(
        rf"https://data\.mendeley\.com/public-files/datasets/{re.escape(dataset_id)}/files/[a-f0-9-]+/file_downloaded"
    )
    urls = list(dict.fromkeys(pattern.findall(html)))
    if urls:
        return urls

    # Fallback: JSON embebido en la página (__NEXT_DATA__ u otros blobs)
    for match in re.finditer(r"/public-files/datasets/" + dataset_id + r"/files/([a-f0-9-]+)", html):
        file_id = match.group(1)
        urls.append(
            f"https://data.mendeley.com/public-files/datasets/{dataset_id}/files/{file_id}/file_downloaded"
        )
    return list(dict.fromkeys(urls))


def _download_mendeley_zip(dataset_id: str, zip_name: str) -> Path:
    dest_dir = DATASETS_DIR / dataset_id
    zip_path = dest_dir / zip_name
    if zip_path.exists() and zip_path.stat().st_size > 50_000:
        print(f"  ZIP ya presente: {zip_path}")
        return zip_path

    urls = _mendeley_file_urls(dataset_id)
    if not urls:
        raise RuntimeError(
            f"No se encontraron URLs de descarga para Mendeley {dataset_id}. "
            f"Descarga manual desde https://data.mendeley.com/datasets/{dataset_id}/1"
        )

    dest_dir.mkdir(parents=True, exist_ok=True)
    last_error: Exception | None = None
    for url in urls:
        try:
            print(f"  Descargando {url[:90]}...")
            _download(url, zip_path, timeout=600)
            return zip_path
        except Exception as exc:
            last_error = exc
            print(f"  Falló: {exc}")
    raise RuntimeError(f"No se pudo descargar Mendeley {dataset_id}: {last_error}")


def _extract_zip(zip_path: Path, extract_dir: Path) -> None:
    if extract_dir.exists() and any(extract_dir.rglob("*")):
        print(f"  Ya extraído en {extract_dir}")
        return
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)


def _normalize_folder_name(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"^\d+[\.\)_-]*\s*", "", name)
    name = name.replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", name)


def _map_folder_to_label(folder_name: str, mapping: dict[str, str]) -> str | None:
    norm = _normalize_folder_name(folder_name)
    if norm in mapping:
        return mapping[norm]
    for key, label in mapping.items():
        if key in norm or norm in key:
            return label
    return None


def _import_from_class_folders(
    root: Path,
    mapping: dict[str, str],
    prefix: str,
    max_per_class: int,
    counts: dict[str, int],
) -> int:
    imported = 0
    class_dirs: list[Path] = []

    for path in sorted(root.rglob("*")):
        if path.is_dir() and any(c.suffix.lower() in IMAGE_EXTS for c in path.iterdir() if c.is_file()):
            class_dirs.append(path)

    # Preferir carpetas de primer nivel si existen
    top_level = [d for d in root.iterdir() if d.is_dir()] if root.is_dir() else []
    if top_level and all(any(c.is_file() for c in d.iterdir()) for d in top_level[:3] if d.exists()):
        class_dirs = top_level

    seen_roots: set[Path] = set()
    for class_dir in class_dirs:
        if class_dir in seen_roots:
            continue
        seen_roots.add(class_dir)
        label = _map_folder_to_label(class_dir.name, mapping)
        if label is None:
            continue
        if counts[label] >= max_per_class:
            continue
        dest_dir = EXTRA_DIR / label
        for img in sorted(class_dir.iterdir()):
            if not img.is_file() or img.suffix.lower() not in IMAGE_EXTS:
                continue
            if counts[label] >= max_per_class:
                break
            dest = dest_dir / f"{prefix}{class_dir.name}_{img.name}"
            if dest.exists():
                continue
            shutil.copy2(img, dest)
            counts[label] += 1
            imported += 1
    return imported


def import_mendeley8(max_per_class: int, zip_path: Path | None = None) -> tuple[dict[str, int], int]:
    print("\n--- Mendeley 8 tomato pests (s62zm6djd2) ---")
    if zip_path is None:
        try:
            zip_path = _download_mendeley_zip(MENDELEY8_DATASET_ID, "tomato_pests_8.zip")
        except Exception as exc:
            manual = DATASETS_DIR / MENDELEY8_DATASET_ID / "tomato_pests_8.zip"
            if manual.exists():
                print(f"  Usando ZIP manual: {manual}")
                zip_path = manual
            else:
                raise RuntimeError(
                    f"{exc}. Descarga manual: https://data.mendeley.com/datasets/{MENDELEY8_DATASET_ID}/1 "
                    f"→ guarda como {manual}"
                ) from exc
    extract_dir = DATASETS_DIR / MENDELEY8_DATASET_ID / "extracted"
    _extract_zip(zip_path, extract_dir)
    counts: dict[str, int] = defaultdict(int)
    imported = _import_from_class_folders(extract_dir, MENDELEY8_TO_LABEL, "mendeley8_", max_per_class, counts)
    print(f"  Importadas: {imported}")
    return dict(counts), imported


def import_mendeley6(max_per_class: int, zip_path: Path | None = None) -> tuple[dict[str, int], int]:
    print("\n--- Mendeley 6 tomato pests (ysk546n9np) ---")
    if zip_path is None:
        try:
            zip_path = _download_mendeley_zip(MENDELEY6_DATASET_ID, "tomato_pests_6.zip")
        except Exception as exc:
            manual = DATASETS_DIR / MENDELEY6_DATASET_ID / "tomato_pests_6.zip"
            if manual.exists():
                print(f"  Usando ZIP manual: {manual}")
                zip_path = manual
            else:
                raise RuntimeError(
                    f"{exc}. Descarga manual: https://data.mendeley.com/datasets/{MENDELEY6_DATASET_ID}/1 "
                    f"→ guarda como {manual}"
                ) from exc
    extract_dir = DATASETS_DIR / MENDELEY6_DATASET_ID / "extracted"
    _extract_zip(zip_path, extract_dir)
    counts: dict[str, int] = defaultdict(int)
    imported = _import_from_class_folders(extract_dir, MENDELEY6_TO_LABEL, "mendeley6_", max_per_class, counts)
    print(f"  Importadas: {imported}")
    return dict(counts), imported


def _zenodo_download_urls(record_id: str) -> list[tuple[str, str]]:
    api = f"https://zenodo.org/api/records/{record_id}"
    req = urllib.request.Request(api, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    payload = json.loads(urllib.request.urlopen(req, timeout=60).read().decode("utf-8"))
    files = payload.get("files") or []
    return [(f.get("key", "file"), f["links"]["self"]) for f in files if f.get("links", {}).get("self")]


def import_tomatoebola(max_per_class: int) -> tuple[dict[str, int], int]:
    print("\n--- Zenodo TomatoEbola (tuta absoluta) ---")
    urls = _zenodo_download_urls(ZENODO_TOMATOEBOLA_ID)
    if not urls:
        print("  Sin archivos publicados en Zenodo 13324917 — omitido.")
        return {}, 0

    dest_root = DATASETS_DIR / "tomatoebola"
    dest_root.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = defaultdict(int)
    imported = 0
    label = "tuta absoluta"

    for name, url in urls:
        local = dest_root / name
        if not local.exists():
            print(f"  Descargando {name}...")
            _download(url, local, timeout=600)
        if local.suffix.lower() == ".zip":
            extract_dir = dest_root / "extracted"
            _extract_zip(local, extract_dir)
            imported += _import_labeled_yolo_or_flat(extract_dir, label, "tutaebola_", max_per_class, counts)
        elif local.suffix.lower() in IMAGE_EXTS and counts[label] < max_per_class:
            dest = EXTRA_DIR / label / f"tutaebola_{local.name}"
            if not dest.exists():
                shutil.copy2(local, dest)
                counts[label] += 1
                imported += 1

    print(f"  Importadas: {imported}")
    return dict(counts), imported


def _import_labeled_yolo_or_flat(root: Path, label: str, prefix: str, max_per_class: int, counts: dict[str, int]) -> int:
    """Importa imágenes sueltas o estructura train/images de YOLO."""
    imported = 0
    search_roots = [root / "train" / "images", root / "images", root]
    for search in search_roots:
        if not search.exists():
            continue
        for img in search.rglob("*"):
            if not img.is_file() or img.suffix.lower() not in IMAGE_EXTS:
                continue
            if counts[label] >= max_per_class:
                return imported
            dest = EXTRA_DIR / label / f"{prefix}{img.parent.name}_{img.name}"
            if dest.exists():
                continue
            shutil.copy2(img, dest)
            counts[label] += 1
            imported += 1
    return imported


def print_summary(total_imported: int) -> None:
    print("\n=== Resumen extra_data (post-import público) ===")
    for label in LABELS:
        folder = EXTRA_DIR / label
        n = sum(1 for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTS) if folder.exists() else 0
        print(f"  {label:22} {n:4d}")
    print(f"\nNuevas imágenes en esta ejecución: {total_imported}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Importar datasets públicos → extra_data")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--mendeley8", action="store_true")
    parser.add_argument("--mendeley6", action="store_true")
    parser.add_argument("--tomatoebola", action="store_true")
    parser.add_argument("--max-per-class", type=int, default=80)
    parser.add_argument("--mendeley8-zip", type=Path, default=None, help="ZIP manual Mendeley 8 plagas")
    parser.add_argument("--mendeley6-zip", type=Path, default=None, help="ZIP manual Mendeley 6 plagas")
    args = parser.parse_args()

    if not (args.all or args.mendeley8 or args.mendeley6 or args.tomatoebola):
        parser.error("Indica --all, --mendeley8, --mendeley6 o --tomatoebola")

    _ensure_dirs()
    total = 0

    if args.all or args.mendeley8:
        try:
            _, n = import_mendeley8(args.max_per_class, args.mendeley8_zip)
            total += n
        except Exception as exc:
            print(f"  OMITIDO mendeley8: {exc}")

    if args.all or args.mendeley6:
        try:
            _, n = import_mendeley6(args.max_per_class, args.mendeley6_zip)
            total += n
        except Exception as exc:
            print(f"  OMITIDO mendeley6: {exc}")

    if args.all or args.tomatoebola:
        try:
            _, n = import_tomatoebola(args.max_per_class)
            total += n
        except Exception as exc:
            print(f"  OMITIDO tomatoebola: {exc}")

    print_summary(total)


if __name__ == "__main__":
    main()
