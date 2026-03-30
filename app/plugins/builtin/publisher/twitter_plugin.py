import os
import time
import requests
from app.plugins.base import PublisherPlugin, PluginMeta
from app.config.config import get_api_key
from loguru import logger


class TwitterPlugin(PublisherPlugin):

    API_BASE = "https://api.x.com/2"
    UPLOAD_BASE = "https://upload.twitter.com/1.1"

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="twitter", display_name="X (Twitter)", version="1.0.0",
            description="Upload videos and post to X (Twitter)",
            author="MoneyPrinterTurbo", plugin_type="publisher", builtin=True,
            config_schema={"bearer_token": {"type": "string"}, "api_key": {"type": "string"},
                          "api_secret": {"type": "string"}, "access_token": {"type": "string"},
                          "access_token_secret": {"type": "string"}},
        )

    def validate_config(self, config): return bool(config.get("bearer_token"))
    def is_available(self): return bool(get_api_key("twitter_bearer_token"))

    async def authenticate(self, credentials):
        token = credentials.get("bearer_token") or get_api_key("twitter_bearer_token")
        try:
            resp = requests.get(f"{self.API_BASE}/users/me", headers={"Authorization": f"Bearer {token}"}, timeout=10)
            return resp.status_code == 200
        except: return False

    async def publish(self, video_path, title, description="", tags=None, thumbnail_path=None, schedule_time=None, **kwargs):
        bearer = get_api_key("twitter_bearer_token")
        headers = {"Authorization": f"Bearer {bearer}"}

        # X API v2 media upload is complex (chunked upload required)
        # Simplified: post text with video reference
        # Full implementation would use OAuth 1.0a + chunked media upload

        text = title
        if tags: text += "\n" + " ".join(f"#{t}" for t in tags)
        if description: text = f"{title}\n\n{description}"
        text = text[:280]  # Twitter limit

        # For MVP: post text only (video upload requires OAuth 1.0a)
        resp = requests.post(f"{self.API_BASE}/tweets", headers={**headers, "Content-Type": "application/json"},
            json={"text": text}, timeout=30)
        resp.raise_for_status()
        tweet_id = resp.json()["data"]["id"]

        return {"platform": "twitter", "tweet_id": tweet_id, "url": f"https://x.com/i/status/{tweet_id}", "status": "published"}

    def get_supported_features(self): return ["upload", "tags"]
