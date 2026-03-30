import os
import requests
from app.plugins.base import PublisherPlugin, PluginMeta
from app.config.config import get_api_key
from loguru import logger


class LinkedInPlugin(PublisherPlugin):

    API_BASE = "https://api.linkedin.com/v2"

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="linkedin", display_name="LinkedIn", version="1.0.0",
            description="Share videos on LinkedIn with professional context",
            author="MoneyPrinterTurbo", plugin_type="publisher", builtin=True,
            config_schema={"access_token": {"type": "string"}, "person_urn": {"type": "string"}},
        )

    def validate_config(self, config): return bool(config.get("access_token"))
    def is_available(self): return bool(get_api_key("linkedin_access_token"))

    async def authenticate(self, credentials):
        token = credentials.get("access_token") or get_api_key("linkedin_access_token")
        try:
            resp = requests.get(f"{self.API_BASE}/userinfo", headers={"Authorization": f"Bearer {token}"}, timeout=10)
            return resp.status_code == 200
        except: return False

    async def publish(self, video_path, title, description="", tags=None, thumbnail_path=None, schedule_time=None, **kwargs):
        token = get_api_key("linkedin_access_token")
        person_urn = get_api_key("linkedin_person_urn")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        # Step 1: Register upload
        reg_resp = requests.post(f"{self.API_BASE}/assets?action=registerUpload", headers=headers, json={
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-video"],
                "owner": f"urn:li:person:{person_urn}",
                "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}],
            }
        }, timeout=30)
        reg_resp.raise_for_status()
        reg_data = reg_resp.json()
        upload_url = reg_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
        asset = reg_data["value"]["asset"]

        # Step 2: Upload video
        with open(video_path, "rb") as f:
            requests.put(upload_url, headers={"Authorization": f"Bearer {token}"}, data=f, timeout=600)

        # Step 3: Create post
        text = f"{title}\n\n{description}" if description else title
        if tags: text += "\n" + " ".join(f"#{t}" for t in tags)

        post_resp = requests.post(f"{self.API_BASE}/ugcPosts", headers=headers, json={
            "author": f"urn:li:person:{person_urn}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "VIDEO",
                    "media": [{"status": "READY", "media": asset, "title": {"text": title}}],
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }, timeout=30)
        post_resp.raise_for_status()

        return {"platform": "linkedin", "post_id": post_resp.json().get("id", ""), "status": "published"}

    def get_supported_features(self): return ["upload", "description", "tags"]
