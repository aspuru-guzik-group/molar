from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from mdb.backend.db.base_class import Base
import warnings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    Base.prepare(engine,
                 reflect=True)
    Base.prepare(engine,
                 reflect=True,
                 schema='sourcing')
