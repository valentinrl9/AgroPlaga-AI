"""Tests de validación perito en registro de tratamientos."""

from app.db.session import SessionLocal
from app.models.user import User
from tests.conftest import auth_headers, register_and_login
from tests.test_siex import (
    _admin_headers,
    _create_farm,
    _create_scan,
    _create_scan_with_image,
    _create_treatment,
)


def _enable_siex_enterprise(email: str) -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        assert user is not None
        user.has_siex_enterprise = True
        db.commit()
    finally:
        db.close()


def test_treatment_blocked_on_rejected_scan(client, unique_email):
    token = register_and_login(client, unique_email)
    headers = auth_headers(token)
    admin_headers = _admin_headers(client)
    farm = _create_farm(client, token)
    scan_id = _create_scan_with_image(client, token, farm_id=farm["id"])

    rejected = client.patch(
        f"/api/v1/scans/{scan_id}/validate",
        headers=admin_headers,
        json={"action": "reject", "tech_notes": "Imagen no válida"},
    )
    assert rejected.status_code == 200

    response = client.post(
        "/api/v1/treatments",
        headers=headers,
        json={
            "farm_id": farm["id"],
            "scan_id": scan_id,
            "product_name": "Producto test",
            "registry_number": "12345",
            "safety_hours": 48,
            "ack_unverified": True,
        },
    )
    assert response.status_code == 400
    assert "rechazado" in response.json()["detail"].lower()


def test_unverified_treatment_requires_ack(client, unique_email):
    token = register_and_login(client, unique_email)
    headers = auth_headers(token)
    farm = _create_farm(client, token)
    scan_id = _create_scan(client, token, farm_id=farm["id"])

    blocked = client.post(
        "/api/v1/treatments",
        headers=headers,
        json={
            "farm_id": farm["id"],
            "scan_id": scan_id,
            "product_name": "Producto test",
            "registry_number": "12345",
            "safety_hours": 48,
        },
    )
    assert blocked.status_code == 400
    assert "ack_unverified" in blocked.json()["detail"]

    ok = client.post(
        "/api/v1/treatments",
        headers=headers,
        json={
            "farm_id": farm["id"],
            "scan_id": scan_id,
            "product_name": "Producto test",
            "registry_number": "12345",
            "safety_hours": 48,
            "ack_unverified": True,
        },
    )
    assert ok.status_code == 201
    assert ok.json()["scan_verification"] == "unverified"


def test_verified_scan_allows_treatment_without_ack(client, unique_email):
    token = register_and_login(client, unique_email)
    admin_headers = _admin_headers(client)
    farm = _create_farm(client, token)
    scan_id = _create_scan_with_image(client, token, farm_id=farm["id"])

    validated = client.patch(
        f"/api/v1/scans/{scan_id}/validate",
        headers=admin_headers,
        json={"action": "confirm"},
    )
    assert validated.status_code == 200

    response = _create_treatment(
        client,
        token,
        farm_id=farm["id"],
        scan_id=scan_id,
        ack_unverified=False,
    )
    assert response["scan_verification"] == "verified"


def test_enterprise_skips_siex_on_unverified_scan(client, unique_email):
    token = register_and_login(client, unique_email)
    _enable_siex_enterprise(unique_email)
    headers = auth_headers(token)
    farm = _create_farm(client, token)
    scan_id = _create_scan(client, token, farm_id=farm["id"])

    response = client.post(
        "/api/v1/treatments",
        headers=headers,
        json={
            "farm_id": farm["id"],
            "scan_id": scan_id,
            "product_name": "Producto test",
            "registry_number": "12345",
            "safety_hours": 48,
            "ack_unverified": True,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["siex_entry_id"] is None
    assert "cooperativa" in (body["siex_message"] or "").lower()
