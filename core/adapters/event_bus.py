# core/adapters/event_bus.py
from core.interfaces.event_bus_interface import EventBusInterface
from core.logger import logger

class EventBus(EventBusInterface):
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type, callback):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    async def publish(self, event_type, data=None):
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    await callback(data)
                except Exception as e:
                    logger.error(f"Ошибка при обработке события {event_type}: {e}")