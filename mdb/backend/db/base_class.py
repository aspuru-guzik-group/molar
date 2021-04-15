from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.ext.automap import automap_base
import warnings

Base = automap_base()


# @as_declarative()
# class Base:
#     #TODO should id this be type Any?
#     # maybe Column("some_table_id", Integer, primary_key=True)
#     id: Any
#     __name__: str
#     # Generate __tablename__ automatically
#     @declared_attr
#     def __tablename__(cls) -> str:
#         return cls.__name__.lower()