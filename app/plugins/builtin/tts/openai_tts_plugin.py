from app.plugins.base import TTSPlugin, PluginMeta
from app.config.config import get_api_key, app


class OpenAITTSPlugin(TTSPlugin):

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="openai-tts",
            display_name="OpenAI TTS",
            version="1.0.0",
            description="OpenAI text-to-speech with high quality voices",
            author="MoneyPrinterTurbo",
            plugin_type="tts",
            config_schema={
                "api_key": {"type": "string", "required": True},
                "model": {"type": "string", "default": "tts-1"},
                "response_format": {"type": "string", "default": "mp3"},
            },
            builtin=True,
        )

    def validate_config(self, config: dict) -> bool:
        return bool(config.get("api_key"))

    def is_available(self) -> bool:
        api_key = get_api_key("openai_api_key")
        return bool(api_key and api_key.strip())

    async def synthesize(self, text, voice, rate=1.0, output_path=""):
        from openai import OpenAI

        api_key = get_api_key("openai_api_key")
        base_url = get_api_key("openai_base_url") or app.get(
            "openai_base_url", "https://api.openai.com/v1"
        )
        model = app.get("openai_tts_model", "tts-1")

        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            speed=rate,
        )

        response.stream_to_file(output_path)

        # OpenAI TTS doesn't return word-level timing
        # Subtitle generation will fall back to Whisper
        return output_path, None

    def get_voices(self) -> list[dict]:
        return [
            {"id": "alloy", "name": "Alloy", "language": "en", "gender": "Neutral"},
            {"id": "ash", "name": "Ash", "language": "en", "gender": "Male"},
            {"id": "ballad", "name": "Ballad", "language": "en", "gender": "Male"},
            {"id": "coral", "name": "Coral", "language": "en", "gender": "Female"},
            {"id": "echo", "name": "Echo", "language": "en", "gender": "Male"},
            {"id": "fable", "name": "Fable", "language": "en", "gender": "Male"},
            {"id": "nova", "name": "Nova", "language": "en", "gender": "Female"},
            {"id": "onyx", "name": "Onyx", "language": "en", "gender": "Male"},
            {"id": "sage", "name": "Sage", "language": "en", "gender": "Female"},
            {"id": "shimmer", "name": "Shimmer", "language": "en", "gender": "Female"},
        ]
