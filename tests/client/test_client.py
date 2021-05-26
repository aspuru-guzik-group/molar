from time import sleep

import pytest
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
        client.database_creation_request("new_database", ["f875464bb81d"])
        df = client.get_database_requests()
        assert len(df) == 1

    def test_approve_request(self, client, new_database_client):
        client.approve_database("new_database")
        sleep(1)
        new_database_client.test_token()

    def test_remove_request(self, client):
        with pytest.raises(MolarBackendError):
            client.remove_database_request("new_database")

        client.database_creation_request("test", ["f875464bb81d"])
        client.remove_database_request("test")

    def test_database_removed(self, client, new_database_client):
        client.remove_database("new_database")
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
    pass


class TestClientEventstore:
    pass


class TestClientQuery:
    pass
