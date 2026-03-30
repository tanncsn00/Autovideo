"""Publishing manager — orchestrates publishing to multiple platforms"""

from typing import Optional
from loguru import logger
from app.plugins import plugin_manager
from app.plugins.base import PublisherPlugin


class PublishManager:
    """Manages video publishing across platforms"""

    def get_available_publishers(self) -> list[dict]:
        """List all publisher plugins with their status"""
        return plugin_manager.list_plugins("publisher")

    def get_publisher(self, platform: str) -> Optional[PublisherPlugin]:
        """Get a specific publisher plugin by name"""
        plugin = plugin_manager.get_plugin("publisher", platform)
        if plugin and isinstance(plugin, PublisherPlugin):
            return plugin
        return None

    async def publish_to_platform(
        self,
        platform: str,
        video_path: str,
        title: str,
        description: str = "",
        tags: list[str] = None,
        thumbnail_path: str = None,
        schedule_time: str = None,
        **kwargs,
    ) -> dict:
        """Publish a video to a specific platform"""
        publisher = self.get_publisher(platform)
        if not publisher:
            raise ValueError(f"Publisher not found: {platform}")
        if not publisher.is_available():
            raise ValueError(f"Publisher {platform} is not configured (missing credentials)")

        result = await publisher.publish(
            video_path=video_path,
            title=title,
            description=description,
            tags=tags,
            thumbnail_path=thumbnail_path,
            schedule_time=schedule_time,
            **kwargs,
        )

        # Record analytics after successful publish
        try:
            import os as _os
            if _os.environ.get("MPT_MODE") == "desktop":
                from app.services.analytics import AnalyticsManager
                analytics = AnalyticsManager()
                analytics.record_metrics(
                    task_id=kwargs.get("task_id", ""),
                    platform=platform,
                    video_url=result.get("url", ""),
                    metadata={"publish_result": result}
                )
        except Exception:
            pass

        return result

    async def publish_to_multiple(
        self,
        platforms: list[str],
        video_path: str,
        title: str,
        description: str = "",
        tags: list[str] = None,
        thumbnail_path: str = None,
        **kwargs,
    ) -> dict:
        """Publish to multiple platforms at once"""
        results = {}
        for platform in platforms:
            try:
                result = await self.publish_to_platform(
                    platform=platform,
                    video_path=video_path,
                    title=title,
                    description=description,
                    tags=tags,
                    thumbnail_path=thumbnail_path,
                    **kwargs,
                )
                results[platform] = {"status": "success", **result}
            except Exception as e:
                results[platform] = {"status": "error", "error": str(e)}
                logger.error(f"Publishing to {platform} failed: {e}")
        return results


# Global instance
publish_manager = PublishManager()
