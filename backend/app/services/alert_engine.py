"""Motor de alertas tempranas — Fase 5."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Iterable

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.outbreak_event import OutbreakEvent
from app.models.zone import AgriZone
from app.services.notification_service import notify_alert_created

SPIKE_PCT_THRESHOLD = 0.35
ZSCORE_THRESHOLD = 2.0
SEVERITY_AVG_THRESHOLD = 2.5
MIN_EVENTS_FOR_SEVERITY = 2
DEDUP_HOURS = 24
ALERT_TTL_DAYS = 14


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _count_events(
    db: Session,
    zone_id: int,
    plague: str,
    since: datetime,
    until: datetime | None = None,
) -> int:
    query = db.query(func.count(OutbreakEvent.id)).filter(
        OutbreakEvent.zone_id == zone_id,
        OutbreakEvent.plague == plague,
        OutbreakEvent.reported_at >= since,
    )
    if until is not None:
        query = query.filter(OutbreakEvent.reported_at < until)
    return query.scalar() or 0


def _severity_stats(
    db: Session,
    zone_id: int,
    plague: str,
    since: datetime,
    until: datetime | None = None,
) -> tuple[float, int, int]:
    query = db.query(
        func.avg(OutbreakEvent.severity),
        func.max(OutbreakEvent.severity),
        func.count(OutbreakEvent.id),
    ).filter(
        OutbreakEvent.zone_id == zone_id,
        OutbreakEvent.plague == plague,
        OutbreakEvent.reported_at >= since,
    )
    if until is not None:
        query = query.filter(OutbreakEvent.reported_at < until)
    avg_sev, max_sev, count = query.one()
    return float(avg_sev or 0), int(max_sev or 0), int(count or 0)


def _daily_counts(
    db: Session,
    zone_id: int,
    plague: str,
    start: datetime,
    days: int,
) -> list[int]:
    counts: list[int] = []
    for offset in range(days):
        day_start = start + timedelta(days=offset)
        day_end = day_start + timedelta(days=1)
        counts.append(_count_events(db, zone_id, plague, day_start, day_end))
    return counts


def _zscore(current: float, historical: Iterable[float]) -> float:
    values = list(historical)
    if len(values) < 3:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    std = math.sqrt(variance)
    if std < 0.01:
        return 0.0 if current <= mean else ZSCORE_THRESHOLD
    return (current - mean) / std


def compute_priority_score(max_severity: int, increment_ratio: float) -> float:
    severity_norm = max(0.0, min(1.0, (max_severity - 1) / 2))
    increment_norm = max(0.0, min(1.0, increment_ratio - 1.0))
    return round(severity_norm * 0.6 + increment_norm * 0.4, 2)


def _has_recent_duplicate(
    db: Session,
    zone_id: int,
    plague: str,
    alert_type: str,
) -> bool:
    since = _utcnow() - timedelta(hours=DEDUP_HOURS)
    exists = (
        db.query(Alert.id)
        .filter(
            Alert.zone_id == zone_id,
            Alert.plague == plague,
            Alert.alert_type == alert_type,
            Alert.active.is_(True),
            Alert.created_at >= since,
        )
        .first()
    )
    return exists is not None


def _persist_alert(
    db: Session,
    *,
    zone_id: int,
    plague: str,
    alert_type: str,
    description: str,
    priority_score: float,
) -> Alert | None:
    if _has_recent_duplicate(db, zone_id, plague, alert_type):
        return None

    alert = Alert(
        zone_id=zone_id,
        plague=plague,
        alert_type=alert_type,
        description=description,
        priority_score=priority_score,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    notify_alert_created(alert)
    return alert


def _zone_name(db: Session, zone_id: int) -> str:
    zone = db.query(AgriZone).filter(AgriZone.id == zone_id).first()
    return zone.name if zone else "zona desconocida"


def evaluate_zone_plague(db: Session, zone_id: int, plague: str) -> list[Alert]:
    now = _utcnow()
    created: list[Alert] = []
    zone_name = _zone_name(db, zone_id)

    count_48h = _count_events(db, zone_id, plague, now - timedelta(hours=48))
    if count_48h == 0:
        return created

    baseline_start = now - timedelta(days=16)
    daily_history = _daily_counts(db, zone_id, plague, baseline_start, 14)
    daily_avg = sum(daily_history) / len(daily_history) if daily_history else 0
    expected_48h = max(daily_avg * 2, 0.5)
    increment_ratio = count_48h / expected_48h
    pct = int(max(0, increment_ratio - 1) * 100)
    zscore = _zscore(float(count_48h), daily_history)

    _, max_sev_48h, _ = _severity_stats(db, zone_id, plague, now - timedelta(hours=48))

    if increment_ratio >= 1 + SPIKE_PCT_THRESHOLD or zscore >= ZSCORE_THRESHOLD:
        priority = compute_priority_score(max_sev_48h or 2, increment_ratio)
        description = (
            f"Aumento del {max(pct, 35)}% de {plague} en {zone_name} "
            f"en las últimas 48 h (Z={zscore:.1f})."
        )
        alert = _persist_alert(
            db,
            zone_id=zone_id,
            plague=plague,
            alert_type="spike",
            description=description,
            priority_score=priority,
        )
        if alert:
            created.append(alert)

    count_prev_30d = _count_events(
        db,
        zone_id,
        plague,
        now - timedelta(days=37),
        now - timedelta(days=7),
    )
    count_7d = _count_events(db, zone_id, plague, now - timedelta(days=7))
    if count_7d > 0 and count_prev_30d == 0:
        _, max_sev_7d, _ = _severity_stats(db, zone_id, plague, now - timedelta(days=7))
        priority = compute_priority_score(max_sev_7d or 2, 1.5)
        description = (
            f"Nueva detección de {plague} en {zone_name}: "
            f"{count_7d} reporte(s) en los últimos 7 días."
        )
        alert = _persist_alert(
            db,
            zone_id=zone_id,
            plague=plague,
            alert_type="new_plague",
            description=description,
            priority_score=priority,
        )
        if alert:
            created.append(alert)

    avg_sev, max_sev, event_count = _severity_stats(
        db, zone_id, plague, now - timedelta(hours=48)
    )
    if event_count >= MIN_EVENTS_FOR_SEVERITY and (
        avg_sev >= SEVERITY_AVG_THRESHOLD or max_sev >= 3
    ):
        priority = compute_priority_score(max_sev, max(1.2, avg_sev / 2))
        description = (
            f"Severidad acumulada alta de {plague} en {zone_name}: "
            f"media {avg_sev:.1f}/3 en {event_count} reporte(s) (48 h)."
        )
        alert = _persist_alert(
            db,
            zone_id=zone_id,
            plague=plague,
            alert_type="severity_surge",
            description=description,
            priority_score=priority,
        )
        if alert:
            created.append(alert)

    return created


def deactivate_stale_alerts(db: Session) -> int:
    cutoff = _utcnow() - timedelta(days=ALERT_TTL_DAYS)
    updated = (
        db.query(Alert)
        .filter(Alert.active.is_(True), Alert.created_at < cutoff)
        .update({"active": False}, synchronize_session=False)
    )
    db.commit()
    return updated


def run_alert_scan(db: Session) -> int:
    now = _utcnow()
    since = now - timedelta(days=7)
    pairs = (
        db.query(OutbreakEvent.zone_id, OutbreakEvent.plague)
        .filter(OutbreakEvent.reported_at >= since)
        .distinct()
        .all()
    )

    created_count = 0
    for zone_id, plague in pairs:
        alerts = evaluate_zone_plague(db, zone_id, plague)
        created_count += len(alerts)

    deactivate_stale_alerts(db)
    return created_count
