import random


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"



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
