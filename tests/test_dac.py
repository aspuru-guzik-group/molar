from mdb.client import DataAccessObject
from mdb.database import init_db

import os
from datetime import datetime

import pytest


@pytest.fixture
def dac():
    db_host = os.getenv("DB_HOST") or "localhost"
    db_user = os.getenv("DB_USER") or "postgres"
    db_pass = os.getenv("DB_PASS") or ""
    db_name = os.getenv("DB_NAME") or "molecdb"
    Session, _ = init_db(f'postgresql://{db_user}:{db_pass}@{db_host}/{db_name}')
    from mdb import models
    return DataAccessObject(Session(), models)


def test_add(dac):
    dac.add('fragment', {'smiles': 'C1ccccc1'})
    dac.session.commit()


def test_get(dac):
    query = dac.get('fragment')
    assert query[0].smiles == 'C1ccccc1'


def test_update(dac):
    query = dac.get('fragment')
    dac.update('fragment', {'smiles': 'CCC=C'}, query[0].uuid)
    dac.session.commit()
    query = dac.get('fragment')
    assert query[0].smiles == 'CCC=C'


def test_delete(dac):
    query = dac.get('fragment')
    dac.delete('fragment', query[0].uuid)
    dac.session.commit()
    query = dac.get('fragment')
    assert len(query) == 0


def test_rollback(dac):
    dac.add('fragment', {'smiles': 'C1cc(=C)ccc1'})
    dac.add('fragment', {'smiles': 'C=CCC'})
    dac.add('fragment', {'smiles': 'CC=CC'})
    dac.add('fragment', {'smiles': 'C#CCCC'})
    dac.session.commit()
    dac.rollback(before=datetime(1979, 12, 12, 12, 12, 12))
    dac.session.commit()
    query = dac.get('fragment')
    assert len(query) == 0
