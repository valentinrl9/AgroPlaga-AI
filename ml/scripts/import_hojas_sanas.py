"""
Importa hojas sanas por cultivo → ml/dataset_semilla/00_hojas_sanas/{cultivo}/.

Fuentes:
  1. PlantVillage (HuggingFace geraldmc/plantvillage-full) — clases *healthy*
  2. PlantDoc local (ml/datasets/plantdoc) — carpetas de hoja sana
  3. iNaturalist API — complemento por nombre científico

Uso:
  python ml/scripts/import_hojas_sanas.py
  python ml/scripts/import_hojas_sanas.py --max-per-crop 40 --min-target 30
"""

from __future__ import annotations

import argparse
import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

try:
    import certifi

    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()

SCRIPT_DIR = Path(__file__).resolve().parent
ML_DIR = SCRIPT_DIR.parent
DATASET_ROOT = ML_DIR / "dataset_semilla"
HOJAS_ROOT = DATASET_ROOT / "00_hojas_sanas"
PLANTDOC_DIR = ML_DIR / "datasets" / "plantdoc"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
USER_AGENT = "AgroPlaga-AI/1.0 (educational; hojas_sanas)"

# PlantVillage class_label → cultivo (solo hortícolas invernadero)
PLANTVILLAGE_CLASS_TO_CROP: dict[str, str] = {
    "Tomato___healthy": "tomate",
    "Pepper,_bell___healthy": "pimiento",
}

# PlantDoc carpeta → cultivo
PLANTDOC_FOLDER_TO_CROP: dict[str, str] = {
    "Tomato leaf": "tomate",
    "Bell_pepper leaf": "pimiento",
}

# iNaturalist: cultivo → (nombre científico, términos extra en búsqueda)
INATURALIST_CROPS: dict[str, tuple[str, str]] = {
    "tomate": ("Solanum lycopersicum", "leaf"),
    "pimiento": ("Capsicum annuum", "leaf"),
    "pepino": ("Cucumis sativus", "leaf"),
    "calabacin": ("Cucurbita pepo", "leaf"),
    "berenjena": ("Solanum melongena", "leaf"),
    "lechuga": ("Lactuca sativa", "leaf"),
}


def _load_crops() -> list[str]:
    meta = HOJAS_ROOT / "_meta.json"
    if meta.exists():
        return json.loads(meta.read_text(encoding="utf-8"))["crops"]
    reg = json.loads((DATASET_ROOT / "plague_registry.json").read_text(encoding="utf-8"))
    return reg["healthy_crops"]


def _count_images(crop_dir: Path) -> int:
    if not crop_dir.exists():
        return 0
    return sum(1 for f in crop_dir.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTS)


def _next_path(crop_dir: Path, prefix: str, crop: str, index: int) -> Path:
    crop_dir.mkdir(parents=True, exist_ok=True)
    for n in range(index, index + 10_000):
        dest = crop_dir / f"{crop}_{prefix}_{n:03d}.jpg"
        if not dest.exists():
            return dest
    raise RuntimeError(f"Sin nombre libre en {crop_dir}")


def _download_url(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=90, context=SSL_CTX) as response:
        data = response.read()
    if len(data) < 2048:
        raise ValueError("respuesta demasiado pequeña")
    dest.write_bytes(data)


def _save_pil_image(image, dest: Path) -> None:
    if hasattr(image, "convert"):
        image.convert("RGB").save(dest, format="JPEG", quality=92)
    else:
        raise RuntimeError("imagen no PIL")


def import_plantvillage(counts: dict[str, int], max_per_crop: int) -> dict[str, int]:
    from datasets import load_dataset

    added: dict[str, int] = defaultdict(int)
    print("\n--- PlantVillage (healthy) ---")
    ds = load_dataset("geraldmc/plantvillage-full", split="train", streaming=True)

    for example in ds:
        class_label = example["class_label"]
        crop = PLANTVILLAGE_CLASS_TO_CROP.get(class_label)
        if crop is None:
            continue
        if counts[crop] >= max_per_crop:
            continue

        dest = _next_path(HOJAS_ROOT / crop, "pv", crop, counts[crop] + 1)
        _save_pil_image(example["image"], dest)
        counts[crop] += 1
        added[crop] += 1

    for crop, n in sorted(added.items()):
        if n:
            print(f"  {crop}: +{n}")
    return dict(added)


def import_plantdoc(counts: dict[str, int], max_per_crop: int) -> dict[str, int]:
    added: dict[str, int] = defaultdict(int)
    print("\n--- PlantDoc (hoja sana) ---")
    if not PLANTDOC_DIR.exists() or not (PLANTDOC_DIR / "train").exists():
        print("  PlantDoc no encontrado (ejecuta antes: python ml/import_extra_data.py --plantdoc)")
        return {}

    import shutil

    for split in ("train", "test"):
        split_dir = PLANTDOC_DIR / split
        if not split_dir.exists():
            continue
        for class_dir in sorted(split_dir.iterdir()):
            if not class_dir.is_dir():
                continue
            crop = PLANTDOC_FOLDER_TO_CROP.get(class_dir.name)
            if crop is None:
                continue
            if counts[crop] >= max_per_crop:
                continue
            for img in sorted(class_dir.iterdir()):
                if img.suffix.lower() not in IMAGE_EXTS:
                    continue
                if counts[crop] >= max_per_crop:
                    break
                dest = _next_path(HOJAS_ROOT / crop, "pd", crop, counts[crop] + 1)
                shutil.copy2(img, dest)
                counts[crop] += 1
                added[crop] += 1

    for crop, n in sorted(added.items()):
        if n:
            print(f"  {crop}: +{n}")
    return dict(added)


