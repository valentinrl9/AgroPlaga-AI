"""Códigos del piloto Lean (7 agricultores + 2 técnicos + 1 cooperativa)."""

from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.models.pilot_invite import PilotInvite

DEFAULT_PILOT_INVITES: list[dict] = [
    {"code": "PLG-PILOT-F01", "role": "farmer", "label": "Agricultor piloto 1"},
    {"code": "PLG-PILOT-F02", "role": "farmer", "label": "Agricultor piloto 2"},
    {"code": "PLG-PILOT-F03", "role": "farmer", "label": "Agricultor piloto 3"},
    {"code": "PLG-PILOT-F04", "role": "farmer", "label": "Agricultor piloto 4"},
    {"code": "PLG-PILOT-F05", "role": "farmer", "label": "Agricultor piloto 5"},
    {"code": "PLG-PILOT-F06", "role": "farmer", "label": "Agricultor piloto 6"},
    {"code": "PLG-PILOT-F07", "role": "farmer", "label": "Agricultor piloto 7"},
    {"code": "PLG-PILOT-T01", "role": "tech", "label": "Técnico / perito 1"},
    {"code": "PLG-PILOT-T02", "role": "tech", "label": "Técnico / perito 2"},
    {"code": "PLG-PILOT-C01", "role": "tech", "label": "Cooperativa (panel web + validación)"},
]

# Fin del piloto Lean (~8 semanas desde despliegue; ajustar en VPS si hace falta)
PILOT_INVITES_EXPIRE_AT = datetime(2026, 8, 15, 23, 59, 59, tzinfo=timezone.utc)


def seed_pilot_invites() -> None:
    db = SessionLocal()
    try:
        if db.query(PilotInvite).count() > 0:
            return
        for entry in DEFAULT_PILOT_INVITES:
            db.add(
                PilotInvite(
                    code=entry["code"],
                    role=entry["role"],
                    label=entry["label"],
                    max_uses=1,
                    expires_at=PILOT_INVITES_EXPIRE_AT,
                )
            )
        db.commit()
    finally:
        db.close()
