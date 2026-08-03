"""
Descarga fotos EPPO vía API oficial → ml/dataset_semilla/{plaga}/{subcarpeta}/.

Requiere cuenta gratuita EPPO Data Portal y clave API:
  https://data.eppo.int/  → Create Account → API key
  Variable de entorno: EPPO_API_KEY

Uso:
  python ml/scripts/fetch_eppo_photos.py --dry-run
  python ml/scripts/fetch_eppo_photos.py --plague 02_tuta --max-per-subfolder 30
  python ml/scripts/fetch_eppo_photos.py --all --skip-existing
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import certifi
except ImportError:
    certifi = None  # type: ignore[assignment]

SCRIPT_DIR = Path(__file__).resolve().parent
ML_DIR = SCRIPT_DIR.parent
DATASET_ROOT = ML_DIR / "dataset_semilla"
sys.path.insert(0, str(SCRIPT_DIR))

from eppo_tag_mapping import (  # noqa: E402
    DANO_ALIASES,
    DAMAGE_HINTS,
    EPPO_CODE_OVERRIDES,
    ORG_ALIASES,
)

EPPO_API_BASE = "https://api.eppo.int/gd/v2"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
USER_AGENT = "AgroPlaga-AI/1.0 (educational; dataset_semilla)"


def _load_api_key(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    key = os.environ.get("EPPO_API_KEY")
    if key:
        return key
    env_file = ML_DIR.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("EPPO_API_KEY="):
                value = line.split("=", 1)[1].strip()
                if value:
                    return value
    return None


def _ssl_context() -> ssl.SSLContext:
    if certifi is not None:
        return ssl.create_default_context(cafile=certifi.where())
    return ssl.create_default_context()


def _load_registry() -> dict[str, Any]:
    return json.loads((DATASET_ROOT / "plague_registry.json").read_text(encoding="utf-8"))


def _eppo_code(plague: dict[str, Any]) -> str:
    return EPPO_CODE_OVERRIDES.get(plague["folder"], plague["eppo_code"])


def _score_tag(tag: str, aliases: tuple[str, ...]) -> int:
    tag_l = tag.lower()
    return max((2 if alias in tag_l else 0) + (1 if tag_l in alias else 0) for alias in aliases)


def _is_damage_tag(tag: str) -> bool:
    tag_l = tag.lower()
    return any(h in tag_l for h in DAMAGE_HINTS)


def map_tag_to_subfolder(tag: str, subfolders: list[str]) -> str | None:
    if not tag or not subfolders:
        return None

    usable = [s for s in subfolders if s != "cromo"]
    dano_folders = [s for s in usable if s.startswith("dano_")]
    org_folders = [s for s in usable if not s.startswith("dano_")]

    if not dano_folders and not org_folders:
        return None

    if _is_damage_tag(tag) or tag.lower().startswith("damage"):
        if not dano_folders:
            return org_folders[0] if org_folders else None
        scores = {sf: _score_tag(tag, DANO_ALIASES.get(sf, ())) for sf in dano_folders}
        best = max(scores.items(), key=lambda x: x[1])
        return best[0] if best[1] > 0 else dano_folders[0]

    if not org_folders:
        if dano_folders:
            scores = {sf: _score_tag(tag, DANO_ALIASES.get(sf, ())) for sf in dano_folders}
            if scores:
                best = max(scores.items(), key=lambda x: x[1])
                if best[1] > 0:
                    return best[0]
            return dano_folders[0]
        return None

    scores = {sf: _score_tag(tag, ORG_ALIASES.get(sf, ())) for sf in org_folders}
    best = max(scores.items(), key=lambda x: x[1])
    if best[1] > 0:
        return best[0]

    tag_l = tag.lower()
    for sf in org_folders:
        key = sf.replace("_", " ")
        if key in tag_l or sf.replace("_", "") in tag_l.replace(" ", ""):
            return sf

    return org_folders[0] if org_folders else None


def _flatten_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in ("photos", "data", "items", "results", "content"):
            value = payload.get(key)
            if isinstance(value, list):
                return [x for x in value if isinstance(x, dict)]
        return [payload]
    return []


def _pick(record: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = record.get(key)
        if value is None:
            continue
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, (int, float)):
            return str(value)
    return None


def fetch_eppo_photos(api_key: str, eppo_code: str) -> list[dict[str, Any]]:
    endpoint = f"{EPPO_API_BASE}/taxons/taxon/{eppo_code}/photos"
    req = urllib.request.Request(
        endpoint,
        headers={"X-Api-Key": api_key, "Accept": "application/json", "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=60, context=_ssl_context()) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return _flatten_records(payload)


def _photo_url(record: dict[str, Any]) -> str | None:
    files = record.get("files")
    if isinstance(files, list) and files:
        preferred_sizes = ("1024x0", "1024", "800x0", "640x0", "220x130")
        by_size = {
            str(item.get("size", "")): item.get("url")
            for item in files
            if isinstance(item, dict) and item.get("url")
        }
        for size in preferred_sizes:
            url = by_size.get(size)
            if isinstance(url, str) and url.startswith("http"):
                return url
        for item in files:
            if isinstance(item, dict):
                url = item.get("url")
                if isinstance(url, str) and url.startswith("http"):
                    return url

    url = _pick(
        record,
        "url",
        "photoUrl",
        "photo_url",
        "imageUrl",
        "image_url",
        "link",
        "fullUrl",
        "full_url",
        "href",
    )
    if url and url.startswith("http"):
        return url
    return None


def _photo_tag(record: dict[str, Any]) -> str:
    tags = record.get("tags") or record.get("tagList") or record.get("labels")
    if isinstance(tags, list) and tags:
        parts = []
        for tag in tags:
            if isinstance(tag, dict):
                parts.append(str(tag.get("label") or tag.get("name") or tag.get("tag") or tag))
            else:
                parts.append(str(tag))
        return ", ".join(parts)
    desc = _pick(record, "descinfo", "description", "caption")
    if desc:
        return desc
    return _pick(record, "tag", "photoTag", "photo_tag", "category", "type", "label") or "unknown"


def _next_filename(dest_dir: Path, eppo_code: str, subfolder: str, index: int) -> Path:
    slug = subfolder.replace("dano_", "dano").replace("_", "")[:20]
    for n in range(index, index + 10_000):
        candidate = dest_dir / f"{eppo_code}_{slug}_{n:03d}.jpg"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"No hay nombre libre en {dest_dir}")


def _append_manifest(rows: list[dict[str, str]]) -> None:
    manifest = DATASET_ROOT / "manifest.csv"
    write_header = not manifest.exists() or manifest.stat().st_size == 0
    with manifest.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "plague_folder",
                "subfolder",
                "filename",
                "eppo_code",
                "source_url",
                "courtesy",
                "tag_eppo",
                "downloaded_at",
            ],
        )
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


def download_image(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=90, context=_ssl_context()) as response:
        data = response.read()
    if len(data) < 1024:
        raise ValueError("Imagen demasiado pequeña")
    dest.write_bytes(data)


def process_plague(
    plague: dict[str, Any],
    api_key: str,
    max_per_subfolder: int,
    skip_existing: bool,
    dry_run: bool,
    delay_s: float,
) -> dict[str, int]:
    folder = plague["folder"]
    eppo_code = _eppo_code(plague)
    subfolders: list[str] = plague["subfolders"]
    plague_dir = DATASET_ROOT / folder
    plague_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== {folder} ({eppo_code}) ===")
    try:
        records = fetch_eppo_photos(api_key, eppo_code)
    except urllib.error.HTTPError as exc:
        print(f"  ERROR API: {exc}")
        return {}
    except Exception as exc:
        print(f"  ERROR: {exc}")
        return {}

    print(f"  Metadatos EPPO: {len(records)} fotos")
    per_sub: dict[str, int] = {sf: 0 for sf in subfolders if sf != "cromo"}
    existing_counts: dict[str, int] = {}
    for sf in per_sub:
        sf_dir = plague_dir / sf
        if sf_dir.exists():
            existing_counts[sf] = sum(
                1 for p in sf_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS
            )
        else:
            existing_counts[sf] = 0

    manifest_rows: list[dict[str, str]] = []
    downloaded = 0
    skipped = 0

    for record in records:
        tag = _photo_tag(record)
        subfolder = map_tag_to_subfolder(tag, subfolders)
        if subfolder is None or subfolder == "cromo":
            skipped += 1
            continue

        if existing_counts.get(subfolder, 0) + per_sub.get(subfolder, 0) >= max_per_subfolder:
            continue

        url = _photo_url(record)
        if not url:
            skipped += 1
            continue

        courtesy = _pick(record, "courtesy", "author", "credit", "photographer", "copyright")
        if not courtesy:
            authors = record.get("authors")
            if isinstance(authors, list) and authors:
                courtesy = ", ".join(str(a) for a in authors if a)
            elif isinstance(authors, str):
                courtesy = authors
        courtesy = courtesy or "EPPO"
        dest_dir = plague_dir / subfolder
        dest_dir.mkdir(parents=True, exist_ok=True)
        next_idx = existing_counts.get(subfolder, 0) + per_sub.get(subfolder, 0) + 1
        dest = _next_filename(dest_dir, eppo_code, subfolder, next_idx)

        if skip_existing and dest.exists():
            continue

        if dry_run:
            print(f"  [dry-run] {subfolder}/{dest.name}  tag={tag[:50]}")
            per_sub[subfolder] = per_sub.get(subfolder, 0) + 1
            continue

        try:
            download_image(url, dest)
        except Exception as exc:
            print(f"  omitida {url}: {exc}")
            skipped += 1
            time.sleep(delay_s)
            continue

        per_sub[subfolder] = per_sub.get(subfolder, 0) + 1
        downloaded += 1
        manifest_rows.append(
            {
                "plague_folder": folder,
                "subfolder": subfolder,
                "filename": dest.name,
                "eppo_code": eppo_code,
                "source_url": url,
                "courtesy": courtesy,
                "tag_eppo": tag,
                "downloaded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
        )
        print(f"  + {subfolder}/{dest.name}  ({tag[:40]})")
        time.sleep(delay_s)

    if manifest_rows and not dry_run:
        _append_manifest(manifest_rows)

    total_new = sum(per_sub.values())
    print(f"  Nuevas: {total_new}  Omitidas: {skipped}")
    return per_sub


def main() -> None:
    parser = argparse.ArgumentParser(description="Descargar fotos EPPO → dataset_semilla")
    parser.add_argument("--all", action="store_true", help="Todas las plagas del registry")
    parser.add_argument("--plague", action="append", default=[], help="Carpeta plaga (ej. 02_tuta)")
    parser.add_argument("--max-per-subfolder", type=int, default=30)
    parser.add_argument("--skip-existing", action="store_true", help="No sobrescribir nombres existentes")
    parser.add_argument("--dry-run", action="store_true", help="Solo listar, sin descargar")
    parser.add_argument("--delay", type=float, default=0.4, help="Segundos entre descargas")
    parser.add_argument("--api-key", default=None, help="Clave EPPO (o EPPO_API_KEY / .env)")
    args = parser.parse_args()

    if not args.all and not args.plague:
        parser.error("Indica --all o --plague 02_tuta (repetible)")

    api_key = _load_api_key(args.api_key)
    if not args.dry_run and not api_key:
        parser.error(
            "Falta EPPO_API_KEY. Regístrate gratis en https://data.eppo.int/ y exporta la clave:\n"
            "  PowerShell: $env:EPPO_API_KEY='tu_clave'   o crea .env en la raíz del proyecto"
        )

    registry = _load_registry()
    plagues = registry["plagues"]
    if args.plague:
        wanted = set(args.plague)
        plagues = [p for p in plagues if p["folder"] in wanted]
        missing = wanted - {p["folder"] for p in plagues}
        if missing:
            parser.error(f"Carpetas no encontradas: {', '.join(sorted(missing))}")

    api_key = api_key or "dry-run"
    summary: dict[str, dict[str, int]] = {}
    for plague in plagues:
        summary[plague["folder"]] = process_plague(
            plague,
            api_key=api_key,
            max_per_subfolder=args.max_per_subfolder,
            skip_existing=args.skip_existing,
            dry_run=args.dry_run,
            delay_s=args.delay,
        )

    print("\n=== Resumen ===")
    for folder, counts in summary.items():
        total = sum(counts.values())
        if total:
            detail = ", ".join(f"{k}:{v}" for k, v in sorted(counts.items()) if v)
            print(f"  {folder}: {total} ({detail})")
        else:
            print(f"  {folder}: 0")


if __name__ == "__main__":
    main()
