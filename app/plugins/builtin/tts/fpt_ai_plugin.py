"""FPT.AI TTS Plugin — Vietnamese natural voices (banmai, thuminh, leminh, etc.)"""

import os
import time
import requests
from app.plugins.base import TTSPlugin, PluginMeta
from app.config.config import get_api_key
from loguru import logger


class FPTAIPlugin(TTSPlugin):

    API_URL = "https://api.fpt.ai/hmi/tts/v5"

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="fpt-ai",
            display_name="FPT.AI (Vietnamese)",
            version="1.0.0",
            description="Vietnamese TTS with natural voices — banmai, thuminh, leminh. 100K chars/month free.",
            author="MoneyPrinterTurbo",
            plugin_type="tts",
            config_schema={
                "api_key": {"type": "string", "required": True},
                "voice": {"type": "string", "default": "banmai"},
                "speed": {"type": "string", "default": "0"},
            },
            builtin=True,
        )

    def validate_config(self, config: dict) -> bool:
        return bool(config.get("api_key"))

    def is_available(self) -> bool:
        api_key = get_api_key("fpt_ai_api_key")
        return bool(api_key and api_key.strip())

    async def synthesize(self, text, voice, rate=1.0, output_path=""):
        api_key = get_api_key("fpt_ai_api_key")
        if not api_key:
            raise ValueError("FPT.AI API key not set")

        # Map voice name: "fpt-ai:banmai-Female" → "banmai"
        voice_id = voice
        if ":" in voice_id:
            voice_id = voice_id.split(":")[-1]
        if "-" in voice_id and voice_id.split("-")[-1] in ("Male", "Female"):
            voice_id = voice_id.rsplit("-", 1)[0]

        # Map rate to FPT speed: -3 (slow) to 3 (fast), 0 = normal
        speed = str(int((rate - 1.0) * 3))

        headers = {
            "api_key": api_key,
            "voice": voice_id,
            "speed": speed,
            "format": "mp3",
        }

        # FPT.AI is async — returns URL to download audio
        resp = requests.post(
            self.API_URL,
            headers=headers,
            data=text.encode("utf-8"),
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()

        if result.get("error"):
            raise RuntimeError(f"FPT.AI error: {result.get('message', result.get('error'))}")

        audio_url = result.get("async")
        if not audio_url:
            raise RuntimeError(f"FPT.AI returned no audio URL: {result}")

        # Poll until audio is ready (usually 2-10 seconds)
        for _ in range(30):
            time.sleep(1)
            try:
                audio_resp = requests.get(audio_url, timeout=15)
                if audio_resp.status_code == 200 and len(audio_resp.content) > 1000:
                    with open(output_path, "wb") as f:
                        f.write(audio_resp.content)
                    logger.info(f"FPT.AI TTS done: {output_path} ({len(audio_resp.content)} bytes)")
                    return output_path, None
            except Exception:
                pass

        raise TimeoutError("FPT.AI audio generation timed out")

    def get_voices(self) -> list[dict]:
        return [
            {"id": "fpt-ai:banmai-Female", "name": "Ban Mai (Nu Bac)", "language": "vi-VN", "gender": "Female"},
            {"id": "fpt-ai:thuminh-Female", "name": "Thu Minh (Nu Bac)", "language": "vi-VN", "gender": "Female"},
            {"id": "fpt-ai:leminh-Male", "name": "Le Minh (Nam Bac)", "language": "vi-VN", "gender": "Male"},
            {"id": "fpt-ai:myan-Female", "name": "My An (Nu Trung)", "language": "vi-VN", "gender": "Female"},
            {"id": "fpt-ai:giahuy-Male", "name": "Gia Huy (Nam Trung)", "language": "vi-VN", "gender": "Male"},
            {"id": "fpt-ai:lannhi-Female", "name": "Lan Nhi (Nu Nam)", "language": "vi-VN", "gender": "Female"},
            {"id": "fpt-ai:linhsan-Female", "name": "Linh San (Nu Nam)", "language": "vi-VN", "gender": "Female"},
        ]
