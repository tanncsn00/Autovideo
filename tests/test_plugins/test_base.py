import pytest
from app.plugins.base import (
    BasePlugin, LLMPlugin, TTSPlugin, MaterialPlugin,
    EffectPlugin, MusicPlugin, PluginMeta, PluginConfig,
)


# --- Mock implementations for testing ---

class MockLLMPlugin(LLMPlugin):
    def get_meta(self):
        return PluginMeta(
            name="mock-llm", display_name="Mock LLM", version="1.0.0",
            description="Test LLM", author="test", plugin_type="llm",
        )
    def validate_config(self, config): return True
    def is_available(self): return True
    async def generate_response(self, prompt, **kwargs): return f"response to: {prompt}"
    def get_models(self): return ["mock-model-1", "mock-model-2"]


class MockTTSPlugin(TTSPlugin):
    def get_meta(self):
        return PluginMeta(
            name="mock-tts", display_name="Mock TTS", version="1.0.0",
            description="Test TTS", author="test", plugin_type="tts",
        )
    def validate_config(self, config): return True
    def is_available(self): return True
    async def synthesize(self, text, voice, rate=1.0, output_path=""):
        return output_path, None
    def get_voices(self):
        return [{"id": "voice-1", "name": "Voice 1", "language": "en", "gender": "Female"}]


class MockMaterialPlugin(MaterialPlugin):
    def get_meta(self):
        return PluginMeta(
            name="mock-material", display_name="Mock Material", version="1.0.0",
            description="Test Material", author="test", plugin_type="material",
        )
    def validate_config(self, config): return True
    def is_available(self): return True
    async def search(self, query, aspect="16:9", max_results=10):
        return [{"url": "http://example.com/video.mp4", "duration": 10}]
    async def download(self, url, output_dir):
        return f"{output_dir}/video.mp4"


# --- Tests ---

class TestPluginMeta:
    def test_create_meta(self):
        meta = PluginMeta(
            name="test", display_name="Test", version="1.0.0",
            description="desc", author="auth", plugin_type="llm",
        )
        assert meta.name == "test"
        assert meta.plugin_type == "llm"
        assert meta.builtin is True
        assert meta.config_schema == {}

    def test_meta_with_config_schema(self):
        meta = PluginMeta(
            name="test", display_name="Test", version="1.0.0",
            description="desc", author="auth", plugin_type="llm",
            config_schema={"api_key": {"type": "string"}},
        )
        assert "api_key" in meta.config_schema


class TestPluginConfig:
    def test_default_config(self):
        config = PluginConfig()
        assert config.enabled is True
        assert config.priority == 0


class TestAbstractPlugins:
    def test_cannot_instantiate_base_plugin(self):
        with pytest.raises(TypeError):
            BasePlugin()

    def test_cannot_instantiate_llm_plugin(self):
        with pytest.raises(TypeError):
            LLMPlugin()

    def test_cannot_instantiate_tts_plugin(self):
        with pytest.raises(TypeError):
            TTSPlugin()

    def test_cannot_instantiate_material_plugin(self):
        with pytest.raises(TypeError):
            MaterialPlugin()

    def test_cannot_instantiate_effect_plugin(self):
        with pytest.raises(TypeError):
            EffectPlugin()

    def test_cannot_instantiate_music_plugin(self):
        with pytest.raises(TypeError):
            MusicPlugin()


class TestMockLLMPlugin:
    def test_instantiation(self):
        plugin = MockLLMPlugin()
        meta = plugin.get_meta()
        assert meta.name == "mock-llm"
        assert meta.plugin_type == "llm"

    def test_is_available(self):
        assert MockLLMPlugin().is_available() is True

    def test_validate_config(self):
        assert MockLLMPlugin().validate_config({}) is True

    def test_get_models(self):
        models = MockLLMPlugin().get_models()
        assert len(models) == 2

    @pytest.mark.asyncio
    async def test_generate_response(self):
        plugin = MockLLMPlugin()
        result = await plugin.generate_response("hello")
        assert "hello" in result


class TestMockTTSPlugin:
    def test_instantiation(self):
        plugin = MockTTSPlugin()
        assert plugin.get_meta().plugin_type == "tts"

    def test_get_voices(self):
        voices = MockTTSPlugin().get_voices()
        assert len(voices) == 1
        assert voices[0]["id"] == "voice-1"


class TestMockMaterialPlugin:
    def test_instantiation(self):
        plugin = MockMaterialPlugin()
        assert plugin.get_meta().plugin_type == "material"

    @pytest.mark.asyncio
    async def test_search(self):
        results = await MockMaterialPlugin().search("test")
        assert len(results) == 1
