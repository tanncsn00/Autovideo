from app.plugins.builtin.llm.base_openai_compatible import OpenAICompatibleLLMPlugin

class DeepSeekPlugin(OpenAICompatibleLLMPlugin):
    NAME = "deepseek"
    DISPLAY_NAME = "DeepSeek"
    DESCRIPTION = "DeepSeek models — strong reasoning and coding"
    DEFAULT_BASE_URL = "https://api.deepseek.com/v1"
    DEFAULT_MODEL = "deepseek-chat"
    MODELS = ["deepseek-chat", "deepseek-reasoner"]
    API_KEY_NAME = "deepseek_api_key"
