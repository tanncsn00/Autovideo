"""Animated captions system — word-by-word highlight synchronized with audio.

Supports multiple visual styles similar to CapCut and Opus Clip.
"""

import re
from dataclasses import dataclass
from typing import Optional
from moviepy import TextClip, CompositeVideoClip, ColorClip
from PIL import ImageFont
import numpy as np


@dataclass
class CaptionWord:
    """A single word with timing"""
    text: str
    start: float  # seconds
    end: float    # seconds


@dataclass
class CaptionSegment:
    """A subtitle segment containing multiple words"""
    words: list[CaptionWord]
    start: float
    end: float

    @property
    def full_text(self) -> str:
        return " ".join(w.text for w in self.words)


# ═══════════════════════════════════════════
# CAPTION STYLES
# ═══════════════════════════════════════════

CAPTION_STYLES = {
    "default": {
        "font_size": 60,
        "font_color": "#FFFFFF",
        "highlight_color": "#FFFF00",
        "stroke_color": "#000000",
        "stroke_width": 2,
        "bg_color": None,
        "position": "bottom",
        "animation": "highlight",  # highlight, scale, none
    },
    "hormozi": {
        "font_size": 80,
        "font_color": "#FFFFFF",
        "highlight_color": "#00FF88",
        "stroke_color": "#000000",
        "stroke_width": 3,
        "bg_color": None,
        "position": "center",
        "animation": "highlight",
    },
    "documentary": {
        "font_size": 48,
        "font_color": "#FFFFFF",
        "highlight_color": "#4A9EFF",
        "stroke_color": "#000000",
        "stroke_width": 1.5,
        "bg_color": "rgba(0,0,0,0.6)",
        "position": "bottom",
        "animation": "highlight",
    },
    "tiktok-viral": {
        "font_size": 72,
        "font_color": "#FFFFFF",
        "highlight_color": "#FF3366",
        "stroke_color": "#000000",
        "stroke_width": 2.5,
        "bg_color": None,
        "position": "center",
        "animation": "highlight",
    },
    "corporate": {
        "font_size": 44,
        "font_color": "#FFFFFF",
        "highlight_color": "#3B82F6",
        "stroke_color": "#1E293B",
        "stroke_width": 1,
        "bg_color": "rgba(15,23,42,0.7)",
        "position": "bottom",
        "animation": "highlight",
    },
}


def get_caption_style(style_name: str) -> dict:
    """Get a caption style by name, with fallback to default"""
    return CAPTION_STYLES.get(style_name, CAPTION_STYLES["default"]).copy()


def list_caption_styles() -> list[str]:
    """List all available caption style names"""
    return list(CAPTION_STYLES.keys())


# ═══════════════════════════════════════════
# SRT PARSING
# ═══════════════════════════════════════════

def parse_srt_to_segments(srt_path: str) -> list[CaptionSegment]:
    """Parse an SRT file into CaptionSegments with word-level timing estimates"""
    segments = []

    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse SRT blocks
    blocks = re.split(r"\n\n+", content.strip())
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue

        # Parse timing line: "00:00:01,000 --> 00:00:05,000"
        timing_match = re.match(
            r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})",
            lines[1],
        )
        if not timing_match:
            continue

        g = timing_match.groups()
        start = int(g[0]) * 3600 + int(g[1]) * 60 + int(g[2]) + int(g[3]) / 1000
        end = int(g[4]) * 3600 + int(g[5]) * 60 + int(g[6]) + int(g[7]) / 1000

        text = " ".join(lines[2:]).strip()
        if not text:
            continue

        # Split into words and distribute timing evenly
        words_text = text.split()
        if not words_text:
            continue

        duration = end - start
        word_duration = duration / len(words_text)

        words = []
        for i, word in enumerate(words_text):
            w_start = start + i * word_duration
            w_end = start + (i + 1) * word_duration
            words.append(CaptionWord(text=word, start=w_start, end=w_end))

        segments.append(CaptionSegment(words=words, start=start, end=end))

    return segments


# ═══════════════════════════════════════════
# CAPTION RENDERING
# ═══════════════════════════════════════════

def create_animated_caption_clips(
    segments: list[CaptionSegment],
    video_width: int,
    video_height: int,
    style_name: str = "default",
    font_path: str = None,
) -> list:
    """Create MoviePy clips for animated captions.

    Returns a list of CompositeVideoClip-compatible clips that can be
    overlaid on the main video.
    """
    style = get_caption_style(style_name)
    clips = []

    for segment in segments:
        segment_clips = _render_segment(
            segment=segment,
            video_width=video_width,
            video_height=video_height,
            style=style,
            font_path=font_path,
        )
        clips.extend(segment_clips)

    return clips


