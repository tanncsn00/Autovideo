from app.plugins.builtin.llm.base_openai_compatible import OpenAICompatibleLLMPlugin

class QwenPlugin(OpenAICompatibleLLMPlugin):
    NAME = "qwen"
    DISPLAY_NAME = "Qwen (Alibaba)"
    DESCRIPTION = "Alibaba Qwen — strong multilingual and Chinese support"
    DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    DEFAULT_MODEL = "qwen-plus"
    MODELS = ["qwen-plus", "qwen-turbo", "qwen-max", "qwen-long"]
    API_KEY_NAME = "qwen_api_key"
