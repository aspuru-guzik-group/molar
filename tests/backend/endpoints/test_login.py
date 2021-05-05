import os

from fastapi.testclient import TestClient
from molar.backend.main import app

client = TestClient(app)
superuser_email = os.getenv("MOLAR_SUPERUSER") or "test@molar.tooth"
superuser_password = os.getenv("MOLAR_PASSWORD") or "tooth"


def login_request(username, password, database_name="molar_main"):
    out = client.post(
        f"/api/v1/login/access-token?database_name={database_name}",
        data={"username": username, "password": password},
    )
    return out


def login_and_get_headers(username, password, database_name="molar_main"):
    out = login_request(username, password, database_name)
    token = out.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers


def test_login_access_token():
    # Valid crediential
    out = login_request(superuser_email, superuser_password)
    assert out.status_code == 200
    # Invalid credential
    out = login_request("asdf", "asdf")
    assert out.status_code == 400
    # Invalid database
    out = login_request(superuser_email, superuser_password, "idonotexist")
    assert out.status_code == 400


def test_token():
    # Legit token
    headers = login_and_get_headers(superuser_email, superuser_password)
    out = client.post("/api/v1/login/test-token", headers=headers)
    assert out.status_code == 200

    # Fake token
    headers = {"Authorization": "Bearer asdfasdfasdfasdfd"}
    out = client.post("/api/v1/login/test-token", headers=headers)
    assert out.status_code == 403
