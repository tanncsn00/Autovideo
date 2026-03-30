import numpy as np
from moviepy import Clip, vfx, VideoClip


# FadeIn
def fadein_transition(clip: Clip, t: float) -> Clip:
    return clip.with_effects([vfx.FadeIn(t)])


# FadeOut
def fadeout_transition(clip: Clip, t: float) -> Clip:
    return clip.with_effects([vfx.FadeOut(t)])


# SlideIn
def slidein_transition(clip: Clip, t: float, side: str) -> Clip:
    return clip.with_effects([vfx.SlideIn(t, side)])


# SlideOut
def slideout_transition(clip: Clip, t: float, side: str) -> Clip:
    return clip.with_effects([vfx.SlideOut(t, side)])


# --- NEW transitions ---

def dissolve_transition(clip1: Clip, clip2: Clip, duration: float = 1.0):
    """Cross-dissolve between two clips"""
    clip1_faded = clip1.with_effects([vfx.FadeOut(duration)])
    clip2_faded = clip2.with_effects([vfx.FadeIn(duration)])
    return clip1_faded, clip2_faded


def wipe_left_transition(clip: Clip, t: float) -> Clip:
    """Wipe from right to left"""
    return clip.with_effects([vfx.SlideIn(t, "left")])


def wipe_right_transition(clip: Clip, t: float) -> Clip:
    """Wipe from left to right"""
    return clip.with_effects([vfx.SlideIn(t, "right")])


def wipe_up_transition(clip: Clip, t: float) -> Clip:
    """Wipe from bottom to top"""
    return clip.with_effects([vfx.SlideIn(t, "bottom")])


def wipe_down_transition(clip: Clip, t: float) -> Clip:
    """Wipe from top to bottom"""
    return clip.with_effects([vfx.SlideIn(t, "top")])


def push_left_transition(clip: Clip, t: float) -> Clip:
    """Push clip out to the left"""
    return clip.with_effects([vfx.SlideOut(t, "left")])


def push_right_transition(clip: Clip, t: float) -> Clip:
    """Push clip out to the right"""
    return clip.with_effects([vfx.SlideOut(t, "right")])


def zoom_in_transition(clip: Clip, t: float) -> Clip:
    """Zoom in effect at start of clip"""
    def zoom_effect(get_frame, t_val):
        frame = get_frame(t_val)
        if t_val < t:
            # Scale from 1.3 to 1.0 during transition
            progress = t_val / t
            scale = 1.3 - (0.3 * progress)
            h, w = frame.shape[:2]
            new_h, new_w = int(h * scale), int(w * scale)
            # Center crop
            y_start = (new_h - h) // 2
            x_start = (new_w - w) // 2
            from PIL import Image
            img = Image.fromarray(frame)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            cropped = np.array(img)[y_start:y_start+h, x_start:x_start+w]
            return cropped
        return frame
    return clip.transform(zoom_effect)


def zoom_out_transition(clip: Clip, t: float) -> Clip:
    """Zoom out effect at start of clip"""
    def zoom_effect(get_frame, t_val):
        frame = get_frame(t_val)
        if t_val < t:
            progress = t_val / t
            scale = 0.7 + (0.3 * progress)
            h, w = frame.shape[:2]
            new_h, new_w = int(h * scale), int(w * scale)
            from PIL import Image
            img = Image.fromarray(frame)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            # Center pad
            result = np.zeros_like(frame)
            y_start = (h - new_h) // 2
            x_start = (w - new_w) // 2
            result[max(0,y_start):max(0,y_start)+new_h, max(0,x_start):max(0,x_start)+new_w] = np.array(img)
            return result
        return frame
    return clip.transform(zoom_effect)


def flash_transition(clip: Clip, t: float) -> Clip:
    """White flash at start of clip"""
    def flash_effect(get_frame, t_val):
        frame = get_frame(t_val)
        if t_val < t:
            progress = t_val / t
            # Flash fades from white to normal
            white = np.ones_like(frame) * 255
            alpha = 1.0 - progress
            blended = (frame * progress + white * alpha).astype(np.uint8)
            return blended
        return frame
    return clip.transform(flash_effect)


def black_fade_transition(clip: Clip, t: float) -> Clip:
    """Fade from black at start of clip"""
    def fade_effect(get_frame, t_val):
        frame = get_frame(t_val)
        if t_val < t:
            progress = t_val / t
            return (frame * progress).astype(np.uint8)
        return frame
    return clip.transform(fade_effect)


# Registry mapping transition names to functions
TRANSITION_REGISTRY = {
    "FadeIn": lambda clip, t: fadein_transition(clip, t),
    "FadeOut": lambda clip, t: fadeout_transition(clip, t),
    "SlideIn": lambda clip, t: slidein_transition(clip, t, "left"),
    "SlideOut": lambda clip, t: slideout_transition(clip, t, "right"),
    "WipeLeft": lambda clip, t: wipe_left_transition(clip, t),
    "WipeRight": lambda clip, t: wipe_right_transition(clip, t),
    "WipeUp": lambda clip, t: wipe_up_transition(clip, t),
    "WipeDown": lambda clip, t: wipe_down_transition(clip, t),
    "PushLeft": lambda clip, t: push_left_transition(clip, t),
    "PushRight": lambda clip, t: push_right_transition(clip, t),
    "ZoomIn": lambda clip, t: zoom_in_transition(clip, t),
    "ZoomOut": lambda clip, t: zoom_out_transition(clip, t),
    "Flash": lambda clip, t: flash_transition(clip, t),
    "BlackFade": lambda clip, t: black_fade_transition(clip, t),
}


def apply_transition(clip: Clip, transition_name: str, duration: float = 0.8) -> Clip:
    """Apply a transition by name. Returns the clip with transition applied."""
    if transition_name in TRANSITION_REGISTRY:
        return TRANSITION_REGISTRY[transition_name](clip, duration)
    # Fallback: no transition
    return clip
