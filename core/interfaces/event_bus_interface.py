# core/interfaces/event_bus_interface.py
from abc import ABC, abstractmethod

class EventBusInterface(ABC):
    @abstractmethod
    def subscribe(self, event_type, callback):
        pass

    @abstractmethod
    async def publish(self, event_type, data=None):
        pass