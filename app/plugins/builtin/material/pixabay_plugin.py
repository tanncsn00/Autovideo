import hashlib
import os
import requests
from app.plugins.base import MaterialPlugin, PluginMeta
from app.config.config import get_api_key, app


class PixabayPlugin(MaterialPlugin):

    API_BASE = "https://pixabay.com/api/videos/"

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="pixabay",
            display_name="Pixabay",
            version="1.0.0",
            description="Free stock videos and images",
            author="MoneyPrinterTurbo",
            plugin_type="material",
            config_schema={
                "api_keys": {"type": "string", "required": True},
            },
            builtin=True,
        )

    def validate_config(self, config: dict) -> bool:
        return bool(config.get("api_keys"))

    def is_available(self) -> bool:
        keys = get_api_key("pixabay_api_keys")
        if not keys:
            keys_list = app.get("pixabay_api_keys", [])
            return bool(keys_list and any(k for k in keys_list))
        return bool(keys)

    def _get_api_key(self) -> str:
        keys = get_api_key("pixabay_api_keys")
        if keys and "," in keys:
            return keys.split(",")[0].strip()
        if keys:
            return keys.strip()
        keys_list = app.get("pixabay_api_keys", [])
        if keys_list:
            return keys_list[0]
        return ""

    async def search(self, query, aspect="16:9", max_results=10):
        api_key = self._get_api_key()
        if not api_key:
            return []

        params = {
            "key": api_key,
            "q": query,
            "per_page": max_results,
            "video_type": "film",
        }

        resp = requests.get(self.API_BASE, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        results = []
        for hit in data.get("hits", []):
            videos = hit.get("videos", {})
            # Prefer "large" quality, fallback to "medium"
            best = videos.get("large", videos.get("medium", {}))
            if best and best.get("url"):
                results.append({
                    "url": best["url"],
                    "duration": hit.get("duration", 0),
                    "width": best.get("width", 0),
                    "height": best.get("height", 0),
                    "provider": "pixabay",
                })
        return results

    async def download(self, url, output_dir):
        filename = f"vid-{hashlib.md5(url.encode()).hexdigest()}.mp4"
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            return filepath
        resp = requests.get(url, stream=True, timeout=60)
        resp.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return filepath
