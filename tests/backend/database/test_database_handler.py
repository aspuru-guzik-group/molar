# std
import os

# molar
import molar.backend.database as db

POSTGRES_SERVER = os.getenv("POSTGRES_SERVER") or "localhost"
POSTGRES_USER = os.getenv("POSTGRES_USER") or "postgres"
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD") or "tooth"


def test_database_handler():
    # Existing database
    db_handler = getattr(db, "molar_main", None)
    assert db_handler is not None

    db_handler = getattr(db, "idonotexist", None)
    assert db_handler is None
