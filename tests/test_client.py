from mdb import MDBClient
import pandas as pd
import pytest
import os
from random import random
from sqlalchemy import exc
from datetime import datetime
from uuid import UUID

@pytest.fixture
def client():
    db_host = os.getenv("DB_HOST") or "localhost"
    db_user = os.getenv("DB_USER") or "postgres"
    db_pass = os.getenv("DB_PASS") or ""
    db_name = os.getenv("DB_NAME") or "mdb"
    return MDBClient(db_host, db_user, db_pass, db_name)


def test_get(client):
    q = client.get('fragment')
    assert isinstance(q, pd.DataFrame)

    q = client.get('fragment', return_df=False)
    assert not isinstance(q, pd.DataFrame)

def test_add(client):
    client.add('fragment', 
            [{'smiles': 'abcd'}, {'smiles': 'dfge'}])

def test_get_uuid(client):
    u = client.get_uuid('fragment', smiles='abcd')
    UUID(u) # Validate uuid
    with pytest.raises(ValueError):
        client.get_uuid('molecule', smiles='Idontexistlol')

def test_update(client):
    q = client.get('fragment')
    q.at[0, 'smiles'] = 'jkl;'
    client.update('fragment', q)

    q = client.get('fragment')
    assert q.at[0, 'smiles'] == 'jkl;'

def test_delete(client):
    q = client.get('fragment')

    client.delete('fragment', q['uuid'].tolist())
