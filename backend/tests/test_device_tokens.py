"""Tests FCM device tokens (Fase 4)."""

from tests.conftest import auth_headers, register_and_login


def test_register_device_token(client, unique_email):
    token = register_and_login(client, unique_email)
    headers = auth_headers(token)

    resp = client.post(
        "/api/v1/me/device-token",
        headers=headers,
        json={"token": "fcm-test-token-abc123456789", "platform": "android"},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["platform"] == "android"
    assert "updated_at" in body

    # Upsert same token for same user
    resp2 = client.post(
        "/api/v1/me/device-token",
        headers=headers,
        json={"token": "fcm-test-token-abc123456789", "platform": "android"},
    )
    assert resp2.status_code == 201, resp2.text
    assert resp2.json()["id"] == body["id"]


def test_register_device_token_requires_auth(client):
    resp = client.post(
        "/api/v1/me/device-token",
        json={"token": "no-auth-token-1234567890"},
    )
    assert resp.status_code == 401
