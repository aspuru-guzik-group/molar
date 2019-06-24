from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.automap import automap_base


Base = automap_base()


def dump(query):
    return dict([(k, v) for k, v in vars(query).items() if not k.startswith('_')])


def init_db(uri):
    engine = create_engine(uri, convert_unicode=True)
    Session = sessionmaker(autocommit=False, autoflush=True, bind=engine)
    Base.prepare(engine,
                 reflect=True)
    Base.prepare(engine,
                 reflect=True,
                 schema='sourcing')
    return Session, engine
