import asyncio
from core.interfaces.plugin_interface import PluginInterface
from core.logger import logger

class Plugin(PluginInterface):
    def __init__(self):
        self.temperature = 22.5
        self.device_name = "Датчик температуры"

    def initialize(self, event_bus, state):
        self.event_bus = event_bus
        self.state = state
        # Добавляем устройство в список devices
        current_devices = self.state.get_data("devices") or []
        if self.device_name not in current_devices:
            current_devices.append(self.device_name)
            self.state.set_data("devices", current_devices)
        # Инициализируем данные в sensor_data
        self.update_sensor_data()
        asyncio.create_task(self.simulate_temperature())

    def register(self):
        self.event_bus.subscribe("request_temperature", self.on_request_temperature)

    async def on_request_temperature(self, data):
        self.temperature += 0.5
        self.update_sensor_data()
        await self.event_bus.publish("temperature_update", {"temperature": self.temperature})
        logger.info(f"Температура обновлена: {self.temperature}")

    async def simulate_temperature(self):
        while True:
            self.temperature += 0.1
            self.update_sensor_data()
            await self.event_bus.publish("temperature_update", {"temperature": self.temperature})
            logger.info(f"Температура симулирована: {self.temperature}")
            await asyncio.sleep(5)

    def update_sensor_data(self):
        # Обновляем данные в sensor_data для конкретного устройства
        sensor_data = self.state.get_data("sensor_data") or {}
        sensor_data[self.device_name] = {"temperature": round(self.temperature, 1)}
        self.state.set_data("sensor_data", sensor_data)