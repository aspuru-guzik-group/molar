from ..registry import register_alembic_branch

register_alembic_branch(
    branch_label="molecule-table",
    options=[
        {
            "branch_label": "molecule-type",
            "help": "Adding the possibility to have types of molecules",
            "default": False,
        }
    ],
    help="Table for SMILES and extra data at the molecular level.",
    default=True,
)


register_alembic_branch(
    branch_label="molar-main",
    options=[],
    help="Structure of the main molar database",
    default=False,
)
