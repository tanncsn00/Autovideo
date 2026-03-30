import pytest
from pathlib import Path
from app.config.migration import migrate_v1_to_v2


@pytest.fixture
def legacy_config(tmp_path):
    config = tmp_path / "config.toml"
    config.write_text('''
[app]
video_source = "pexels"
llm_provider = "openai"
openai_api_key = "sk-test-123"
openai_base_url = "https://api.openai.com/v1"
openai_model_name = "gpt-4o-mini"
pexels_api_keys = ["pexels-key-1", "pexels-key-2"]
pixabay_api_keys = []
max_concurrent_tasks = 3

[whisper]
model_size = "large-v3"
device = "cuda"
compute_type = "float16"

[azure]
speech_key = "azure-speech-key-123"
speech_region = "eastus"

[siliconflow]
api_key = "sf-key-456"

[ui]
language = "zh"
hide_log = true
''', encoding='utf-8')
    return config


@pytest.fixture
def empty_config(tmp_path):
    config = tmp_path / "config.toml"
    config.write_text('''
[app]
video_source = "pexels"

[ui]
language = "en-US"
''', encoding='utf-8')
    return config


class TestConfigMigration:
    def test_creates_backup(self, legacy_config):
        migrate_v1_to_v2(legacy_config)
        backup = legacy_config.with_suffix(".toml.bak")
        assert backup.exists()

    def test_backup_content_matches_original(self, legacy_config):
        original_content = legacy_config.read_text()
        migrate_v1_to_v2(legacy_config)
        backup = legacy_config.with_suffix(".toml.bak")
        assert backup.read_text() == original_content

    def test_extracts_secrets(self, legacy_config):
        result = migrate_v1_to_v2(legacy_config)
        secrets = result["secrets"]
        assert secrets["openai_api_key"] == "sk-test-123"
        assert secrets["openai_base_url"] == "https://api.openai.com/v1"
        assert "pexels-key-1" in secrets["pexels_api_keys"]
        assert secrets["azure_speech_key"] == "azure-speech-key-123"
        assert secrets["azure_speech_region"] == "eastus"
        assert secrets["siliconflow_api_key"] == "sf-key-456"

    def test_secrets_not_in_config(self, legacy_config):
        result = migrate_v1_to_v2(legacy_config)
        config = result["config"]
        # Secrets should NOT appear in the new config
        assert "openai_api_key" not in str(config.get("app", {}))
        assert "speech_key" not in str(config)

    def test_maps_settings(self, legacy_config):
        result = migrate_v1_to_v2(legacy_config)
        config = result["config"]
        assert config["app"]["video_source"] == "pexels"
        assert config["app"]["language"] == "zh"
        assert config["app"]["hide_log"] is True
        assert config["app"]["max_concurrent_tasks"] == 3

    def test_maps_whisper(self, legacy_config):
        result = migrate_v1_to_v2(legacy_config)
        config = result["config"]
        assert config["whisper"]["model_size"] == "large-v3"
        assert config["whisper"]["device"] == "cuda"
        assert config["whisper"]["compute_type"] == "float16"

    def test_maps_llm_provider_to_plugin(self, legacy_config):
        result = migrate_v1_to_v2(legacy_config)
        config = result["config"]
        assert config["plugins"]["active"]["llm"] == "openai"

    def test_empty_secrets_not_included(self, empty_config):
        result = migrate_v1_to_v2(empty_config)
        secrets = result["secrets"]
        # Empty values should not be in secrets
        assert len(secrets) == 0 or all(v for v in secrets.values())

    def test_pexels_keys_joined_as_csv(self, legacy_config):
        result = migrate_v1_to_v2(legacy_config)
        pexels = result["secrets"].get("pexels_api_keys", "")
        assert "pexels-key-1" in pexels
        assert "pexels-key-2" in pexels

    def test_nonexistent_config_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            migrate_v1_to_v2(tmp_path / "nonexistent.toml")

    def test_preserves_original_file(self, legacy_config):
        original_content = legacy_config.read_text()
        migrate_v1_to_v2(legacy_config)
        assert legacy_config.read_text() == original_content
