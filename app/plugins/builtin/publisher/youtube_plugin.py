import os
from app.plugins.base import PublisherPlugin, PluginMeta
from app.config.config import get_api_key, app
from loguru import logger


class YouTubePlugin(PublisherPlugin):

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="youtube",
            display_name="YouTube",
            version="1.0.0",
            description="Upload videos to YouTube with title, description, tags, thumbnail, and scheduling",
            author="MoneyPrinterTurbo",
            plugin_type="publisher",
            config_schema={
                "client_id": {"type": "string", "required": True},
                "client_secret": {"type": "string", "required": True},
                "refresh_token": {"type": "string", "required": True},
            },
            builtin=True,
        )

    def validate_config(self, config: dict) -> bool:
        return all(config.get(k) for k in ["client_id", "client_secret", "refresh_token"])

    def is_available(self) -> bool:
        client_id = get_api_key("youtube_client_id")
        return bool(client_id and client_id.strip())

    async def authenticate(self, credentials: dict) -> bool:
        """Authenticate using OAuth2 refresh token"""
        try:
            import requests
            resp = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": credentials.get("client_id") or get_api_key("youtube_client_id"),
                    "client_secret": credentials.get("client_secret") or get_api_key("youtube_client_secret"),
                    "refresh_token": credentials.get("refresh_token") or get_api_key("youtube_refresh_token"),
                    "grant_type": "refresh_token",
                },
                timeout=10,
            )
            return resp.status_code == 200 and "access_token" in resp.json()
        except Exception as e:
            logger.error(f"YouTube auth failed: {e}")
            return False

    def _get_access_token(self) -> str:
        """Get fresh access token from refresh token"""
        import requests
        resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": get_api_key("youtube_client_id"),
                "client_secret": get_api_key("youtube_client_secret"),
                "refresh_token": get_api_key("youtube_refresh_token"),
                "grant_type": "refresh_token",
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    async def publish(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: list[str] = None,
        thumbnail_path: str = None,
        schedule_time: str = None,
        **kwargs,
    ) -> dict:
        """Upload video to YouTube using resumable upload API"""
        import requests
        import json

        access_token = self._get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Video metadata
        privacy = "private" if schedule_time else kwargs.get("privacy", "public")
        body = {
            "snippet": {
                "title": title[:100],  # YouTube limit
                "description": description[:5000],
                "tags": tags or [],
                "categoryId": kwargs.get("category_id", "22"),  # 22 = People & Blogs
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False,
            },
        }

        if schedule_time:
            body["status"]["publishAt"] = schedule_time  # ISO 8601 format
            body["status"]["privacyStatus"] = "private"

        # Step 1: Initiate resumable upload
        init_resp = requests.post(
            "https://www.googleapis.com/upload/youtube/v3/videos"
            "?uploadType=resumable&part=snippet,status",
            headers=headers,
            json=body,
            timeout=30,
        )
        init_resp.raise_for_status()
        upload_url = init_resp.headers["Location"]

        # Step 2: Upload video file
        file_size = os.path.getsize(video_path)
        with open(video_path, "rb") as f:
            upload_resp = requests.put(
                upload_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "video/*",
                    "Content-Length": str(file_size),
                },
                data=f,
                timeout=600,
            )
        upload_resp.raise_for_status()
        video_data = upload_resp.json()
        video_id = video_data["id"]

        # Step 3: Upload thumbnail (if provided)
        if thumbnail_path and os.path.exists(thumbnail_path):
            try:
                with open(thumbnail_path, "rb") as thumb:
                    requests.post(
                        f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set"
                        f"?videoId={video_id}",
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Content-Type": "image/jpeg",
                        },
                        data=thumb,
                        timeout=30,
                    )
            except Exception as e:
                logger.warning(f"Thumbnail upload failed: {e}")

        result = {
            "platform": "youtube",
            "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "status": "published" if not schedule_time else "scheduled",
        }

        logger.info(f"YouTube upload success: {result['url']}")
        return result

    def get_supported_features(self) -> list[str]:
        return ["upload", "schedule", "thumbnail", "tags", "description", "analytics"]
