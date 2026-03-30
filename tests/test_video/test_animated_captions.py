import pytest
import tempfile
import os
from app.services.animated_captions import (
    parse_srt_to_segments,
    get_caption_style,
    list_caption_styles,
    CaptionWord,
    CaptionSegment,
    CAPTION_STYLES,
)


@pytest.fixture
def sample_srt(tmp_path):
    srt_content = """1
00:00:01,000 --> 00:00:03,000
Hello world this is a test

2
00:00:03,500 --> 00:00:06,000
Second subtitle segment here
"""
    srt_file = tmp_path / "test.srt"
    srt_file.write_text(srt_content)
    return str(srt_file)


class TestSRTParsing:
    def test_parse_segments(self, sample_srt):
        segments = parse_srt_to_segments(sample_srt)
        assert len(segments) == 2

    def test_segment_timing(self, sample_srt):
        segments = parse_srt_to_segments(sample_srt)
        assert segments[0].start == 1.0
        assert segments[0].end == 3.0
        assert segments[1].start == 3.5
        assert segments[1].end == 6.0

    def test_word_splitting(self, sample_srt):
        segments = parse_srt_to_segments(sample_srt)
        assert len(segments[0].words) == 6  # "Hello world this is a test"
        assert segments[0].words[0].text == "Hello"

    def test_word_timing_distribution(self, sample_srt):
        segments = parse_srt_to_segments(sample_srt)
        words = segments[0].words
        # 6 words in 2 seconds = ~0.333s per word
        assert abs(words[0].end - words[0].start - (2.0 / 6)) < 0.01

    def test_full_text(self, sample_srt):
        segments = parse_srt_to_segments(sample_srt)
        assert segments[0].full_text == "Hello world this is a test"

    def test_empty_file(self, tmp_path):
        empty = tmp_path / "empty.srt"
        empty.write_text("")
        segments = parse_srt_to_segments(str(empty))
        assert segments == []


class TestCaptionStyles:
    def test_all_styles_exist(self):
        styles = list_caption_styles()
        assert "default" in styles
        assert "hormozi" in styles
        assert "documentary" in styles
        assert "tiktok-viral" in styles
        assert "corporate" in styles

    def test_style_has_required_keys(self):
        for name in list_caption_styles():
            style = get_caption_style(name)
            assert "font_size" in style
            assert "font_color" in style
            assert "highlight_color" in style
            assert "position" in style

    def test_unknown_style_returns_default(self):
        style = get_caption_style("nonexistent")
        default = get_caption_style("default")
        assert style == default

    def test_hormozi_style(self):
        style = get_caption_style("hormozi")
        assert style["font_size"] == 80
        assert style["position"] == "center"
        assert style["highlight_color"] == "#00FF88"
