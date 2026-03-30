import shutil
import subprocess

from app.plugins.base import TTSPlugin, PluginMeta


class PiperPlugin(TTSPlugin):

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="piper",
            display_name="Piper TTS (Offline)",
            version="1.0.0",
            description="Fast offline TTS — 30+ languages, runs locally without internet",
            author="MoneyPrinterTurbo",
            plugin_type="tts",
            config_schema={
                "model_path": {
                    "type": "string",
                    "description": "Path to .onnx voice model file",
                },
                "data_dir": {
                    "type": "string",
                    "description": "Directory for downloaded models",
                },
            },
            builtin=True,
        )

    def validate_config(self, config: dict) -> bool:
        return True  # Piper can work with default model

    def is_available(self) -> bool:
        """Check if piper-tts CLI or Python package is installed."""
        if shutil.which("piper"):
            return True
        try:
            import piper  # noqa: F401

            return True
        except ImportError:
            return False

    async def synthesize(self, text, voice, rate=1.0, output_path=""):
        """Synthesize speech using piper CLI or Python API.

        Args:
            text: The text to synthesize.
            voice: Path to a .onnx model file, or a model name like
                ``en_US-amy-medium``.
            rate: Speech rate multiplier (1.0 = normal).
            output_path: Destination WAV file path.

        Returns:
            Tuple of (audio_path, subtitle_data).  subtitle_data is None
            because Piper does not provide word-level timing; subtitle
            generation should fall back to Whisper or another aligner.
        """
        piper_path = shutil.which("piper")

        if piper_path:
            cmd = [
                piper_path,
                "--model",
                voice,
                "--output_file",
                output_path,
            ]
            if rate != 1.0:
                # Piper uses --length-scale which is the inverse of rate
                length_scale = 1.0 / rate
                cmd.extend(["--length-scale", str(length_scale)])

            proc = subprocess.run(
                cmd,
                input=text,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if proc.returncode != 0:
                raise RuntimeError(f"Piper TTS failed: {proc.stderr}")
        else:
            # Fall back to the Python API
            try:
                from piper import PiperVoice
            except ImportError:
                raise RuntimeError(
                    "Piper TTS is not installed. Install with:\n"
                    "  pip install piper-tts\n"
                    "Then download a voice model from:\n"
                    "  https://github.com/rhasspy/piper/releases"
                )

            piper_voice = PiperVoice.load(voice)
            synthesize_kwargs = {}
            if rate != 1.0:
                synthesize_kwargs["length_scale"] = 1.0 / rate

            import wave

            with wave.open(output_path, "wb") as wav_file:
                piper_voice.synthesize(text, wav_file, **synthesize_kwargs)

        return output_path, None

    def get_voices(self) -> list[dict]:
        """Return commonly used Piper voice models.

        Each ``id`` corresponds to a downloadable model name from the Piper
        releases page.  The user must download the ``.onnx`` and ``.onnx.json``
        files for the chosen voice before using it.
        """
        return [
            {"id": "en_US-amy-medium", "name": "Amy (US English)", "language": "en-US", "gender": "Female"},
            {"id": "en_US-joe-medium", "name": "Joe (US English)", "language": "en-US", "gender": "Male"},
            {"id": "en_US-lessac-medium", "name": "Lessac (US English)", "language": "en-US", "gender": "Female"},
            {"id": "en_GB-alba-medium", "name": "Alba (British English)", "language": "en-GB", "gender": "Female"},
            {"id": "de_DE-thorsten-medium", "name": "Thorsten (German)", "language": "de-DE", "gender": "Male"},
            {"id": "fr_FR-siwis-medium", "name": "Siwis (French)", "language": "fr-FR", "gender": "Female"},
            {"id": "es_ES-mls_9972-medium", "name": "MLS (Spanish)", "language": "es-ES", "gender": "Male"},
            {"id": "zh_CN-huayan-medium", "name": "Huayan (Chinese)", "language": "zh-CN", "gender": "Female"},
            {"id": "ja_JP-kokoro-medium", "name": "Kokoro (Japanese)", "language": "ja-JP", "gender": "Female"},
            {"id": "vi_VN-25hours-medium", "name": "25hours (Vietnamese)", "language": "vi-VN", "gender": "Female"},
            {"id": "ko_KR-kss-medium", "name": "KSS (Korean)", "language": "ko-KR", "gender": "Female"},
            {"id": "pt_BR-faber-medium", "name": "Faber (Portuguese)", "language": "pt-BR", "gender": "Male"},
            {"id": "ru_RU-irina-medium", "name": "Irina (Russian)", "language": "ru-RU", "gender": "Female"},
        ]
