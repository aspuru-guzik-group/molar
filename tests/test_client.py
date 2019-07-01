from goldmine import GoldmineClient
import pandas as pd
import pytest
import os
from sqlalchemy import exc
from datetime import datetime


@pytest.fixture
def client():
    db_host = os.getenv("DB_HOST") or "localhost"
    db_user = os.getenv("DB_USER") or "postgres"
    db_pass = os.getenv("DB_PASS") or ""
    db_name = os.getenv("DB_NAME") or "molecdb"
    return GoldmineClient(db_host, db_user, db_pass, db_name)


def test_rollback(client):
    before = datetime(1979, 12, 12, 12, 12, 12)
    client.rollback(before)


def test_get(client):
    df = client.get('molecule', dataframe=True)
    models = client.get_models()
    df = client.get('molecule', dataframe=True, filters=[models.molecule.smiles == 'CCCC'])

    df = client.get(['molecule', 'molecule_fragment', 'fragment'])


def test_add(client):
    data = pd.DataFrame([{'smiles': 'C#N'},
                       {'smiles': 'CCC'}])
    client.add('molecule', data)
    df = client.get('molecule')
    assert len(df) == 2

    data = [{'smiles': 'CCCC'},
            {'smiles': 'CCCCC'}]
    client.add('molecule', data)
    df = client.get('molecule')
    assert len(df) == 4

    data = {'smiles': 'C1cccccc1'}
    client.add('molecule', data)
    df = client.get('molecule')
    assert len(df) == 5

    with pytest.raises(exc.IntegrityError):
        client.add('molecule', {'smiles': 'CCC'})
    client.session.rollback()

    with pytest.raises(TypeError):
        client.add('table', 23)


def test_update(client):
    df = client.get('molecule')
    df.at[0, 'properties'] = {'test': 'is it working?'}
    client.update('molecule', df)
    df = client.get('molecule')
    assert df['properties'][0]['test'] == 'is it working?'

    data = df.iloc[0].to_dict()
    data['properties'] = {'test': 'something else'}
    uuid = data['uuid']
    del data['uuid']
    del data['id']
    client.update('molecule', data, uuid)
    df = client.get('molecule')
    df.sort_values('id', inplace=True)
    assert df.iloc[0]['properties']['test'] == 'something else'

    uuid_list = df['uuid'].tolist()
    del df['uuid']
    del df['id']
    df.at[0, 'smiles'] = "CECI N'EST PAS UN SMILES"
    records = df.to_dict(orient='records')
    
    client.update('molecule', records, uuid_list)
    
    with pytest.raises(TypeError):
        client.update('molecule', 123)


def test_delete(client):
    df = client.get('molecule')
    client.delete('molecule', df['uuid'].tolist())


def test_fragment(client):
    fragments = client.get('fragment')
    if not fragments.empty:
        client.delete('fragment', uuid=fragments['uuid'].tolist())
    client.add_fragment('C1cccccc1')
    client.del_fragment('C1cccccc1')

    client.add_fragment(['A', 'B'])
    client.add_fragment(['A', 'B', 'C'])
    client.del_fragment(['A', 'B'])

    df = client.get('fragment')
    client.delete('fragment', uuid=df['uuid'].tolist())


def test_molecule(client):
    client.add_molecule(['A', 'B'], 'C')
    assert len(client.get('molecule')) == 1
    assert len(client.get('fragment')) == 2
    
    client.del_molecule('C')
    assert len(client.get('molecule')) == 0
    assert len(client.get('molecule_fragment')) == 0
    assert len(client.get('fragment')) == 2

    client.del_fragment('A')
    client.del_fragment('B')

    client.add_molecule([['A', 'B'], ['C', 'D']], ['Z', 'Y'])


def test_software(client):
    client.add_software("A", "B")

    with pytest.raises(exc.IntegrityError):
        client.add_software("A", "B")
    
    client.session.rollback()
    df = client.get('software')
    client.delete('software', df['uuid'].tolist())


def test_conformation(client):
    df = client.get('molecule')
    molecule_uuid = df.iloc[0]['uuid']
    atoms = [
        {'x': 1, 'y': 1, 'z': 1, 'n': 1},
        {'x': 2, 'y': 2, 'z': 1, 'n': 6},
        {'x': 3, 'y': 1, 'z': 3, 'n': 5},
        {'x': 4, 'y': 2, 'z': 1, 'n': 4},
        {'x': 5, 'y': 1, 'z': 3, 'n': 3}
    ]
    client.add_conformation(molecule_uuid, atoms, {'prop': 'value'})

def test_calculation(client):
    client.add_software('test', 'test')
    soft_uuid = client.get('software').iloc[0]['uuid']
    conf_uuid = client.get('conformation').iloc[0]['uuid']
    client.add_calculation('PENDING', 
                           'ENERGY', 
                           soft_uuid, 
                           conf_uuid, 
                           {'prop': 1})
