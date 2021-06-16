# external
import pytest


@pytest.fixture(autouse=True, scope="class")
def insert_dummy_data(client, new_database_headers):
    out = client.post(
        "/api/v1/eventstore/test_database",
        headers=new_database_headers,
        json={
            "type": "molecule",
            "data": {
                "smiles": "abc",
                "metadata": {"test": "test", "test_filters": "abc"},
            },
        },
    )
    assert out.status_code == 200
    molecule = out.json()
    out = client.post(
        "/api/v1/eventstore/test_database",
        headers=new_database_headers,
        json={
            "type": "conformer",
            "data": {
                "x": [0],
                "y": [1],
                "z": [2],
                "atomic_numbers": [2],
                "molecule_id": molecule["uuid"],
            },
        },
    )
    assert out.status_code == 200
    conformer = out.json()
    out = client.post(
        "/api/v1/eventstore/test_database",
        headers=new_database_headers,
        json={
            "type": "software",
            "data": {
                "name": "cp2k",
                "version": "v1.0",
            },
        },
    )
    assert out.status_code == 200
    software = out.json()
    out = client.post(
        "/api/v1/eventstore/test_database",
        headers=new_database_headers,
        json={
            "type": "calculation",
            "data": {
                "conformer_id": conformer["uuid"],
                "software_id": software["uuid"],
                "output_conformer_id": conformer["uuid"],
            },
        },
    )

    out = client.post(
        "/api/v1/eventstore/test_database",
        headers=new_database_headers,
        json={"type": "molecule_type", "data": {"name": "test_type"}},
    )
    assert out.status_code == 200
    event = out.json()

    out = client.post(
        "/api/v1/eventstore/test_database",
        headers=new_database_headers,
        json={
            "type": "molecule",
            "data": {"smiles": "def", "molecule_type_id": event["uuid"]},
        },
    )
    assert out.status_code == 200


