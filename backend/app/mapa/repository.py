"""Persistencia catálogo MAPA en PostgreSQL."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.biocide_product import BiocideProduct


def replace_mapa_catalog(db: Session, rows: list[dict]) -> int:
    db.query(BiocideProduct).delete()
    for row in rows:
        db.add(BiocideProduct(**row))
    db.commit()
    return len(rows)


def count_mapa_products(db: Session) -> int:
    return db.query(BiocideProduct).filter(BiocideProduct.source == "mapa_cex").count()


def latest_sync_at(db: Session) -> datetime | None:
    row = (
        db.query(BiocideProduct.synced_at)
        .filter(BiocideProduct.source == "mapa_cex", BiocideProduct.synced_at.isnot(None))
        .order_by(BiocideProduct.synced_at.desc())
        .first()
    )
    return row[0] if row else None
