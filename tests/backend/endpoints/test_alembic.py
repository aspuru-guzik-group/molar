class TestAlembic:
    def test_get_alembic_revisions(self, client, new_database_headers):
        out = client.get("/api/v1/alembic/revisions", headers=new_database_headers)
        assert out.status_code == 200

    def test_alembic_downgrade(self, client, new_database_headers):
        out = client.post(
            "/api/v1/alembic/downgrade?database_name=test_database&revision=-1",
            headers=new_database_headers,
        )
        assert out.status_code == 200

    def test_alembic_upgrade(self, client, new_database_headers):
        out = client.post(
            "/api/v1/alembic/upgrade?database_name=test_database&revision=heads",
            headers=new_database_headers,
        )
        assert out.status_code == 200
