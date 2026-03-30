"""VBee AIVoice TTS Plugin — 200+ Vietnamese voices, very natural"""

import os
import time
import requests
from app.plugins.base import TTSPlugin, PluginMeta
from app.config.config import get_api_key, app
from loguru import logger


class VBeePlugin(TTSPlugin):

    API_URL = "https://vbee.vn/api/v1/tts"

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="vbee",
            display_name="VBee AIVoice (Vietnamese)",
            version="1.0.0",
            description="200+ Vietnamese voices, 90% human-like. Best Vietnamese TTS. 3000 chars/day free.",
            author="MoneyPrinterTurbo",
            plugin_type="tts",
            config_schema={
                "api_key": {"type": "string", "required": True},
                "app_id": {"type": "string", "required": True},
            },
            builtin=True,
        )

    def validate_config(self, config: dict) -> bool:
        return bool(config.get("api_key") and config.get("app_id"))

    def is_available(self) -> bool:
        api_key = get_api_key("vbee_api_key")
        return bool(api_key and api_key.strip())

    async def synthesize(self, text, voice, rate=1.0, output_path=""):
        api_key = get_api_key("vbee_api_key")
        app_id = get_api_key("vbee_app_id") or app.get("vbee_app_id", "")

        if not api_key:
            raise ValueError("VBee API key not set")

        # Parse voice: "vbee:hn_female_ngochuyen_news_48k-Female" → "hn_female_ngochuyen_news_48k"
        voice_id = voice
        if ":" in voice_id:
            voice_id = voice_id.split(":")[-1]
        if "-" in voice_id and voice_id.split("-")[-1] in ("Male", "Female"):
            voice_id = voice_id.rsplit("-", 1)[0]

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # Speed: 0.5x - 2.0x
        payload = {
            "app_id": app_id,
            "input_text": text,
            "voice_code": voice_id,
            "audio_type": "mp3",
            "bitrate": 128000,
            "speed_rate": str(rate),
        }

        # Step 1: Create TTS request
        resp = requests.post(
            self.API_URL,
            headers=headers,
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()

        request_id = result.get("request_id") or result.get("id")
        if not request_id:
            # Some VBee API versions return audio URL directly
            audio_url = result.get("audio_url") or result.get("url")
            if audio_url:
                audio_resp = requests.get(audio_url, timeout=60)
                audio_resp.raise_for_status()
                with open(output_path, "wb") as f:
                    f.write(audio_resp.content)
                return output_path, None
            raise RuntimeError(f"VBee returned unexpected response: {result}")

        # Step 2: Poll for result
        status_url = f"{self.API_URL}/{request_id}"
        for _ in range(60):
            time.sleep(1)
            try:
                status_resp = requests.get(status_url, headers=headers, timeout=10)
                status_data = status_resp.json()
                status = status_data.get("status", "")

                if status in ("SUCCESS", "success", "done"):
                    audio_url = status_data.get("audio_url") or status_data.get("url")
                    if audio_url:
                        audio_resp = requests.get(audio_url, timeout=60)
                        audio_resp.raise_for_status()
                        with open(output_path, "wb") as f:
                            f.write(audio_resp.content)
                        logger.info(f"VBee TTS done: {output_path}")
                        return output_path, None

                if status in ("FAILED", "failed", "error"):
                    raise RuntimeError(f"VBee TTS failed: {status_data}")

            except requests.exceptions.RequestException:
                pass

        raise TimeoutError("VBee audio generation timed out")

    def get_voices(self) -> list[dict]:
        """Popular VBee Vietnamese voices"""
        return [
            # Northern Female
            {"id": "vbee:hn_female_ngochuyen_news_48k-Female", "name": "Ngoc Huyen (Nu Bac - Tin tuc)", "language": "vi-VN", "gender": "Female"},
            {"id": "vbee:hn_female_maiphuong_news_48k-Female", "name": "Mai Phuong (Nu Bac - Tin tuc)", "language": "vi-VN", "gender": "Female"},
            {"id": "vbee:hn_female_thutrang_phrase_48k-Female", "name": "Thu Trang (Nu Bac - Doc truyen)", "language": "vi-VN", "gender": "Female"},
            {"id": "vbee:hn_female_thuha_phrase_48k-Female", "name": "Thu Ha (Nu Bac - Doc truyen)", "language": "vi-VN", "gender": "Female"},
            # Northern Male
            {"id": "vbee:hn_male_manhdung_news_48k-Male", "name": "Manh Dung (Nam Bac - Tin tuc)", "language": "vi-VN", "gender": "Male"},
            {"id": "vbee:hn_male_thanhlong_phrase_48k-Male", "name": "Thanh Long (Nam Bac - Doc truyen)", "language": "vi-VN", "gender": "Male"},
            # Southern Female
            {"id": "vbee:sg_female_thaotrinh_news_48k-Female", "name": "Thao Trinh (Nu Nam - Tin tuc)", "language": "vi-VN", "gender": "Female"},
            {"id": "vbee:sg_female_thanhtam_phrase_48k-Female", "name": "Thanh Tam (Nu Nam - Doc truyen)", "language": "vi-VN", "gender": "Female"},
            # Southern Male
            {"id": "vbee:sg_male_minhhoang_news_48k-Male", "name": "Minh Hoang (Nam Nam - Tin tuc)", "language": "vi-VN", "gender": "Male"},
            {"id": "vbee:sg_male_giabao_phrase_48k-Male", "name": "Gia Bao (Nam Nam - Doc truyen)", "language": "vi-VN", "gender": "Male"},
            # Central
            {"id": "vbee:hue_female_huonggiang_phrase_48k-Female", "name": "Huong Giang (Nu Trung - Doc truyen)", "language": "vi-VN", "gender": "Female"},
        ]
