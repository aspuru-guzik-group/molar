from molar import client
from molar.backend.api.api_v1.endpoints.login import recover_password
import os
from tests.backend.client.conftest import client_fastapi, client_interface, molar_main_headers
import pytest
from fastapi.testclient import TestClient
from molar.backend.main import app
from molar.interface_client import Interface_Client

def test_api(client_fastapi, client_interface):
    out = client_fastapi.get(
        "/api/v1/utils/test/api/"
    )
    answer = out.json()["msg"]
    myclient = client_interface.test()["msg"]
    assert answer == myclient

def test_dummy(client_interface):
    assert True

def test_client_login(client_interface):
    headers = client_interface.headers
    # myclient = Interface_Client("test@molar.tooth", "tooth")
    #TODO no way to check for the token without changing visibility
    assert len(headers.json()) == 2

"""
DATABASE TESTS
"""
def test_get_database(client_interface):
    requests = client_interface.get_database_requests()
    assert requests.status_code == 200

def test_create_db_request(client_interface):
    requests = client_interface.get_database_requests()
    assert requests is []
    message = client_interface.database_creation_request("myDatabase")
    assert message == "Database request created"
    requests = client_interface.get_database_requests()
    mydatabase = {
        "database_name": "myDatabase",
            "superuser_fullname": "",
            "superuser_email": "test@molar.tooth",
            "superuser_password": "tooth",
            "alembic_revisions": []
    }
    assert mydatabase in requests
    


