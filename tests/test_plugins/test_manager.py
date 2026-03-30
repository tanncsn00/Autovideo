import pytest
from pathlib import Path
from app.plugins.manager import PluginManager


class TestPluginManager:
    def test_init(self):
        manager = PluginManager()
        assert manager.registry is not None

    def test_discover_with_no_builtin_dir(self, tmp_path):
        manager = PluginManager()
        # Should not crash even if builtin dir is empty/missing
        manager.discover_plugins()
        plugins = manager.list_plugins()
        assert isinstance(plugins, list)

    def test_get_active_nonexistent_type(self):
        manager = PluginManager()
        assert manager.get_active_plugin("nonexistent") is None

    def test_get_plugin_nonexistent(self):
        manager = PluginManager()
        assert manager.get_plugin("llm", "nonexistent") is None

    def test_add_plugin_dir(self, tmp_path):
        manager = PluginManager()
        manager.add_plugin_dir(tmp_path)
        assert tmp_path in manager._plugin_dirs

    def test_discover_from_custom_dir(self, tmp_path):
        # Create a fake plugin directory structure
        llm_dir = tmp_path / "llm"
        llm_dir.mkdir()
        plugin_file = llm_dir / "test_plugin.py"
        plugin_file.write_text('''
from app.plugins.base import LLMPlugin, PluginMeta

class TestPlugin(LLMPlugin):
    def get_meta(self):
        return PluginMeta(
            name="test-dynamic", display_name="Test Dynamic",
            version="1.0.0", description="Dynamic test",
            author="test", plugin_type="llm",
        )
    def validate_config(self, config): return True
    def is_available(self): return True
    async def generate_response(self, prompt, **kwargs): return "dynamic"
    def get_models(self): return []
''')

        manager = PluginManager()
        manager.add_plugin_dir(tmp_path)
        manager.discover_plugins()

        plugins = manager.list_plugins("llm")
        names = [p["name"] for p in plugins]
        assert "test-dynamic" in names

    def test_enable_disable(self, tmp_path):
        # Setup a plugin
        llm_dir = tmp_path / "llm"
        llm_dir.mkdir()
        plugin_file = llm_dir / "dummy_plugin.py"
        plugin_file.write_text('''
from app.plugins.base import LLMPlugin, PluginMeta

class DummyPlugin(LLMPlugin):
    def get_meta(self):
        return PluginMeta(
            name="dummy", display_name="Dummy",
            version="1.0.0", description="Dummy",
            author="test", plugin_type="llm",
        )
    def validate_config(self, config): return True
    def is_available(self): return True
    async def generate_response(self, prompt, **kwargs): return "dummy"
    def get_models(self): return []
''')

        manager = PluginManager()
        manager.add_plugin_dir(tmp_path)
        manager.discover_plugins()

        manager.disable_plugin("llm", "dummy")
        plugins = manager.list_plugins("llm")
        dummy = next(p for p in plugins if p["name"] == "dummy")
        assert dummy["enabled"] is False

        manager.enable_plugin("llm", "dummy")
        plugins = manager.list_plugins("llm")
        dummy = next(p for p in plugins if p["name"] == "dummy")
        assert dummy["enabled"] is True


class TestRunAsync:
    def test_run_async_from_sync(self):
        from app.plugins.utils import run_async
        import asyncio

        async def async_func():
            return 42

        result = run_async(async_func())
        assert result == 42
