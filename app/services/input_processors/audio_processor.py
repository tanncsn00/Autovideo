"""Audio to Video — transcribe audio and generate video from transcript"""

import os
from dataclasses import dataclass
from loguru import logger


@dataclass
class TranscribedAudio:
    text: str
    language: str
    duration: float
    segments: list[dict]  # [{start, end, text}]


class AudioProcessor:
    """Process audio files into video-ready content"""

    async def transcribe(self, audio_path: str, language: str = None) -> TranscribedAudio:
        """Transcribe audio file using Whisper"""
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            from faster_whisper import WhisperModel
            from app.config import config

            model_size = config.whisper.get("model_size", "large-v3")
            device = config.whisper.get("device", "cpu")
            compute_type = config.whisper.get("compute_type", "int8")

            model = WhisperModel(model_size, device=device, compute_type=compute_type)
            segments_iter, info = model.transcribe(
                audio_path,
                language=language,
                beam_size=5,
                vad_filter=True,
            )

            segments = []
            full_text = []
            for segment in segments_iter:
                segments.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip(),
                })
                full_text.append(segment.text.strip())

            return TranscribedAudio(
                text=" ".join(full_text),
                language=info.language or language or "en",
                duration=info.duration,
                segments=segments,
            )

        except ImportError:
            raise ImportError("faster-whisper is required. Install: pip install faster-whisper")

    async def prepare_video_params(self, audio_path: str, template_id: str = None) -> dict:
        """Transcribe audio and prepare VideoParams"""
        result = await self.transcribe(audio_path)

        params = {
            "video_script": result.text[:3000],
            "video_subject": result.text[:100],
            "video_language": result.language,
            "custom_audio_file": audio_path,
        }

        if template_id:
            from app.services.template import TemplateManager
            mgr = TemplateManager()
            try:
                template_params = mgr.apply_template(template_id)
                template_params.update(params)
                params = template_params
            except ValueError:
                pass

        return params


audio_processor = AudioProcessor()
