from mdb.client import DataAccessObject
from mdb.database import init_db

import os
from datetime import datetime

import pytest


@pytest.fixture
def dao():
    db_host = os.getenv("DB_HOST") or "localhost"
    db_user = os.getenv("DB_USER") or "postgres"
    db_pass = os.getenv("DB_PASS") or ""
    db_name = os.getenv("DB_NAME") or "mdb"
    Session, _, models = init_db(f'postgresql://{db_user}:{db_pass}@{db_host}/{db_name}')
    return DataAccessObject(Session(), models)


def test_add(dao):
    dao.add('fragment', {'smiles': 'C1ccccc1'})
    dao.session.commit()


def test_get(dao):
    query = dao.get('fragment')
    assert query[0].smiles == 'C1ccccc1'


def test_update(dao):
    query = dao.get('fragment')
    dao.update('fragment', {'smiles': 'CCC=C'}, query[0].id)
    dao.session.commit()
    query = dao.get('fragment')
    assert query[0].smiles == 'CCC=C'


def test_delete(dao):
    query = dao.get('fragment')
    dao.delete('fragment', query[0].id)
    dao.session.commit()
    query = dao.get('fragment')
    assert len(query) == 0


def test_rollback(dao):
    dao.add('fragment', {'smiles': 'C1cc(=C)ccc1'})
    dao.add('fragment', {'smiles': 'C=CCC'})
    dao.add('fragment', {'smiles': 'CC=CC'})
    dao.add('fragment', {'smiles': 'C#CCCC'})
    dao.session.commit()
    dao.rollback(before=datetime(1979, 12, 12, 12, 12, 12))
    dao.session.commit()
    query = dao.get('fragment')
    assert len(query) == 0
