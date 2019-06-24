from goldmine import GoldmineClient
import pandas as pd
import pytest
from datetime import datetime


@pytest.fixture
def client():
    return GoldmineClient('localhost', 'postgres', '', 'molecdb')


def test_rollback(client):
    before = datetime(1979, 12, 12, 12, 12, 12)


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


def test_update(client):
    df = client.get('molecule')
    df.at[0, 'properties'] = {'test': 'is it working?'}
    client.update('molecule', df)
    df = client.get('molecule')
    assert df['properties'][0]['test'] == 'is it working?'


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
    client.del_fragment(['A', 'B'])


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

