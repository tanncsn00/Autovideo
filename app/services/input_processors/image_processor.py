"""Images to Video — create slideshow videos from uploaded images"""

import os
import glob
from dataclasses import dataclass
from loguru import logger


@dataclass
class ImageSet:
    paths: list[str]
    count: int


class ImageProcessor:
    """Convert images into video-ready material"""

    def collect_images(self, directory: str = None, paths: list[str] = None) -> ImageSet:
        """Collect images from a directory or explicit paths"""
        image_paths = []

        if paths:
            for p in paths:
                if os.path.exists(p) and self._is_image(p):
                    image_paths.append(p)

        if directory and os.path.isdir(directory):
            for ext in ["*.jpg", "*.jpeg", "*.png", "*.webp", "*.bmp"]:
                image_paths.extend(glob.glob(os.path.join(directory, ext)))

        # Sort by name for consistent ordering
        image_paths = sorted(set(image_paths))

        return ImageSet(paths=image_paths, count=len(image_paths))

    def _is_image(self, path: str) -> bool:
        return path.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"))

    async def prepare_video_params(
        self,
        image_paths: list[str],
        title: str = "Image Slideshow",
        duration_per_image: int = 5,
        template_id: str = None,
    ) -> dict:
        """Prepare VideoParams for image slideshow"""
        image_set = self.collect_images(paths=image_paths)

        if image_set.count == 0:
            raise ValueError("No valid images found")

        params = {
            "video_subject": title,
            "video_source": "local",
            "video_materials": image_set.paths,
            "video_clip_duration": duration_per_image,
            "video_concat_mode": "sequential",
            "video_transition_mode": "FadeIn",
        }

        if template_id:
            from app.services.template import TemplateManager
            mgr = TemplateManager()
            try:
                template_params = mgr.apply_template(template_id)
                template_params.update(params)
                params = template_params
            except ValueError:
                pass

        return params


image_processor = ImageProcessor()
