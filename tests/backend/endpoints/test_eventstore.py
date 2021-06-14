# std
from datetime import datetime


class TestEventStore:
    def test_create_eventstore(self, client, new_database_headers):
        out = client.post(
            "/api/v1/eventstore/test_database",
            headers=new_database_headers,
            json={"type": "molecule", "data": {"smiles": "abc"}},
        )
        assert out.status_code == 200
        out = client.get(
            "/api/v1/eventstore/test_database", headers=new_database_headers
        )
        assert out.status_code == 200
        assert len(out.json()) == 1

        # Database without eventstore
        out = client.get("/api/v1/eventstore/main", headers=new_database_headers)
        assert out.status_code == 403

    def test_update_eventstore(self, client, new_database_headers):
        out = client.get(
            "/api/v1/eventstore/test_database", headers=new_database_headers
        )
        events = out.json()
        out = client.patch(
            "/api/v1/eventstore/test_database",
            headers=new_database_headers,
            json={
                "type": "molecule",
                "data": {"smiles": "def"},
                "uuid": events[0]["uuid"],
            },
        )
        assert out.status_code == 200
        # fake UUID
        out = client.patch(
            "/api/v1/eventstore/test_database",
            headers=new_database_headers,
            json={
                "type": "molecule",
                "data": {"smiles": "abc"},
                "uuid": "91912ca4-cf33-428b-baf0-dfe89ef2dbda",
            },
        )
        assert out.status_code == 404

    def test_delete_eventstore(self, client, new_database_headers):
        out = client.get(
            "/api/v1/eventstore/test_database", headers=new_database_headers
        )
        events = out.json()
        out = client.delete(
            "/api/v1/eventstore/test_database",
            headers=new_database_headers,
            json={"type": "molecule", "uuid": events[0]["uuid"]},
        )
        assert out.status_code == 200

    def test_rollback_eventstore(self, client, new_database_headers):
        out = client.patch(
            "/api/v1/eventstore/rollback/test_database",
            params={"before": str(datetime(1980, 1, 1, 16, 30))},
            headers=new_database_headers,
        )

        assert out.status_code == 200
        out = client.get(
            "/api/v1/eventstore/test_database", headers=new_database_headers
        )
        events = out.json()
        len(events) == 0

    def test_user_id_alembic_notnull(self, client, new_database_headers):
        out = client.get(
            "/api/v1/eventstore/test_database", headers=new_database_headers
        )
        events = out.json()
        assert events[0]["alembic_version"] is not None
        assert events[0]["user_id"] is not None
