import pytest
import tempfile
from app.services.analytics import AnalyticsManager


@pytest.fixture
def analytics():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        return AnalyticsManager(db_path=f.name)


def test_record_and_get(analytics):
    analytics.record_metrics("task-1", "youtube", views=100, likes=10)
    metrics = analytics.get_video_metrics("task-1")
    assert len(metrics) == 1
    assert metrics[0]["views"] == 100
    assert metrics[0]["likes"] == 10


def test_multiple_platforms(analytics):
    analytics.record_metrics("task-1", "youtube", views=100)
    analytics.record_metrics("task-1", "tiktok", views=500)
    metrics = analytics.get_video_metrics("task-1")
    assert len(metrics) == 2


def test_platform_summary(analytics):
    analytics.record_metrics("task-1", "youtube", views=100, likes=10)
    analytics.record_metrics("task-2", "youtube", views=200, likes=20)
    summary = analytics.get_platform_summary("youtube")
    assert summary["total_videos"] == 2
    assert summary["total_views"] == 300
    assert summary["total_likes"] == 30


def test_overall_summary(analytics):
    analytics.record_metrics("task-1", "youtube", views=100)
    analytics.record_metrics("task-2", "tiktok", views=500)
    summary = analytics.get_platform_summary()
    assert summary["total_views"] == 600


def test_top_performing(analytics):
    analytics.record_metrics("task-1", "youtube", views=100)
    analytics.record_metrics("task-2", "youtube", views=500)
    analytics.record_metrics("task-3", "youtube", views=50)
    top = analytics.get_top_performing("views", limit=2)
    assert len(top) == 2
    assert top[0]["views"] == 500


def test_empty_analytics(analytics):
    summary = analytics.get_platform_summary()
    assert summary["total_views"] == 0
    assert summary["total_videos"] == 0


def test_trend(analytics):
    analytics.record_metrics("task-1", "youtube", views=100)
    trend = analytics.get_trend(days=7)
    assert len(trend) >= 1


def test_export_csv(analytics, tmp_path):
    analytics.record_metrics("task-1", "youtube", views=100)
    csv_path = str(tmp_path / "export.csv")
    analytics.export_csv(csv_path)
    with open(csv_path) as f:
        content = f.read()
    assert "task-1" in content
    assert "youtube" in content
