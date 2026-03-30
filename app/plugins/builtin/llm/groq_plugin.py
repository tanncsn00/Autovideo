from app.plugins.builtin.llm.base_openai_compatible import OpenAICompatibleLLMPlugin

class GroqPlugin(OpenAICompatibleLLMPlugin):
    NAME = "groq"
    DISPLAY_NAME = "Groq"
    DESCRIPTION = "Groq LPU — fastest LLM inference (500+ tokens/s)"
    DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"
    DEFAULT_MODEL = "llama-3.3-70b-versatile"
    MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"]
    API_KEY_NAME = "groq_api_key"
