import pytest

from tests.conftest import auth_headers, register_and_login


def _jpeg_bytes() -> bytes:
    # JPEG mínimo válido (1x1 px)
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


def test_create_scan_with_image_for_tech(client, unique_email):
    token = register_and_login(client, unique_email)
    headers = auth_headers(token)

    files = {"image": ("leaf.jpg", _jpeg_bytes(), "image/jpeg")}
    data = {
        "crop": "Tomate",
        "plague": "trips",
        "severity": "Moderado",
        "confidence": "0.72",
        "share_with_tech": "true",
    }
    response = client.post(
        "/api/v1/scans/with-image",
        headers=headers,
        data=data,
        files=files,
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["share_with_tech"] is True
    assert body["tech_status"] == "pending"
    assert body["has_image"] is True


def test_pending_scans_visible_to_admin(client, unique_email):
    farmer_token = register_and_login(client, unique_email)
    farmer_headers = auth_headers(farmer_token)
    admin_headers = _admin_headers(client)

    files = {"image": ("leaf.jpg", _jpeg_bytes(), "image/jpeg")}
    data = {
        "crop": "Pimiento",
        "plague": "oidio",
        "severity": "Leve",
        "confidence": "0.55",
        "share_with_tech": "true",
    }
    created = client.post(
        "/api/v1/scans/with-image",
        headers=farmer_headers,
        data=data,
        files=files,
    )
    assert created.status_code == 201
    scan_id = created.json()["id"]

    pending = client.get("/api/v1/tech/pending-scans", headers=admin_headers)
    assert pending.status_code == 200
    ids = [item["id"] for item in pending.json()]
    assert scan_id in ids


def test_validate_scan_confirm(client, unique_email):
    farmer_token = register_and_login(client, unique_email)
    farmer_headers = auth_headers(farmer_token)
    admin_headers = _admin_headers(client)

    files = {"image": ("leaf.jpg", _jpeg_bytes(), "image/jpeg")}
    data = {
        "crop": "Tomate",
        "plague": "mosca blanca",
        "severity": "Alto",
        "confidence": "0.61",
        "share_with_tech": "true",
    }
    created = client.post(
        "/api/v1/scans/with-image",
        headers=farmer_headers,
        data=data,
        files=files,
    )
    scan_id = created.json()["id"]

    validated = client.patch(
        f"/api/v1/scans/{scan_id}/validate",
        headers=admin_headers,
        json={"action": "confirm", "tech_notes": "Encaja con campo"},
    )
    assert validated.status_code == 200
    body = validated.json()
    assert body["tech_status"] == "confirmed"
    assert body["tech_notes"] == "Encaja con campo"

    pending = client.get("/api/v1/tech/pending-scans", headers=admin_headers)
    assert scan_id not in [item["id"] for item in pending.json()]


def test_validate_scan_forbidden_for_farmer(client, unique_email):
    farmer_token = register_and_login(client, unique_email)
    headers = auth_headers(farmer_token)

    files = {"image": ("leaf.jpg", _jpeg_bytes(), "image/jpeg")}
    data = {
        "crop": "Tomate",
        "plague": "trips",
        "severity": "Moderado",
        "confidence": "0.5",
        "share_with_tech": "true",
    }
    created = client.post(
        "/api/v1/scans/with-image",
        headers=headers,
        data=data,
        files=files,
    )
    scan_id = created.json()["id"]

    response = client.patch(
        f"/api/v1/scans/{scan_id}/validate",
        headers=headers,
        json={"action": "confirm"},
    )
    assert response.status_code == 403


def test_pilot_farmers_list(client, unique_email):
    register_and_login(client, unique_email)
    admin_headers = _admin_headers(client)
    response = client.get("/api/v1/tech/farmers", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
