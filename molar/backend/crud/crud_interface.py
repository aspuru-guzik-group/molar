from .crud_user import CRUDUser


class CRUDInterface:
    def __init__(self, models):
        user = getattr(models, "user", None)
        if user is not None:
            self.user = CRUDUser(user)
        # eventstore = getattr(models, "eventstore", None)
