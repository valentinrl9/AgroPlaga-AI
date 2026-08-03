"""Auditoría rápida de ml/dataset_semilla/."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1] / "dataset_semilla"
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def count_images(folder: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    if not folder.exists():
        return counts
    for sub in sorted(folder.iterdir()):
        if sub.is_dir():
            counts[sub.name] = sum(
                1 for f in sub.rglob("*") if f.is_file() and f.suffix.lower() in EXTS
            )
    return counts


def main() -> None:
    reg = json.loads((ROOT / "plague_registry.json").read_text(encoding="utf-8"))
    plagues = reg["plagues"]
    crops = reg.get("healthy_crops", [])

    totals: dict[str, int] = {}
    print("=== PLAGAS ===")
    for i, pl in enumerate(plagues, 1):
        folder = pl["folder"]
        counts = count_images(ROOT / folder)
        total = sum(counts.values())
        totals[folder] = total
        org = sum(v for k, v in counts.items() if not k.startswith("dano") and k != "cromo")
        dano = sum(v for k, v in counts.items() if k.startswith("dano"))
        cromo = counts.get("cromo", 0)
        subs = ", ".join(f"{k}:{v}" for k, v in sorted(counts.items()) if v > 0)
        print(
            f"{i:02d} {folder:28} total={total:3d}  org={org:3d}  dano={dano:3d}  "
            f"cromo={cromo}  [{subs}]"
        )

    print(f"\nGRAND TOTAL plagas: {sum(totals.values())}")

    print("\n=== HOJAS SANAS ===")
    hs = ROOT / "00_hojas_sanas"
    crop_totals = 0
    if hs.exists():
        for crop in crops:
            cp = hs / crop
            n = (
                sum(1 for f in cp.rglob("*") if f.is_file() and f.suffix.lower() in EXTS)
                if cp.exists()
                else 0
            )
            crop_totals += n
            status = "OK" if n >= 30 else ("bajo" if n >= 10 else "critico")
            print(f"  {crop:12} {n:3d}  [{status}]")
        other = [d.name for d in hs.iterdir() if d.is_dir() and d.name not in crops]
        if other:
            print(f"  otras carpetas: {other}")
    else:
        print("  (no existe)")
    print(f"  TOTAL hojas sanas: {crop_totals}")

    print("\n=== VALIDACION ===")
    corrupt: list[str] = []
    small: list[str] = []
    all_imgs: list[Path] = []
    for pl in plagues:
        pdir = ROOT / pl["folder"]
        if not pdir.exists():
            continue
        for f in pdir.rglob("*"):
            if not f.is_file() or f.suffix.lower() not in EXTS:
                continue
            all_imgs.append(f)
            try:
                with Image.open(f) as im:
                    im.verify()
                with Image.open(f) as im:
                    w, h = im.size
                if min(w, h) < 150:
                    small.append(f"{f.parent.name}/{f.name} {w}x{h}")
            except Exception as e:
                corrupt.append(f"{f.relative_to(ROOT)}: {e}")

    print(f"Total imagenes plagas: {len(all_imgs)}")
    print(f"Corruptas: {len(corrupt)}")
    for c in corrupt[:15]:
        print(f"  {c}")
    print(f"Muy pequenas (<150px): {len(small)}")
    for s in small[:15]:
        print(f"  {s}")

    print("\n=== RESUMEN POR UMBRAL ===")
    min_org, min_dano = 10, 20
    ok_pilot, partial, critical = [], [], []
    for pl in plagues:
        folder = pl["folder"]
        counts = count_images(ROOT / folder)
        total = sum(counts.values())
        org = sum(v for k, v in counts.items() if not k.startswith("dano") and k != "cromo")
        dano = sum(v for k, v in counts.items() if k.startswith("dano"))
        entry = f"{folder} ({total} total, org={org}, dano={dano})"
        if total >= 30 and org >= min_org and dano >= min_dano:
            ok_pilot.append(entry)
        elif total >= 10:
            partial.append(entry)
        else:
            critical.append(entry)

    print(f"Listas para piloto (>=30 total, org>={min_org}, dano>={min_dano}): {len(ok_pilot)}")
    for e in ok_pilot:
        print(f"  + {e}")
    print(f"Parciales (10-29 fotos): {len(partial)}")
    for e in partial:
        print(f"  ~ {e}")
    print(f"Criticas (<10 fotos): {len(critical)}")
    for e in critical:
        print(f"  ! {e}")


if __name__ == "__main__":
    main()
