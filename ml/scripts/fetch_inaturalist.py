"""
Descarga fotos iNaturalist → ml/dataset_semilla/{plaga}/{subcarpeta}/.

API gratuita: https://api.inaturalist.org/v1/observations
Solo observaciones quality_grade=research con fotos.

Uso:
  python ml/scripts/fetch_inaturalist.py --critical
  python ml/scripts/fetch_inaturalist.py --plague 04_pulgon --max-per-subfolder 25
  python ml/scripts/fetch_inaturalist.py --all --skip-existing
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import certifi

    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()

try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore[assignment,misc]

SCRIPT_DIR = Path(__file__).resolve().parent
ML_DIR = SCRIPT_DIR.parent
DATASET_ROOT = ML_DIR / "dataset_semilla"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
USER_AGENT = "AgroPlaga-AI/1.0 (educational; inaturalist)"
MIN_SIDE_PX = 350

# Plagas críticas (<10 fotos o vacías tras EPPO)
CRITICAL_FOLDERS = (
    "04_pulgon",
    "06_minador",
    "07_piojo_harinoso",
    "08_oruga_spodoptera",
    "10_oruga_plusia",
    "15_mancha_bacteriana",
    "16_fusarium",
)

# Búsquedas orientadas a subcarpeta (calidad > volumen bruto)
SearchSpec = dict[str, Any]
PLAGUE_SEARCHES: dict[str, list[SearchSpec]] = {
    "04_pulgon": [
        {"taxon_name": "Aphis gossypii", "subfolder": "formas_apteras", "q": "aphid"},
        {"taxon_name": "Aphis gossypii", "subfolder": "formas_aladas", "q": "winged"},
        {"taxon_name": "Aphis gossypii", "subfolder": "dano_enrollamiento", "q": "curl damage leaf"},
    ],
    "06_minador": [
        {"taxon_name": "Liriomyza trifolii", "subfolder": "larva", "q": "leafminer"},
        {"taxon_name": "Liriomyza trifolii", "subfolder": "adulto", "q": "fly"},
        {"taxon_name": "Liriomyza trifolii", "subfolder": "dano_mina_serpiente", "q": "leaf mine"},
        {"taxon_name": "Liriomyza", "subfolder": "dano_mina_serpiente", "q": "serpentine mine tomato"},
    ],
    "07_piojo_harinoso": [
        {"taxon_name": "Planococcus citri", "subfolder": "adulto_ninfa", "q": "mealybug"},
        {"taxon_name": "Planococcus citri", "subfolder": "dano_brote", "q": "citrus stem"},
        {"taxon_name": "Planococcus citri", "subfolder": "dano_melaza", "q": "sooty mold honeydew"},
    ],
    "08_oruga_spodoptera": [
        {"taxon_name": "Spodoptera exigua", "subfolder": "larva", "q": "caterpillar"},
        {"taxon_name": "Spodoptera exigua", "subfolder": "adulto", "q": "moth"},
        {"taxon_name": "Spodoptera exigua", "subfolder": "dano_defoliacion", "q": "defoliation"},
        {"taxon_name": "Spodoptera exigua", "subfolder": "dano_fruto", "q": "fruit damage"},
    ],
    "10_oruga_plusia": [
        {"taxon_name": "Chrysodeixis chalcites", "subfolder": "larva", "q": "caterpillar"},
        {"taxon_name": "Chrysodeixis chalcites", "subfolder": "dano_defoliacion", "q": "leaf damage"},
        {"taxon_name": "Chrysodeixis", "subfolder": "larva", "q": "plusia tomato"},
    ],
    "15_mancha_bacteriana": [
        {"taxon_name": "Solanum lycopersicum", "subfolder": "dano_mancha_foliar", "q": "bacterial leaf spot"},
        {"taxon_name": "Capsicum annuum", "subfolder": "dano_mancha_foliar", "q": "bacterial spot"},
        {"taxon_name": "Solanum lycopersicum", "subfolder": "dano_fruto", "q": "bacterial spot fruit"},
    ],
    "16_fusarium": [
        {"taxon_name": "Solanum lycopersicum", "subfolder": "dano_marchitez", "q": "fusarium wilt"},
        {"taxon_name": "Solanum lycopersicum", "subfolder": "dano_vascular", "q": "vascular wilt stem"},
        {"taxon_name": "Capsicum annuum", "subfolder": "dano_marchitez", "q": "fusarium wilt"},
    ],
    # Extra: daño en mosca blanca (0 fotos dano en EPPO)
    "03_mosca_blanca": [
        {"taxon_name": "Bemisia tabaci", "subfolder": "dano_amarilleo", "q": "yellowing virus"},
        {"taxon_name": "Bemisia tabaci", "subfolder": "dano_melaza", "q": "honeydew sooty mold"},
    ],
}


def _load_registry() -> dict[str, Any]:
    return json.loads((DATASET_ROOT / "plague_registry.json").read_text(encoding="utf-8"))


def _count_subfolder(plague_dir: Path, subfolder: str) -> int:
    d = plague_dir / subfolder
    if not d.exists():
        return 0
    return sum(1 for f in d.iterdir() if f.suffix.lower() in IMAGE_EXTS)


def _photo_url(photo: dict[str, Any]) -> str | None:
    url = photo.get("url")
    if not isinstance(url, str):
        return None
    return re.sub(r"/(square|small|medium|large|original)\.", "/large.", url)


def _validate_image(path: Path) -> bool:
    if Image is None:
        return path.stat().st_size >= 8192
    try:
        with Image.open(path) as im:
            w, h = im.size
        return min(w, h) >= MIN_SIDE_PX
    except Exception:
        return False


def _download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=90, context=SSL_CTX) as response:
        data = response.read()
    if len(data) < 4096:
        raise ValueError("imagen demasiado pequeña")
    dest.write_bytes(data)
    if not _validate_image(dest):
        dest.unlink(missing_ok=True)
        raise ValueError("resolución insuficiente")


def _next_path(dest_dir: Path, prefix: str, index: int) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    for n in range(index, index + 5000):
        dest = dest_dir / f"{prefix}_{n:03d}.jpg"
        if not dest.exists():
            return dest
    raise RuntimeError(f"sin nombre libre en {dest_dir}")


def _fetch_observations(
    spec: SearchSpec,
    max_needed: int,
    delay: float,
) -> list[dict[str, Any]]:
    collected: list[dict[str, Any]] = []
    page = 1
    taxon = spec.get("taxon_name", "")
    q = spec.get("q", "")

    while len(collected) < max_needed and page <= 12:
        params: dict[str, Any] = {
            "photos": "true",
            "quality_grade": "research",
            "per_page": 100,
            "page": page,
        }
        if taxon:
            params["taxon_name"] = taxon
        if q:
            params["q"] = q

        url = "https://api.inaturalist.org/v1/observations?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60, context=SSL_CTX) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            print(f"    API error p{page}: {exc}")
            break

        results = payload.get("results") or []
        if not results:
            break

        for obs in results:
            obs_url = f"https://www.inaturalist.org/observations/{obs.get('id', '')}"
            species = obs.get("species_guess") or obs.get("taxon", {}).get("name") or ""
            for photo in obs.get("photos") or []:
                photo_url = _photo_url(photo)
                if not photo_url:
                    continue
                collected.append(
                    {
                        "photo_url": photo_url,
                        "obs_url": obs_url,
                        "attribution": photo.get("attribution") or "iNaturalist",
                        "tag": f"{species}; {q}".strip("; "),
                    }
                )
                if len(collected) >= max_needed * 3:
                    break
            if len(collected) >= max_needed * 3:
                break

        page += 1
        time.sleep(delay)

    return collected


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


def process_plague(
    plague: dict[str, Any],
    max_per_subfolder: int,
    skip_existing: bool,
    delay: float,
) -> dict[str, int]:
    folder = plague["folder"]
    searches = PLAGUE_SEARCHES.get(folder)
    if not searches:
        print(f"\n=== {folder}: sin búsquedas iNaturalist configuradas ===")
        return {}

    plague_dir = DATASET_ROOT / folder
    eppo = plague.get("eppo_code", "INAT")
    subfolders: list[str] = plague["subfolders"]
    per_sub = {sf: _count_subfolder(plague_dir, sf) for sf in subfolders if sf != "cromo"}
    added: dict[str, int] = {sf: 0 for sf in per_sub}
    manifest_rows: list[dict[str, str]] = []

    print(f"\n=== {folder} ({plague.get('scientific', '')}) ===")

    for spec in searches:
        subfolder = spec["subfolder"]
        if subfolder not in per_sub:
            continue
        if per_sub[subfolder] >= max_per_subfolder:
            continue

        need = max_per_subfolder - per_sub[subfolder]
        label = spec.get("q") or spec.get("taxon_name", "")
        print(f"  buscando [{subfolder}] {label} (faltan {need})")

        candidates = _fetch_observations(spec, need, delay)
        for item in candidates:
            if per_sub[subfolder] >= max_per_subfolder:
                break

            dest = _next_path(plague_dir / subfolder, "INAT", per_sub[subfolder] + 1)
            if skip_existing and dest.exists():
                continue

            try:
                _download(item["photo_url"], dest)
            except Exception:
                continue

            per_sub[subfolder] += 1
            added[subfolder] += 1
            manifest_rows.append(
                {
                    "plague_folder": folder,
                    "subfolder": subfolder,
                    "filename": dest.name,
                    "eppo_code": eppo,
                    "source_url": item["obs_url"],
                    "courtesy": item["attribution"],
                    "tag_eppo": item["tag"],
                    "downloaded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
            )
            time.sleep(delay)

    if manifest_rows:
        _append_manifest(manifest_rows)

    total_new = sum(added.values())
    detail = ", ".join(f"{k}:+{v}" for k, v in sorted(added.items()) if v)
    print(f"  Nuevas: {total_new}  [{detail}]")
    return added


def main() -> None:
    parser = argparse.ArgumentParser(description="Descargar fotos iNaturalist → dataset_semilla")
    parser.add_argument("--all", action="store_true", help="Todas las plagas con búsquedas configuradas")
    parser.add_argument("--critical", action="store_true", help="Solo plagas críticas (7)")
    parser.add_argument("--plague", action="append", default=[], help="Carpeta plaga")
    parser.add_argument("--max-per-subfolder", type=int, default=25)
    parser.add_argument("--skip-existing", action="store_true", default=True)
    parser.add_argument("--delay", type=float, default=0.25)
    args = parser.parse_args()

    if not args.all and not args.critical and not args.plague:
        parser.error("Indica --critical, --all o --plague 04_pulgon")

    registry = _load_registry()
    plagues = registry["plagues"]

    if args.critical:
        wanted = set(CRITICAL_FOLDERS)
        plagues = [p for p in plagues if p["folder"] in wanted]
    elif args.plague:
        wanted = set(args.plague)
        plagues = [p for p in plagues if p["folder"] in wanted]
    else:
        plagues = [p for p in plagues if p["folder"] in PLAGUE_SEARCHES]

    summary: dict[str, int] = {}
    for plague in plagues:
        counts = process_plague(
            plague,
            max_per_subfolder=args.max_per_subfolder,
            skip_existing=args.skip_existing,
            delay=args.delay,
        )
        summary[plague["folder"]] = sum(counts.values())

    print("\n=== Resumen iNaturalist ===")
    for folder, total in sorted(summary.items()):
        print(f"  {folder}: +{total}")


if __name__ == "__main__":
    main()
