import os

import pytest
from fastapi.testclient import TestClient
from molar.backend.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def molar_main_headers(client):
    out = client.post(
        "/api/v1/login/access-token",
        data={
            "username": os.getenv("MOLAR_SUPERUSER") or "test@molar.tooth",
            "password": os.getenv("MOLAR_PASSWORD") or "tooth",
        },
    )
    token = out.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers


@pytest.fixture(scope="class")
def new_database_headers(client, molar_main_headers):
    out = client.post(
        "/api/v1/database/request",
        json={
            "superuser_fullname": "Test User",
            "superuser_email": "test@firstuser.com",
            "superuser_password": "asdf",
            "database_name": "test_database",
            "alembic_revisions": ["compchem@head"],
        },
    )
    assert out.status_code == 200
    out = client.put(
        "/api/v1/database/approve/test_database", headers=molar_main_headers
    )
    assert out.status_code == 200
    out = client.post(
        "/api/v1/login/access-token?database_name=test_database",
        data={"username": "test@firstuser.com", "password": "asdf"},
    )
    token = out.json()["access_token"]
    yield {"Authorization": f"Bearer {token}"}
    out = client.delete("/api/v1/database/test_database", headers=molar_main_headers)
    assert out.status_code == 200
