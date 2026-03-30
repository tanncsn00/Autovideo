"""API endpoints for multi-modal input processing"""

from pydantic import BaseModel
from typing import Optional
from app.controllers.v1.base import new_router
from app.utils import utils
from loguru import logger

router = new_router()


class URLInputRequest(BaseModel):
    url: str
    template_id: str = ""


@router.post("/input/url", summary="Create video from URL (article or video)")
async def process_url(body: URLInputRequest):
    url = body.url.strip()

    # Auto-detect: YouTube/TikTok → extract transcript; Other → extract article
    if any(domain in url for domain in ["youtube.com", "youtu.be", "tiktok.com"]):
        from app.services.input_processors.video_url_processor import video_url_processor
        try:
            params = await video_url_processor.prepare_video_params(url, body.template_id)
            return utils.get_response(200, params)
        except Exception as e:
            return utils.get_response(400, message=str(e))
    else:
        from app.services.input_processors.url_processor import url_processor
        try:
            params = await url_processor.prepare_video_params(url, body.template_id)
            return utils.get_response(200, params)
        except Exception as e:
            return utils.get_response(400, message=str(e))


class RSSInputRequest(BaseModel):
    feed_url: str
    template_id: str = ""
    max_items: int = 10


@router.post("/input/rss", summary="Create batch from RSS feed")
async def process_rss(body: RSSInputRequest):
    from app.services.input_processors.rss_processor import rss_processor
    try:
        topics = await rss_processor.feed_to_batch_topics(body.feed_url, body.template_id, body.max_items)
        return utils.get_response(200, topics)
    except Exception as e:
        return utils.get_response(400, message=str(e))


class AIDirectorRequest(BaseModel):
    subject: str
    script: str = ""
    platform: str = "general"
    language: str = "en"


@router.post("/input/ai-director", summary="Get AI Director suggestions")
async def ai_director_analyze(body: AIDirectorRequest):
    from app.services.ai_director import ai_director
    try:
        suggestion = await ai_director.analyze(body.subject, body.script, body.platform, body.language)
        return utils.get_response(200, suggestion.to_dict())
    except Exception as e:
        return utils.get_response(400, message=str(e))
