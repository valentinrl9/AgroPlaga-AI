"""Incidencias CRM visibles para rol técnico/cooperativa."""

from tests.conftest import auth_headers, register_and_login
from tests.test_incidents import _create_scan, _open_incident, _setup_farmer_with_farm


def _admin_headers(client):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "admin1234"},
    )
    if login.status_code != 200:
        return None
    return auth_headers(login.json()["access_token"])


def test_tech_lists_active_incidents(client, unique_email):
    admin_headers = _admin_headers(client)
    if admin_headers is None:
        return

    _, farmer_headers, farm_id = _setup_farmer_with_farm(client, unique_email)
    scan = _create_scan(client, farmer_headers, farm_id)
    incident = _open_incident(client, farmer_headers, scan["id"])

    response = client.get("/api/v1/tech/incidents", headers=admin_headers)
    assert response.status_code == 200
    rows = response.json()
    match = next((row for row in rows if row["id"] == incident["id"]), None)
    assert match is not None
    assert match["farmer_email"] is not None
    assert match["stage"] == "detection"
    assert match["plague"] == incident["plague"]


def test_farmer_cannot_list_tech_incidents(client, unique_email):
    token = register_and_login(client, unique_email)
    response = client.get("/api/v1/tech/incidents", headers=auth_headers(token))
    assert response.status_code == 403
