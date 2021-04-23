from .. import utils
from ..registry import register_mapper


@register_mapper("molecule", table="molecule")
def map_molecule(smiles, metadata={}, pubchem_autofill=True):
    data = {"smiles": smiles, "metadata": metadata}
    if pubchem_autofill:
        pubchem_data = utils.pubchem_lookup(smiles)
        if pubchem_data:
            data.extend(pubchem_data)
    return data


@register_mapper(
    "add_molecule",
    table="molecule",
    requirements=[{"type": "table", "name": "molecule_type"}],
)
def map_molecule_with_type(
    smiles, molecule_type_id, metadata={}, pubchem_autofill=True
):
    data = map_molecule(smiles, metadata, pubchem_autofill)
    data["molecule_type_id"] = molecule_type_id
    return data
