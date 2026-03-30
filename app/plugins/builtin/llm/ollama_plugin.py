import requests
from app.plugins.builtin.llm.base_openai_compatible import OpenAICompatibleLLMPlugin
from app.config.config import app

class OllamaPlugin(OpenAICompatibleLLMPlugin):
    NAME = "ollama"
    DISPLAY_NAME = "Ollama (Local)"
    DESCRIPTION = "Run LLMs locally — Llama 3, Mistral, Phi. Fully offline."
    DEFAULT_BASE_URL = "http://localhost:11434/v1"
    DEFAULT_MODEL = "llama3.2"
    MODELS = ["llama3.2", "llama3.1", "mistral", "phi3", "gemma2", "qwen2.5", "deepseek-r1"]
    API_KEY_NAME = "ollama_api_key"

    def is_available(self) -> bool:
        base_url = app.get("ollama_base_url", "http://localhost:11434")
        try:
            return requests.get(f"{base_url}/api/tags", timeout=2).status_code == 200
        except Exception:
            return False

    async def generate_response(self, prompt, **kwargs):
        from app.config.config import get_api_key
        # Ollama doesn't need real API key
        from openai import OpenAI
        base_url = get_api_key("ollama_base_url") or app.get("ollama_base_url", self.DEFAULT_BASE_URL)
        if not base_url.endswith("/v1"):
            base_url = f"{base_url}/v1"
        client = OpenAI(api_key="ollama", base_url=base_url)
        response = client.chat.completions.create(
            model=app.get("ollama_model_name", self.DEFAULT_MODEL),
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
