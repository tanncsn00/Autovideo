"""Video filters and color grading presets for MoneyPrinterTurbo"""

import numpy as np
from moviepy import Clip


# ═══════════════════════════════════════════
# COLOR GRADING PRESETS
# ═══════════════════════════════════════════

def apply_color_preset(clip: Clip, preset: str) -> Clip:
    """Apply a color grading preset to a video clip"""
    presets = {
        "cinematic": _cinematic,
        "warm": _warm,
        "cool": _cool,
        "vintage": _vintage,
        "noir": _noir,
        "vibrant": _vibrant,
        "muted": _muted,
        "high_contrast": _high_contrast,
        "dark_motivation": _dark_motivation,
        "dark_cinematic": _dark_cinematic,
    }
    fn = presets.get(preset)
    if fn is None:
        return clip  # "none" or unknown preset
    return clip.image_transform(fn)


def _cinematic(frame: np.ndarray) -> np.ndarray:
    """Cinematic look: slight teal in shadows, warm highlights, crushed blacks"""
    result = frame.astype(np.float32)
    # Crush blacks slightly
    result = np.clip(result - 10, 0, 255)
    # Teal shadows: boost blue in dark areas
    mask = (result.mean(axis=2, keepdims=True) < 80).astype(np.float32)
    result[:, :, 2] = np.clip(result[:, :, 2] + mask[:, :, 0] * 15, 0, 255)  # Blue
    result[:, :, 1] = np.clip(result[:, :, 1] + mask[:, :, 0] * 5, 0, 255)   # Green (teal)
    # Warm highlights: boost red/yellow in bright areas
    bright_mask = (result.mean(axis=2, keepdims=True) > 180).astype(np.float32)
    result[:, :, 0] = np.clip(result[:, :, 0] + bright_mask[:, :, 0] * 10, 0, 255)  # Red
    # Boost contrast slightly
    result = _adjust_contrast(result, 1.1)
    return result.astype(np.uint8)


def _warm(frame: np.ndarray) -> np.ndarray:
    """Warm look: boost reds and yellows"""
    result = frame.astype(np.float32)
    result[:, :, 0] = np.clip(result[:, :, 0] * 1.08, 0, 255)  # Red +8%
    result[:, :, 1] = np.clip(result[:, :, 1] * 1.03, 0, 255)  # Green +3%
    result[:, :, 2] = np.clip(result[:, :, 2] * 0.92, 0, 255)  # Blue -8%
    return result.astype(np.uint8)


def _cool(frame: np.ndarray) -> np.ndarray:
    """Cool look: boost blues"""
    result = frame.astype(np.float32)
    result[:, :, 0] = np.clip(result[:, :, 0] * 0.93, 0, 255)  # Red -7%
    result[:, :, 2] = np.clip(result[:, :, 2] * 1.1, 0, 255)   # Blue +10%
    return result.astype(np.uint8)


def _vintage(frame: np.ndarray) -> np.ndarray:
    """Vintage/retro: desaturated, warm tint, slight fade"""
    result = frame.astype(np.float32)
    # Desaturate
    gray = result.mean(axis=2, keepdims=True)
    result = result * 0.7 + gray * 0.3
    # Warm tint
    result[:, :, 0] = np.clip(result[:, :, 0] + 15, 0, 255)  # Red
    result[:, :, 1] = np.clip(result[:, :, 1] + 5, 0, 255)   # Green
    # Fade blacks (raise floor)
    result = np.clip(result + 20, 0, 255)
    # Reduce contrast
    result = _adjust_contrast(result, 0.9)
    return result.astype(np.uint8)


def _noir(frame: np.ndarray) -> np.ndarray:
    """Black and white with high contrast"""
    result = frame.astype(np.float32)
    gray = 0.299 * result[:, :, 0] + 0.587 * result[:, :, 1] + 0.114 * result[:, :, 2]
    gray = _adjust_contrast(gray[:, :, np.newaxis], 1.3)[:, :, 0]
    result[:, :, 0] = gray
    result[:, :, 1] = gray
    result[:, :, 2] = gray
    return np.clip(result, 0, 255).astype(np.uint8)


def _vibrant(frame: np.ndarray) -> np.ndarray:
    """Vibrant: boost saturation"""
    result = frame.astype(np.float32)
    gray = result.mean(axis=2, keepdims=True)
    result = gray + (result - gray) * 1.4  # Boost saturation by 40%
    return np.clip(result, 0, 255).astype(np.uint8)


def _muted(frame: np.ndarray) -> np.ndarray:
    """Muted: reduce saturation"""
    result = frame.astype(np.float32)
    gray = result.mean(axis=2, keepdims=True)
    result = gray + (result - gray) * 0.6  # Reduce saturation by 40%
    return np.clip(result, 0, 255).astype(np.uint8)


def _high_contrast(frame: np.ndarray) -> np.ndarray:
    """High contrast"""
    return _adjust_contrast(frame.astype(np.float32), 1.4).astype(np.uint8)


