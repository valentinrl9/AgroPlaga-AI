"""Cuentas demo fijas para pruebas locales (upsert en cada arranque)."""

import os

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.user import User

DEFAULT_PASSWORD = os.getenv("DEMO_USERS_PASSWORD", "nexo1234")

LOCAL_DEMO_USERS: tuple[dict, ...] = (
    {
        "email": "local.agricultor@nexo.test",
        "name": "Demo Agricultor",
        "role": "farmer",
        "has_field_premium": True,
        "has_climate_module": True,
        "has_siex_module": True,
        "has_siex_enterprise": False,
    },
    {
        "email": "local.perito@nexo.test",
        "name": "Demo Perito",
        "role": "tech",
        "has_field_premium": True,
        "has_climate_module": True,
        "has_siex_module": True,
        "has_siex_enterprise": False,
    },
    {
        "email": "local.cooperativa@nexo.test",
        "name": "Demo Cooperativa",
        "role": "tech",
        "has_field_premium": True,
        "has_climate_module": True,
        "has_siex_module": True,
        "has_siex_enterprise": True,
    },
)


def seed_local_demo_users() -> None:
    if os.getenv("DEMO_SEED_USERS", "true").strip().lower() not in {"1", "true", "yes"}:
        return

    password = os.getenv("DEMO_USERS_PASSWORD", DEFAULT_PASSWORD).strip()
    if not password:
        return

    db = SessionLocal()
    try:
        hashed = get_password_hash(password)
        for spec in LOCAL_DEMO_USERS:
            email = spec["email"].strip().lower()
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                existing.name = spec["name"]
                existing.role = spec["role"]
                existing.hashed_password = hashed
                existing.has_field_premium = spec["has_field_premium"]
                existing.has_climate_module = spec["has_climate_module"]
                existing.has_siex_module = spec["has_siex_module"]
                existing.has_siex_enterprise = spec["has_siex_enterprise"]
            else:
                db.add(
                    User(
                        name=spec["name"],
                        email=email,
                        hashed_password=hashed,
                        role=spec["role"],
                        has_field_premium=spec["has_field_premium"],
                        has_climate_module=spec["has_climate_module"],
                        has_siex_module=spec["has_siex_module"],
                        has_siex_enterprise=spec["has_siex_enterprise"],
                    )
                )
        db.commit()
    finally:
        db.close()
