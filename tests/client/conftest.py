# std
import os
from time import sleep

# external
import pytest

# molar
from molar import Client, ClientConfig


def client_factory(database_name="main"):
    cfg = ClientConfig(
        server_url=os.getenv("SERVER_HOST") or "http://localhost:",
        api_prefix=os.getenv("API_PATH") or "/api/v1",
        database_name=database_name,
        email="test@molar.tooth",
        password="tooth",
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
    out = client.database_creation_request("new_database", ["compchem@head"])
    assert out["msg"] == "Database request created"
    out = client.approve_database("new_database")
    df = client.get_database_requests()
    assert len(df) == 1
    yield df
    client.remove_database("new_database")
    df = client.get_database_requests()
    assert len(df) == 0
