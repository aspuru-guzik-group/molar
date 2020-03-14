from mdb.client import DataAccessObject
from mdb.mapper import  SchemaMapper
from mdb.database import init_db

import os
import pytest

from datetime import datetime


@pytest.fixture
def mapper():
    db_host = os.getenv("DB_HOST") or "localhost"
    db_user = os.getenv("DB_USER") or "postgres"
    db_pass = os.getenv("DB_PASS") or ""
    db_name = os.getenv("DB_NAME") or "mdb"
    Session, _, models = init_db(f'postgresql://{db_user}:{db_pass}@{db_host}/{db_name}')
    dao = DataAccessObject(Session(), models)
    return SchemaMapper(dao)


def test_add_molecule_type(mapper):
    mapper.add_molecule_type('fragment')


def test_add_molecule(mapper):
    mol_type = mapper.dao.get('molecule_type')
    mol1 = mapper.add_molecule('asdf', mol_type[0].molecule_type_id)
    mol2 = mapper.add_molecule('CC(=O)OC1=CC=CC=C1C(=O)O',
                               mol_type[0].molecule_type_id)
    mapper.add_molecule('asdf-aspirin', mol_type[0].molecule_type_id,
                        reactant_id=[mol1.uuid, mol2.uuid])


def test_add_conformer(mapper):
    molecule = mapper.dao.get('molecule')

    x = [1.0, 4.5, 2.1, 3.0]
    n = [1, 4, 2, 6, 4]
    mapper.add_conformer(molecule[0].molecule_id, x, x, x, n,
                         {'property_xasd': 'lol'})


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
    mapper.add_calculation('test_in', 'test_out', 'test -c -x',
            type[0].calculation_type_id, software[0].software_id,
            conf[0].conformer_id, {'is this a test': True})


def test_add_xy_data_calculation(mapper):
    units = mapper.dao.get('data_unit')
    calc = mapper.dao.get('calculation')
    mapper.add_xy_data_calculation(calc[0].calculation_id, 'test', [1, 2, 3, 4], [0, 4, 3, 1],
            units[0].data_unit_id, units[0].data_unit_id)


def test_add_xyz_data_calculation(mapper):
    units = mapper.dao.get('data_unit')
    calc = mapper.dao.get('calculation')
    mapper.add_xyz_data_calculation(calc[0].calculation_id,
                                    'test',
                                    [1, 2, 3, 4],
                                    [0, 4, 3, 1],
                                    [0, 2, 3, 4],
                                    units[0].data_unit_id,
                                    units[0].data_unit_id,
                                    units[0].data_unit_id)

def test_add_lab(mapper):
    mapper.add_lab('Random lab', 'LAB')


def test_add_synthesis_machine(mapper):
    lab = mapper.dao.get('lab')
    mapper.add_synthesis_machine('chemputer',
                                 'Cronin(c)',
                                 'v1.2',
                                 {'version': 1324}, lab[0].lab_id)


def test_add_synthesis(mapper):
    mol = mapper.dao.get('molecule')
    machine = mapper.dao.get('synthesis_machine')
    mapper.add_synthesis(machine[0].synthesis_machine_id, mol[0].molecule_id, '<xdl></xdl>', 'Blablabla')


def test_add_synthesis_molecule(mapper):
    synth = mapper.dao.get('synthesis')
    mol = mapper.dao.get('molecule')
    mapper.add_synthesis_molecule(synth[0].synthesis_id, mol[0].molecule_id, 1.0)


def test_add_experiment_type(mapper):
    mapper.add_experiment_type("stupid_experiment")


def test_add_experiment_machine(mapper):
    type_ = mapper.dao.get('experiment_type')
    lab = mapper.dao.get('lab')
    mapper.add_experiment_machine('hplc',
                                  'brand',
                                  '3000',
                                  {'metadata': 'nop'},
                                  type_[0].experiment_type_id,
                                  lab[0].lab_id)


def test_add_experiment(mapper):
    machine = mapper.dao.get('experiment_machine')
    synth = mapper.dao.get('synthesis')
    mols = mapper.dao.get('molecule')
    event = mapper.add_experiment(synth[0].synthesis_id,
                                  None,
                                  machine[0].experiment_machine_id,
                                  {'concentration': '10M/L'},
                                  'blablabla',
                                  'C:\\somewhere\\ona\\machine')
    mapper.dao.session.commit()

    mapper.add_experiment(None,
                          mols[0].molecule_id,
                          machine[0].experiment_machine_id,
                          {'concentration': '10M/L'},
                          'exp part 2',
                          'C:\\somewhereelse\\ona\\machine',
                          parent_experiment_id=event.uuid)
    mapper.dao.session.commit()
    mapper.dao.rollback(before=datetime(1979, 12, 12, 12, 12, 12))
    mapper.dao.session.commit()
