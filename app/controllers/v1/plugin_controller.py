from fastapi import Query
from app.controllers.v1.base import new_router
from app.plugins import plugin_manager
from app.utils import utils

router = new_router()


@router.get("/plugins", summary="List all plugins")
def list_plugins(plugin_type: str = Query(None)):
    plugins = plugin_manager.list_plugins(plugin_type)
    return utils.get_response(200, plugins)


@router.post("/plugins/{plugin_type}/{name}/activate", summary="Set plugin as active")
def activate_plugin(plugin_type: str, name: str):
    plugin = plugin_manager.get_plugin(plugin_type, name)
    if not plugin:
        return utils.get_response(404, message=f"Plugin {name} not found")
    plugin_manager.set_active(plugin_type, name)
    return utils.get_response(200, {"message": f"Activated {name} for {plugin_type}"})


@router.post("/plugins/{plugin_type}/{name}/enable", summary="Enable plugin")
def enable_plugin(plugin_type: str, name: str):
    plugin_manager.enable_plugin(plugin_type, name)
    return utils.get_response(200, {"message": f"Enabled {name}"})


@router.post("/plugins/{plugin_type}/{name}/disable", summary="Disable plugin")
def disable_plugin(plugin_type: str, name: str):
    plugin_manager.disable_plugin(plugin_type, name)
    return utils.get_response(200, {"message": f"Disabled {name}"})
