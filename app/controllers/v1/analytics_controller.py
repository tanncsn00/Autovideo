from app.controllers.v1.base import new_router
from app.services.analytics import AnalyticsManager
from app.utils import utils
from pydantic import BaseModel

router = new_router()

_analytics = AnalyticsManager()


class RecordMetricsRequest(BaseModel):
    task_id: str
    platform: str
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    watch_time_hours: float = 0
    video_url: str = ""


@router.post("/analytics/record", summary="Record video metrics")
def record_metrics(body: RecordMetricsRequest):
    _analytics.record_metrics(**body.model_dump())
    return utils.get_response(200, {"message": "Metrics recorded"})


@router.get("/analytics/video/{task_id}", summary="Get metrics for a video")
def get_video_metrics(task_id: str):
    metrics = _analytics.get_video_metrics(task_id)
    return utils.get_response(200, metrics)


@router.get("/analytics/summary", summary="Get platform summary")
def get_summary(platform: str = None):
    summary = _analytics.get_platform_summary(platform)
    return utils.get_response(200, summary)


@router.get("/analytics/top", summary="Get top performing videos")
def get_top(metric: str = "views", limit: int = 10):
    top = _analytics.get_top_performing(metric, limit)
    return utils.get_response(200, top)


@router.get("/analytics/trend", summary="Get performance trend")
def get_trend(task_id: str = None, days: int = 30):
    trend = _analytics.get_trend(task_id, days)
    return utils.get_response(200, trend)
