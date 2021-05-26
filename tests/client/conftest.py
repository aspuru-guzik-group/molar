import os
from time import sleep

import pytest
from molar import Client, ClientConfig


def client_factory(database_name="molar_main"):
    cfg = ClientConfig(
        server_url=os.getenv("SERVER_HOST") or "http://localhost",
        api_prefix=os.getenv("API_PATH") or "/api/v1",
        database_name=database_name,
        username="test@molar.tooth",
        password="tooth",
        fullname="Tooth Fairy",
    )
    return Client(cfg)


@pytest.fixture(scope="module")
def client():
    return client_factory()


@pytest.fixture(scope="class")
def new_database_client():
    return client_factory("new_database")


@pytest.fixture(scope="class")
def new_database(client):
    out = client.database_creation_request("new_database", ["f875464bb81d"])
    assert out["msg"] == "Database request created"
    out = client.approve_database("new_database")
    assert (
        out["msg"]
        == "Database approved. The database will be available in a few seconds"
    )
    df = client.get_database_requests()
    assert len(df) == 1
    sleep(1)
    yield df
    client.remove_database("new_database")
    df = client.get_database_requests()
    assert len(df) == 0
