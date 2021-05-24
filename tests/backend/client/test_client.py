from molar import client
from molar.backend.api.api_v1.endpoints.login import recover_password
import os
from tests.backend.client.conftest import client_fastapi, client_interface, molar_main_headers
import pytest
from fastapi import HTTPException
from molar.backend.main import app

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
    assert len(headers) == 2

"""
DATABASE TESTS
"""
def test_get_database(client_interface):
    requests = client_interface.get_database_requests()
    assert requests.size == 0

def test_create_db_request(client_interface):
    pandas = client_interface.get_database_requests()
    assert pandas.size == 0 #get returns pandas
    message = client_interface.database_creation_request("myDatabase")
    assert message["msg"] == "Database request created" #creates returns dict
    pandas = client_interface.get_database_requests()
    assert pandas.size == 7
    assert "myDatabase" in pandas.values
    index = pandas.index[pandas.database_name == "myDatabase"][0]
    assert pandas.at[0, "is_approved"] == False

def test_approve_database(client_interface):
    message = client_interface.approve_database("myDatabase")
    assert message["msg"] == "Database approved. The database will be available in a few seconds"
    pandas = client_interface.get_database_requests()
    assert pandas.at[0, "is_approved"] == True

def test_valid_remove_db_request(client_interface):
    message = client_interface.database_creation_request("anotherDatabase")
    assert message["msg"] == "Database request created"
    pandas = client_interface.get_database_requests()
    assert "anotherDatabase" in pandas.values
    message = client_interface.remove_database_request("anotherDatabase")
    assert message["msg"] == "Database request removed"
    pandas = client_interface.get_database_requests()
    assert "anotherDatabase" not in pandas.values

def test_invalid_remove_db_request(client_interface):
    client_interface.database_creation_request("badDatabase")
    client_interface.approve_database("badDatabase")
    try:
        client_interface.remove_database_request("badDatabase")
    except HTTPException as e:
        assert e.detail == "This database request has been approved and therefore cannot be removed"
    finally:
        client_interface.remove_database("badDatabase")

def test_remove_database(client_interface):
    pandas = client_interface.get_database_requests()
    assert "myDatabase" in pandas.values
    message = client_interface.remove_database("myDatabase")
    assert message["msg"] == "The database has been scheduled for deletion!"
    pandas = client_interface.get_database_requests()
    assert "myDatabase" not in pandas.values 

"""
QUERY TESTS
"""



