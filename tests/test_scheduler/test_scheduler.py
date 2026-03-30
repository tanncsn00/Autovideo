import pytest
import tempfile
from app.services.scheduler import ScheduleManager
from datetime import datetime, timezone, timedelta


@pytest.fixture
def scheduler():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        return ScheduleManager(db_path=f.name)


def test_schedule_post(scheduler):
    post = scheduler.schedule_post("task-1", "youtube", "Test Video", scheduled_time="2026-12-31T12:00:00Z")
    assert post.status == "pending"
    assert post.platform == "youtube"


def test_list_posts(scheduler):
    scheduler.schedule_post("t1", "youtube", "V1", scheduled_time="2026-12-31T12:00:00Z")
    scheduler.schedule_post("t2", "tiktok", "V2", scheduled_time="2026-12-31T13:00:00Z")
    posts = scheduler.list_posts()
    assert len(posts) == 2


def test_list_posts_by_status(scheduler):
    scheduler.schedule_post("t1", "youtube", "V1", scheduled_time="2026-12-31T12:00:00Z")
    posts = scheduler.list_posts(status="pending")
    assert len(posts) == 1
    posts = scheduler.list_posts(status="published")
    assert len(posts) == 0


def test_cancel_post(scheduler):
    post = scheduler.schedule_post("t1", "youtube", "V1", scheduled_time="2026-12-31T12:00:00Z")
    assert scheduler.cancel_post(post.id) is True
    updated = scheduler.get_post(post.id)
    assert updated["status"] == "cancelled"


def test_cancel_nonexistent(scheduler):
    assert scheduler.cancel_post("nonexistent") is False


def test_delete_post(scheduler):
    post = scheduler.schedule_post("t1", "youtube", "V1", scheduled_time="2026-12-31T12:00:00Z")
    assert scheduler.delete_post(post.id) is True
    assert scheduler.get_post(post.id) is None


def test_get_due_posts(scheduler):
    past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    scheduler.schedule_post("t1", "youtube", "Past", scheduled_time=past)
    scheduler.schedule_post("t2", "youtube", "Future", scheduled_time=future)
    due = scheduler.get_due_posts()
    assert len(due) == 1
    assert due[0]["title"] == "Past"


def test_update_status(scheduler):
    post = scheduler.schedule_post("t1", "youtube", "V1", scheduled_time="2026-12-31T12:00:00Z")
    scheduler.update_post_status(post.id, "published", result={"url": "http://..."})
    updated = scheduler.get_post(post.id)
    assert updated["status"] == "published"
    assert updated["result"]["url"] == "http://..."
