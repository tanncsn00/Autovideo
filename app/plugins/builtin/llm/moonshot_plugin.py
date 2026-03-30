from app.plugins.builtin.llm.base_openai_compatible import OpenAICompatibleLLMPlugin

class MoonshotPlugin(OpenAICompatibleLLMPlugin):
    NAME = "moonshot"
    DISPLAY_NAME = "Moonshot AI (Kimi)"
    DESCRIPTION = "Moonshot Kimi — long context window, good for Chinese"
    DEFAULT_BASE_URL = "https://api.moonshot.cn/v1"
    DEFAULT_MODEL = "moonshot-v1-8k"
    MODELS = ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]
    API_KEY_NAME = "moonshot_api_key"
