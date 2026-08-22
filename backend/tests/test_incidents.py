import uuid

from tests.conftest import auth_headers, register_and_login

MAPA_REGISTRY = "ES-00001"
DEFAULT_PLAGUE = "tuta absoluta"


def _setup_farmer_with_farm(client, email: str | None = None) -> tuple[str, dict, int]:
    email = email or f"inc_{uuid.uuid4().hex[:10]}@example.com"
    token = register_and_login(client, email)
    headers = auth_headers(token)

    zones = client.get("/api/v1/zones", headers=headers)
    assert zones.status_code == 200
    zone_id = zones.json()[0]["id"]

    farm = client.post(
        "/api/v1/farms",
        headers=headers,
        json={
            "name": "Invernadero Inc",
            "crop": "Tomate",
            "farm_type": "greenhouse",
            "zone_id": zone_id,
            "crop_stage": "floración",
        },
    )
    assert farm.status_code == 201, farm.text
    return token, headers, farm.json()["id"]


def _create_scan(client, headers: dict, farm_id: int, plague: str = DEFAULT_PLAGUE) -> dict:
    response = client.post(
        "/api/v1/scans",
        headers=headers,
        json={
            "crop": "Tomate",
            "plague": plague,
            "severity": "Moderado",
            "confidence": 0.85,
            "farm_id": farm_id,
            "latitude": 36.7763,
            "longitude": -2.8144,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _open_incident(client, headers: dict, scan_id: int) -> dict:
    opened = client.post("/api/v1/incidents", headers=headers, json={"scan_id": scan_id})
    assert opened.status_code == 201, opened.text
    return opened.json()


def _advance_to_diagnosis(client, headers: dict, incident_id: int) -> None:
    adv = client.patch(f"/api/v1/incidents/{incident_id}/advance", headers=headers, json={})
    assert adv.status_code == 200, adv.text
    assert adv.json()["stage"] == "diagnosis"


def _prescribe(client, headers: dict, incident_id: int, surface_m2: float = 5000.0) -> dict:
    resp = client.patch(
        f"/api/v1/incidents/{incident_id}/prescribe",
        headers=headers,
        json={"registry_no": MAPA_REGISTRY, "surface_m2": surface_m2},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["stage"] == "prescription"
    assert body["prescription_product_name"] is not None
    assert body["prescription_dose_ml"] is not None
    return body


def _apply_treatment(client, headers: dict, incident_id: int) -> dict:
    resp = client.patch(
        f"/api/v1/incidents/{incident_id}/apply-treatment",
        headers=headers,
        json={"ack_unverified": True},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["stage"] == "treatment"
    assert body["treatment"] is not None
    return body


def _start_evaluation(client, headers: dict, incident_id: int) -> dict:
    resp = client.patch(f"/api/v1/incidents/{incident_id}/start-evaluation", headers=headers, json={})
    assert resp.status_code == 200, resp.text
    assert resp.json()["stage"] == "evaluation"
    return resp.json()


def test_incidents_requires_auth(client):
    response = client.get("/api/v1/incidents")
    assert response.status_code == 401


def test_open_incident_from_scan(client, unique_email):
    _, headers, farm_id = _setup_farmer_with_farm(client, unique_email)
    scan = _create_scan(client, headers, farm_id)

    body = _open_incident(client, headers, scan["id"])
    assert body["scan_id"] == scan["id"]
    assert body["stage"] == "detection"
    assert body["zone_name"] is not None
    assert body["outbreak_event_id"] is not None

    listing = client.get("/api/v1/incidents", headers=headers)
    assert listing.status_code == 200
    assert len(listing.json()) == 1


def test_open_incident_backfills_legacy_map_consent(client, unique_email):
    from app.db.session import SessionLocal
    from app.models.user import User

    _, headers, farm_id = _setup_farmer_with_farm(client, unique_email)
    scan = _create_scan(client, headers, farm_id)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == unique_email).first()
        assert user is not None
        user.consent_accepted_at = None
        db.commit()
    finally:
        db.close()

    body = _open_incident(client, headers, scan["id"])
    assert body["scan_id"] == scan["id"]

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == unique_email).first()
        assert user is not None
        assert user.consent_accepted_at is not None
    finally:
        db.close()


def test_open_incident_rejects_sana(client, unique_email):
    _, headers, farm_id = _setup_farmer_with_farm(client, unique_email)
    scan = _create_scan(client, headers, farm_id, plague="sana")

    response = client.post(
        "/api/v1/incidents",
        headers=headers,
        json={"scan_id": scan["id"]},
    )
    assert response.status_code == 400


def test_close_incident(client, unique_email):
    _, headers, farm_id = _setup_farmer_with_farm(client, unique_email)
    scan = _create_scan(client, headers, farm_id)
    incident_id = _open_incident(client, headers, scan["id"])["id"]

    _advance_to_diagnosis(client, headers, incident_id)
    _prescribe(client, headers, incident_id)
    _apply_treatment(client, headers, incident_id)

    closed = client.patch(
        f"/api/v1/incidents/{incident_id}/close",
        headers=headers,
        json={"outcome": "resolved"},
    )
    assert closed.status_code == 200
    assert closed.json()["stage"] == "closed"
    assert closed.json()["closure_outcome"] == "resolved"

    active = client.get("/api/v1/incidents?active_only=true", headers=headers)
    assert active.status_code == 200
    assert active.json() == []


def test_evaluate_no_improvement_returns_to_treatment(client, unique_email):
    _, headers, farm_id = _setup_farmer_with_farm(client, unique_email)
    scan = _create_scan(client, headers, farm_id)
    incident_id = _open_incident(client, headers, scan["id"])["id"]

    _advance_to_diagnosis(client, headers, incident_id)
    _prescribe(client, headers, incident_id)
    _apply_treatment(client, headers, incident_id)
    _start_evaluation(client, headers, incident_id)

    evaluated = client.patch(
        f"/api/v1/incidents/{incident_id}/evaluate",
        headers=headers,
        json={"improved": False},
    )
    assert evaluated.status_code == 200
    assert evaluated.json()["stage"] == "treatment"