def _render_segment(
    segment: CaptionSegment,
    video_width: int,
    video_height: int,
    style: dict,
    font_path: str = None,
) -> list:
    """Render a single caption segment as animated clips"""
    full_text = segment.full_text
    duration = segment.end - segment.start
    font_size = style["font_size"]
    position = style["position"]

    # Calculate Y position
    if position == "center":
        y_pos = video_height // 2
    elif position == "top":
        y_pos = int(video_height * 0.15)
    else:  # bottom
        y_pos = int(video_height * 0.80)

    clips = []

    # Create the main text clip (non-highlighted words)
    def make_frame(t):
        """Generate frame with highlighted word at time t"""
        # Find which word should be highlighted at time t
        absolute_t = segment.start + t
        highlighted_idx = -1
        for i, word in enumerate(segment.words):
            if word.start <= absolute_t < word.end:
                highlighted_idx = i
                break

        # Build the text image with highlight
        from PIL import Image, ImageDraw

        # Estimate text dimensions
        try:
            if font_path:
                font = ImageFont.truetype(font_path, font_size)
            else:
                font = ImageFont.truetype("arial.ttf", font_size)
        except (IOError, OSError):
            font = ImageFont.load_default()

        # Measure full text
        dummy_img = Image.new("RGBA", (video_width, font_size * 3), (0, 0, 0, 0))
        draw = ImageDraw.Draw(dummy_img)

        # Calculate word positions
        words = segment.words
        x_cursor = 0
        word_positions = []
        space_width = draw.textlength(" ", font=font) if hasattr(draw, "textlength") else font_size // 3

        for i, word in enumerate(words):
            w = draw.textlength(word.text, font=font) if hasattr(draw, "textlength") else len(word.text) * font_size * 0.6
            word_positions.append((x_cursor, w))
            x_cursor += w + space_width

        total_width = x_cursor - space_width
        x_offset = (video_width - total_width) // 2

        # Create the actual image
        img = Image.new("RGBA", (video_width, font_size * 2 + 20), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw background bar if style has one
        if style.get("bg_color") and style["bg_color"] != "None":
            bg_padding = 10
            draw.rectangle(
                [x_offset - bg_padding, 0, x_offset + total_width + bg_padding, font_size + bg_padding * 2],
                fill=(0, 0, 0, 150),
            )

        # Draw each word
        stroke_w = int(style.get("stroke_width", 2))
        for i, word in enumerate(words):
            x, w = word_positions[i]
            color = style["highlight_color"] if i == highlighted_idx else style["font_color"]

            # Draw stroke
            for dx in range(-stroke_w, stroke_w + 1):
                for dy in range(-stroke_w, stroke_w + 1):
                    if dx == 0 and dy == 0:
                        continue
                    draw.text(
                        (x_offset + x + dx, 10 + dy),
                        word.text,
                        fill=style["stroke_color"],
                        font=font,
                    )
            # Draw text
            draw.text((x_offset + x, 10), word.text, fill=color, font=font)

        return np.array(img)

    # Create a VideoClip from the frame generator
    from moviepy import VideoClip

    caption_clip = VideoClip(make_frame, duration=duration)
    caption_clip = caption_clip.with_start(segment.start)
    caption_clip = caption_clip.with_position(("center", y_pos))

    clips.append(caption_clip)

    return clips


# ═══════════════════════════════════════════
# CONVENIENCE FUNCTION
# ═══════════════════════════════════════════

def overlay_animated_captions(
    video_clip,
    srt_path: str,
    style_name: str = "default",
    font_path: str = None,
):
    """Overlay animated captions on a video clip.

    Args:
        video_clip: MoviePy VideoClip
        srt_path: Path to SRT subtitle file
        style_name: Caption style name
        font_path: Optional path to font file

    Returns:
        CompositeVideoClip with animated captions overlaid
    """
    segments = parse_srt_to_segments(srt_path)
    if not segments:
        return video_clip

    caption_clips = create_animated_caption_clips(
        segments=segments,
        video_width=video_clip.w,
        video_height=video_clip.h,
        style_name=style_name,
        font_path=font_path,
    )

    return CompositeVideoClip([video_clip] + caption_clips)
