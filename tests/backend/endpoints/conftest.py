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
        f"/api/v1/login/access-token",
        data={
            "username": os.getenv("MOLAR_SUPERUSER") or "test@molar.tooth",
            "password": os.getenv("MOLAR_PASSWORD") or "tooth",
        },
    )
    token = out.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers
