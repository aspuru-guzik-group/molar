from .crud_eventstore import CRUDEventStore
from .crud_molar_database import CRUDMolarDatabase
from .crud_user import CRUDUser


class CRUDInterface:
    def __init__(self, models):
        user = getattr(models, "user", None)
        if user is not None:
            self.user = CRUDUser(user)

        molar_database = getattr(models, "molar_database", None)
        if molar_database is not None:
            self.molar_database = CRUDMolarDatabase(molar_database)

        self.eventstore = None
        eventstore = getattr(models, "eventstore", None)
        if eventstore is not None:
            self.eventstore = CRUDEventStore(eventstore)
