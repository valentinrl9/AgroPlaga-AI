"""Envío push con preferencias, quiet hours y anti-spam (Fase 5)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.notification_preference_service import (
    log_push,
    maybe_group_push,
    should_send_push,
)
from app.services.notification_service import send_push_to_user


def dispatch_push(
    db: Session,
    user_id: int,
    notification_type: str,
    title: str,
    body: str,
    *,
    data: dict[str, str] | None = None,
) -> None:
    from app.services.user_notification_service import unread_count

    ok, _reason = should_send_push(db, user_id, notification_type)
    if not ok:
        return

    payload = dict(data or {})
    payload.setdefault("type", notification_type)
    pending = unread_count(db, user_id)

    if maybe_group_push(db, user_id, notification_type, pending):
        send_push_to_user(
            db,
            user_id,
            "Avisos pendientes",
            f"Tienes {pending} aviso(s) sin leer en AgroPlaga",
            data={
                "type": "grouped",
                "section": "home",
            },
        )
        log_push(db, user_id, "grouped", is_grouped=True)
        return

    send_push_to_user(db, user_id, title, body, data=payload)
    log_push(db, user_id, notification_type, is_grouped=False)
