# std
import os

# external
from fastapi.testclient import TestClient

# molar
from molar.backend.main import app


def login(client, username=None, password=None, database="molar_main"):
    if username is None:
        username = os.getenv("MOLAR_SUPERUSER") or "test@molar.tooth"
    if password is None:
        password = os.getenv("MOLAR_PASSWORD") or "tooth"
    out = client.post(
        f"/api/v1/login/access-token?database_name={database}",
        data={
            "username": username,
            "password": password,
        },
    )
    return out


def test_login_access_token(client):
    # Valid crediential
    out = login(client)
    assert out.status_code == 200
    # Invalid credential
    out = login(client, "asdf", "asdf")
    assert out.status_code == 400
    # Invalid database
    out = login(client, database="idonotexist")
    assert out.status_code == 400


def test_token(client, molar_main_headers):
    # Legit token
    out = client.post("/api/v1/login/test-token", headers=molar_main_headers)
    assert out.status_code == 200

    # Fake token
    headers = {"Authorization": "Bearer asdfasdfasdfasdfd"}
    out = client.post("/api/v1/login/test-token", headers=headers)
    assert out.status_code == 403
