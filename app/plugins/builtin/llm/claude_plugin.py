from app.plugins.base import LLMPlugin, PluginMeta
from app.config.config import get_api_key, app


class ClaudePlugin(LLMPlugin):

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="claude",
            display_name="Claude (Anthropic)",
            version="1.0.0",
            description="Anthropic Claude models — best quality scripts, large context window",
            author="MoneyPrinterTurbo",
            plugin_type="llm",
            config_schema={
                "api_key": {"type": "string", "required": True},
                "model_name": {"type": "string", "default": "claude-sonnet-4-20250514"},
                "base_url": {"type": "string", "default": "https://api.anthropic.com"},
                "max_tokens": {"type": "integer", "default": 4096},
            },
            builtin=True,
        )

    def validate_config(self, config: dict) -> bool:
        return bool(config.get("api_key"))

    def is_available(self) -> bool:
        api_key = get_api_key("claude_api_key")
        return bool(api_key and api_key.strip())

    async def generate_response(self, prompt: str, **kwargs) -> str:
        import anthropic

        api_key = get_api_key("claude_api_key")
        base_url = get_api_key("claude_base_url") or app.get("claude_base_url", "https://api.anthropic.com")
        model = app.get("claude_model_name", "claude-sonnet-4-20250514")
        max_tokens = int(app.get("claude_max_tokens", 4096))

        client = anthropic.Anthropic(api_key=api_key, base_url=base_url)
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        # Extract text from response
        text_parts = [block.text for block in message.content if hasattr(block, "text")]
        return "\n".join(text_parts)

    def get_models(self) -> list[str]:
        return [
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514",
            "claude-haiku-4-20250514",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
        ]
