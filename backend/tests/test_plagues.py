from tests.conftest import auth_headers, register_and_login


def test_plagues_catalog(client, unique_email):
    token = register_and_login(client, unique_email)
    response = client.get("/api/v1/plagues", headers=auth_headers(token))
    assert response.status_code == 200
    body = response.json()
    assert body["version"] == "v1.5"
    assert len(body["labels"]) == 15
    assert "tuta absoluta" in body["labels"]
    assert len(body["plagues"]) == 15


def test_plagues_requires_auth(client):
    assert client.get("/api/v1/plagues").status_code == 401
