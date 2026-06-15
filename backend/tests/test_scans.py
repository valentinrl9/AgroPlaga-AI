from tests.conftest import auth_headers, register_and_login


def test_get_scans_requires_auth(client):
    response = client.get("/api/v1/scans")
    assert response.status_code == 401


def test_create_and_list_scan(client, unique_email):
    token = register_and_login(client, unique_email)
    headers = auth_headers(token)

    create = client.post(
        "/api/v1/scans",
        headers=headers,
        json={
            "crop": "Tomate",
            "plague": "trips",
            "severity": "Moderado",
            "confidence": 0.87,
        },
    )
    assert create.status_code == 201
    body = create.json()
    assert body["crop"] == "Tomate"
    assert body["plague"] == "trips"

    listing = client.get("/api/v1/scans", headers=headers)
    assert listing.status_code == 200
    scans = listing.json()
    assert len(scans) >= 1
    assert scans[0]["id"] == body["id"]


def test_create_scan_rejects_foreign_farm(client, unique_email):
    token = register_and_login(client, unique_email)
    headers = auth_headers(token)

    response = client.post(
        "/api/v1/scans",
        headers=headers,
        json={
            "crop": "Tomate",
            "plague": "trips",
            "severity": "Leve",
            "confidence": 0.5,
            "farm_id": 999999,
        },
    )
    assert response.status_code == 400
