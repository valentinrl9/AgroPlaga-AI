"""Contadores badge SIEX / SIGPAC (Fase 5)."""

from sqlalchemy.orm import Session

from app.models.farm import Farm
from app.models.siex_entry import SiexCuadernoEntry
from app.models.user import User


def get_siex_badge_counts(db: Session, user: User) -> dict[str, int]:
    if not user.has_siex_module:
        return {"siex_pending_sigpac": 0, "farms_missing_sigpac": 0}

    siex_pending = (
        db.query(SiexCuadernoEntry)
        .filter(
            SiexCuadernoEntry.user_id == user.id,
            SiexCuadernoEntry.status == "pendiente_sigpac",
        )
        .count()
    )
    farms_missing = (
        db.query(Farm)
        .filter(
            Farm.user_id == user.id,
            (Farm.sigpac_code.is_(None)) | (Farm.sigpac_code == ""),
        )
        .count()
    )
    return {
        "siex_pending_sigpac": siex_pending,
        "farms_missing_sigpac": farms_missing,
    }
