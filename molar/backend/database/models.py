class ModelsFromAutomapBase:
    def __init__(self, base):
        self.base = base

    def __getattr__(self, name: str):
        if name in self.base.classes.keys():
            return self.base.classes[name]
        return None
