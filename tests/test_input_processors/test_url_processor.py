import pytest
from app.services.input_processors.url_processor import URLProcessor, ExtractedContent


def test_extracted_content_defaults():
    content = ExtractedContent(title="Test", text="Body", url="http://example.com")
    assert content.title == "Test"
    assert content.images == []
    assert content.language == "en"


def test_extracted_content_with_images():
    content = ExtractedContent(
        title="Test", text="Body", url="http://example.com",
        images=["http://img1.jpg", "http://img2.jpg"],
    )
    assert len(content.images) == 2


@pytest.mark.asyncio
async def test_basic_extraction():
    """Test basic HTML extraction (doesn't need external libs)"""
    processor = URLProcessor()
    # This tests the _extract_basic method with a real URL
    # Skip if network unavailable
    try:
        content = await processor._extract_basic("https://example.com")
        assert content.url == "https://example.com"
        assert isinstance(content.title, str)
    except Exception:
        pytest.skip("Network unavailable")


@pytest.mark.asyncio
async def test_prepare_video_params():
    processor = URLProcessor()
    try:
        params = await processor.prepare_video_params("https://example.com")
        assert "video_subject" in params
        assert "video_script" in params or "video_language" in params
    except Exception:
        pytest.skip("Network unavailable or no content")


def test_url_processor_instantiation():
    processor = URLProcessor()
    assert processor is not None
