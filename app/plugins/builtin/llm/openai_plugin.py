from app.plugins.builtin.llm.base_openai_compatible import OpenAICompatibleLLMPlugin

class OpenAIPlugin(OpenAICompatibleLLMPlugin):
    NAME = "openai"
    DISPLAY_NAME = "OpenAI GPT"
    DESCRIPTION = "OpenAI GPT models — GPT-4o, GPT-4, GPT-3.5"
    DEFAULT_BASE_URL = "https://api.openai.com/v1"
    DEFAULT_MODEL = "gpt-4o-mini"
    MODELS = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
    API_KEY_NAME = "openai_api_key"
