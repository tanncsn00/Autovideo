import hashlib
import os

import requests
from app.plugins.base import MaterialPlugin, PluginMeta
from app.config.config import get_api_key, app


class PexelsPlugin(MaterialPlugin):

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="pexels",
            display_name="Pexels",
            version="1.0.0",
            description="Free stock video and photo library",
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
        keys = get_api_key("pexels_api_keys")
        if not keys:
            # Also check the list format from config
            keys_list = app.get("pexels_api_keys", [])
            return bool(keys_list and any(k for k in keys_list))
        return bool(keys)

    def _get_api_key(self) -> str:
        keys = get_api_key("pexels_api_keys")
        if keys and "," in keys:
            return keys.split(",")[0].strip()
        if keys:
            return keys.strip()
        keys_list = app.get("pexels_api_keys", [])
        if keys_list:
            return keys_list[0]
        return ""

    async def search(self, query, aspect="16:9", max_results=10):
        api_key = self._get_api_key()
        if not api_key:
            return []

        orientation_map = {"16:9": "landscape", "9:16": "portrait", "1:1": "square"}
        params = {"query": query, "per_page": max_results}
        orientation = orientation_map.get(aspect)
        if orientation:
            params["orientation"] = orientation

        headers = {"Authorization": api_key}
        resp = requests.get(
            "https://api.pexels.com/videos/search",
            headers=headers,
            params=params,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        for video in data.get("videos", []):
            files = video.get("video_files", [])
            best = max(files, key=lambda f: f.get("width", 0), default=None)
            if best:
                results.append({
                    "url": best.get("link", ""),
                    "duration": video.get("duration", 0),
                    "width": best.get("width", 0),
                    "height": best.get("height", 0),
                    "provider": "pexels",
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
