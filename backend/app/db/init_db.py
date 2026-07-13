import os
import time
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import text

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.seed_zones import SIGPAC_ZONES
from app.db.session import SessionLocal, engine
from app.db.seed_pilot_invites import seed_pilot_invites
from app.db.seed_demo_users import seed_local_demo_users
from app.models import user, scan, feedback, zone, outbreak_event, alert, alert_preference, user_badge, farm, contribution_log, pilot_invite, climate, farm_treatment, biocide_product, siex_entry
from app.models.user import User
from app.models.zone import AgriZone
from app.services.geo_service import point_wkt


def wait_for_db(max_retries: int = 12, delay: float = 2.0) -> None:
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return
        except Exception as exc:
            last_error = exc
            time.sleep(delay)
    raise RuntimeError(f"Database is not available after {max_retries} attempts") from last_error


def run_migrations() -> None:
    wait_for_db()
    alembic_cfg = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
    command.upgrade(alembic_cfg, "head")


def seed_sigpac_zones() -> None:
    db = SessionLocal()
    try:
        if db.query(AgriZone).count() > 0:
            return
        for entry in SIGPAC_ZONES:
            db.add(
                AgriZone(
                    sigpac_code=entry["sigpac_code"],
                    name=entry["name"],
                    province=entry["province"],
                    municipality_code=entry["municipality_code"],
                    centroid=point_wkt(entry["lon"], entry["lat"]),
                )
            )
        db.commit()
    finally:
        db.close()


def seed_admin_user() -> None:
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin_name = os.getenv("ADMIN_NAME", "Admin")

    if not admin_email or not admin_password:
        return

    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.role == "admin").first()
        if not existing_admin:
            admin = User(
                name=admin_name,
                email=admin_email,
                hashed_password=get_password_hash(admin_password),
                role="admin",
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


def seed_master_user() -> None:
    """Cuenta demo/maestro para entrevistas B2B (upsert por email)."""
    email = os.getenv("MASTER_EMAIL", "").strip().lower()
    password = os.getenv("MASTER_PASSWORD", "")
    name = os.getenv("MASTER_NAME", "Master Demo")

    if not email or not password:
        return

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            existing.name = name
            existing.role = "admin"
            existing.hashed_password = get_password_hash(password)
            existing.has_field_premium = True
            existing.has_climate_module = True
            existing.has_siex_module = True
            existing.has_siex_enterprise = True
        else:
            db.add(
                User(
                    name=name,
                    email=email,
                    hashed_password=get_password_hash(password),
                    role="admin",
                    has_field_premium=True,
                    has_climate_module=True,
                    has_siex_module=True,
                    has_siex_enterprise=True,
                )
            )
        db.commit()
    finally:
        db.close()


def init_db() -> None:
    run_migrations()
    seed_sigpac_zones()
    seed_admin_user()
    seed_master_user()
    seed_local_demo_users()
    if os.getenv("PILOT_SEED_INVITES", "").strip().lower() in {"1", "true", "yes"}:
        seed_pilot_invites()
