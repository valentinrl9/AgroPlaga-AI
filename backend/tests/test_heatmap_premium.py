from tests.conftest import auth_headers, register_and_login


def test_heatmap_freemium_allows_24h(client, unique_email):
    token = register_and_login(client, unique_email)
    response = client.get("/api/v1/heatmap?hours=24", headers=auth_headers(token))
    assert response.status_code == 200
    body = response.json()
    assert body["hours"] == 24
    assert body["historical_enabled"] is False
    assert body["max_hours"] == 24
    assert body["allowed_hours"] == [24]


def test_heatmap_freemium_blocks_7d(client, unique_email):
    token = register_and_login(client, unique_email)
    response = client.get("/api/v1/heatmap?hours=168", headers=auth_headers(token))
    assert response.status_code == 403


def test_heatmap_admin_allows_30d(client):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "admin1234"},
    )
    if login.status_code != 200:
        import pytest

        pytest.skip("Admin seed user not available")
    token = login.json()["access_token"]
    response = client.get("/api/v1/heatmap?hours=720", headers=auth_headers(token))
    assert response.status_code == 200
    body = response.json()
    assert body["hours"] == 720
    assert body["historical_enabled"] is True
    assert 168 in body["allowed_hours"]
    assert 720 in body["allowed_hours"]


def test_outbreak_events_freemium_blocks_7d(client, unique_email):
    token = register_and_login(client, unique_email)
    response = client.get("/api/v1/outbreak-events?hours=168", headers=auth_headers(token))
    assert response.status_code == 403
