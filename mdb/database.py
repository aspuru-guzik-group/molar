import warnings

from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import scoped_session, sessionmaker

Base = automap_base()


def dump(query):
    return dict([(k, v) for k, v in vars(query).items() if not k.startswith("_")])


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


def fetch_database_capabilities(session):
    import ipdb

    ipdb.set_trace()
