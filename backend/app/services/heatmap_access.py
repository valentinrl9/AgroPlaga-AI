"""Control de acceso freemium/premium al mapa de calor."""

from fastapi import HTTPException, status

from app.models.user import User

FREEMIUM_MAX_HOURS = 24
PREMIUM_HOURS = (24, 168, 720)
MAX_HOURS = 720
B2B_ROLES = frozenset({"tech", "admin"})


def map_access_profile(user: User) -> dict:
    if user.role in B2B_ROLES or user.has_field_premium:
        return {
            "historical_enabled": True,
            "max_hours": MAX_HOURS,
            "allowed_hours": list(PREMIUM_HOURS),
            "default_hours": 168,
        }
    return {
        "historical_enabled": False,
        "max_hours": FREEMIUM_MAX_HOURS,
        "allowed_hours": [FREEMIUM_MAX_HOURS],
        "default_hours": FREEMIUM_MAX_HOURS,
    }


def enforce_map_hours(user: User, requested_hours: int) -> int:
    profile = map_access_profile(user)
    if requested_hours > profile["max_hours"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El histórico de 7 y 30 días requiere Field Premium",
        )
    return requested_hours
