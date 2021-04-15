# Import all the models, so that Base has them before being
# imported by Alembic
from mdb.backend.db.base_class import Base  # noqa
from mdb.models.item import Item  # noqa
from mdb.backend.models.user import User  # noq