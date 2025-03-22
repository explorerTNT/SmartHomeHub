# core/interfaces/plugin_interface.py
from abc import ABC, abstractmethod

class PluginInterface(ABC):
    @abstractmethod
    def initialize(self, event_bus, state):
        pass

    @abstractmethod
    def register(self):
        pass

    def get_ui_blueprint(self):
        return None