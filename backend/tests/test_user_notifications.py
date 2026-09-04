"""Tests notificaciones agricultor (Fases 1–3)."""

import pytest

from tests.conftest import auth_headers, register_and_login


def _jpeg_bytes() -> bytes:
    return bytes.fromhex(
        "ffd8ffe000104a46494600010100000100010000ffdb004300080606070605080707"
        "070908090a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c"
        "1c2837292c30313434341f27393d38323c2e333432ffdb0043010909090c0b0c180d0d"
        "1832211c2132323232323232323232323232323232323232323232323232323232323232"
        "323232323232323232323232323232323232323c0a2834001108df0450100301100002"
        "011101c2100000000110010002011101c210000000011000fc0000003fffd9"
    )


def _admin_headers(client):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "admin1234"},
    )
    if login.status_code != 200:
        pytest.skip("Admin seed user not available")
    return auth_headers(login.json()["access_token"])


def test_validate_scan_notifies_farmer(client, unique_email):
    farmer_token = register_and_login(client, unique_email)
    farmer_headers = auth_headers(farmer_token)
    admin_headers = _admin_headers(client)

    scan_resp = client.post(
        "/api/v1/scans/with-image",
        headers=farmer_headers,
        data={
            "crop": "tomate",
            "plague": "trips",
            "confidence": "0.8",
            "severity": "2",
            "share_with_tech": "true",
        },
        files={"image": ("scan.jpg", _jpeg_bytes(), "image/jpeg")},
    )
    assert scan_resp.status_code == 201, scan_resp.text
    scan_id = scan_resp.json()["id"]

    validate = client.patch(
        f"/api/v1/scans/{scan_id}/validate",
        headers=admin_headers,
        json={"action": "confirm"},
    )
    assert validate.status_code == 200, validate.text

    summary = client.get("/api/v1/me/activity-summary", headers=farmer_headers)
    assert summary.status_code == 200, summary.text
    body = summary.json()
    assert body["unread_count"] >= 1
    assert body["sections"].get("history", 0) >= 1

    notifs = client.get("/api/v1/me/notifications?unread_only=true", headers=farmer_headers)
    assert notifs.status_code == 200
    assert any(n["notification_type"] == "scan_confirmed" for n in notifs.json())

    mark = client.patch("/api/v1/me/notifications/sections/history/read", headers=farmer_headers)
    assert mark.status_code == 200
    assert mark.json()["marked_read"] >= 1


def test_activity_summary_shape(client, unique_email):
    token = register_and_login(client, unique_email)
    headers = auth_headers(token)
    resp = client.get("/api/v1/me/activity-summary", headers=headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "weekly_vigilance" in data
    assert "streak_weeks" in data
    assert "pilot_collective" in data
    assert data["weekly_vigilance"]["streak_weeks"] >= 0
