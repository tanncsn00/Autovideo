"""GPT-SoVITS voice cloning plugin — clone any voice from a 30-second sample"""

import os
import requests
from app.plugins.base import TTSPlugin, PluginMeta
from app.config.config import get_api_key, app
from loguru import logger


class GPTSoVITSPlugin(TTSPlugin):

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="gpt-sovits",
            display_name="GPT-SoVITS (Voice Clone)",
            version="1.0.0",
            description="Local voice cloning — clone any voice from a 30-second audio sample. Runs offline.",
            author="MoneyPrinterTurbo",
            plugin_type="tts",
            config_schema={
                "api_url": {
                    "type": "string",
                    "default": "http://127.0.0.1:9880",
                    "description": "GPT-SoVITS API server URL",
                },
                "reference_audio": {
                    "type": "string",
                    "description": "Path to reference audio file (30s sample of target voice)",
                },
                "reference_text": {
                    "type": "string",
                    "description": "Transcript of the reference audio",
                },
            },
            builtin=True,
        )

    def validate_config(self, config: dict) -> bool:
        return bool(config.get("api_url"))

    def is_available(self) -> bool:
        """Check if GPT-SoVITS server is running"""
        api_url = app.get("gpt_sovits_api_url", "http://127.0.0.1:9880")
        try:
            resp = requests.get(api_url, timeout=2)
            return resp.status_code == 200
        except Exception:
            return False

    async def synthesize(self, text, voice, rate=1.0, output_path=""):
        """Synthesize speech using GPT-SoVITS API.

        Args:
            text: Text to speak
            voice: Either a voice preset name or path to reference audio file
            rate: Speech rate (mapped to speed parameter)
            output_path: Where to save the audio
        """
        api_url = app.get("gpt_sovits_api_url", "http://127.0.0.1:9880")

        # Build request parameters
        params = {
            "text": text,
            "text_language": app.get("gpt_sovits_text_lang", "en"),
        }

        # Voice can be a reference audio path or preset name
        if voice and os.path.exists(voice):
            # Use provided reference audio
            params["refer_wav_path"] = voice
            ref_text = app.get("gpt_sovits_reference_text", "")
            if ref_text:
                params["prompt_text"] = ref_text
                params["prompt_language"] = app.get("gpt_sovits_prompt_lang", "en")
        elif voice:
            # Treat as a preset/model name
            params["refer_wav_path"] = app.get("gpt_sovits_reference_audio", "")
            params["prompt_text"] = app.get("gpt_sovits_reference_text", "")
            params["prompt_language"] = app.get("gpt_sovits_prompt_lang", "en")

        # Speed control
        if rate != 1.0:
            params["speed"] = rate

        # Call GPT-SoVITS API
        try:
            resp = requests.post(
                api_url,
                json=params,
                timeout=300,  # Voice synthesis can take time
                stream=True,
            )
            resp.raise_for_status()

            # Save audio
            with open(output_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"GPT-SoVITS synthesis complete: {output_path}")

        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                "Cannot connect to GPT-SoVITS server. "
                f"Make sure it's running at {api_url}. "
                "Start GPT-SoVITS: python api.py"
            )

        # GPT-SoVITS doesn't provide word-level timing
        return output_path, None

    def get_voices(self) -> list[dict]:
        """Return available voice presets.

        GPT-SoVITS voices are user-configured (reference audio files),
        not pre-defined. Return instructions for setup.
        """
        # Check if reference audio is configured
        ref_audio = app.get("gpt_sovits_reference_audio", "")
        voices = []

        if ref_audio and os.path.exists(ref_audio):
            voices.append({
                "id": ref_audio,
                "name": "Custom Voice (configured)",
                "language": app.get("gpt_sovits_text_lang", "en"),
                "gender": "Custom",
            })

        # Add instructions as a "voice"
        voices.append({
            "id": "setup-required",
            "name": "Setup: Provide 30s audio sample",
            "language": "any",
            "gender": "Any",
        })

        return voices

    def get_status(self) -> dict:
        """Get detailed GPT-SoVITS server status"""
        api_url = app.get("gpt_sovits_api_url", "http://127.0.0.1:9880")
        try:
            resp = requests.get(api_url, timeout=2)
            return {
                "server_running": True,
                "api_url": api_url,
                "reference_audio": app.get("gpt_sovits_reference_audio", ""),
                "has_reference": bool(app.get("gpt_sovits_reference_audio", "")),
            }
        except Exception:
            return {
                "server_running": False,
                "api_url": api_url,
                "message": "GPT-SoVITS server not running. Start with: python api.py",
            }
