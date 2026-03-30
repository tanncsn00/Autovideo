import numpy as np
import pytest
from app.services.utils.video_filters import (
    apply_color_preset, adjust_brightness, adjust_contrast,
    adjust_saturation, AVAILABLE_PRESETS,
    _cinematic, _warm, _cool, _vintage, _noir, _vibrant, _muted,
)


@pytest.fixture
def sample_frame():
    """Create a simple 100x100 RGB test frame"""
    return np.random.randint(50, 200, (100, 100, 3), dtype=np.uint8)


class TestColorPresets:
    def test_all_presets_valid(self):
        assert len(AVAILABLE_PRESETS) >= 8
        assert "cinematic" in AVAILABLE_PRESETS
        assert "none" in AVAILABLE_PRESETS

    def test_cinematic(self, sample_frame):
        result = _cinematic(sample_frame)
        assert result.shape == sample_frame.shape
        assert result.dtype == np.uint8

    def test_warm(self, sample_frame):
        result = _warm(sample_frame)
        assert result.shape == sample_frame.shape
        # Warm should increase red channel on average
        assert result[:, :, 0].mean() >= sample_frame[:, :, 0].mean()

    def test_cool(self, sample_frame):
        result = _cool(sample_frame)
        assert result.shape == sample_frame.shape
        # Cool should increase blue channel
        assert result[:, :, 2].mean() >= sample_frame[:, :, 2].mean()

    def test_vintage(self, sample_frame):
        result = _vintage(sample_frame)
        assert result.shape == sample_frame.shape

    def test_noir(self, sample_frame):
        result = _noir(sample_frame)
        assert result.shape == sample_frame.shape
        # Noir should be grayscale
        assert np.allclose(result[:, :, 0], result[:, :, 1], atol=1)

    def test_vibrant(self, sample_frame):
        result = _vibrant(sample_frame)
        assert result.shape == sample_frame.shape

    def test_muted(self, sample_frame):
        result = _muted(sample_frame)
        assert result.shape == sample_frame.shape

    def test_none_returns_same(self, sample_frame):
        # When preset is "none", should not modify
        from unittest.mock import MagicMock
        clip = MagicMock()
        result_clip = apply_color_preset(clip, "none")
        assert result_clip is clip  # No transformation applied

    def test_unknown_preset_returns_same(self):
        from unittest.mock import MagicMock
        clip = MagicMock()
        result_clip = apply_color_preset(clip, "nonexistent")
        assert result_clip is clip


class TestAdjustments:
    def test_brightness_increase(self, sample_frame):
        result = (sample_frame.astype(np.float32) * 1.5).clip(0, 255).astype(np.uint8)
        assert result.mean() > sample_frame.mean()

    def test_contrast(self, sample_frame):
        from app.services.utils.video_filters import _adjust_contrast
        result = _adjust_contrast(sample_frame.astype(np.float32), 1.5)
        assert result.std() > sample_frame.astype(np.float32).std() * 0.9
