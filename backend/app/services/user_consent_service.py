"""Consentimiento del mapa comunitario anónimo."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.user import User


def ensure_map_consent(db: Session, user: User) -> None:
    """Garantiza consentimiento de mapa para abrir incidencias.

    El registro exige aceptar el mapa anónimo; filas antiguas pueden tener
    ``consent_accepted_at`` nulo y se rellenan en la primera incidencia.
    """
    if user.consent_accepted_at is not None:
        return
    if user.role != "farmer":
        raise ValueError("Se requiere consentimiento de mapa anónimo para abrir incidencias")
    user.consent_accepted_at = datetime.now(timezone.utc)
    db.add(user)
    db.flush()