def _dark_motivation(frame: np.ndarray) -> np.ndarray:
    """Dark motivation style: very dark, desaturated, high contrast — like hustle/grind videos"""
    result = frame.astype(np.float32)
    # Heavy desaturation (almost B&W but keep slight color)
    gray = result.mean(axis=2, keepdims=True)
    result = gray + (result - gray) * 0.15  # Keep only 15% color
    # Darken significantly
    result = result * 0.55
    # Boost contrast hard
    result = _adjust_contrast(result, 1.6)
    # Crush blacks
    result = np.clip(result - 15, 0, 255)
    return result.astype(np.uint8)


def _dark_cinematic(frame: np.ndarray) -> np.ndarray:
    """Dark cinematic: moody, teal shadows, dark overall"""
    result = frame.astype(np.float32)
    # Darken
    result = result * 0.65
    # Teal in shadows
    mask = (result.mean(axis=2, keepdims=True) < 60).astype(np.float32)
    result[:, :, 2] = np.clip(result[:, :, 2] + mask[:, :, 0] * 25, 0, 255)
    result[:, :, 1] = np.clip(result[:, :, 1] + mask[:, :, 0] * 10, 0, 255)
    # High contrast
    result = _adjust_contrast(result, 1.4)
    return np.clip(result, 0, 255).astype(np.uint8)


# ═══════════════════════════════════════════
# ADJUSTMENT FUNCTIONS
# ═══════════════════════════════════════════

def _adjust_contrast(img: np.ndarray, factor: float) -> np.ndarray:
    """Adjust contrast. factor > 1 = more contrast."""
    mean = img.mean()
    return np.clip((img - mean) * factor + mean, 0, 255)


def adjust_brightness(clip: Clip, factor: float) -> Clip:
    """Adjust brightness. factor > 1 = brighter."""
    def transform(frame):
        return np.clip(frame.astype(np.float32) * factor, 0, 255).astype(np.uint8)
    return clip.image_transform(transform)


def adjust_contrast(clip: Clip, factor: float) -> Clip:
    """Adjust contrast. factor > 1 = more contrast."""
    def transform(frame):
        return _adjust_contrast(frame.astype(np.float32), factor).astype(np.uint8)
    return clip.image_transform(transform)


def adjust_saturation(clip: Clip, factor: float) -> Clip:
    """Adjust saturation. factor > 1 = more saturated."""
    def transform(frame):
        result = frame.astype(np.float32)
        gray = result.mean(axis=2, keepdims=True)
        result = gray + (result - gray) * factor
        return np.clip(result, 0, 255).astype(np.uint8)
    return clip.image_transform(transform)


# ═══════════════════════════════════════════
# VISUAL EFFECTS
# ═══════════════════════════════════════════

def apply_vignette(clip: Clip, strength: float = 0.5) -> Clip:
    """Add vignette effect (darken edges)"""
    def transform(frame):
        h, w = frame.shape[:2]
        Y, X = np.ogrid[:h, :w]
        center_y, center_x = h / 2, w / 2
        # Distance from center, normalized
        dist = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
        max_dist = np.sqrt(center_x**2 + center_y**2)
        dist = dist / max_dist
        # Vignette mask
        mask = 1.0 - (dist * strength)
        mask = np.clip(mask, 0, 1)
        mask = mask[:, :, np.newaxis]
        return (frame * mask).astype(np.uint8)
    return clip.image_transform(transform)


def apply_film_grain(clip: Clip, intensity: float = 0.05) -> Clip:
    """Add film grain noise"""
    def transform(frame):
        noise = np.random.normal(0, intensity * 255, frame.shape)
        return np.clip(frame.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    return clip.image_transform(transform)


def apply_letterbox(clip: Clip, ratio: float = 0.1) -> Clip:
    """Add cinematic letterbox (black bars top/bottom)"""
    def transform(frame):
        h, w = frame.shape[:2]
        bar_height = int(h * ratio)
        result = frame.copy()
        result[:bar_height, :] = 0
        result[h - bar_height:, :] = 0
        return result
    return clip.image_transform(transform)


# ═══════════════════════════════════════════
# WATERMARK
# ═══════════════════════════════════════════

def add_watermark_text(clip: Clip, text: str, position: str = "bottom-right",
                       font_size: int = 24, opacity: float = 0.5) -> Clip:
    """Add text watermark overlay"""
    from moviepy import TextClip, CompositeVideoClip

    txt_clip = TextClip(
        text=text,
        font_size=font_size,
        color="white",
        font="Arial",
    )
    txt_clip = txt_clip.with_duration(clip.duration)
    txt_clip = txt_clip.with_opacity(opacity)

    pos_map = {
        "top-left": ("left", "top"),
        "top-right": ("right", "top"),
        "bottom-left": ("left", "bottom"),
        "bottom-right": ("right", "bottom"),
        "center": ("center", "center"),
    }
    pos = pos_map.get(position, ("right", "bottom"))

    return CompositeVideoClip([clip, txt_clip.with_position(pos)])


# ═══════════════════════════════════════════
# PRESET NAMES
# ═══════════════════════════════════════════

AVAILABLE_PRESETS = [
    "none", "cinematic", "warm", "cool", "vintage", "noir",
    "vibrant", "muted", "high_contrast", "dark_motivation", "dark_cinematic",
]
