import os

import pytest
from fastapi.testclient import TestClient
from molar.backend.main import app
from molar.client_interface import Client_Interface
from molar.client_config import Client_Config


@pytest.fixture(scope="module")
def client_fastapi():
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
def client_interface():
    cfg = Client_Config(
        hostname="localhost", 
        database="postgres", 
        username="test@molar.tooth", 
        password="tooth", 
        fullname="Tooth Fairy",
    )
    return Client_Interface(cfg)    


