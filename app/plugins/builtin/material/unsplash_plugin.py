import hashlib
import os
import requests
from app.plugins.base import MaterialPlugin, PluginMeta
from app.config.config import get_api_key


class UnsplashPlugin(MaterialPlugin):

    API_BASE = "https://api.unsplash.com"

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="unsplash",
            display_name="Unsplash",
            version="1.0.0",
            description="High-quality photos for Ken Burns effect video clips",
            author="MoneyPrinterTurbo",
            plugin_type="material",
            config_schema={
                "access_key": {"type": "string", "required": True},
            },
            builtin=True,
        )

    def validate_config(self, config: dict) -> bool:
        return bool(config.get("access_key"))

    def is_available(self) -> bool:
        key = get_api_key("unsplash_access_key")
        return bool(key and key.strip())

    async def search(self, query, aspect="16:9", max_results=10):
        access_key = get_api_key("unsplash_access_key")
        if not access_key:
            return []

        orientation_map = {"16:9": "landscape", "9:16": "portrait", "1:1": "squarish"}
        params = {
            "query": query,
            "per_page": max_results,
            "client_id": access_key,
        }
        orientation = orientation_map.get(aspect)
        if orientation:
            params["orientation"] = orientation

        resp = requests.get(
            f"{self.API_BASE}/search/photos",
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        for photo in data.get("results", []):
            # Use regular size for Ken Burns effect
            url = photo.get("urls", {}).get("regular", "")
            if url:
                results.append({
                    "url": url,
                    "duration": 0,  # Photos don't have duration
                    "width": photo.get("width", 0),
                    "height": photo.get("height", 0),
                    "provider": "unsplash",
                    "type": "image",  # Important: this is an image, not video
                    "description": photo.get("alt_description", ""),
                })
        return results

    async def download(self, url, output_dir):
        filename = f"img-{hashlib.md5(url.encode()).hexdigest()}.jpg"
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            return filepath
        resp = requests.get(url, stream=True, timeout=30)
        resp.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return filepath
