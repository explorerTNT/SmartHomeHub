# core/adapters/ui_adapter.py
from flask import Blueprint

def register_ui(app, plugin_manager):
    for blueprint in plugin_manager.ui_blueprints:
        app.register_blueprint(blueprint)