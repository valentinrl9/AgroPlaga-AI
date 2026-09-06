"""Envío push con preferencias, quiet hours y anti-spam (Fase 5)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.notification_preference_service import (
    log_push,
    maybe_group_push,
    should_send_push,
)
from app.services.notification_service import send_push_to_user
from app.services.user_notification_service import unread_count


def dispatch_push(
    db: Session,
    user_id: int,
    notification_type: str,
    title: str,
    body: str,
    *,
    data: dict[str, str] | None = None,
) -> None:
    ok, _reason = should_send_push(db, user_id, notification_type)
    if not ok:
        return

    payload = dict(data or {})
    payload.setdefault("type", notification_type)

    if maybe_group_push(db, user_id, notification_type, unread_count(db, user_id)):
        grouped_title = "Avisos pendientes"
        grouped_body = f"Tienes {unread_count(db, user_id)} aviso(s) sin leer en AgroPlaga"
        send_push_to_user(
            db,
            user_id,
            grouped_title,
            grouped_body,
            data={
                "type": "grouped",
                "section": "home",
            },
        )
        log_push(db, user_id, "grouped", is_grouped=True)
        return

    send_push_to_user(db, user_id, title, body, data=payload)
    log_push(db, user_id, notification_type, is_grouped=False)
