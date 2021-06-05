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

    def test_login_other_database(self, new_database_client, new_database):
        new_database_client.test_token()


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
        response = client.add_user(
            email="anew@email.com", 
            password="blablablabla", 
            full_name="Bucky Tooth",
            is_active=True,
            is_superuser=False,
        )
        assert response["msg"] == "User anew@email.com created"
        pandas = client.get_users()
        assert len(pandas) == 2
    
    def test_get_user_by_email(self, client):
        pandas = client.get_user_by_email("anew@email.com")
        assert pandas["full_name"] == "Bucky Tooth"
        with pytest.raises(MolarBackendError):
            message = client.get_user_by_email("fake@email.com")
    
    def test_register_new_user(self, client):
        answer = client.register_user(
            email="registereduser@email.com",
            password="password",
            full_name="Chip Skylark",
        )
        assert answer["msg"] == "User registereduser@email.com has been register. Ask your database admin to activate this account"
        pandas = client.get_user_by_email("registereduser@email.com")
        assert pandas["is_active"] is False


    def test_activate_user(self, client):
        response = client.activate_user("registereduser@email.com")
        assert response["msg"] == "User registereduser@email.com is now active!"
        pandas = client.get_user_by_email("registereduser@email.com")
        assert pandas["is_active"] is True

    def test_deactivate_user(self, client):
        response = client.deactivate_user("registereduser@email.com")
        assert response["msg"] == "User registereduser@email.com is now deactivated!"
        pandas = client.get_user_by_email("registereduser@email.com")
        assert pandas["is_active"] is False

    def test_delete_user(self, client):
        response = client.delete_user(email="anew@email.com")
        assert response["msg"] == "User anew@email.com has been deleted!"
        with pytest.raises(MolarBackendError):
            pandas = client.get_user_by_email(email="anew@email.com")
        response = client.delete_user(email="registereduser@email.com")
        assert response["msg"] == "User registereduser@email.com has been deleted!"


class TestClientEventstore:
    def test_view_entries(self, client, new_database_client,new_database):
        #verifying that the database is empty and working
        pandas = new_database_client.view_entries("new_database")
        assert len(pandas) == 0
    
    def test_create_entry(self, new_database_client):
        #create first entry
        pandas = new_database_client.create_entry(
            database_name="new_database", 
            type="molecule", 
            data={"smiles": "abc"}
        )
        assert pandas["type"] == "molecule"
        
        #check the number of eventstores and making sure it's the right one
        pandas = new_database_client.view_entries("new_database")
        assert len(pandas) == 1
        assert pandas.iloc[0]["type"] == "molecule"

        #making sure that the entry is in the database as an entry
        pandas = new_database_client.query_database(
            database_name="new_database",
            type="molecule"
        )
        assert pandas.iloc[0]["smiles"] == "abc"
        assert len(pandas) == 1
    
    def test_update_entry(self, new_database_client):
        #get the id of the item in the database 
        item = new_database_client.query_database(
            database_name="new_database",
            type="molecule"
        )

        #update that item
        updated_resp = new_database_client.update_entry(
            database_name="new_database",
            uuid=item.iloc[0]["molecule_id"],
            type="molecule",
            data={"smiles": "hyp"}
        )
        assert updated_resp["type"] == "molecule"

        #checking that the database stored the change and only has one item still
        pandas = new_database_client.query_database(
            database_name="new_database",
            type="molecule"
        )
        assert pandas.iloc[0]["smiles"] == "hyp"
        assert len(pandas) == 1

        #an error should be raised when it isn't a real id
        with pytest.raises(MolarBackendError):
            new_database_client.update_entry(
                database_name="new_database",
                uuid="000000000000",
                type="what",
                data="what"
            )
    
    def test_delete_entry(self, new_database_client):

        #get the id of the item in the database
        pandas = new_database_client.view_entries("new_database")
        item = pandas.iloc[0]

        #delete that item 
        deleted_entry = new_database_client.delete_entry(
            database_name="new_database",
            type=item["type"],
            uuid=item["uuid"]
        )
        assert deleted_entry["type"] == "molecule"

        #check the eventstores to note that there are 3 events that happened and check the latest for delete
        pandas = new_database_client.view_entries("new_database")
        assert pandas.iloc[2]["event"] == "delete"
        assert len(pandas) == 3

        #there should be no more entries in the database that has that id
        with pytest.raises(MolarBackendError):
            new_database_client.delete_entry(
                database_name="new_database",
                uuid=item["uuid"],
                type=item["type"]
            )
    
    

class TestClientQuery:
    @pytest.fixture(autouse=True, scope="class")
    def insert_data(client, new_database_client, new_database):
        new_database_client.create_entry(
            database_name="new_database",
            type="molecule",
            data={
                "smiles": "abc",
                "metadata": {
                    "name": "benzene",
                    "filter": "cycle",
                }
            }
        )
        new_database_client.create_entry(
            database_name="new_database",
            type="molecule",
            data={
                "smiles": "abbae",
                "metadata": {
                    "name": "benzoic acid",
                    "filter": "cycle",
                }
            }
        )
        new_database_client.create_entry(
            database_name="new_database",
            type="conformer",
            data={
                "x": [0],
                "y": [1],
                "z": [2],
                "atomic_numbers"
                "metadata": {
                    "name": "benzene",
                    "filter": "cycle",
                }
            }
        )

