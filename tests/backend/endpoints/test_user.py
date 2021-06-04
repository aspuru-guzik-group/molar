def test_get_users(client, molar_main_headers):
    out = client.get("/api/v1/user/", headers=molar_main_headers)
    assert out.status_code == 200
    assert len(out.json()) == 1


def test_add_user(client, molar_main_headers):
    out = client.post(
        "/api/v1/user/add",
        json={
            "email": "test@newuser.com",
            "full_name": "Margaret Atwood",
            "password": "test",
            "is_active": True,
        },
        headers=molar_main_headers,
    )
    assert out.status_code == 200
    out = client.post(
        "/api/v1/login/access-token",
        data={"username": "test@newuser.com", "password": "test"},
    )
    assert out.status_code == 200

    out = client.delete(
        "/api/v1/user/",
        params={"email": "test@newuser.com"},
        headers=molar_main_headers,
    )
    assert out.status_code == 200


class TestUpdateUser:
    def test_register(self, client, molar_main_headers):
        out = client.post(
            "/api/v1/user/register",
            json={"full_name": "John Doe", "email": "john@doe.com", "password": "lol"},
        )
        assert out.status_code == 200
        out = client.get(
            "/api/v1/user/john@doe.com",
            headers=molar_main_headers,
        )
        assert out.json()["is_active"] is False

    def test_activate_user(self, client, molar_main_headers):
        out = client.patch(
            "/api/v1/user/activate",
            params={"email": "john@doe.com"},
            headers=molar_main_headers,
        )
        assert out.status_code == 200

        out = client.get("/api/v1/user/john@doe.com", headers=molar_main_headers)
        assert out.status_code == 200
        data = out.json()
        assert data["is_active"] is True

    def test_deactivate_user(self, client, molar_main_headers):
        out = client.patch(
            "/api/v1/user/deactivate",
            params={"email": "john@doe.com"},
            headers=molar_main_headers,
        )
        assert out.status_code == 200

    def test_update_user(self, client, molar_main_headers):
        client.patch(
            "/api/v1/user/activate",
            params={"email": "john@doe.com"},
            headers=molar_main_headers,
        )
        out = client.post(
            "/api/v1/login/access-token",
            data={"username": "john@doe.com", "password": "lol"},
        )
        assert out.status_code == 200
        token = out.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        out = client.patch(
            "/api/v1/user/",
            json={"email": "john@doe.com", "password": "test"},
            headers=headers,
        )
        assert out.status_code == 200
        out = client.patch(
            "/api/v1/user/",
            json={"email": "john@doe.com", "is_superuser": True},
            headers=headers,
        )
        assert out.status_code == 401

    def test_delete_user(self, client, molar_main_headers):
        out = client.delete(
            "/api/v1/user/",
            params={"email": "john@doe.com"},
            headers=molar_main_headers,
        )
        assert out.status_code == 200