class TestQuery:
    def test_simple_query(self, client, new_database_headers):
        # Database doesn't exist
        out = client.get("/api/v1/query/idontexist", headers=new_database_headers)
        assert out.status_code == 404
        # No types provided
        out = client.get("/api/v1/query/test_database", headers=new_database_headers)
        assert out.status_code == 422

        # Normal query
        out = client.get(
            "/api/v1/query/test_database",
            headers=new_database_headers,
            json={"types": "molecule"},
        )
        assert out.status_code == 200
        data = out.json()
        assert len(data) == 2

        out = client.get(
            "/api/v1/query/test_database",
            headers=new_database_headers,
            json={"types": ["molecule.smiles", "molecule_type.name"]},
        )
        assert out.status_code == 200
        data = out.json()
        assert len(data) == 2
        assert "molecule.smiles" in data[0].keys()
        assert "molecule_type.name" in data[0].keys()

    def test_aliased_query(self, client, new_database_headers):
        out = client.get(
            "/api/v1/query/test_database",
            headers=new_database_headers,
            json={
                "types": "aliased_molecule",
                "aliases": {"alias": "aliased_molecule", "type": "molecule"},
            },
        )
        assert out.status_code == 200

        # Alias of a table
        out = client.get(
            "/api/v1/query/test_database",
            headers=new_database_headers,
            json={
                "alises": {"type": "molecule_type", "alias": "asdf"},
                "types": ["molecule", "asdf"],
                "joins": "asdf",
            },
        )

        # Alias of a column
        out = client.get(
            "/api/v1/query/test_database",
            headers=new_database_headers,
            json={
                "aliases": {"type": "molecule_type", "alias": "asdf"},
                "types": ["molecule", "asdf.name"],
                "joins": "asdf",
            },
        )

        # alias of a json field
        out = client.get(
            "/api/v1/query/test_database",
            headers=new_database_headers,
            json={
                "aliases": {"type": "molecule", "alias": "test"},
                "types": [
                    "test.metadata.test",
                    "molecule_type.name",
                ],
                "joins": {"type": "molecule_type"},
            },
        )

    def test_query_with_json_field(self, client, new_database_headers):
        out = client.get(
            "/api/v1/query/test_database",
            headers=new_database_headers,
            json={"types": "molecule.metadata.test"},
        )
        assert out.status_code == 200
        data = out.json()
        assert len(data) == 2
        assert data[0]["molecule.metadata.test"] == "test"
        assert data[1]["molecule.metadata.test"] is None

        out = client.get(
            "/api/v1/query/test_database",
            headers=new_database_headers,
            json={"types": ["molecule.metadata.test", "molecule.smiles"]},
        )
        assert out.status_code == 200

    def test_filters(self, client, new_database_headers):
        out = client.get(
            "/api/v1/query/test_database",
            headers=new_database_headers,
            json={
                "types": "molecule",
                "filters": {"type": "molecule.smiles", "op": "==", "value": "abc"},
            },
        )
        assert out.status_code == 200
        data = out.json()
        assert len(data) == 1
        assert data[0]["smiles"] == "abc"

        out = client.get(
            "/api/v1/query/test_database",
            headers=new_database_headers,
            json={
                "types": "molecule",
                "filters": {
                    "type": "molecule.smiles",
                    "op": "==",
                    "value": "molecule.metadata.test_filters",
                },
            },
        )
        assert out.status_code == 200
        data = out.json()
        assert len(data) == 1

    def test_joins(self, client, new_database_headers):
        out = client.get(
            "/api/v1/query/test_database",
            headers=new_database_headers,
            json={"types": "molecule", "joins": {"type": "molecule_type"}},
        )
        assert out.status_code == 200
        data = out.json()
        len(data) == 1
        out = client.get(
            "/api/v1/query/test_database",
            headers=new_database_headers,
            json={
                "types": "molecule",
                "joins": {"type": "molecule_type", "join_type": "outer"},
            },
        )
        assert out.status_code == 200
        data = out.json()
        len(data) == 1
        out = client.get(
            "/api/v1/query/test_database",
            headers=new_database_headers,
            json={
                "types": "molecule",
                "joins": {"type": "molecule_type", "join_type": "full"},
            },
        )
        assert out.status_code == 200
        data = out.json()
        len(data) == 1

    def test_ambiguous_joins(self, client, new_database_headers):
        out = client.get(
            "/api/v1/query/test_database",
            headers=new_database_headers,
            json={"types": "calculation", "joins": {"type": "conformer"}},
        )
        assert out.status_code == 400
        out = client.get(
            "/api/v1/query/test_database",
            headers=new_database_headers,
            json={
                "types": "calculation",
                "joins": {
                    "type": "conformer",
                    "on": {
                        "column1": "conformer.conformer_id",
                        "column2": "calculation.conformer_id",
                    },
                },
            },
        )
        assert out.status_code == 200

        out = client.get(
            "/api/v1/query/test_database",
            headers=new_database_headers,
            json={
                "types": ["calculation", "conformer"],
                "joins": [
                    {
                        "type": "conformer",
                        "on": {
                            "column1": "conformer.conformer_id",
                            "column2": "calculation.conformer_id",
                        },
                    },
                    {
                        "type": "conformer",
                        "on": {
                            "column1": "conformer.conformer_id",
                            "column2": "calculation.output_conformer_id",
                        },
                    },
                ],
            },
        )
        assert out.status_code == 400

    def test_ambiguous_joins2(self, client, new_database_headers):
        out = client.get(
            "/api/v1/query/test_database",
            headers=new_database_headers,
            json={
                "aliases": [
                    {"type": "conformer", "alias": "initial_conformer"},
                    {"type": "conformer", "alias": "output_conformer"},
                ],
                "types": [
                    "initial_conformer",
                    "output_conformer",
                    "calculation",
                ],
                "joins": [
                    {
                        "type": "initial_conformer",
                        "on": {
                            "column1": "initial_conformer.conformer_id",
                            "column2": "calculation.conformer_id",
                        },
                    },
                    {
                        "type": "output_conformer",
                        "on": {
                            "column1": "output_conformer.conformer_id",
                            "column2": "calculation.output_conformer_id",
                        },
                    },
                ],
            },
        )
        assert out.status_code == 200

    def test_debug_query(self, client, new_database_headers):
        datum = {"types": ["calculation", "software"], "joins": {"type": "software"}}
        out = client.get(
            "/api/v1/query/debug/test_database",
            headers=new_database_headers,
            json=datum,
        )
        assert out.status_code == 200

        out = client.get(
            "/api/v1/query/debug/test_database",
            headers=new_database_headers,
            json=datum,
            params={"explain_analyze": True},
        )
