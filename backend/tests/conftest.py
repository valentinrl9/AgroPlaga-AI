import os
import uuid

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://plagaia:plagaia@localhost:5432/plagaia_db",
)
os.environ.setdefault("REGISTRATION_MODE", "open")
os.environ.setdefault("ADMIN_EMAIL", "admin@example.com")
os.environ.setdefault("ADMIN_PASSWORD", "admin1234")


@pytest.fixture(scope="session", autouse=True)
def _prepare_database():
    from unittest.mock import patch

    with (
        patch("app.main.start_scheduler"),
        patch("app.main.stop_scheduler"),
    ):
        from app.db.init_db import init_db

        init_db()


@pytest.fixture
def client():
    from unittest.mock import patch

    with (
        patch("app.main.start_scheduler"),
        patch("app.main.stop_scheduler"),
    ):
        from app.main import app

        with TestClient(app) as test_client:
            yield test_client


@pytest.fixture
def unique_email():
    return f"test_{uuid.uuid4().hex[:12]}@example.com"


def register_and_login(client: TestClient, email: str, password: str = "testpass1") -> str:
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Test Farmer", "email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
