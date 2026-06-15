import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    app_name: str = os.getenv("APP_NAME", "AgroPlaga AI")
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    cors_origins: list[str] = [
        origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()
    ] or [
        "http://localhost",
        "http://127.0.0.1",
    ]
    cors_origin_regex: str | None = os.getenv("CORS_ORIGIN_REGEX") or r"https?://(localhost|127\.0\.0\.1)(:\d+)?"

settings = Settings()
