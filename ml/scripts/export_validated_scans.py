#!/usr/bin/env python3
"""
Exporta escaneos validados por perito → ml/extra_data/{plaga}/.

Requiere DATABASE_URL (PostgreSQL del piloto).

Uso:
  python ml/scripts/export_validated_scans.py --dry-run
  python ml/scripts/export_validated_scans.py --database-url %DATABASE_URL%
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ML_DIR = Path(__file__).resolve().parents[1]
ROOT = ML_DIR.parent
EXTRA_DIR = ML_DIR / "extra_data"
_WIN_INVALID = re.compile(r'[<>:"/\\|?*]')

sys.path.insert(0, str(ML_DIR))
from plague_catalog import LABELS  # noqa: E402


def _sanitize(name: str) -> str:
    return _WIN_INVALID.sub("_", name)[:80]


def _resolve_upload_path(image_path: str) -> Path | None:
    raw = Path(image_path)
    candidates = [
        raw,
        ROOT / "backend" / raw,
        ROOT / raw,
        ROOT / "backend" / "uploads" / "scans" / raw.name,
    ]
    if not raw.is_absolute():
        candidates.append(ROOT / "backend" / "uploads" / image_path.lstrip("/"))
    for path in candidates:
        if path.exists() and path.is_file():
            return path
    return None


def _load_scans(database_url: str) -> list[dict]:
    try:
        from sqlalchemy import create_engine, text
    except ImportError as exc:
        raise SystemExit("Instala sqlalchemy: pip install sqlalchemy psycopg2-binary") from exc

    engine = create_engine(database_url)
    query = text(
        """
        SELECT id, plague, corrected_plague, farmer_plague, image_path, tech_status, created_at
        FROM scans
        WHERE tech_status IN ('confirmed', 'corrected')
          AND image_path IS NOT NULL
          AND image_path != ''
        ORDER BY id
        """
    )
    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()
    return [dict(row) for row in rows]


def effective_label(row: dict) -> str | None:
    for key in ("corrected_plague", "farmer_plague", "plague"):
        value = row.get(key)
        if not value:
            continue
        label = str(value).strip().lower()
        if label in LABELS:
            return label
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Exportar escaneos validados → extra_data")
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    if not args.database_url:
        parser.error("Indica --database-url o DATABASE_URL")

    rows = _load_scans(args.database_url)
    if args.limit > 0:
        rows = rows[: args.limit]

    manifest_path = ML_DIR / "reports" / "export_validated_scans.csv"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    exported = 0
    skipped = 0
    manifest_rows: list[dict[str, str]] = []

    for row in rows:
        label = effective_label(row)
        if label is None:
            skipped += 1
            continue
        src = _resolve_upload_path(str(row["image_path"]))
        if src is None:
            skipped += 1
            continue

        dest_dir = EXTRA_DIR / label
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_name = f"scan_{row['id']}_{_sanitize(src.name)}"
        dest = dest_dir / dest_name
        if dest.exists():
            continue

        if args.dry_run:
            print(f"[dry-run] {label} <- {src}")
            exported += 1
            continue

        shutil.copy2(src, dest)
        exported += 1
        manifest_rows.append(
            {
                "scan_id": str(row["id"]),
                "label": label,
                "tech_status": str(row.get("tech_status", "")),
                "source": str(src),
                "dest": str(dest),
                "exported_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    if manifest_rows and not args.dry_run:
        write_header = not manifest_path.exists() or manifest_path.stat().st_size == 0
        with manifest_path.open("a", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(manifest_rows[0].keys()))
            if write_header:
                writer.writeheader()
            writer.writerows(manifest_rows)

    print(f"Escaneos en BD (validados): {len(rows)}")
    print(f"Exportados: {exported}  Omitidos: {skipped}")
    if not args.dry_run:
        print(f"Manifiesto: {manifest_path}")


if __name__ == "__main__":
    main()
