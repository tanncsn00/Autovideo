from typing import Optional
from pydantic import BaseModel
from app.controllers.v1.base import new_router
from app.services.scheduler import ScheduleManager
from app.utils import utils

router = new_router()

_scheduler = ScheduleManager()


class ScheduleRequest(BaseModel):
    task_id: str
    platform: str
    title: str
    description: str = ""
    tags: list[str] = []
    scheduled_time: str
    timezone: str = "UTC"


@router.post("/schedule", summary="Schedule a video for publishing")
def schedule_post(body: ScheduleRequest):
    post = _scheduler.schedule_post(
        task_id=body.task_id, platform=body.platform, title=body.title,
        description=body.description, tags=body.tags,
        scheduled_time=body.scheduled_time, timezone_name=body.timezone,
    )
    return utils.get_response(200, post.to_dict())


@router.get("/schedule", summary="List scheduled posts")
def list_scheduled(status: str = None, platform: str = None):
    posts = _scheduler.list_posts(status=status, platform=platform)
    return utils.get_response(200, posts)


@router.get("/schedule/{post_id}", summary="Get scheduled post")
def get_scheduled(post_id: str):
    post = _scheduler.get_post(post_id)
    if not post:
        return utils.get_response(404, message="Post not found")
    return utils.get_response(200, post)


@router.post("/schedule/{post_id}/cancel", summary="Cancel scheduled post")
def cancel_scheduled(post_id: str):
    ok = _scheduler.cancel_post(post_id)
    if not ok:
        return utils.get_response(404, message="Post not found or already published")
    return utils.get_response(200, {"message": "Cancelled"})


@router.delete("/schedule/{post_id}", summary="Delete scheduled post")
def delete_scheduled(post_id: str):
    ok = _scheduler.delete_post(post_id)
    if not ok:
        return utils.get_response(404, message="Post not found")
    return utils.get_response(200, {"message": "Deleted"})
