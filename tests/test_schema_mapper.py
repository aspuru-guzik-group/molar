from mdb.client import DataAccessObject, SchemaMapper
from mdb.database import init_db

import os
import pytest

from datetime import datetime


@pytest.fixture
def mapper():
    db_host = os.getenv("DB_HOST") or "localhost"
    db_user = os.getenv("DB_USER") or "postgres"
    db_pass = os.getenv("DB_PASS") or ""
    db_name = os.getenv("DB_NAME") or "molecdb"
    Session, _ = init_db(f'postgresql://{db_user}:{db_pass}@{db_host}/{db_name}')
    from mdb import models
    dao = DataAccessObject(Session(), models)
    return SchemaMapper(dao)


def test_add_fragment(mapper):
    mapper.add_fragment('abcd')


def test_add_molecule(mapper):
    fragment = mapper.dao.get('fragment')
    mapper.add_molecule('abcd', fragment[0].uuid)


def test_add_conformer(mapper):
    molecule = mapper.dao.get('molecule')

    x = [1.0, 4.5, 2.1, 3.0]
    n = [1, 4, 2, 6, 4]
    mapper.add_conformer(molecule[0].uuid, x, x, x, n, {'property_xasd': 'lol'})


def test_add_data_unit(mapper):
    mapper.add_data_unit("dummy")


def test_add_calculation_type(mapper):
    mapper.add_calculation_type('badass_dft')


def test_add_software(mapper):
    mapper.add_software('rdkit', '101010')


def test_add_calculation(mapper):
    conf = mapper.dao.get('conformer')
    type = mapper.dao.get('calculation_type')
    software = mapper.dao.get('software')
    mapper.add_calculation('test_in', 'test_out', 'test -c -x', type[0].uuid, software[0].uuid,
            conf[0].uuid, {'is this a test': True})


def test_add_xy_data_calculation(mapper):
    units = mapper.dao.get('data_unit')
    calc = mapper.dao.get('calculation')
    mapper.add_xy_data_calculation(calc[0].uuid, [1, 2, 3, 4], [0, 4, 3, 1],
            units[0].uuid, units[0].uuid)


def test_add_lab(mapper):
    mapper.add_lab('Random lab', 'LAB')


def test_add_synthesis_machine(mapper):
    lab = mapper.dao.get('lab')
    mapper.add_synthesis_machine('chemputer', {'version': 1324}, lab[0].uuid)


def test_add_synthesis(mapper):
    mol = mapper.dao.get('molecule')
    machine = mapper.dao.get('synthesis_machine')
    mapper.add_synthesis(machine[0].uuid, mol[0].uuid, '<xdl></xdl>', 'Blablabla')


def test_add_synth_molecule(mapper):
    synth = mapper.dao.get('synthesis')
    mol = mapper.dao.get('molecule')
    mapper.add_synth_molecule(synth[0].uuid, mol[0].uuid, 1.0)


def test_add_synth_fragment(mapper):
    synth = mapper.dao.get('synthesis')
    mol = mapper.dao.get('fragment')
    mapper.add_synth_fragment(synth[0].uuid, mol[0].uuid, 1.0)


def test_add_experiment_type(mapper):
    mapper.add_experiment_type("stupid_experiment") 


def test_add_experiment_machine(mapper):
    type_ = mapper.dao.get('experiment_type')
    lab = mapper.dao.get('lab')
    mapper.add_experiment_machine('hplc', {'metadata': 'nop'}, type_[0].uuid, lab[0].uuid)


def test_add_experiment(mapper):
    machine = mapper.dao.get('experiment_machine')
    synth = mapper.dao.get('synthesis')
    unit = mapper.dao.get('data_unit')
    mapper.add_experiment(synth[0].uuid, [1, 2, 3, 4], [1, 2, 3, 4],
            unit[0].uuid, unit[0].uuid, machine[0].uuid, {'concentration': '10M/L'},
            'blablabla') 

    mapper.dao.rollback(before=datetime(1979, 12, 12, 12, 12, 12))
    mapper.dao.session.commit()
