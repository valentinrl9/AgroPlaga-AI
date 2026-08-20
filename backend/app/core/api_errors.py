"""Helpers for safe API error responses."""

from fastapi import HTTPException


def safe_http_error(exc: Exception, *, public_message: str = "Error interno del servidor") -> HTTPException:
    """Return a generic client message; avoid leaking stack traces or DB details."""
    return HTTPException(status_code=500, detail=public_message)
