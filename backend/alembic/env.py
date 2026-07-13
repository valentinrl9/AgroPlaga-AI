import os
import sys
from logging.config import fileConfig

from dotenv import load_dotenv
from alembic import context
from sqlalchemy import engine_from_config, pool

# Load environment file if present
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(CURRENT_DIR, "..", ".env"))

# Add backend directory to Python path to import the app package
sys.path.append(os.path.abspath(os.path.join(CURRENT_DIR, "..")))

from app.db.base import Base
from app.models import user, scan, feedback, zone, outbreak_event, alert, climate, farm_treatment, biocide_product, siex_entry  # noqa: F401

config = context.config
fileConfig(config.config_file_name)

config.set_main_option(
    "sqlalchemy.url",
    os.getenv("DATABASE_URL", "sqlite:///./app.db"),
)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
