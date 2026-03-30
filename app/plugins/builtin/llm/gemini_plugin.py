from app.plugins.base import LLMPlugin, PluginMeta
from app.config.config import get_api_key, app


class GeminiPlugin(LLMPlugin):

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="gemini",
            display_name="Google Gemini",
            version="1.0.0",
            description="Google Gemini models — multimodal, strong reasoning",
            author="MoneyPrinterTurbo",
            plugin_type="llm",
            config_schema={
                "api_key": {"type": "string", "required": True},
                "model_name": {"type": "string", "default": "gemini-2.0-flash"},
            },
            builtin=True,
        )

    def validate_config(self, config: dict) -> bool:
        return bool(config.get("api_key"))

    def is_available(self) -> bool:
        api_key = get_api_key("gemini_api_key")
        return bool(api_key and api_key.strip())

    async def generate_response(self, prompt: str, **kwargs) -> str:
        import google.generativeai as genai

        api_key = get_api_key("gemini_api_key")
        model_name = app.get("gemini_model_name", "gemini-2.0-flash")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text

    def get_models(self) -> list[str]:
        return ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-pro", "gemini-1.5-flash"]
