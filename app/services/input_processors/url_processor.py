"""URL to Video — extract article content from URL, generate video script"""

import re
from dataclasses import dataclass
from typing import Optional
from loguru import logger


@dataclass
class ExtractedContent:
    """Content extracted from a URL"""
    title: str
    text: str
    url: str
    author: str = ""
    date: str = ""
    images: list[str] = None
    language: str = "en"

    def __post_init__(self):
        if self.images is None:
            self.images = []


class URLProcessor:
    """Extract content from URLs and prepare for video generation"""

    async def extract(self, url: str) -> ExtractedContent:
        """Extract article content from a URL"""
        try:
            return await self._extract_with_trafilatura(url)
        except ImportError:
            logger.warning("trafilatura not installed, trying newspaper3k")
            try:
                return await self._extract_with_newspaper(url)
            except ImportError:
                return await self._extract_basic(url)

    async def _extract_with_trafilatura(self, url: str) -> ExtractedContent:
        """Extract using trafilatura (best quality)"""
        import trafilatura

        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            raise ValueError(f"Failed to download content from {url}")

        result = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
            output_format="json",
        )

        if not result:
            raise ValueError(f"Failed to extract content from {url}")

        import json
        data = json.loads(result)

        return ExtractedContent(
            title=data.get("title", ""),
            text=data.get("text", ""),
            url=url,
            author=data.get("author", ""),
            date=data.get("date", ""),
            language=data.get("language", "en"),
        )

    async def _extract_with_newspaper(self, url: str) -> ExtractedContent:
        """Extract using newspaper3k (fallback)"""
        from newspaper import Article

        article = Article(url)
        article.download()
        article.parse()

        return ExtractedContent(
            title=article.title or "",
            text=article.text or "",
            url=url,
            author=", ".join(article.authors) if article.authors else "",
            date=str(article.publish_date) if article.publish_date else "",
            images=list(article.images)[:10] if article.images else [],
        )

    async def _extract_basic(self, url: str) -> ExtractedContent:
        """Basic extraction using requests + regex (last resort)"""
        import requests
        from html import unescape

        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        html = resp.text

        # Extract title
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        title = unescape(title_match.group(1).strip()) if title_match else ""

        # Extract text from paragraphs
        paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", html, re.IGNORECASE | re.DOTALL)
        text = "\n".join(
            re.sub(r"<[^>]+>", "", unescape(p)).strip()
            for p in paragraphs
            if len(re.sub(r"<[^>]+>", "", p).strip()) > 50
        )

        # Extract images
        images = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)[:10]

        return ExtractedContent(
            title=title,
            text=text[:5000],  # Limit text length
            url=url,
            images=images,
        )

    async def prepare_video_params(self, url: str, template_id: str = None) -> dict:
        """Extract content from URL and prepare VideoParams-compatible dict"""
        content = await self.extract(url)

        if not content.text:
            raise ValueError(f"No content extracted from {url}")

        # Use the extracted text as the video script
        params = {
            "video_subject": content.title,
            "video_script": content.text[:3000],  # Limit for LLM context
            "video_language": content.language,
        }

        if template_id:
            from app.services.template import TemplateManager
            mgr = TemplateManager()
            try:
                template_params = mgr.apply_template(template_id)
                template_params.update(params)
                params = template_params
            except ValueError:
                pass

        return params


# Global instance
url_processor = URLProcessor()
