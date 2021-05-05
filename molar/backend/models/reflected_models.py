from ..db.base_class import Base


class ReflectedModels:
    def __init__(self, base: Base):
        self.base = Base

    def __getattr__(self, name):
        return self.base.classes[name]
