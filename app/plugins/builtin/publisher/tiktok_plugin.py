import os
import requests
from app.plugins.base import PublisherPlugin, PluginMeta
from app.config.config import get_api_key
from loguru import logger


class TikTokPlugin(PublisherPlugin):

    API_BASE = "https://open.tiktokapis.com/v2"

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="tiktok", display_name="TikTok", version="1.0.0",
            description="Upload videos to TikTok with captions and hashtags",
            author="MoneyPrinterTurbo", plugin_type="publisher", builtin=True,
            config_schema={"access_token": {"type": "string", "required": True}},
        )

    def validate_config(self, config): return bool(config.get("access_token"))
    def is_available(self): return bool(get_api_key("tiktok_access_token"))

    async def authenticate(self, credentials):
        token = credentials.get("access_token") or get_api_key("tiktok_access_token")
        try:
            resp = requests.get(f"{self.API_BASE}/user/info/", headers={"Authorization": f"Bearer {token}"}, timeout=10)
            return resp.status_code == 200
        except: return False

    async def publish(self, video_path, title, description="", tags=None, thumbnail_path=None, schedule_time=None, **kwargs):
        token = get_api_key("tiktok_access_token")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        # Step 1: Init upload
        file_size = os.path.getsize(video_path)
        init_resp = requests.post(f"{self.API_BASE}/post/publish/video/init/", headers=headers, json={
            "post_info": {
                "title": f"{title} {' '.join(f'#{t}' for t in (tags or []))}",
                "privacy_level": "PUBLIC_TO_EVERYONE",
                "disable_comment": False, "disable_duet": False, "disable_stitch": False,
            },
            "source_info": {"source": "FILE_UPLOAD", "video_size": file_size, "chunk_size": file_size},
        }, timeout=30)
        init_resp.raise_for_status()
        upload_url = init_resp.json()["data"]["upload_url"]
        publish_id = init_resp.json()["data"]["publish_id"]

        # Step 2: Upload video
        with open(video_path, "rb") as f:
            upload_resp = requests.put(upload_url, headers={
                "Content-Range": f"bytes 0-{file_size-1}/{file_size}", "Content-Type": "video/mp4",
            }, data=f, timeout=600)
        upload_resp.raise_for_status()

        return {"platform": "tiktok", "publish_id": publish_id, "status": "published"}

    def get_supported_features(self): return ["upload", "tags"]
