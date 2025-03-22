# core/use_cases/manage_state.py
class ManageState:
    def __init__(self, state):
        self.state = state

    def set_data(self, key, value):
        self.state.set_data(key, value)

    def get_data(self, key):
        return self.state.get_data(key)

    def set_active_module(self, module):
        self.state.set_active_module(module)