def _inat_photo_url(photo: dict) -> str | None:
    url = photo.get("url")
    if not isinstance(url, str):
        return None
    for size in ("original", "large", "medium"):
        candidate = re.sub(r"/(square|small|medium|large|original)\.", f"/{size}.", url)
        if candidate != url:
            return candidate
    return url


def import_inaturalist(counts: dict[str, int], max_per_crop: int, delay: float) -> dict[str, int]:
    added: dict[str, int] = defaultdict(int)
    print("\n--- iNaturalist ---")

    for crop, (scientific, term) in INATURALIST_CROPS.items():
        if counts[crop] >= max_per_crop:
            print(f"  {crop}: omitido (ya {counts[crop]})")
            continue

        page = 1
        queries = [term, ""] if term else [""]
        query_idx = 0
        while counts[crop] < max_per_crop and page <= 15:
            q = queries[query_idx] if query_idx < len(queries) else ""
            params = urllib.parse.urlencode(
                {
                    "taxon_name": scientific,
                    "photos": "true",
                    "quality_grade": "research",
                    "per_page": 100,
                    "page": page,
                    **({"q": q} if q else {}),
                }
            )
            url = f"https://api.inaturalist.org/v1/observations?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=60, context=SSL_CTX) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                print(f"  {crop}: error API pagina {page} ({exc})")
                break

            results = payload.get("results") or []
            if not results:
                if query_idx + 1 < len(queries):
                    query_idx += 1
                    page = 1
                    continue
                break

            for obs in results:
                if counts[crop] >= max_per_crop:
                    break
                photos = obs.get("photos") or []
                for photo in photos:
                    if counts[crop] >= max_per_crop:
                        break
                    photo_url = _inat_photo_url(photo)
                    if not photo_url:
                        continue
                    dest = _next_path(HOJAS_ROOT / crop, "inat", crop, counts[crop] + 1)
                    try:
                        _download_url(photo_url, dest)
                    except Exception:
                        continue
                    counts[crop] += 1
                    added[crop] += 1
                    time.sleep(delay)

            page += 1
            time.sleep(delay)

        print(f"  {crop}: +{added.get(crop, 0)} (total {counts[crop]})")

    return dict(added)


def print_report(crops: list[str], min_target: int) -> None:
    print("\n=== Informe 00_hojas_sanas ===")
    manual: list[str] = []
    for crop in crops:
        n = _count_images(HOJAS_ROOT / crop)
        status = "OK" if n >= min_target else ("bajo" if n >= 10 else "CRITICO")
        bar = "#" * min(n // 3, 25)
        print(f"  {crop:12} {n:3d}  [{status:7}]  {bar}")
        if n < min_target:
            manual.append(crop)

    total = sum(_count_images(HOJAS_ROOT / c) for c in crops)
    print(f"\n  TOTAL: {total} fotos")

    if manual:
        need = {c: max(0, min_target - _count_images(HOJAS_ROOT / c)) for c in manual}
        print("\n  Buscar a mano (fotos propias invernadero o IFAPA):")
        for crop in manual:
            print(f"    - {crop}: faltan ~{need[crop]} (objetivo {min_target})")
    else:
        print("\n  Todos los cultivos alcanzan el mínimo automático.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Importar hojas sanas por cultivo")
    parser.add_argument("--max-per-crop", type=int, default=40, help="Máximo por cultivo")
    parser.add_argument("--min-target", type=int, default=30, help="Mínimo recomendado (informe)")
    parser.add_argument("--skip-plantvillage", action="store_true")
    parser.add_argument("--skip-plantdoc", action="store_true")
    parser.add_argument("--skip-inaturalist", action="store_true")
    parser.add_argument("--delay", type=float, default=0.3, help="Pausa iNaturalist (s)")
    args = parser.parse_args()

    crops = _load_crops()
    for crop in crops:
        (HOJAS_ROOT / crop).mkdir(parents=True, exist_ok=True)

    counts = {crop: _count_images(HOJAS_ROOT / crop) for crop in crops}
    print("Estado inicial:", ", ".join(f"{c}={counts[c]}" for c in crops))

    if not args.skip_plantvillage:
        import_plantvillage(counts, args.max_per_crop)
    if not args.skip_plantdoc:
        import_plantdoc(counts, args.max_per_crop)
    if not args.skip_inaturalist:
        import_inaturalist(counts, args.max_per_crop, args.delay)

    print_report(crops, args.min_target)


if __name__ == "__main__":
    main()
