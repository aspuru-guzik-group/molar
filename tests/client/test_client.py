# std
from time import sleep

# external
import pytest

# molar
from molar.exceptions import MolarBackendError


class TestClientLogin:
    def test_headers(self, client):
        headers = client.headers
        assert "User-Agent" in headers.keys()
        assert "Authorization" in headers.keys()

    def test_test_token(self, client):
        client.test_token()


class TestClientDatabase:
    def test_get_database_requests(self, client):
        requests = client.get_database_requests()
        assert len(requests) == 0

    def test_database_creation_request(self, client):
        client.database_creation_request("new_database", ["compchem@head"])
        df = client.get_database_requests()
        assert len(df) == 1

    def test_approve_request(self, client, new_database_client):
        out = client.approve_database("new_database")
        assert "msg" in out.keys()  # Check for message
        new_database_client.test_token()
    
    def test_get_database_information(self, client, new_database_client):
        requests = client.get_database_information()
        assert "table_name" in requests.keys()
        

    def test_remove_request(self, client):
        with pytest.raises(MolarBackendError):
            client.remove_database_request("new_database")

        client.database_creation_request("test", ["compchem@head"])
        client.remove_database_request("test")

    def test_database_removed(self, client, new_database_client):
        client.remove_database("new_database")
        sleep(3)
        with pytest.raises(MolarBackendError):
            new_database_client.test_token()


class TestClientAlembic:
    def test_get_alembic_revisions(self, client):
        client.get_alembic_revisions()

    def test_alembic_downgrade(self, new_database_client, new_database):
        new_database_client.alembic_downgrade("-1")

    def test_alembic_upgrade(self, new_database_client, new_database):
        new_database_client.alembic_upgrade("heads")


class TestClientUser:
    def test_get_users(self, client):
        pandas = client.get_users()
        assert len(pandas) == 1

    def test_add_user(self, client):
        client.add_user(
            email="anew@email.com", 
            password="blablablabla", 
            full_name="Bucky Tooth",
        )
        pandas = client.get_users()
        assert len(pandas) == 2
    
    # def test_get_user_by_email(self, client):
    #     pandas = client.get_user_by_email("anew@email.com")
    #     assert "Tooth inc" in pandas.values
    #     message = client.get_user_by_email("fake@email.com")
    #     assert message["message"] == "User not found"
    
    # def test_register_new_user(self, client):
    #     client.register_user(
    #         email="registereduser@email.com",
    #         password="password",
    #         organization="Not Tooth inc",
    #     )
    #     pandas = client.get_users_by_email("registereduser@email.com")
    #     assert pandas
    #     assert pandas["is_active"] == False


    # def test_activate_user(self, client):
    #     response = client.activate_user("registereduser@email.com")
    #     assert response["msg"] == "User registereduser@email.com is now active!"

    # def test_deactivate_user(self, client):
    #     response = client.deactivate_user("registereduser@email.com")
    #     assert response["msg"] == "User registereduser@email.com is now deactivated!"

    # def test_update_user(self, client):
    #     response = client.update_user(
    #         email="anew@email.com",
    #         password="newpassword",
    #     )
    #     assert response["msg"] == "User anew@email.com has been updated!"

    def test_delete_user(self, client):
        response = client.delete_user(email="anew@email.com")
        assert response is None
        # assert response["msg"] == "User anew@email.com has been deleted!"
        with pytest.raises(MolarBackendError):
            pandas = client.get_user_by_email(email="anew@email.com")
    #     response = client.delete_user(email="registereduser@email.com")
    #     assert response["msg"] == "User registereduser@email.com has been deleted!"


class TestClientEventstore:
    pass


class TestClientQuery:
    pass
