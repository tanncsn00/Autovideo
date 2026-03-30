from app.plugins.builtin.llm.base_openai_compatible import OpenAICompatibleLLMPlugin

class MistralPlugin(OpenAICompatibleLLMPlugin):
    NAME = "mistral"
    DISPLAY_NAME = "Mistral AI"
    DESCRIPTION = "Mistral AI — strong multilingual capabilities"
    DEFAULT_BASE_URL = "https://api.mistral.ai/v1"
    DEFAULT_MODEL = "mistral-large-latest"
    MODELS = ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest", "open-mistral-nemo", "codestral-latest"]
    API_KEY_NAME = "mistral_api_key"
