"""Notificaciones in-app/push por alertas comarcales (Fase 5)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.alert_preference import UserAlertPreference
from app.models.farm import Farm
from app.models.zone import AgriZone
from app.services.notification_preference_service import get_or_create_preferences
from app.services.user_notification_service import create_user_notification


def _zone_name(db: Session, zone_id: int) -> str:
    zone = db.query(AgriZone).filter(AgriZone.id == zone_id).first()
    return zone.name if zone else "tu zona"


def _user_wants_plague(db: Session, user_id: int, plague: str) -> bool:
    prefs = db.query(UserAlertPreference).filter(UserAlertPreference.user_id == user_id).all()
    if not prefs:
        return True
    enabled = {pref.plague for pref in prefs if pref.enabled}
    return plague in enabled


def _users_in_zone(db: Session, zone_id: int) -> list[int]:
    rows = db.query(Farm.user_id).filter(Farm.zone_id == zone_id).distinct().all()
    return [row[0] for row in rows]


def notify_users_for_comarcal_alert(db: Session, alert: Alert) -> int:
    """Crea notificación in-app; push solo si opt-in comarcal."""
    if alert.zone_id is None:
        return 0

    created = 0
    zone_label = _zone_name(db, alert.zone_id)
    for user_id in _users_in_zone(db, alert.zone_id):
        if not _user_wants_plague(db, user_id, alert.plague):
            continue

        prefs = get_or_create_preferences(db, user_id)
        title = f"Alerta comarcal · {alert.plague}"
        body = alert.description or f"Actividad de {alert.plague} en {zone_label}."

        row = create_user_notification(
            db,
            user_id=user_id,
            notification_type="alert_comarcal",
            title=title,
            body=body,
            section="alerts",
            reference_type="alert",
            reference_id=alert.id,
            dedupe_key=f"alert_comarcal:{alert.id}",
            skip_dedupe=True,
            send_push=prefs.push_alerts_comarcal,
        )
        if row is not None:
            created += 1
    return created
