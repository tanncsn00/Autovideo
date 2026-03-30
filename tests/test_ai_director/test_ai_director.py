import json
import pytest
from app.services.ai_director import AIDirector, DirectorSuggestion, DIRECTOR_PROMPT


class TestDirectorSuggestion:
    def test_dataclass(self):
        s = DirectorSuggestion(
            template_id="test", caption_style="hormozi", color_preset="cinematic",
            transition="FadeIn", bgm_mood="energetic", voice_rate=1.1,
            paragraph_number=2, titles={"youtube": "Title"}, hashtags={"youtube": ["ai"]},
            reasoning="test",
        )
        assert s.template_id == "test"
        assert s.voice_rate == 1.1

    def test_to_dict(self):
        s = DirectorSuggestion(
            template_id="t", caption_style="default", color_preset="none",
            transition="FadeIn", bgm_mood="calm", voice_rate=1.0,
            paragraph_number=1, titles={}, hashtags={}, reasoning="r",
        )
        d = s.to_dict()
        assert d["template_id"] == "t"
        assert d["bgm_mood"] == "calm"


class TestAIDirector:
    def test_instantiation(self):
        d = AIDirector()
        assert d is not None

    def test_parse_valid_json(self):
        d = AIDirector()
        response = json.dumps({
            "template_id": "tiktok-trending-facts",
            "caption_style": "hormozi",
            "color_preset": "cinematic",
            "transition": "ZoomIn",
            "bgm_mood": "energetic",
            "voice_rate": 1.15,
            "paragraph_number": 1,
            "titles": {"youtube": "AI Trends", "tiktok": "AI is changing everything"},
            "hashtags": {"youtube": ["ai", "tech"], "tiktok": ["ai", "viral"]},
            "reasoning": "Energetic topic suits TikTok format",
        })
        suggestion = d._parse_response(response)
        assert suggestion.template_id == "tiktok-trending-facts"
        assert suggestion.caption_style == "hormozi"
        assert suggestion.voice_rate == 1.15

    def test_parse_json_in_markdown(self):
        d = AIDirector()
        response = '```json\n{"template_id": "test", "caption_style": "default", "color_preset": "none", "transition": "FadeIn", "bgm_mood": "calm", "voice_rate": 1.0, "paragraph_number": 1, "titles": {}, "hashtags": {}, "reasoning": "ok"}\n```'
        suggestion = d._parse_response(response)
        assert suggestion.template_id == "test"

    def test_default_suggestion_tiktok(self):
        d = AIDirector()
        s = d._default_suggestion("AI Trends", "tiktok")
        assert s.template_id == "tiktok-trending-facts"
        assert s.caption_style == "hormozi"
        assert s.voice_rate == 1.1

    def test_default_suggestion_youtube(self):
        d = AIDirector()
        s = d._default_suggestion("Tutorial", "youtube")
        assert s.template_id == "youtube-tutorial"
        assert s.caption_style == "documentary"

    def test_default_suggestion_unknown_platform(self):
        d = AIDirector()
        s = d._default_suggestion("Topic", "linkedin")
        assert s.caption_style == "default"
        assert s.reasoning == "Default settings (AI Director unavailable)"

    def test_prompt_template(self):
        assert "{subject}" in DIRECTOR_PROMPT
        assert "{platform}" in DIRECTOR_PROMPT
        assert "{templates}" in DIRECTOR_PROMPT
