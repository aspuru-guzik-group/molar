from mdb.client import DataAccessObject, ArgumentsFetcher
from mdb.database import init_db

from datetime import datetime
import os
import pytest


@pytest.fixture
def dao():
    db_host = os.getenv("DB_HOST") or "localhost"
    db_user = os.getenv("DB_USER") or "postgres"
    db_pass = os.getenv("DB_PASS") or ""
    db_name = os.getenv("DB_NAME") or "molecdb"
    Session, _, models = init_db(f'postgresql://{db_user}:{db_pass}@{db_host}/{db_name}')
    return DataAccessObject(Session(), models)


def test_molecule_to_uuid(dao):
    event = dao.add('fragment', {'smiles': 'CCC=C'})
    dao.session.commit()
    uuid = ArgumentsFetcher.molecule_to_uuid(dao, 'CCC=C', 'fragment')
    assert event.uuid == uuid
    
    dao.delete('fragment', event.uuid)
    dao.session.commit()


def test_lab_short_name_to_uuid(dao):
    event = dao.add('lab', {'name': 'Mad scientists lab', 'short_name': 'MAD'})
    dao.session.commit()

    uuid = ArgumentsFetcher.lab_short_name_to_uuid(dao, 'MAD')
    assert event.uuid == uuid


def test_synth_hid_to_uuid(dao):
    mol = dao.add('molecule', {'smiles': 'CCC=C'})
    dao.session.commit()
    labs = dao.get('lab')
    machine = dao.add('synthesis_machine', {'lab_id': labs[0].uuid, 'name': 'mad machine'})
    dao.session.commit()
    synth = dao.add('synthesis', {'machine_id': machine.uuid, 
                                  'targeted_molecule_id': mol.uuid})
    dao.session.commit()
    now = datetime.now()
    assert synth.data['hid'] == f'MAD_{now.month}-{now.day}-{now.year}_0'

    dao.rollback(before=datetime(1979, 12, 12, 12, 12, 12))
    dao.session.commit()


def test__call__(dao):
    def func(molecule_uuid):
        return molecule_uuid

    mol = dao.add('molecule', {'smiles': 'CCC=C'})
    dao.session.commit()

    arg_fetch = ArgumentsFetcher(func, dao, True, False, False)
    out = arg_fetch('CCC=C')
    assert out == mol.uuid

    dao.delete('molecule', out)
    dao.session.commit()

    def func(lab_uuid):
        return lab_uuid

    lab = dao.add('lab', {'name': 'Mad scientists lab', 'short_name': 'MAD'})
    dao.session.commit()

    arg_fetch = ArgumentsFetcher(func, dao, False, False, True)
    out = arg_fetch('MAD')
    assert out == lab.uuid

    dao.delete('lab', out)
    dao.session.commit()
