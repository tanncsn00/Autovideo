import pytest
from app.plugins.manager import PluginManager


class TestBuiltinPluginDiscovery:
    def test_discovers_all_builtin_plugins(self):
        manager = PluginManager()
        manager.discover_plugins()
        plugins = manager.list_plugins()
        names = [p["name"] for p in plugins]
        assert "openai" in names
        assert "edge-tts" in names
        assert "pexels" in names

    def test_plugin_types_correct(self):
        manager = PluginManager()
        manager.discover_plugins()
        llm_plugins = manager.list_plugins("llm")
        assert any(p["name"] == "openai" for p in llm_plugins)
        tts_plugins = manager.list_plugins("tts")
        assert any(p["name"] == "edge-tts" for p in tts_plugins)
        material_plugins = manager.list_plugins("material")
        assert any(p["name"] == "pexels" for p in material_plugins)

    def test_edge_tts_always_available(self):
        manager = PluginManager()
        manager.discover_plugins()
        tts = manager.get_active_plugin("tts")
        assert tts is not None
        assert tts.is_available() is True

    def test_openai_meta(self):
        manager = PluginManager()
        manager.discover_plugins()
        plugin = manager.get_plugin("llm", "openai")
        meta = plugin.get_meta()
        assert meta.display_name == "OpenAI GPT"
        assert "gpt-4o" in plugin.get_models()
