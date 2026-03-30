import os
import pytest
from app.config.config import get_mode, is_desktop_mode, get_api_key


def test_default_mode_is_api():
    os.environ.pop("MPT_MODE", None)
    assert get_mode() == "api"
    assert is_desktop_mode() is False


def test_desktop_mode_detected():
    os.environ["MPT_MODE"] = "desktop"
    assert get_mode() == "desktop"
    assert is_desktop_mode() is True
    os.environ.pop("MPT_MODE")


def test_get_api_key_from_env():
    os.environ["MPT_TEST_KEY"] = "env-value"
    assert get_api_key("test_key") == "env-value"
    os.environ.pop("MPT_TEST_KEY")


def test_get_api_key_fallback_to_config():
    os.environ.pop("MPT_OPENAI_API_KEY", None)
    # Should fall back to config.toml value (may be empty string)
    result = get_api_key("openai_api_key")
    assert isinstance(result, str)
