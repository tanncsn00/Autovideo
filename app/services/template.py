import json
import os
from pathlib import Path
from typing import Optional
from loguru import logger
from pydantic import BaseModel


class TemplateConfig(BaseModel):
    """Template definition schema"""
    id: str
    name: str
    description: str
    category: str  # tiktok, youtube-shorts, instagram-reels, corporate, education
    platform: str  # tiktok, youtube, instagram, general
    thumbnail: str = ""

    # Video settings
    video_aspect: str = "9:16"
    video_concat_mode: str = "random"
    video_transition_mode: str = "FadeIn"
    video_clip_duration: int = 5
    video_count: int = 1

    # Audio settings
    voice_name: str = "en-US-AriaNeural-Female"
    voice_rate: float = 1.0
    bgm_volume: float = 0.2

    # Subtitle settings
    subtitle_enabled: bool = True
    subtitle_position: str = "bottom"
    font_name: str = ""
    font_size: int = 60
    text_fore_color: str = "#FFFFFF"
    stroke_color: str = "#000000"
    stroke_width: float = 1.5
    text_background_color: str = "transparent"

    # Caption style
    caption_style: str = "default"  # default, hormozi, documentary, tiktok-viral, corporate

    # Video filters
    color_preset: str = "none"  # none, cinematic, warm, cool, vintage, noir

    # Pacing
    paragraph_number: int = 1
    video_language: str = "en"


class TemplateManager:
    """Manages video templates — load, list, apply"""

    def __init__(self, templates_dir: str = None):
        if templates_dir:
            self._templates_dir = Path(templates_dir)
        else:
            self._templates_dir = Path(__file__).parent.parent.parent / "templates"
        self._templates: dict[str, TemplateConfig] = {}
        self._load_templates()

    def _load_templates(self):
        """Scan templates directory and load all JSON templates"""
        if not self._templates_dir.exists():
            logger.warning(f"Templates directory not found: {self._templates_dir}")
            return

        for category_dir in self._templates_dir.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith("_"):
                continue
            for template_file in category_dir.glob("*.json"):
                try:
                    with open(template_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    template = TemplateConfig(**data)
                    self._templates[template.id] = template
                    logger.debug(f"Loaded template: {template.name} ({template.id})")
                except Exception as e:
                    logger.error(f"Failed to load template {template_file}: {e}")

    def list_templates(self, category: str = None, platform: str = None) -> list[dict]:
        """List all templates, optionally filtered"""
        results = []
        for t in self._templates.values():
            if category and t.category != category:
                continue
            if platform and t.platform != platform:
                continue
            results.append(t.model_dump())
        return results

    def get_template(self, template_id: str) -> Optional[TemplateConfig]:
        """Get a specific template by ID"""
        return self._templates.get(template_id)

    def apply_template(self, template_id: str, overrides: dict = None) -> dict:
        """Apply a template, returning VideoParams-compatible dict with optional overrides"""
        template = self._templates.get(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")

        params = {
            "video_aspect": template.video_aspect,
            "video_concat_mode": template.video_concat_mode,
            "video_transition_mode": template.video_transition_mode,
            "video_clip_duration": template.video_clip_duration,
            "video_count": template.video_count,
            "voice_name": template.voice_name,
            "voice_rate": template.voice_rate,
            "bgm_volume": template.bgm_volume,
            "subtitle_enabled": template.subtitle_enabled,
            "subtitle_position": template.subtitle_position,
            "font_name": template.font_name,
            "font_size": template.font_size,
            "text_fore_color": template.text_fore_color,
            "stroke_color": template.stroke_color,
            "stroke_width": template.stroke_width,
            "paragraph_number": template.paragraph_number,
            "video_language": template.video_language,
        }

        # Apply overrides (user can customize on top of template)
        if overrides:
            params.update(overrides)

        return params

    def get_categories(self) -> list[str]:
        """Get all available categories"""
        return sorted(set(t.category for t in self._templates.values()))

    def save_custom_template(self, template: TemplateConfig) -> str:
        """Save a custom template"""
        custom_dir = self._templates_dir / "custom"
        custom_dir.mkdir(parents=True, exist_ok=True)
        filepath = custom_dir / f"{template.id}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(template.model_dump(), f, indent=2, ensure_ascii=False)
        self._templates[template.id] = template
        return str(filepath)
