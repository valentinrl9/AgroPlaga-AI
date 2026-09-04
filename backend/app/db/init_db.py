import os
import time
from datetime import datetime, timezone
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import text

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.seed_zones import load_almeria_municipalities
from app.db.session import SessionLocal, engine
from app.db.seed_pilot_invites import seed_pilot_invites
from app.db.seed_climate_stations import seed_climate_stations
from app.db.seed_demo_users import seed_local_demo_users
from app.models import user, scan, feedback, zone, outbreak_event, alert, alert_preference, user_badge, farm, contribution_log, pilot_invite, climate, climate_station, pest_incident, farm_treatment, biocide_product, siex_entry, user_notification
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
        for entry in load_almeria_municipalities():
            zone = (
                db.query(AgriZone)
                .filter(AgriZone.municipality_code == entry["municipality_code"])
                .first()
            )
            centroid = point_wkt(entry["lon"], entry["lat"])
            if zone:
                zone.sigpac_code = entry["sigpac_code"]
                zone.name = entry["name"]
                zone.province = entry["province"]
                zone.centroid = centroid
            else:
                db.add(
                    AgriZone(
                        sigpac_code=entry["sigpac_code"],
                        name=entry["name"],
                        province=entry["province"],
                        municipality_code=entry["municipality_code"],
                        centroid=centroid,
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
        now = datetime.now(timezone.utc)
        if not existing_admin:
            admin = User(
                name=admin_name,
                email=admin_email,
                hashed_password=get_password_hash(admin_password),
                role="admin",
                consent_accepted_at=now,
            )
            db.add(admin)
            db.commit()
        elif existing_admin.consent_accepted_at is None:
            existing_admin.consent_accepted_at = now
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

    force_reset = os.getenv("MASTER_FORCE_RESET", "false").strip().lower() in {"1", "true", "yes"}

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        now = datetime.now(timezone.utc)
        if existing:
            existing.name = name
            existing.role = "admin"
            if force_reset:
                existing.hashed_password = get_password_hash(password)
            existing.has_field_premium = True
            existing.has_climate_module = True
            existing.has_siex_module = True
            existing.has_siex_enterprise = True
            if existing.consent_accepted_at is None:
                existing.consent_accepted_at = now
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
                    consent_accepted_at=now,
                )
            )
        db.commit()
    finally:
        db.close()


def seed_mapa_biocide_stubs() -> None:
    """Garantiza productos MAPA de demo para CRM/tratamientos (upsert mínimo)."""
    from app.models.biocide_product import BiocideProduct

    stubs = [
        ("ES-00001", "Spintor 480 SC", "spinosad", "tuta absoluta", "tomate", 0.06, 0.09, 72),
        ("ES-00002", "Confidor 200 SL", "imidacloprid", "mosca blanca", "tomate", 0.3, 0.5, 48),
        ("ES-00003", "Vertimec 1.8 EC", "abamectina", "arañuela roja", "tomate", 0.2, 0.3, 48),
        ("ES-00004", "Previcur Energy", "propamocarb", "mildiu", "tomate", 1.5, 2.0, 120),
        ("ES-00005", "Amistar", "azoxistrobin", "oídio", "tomate", 0.6, 0.8, 96),
        ("ES-00006", "Amistar", "azoxistrobin", "oídio", "calabacín", 0.6, 0.8, 96),
        ("ES-00007", "VACCIPLANT MAX", "Bacillus subtilis", "oídio", "calabacín", 0.25, 0.35, 24),
        ("ES-00008", "Serenade ASO", "Bacillus subtilis QST713", "oídio", "calabacín", 0.4, 0.6, 24),
        ("ES-00009", "Kumulus DF", "azufre", "oídio", "calabacín", 2.0, 3.0, 48),
        ("ES-00010", "Previcur Energy", "propamocarb", "oídio", "calabacín", 1.2, 1.8, 120),
    ]

    db = SessionLocal()
    try:
        for reg, name, substance, plague, crop, dmin, dmax, safety in stubs:
            existing = (
                db.query(BiocideProduct)
                .filter(
                    BiocideProduct.registry_no == reg,
                    BiocideProduct.plague == plague,
                    BiocideProduct.crop == crop,
                )
                .first()
            )
            if existing is not None:
                continue
            db.add(
                BiocideProduct(
                    registry_no=reg,
                    name=name,
                    active_substance=substance,
                    plague=plague,
                    crop=crop,
                    dose_min_l_ha=dmin,
                    dose_max_l_ha=dmax,
                    safety_hours=safety,
                    product_status="vigente",
                    source="mapa_cex",
                )
            )
        db.commit()
    finally:
        db.close()


def init_db() -> None:
    run_migrations()
    seed_sigpac_zones()
    seed_mapa_biocide_stubs()
    seed_climate_stations()
    seed_admin_user()
    seed_master_user()
    seed_local_demo_users()
    if os.getenv("PILOT_SEED_INVITES", "").strip().lower() in {"1", "true", "yes"}:
        seed_pilot_invites()
