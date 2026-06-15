"""Notificaciones — stub FCM (Fase 5). Sustituir por Firebase Admin SDK en producción."""

from app.models.alert import Alert


def notify_alert_created(alert: Alert) -> None:
    message = (
        f"[alert:{alert.alert_type}] zona={alert.zone_id} "
        f"plaga={alert.plague} prioridad={alert.priority_score} — {alert.description}"
    )
    print(f"[notification] {message}")


def send_push_to_user(user_id: int, title: str, body: str) -> None:
    print(f"[notification] push user={user_id} title={title!r} body={body!r}")
