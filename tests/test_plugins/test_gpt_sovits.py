import pytest
from app.plugins.builtin.tts.gpt_sovits_plugin import GPTSoVITSPlugin


def test_meta():
    p = GPTSoVITSPlugin()
    meta = p.get_meta()
    assert meta.name == "gpt-sovits"
    assert meta.plugin_type == "tts"
    assert "voice clone" in meta.description.lower() or "voice cloning" in meta.description.lower()


def test_is_available_when_server_down():
    p = GPTSoVITSPlugin()
    # Server is not running in test environment
    assert p.is_available() is False


def test_get_voices():
    p = GPTSoVITSPlugin()
    voices = p.get_voices()
    assert len(voices) >= 1
    # Should have setup instructions
    assert any("setup" in v["name"].lower() for v in voices)


def test_get_status():
    p = GPTSoVITSPlugin()
    status = p.get_status()
    assert "server_running" in status
    assert status["server_running"] is False  # Not running in test


def test_plugin_discovered():
    from app.plugins.manager import PluginManager
    m = PluginManager()
    m.discover_plugins()
    tts_plugins = m.list_plugins("tts")
    names = [p["name"] for p in tts_plugins]
    assert "gpt-sovits" in names
