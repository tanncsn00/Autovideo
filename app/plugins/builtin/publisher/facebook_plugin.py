import os
import requests
from app.plugins.base import PublisherPlugin, PluginMeta
from app.config.config import get_api_key
from loguru import logger


class FacebookPlugin(PublisherPlugin):

    API_BASE = "https://graph.facebook.com/v21.0"

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="facebook", display_name="Facebook", version="1.0.0",
            description="Upload videos to Facebook Pages with scheduling support",
            author="MoneyPrinterTurbo", plugin_type="publisher", builtin=True,
            config_schema={"access_token": {"type": "string"}, "page_id": {"type": "string"}},
        )

    def validate_config(self, config): return bool(config.get("access_token"))
    def is_available(self): return bool(get_api_key("facebook_access_token") and get_api_key("facebook_page_id"))

    async def authenticate(self, credentials):
        token = credentials.get("access_token") or get_api_key("facebook_access_token")
        try:
            resp = requests.get(f"{self.API_BASE}/me", params={"access_token": token}, timeout=10)
            return resp.status_code == 200
        except: return False

    async def publish(self, video_path, title, description="", tags=None, thumbnail_path=None, schedule_time=None, **kwargs):
        token = get_api_key("facebook_access_token")
        page_id = get_api_key("facebook_page_id")

        data = {"title": title, "description": description or title, "access_token": token}
        if schedule_time:
            import datetime
            dt = datetime.datetime.fromisoformat(schedule_time)
            data["scheduled_publish_time"] = str(int(dt.timestamp()))
            data["published"] = "false"

        with open(video_path, "rb") as f:
            resp = requests.post(f"{self.API_BASE}/{page_id}/videos",
                data=data, files={"source": f}, timeout=600)
        resp.raise_for_status()
        video_id = resp.json().get("id")

        return {"platform": "facebook", "video_id": video_id, "status": "published" if not schedule_time else "scheduled"}

    def get_supported_features(self): return ["upload", "schedule", "description"]
