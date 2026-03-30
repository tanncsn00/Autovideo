import os
import requests
from app.plugins.base import TTSPlugin, PluginMeta
from app.config.config import get_api_key, app


class ElevenLabsPlugin(TTSPlugin):

    API_BASE = "https://api.elevenlabs.io/v1"

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="elevenlabs",
            display_name="ElevenLabs",
            version="1.0.0",
            description="Most realistic AI voices with voice cloning support",
            author="MoneyPrinterTurbo",
            plugin_type="tts",
            config_schema={
                "api_key": {"type": "string", "required": True},
                "model_id": {"type": "string", "default": "eleven_multilingual_v2"},
                "stability": {"type": "number", "default": 0.5},
                "similarity_boost": {"type": "number", "default": 0.75},
            },
            builtin=True,
        )

    def validate_config(self, config: dict) -> bool:
        return bool(config.get("api_key"))

    def is_available(self) -> bool:
        api_key = get_api_key("elevenlabs_api_key")
        return bool(api_key and api_key.strip())

    def _get_headers(self) -> dict:
        api_key = get_api_key("elevenlabs_api_key")
        return {
            "xi-api-key": api_key,
            "Content-Type": "application/json",
        }

    async def synthesize(self, text, voice, rate=1.0, output_path=""):
        api_key = get_api_key("elevenlabs_api_key")
        model_id = app.get("elevenlabs_model_id", "eleven_multilingual_v2")
        stability = float(app.get("elevenlabs_stability", 0.5))
        similarity = float(app.get("elevenlabs_similarity_boost", 0.75))

        url = f"{self.API_BASE}/text-to-speech/{voice}"
        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity,
                "speed": rate,
            },
        }

        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(resp.content)

        # ElevenLabs doesn't return word-level timing
        # Subtitle generation will fall back to Whisper
        return output_path, None

    def get_voices(self) -> list[dict]:
        try:
            resp = requests.get(
                f"{self.API_BASE}/voices",
                headers=self._get_headers(),
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            return [
                {
                    "id": v["voice_id"],
                    "name": v.get("name", "Unknown"),
                    "language": ",".join(v.get("labels", {}).values()),
                    "gender": v.get("labels", {}).get("gender", "unknown"),
                }
                for v in data.get("voices", [])
            ]
        except Exception:
            # Return well-known default voices if API call fails
            return [
                {"id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel", "language": "en", "gender": "Female"},
                {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella", "language": "en", "gender": "Female"},
                {"id": "ErXwobaYiN019PkySvjV", "name": "Antoni", "language": "en", "gender": "Male"},
                {"id": "MF3mGyEYCl7XYWbV9V6O", "name": "Elli", "language": "en", "gender": "Female"},
                {"id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh", "language": "en", "gender": "Male"},
                {"id": "VR6AewLTigWG4xSOukaG", "name": "Arnold", "language": "en", "gender": "Male"},
                {"id": "pNInz6obpgDQGcFmaJgB", "name": "Adam", "language": "en", "gender": "Male"},
                {"id": "yoZ06aMxZJJ28mfd3POQ", "name": "Sam", "language": "en", "gender": "Male"},
            ]
