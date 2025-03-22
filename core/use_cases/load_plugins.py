# core/use_cases/load_plugins.py
import importlib
import os
from core.logger import logger

class LoadPlugins:
    def __init__(self, plugin_manager):
        self.plugin_manager = plugin_manager

    def execute(self, plugins_directory="modules"):
        self.plugin_manager.load_plugins(plugins_directory)