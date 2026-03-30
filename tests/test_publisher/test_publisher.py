import pytest
from app.plugins.base import PublisherPlugin, PluginMeta


class MockPublisher(PublisherPlugin):
    def get_meta(self):
        return PluginMeta(name="mock-pub", display_name="Mock", version="1.0.0",
                         description="Test", author="test", plugin_type="publisher")
    def validate_config(self, config): return True
    def is_available(self): return True
    async def authenticate(self, credentials): return True
    async def publish(self, video_path, title, **kwargs):
        return {"platform": "mock", "status": "published", "url": "http://example.com"}
    def get_supported_features(self): return ["upload"]


def test_publisher_plugin_instantiation():
    p = MockPublisher()
    assert p.get_meta().plugin_type == "publisher"
    assert p.is_available() is True


def test_publisher_cannot_instantiate_abstract():
    with pytest.raises(TypeError):
        PublisherPlugin()


@pytest.mark.asyncio
async def test_publisher_publish():
    p = MockPublisher()
    result = await p.publish("/tmp/video.mp4", "Test Title")
    assert result["status"] == "published"


def test_youtube_plugin_loads():
    from app.plugins.builtin.publisher.youtube_plugin import YouTubePlugin
    p = YouTubePlugin()
    meta = p.get_meta()
    assert meta.name == "youtube"
    assert meta.plugin_type == "publisher"
    assert "upload" in p.get_supported_features()
    assert "schedule" in p.get_supported_features()


def test_publish_manager():
    from app.services.publisher import PublishManager
    pm = PublishManager()
    publishers = pm.get_available_publishers()
    assert isinstance(publishers, list)
