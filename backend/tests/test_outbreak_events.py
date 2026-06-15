import uuid

import pytest

from tests.conftest import auth_headers, register_and_login


def _first_zone_id(client, token: str) -> int:
    response = client.get("/api/v1/zones", headers=auth_headers(token))
    assert response.status_code == 200
    return response.json()[0]["id"]


def test_outbreak_events_requires_auth(client):
    response = client.get("/api/v1/outbreak-events")
    assert response.status_code == 401


def test_contribute_outbreak_event(client, unique_email):
    token = register_and_login(client, unique_email)
    headers = auth_headers(token)
    zone_id = _first_zone_id(client, token)

    response = client.post(
        "/api/v1/outbreak-events",
        headers=headers,
        json={
            "plague": "trips",
            "severity": 2,
            "zone_id": zone_id,
            "model_version": "v1.0",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["plague"] == "trips"
    assert body["zone_id"] == zone_id
    assert body["validated"] is False


def test_contribute_invalid_zone(client, unique_email):
    token = register_and_login(client, unique_email)
    response = client.post(
        "/api/v1/outbreak-events",
        headers=auth_headers(token),
        json={"plague": "trips", "severity": 2, "zone_id": 999999},
    )
    assert response.status_code == 404


def test_validate_event_forbidden_for_farmer(client, unique_email):
    token = register_and_login(client, unique_email)
    headers = auth_headers(token)
    zone_id = _first_zone_id(client, token)

    created = client.post(
        "/api/v1/outbreak-events",
        headers=headers,
        json={"plague": "oidio", "severity": 1, "zone_id": zone_id},
    )
    event_id = created.json()["id"]

    response = client.patch(
        f"/api/v1/outbreak-events/{event_id}/validate",
        headers=headers,
        json={"validated": True},
    )
    assert response.status_code == 403


def test_validate_event_as_admin(client):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "admin1234"},
    )
    if login.status_code != 200:
        pytest.skip("Admin seed user not available")
    admin_token = login.json()["access_token"]
    admin_headers = auth_headers(admin_token)
    zone_id = _first_zone_id(client, admin_token)

    farmer_email = f"farmer_{uuid.uuid4().hex[:8]}@example.com"
    farmer_token = register_and_login(client, farmer_email)
    created = client.post(
        "/api/v1/outbreak-events",
        headers=auth_headers(farmer_token),
        json={"plague": "mosca_blanca", "severity": 3, "zone_id": zone_id},
    )
    event_id = created.json()["id"]

    response = client.patch(
        f"/api/v1/outbreak-events/{event_id}/validate",
        headers=admin_headers,
        json={"validated": True},
    )
    assert response.status_code == 200
    assert response.json()["validated"] is True
