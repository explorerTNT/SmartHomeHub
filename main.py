import asyncio
import importlib
import threading
import os
import sys
import subprocess
from core.adapters.event_bus import EventBus
from core.entities.state import State
from core.use_cases.load_plugins import LoadPlugins
from core.adapters.ui_adapter import register_ui
from web.views import app
from core.logger import logger

# Добавляем корень проекта в sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Список зависимостей
REQUIRED_PACKAGES = ["flask", "psutil"]

def check_and_install_dependencies():
    """Проверяет наличие зависимостей и предлагает установить их, если отсутствуют."""
    missing_packages = []
    for package in REQUIRED_PACKAGES:
        try:
            importlib.import_module(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.warning(f"Отсутствуют зависимости: {', '.join(missing_packages)}")
        response = input(f"Хотите установить отсутствующие зависимости ({', '.join(missing_packages)})? [y/n]: ")
        if response.lower() == 'y':
            try:
                for package in missing_packages:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                logger.info("Зависимости успешно установлены")
            except subprocess.CalledProcessError as e:
                logger.error(f"Ошибка при установке зависимостей: {e}")
                sys.exit(1)
        else:
            logger.error("Проект не может работать без необходимых зависимостей. Установите их вручную с помощью 'pip install flask psutil'")
            sys.exit(1)

class PluginManager:
    def __init__(self, event_bus, state):
        self.event_bus = event_bus
        self.state = state
        self.plugins = []
        self.ui_blueprints = []

    def load_plugins(self, plugins_directory="modules"):
        logger.info(f"Начинаю загрузку плагинов из {plugins_directory}")
        plugins_directory = os.path.normpath(plugins_directory)
        logger.info(f"Абсолютный путь к {plugins_directory}: {os.path.abspath(plugins_directory)}")
        for root, dirs, files in os.walk(plugins_directory):
            logger.info(f"Проверка директории: {root}")
            logger.info(f"Файлы в директории: {files}")
            if "__init__.py" in files and "plugin.py" in files:
                relative_path = os.path.relpath(root, os.path.dirname(os.path.abspath(__file__)))
                module_name = relative_path.replace(os.sep, ".")
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
                    logger.error(f"Ошибка при загрузке плагина {plugin_module_name}: {str(e)}")
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
    app.config['state'] = state
    register_ui(app, plugin_manager)
    
    # Запуск главного цикла
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    logger.info(f"Запуск проекта с Python {sys.version}")
    # Проверяем и устанавливаем зависимости, если их нет
    check_and_install_dependencies()
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    asyncio.run(main())