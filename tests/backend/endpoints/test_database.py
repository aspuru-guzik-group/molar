import os

from fastapi.testclient import TestClient
from molar.backend.main import app

from .utils import login_and_get_headers

client = TestClient(app)
superuser_email = os.getenv("MOLAR_SUPERUSER") or "test@molar.tooth"
superuser_password = os.getenv("MOLAR_PASSWORD") or "tooth"


def test_get_alembic_revisions():
    out = client.get("/api/v1/database/revisions")
    assert out.status_code == 200


def test_database_creation_request():
    out = client.post(
        "/api/v1/database/request",
        json={
            "superuser_email": "test@firstuser.com",
            "superuser_password": "asdf",
            "database_name": "test",
            "alembic_revisions": ["fe0674e45ba8"],
        },
    )
    assert out.status_code == 200


def test_get_database_requests():
    headers = login_and_get_headers(client, superuser_email, superuser_password)
    out = client.get("/api/v1/database/requests", headers=headers)
    assert out.status_code == 200
    assert len(out.json()) == 1


def test_approve_database():
    headers = login_and_get_headers(client, superuser_email, superuser_password)
    out = client.put("/api/v1/database/approve/test", headers=headers)
    assert out.status_code == 200
    out = client.put("/api/v1/database/approve/asdf", headers=headers)
    assert out.status_code == 404


def test_remove_request():
    headers = login_and_get_headers(client, superuser_email, superuser_password)
    out = client.delete("/api/v1/database/request/test", headers=headers)
    assert out.status_code == 403
    out = client.delete("/api/v1/database/request/asdf", headers=headers)
    assert out.status_code == 404

    out = client.post(
        "/api/v1/database/request",
        json={
            "superuser_email": "test@firstuser.com",
            "superuser_password": "asdf",
            "database_name": "test2",
            "alembic_revisions": ["fe0674e45ba8"],
        },
    )
    assert out.status_code == 200
    out = client.delete("/api/v1/database/request/test2", headers=headers)
    assert out.status_code == 200


def test_remove_database():
    headers = login_and_get_headers(client, superuser_email, superuser_password)
    out = client.delete("/api/v1/database/test", headers=headers)
    assert out.status_code == 200
    out = client.delete("/api/v1/database/asdf", headers=headers)
    assert out.status_code == 404
