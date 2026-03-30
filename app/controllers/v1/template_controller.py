from typing import Optional
from pydantic import BaseModel
from app.controllers.v1.base import new_router
from app.services.template import TemplateManager, TemplateConfig
from app.services.utils.video_filters import AVAILABLE_PRESETS
from app.services.animated_captions import list_caption_styles
from app.utils import utils

router = new_router()

# Global template manager
_template_manager = TemplateManager()


@router.get("/templates", summary="List all templates")
def list_templates(category: str = None, platform: str = None):
    templates = _template_manager.list_templates(category=category, platform=platform)
    return utils.get_response(200, templates)


@router.get("/templates/categories", summary="Get all template categories")
def get_categories():
    categories = _template_manager.get_categories()
    return utils.get_response(200, categories)


@router.get("/templates/{template_id}", summary="Get a specific template")
def get_template(template_id: str):
    template = _template_manager.get_template(template_id)
    if not template:
        return utils.get_response(404, message=f"Template not found: {template_id}")
    return utils.get_response(200, template.model_dump())


class ApplyTemplateRequest(BaseModel):
    template_id: str
    overrides: dict = {}


@router.post("/templates/apply", summary="Apply a template and get video params")
def apply_template(body: ApplyTemplateRequest):
    try:
        params = _template_manager.apply_template(body.template_id, body.overrides)
        return utils.get_response(200, params)
    except ValueError as e:
        return utils.get_response(404, message=str(e))


class SaveTemplateRequest(BaseModel):
    id: str
    name: str
    description: str
    category: str = "custom"
    platform: str = "general"
    video_aspect: str = "9:16"
    video_transition_mode: str = "FadeIn"
    video_clip_duration: int = 5
    voice_name: str = "en-US-AriaNeural-Female"
    voice_rate: float = 1.0
    bgm_volume: float = 0.2
    subtitle_enabled: bool = True
    subtitle_position: str = "bottom"
    font_size: int = 60
    text_fore_color: str = "#FFFFFF"
    stroke_color: str = "#000000"
    caption_style: str = "default"
    color_preset: str = "none"
    paragraph_number: int = 1
    video_language: str = "en"


@router.post("/templates", summary="Save a custom template")
def save_template(body: SaveTemplateRequest):
    template = TemplateConfig(**body.model_dump())
    filepath = _template_manager.save_custom_template(template)
    return utils.get_response(200, {"message": "Template saved", "path": filepath})


@router.get("/effects/presets", summary="List available color presets")
def list_color_presets():
    return utils.get_response(200, AVAILABLE_PRESETS)


@router.get("/effects/caption-styles", summary="List available caption styles")
def list_caption_styles_endpoint():
    return utils.get_response(200, list_caption_styles())


@router.get("/prompt-templates", summary="List all prompt templates")
def list_prompt_templates(category: str = None, language: str = None):
    from app.services.prompt_templates import get_all_templates
    results = get_all_templates()
    if category:
        results = [t for t in results if t["category"] == category]
    if language:
        results = [t for t in results if t["language"] in (language, "any")]
    return utils.get_response(200, results)


@router.get("/prompt-templates/categories", summary="List prompt template categories")
def list_prompt_categories():
    from app.services.prompt_templates import get_categories
    return utils.get_response(200, get_categories())


class SavePromptTemplateRequest(BaseModel):
    id: str = ""
    name: str
    description: str = ""
    category: str = "custom"
    prompt_prefix: str
    prompt_suffix: str = ""
    language: str = "any"
    example: str = ""


@router.post("/prompt-templates", summary="Save a custom prompt template")
def save_prompt_template(body: SavePromptTemplateRequest):
    from app.services.prompt_templates import save_custom_template
    template_id = save_custom_template(body.model_dump())
    return utils.get_response(200, {"message": "Prompt template saved", "id": template_id})


@router.delete("/prompt-templates/{template_id}", summary="Delete a custom prompt template")
def delete_prompt_template(template_id: str):
    from app.services.prompt_templates import delete_custom_template
    ok = delete_custom_template(template_id)
    if not ok:
        return utils.get_response(400, message="Cannot delete built-in template or template not found")
    return utils.get_response(200, {"message": "Deleted"})
