"""Rate limiting simple en memoria para endpoints de auth."""

from __future__ import annotations

import time
from collections import defaultdict

from fastapi import HTTPException, status

_buckets: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(key: str, *, max_attempts: int = 10, window_seconds: int = 60) -> None:
    now = time.time()
    recent = [ts for ts in _buckets[key] if now - ts < window_seconds]
    if len(recent) >= max_attempts:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos. Espera un minuto e inténtalo de nuevo.",
        )
    recent.append(now)
    _buckets[key] = recent
