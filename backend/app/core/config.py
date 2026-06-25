import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_DEFAULT_SCAN_DIR = Path(__file__).resolve().parents[2] / "data" / "scans"

class Settings:
    app_name: str = os.getenv("APP_NAME", "AgroPlaga AI")
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    registration_mode: str = os.getenv("REGISTRATION_MODE", "open").strip().lower()
    cors_origins: list[str] = [
        origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()
    ] or [
        "http://localhost",
        "http://127.0.0.1",
    ]
    _cors_regex = os.getenv("CORS_ORIGIN_REGEX")
    cors_origin_regex: str | None = (
        None if _cors_regex == "none" else (_cors_regex or r"https?://(localhost|127\.0\.0\.1)(:\d+)?")
    )
    scan_images_dir: str = os.getenv("SCAN_IMAGES_DIR", str(_DEFAULT_SCAN_DIR))

settings = Settings()
