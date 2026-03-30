from pydantic import BaseModel
from app.controllers.v1.base import new_router
from app.services.publisher import publish_manager
from app.utils import utils

router = new_router()


@router.get("/publishers", summary="List available publishers")
def list_publishers():
    publishers = publish_manager.get_available_publishers()
    return utils.get_response(200, publishers)


class PublishRequest(BaseModel):
    task_id: str
    platforms: list[str]
    title: str
    description: str = ""
    tags: list[str] = []


@router.post("/publish", summary="Publish video to platforms")
async def publish_video(body: PublishRequest):
    from app.services import state as sm

    task = sm.state.get_task(body.task_id)
    if not task or not task.get("videos"):
        return utils.get_response(404, message="No video found for this task")

    video_path = task["videos"][0]

    results = await publish_manager.publish_to_multiple(
        platforms=body.platforms,
        video_path=video_path,
        title=body.title,
        description=body.description,
        tags=body.tags,
    )
    return utils.get_response(200, results)


@router.post("/publishers/tiktok/login", summary="Login to TikTok (opens browser)")
def tiktok_login():
    """Open browser for TikTok login. Saves cookies for auto-upload."""
    try:
        from app.plugins.builtin.publisher.tiktok_auto_plugin import TikTokAutoPlugin
        plugin = TikTokAutoPlugin()
        ok = plugin.login()
        if ok:
            return utils.get_response(200, {"message": "TikTok login successful. Cookies saved.", "connected": True})
        return utils.get_response(400, message="TikTok login failed or cancelled")
    except Exception as e:
        return utils.get_response(400, message=f"TikTok login error: {str(e)}")


@router.get("/publishers/tiktok/status", summary="Check TikTok login status")
def tiktok_status():
    """Check if TikTok cookies exist"""
    try:
        from app.plugins.builtin.publisher.tiktok_auto_plugin import TikTokAutoPlugin
        plugin = TikTokAutoPlugin()
        logged_in = plugin.is_logged_in()
        return utils.get_response(200, {"connected": logged_in})
    except Exception:
        return utils.get_response(200, {"connected": False})
