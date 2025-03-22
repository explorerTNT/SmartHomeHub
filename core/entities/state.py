# core/entities/state.py
class State:
    def __init__(self):
        self.data = {}
        self.active_module = None

    def get_data(self, key):
        return self.data.get(key)

    def set_data(self, key, value):
        self.data[key] = value

    def set_active_module(self, module):
        self.active_module = module