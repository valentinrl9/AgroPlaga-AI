"""Tests preferencias y dispatch notificaciones (Fase 5)."""

from datetime import datetime
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

from app.models.user_notification_preference import UserNotificationPreference
from app.services.notification_preference_service import in_quiet_hours, push_enabled_for_type
from tests.conftest import auth_headers, register_and_login


def test_notification_preferences_defaults(client, unique_email):
    token = register_and_login(client, unique_email)
    headers = auth_headers(token)

    resp = client.get("/api/v1/me/notification-preferences", headers=headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["push_scan_validation"] is True
    assert body["push_alerts_comarcal"] is False
    assert body["quiet_hours_enabled"] is True
    assert body["quiet_hours_start"] == 22
    assert body["quiet_hours_end"] == 7


def test_notification_preferences_update(client, unique_email):
    token = register_and_login(client, unique_email)
    headers = auth_headers(token)

    resp = client.patch(
        "/api/v1/me/notification-preferences",
        headers=headers,
        json={
            "push_alerts_comarcal": True,
            "push_badges": False,
            "quiet_hours_start": 23,
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["push_alerts_comarcal"] is True
    assert body["push_badges"] is False
    assert body["quiet_hours_start"] == 23


def test_quiet_hours_overnight_window():
    row = UserNotificationPreference(
        user_id=1,
        quiet_hours_enabled=True,
        quiet_hours_start=22,
        quiet_hours_end=7,
    )
    night = datetime(2026, 9, 6, 23, 0, tzinfo=ZoneInfo("Europe/Madrid"))
    noon = datetime(2026, 9, 6, 12, 0, tzinfo=ZoneInfo("Europe/Madrid"))
    assert in_quiet_hours(row, night) is True
    assert in_quiet_hours(row, noon) is False


def test_push_enabled_for_type_mapping():
    row = UserNotificationPreference(user_id=1, push_scan_validation=False)
    assert push_enabled_for_type(row, "scan_confirmed") is False
    assert push_enabled_for_type(row, "incident_reminder") is True


def test_create_notification_respects_send_push_flag():
    from app.services.user_notification_service import create_user_notification

    db = MagicMock()
    db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

    with patch("app.services.user_notification_service.dispatch_push") as mock_dispatch:
        create_user_notification(
            db,
            user_id=1,
            notification_type="alert_comarcal",
            title="Test",
            body="Body",
            dedupe_key="alert:1",
            skip_dedupe=True,
            send_push=False,
        )
        mock_dispatch.assert_not_called()

        mock_dispatch.reset_mock()
        create_user_notification(
            db,
            user_id=1,
            notification_type="alert_comarcal",
            title="Test",
            body="Body",
            dedupe_key="alert:2",
            skip_dedupe=True,
            send_push=True,
        )
        mock_dispatch.assert_called_once()
