import asyncio
import psutil
from core.interfaces.plugin_interface import PluginInterface
from core.logger import logger

class Plugin(PluginInterface):
    def __init__(self):
        self.pc_name = "Мой ПК"

    def initialize(self, event_bus, state):
        self.event_bus = event_bus
        self.state = state
        # Добавляем устройство в список devices
        current_devices = self.state.get_data("devices") or []
        if self.pc_name not in current_devices:
            current_devices.append(self.pc_name)
            self.state.set_data("devices", current_devices)
        # Инициализируем данные
        self.update_sensor_data()
        asyncio.create_task(self.monitor_pc())

    def register(self):
        self.event_bus.subscribe("request_pc_metrics", self.on_request_metrics)

    async def on_request_metrics(self, data):
        self.update_sensor_data()
        await self.event_bus.publish("pc_metrics_update", self.get_metrics())
        logger.info(f"Метрики ПК обновлены по запросу: {self.get_metrics()}")

    async def monitor_pc(self):
        while True:
            self.update_sensor_data()
            await self.event_bus.publish("pc_metrics_update", self.get_metrics())
            logger.info(f"Метрики ПК обновлены: {self.get_metrics()}")
            await asyncio.sleep(10)

    def update_sensor_data(self):
        # Обновляем данные в sensor_data для конкретного устройства
        sensor_data = self.state.get_data("sensor_data") or {}
        sensor_data[self.pc_name] = self.get_metrics()
        self.state.set_data("sensor_data", sensor_data)

    def get_metrics(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        status = "Онлайн" if psutil.cpu_percent() >= 0 else "Оффлайн"
        return {
            "cpu_usage": round(cpu_usage, 1),
            "memory_usage": round(memory_usage, 1),
            "status": status
        }