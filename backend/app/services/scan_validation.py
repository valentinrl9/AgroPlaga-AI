"""Estado de validación perito de un escaneo (tratamientos / SIEX)."""

from __future__ import annotations

from app.models.scan import Scan

VERIFIED_STATUSES = frozenset({"confirmed", "corrected"})


def is_scan_verified(scan: Scan | None) -> bool:
    if scan is None:
        return True
    return (scan.tech_status or "").strip().lower() in VERIFIED_STATUSES


def is_scan_rejected(scan: Scan | None) -> bool:
    if scan is None:
        return False
    return (scan.tech_status or "").strip().lower() == "rejected"


def effective_plague(scan: Scan | None, fallback: str | None = None) -> str:
    if scan is None:
        return (fallback or "plaga no indicada").strip().lower()
    if scan.corrected_plague:
        return scan.corrected_plague.strip().lower()
    return scan.plague.strip().lower()


def verification_label(scan: Scan | None) -> str:
    if scan is None:
        return "none"
    if is_scan_rejected(scan):
        return "rejected"
    if is_scan_verified(scan):
        return "verified"
    return "unverified"
