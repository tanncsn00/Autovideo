import os
import sys

try:
    import tomllib
except ImportError:
    import tomli as tomllib

import tomli_w
from pathlib import Path
from platformdirs import user_data_dir


APP_NAME = "MoneyPrinterTurbo"
APP_AUTHOR = "MoneyPrinterTurbo"


def get_config_dir() -> Path:
    """Get OS-appropriate config directory"""
    config_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_path() -> Path:
    return get_config_dir() / "config.toml"


class ConfigManager:
    """Manages application configuration with persistence"""

    def __init__(self, config_path: Path = None):
        self._config_path = config_path or get_config_path()
        self._config: dict = {}
        self._load()

    def _load(self):
        if self._config_path.exists():
            with open(self._config_path, "rb") as f:
                self._config = tomllib.load(f)
        else:
            self._config = self._defaults()
            self._save()

    def _save(self):
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._config_path, "wb") as f:
            tomli_w.dump(self._config, f)

    def _defaults(self) -> dict:
        return {
            "app": {
                "language": "en-US",
                "video_source": "pexels",
                "llm_provider": "openai",
                "max_concurrent_tasks": 5,
                "hide_log": False,
            },
            "video": {
                "aspect": "16:9",
                "concat_mode": "random",
                "transition": "FadeIn",
                "clip_duration": 5,
                "threads": 2,
                "count": 1,
            },
            "audio": {
                "voice": "en-US-AriaNeural-Female",
                "voice_rate": 1.0,
                "voice_volume": 1.0,
                "bgm_volume": 0.2,
            },
            "subtitle": {
                "enabled": True,
                "position": "bottom",
                "font_size": 60,
                "text_fore_color": "#FFFFFF",
                "stroke_color": "#000000",
                "stroke_width": 1.5,
            },
            "whisper": {
                "model_size": "large-v3",
                "device": "cpu",
                "compute_type": "int8",
            },
            "plugins": {
                "active": {
                    "llm": "openai",
                    "tts": "edge-tts",
                    "material": "pexels",
                }
            },
        }

    def get(self, section: str, key: str, default=None):
        return self._config.get(section, {}).get(key, default)

    def set(self, section: str, key: str, value):
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
        self._save()

    def get_section(self, section: str) -> dict:
        return self._config.get(section, {}).copy()

    def get_all(self) -> dict:
        return self._config.copy()

    def update(self, data: dict):
        """Deep merge update"""
        self._deep_merge(self._config, data)
        self._save()

    def reset(self):
        """Reset to defaults"""
        self._config = self._defaults()
        self._save()

    @staticmethod
    def _deep_merge(base: dict, override: dict):
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                ConfigManager._deep_merge(base[key], value)
            else:
                base[key] = value
