"""Tests Entrega 1 — cimientos V2."""

from tests.conftest import auth_headers, register_and_login


def test_zones_include_all_almeria_municipalities(client, unique_email):
    token = register_and_login(client, unique_email)
    response = client.get("/api/v1/zones", headers=auth_headers(token))
    assert response.status_code == 200
    zones = response.json()
    assert len(zones) >= 103
    names = {zone["name"] for zone in zones}
    assert "El Ejido" in names
    assert "Roquetas de Mar" in names


def test_crops_search_filters_aliases(client, unique_email):
    token = register_and_login(client, unique_email)
    headers = auth_headers(token)

    all_crops = client.get("/api/v1/crops", headers=headers)
    assert all_crops.status_code == 200
    assert len(all_crops.json()) >= 10

    pepper = client.get("/api/v1/crops?q=piment", headers=headers)
    assert pepper.status_code == 200
    names = [item["name"] for item in pepper.json()]
    assert "Pimiento" in names


def test_register_requires_map_consent(client, unique_email):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Farmer",
            "email": unique_email,
            "password": "secret123",
            "consent_map_anonymous": False,
        },
    )
    assert response.status_code == 422


def test_farm_supports_nave_sector_and_crop_stage(client, unique_email):
    token = register_and_login(client, unique_email)
    headers = auth_headers(token)

    zones = client.get("/api/v1/zones", headers=headers).json()
    zone_id = zones[0]["id"]

    create = client.post(
        "/api/v1/farms",
        headers=headers,
        json={
            "name": "Invernadero Norte",
            "crop": "Tomate",
            "farm_type": "greenhouse",
            "zone_id": zone_id,
            "nave": "Nave 3",
            "sector": "Sector B",
            "crop_stage": "floración",
            "crop_variant": "pera",
        },
    )
    assert create.status_code == 201, create.text
    body = create.json()
    assert body["nave"] == "Nave 3"
    assert body["sector"] == "Sector B"
    assert body["crop_stage"] == "floración"
    assert body["crop_variant"] == "pera"

    update = client.patch(
        f"/api/v1/farms/{body['id']}",
        headers=headers,
        json={"crop_stage": "cuajado"},
    )
    assert update.status_code == 200
    assert update.json()["crop_stage"] == "cuajado"


def test_scan_accepts_gps_coordinates(client, unique_email):
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
            "latitude": 36.7763,
            "longitude": -2.8144,
        },
    )
    assert create.status_code == 201, create.text
    body = create.json()
    assert body["latitude"] == 36.7763
    assert body["longitude"] == -2.8144


def test_scan_rejects_partial_gps(client, unique_email):
    token = register_and_login(client, unique_email)
    headers = auth_headers(token)

    response = client.post(
        "/api/v1/scans",
        headers=headers,
        json={
            "crop": "Tomate",
            "plague": "trips",
            "severity": "Moderado",
            "confidence": 0.87,
            "latitude": 36.7763,
        },
    )
    assert response.status_code == 422
