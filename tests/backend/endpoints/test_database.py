def test_database_creation_request(client):
    out = client.post(
        "/api/v1/database/request",
        json={
            "superuser_fullname": "Charlie Brown",
            "superuser_email": "test@firstuser.com",
            "superuser_password": "asdf",
            "database_name": "test_database_endpoints",
            "alembic_revisions": ["fe0674e45ba8"],
        },
    )
    assert out.status_code == 200


def test_get_database_requests(client, molar_main_headers):
    out = client.get("/api/v1/database/requests", headers=molar_main_headers)
    assert out.status_code == 200
    assert len(out.json()) == 1


def test_approve_database(client, molar_main_headers):
    out = client.put(
        "/api/v1/database/approve/test_database_endpoints", headers=molar_main_headers
    )
    assert out.status_code == 200
    out = client.put("/api/v1/database/approve/asdf", headers=molar_main_headers)
    assert out.status_code == 404


def test_remove_request(client, molar_main_headers):
    out = client.delete(
        "/api/v1/database/request/test_database_endpoints", headers=molar_main_headers
    )
    assert out.status_code == 403
    out = client.delete("/api/v1/database/request/asdf", headers=molar_main_headers)
    assert out.status_code == 404

    out = client.post(
        "/api/v1/database/request",
        json={
            "superuser_fullname": "Test User",
            "superuser_email": "test@firstuser.com",
            "superuser_password": "asdf",
            "database_name": "test2",
            "alembic_revisions": ["fe0674e45ba8"],
        },
    )
    assert out.status_code == 200
    out = client.delete("/api/v1/database/request/test2", headers=molar_main_headers)
    assert out.status_code == 200


def test_remove_database(client, molar_main_headers):
    out = client.delete(
        "/api/v1/database/test_database_endpoints", headers=molar_main_headers
    )
    assert out.status_code == 200
    out = client.delete("/api/v1/database/asdf", headers=molar_main_headers)
    assert out.status_code == 404
