import shutil
from pathlib import Path
from loguru import logger

try:
    import tomllib
except ImportError:
    import tomli as tomllib


# Settings that map from old config to new config structure
SETTINGS_MAP = {
    # (old_section, old_key) → (new_section, new_key)
    ("app", "video_source"): ("app", "video_source"),
    ("app", "llm_provider"): ("plugins.active", "llm"),
    ("app", "max_concurrent_tasks"): ("app", "max_concurrent_tasks"),
    ("ui", "language"): ("app", "language"),
    ("ui", "hide_log"): ("app", "hide_log"),
    ("whisper", "model_size"): ("whisper", "model_size"),
    ("whisper", "device"): ("whisper", "device"),
    ("whisper", "compute_type"): ("whisper", "compute_type"),
}

# Keys that are secrets — extracted to keychain, NOT written to new config
SECRET_KEYS = [
    ("app", "openai_api_key"),
    ("app", "openai_base_url"),
    ("app", "openai_model_name"),
    ("app", "pexels_api_keys"),
    ("app", "pixabay_api_keys"),
    ("app", "moonshot_api_key"),
    ("app", "moonshot_base_url"),
    ("app", "moonshot_model_name"),
    ("app", "ollama_api_key"),
    ("app", "ollama_base_url"),
    ("app", "ollama_model_name"),
    ("app", "oneapi_api_key"),
    ("app", "oneapi_base_url"),
    ("app", "oneapi_model_name"),
    ("app", "g4f_model_name"),
    ("app", "deepseek_api_key"),
    ("app", "deepseek_base_url"),
    ("app", "deepseek_model_name"),
    ("app", "qwen_api_key"),
    ("app", "qwen_base_url"),
    ("app", "qwen_model_name"),
    ("app", "gemini_api_key"),
    ("app", "gemini_model_name"),
    ("app", "cloudflare_api_key"),
    ("app", "cloudflare_account_id"),
    ("app", "cloudflare_model_name"),
    ("app", "ernie_api_key"),
    ("app", "ernie_secret_key"),
    ("app", "ernie_model_name"),
    ("azure", "speech_key"),
    ("azure", "speech_region"),
    ("siliconflow", "api_key"),
]


def migrate_v1_to_v2(legacy_config_path: Path) -> dict:
    """
    Migrate from old config.toml to new v2 format.

    Returns:
        {
            "config": dict,      # New config (non-sensitive settings)
            "secrets": dict,     # Extracted secrets (API keys)
            "backup_path": Path, # Path to backup file
        }
    """
    if not legacy_config_path.exists():
        raise FileNotFoundError(f"Config file not found: {legacy_config_path}")

    # 1. Create backup
    backup_path = legacy_config_path.with_suffix(".toml.bak")
    shutil.copy2(legacy_config_path, backup_path)
    logger.info(f"Config backup created: {backup_path}")

    # 2. Read old config
    try:
        with open(legacy_config_path, "rb") as f:
            old_config = tomllib.load(f)
    except Exception:
        with open(legacy_config_path, "r", encoding="utf-8-sig") as f:
            import toml
            old_config = toml.loads(f.read())

    # 3. Extract secrets
    secrets = {}
    for section, key in SECRET_KEYS:
        value = old_config.get(section, {}).get(key, "")
        if value:
            # Flatten the key name: "app.openai_api_key" → "openai_api_key"
            # "azure.speech_key" → "azure_speech_key"
            if section == "app":
                secret_key = key
            else:
                secret_key = f"{section}_{key}"

            # Handle list values (e.g., pexels_api_keys = ["key1", "key2"])
            if isinstance(value, list):
                value = ",".join(str(v) for v in value if v)

            if value:  # Only store non-empty
                secrets[secret_key] = str(value)

    # 4. Map settings to new structure
    return {
        "config": _build_new_config(old_config),
        "secrets": secrets,
        "backup_path": backup_path,
    }


def _build_new_config(old_config: dict) -> dict:
    """Build new config structure from old config values"""
    new = {
        "app": {
            "language": old_config.get("ui", {}).get("language", "en-US"),
            "video_source": old_config.get("app", {}).get("video_source", "pexels"),
            "llm_provider": old_config.get("app", {}).get("llm_provider", "openai"),
            "max_concurrent_tasks": old_config.get("app", {}).get("max_concurrent_tasks", 5),
            "hide_log": old_config.get("ui", {}).get("hide_log", False),
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
            "model_size": old_config.get("whisper", {}).get("model_size", "large-v3"),
            "device": old_config.get("whisper", {}).get("device", "cpu"),
            "compute_type": old_config.get("whisper", {}).get("compute_type", "int8"),
        },
        "plugins": {
            "active": {
                "llm": old_config.get("app", {}).get("llm_provider", "openai"),
                "tts": "edge-tts",
                "material": old_config.get("app", {}).get("video_source", "pexels"),
            }
        },
    }
    return new
