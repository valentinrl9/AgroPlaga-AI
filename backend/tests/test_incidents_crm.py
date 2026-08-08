import uuid

from tests.conftest import auth_headers, register_and_login
from tests.test_incidents import (
    DEFAULT_PLAGUE,
    MAPA_REGISTRY,
    _advance_to_diagnosis,
    _apply_treatment,
    _create_scan,
    _open_incident,
    _prescribe,
    _setup_farmer_with_farm,
    _start_evaluation,
)


def test_prescribe_requires_diagnosis_stage(client, unique_email):
    _, headers, farm_id = _setup_farmer_with_farm(client, unique_email)
    scan = _create_scan(client, headers, farm_id)
    incident_id = _open_incident(client, headers, scan["id"])["id"]

    blocked = client.patch(
        f"/api/v1/incidents/{incident_id}/prescribe",
        headers=headers,
        json={"registry_no": MAPA_REGISTRY, "surface_m2": 5000},
    )
    assert blocked.status_code == 400


def test_crm_flow_resolved_on_improvement(client, unique_email):
    _, headers, farm_id = _setup_farmer_with_farm(client, unique_email)
    scan = _create_scan(client, headers, farm_id, plague=DEFAULT_PLAGUE)
    incident_id = _open_incident(client, headers, scan["id"])["id"]

    _advance_to_diagnosis(client, headers, incident_id)
    prescribed = _prescribe(client, headers, incident_id)
    assert prescribed["prescription_registry_number"] == MAPA_REGISTRY
    assert prescribed["prescription_safety_hours"] == 72

    treated = _apply_treatment(client, headers, incident_id)
    assert treated["treatment"]["product_name"] == prescribed["prescription_product_name"]

    _start_evaluation(client, headers, incident_id)

    follow_up = _create_scan(client, headers, farm_id, plague=DEFAULT_PLAGUE)
    attached = client.patch(
        f"/api/v1/incidents/{incident_id}/evaluation-scan",
        headers=headers,
        json={"evaluation_scan_id": follow_up["id"]},
    )
    assert attached.status_code == 200
    assert attached.json()["evaluation_scan_id"] == follow_up["id"]

    resolved = client.patch(
        f"/api/v1/incidents/{incident_id}/evaluate",
        headers=headers,
        json={"improved": True},
    )
    assert resolved.status_code == 200
    body = resolved.json()
    assert body["stage"] == "closed"
    assert body["closure_outcome"] == "resolved"


def test_get_incident_includes_prescription(client, unique_email):
    _, headers, farm_id = _setup_farmer_with_farm(client, unique_email)
    scan = _create_scan(client, headers, farm_id)
    incident_id = _open_incident(client, headers, scan["id"])["id"]
    _advance_to_diagnosis(client, headers, incident_id)
    _prescribe(client, headers, incident_id)

    detail = client.get(f"/api/v1/incidents/{incident_id}", headers=headers)
    assert detail.status_code == 200
    body = detail.json()
    assert body["prescription_product_name"] is not None
    assert body["prescription_dose_ml"] is not None
