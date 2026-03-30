import os
import time
import requests
from app.plugins.base import PublisherPlugin, PluginMeta
from app.config.config import get_api_key
from loguru import logger


class InstagramPlugin(PublisherPlugin):

    API_BASE = "https://graph.facebook.com/v21.0"

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="instagram", display_name="Instagram Reels", version="1.0.0",
            description="Upload Reels to Instagram with captions and hashtags",
            author="MoneyPrinterTurbo", plugin_type="publisher", builtin=True,
            config_schema={"access_token": {"type": "string", "required": True}, "ig_user_id": {"type": "string", "required": True}},
        )

    def validate_config(self, config): return bool(config.get("access_token") and config.get("ig_user_id"))
    def is_available(self): return bool(get_api_key("instagram_access_token") and get_api_key("instagram_user_id"))

    async def authenticate(self, credentials):
        token = credentials.get("access_token") or get_api_key("instagram_access_token")
        try:
            resp = requests.get(f"{self.API_BASE}/me", params={"access_token": token}, timeout=10)
            return resp.status_code == 200
        except: return False

    async def publish(self, video_path, title, description="", tags=None, thumbnail_path=None, schedule_time=None, **kwargs):
        token = get_api_key("instagram_access_token")
        user_id = get_api_key("instagram_user_id")
        caption = description or title
        if tags: caption += "\n" + " ".join(f"#{t}" for t in tags)

        # Must be a publicly accessible URL — user needs to host the video
        video_url = kwargs.get("video_url")
        if not video_url:
            raise ValueError("Instagram requires a publicly accessible video_url. Upload to a CDN first.")

        # Step 1: Create media container
        resp = requests.post(f"{self.API_BASE}/{user_id}/media", params={
            "media_type": "REELS", "video_url": video_url, "caption": caption,
            "access_token": token,
        }, timeout=30)
        resp.raise_for_status()
        container_id = resp.json()["id"]

        # Step 2: Wait for processing
        for _ in range(30):
            status_resp = requests.get(f"{self.API_BASE}/{container_id}", params={
                "fields": "status_code", "access_token": token,
            }, timeout=10)
            if status_resp.json().get("status_code") == "FINISHED": break
            time.sleep(5)

        # Step 3: Publish
        pub_resp = requests.post(f"{self.API_BASE}/{user_id}/media_publish", params={
            "creation_id": container_id, "access_token": token,
        }, timeout=30)
        pub_resp.raise_for_status()
        media_id = pub_resp.json()["id"]

        return {"platform": "instagram", "media_id": media_id, "status": "published"}

    def get_supported_features(self): return ["upload", "tags", "description"]
