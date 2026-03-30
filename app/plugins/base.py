from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel


class PluginMeta(BaseModel):
    """Plugin metadata"""
    name: str
    display_name: str
    version: str
    description: str
    author: str
    plugin_type: str  # "llm" | "tts" | "material" | "effect" | "music"
    config_schema: dict = {}
    builtin: bool = True


class PluginConfig(BaseModel):
    """Base config all plugins share"""
    enabled: bool = True
    priority: int = 0


class BasePlugin(ABC):
    """Base class all plugins must extend"""

    @abstractmethod
    def get_meta(self) -> PluginMeta:
        ...

    @abstractmethod
    def validate_config(self, config: dict) -> bool:
        ...

    @abstractmethod
    def is_available(self) -> bool:
        ...


class LLMPlugin(BasePlugin):
    """Interface for LLM provider plugins"""

    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> str:
        ...

    def get_models(self) -> list[str]:
        return []


class TTSPlugin(BasePlugin):
    """Interface for TTS provider plugins"""

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice: str,
        rate: float = 1.0,
        output_path: str = "",
    ) -> tuple[str, Any]:
        """Returns (audio_path, subtitle_data)"""
        ...

    @abstractmethod
    def get_voices(self) -> list[dict]:
        """Returns [{"id": "...", "name": "...", "language": "...", "gender": "..."}]"""
        ...


class MaterialPlugin(BasePlugin):
    """Interface for video/image material source plugins"""

    @abstractmethod
    async def search(
        self,
        query: str,
        aspect: str = "16:9",
        max_results: int = 10,
    ) -> list[dict]:
        ...

    @abstractmethod
    async def download(self, url: str, output_dir: str) -> str:
        ...


class EffectPlugin(BasePlugin):
    """Interface for video effect plugins"""

    @abstractmethod
    def get_transitions(self) -> list[str]:
        ...

    @abstractmethod
    def apply_transition(self, clip_a, clip_b, transition: str, duration: float = 1.0):
        ...


class MusicPlugin(BasePlugin):
    """Interface for background music source plugins"""

    @abstractmethod
    async def search(self, mood: str, duration: float) -> list[dict]:
        ...

    @abstractmethod
    async def download(self, url: str, output_dir: str) -> str:
        ...


class PublisherPlugin(BasePlugin):
    """Interface for video publishing platform plugins"""

    @abstractmethod
    async def authenticate(self, credentials: dict) -> bool:
        """Authenticate with the platform. Returns True if successful."""
        ...

    @abstractmethod
    async def publish(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: list[str] = None,
        thumbnail_path: str = None,
        schedule_time: str = None,
        **kwargs,
    ) -> dict:
        """Publish a video. Returns platform-specific response (e.g., video URL, ID)."""
        ...

    @abstractmethod
    def get_supported_features(self) -> list[str]:
        """Return list of supported features: ['upload', 'schedule', 'thumbnail', 'tags', 'analytics']"""
        ...
