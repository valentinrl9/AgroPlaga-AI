"""Notificaciones push (FCM) y alertas comarcales."""

from __future__ import annotations

import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.alert import Alert

logger = logging.getLogger(__name__)
_firebase_initialized = False


def _init_firebase() -> bool:
    global _firebase_initialized
    if _firebase_initialized:
        return True
    if not settings.fcm_enabled:
        return False

    cred_path = settings.firebase_credentials
    if not cred_path or not Path(cred_path).is_file():
        logger.warning("FCM_ENABLED but FIREBASE_CREDENTIALS missing or not a file")
        return False

    try:
        import firebase_admin
        from firebase_admin import credentials

        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials.Certificate(cred_path))
        _firebase_initialized = True
        return True
    except Exception:
        logger.exception("Failed to initialize Firebase Admin SDK")
        return False


def notify_alert_created(db: Session, alert: Alert) -> None:
    from app.services.alert_notification_service import notify_users_for_comarcal_alert

    count = notify_users_for_comarcal_alert(db, alert)
    logger.info(
        "[notification] alert:%s zone=%s plague=%s notified_users=%s",
        alert.alert_type,
        alert.zone_id,
        alert.plague,
        count,
    )


def send_push_to_user(
    db: Session,
    user_id: int,
    title: str,
    body: str,
    *,
    data: dict[str, str] | None = None,
) -> None:
    payload_data = {k: str(v) for k, v in (data or {}).items()}

    if not settings.fcm_enabled or not _init_firebase():
        logger.info(
            "[notification] push stub user=%s title=%r body=%r data=%s",
            user_id,
            title,
            body,
            payload_data or None,
        )
        return

    from firebase_admin import messaging

    from app.services.device_token_service import delete_token, list_tokens_for_user

    tokens = list_tokens_for_user(db, user_id)
    if not tokens:
        logger.debug("No FCM tokens for user=%s", user_id)
        return

    for row in tokens:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data=payload_data,
            token=row.token,
            android=messaging.AndroidConfig(priority="high"),
        )
        try:
            messaging.send(message)
        except messaging.UnregisteredError:
            delete_token(db, row.token)
        except Exception:
            logger.warning("FCM send failed user=%s token=%s…", user_id, row.token[:12], exc_info=True)
