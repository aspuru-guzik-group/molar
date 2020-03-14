from mdb import MDBClient
import pandas as pd
import pytest
import os
from uuid import UUID


@pytest.fixture
def client():
    db_host = os.getenv("DB_HOST") or "localhost"
    db_user = os.getenv("DB_USER") or "postgres"
    db_pass = os.getenv("DB_PASS") or ""
    db_name = os.getenv("DB_NAME") or "mdb"
    return MDBClient(db_host, db_user, db_pass, db_name)


def test_get(client):
    q = client.get('molecule_type')
    assert isinstance(q, pd.DataFrame)

    q = client.get('molecule_type', return_df=False)
    assert not isinstance(q, pd.DataFrame)


def test_add(client):
    client.add('molecule',
               [{'smiles': 'abcd'}, {'smiles': 'dfge'}])


def test_get_id(client):
    u = client.get_id('molecule', smiles='abcd')
    UUID(u)  # Validate uuid
    with pytest.raises(ValueError):
        client.get_id('molecule', smiles='Idontexistlol')


def test_update(client):
    q = client.get('molecule')
    q.at[0, 'smiles'] = 'jkl;'
    client.update('molecule', q)

    q = client.get('molecule', filters=[client.models.fragment.smiles == 'jkl;'])
    assert len(q) == 1


def test_delete(client):
    q = client.get('molecule')

    client.delete('molecule', q['molecule_id'].tolist())
