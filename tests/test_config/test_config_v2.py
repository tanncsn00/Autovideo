import pytest
from pathlib import Path
from app.config.config_v2 import ConfigManager


@pytest.fixture
def config_manager(tmp_path):
    """Create a ConfigManager with a temp directory"""
    config_path = tmp_path / "config.toml"
    return ConfigManager(config_path=config_path)


class TestConfigManager:
    def test_creates_default_config(self, tmp_path):
        config_path = tmp_path / "config.toml"
        cm = ConfigManager(config_path=config_path)
        assert config_path.exists()

    def test_default_values(self, config_manager):
        assert config_manager.get("app", "language") == "en-US"
        assert config_manager.get("video", "aspect") == "16:9"
        assert config_manager.get("audio", "voice") == "en-US-AriaNeural-Female"
        assert config_manager.get("subtitle", "enabled") is True

    def test_get_nonexistent_section(self, config_manager):
        assert config_manager.get("nonexistent", "key") is None

    def test_get_nonexistent_key(self, config_manager):
        assert config_manager.get("app", "nonexistent") is None

    def test_get_with_default(self, config_manager):
        assert config_manager.get("app", "nonexistent", "fallback") == "fallback"

    def test_set_value(self, config_manager):
        config_manager.set("app", "language", "ja")
        assert config_manager.get("app", "language") == "ja"

    def test_set_new_section(self, config_manager):
        config_manager.set("custom", "key", "value")
        assert config_manager.get("custom", "key") == "value"

    def test_persistence(self, tmp_path):
        config_path = tmp_path / "config.toml"
        cm1 = ConfigManager(config_path=config_path)
        cm1.set("app", "language", "ko")

        cm2 = ConfigManager(config_path=config_path)
        assert cm2.get("app", "language") == "ko"

    def test_get_section(self, config_manager):
        section = config_manager.get_section("app")
        assert "language" in section
        assert "video_source" in section

    def test_get_all(self, config_manager):
        all_config = config_manager.get_all()
        assert "app" in all_config
        assert "video" in all_config
        assert "audio" in all_config

    def test_update_deep_merge(self, config_manager):
        config_manager.update({"app": {"language": "fr"}, "video": {"aspect": "9:16"}})
        assert config_manager.get("app", "language") == "fr"
        assert config_manager.get("video", "aspect") == "9:16"
        # Other values should be preserved
        assert config_manager.get("app", "video_source") == "pexels"

    def test_update_preserves_nested(self, config_manager):
        config_manager.update({"plugins": {"active": {"llm": "gemini"}}})
        assert config_manager.get("plugins", "active")["llm"] == "gemini"
        # Other active plugins preserved
        assert config_manager.get("plugins", "active")["tts"] == "edge-tts"

    def test_reset(self, config_manager):
        config_manager.set("app", "language", "xx")
        config_manager.reset()
        assert config_manager.get("app", "language") == "en-US"

    def test_get_section_returns_copy(self, config_manager):
        """Modifying returned section should not affect internal state"""
        section = config_manager.get_section("app")
        section["language"] = "modified"
        assert config_manager.get("app", "language") == "en-US"
