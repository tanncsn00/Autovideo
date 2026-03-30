import importlib
import importlib.util
from pathlib import Path
from loguru import logger
from app.plugins.base import BasePlugin, PluginMeta
from app.plugins.registry import PluginRegistry


class PluginManager:
    """Discovers, loads, and manages plugins"""

    def __init__(self):
        self.registry = PluginRegistry()
        self._plugin_dirs: list[Path] = []

    def add_plugin_dir(self, path: Path):
        self._plugin_dirs.append(path)

    def discover_plugins(self):
        builtin_dir = Path(__file__).parent / "builtin"
        if builtin_dir.exists():
            self._scan_directory(builtin_dir)

        for plugin_dir in self._plugin_dirs:
            if plugin_dir.exists():
                self._scan_directory(plugin_dir)

    def _scan_directory(self, directory: Path):
        for category_dir in directory.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith("_"):
                continue
            for plugin_file in category_dir.glob("*_plugin.py"):
                self._load_plugin_file(plugin_file)

    def _load_plugin_file(self, filepath: Path):
        try:
            spec = importlib.util.spec_from_file_location(filepath.stem, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BasePlugin)
                    and attr is not BasePlugin
                    and not attr.__name__.startswith("Base")
                    and not attr.__name__.startswith("Mock")
                    and attr.__module__ == module.__name__
                ):
                    try:
                        plugin_instance = attr()
                        meta = plugin_instance.get_meta()
                        self.registry.register(meta.plugin_type, meta.name, plugin_instance)
                        logger.info(f"Loaded plugin: {meta.display_name} ({meta.name})")
                    except Exception as e:
                        logger.error(f"Failed to instantiate plugin {attr.__name__}: {e}")

        except Exception as e:
            logger.error(f"Failed to load plugin {filepath}: {e}")

    def get_plugin(self, plugin_type: str, name: str) -> BasePlugin | None:
        return self.registry.get(plugin_type, name)

    def get_active_plugin(self, plugin_type: str) -> BasePlugin | None:
        return self.registry.get_active(plugin_type)

    def list_plugins(self, plugin_type: str = None) -> list[dict]:
        return self.registry.list(plugin_type)

    def enable_plugin(self, plugin_type: str, name: str):
        self.registry.enable(plugin_type, name)

    def disable_plugin(self, plugin_type: str, name: str):
        self.registry.disable(plugin_type, name)

    def set_active(self, plugin_type: str, name: str):
        self.registry.set_active(plugin_type, name)
