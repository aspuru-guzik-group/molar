from mdb import utils


def test_pubchem_lookup():
    assert utils.pubchem_lookup('asdfasdfasdf') == None

    assert utils.pubchem_lookup('CCCC=O') == {'cid': 261,
                                              'inchi': 'InChI=1S/C4H8O/c1-2-3-4-5/h4H,2-3H2,1H3',
                                              'iupac_name': 'butanal',
                                              'cas': '123-72-8'}
