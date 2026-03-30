"""RSS Feed to Video Series — auto-generate videos from blog feeds"""

from dataclasses import dataclass
from typing import Optional
from loguru import logger


@dataclass
class FeedItem:
    """A single RSS feed entry"""
    title: str
    url: str
    summary: str = ""
    published: str = ""
    author: str = ""


class RSSProcessor:
    """Process RSS feeds into video generation jobs"""

    async def fetch_feed(self, feed_url: str, max_items: int = 10) -> list[FeedItem]:
        """Fetch and parse an RSS/Atom feed"""
        try:
            import feedparser
            feed = feedparser.parse(feed_url)

            items = []
            for entry in feed.entries[:max_items]:
                items.append(FeedItem(
                    title=entry.get("title", ""),
                    url=entry.get("link", ""),
                    summary=entry.get("summary", entry.get("description", ""))[:2000],
                    published=entry.get("published", ""),
                    author=entry.get("author", ""),
                ))
            return items

        except ImportError:
            logger.warning("feedparser not installed. Install with: pip install feedparser")
            raise ImportError("feedparser is required for RSS processing. Install: pip install feedparser")

    async def feed_to_batch_topics(self, feed_url: str, template_id: str = "", max_items: int = 10) -> list[dict]:
        """Convert RSS feed items into batch-compatible topic dicts"""
        items = await self.fetch_feed(feed_url, max_items)

        topics = []
        for item in items:
            if item.title:
                topics.append({
                    "topic": item.title,
                    "template_id": template_id,
                    "platform": "general",
                    "language": "en",
                    "params": {
                        "video_subject": item.title,
                        "video_script": item.summary if item.summary else None,
                    },
                })

        return topics


rss_processor = RSSProcessor()
