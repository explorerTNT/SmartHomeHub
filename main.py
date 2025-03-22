import asyncio
import importlib
import threading
import os
import sys
from core.adapters.event_bus import EventBus
from core.entities.state import State
from core.use_cases.load_plugins import LoadPlugins
from core.adapters.ui_adapter import register_ui
from web.views import app
from core.logger import logger

# Добавляем корень проекта в sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class PluginManager:
    def __init__(self, event_bus, state):
        self.event_bus = event_bus
        self.state = state
        self.plugins = []
        self.ui_blueprints = []

    def load_plugins(self, plugins_directory="modules"):
        logger.info(f"Начинаю загрузку плагинов из {plugins_directory}")
        for root, dirs, files in os.walk(plugins_directory):
            if "__init__.py" in files and "plugin.py" in files:  # Проверяем наличие plugin.py
                module_name = root.replace(os.sep, ".")
                plugin_module_name = f"{module_name}.plugin"
                logger.info(f"Обнаружен модуль: {module_name}, пытаюсь загрузить {plugin_module_name}")
                try:
                    module = importlib.import_module(plugin_module_name)
                    if hasattr(module, 'Plugin'):
                        logger.info(f"Найден класс Plugin в {plugin_module_name}")
                        plugin_class = getattr(module, 'Plugin')
                        plugin = plugin_class()
                        plugin.initialize(self.event_bus, self.state)
                        self.plugins.append(plugin)
                        blueprint = plugin.get_ui_blueprint()
                        if blueprint:
                            self.ui_blueprints.append(blueprint)
                        plugin.register()
                        logger.info(f"Загружен и зарегистрирован плагин: {plugin_module_name}")
                    else:
                        logger.warning(f"В модуле {plugin_module_name} нет класса Plugin")
                except Exception as e:
                    logger.error(f"Ошибка при загрузке плагина {plugin_module_name}: {e}")
        logger.info(f"Загрузка плагинов завершена. Загружено плагинов: {len(self.plugins)}")

def run_flask():
    logger.info("Запуск веб-сервера Flask на порту 5000")
    app.run(host="0.0.0.0", port=5000)

async def main():
    state = State()
    event_bus = EventBus()
    plugin_manager = PluginManager(event_bus, state)
    
    # Загрузка плагинов
    load_plugins_use_case = LoadPlugins(plugin_manager)
    load_plugins_use_case.execute()
    
    # Интеграция с UI
    app.config['state'] = state  # Передача состояния в Flask
    register_ui(app, plugin_manager)
    
    # Запуск главного цикла
    while True:
        await asyncio.sleep(1)  # Пример: держать систему активной

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    asyncio.run(main())