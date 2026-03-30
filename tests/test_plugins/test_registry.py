import pytest
from app.plugins.registry import PluginRegistry
from app.plugins.base import LLMPlugin, PluginMeta


class MockLLMPlugin(LLMPlugin):
    def __init__(self, name="mock-llm"):
        self._name = name
    def get_meta(self):
        return PluginMeta(
            name=self._name, display_name=f"Mock {self._name}", version="1.0.0",
            description="Test", author="test", plugin_type="llm",
        )
    def validate_config(self, config): return True
    def is_available(self): return True
    async def generate_response(self, prompt, **kwargs): return "mock"
    def get_models(self): return ["model"]


class TestPluginRegistry:
    def test_register_and_get(self):
        reg = PluginRegistry()
        plugin = MockLLMPlugin()
        reg.register("llm", "mock-llm", plugin)
        assert reg.get("llm", "mock-llm") is plugin

    def test_get_nonexistent_returns_none(self):
        reg = PluginRegistry()
        assert reg.get("llm", "nonexistent") is None

    def test_first_registered_becomes_active(self):
        reg = PluginRegistry()
        p1 = MockLLMPlugin("p1")
        p2 = MockLLMPlugin("p2")
        reg.register("llm", "p1", p1)
        reg.register("llm", "p2", p2)
        assert reg.get_active("llm") is p1

    def test_set_active(self):
        reg = PluginRegistry()
        p1 = MockLLMPlugin("p1")
        p2 = MockLLMPlugin("p2")
        reg.register("llm", "p1", p1)
        reg.register("llm", "p2", p2)
        reg.set_active("llm", "p2")
        assert reg.get_active("llm") is p2

    def test_set_active_nonexistent_ignored(self):
        reg = PluginRegistry()
        p1 = MockLLMPlugin("p1")
        reg.register("llm", "p1", p1)
        reg.set_active("llm", "nonexistent")
        assert reg.get_active("llm") is p1

    def test_get_active_empty_returns_none(self):
        reg = PluginRegistry()
        assert reg.get_active("llm") is None

    def test_enable_disable(self):
        reg = PluginRegistry()
        plugin = MockLLMPlugin()
        reg.register("llm", "mock-llm", plugin)

        reg.disable("llm", "mock-llm")
        listed = reg.list("llm")
        assert listed[0]["enabled"] is False

        reg.enable("llm", "mock-llm")
        listed = reg.list("llm")
        assert listed[0]["enabled"] is True

    def test_list_returns_metadata(self):
        reg = PluginRegistry()
        plugin = MockLLMPlugin("test-plugin")
        reg.register("llm", "test-plugin", plugin)
        result = reg.list("llm")
        assert len(result) == 1
        assert result[0]["name"] == "test-plugin"
        assert result[0]["active"] is True
        assert result[0]["available"] is True
        assert result[0]["plugin_type"] == "llm"

    def test_list_all_types(self):
        reg = PluginRegistry()
        reg.register("llm", "p1", MockLLMPlugin("p1"))
        reg.register("tts", "p2", MockLLMPlugin("p2"))  # reuse mock, type in meta irrelevant here
        result = reg.list()
        assert len(result) == 2

    def test_list_filtered_by_type(self):
        reg = PluginRegistry()
        reg.register("llm", "p1", MockLLMPlugin("p1"))
        reg.register("tts", "p2", MockLLMPlugin("p2"))
        result = reg.list("llm")
        assert len(result) == 1
