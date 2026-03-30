"""AI Director — automatically optimizes video settings using LLM analysis"""

import json
from dataclasses import dataclass
from typing import Optional
from loguru import logger


@dataclass
class DirectorSuggestion:
    """AI Director's recommendations for a video"""
    template_id: str
    caption_style: str
    color_preset: str
    transition: str
    bgm_mood: str  # energetic, calm, dramatic, upbeat, professional
    voice_rate: float
    paragraph_number: int
    titles: dict  # {platform: title}
    hashtags: dict  # {platform: [hashtags]}
    reasoning: str

    def to_dict(self) -> dict:
        return {
            "template_id": self.template_id,
            "caption_style": self.caption_style,
            "color_preset": self.color_preset,
            "transition": self.transition,
            "bgm_mood": self.bgm_mood,
            "voice_rate": self.voice_rate,
            "paragraph_number": self.paragraph_number,
            "titles": self.titles,
            "hashtags": self.hashtags,
            "reasoning": self.reasoning,
        }


DIRECTOR_PROMPT = """You are an AI Video Director. Analyze the following video content and suggest optimal settings.

CONTENT:
Subject: {subject}
Script: {script}
Target Platform: {platform}
Language: {language}

AVAILABLE TEMPLATES:
{templates}

AVAILABLE OPTIONS:
- Caption styles: default, hormozi, documentary, tiktok-viral, corporate
- Color presets: none, cinematic, warm, cool, vintage, noir, vibrant, muted, high_contrast
- Transitions: FadeIn, FadeOut, SlideIn, SlideOut, WipeLeft, WipeRight, ZoomIn, ZoomOut, Flash, BlackFade
- BGM moods: energetic, calm, dramatic, upbeat, professional, ambient, inspiring

Respond in JSON format ONLY (no markdown, no explanation outside JSON):
{{
    "template_id": "best matching template ID or empty string",
    "caption_style": "best caption style",
    "color_preset": "best color preset",
    "transition": "best transition",
    "bgm_mood": "best BGM mood",
    "voice_rate": 1.0,
    "paragraph_number": 1,
    "titles": {{
        "youtube": "YouTube title (max 100 chars)",
        "tiktok": "TikTok caption (max 150 chars)",
        "instagram": "Instagram caption with hashtags"
    }},
    "hashtags": {{
        "youtube": ["tag1", "tag2", "tag3", "tag4", "tag5"],
        "tiktok": ["tag1", "tag2", "tag3"],
        "instagram": ["tag1", "tag2", "tag3", "tag4", "tag5"]
    }},
    "reasoning": "Brief explanation of choices (1-2 sentences)"
}}"""


class AIDirector:
    """Uses LLM to auto-optimize video production settings"""

    async def analyze(
        self,
        subject: str,
        script: str = "",
        platform: str = "general",
        language: str = "en",
    ) -> DirectorSuggestion:
        """Analyze content and suggest optimal video settings"""
        from app.services.template import TemplateManager

        # Get available templates
        template_mgr = TemplateManager()
        templates = template_mgr.list_templates()
        template_list = "\n".join(
            f"- {t['id']}: {t['name']} ({t['category']}, {t['video_aspect']})"
            for t in templates[:20]
        )

        # Build prompt
        prompt = DIRECTOR_PROMPT.format(
            subject=subject,
            script=script[:2000] if script else "(no script yet — will be generated)",
            platform=platform,
            language=language,
            templates=template_list or "No templates available",
        )

        # Call LLM
        try:
            from app.services.llm import generate_script
            from app.plugins import plugin_manager
            from app.plugins.utils import run_async

            llm_plugin = plugin_manager.get_active_plugin("llm")
            if llm_plugin and llm_plugin.is_available():
                response = run_async(llm_plugin.generate_response(prompt))
            else:
                # Fallback to legacy LLM
                from app.services.llm import _generate_response
                response = _generate_response(prompt)

            # Parse JSON response
            suggestion = self._parse_response(response)
            return suggestion

        except Exception as e:
            logger.warning(f"AI Director failed, using defaults: {e}")
            return self._default_suggestion(subject, platform)

    def _parse_response(self, response: str) -> DirectorSuggestion:
        """Parse LLM JSON response into DirectorSuggestion"""
        # Extract JSON from response (handle markdown code blocks)
        response = response.strip()
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(lines[1:-1])
        if response.startswith("```json"):
            response = response[7:]
        if response.endswith("```"):
            response = response[:-3]

        try:
            data = json.loads(response.strip())
        except json.JSONDecodeError:
            # Try to find JSON in response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError(f"Could not parse AI Director response as JSON")

        return DirectorSuggestion(
            template_id=data.get("template_id", ""),
            caption_style=data.get("caption_style", "default"),
            color_preset=data.get("color_preset", "none"),
            transition=data.get("transition", "FadeIn"),
            bgm_mood=data.get("bgm_mood", "ambient"),
            voice_rate=float(data.get("voice_rate", 1.0)),
            paragraph_number=int(data.get("paragraph_number", 1)),
            titles=data.get("titles", {}),
            hashtags=data.get("hashtags", {}),
            reasoning=data.get("reasoning", ""),
        )

    def _default_suggestion(self, subject: str, platform: str) -> DirectorSuggestion:
        """Return sensible defaults when LLM is unavailable"""
        platform_defaults = {
            "tiktok": {
                "template_id": "tiktok-trending-facts",
                "caption_style": "hormozi",
                "transition": "FadeIn",
                "voice_rate": 1.1,
            },
            "youtube": {
                "template_id": "youtube-tutorial",
                "caption_style": "documentary",
                "transition": "FadeIn",
                "voice_rate": 1.0,
            },
            "instagram": {
                "template_id": "instagram-lifestyle",
                "caption_style": "tiktok-viral",
                "transition": "FadeIn",
                "voice_rate": 1.0,
            },
        }

        defaults = platform_defaults.get(platform, {
            "template_id": "",
            "caption_style": "default",
            "transition": "FadeIn",
            "voice_rate": 1.0,
        })

        return DirectorSuggestion(
            template_id=defaults.get("template_id", ""),
            caption_style=defaults.get("caption_style", "default"),
            color_preset="none",
            transition=defaults.get("transition", "FadeIn"),
            bgm_mood="ambient",
            voice_rate=defaults.get("voice_rate", 1.0),
            paragraph_number=1,
            titles={platform: subject[:100] if subject else "Untitled"},
            hashtags={platform: []},
            reasoning="Default settings (AI Director unavailable)",
        )

    async def generate_titles(self, subject: str, script: str = "", platforms: list[str] = None) -> dict:
        """Generate platform-optimized titles"""
        if not platforms:
            platforms = ["youtube", "tiktok", "instagram"]

        suggestion = await self.analyze(subject, script, platforms[0])
        return suggestion.titles

    async def generate_hashtags(self, subject: str, script: str = "", platforms: list[str] = None) -> dict:
        """Generate platform-optimized hashtags"""
        if not platforms:
            platforms = ["youtube", "tiktok", "instagram"]

        suggestion = await self.analyze(subject, script, platforms[0])
        return suggestion.hashtags


# Global instance
ai_director = AIDirector()
