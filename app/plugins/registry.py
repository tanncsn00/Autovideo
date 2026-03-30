from app.plugins.base import BasePlugin


class PluginRegistry:
    """Stores and retrieves plugin instances"""

    def __init__(self):
        self._plugins: dict[str, dict[str, BasePlugin]] = {}
        self._active: dict[str, str] = {}
        self._enabled: dict[str, dict[str, bool]] = {}

    def register(self, plugin_type: str, name: str, plugin: BasePlugin):
        if plugin_type not in self._plugins:
            self._plugins[plugin_type] = {}
            self._enabled[plugin_type] = {}
        self._plugins[plugin_type][name] = plugin
        self._enabled[plugin_type][name] = True
        if plugin_type not in self._active:
            self._active[plugin_type] = name

    def get(self, plugin_type: str, name: str) -> BasePlugin | None:
        return self._plugins.get(plugin_type, {}).get(name)

    def get_active(self, plugin_type: str) -> BasePlugin | None:
        name = self._active.get(plugin_type)
        if name:
            return self.get(plugin_type, name)
        return None

    def set_active(self, plugin_type: str, name: str):
        if name in self._plugins.get(plugin_type, {}):
            self._active[plugin_type] = name

    def enable(self, plugin_type: str, name: str):
        if plugin_type in self._enabled:
            self._enabled[plugin_type][name] = True

    def disable(self, plugin_type: str, name: str):
        if plugin_type in self._enabled:
            self._enabled[plugin_type][name] = False

    def list(self, plugin_type: str = None) -> list[dict]:
        results = []
        types = [plugin_type] if plugin_type else list(self._plugins.keys())
        for pt in types:
            for name, plugin in self._plugins.get(pt, {}).items():
                meta = plugin.get_meta()
                results.append({
                    **meta.model_dump(),
                    "enabled": self._enabled.get(pt, {}).get(name, True),
                    "active": self._active.get(pt) == name,
                    "available": plugin.is_available(),
                })
        return results
