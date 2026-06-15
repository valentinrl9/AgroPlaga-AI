from tests.conftest import auth_headers, register_and_login


def test_register_returns_token(client, unique_email):
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Farmer", "email": unique_email, "password": "secret123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]


def test_register_duplicate_email(client, unique_email):
    payload = {"name": "Farmer", "email": unique_email, "password": "secret123"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 200
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400


def test_login_valid_credentials(client, unique_email):
    password = "secret123"
    client.post(
        "/api/v1/auth/register",
        json={"name": "Farmer", "email": unique_email, "password": password},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": unique_email, "password": password},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_invalid_password(client, unique_email):
    client.post(
        "/api/v1/auth/register",
        json={"name": "Farmer", "email": unique_email, "password": "secret123"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": unique_email, "password": "wrong"},
    )
    assert response.status_code == 401


def test_oauth2_token_endpoint(client, unique_email):
    password = "secret123"
    client.post(
        "/api/v1/auth/register",
        json={"name": "Farmer", "email": unique_email, "password": password},
    )
    response = client.post(
        "/api/v1/auth/token",
        data={"username": unique_email, "password": password},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]
