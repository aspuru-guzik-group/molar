from .database import Base
import enum
import sys

__module = sys.modules[__name__]

# User defined types 
class UserRole(enum.Enum):
    ADMIN = 'ADMIN'
    EDITOR = 'EDITOR'
    READER = 'READER'


class CalculationStatus(enum.Enum):
    FAILED = 'FAILED'
    PENDING = 'PENDING'
    SUCCESS = 'SUCCESS'


class CalculationType(enum.Enum):
    ENERGY = 'ENERGY'
    FREQUENCY = 'FREQUENCY'
    STRUCT_OPT = 'STRUCT_OPT'
    

for k in Base.classes.keys():
    setattr(__module, k, Base.classes[k])

