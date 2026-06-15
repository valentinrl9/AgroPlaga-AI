from tests.conftest import auth_headers, register_and_login


def test_zones_requires_auth(client):
    response = client.get("/api/v1/zones")
    assert response.status_code == 401


def test_zones_returns_sigpac_list(client, unique_email):
    token = register_and_login(client, unique_email)
    response = client.get("/api/v1/zones", headers=auth_headers(token))
    assert response.status_code == 200
    zones = response.json()
    assert len(zones) > 0
    first = zones[0]
    assert "id" in first
    assert "name" in first
    assert "lat" in first
    assert "lon" in first
