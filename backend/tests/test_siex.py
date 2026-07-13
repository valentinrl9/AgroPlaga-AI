"""Tests del módulo NEXO SIEX (cuaderno borrador)."""

import pytest

from app.db.session import SessionLocal
from app.models.user import User
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


def _first_zone_id(client, token: str) -> int:
    response = client.get("/api/v1/zones", headers=auth_headers(token))
    assert response.status_code == 200
    return response.json()[0]["id"]


def _create_farm(client, token: str, *, sigpac: str | None = "04079A00100001") -> dict:
    zone_id = _first_zone_id(client, token)
    payload = {
        "name": "Invernadero test",
        "crop": "Tomate",
        "farm_type": "greenhouse",
        "zone_id": zone_id,
        "surface_m2": 5000,
    }
    if sigpac is not None:
        payload["sigpac_code"] = sigpac
    response = client.post("/api/v1/farms", headers=auth_headers(token), json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _create_scan(client, token: str, farm_id: int | None = None) -> int:
    response = client.post(
        "/api/v1/scans",
        headers=auth_headers(token),
        json={
            "crop": "Tomate",
            "plague": "tuta absoluta",
            "severity": "Moderado",
            "confidence": 0.82,
            "farm_id": farm_id,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _create_scan_with_image(client, token: str, farm_id: int | None = None) -> int:
    files = {"image": ("leaf.jpg", _jpeg_bytes(), "image/jpeg")}
    data = {
        "crop": "Tomate",
        "plague": "tuta absoluta",
        "severity": "Moderado",
        "confidence": "0.82",
        "share_with_tech": "true",
    }
    if farm_id is not None:
        data["farm_id"] = str(farm_id)
    response = client.post(
        "/api/v1/scans/with-image",
        headers=auth_headers(token),
        data=data,
        files=files,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _create_treatment(
    client,
    token: str,
    *,
    farm_id: int | None,
    scan_id: int | None = None,
    ack_unverified: bool = True,
) -> dict:
    payload = {
        "farm_id": farm_id,
        "scan_id": scan_id,
        "product_name": "Producto test MAPA",
        "registry_number": "12345",
        "safety_hours": 48,
        "dose_ml": 250.0,
    }
    if scan_id is not None:
        payload["ack_unverified"] = ack_unverified
    response = client.post(
        "/api/v1/treatments",
        headers=auth_headers(token),
        json=payload,
    )
    assert response.status_code == 201, response.text
    return response.json()


def _confirm_scan(client, scan_id: int, admin_headers: dict) -> None:
    response = client.patch(
        f"/api/v1/scans/{scan_id}/validate",
        headers=admin_headers,
        json={"action": "confirm"},
    )
    assert response.status_code == 200, response.text


def _enable_siex_enterprise(email: str) -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        assert user is not None
        user.has_siex_enterprise = True
        db.commit()
    finally:
        db.close()


def test_siex_access_endpoint(client, unique_email):
    token = register_and_login(client, unique_email)
    response = client.get("/api/v1/siex/access", headers=auth_headers(token))
    assert response.status_code == 200
    body = response.json()
    assert body["has_access"] is True
    assert body["preview_open"] is True


def test_treatment_without_sigpac_skips_siex_entry(client, unique_email):
    token = register_and_login(client, unique_email)
    farm = _create_farm(client, token, sigpac=None)
    scan_id = _create_scan(client, token, farm_id=farm["id"])

    result = _create_treatment(client, token, farm_id=farm["id"], scan_id=scan_id)
    assert result["siex_entry_id"] is None
    assert "SIGPAC" in (result["siex_message"] or "")

    entries = client.get("/api/v1/siex/entries", headers=auth_headers(token))
    assert entries.status_code == 200
    assert entries.json() == []


def test_treatment_with_sigpac_compiles_siex_entry(client, unique_email):
    token = register_and_login(client, unique_email)
    farm = _create_farm(client, token)
    scan_id = _create_scan(client, token, farm_id=farm["id"])

    result = _create_treatment(client, token, farm_id=farm["id"], scan_id=scan_id)
    assert result["siex_entry_id"] is not None
    assert "SIEX" in (result["siex_message"] or "")

    entries = client.get("/api/v1/siex/entries", headers=auth_headers(token))
    assert entries.status_code == 200
    data = entries.json()
    assert len(data) == 1
    entry = data[0]
    assert entry["sigpac_code"] == "04079A00100001"
    assert entry["status"] == "registrado"
    assert "tuta absoluta" in entry["justificacion"].lower() or "tuta absoluta" in entry["plague"].lower()
    assert entry["que_se_hizo"]
    assert entry["justificacion"]


def test_enterprise_treatment_pending_tech_validation(client, unique_email):
    token = register_and_login(client, unique_email)
    _enable_siex_enterprise(unique_email)
    admin_headers = _admin_headers(client)
    farm = _create_farm(client, token)
    scan_id = _create_scan_with_image(client, token, farm_id=farm["id"])
    _confirm_scan(client, scan_id, admin_headers)

    result = _create_treatment(client, token, farm_id=farm["id"], scan_id=scan_id, ack_unverified=False)
    entry_id = result["siex_entry_id"]
    assert entry_id is not None

    farmer_entries = client.get("/api/v1/siex/entries", headers=auth_headers(token)).json()
    assert farmer_entries[0]["status"] == "pendiente_validacion"

    admin_headers = _admin_headers(client)
    pending = client.get("/api/v1/siex/entries/pending", headers=admin_headers)
    assert pending.status_code == 200
    ids = [item["id"] for item in pending.json()]
    assert entry_id in ids

    validated = client.patch(
        f"/api/v1/siex/entries/{entry_id}/validate",
        headers=admin_headers,
        json={"action": "approve", "tech_notes": "Conforme MAPA"},
    )
    assert validated.status_code == 200
    assert validated.json()["status"] == "validado"
    assert validated.json()["tech_notes"] == "Conforme MAPA"

    export = client.get("/api/v1/siex/entries/export", headers=auth_headers(token))
    assert export.status_code == 200
    body = export.json()
    assert body["count"] == 1
    assert body["entries"][0]["sigpac"] == "04079A00100001"


def test_invalid_sigpac_rejected_on_farm_create(client, unique_email):
    token = register_and_login(client, unique_email)
    zone_id = _first_zone_id(client, token)
    response = client.post(
        "/api/v1/farms",
        headers=auth_headers(token),
        json={
            "name": "Finca mala",
            "crop": "Tomate",
            "farm_type": "farm",
            "zone_id": zone_id,
            "sigpac_code": "ABC",
        },
    )
    assert response.status_code == 400
