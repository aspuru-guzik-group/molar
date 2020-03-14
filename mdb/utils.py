import pubchempy as pcp
import re


def pubchem_lookup(smiles):
    try:
        out = pcp.get_compounds(smiles, namespace='smiles', searchtype='identity')
    except pcp.ServerError:
        return None
    if len(out) < 1:
        return None
    return {'pubchem_cid': out[0].cid, 'inchi': out[0].inchi, 'iupac_name': out[0].iupac_name,
            'cas': re.search(r'\d{2,7}-\d{2}-\d', ','.join(out[0].synonyms)).group()}
