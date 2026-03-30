"""Base class for OpenAI-compatible LLM plugins.

Most LLM providers (OpenAI, DeepSeek, Groq, Mistral, Qwen, Moonshot)
use the same OpenAI-compatible API format. This base class eliminates
95% of the duplicated code.

Usage:
    class GroqPlugin(OpenAICompatibleLLMPlugin):
        NAME = "groq"
        DISPLAY_NAME = "Groq"
        DESCRIPTION = "Fastest LLM inference"
        DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"
        DEFAULT_MODEL = "llama-3.3-70b-versatile"
        MODELS = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]
        API_KEY_NAME = "groq_api_key"
"""

from app.plugins.base import LLMPlugin, PluginMeta
from app.config.config import get_api_key, app


class OpenAICompatibleLLMPlugin(LLMPlugin):
    """Base for any LLM provider that uses the OpenAI chat completions API format."""

    # Subclasses MUST override these
    NAME: str = ""
    DISPLAY_NAME: str = ""
    DESCRIPTION: str = ""
    DEFAULT_BASE_URL: str = ""
    DEFAULT_MODEL: str = ""
    MODELS: list[str] = []
    API_KEY_NAME: str = ""  # e.g. "groq_api_key"

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name=self.NAME,
            display_name=self.DISPLAY_NAME,
            version="1.0.0",
            description=self.DESCRIPTION,
            author="MoneyPrinterTurbo",
            plugin_type="llm",
            config_schema={
                "api_key": {"type": "string", "required": True},
                "base_url": {"type": "string", "default": self.DEFAULT_BASE_URL},
                "model_name": {"type": "string", "default": self.DEFAULT_MODEL},
            },
            builtin=True,
        )

    def validate_config(self, config: dict) -> bool:
        return bool(config.get("api_key"))

    def is_available(self) -> bool:
        api_key = get_api_key(self.API_KEY_NAME)
        return bool(api_key and api_key.strip())

    async def generate_response(self, prompt: str, **kwargs) -> str:
        from openai import OpenAI

        api_key = get_api_key(self.API_KEY_NAME)
        base_url = (get_api_key(f"{self.NAME}_base_url")
                    or app.get(f"{self.NAME}_base_url", self.DEFAULT_BASE_URL))
        model = app.get(f"{self.NAME}_model_name", self.DEFAULT_MODEL)

        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def get_models(self) -> list[str]:
        return self.MODELS
