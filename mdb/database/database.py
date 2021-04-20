import warnings

from sqlalchemy import create_engine, text
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import scoped_session, sessionmaker

Base = automap_base()


def init_database(uri):
    class Models:
        pass

    engine = create_engine(uri, convert_unicode=True)
    Session = sessionmaker(autocommit=False, autoflush=True, bind=engine)

    # Remove duplicates warning when mapping schema different than public
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        Base.prepare(engine, reflect=True)
        Base.prepare(engine, reflect=True, schema="sourcing")

    models = Models()
    for k in Base.classes.keys():
        setattr(models, k, Base.classes[k])
    return Session, engine, models


def fetch_database_specs(session):
    tables = session.execute(
        text(
            "select table_name from information_schema.tables where table_schema='public';"
        )
    )
    functions = session.execute(
        text(
            (
                "select "
                "   n.nspname || '.' || p.proname as function "
                "from pg_proc p "
                "left join pg_namespace n on p.pronamespace = n.oid "
                "where n.nspname not in ('pg_catalog', 'information_schema');"
            )
        )
    )

    structure = {
        "table": [res[0] for res in tables],
        "function": [res[0] for res in functions],
    }
    return structure
