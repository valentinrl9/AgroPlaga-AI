import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_DEFAULT_SCAN_DIR = Path(__file__).resolve().parents[2] / "data" / "scans"
_INSECURE_SECRET_KEYS = frozenset({"change-me-in-production", "secret", "changeme", "dev"})


class Settings:
    app_name: str = os.getenv("APP_NAME", "NEXO Agro")
    environment: str = os.getenv("ENVIRONMENT", "development").strip().lower()
    allow_insecure_secrets: bool = os.getenv("ALLOW_INSECURE_SECRETS", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    registration_mode: str = os.getenv("REGISTRATION_MODE", "open").strip().lower()
    docs_enabled: bool = os.getenv("DOCS_ENABLED", "true").strip().lower() in {"1", "true", "yes"}
    max_scan_images_per_user: int = int(os.getenv("MAX_SCAN_IMAGES_PER_USER", "200"))
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

    contact_notify_email: str = os.getenv("CONTACT_NOTIFY_EMAIL", "valentinruizleon@gmail.com").strip()
    smtp_host: str = os.getenv("SMTP_HOST", "").strip()
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "").strip()
    smtp_password: str = os.getenv("SMTP_PASSWORD", "").strip()
    smtp_from: str = os.getenv("SMTP_FROM", "").strip()
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").strip().lower() in {"1", "true", "yes"}

    @property
    def is_production(self) -> bool:
        return self.environment in {"production", "prod", "pilot"}


def validate_settings() -> None:
    """Fail fast on insecure production configuration."""
    if settings.is_production and not settings.allow_insecure_secrets:
        if settings.secret_key in _INSECURE_SECRET_KEYS or len(settings.secret_key) < 32:
            raise RuntimeError(
                "SECRET_KEY must be a random string of at least 32 characters in production. "
                "Set SECRET_KEY in the environment before starting the API."
            )
        if settings.registration_mode == "open":
            raise RuntimeError(
                "REGISTRATION_MODE=open is not allowed in production. Use invite_only."
            )


settings = Settings()
