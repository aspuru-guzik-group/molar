import os

from fastapi.testclient import TestClient
from molar.backend.main import app

from .utils import login_and_get_headers, login_request

client = TestClient(app)
superuser_email = os.getenv("MOLAR_SUPERUSER") or "test@molar.tooth"
superuser_password = os.getenv("MOLAR_PASSWORD") or "tooth"


def test_login_access_token():
    # Valid crediential
    out = login_request(client, superuser_email, superuser_password)
    assert out.status_code == 200
    # Invalid credential
    out = login_request(client, "asdf", "asdf")
    assert out.status_code == 400
    # Invalid database
    out = login_request(client, superuser_email, superuser_password, "idonotexist")
    assert out.status_code == 400


def test_token():
    # Legit token
    headers = login_and_get_headers(client, superuser_email, superuser_password)
    out = client.post("/api/v1/login/test-token", headers=headers)
    assert out.status_code == 200

    # Fake token
    headers = {"Authorization": "Bearer asdfasdfasdfasdfd"}
    out = client.post("/api/v1/login/test-token", headers=headers)
    assert out.status_code == 403
