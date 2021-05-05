def login_request(client, username, password, database_name="molar_main"):
    out = client.post(
        f"/api/v1/login/access-token?database_name={database_name}",
        data={"username": username, "password": password},
    )
    return out


def login_and_get_headers(client, username, password, database_name="molar_main"):
    out = login_request(client, username, password, database_name)
    token = out.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers
