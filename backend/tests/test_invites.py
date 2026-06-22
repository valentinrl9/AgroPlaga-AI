"""Tests for pilot invite registration."""

import uuid

from tests.conftest import auth_headers, register_and_login


def _admin_token(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "admin1234"},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_register_requires_invite_when_invite_only(client, unique_email, monkeypatch):
    monkeypatch.setattr("app.api.v1.routes.auth.settings.registration_mode", "invite_only")
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Farmer", "email": unique_email, "password": "secret123"},
    )
    assert response.status_code == 400
    assert "invitación" in response.json()["detail"].lower()


def test_register_with_valid_invite_assigns_role(client, unique_email, monkeypatch):
    monkeypatch.setattr("app.api.v1.routes.auth.settings.registration_mode", "invite_only")
    admin_headers = auth_headers(_admin_token(client))
    create = client.post(
        "/api/v1/admin/invites",
        headers=admin_headers,
        json={"code": "TEST-TECH-01", "role": "tech", "label": "Perito test"},
    )
    assert create.status_code == 201, create.text

    email = unique_email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Perito",
            "email": email,
            "password": "secret123",
            "invite_code": "TEST-TECH-01",
        },
    )
    assert response.status_code == 200, response.text

    profile = client.get("/api/v1/users/me", headers=auth_headers(response.json()["access_token"]))
    assert profile.status_code == 200
    assert profile.json()["role"] == "tech"

    reuse = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Otro",
            "email": f"other_{uuid.uuid4().hex[:8]}@example.com",
            "password": "secret123",
            "invite_code": "TEST-TECH-01",
        },
    )
    assert reuse.status_code == 400


def test_admin_list_users(client):
    admin_headers = auth_headers(_admin_token(client))
    response = client.get("/api/v1/admin/users", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
