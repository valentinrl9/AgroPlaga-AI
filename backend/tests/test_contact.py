def test_submit_contact_inquiry(client):
    payload = {
        "name": "María García",
        "email": "maria.test@example.com",
        "role": "agricultor",
        "organization": "Finca Los Claveles",
        "phone": "+34 600 000 000",
        "interest": "mapa",
    }
    response = client.post("/api/v1/contact", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["ok"] is True


def test_submit_contact_rejects_invalid_role(client):
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "role": "invalid",
        "organization": "Finca Test",
        "phone": "+34 600 111 222",
        "interest": "scan",
    }
    response = client.post("/api/v1/contact", json=payload)
    assert response.status_code == 400
