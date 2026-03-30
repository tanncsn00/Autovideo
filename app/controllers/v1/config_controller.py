import os
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel
from app.controllers.v1.base import new_router
from app.config.config import is_desktop_mode
from app.utils import utils

router = new_router()

ALLOWED_SECRET_KEYS = {
    "openai_api_key", "openai_base_url", "openai_model_name",
    "pexels_api_keys", "pixabay_api_keys", "unsplash_access_key",
    "azure_speech_key", "azure_speech_region",
    "siliconflow_api_key",
    "moonshot_api_key", "moonshot_base_url", "moonshot_model_name",
    "ollama_api_key", "ollama_base_url", "ollama_model_name",
    "oneapi_api_key", "oneapi_base_url", "oneapi_model_name",
    "deepseek_api_key", "deepseek_base_url", "deepseek_model_name",
    "qwen_api_key", "qwen_base_url", "qwen_model_name",
    "gemini_api_key", "gemini_model_name",
    "cloudflare_api_key", "cloudflare_account_id", "cloudflare_model_name",
    "ernie_api_key", "ernie_secret_key", "ernie_model_name",
    "g4f_model_name",
    "claude_api_key", "claude_base_url", "claude_model_name", "claude_max_tokens",
    "groq_api_key", "groq_model_name",
    "mistral_api_key", "mistral_model_name",
    "elevenlabs_api_key", "elevenlabs_model_id",
    "youtube_client_id", "youtube_client_secret", "youtube_refresh_token",
    "tiktok_access_token",
    "instagram_access_token", "instagram_user_id",
    "facebook_access_token", "facebook_page_id",
    "twitter_bearer_token",
    "linkedin_access_token", "linkedin_person_urn",
    "gpt_sovits_api_url", "gpt_sovits_reference_audio", "gpt_sovits_reference_text",
    "gpt_sovits_text_lang", "gpt_sovits_prompt_lang",
    "fpt_ai_api_key",
    "vbee_api_key", "vbee_app_id",
    "tiktok_account_name",
}


@router.get("/config", summary="Get app configuration")
def get_config():
    if is_desktop_mode():
        from app.config.config_v2 import ConfigManager
        cm = ConfigManager()
        return utils.get_response(200, cm.get_all())
    else:
        from app.config import config
        return utils.get_response(200, {
            "app": config.app,
            "ui": config.ui,
            "whisper": config.whisper,
        })


class ConfigUpdateRequest(BaseModel):
    data: dict


@router.put("/config", summary="Update configuration")
def update_config(body: ConfigUpdateRequest):
    if is_desktop_mode():
        from app.config.config_v2 import ConfigManager
        cm = ConfigManager()
        cm.update(body.data)
        return utils.get_response(200, {"message": "Config updated"})
    raise HTTPException(400, "Config update only available in desktop mode")


class SecretsUpdateRequest(BaseModel):
    secrets: dict


@router.put("/config/secrets", summary="Receive secrets from desktop frontend")
def update_secrets(body: SecretsUpdateRequest):
    if not is_desktop_mode():
        raise HTTPException(400, "Secrets endpoint only available in desktop mode")

    from app.config import config as cfg
    from app.config.config_v2 import ConfigManager
    cm = ConfigManager()

    set_count = 0
    for key, value in body.secrets.items():
        if key not in ALLOWED_SECRET_KEYS:
            raise HTTPException(400, f"Unknown secret key: {key}")
        if value:  # Only set non-empty values
            os.environ[f"MPT_{key.upper()}"] = str(value)
            cfg.app[key] = value
            # Persist to config file so it survives restart
            cm.set("app", key, value)
            set_count += 1

    return utils.get_response(200, {"message": f"Set {set_count} secrets"})


@router.get("/config/defaults", summary="Get default configuration values")
def get_config_defaults():
    from app.config.config_v2 import ConfigManager
    cm = ConfigManager.__new__(ConfigManager)
    return utils.get_response(200, cm._defaults())
