"""Video URL to Script — extract transcript from YouTube/TikTok without downloading video"""

import re
from dataclasses import dataclass
from loguru import logger


@dataclass
class VideoTranscript:
    title: str
    text: str
    url: str
    language: str = "en"
    duration: float = 0
    platform: str = ""


class VideoURLProcessor:
    """Extract transcript from video URLs (YouTube, TikTok) without downloading"""

    async def extract(self, url: str) -> VideoTranscript:
        """Auto-detect platform and extract transcript"""
        if "youtube.com" in url or "youtu.be" in url:
            return await self._extract_youtube(url)
        elif "tiktok.com" in url:
            return await self._extract_tiktok(url)
        else:
            raise ValueError(f"Unsupported video URL: {url}. Supported: YouTube, TikTok")

    async def _extract_youtube(self, url: str) -> VideoTranscript:
        """Extract transcript from YouTube video"""
        video_id = self._parse_youtube_id(url)
        if not video_id:
            raise ValueError(f"Cannot parse YouTube video ID from: {url}")

        try:
            from youtube_transcript_api import YouTubeTranscriptApi

            api = YouTubeTranscriptApi()

            # Try different languages
            fetched = None
            lang = "en"
            for try_langs in [["vi"], ["en"], ["ja"], ["ko"], ["zh"]]:
                try:
                    fetched = api.fetch(video_id, languages=try_langs)
                    lang = try_langs[0]
                    break
                except Exception:
                    pass

            # Fallback: any language
            if not fetched:
                try:
                    fetched = api.fetch(video_id)
                except Exception as e:
                    raise ValueError(f"No transcript available: {e}")

            # Combine snippets into full text
            snippets = list(fetched)
            full_text = " ".join(s.text for s in snippets)

            # Duration from last snippet
            duration = 0
            if snippets:
                last = snippets[-1]
                duration = last.start + last.duration

            title = await self._get_youtube_title(video_id)

            return VideoTranscript(
                title=title,
                text=full_text[:5000],
                url=url,
                language=lang,
                duration=duration,
                platform="youtube",
            )

        except ImportError:
            raise ImportError("youtube-transcript-api required. Install: pip install youtube-transcript-api")

    async def _extract_tiktok(self, url: str) -> VideoTranscript:
        """Extract info from TikTok — TikTok doesn't have public transcript API,
        so we extract the description/caption instead"""
        import requests

        try:
            # Use oEmbed API (no auth needed)
            oembed_url = f"https://www.tiktok.com/oembed?url={url}"
            resp = requests.get(oembed_url, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            title = data.get("title", "TikTok Video")
            author = data.get("author_name", "")

            return VideoTranscript(
                title=title,
                text=title,  # TikTok captions are short
                url=url,
                language="vi",  # Assume Vietnamese
                platform="tiktok",
            )
        except Exception as e:
            raise ValueError(f"Cannot extract TikTok info: {e}")

    def _parse_youtube_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
            r'(?:embed/)([a-zA-Z0-9_-]{11})',
            r'(?:shorts/)([a-zA-Z0-9_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return ""

    async def _get_youtube_title(self, video_id: str) -> str:
        """Get YouTube video title via oEmbed (no API key needed)"""
        import requests
        try:
            resp = requests.get(
                f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json",
                timeout=5,
            )
            if resp.status_code == 200:
                return resp.json().get("title", "")
        except:
            pass
        return f"YouTube Video {video_id}"

    async def prepare_video_params(self, url: str, template_id: str = None) -> dict:
        """Extract video transcript and prepare VideoParams"""
        transcript = await self.extract(url)

        params = {
            "video_subject": transcript.title,
            "video_script": transcript.text,
            "video_language": transcript.language,
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


video_url_processor = VideoURLProcessor()
