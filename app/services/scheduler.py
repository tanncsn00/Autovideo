"""Content scheduling — queue videos for timed publishing"""

import json
import sqlite3
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from loguru import logger
from app.utils import utils


@dataclass
class ScheduledPost:
    """A scheduled publishing job"""
    id: str
    task_id: str  # Reference to the video generation task
    platform: str  # youtube, tiktok, instagram, etc.
    title: str
    description: str = ""
    tags: str = ""  # comma-separated
    scheduled_time: str = ""  # ISO 8601 format
    timezone_name: str = "UTC"
    status: str = "pending"  # pending, publishing, published, failed
    result: str = ""  # JSON string with publish result
    error: str = ""
    created_at: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "platform": self.platform,
            "title": self.title,
            "description": self.description,
            "tags": self.tags.split(",") if self.tags else [],
            "scheduled_time": self.scheduled_time,
            "timezone": self.timezone_name,
            "status": self.status,
            "result": json.loads(self.result) if self.result else {},
            "error": self.error,
            "created_at": self.created_at,
        }


SCHEDULER_SCHEMA = """
CREATE TABLE IF NOT EXISTS scheduled_posts (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    tags TEXT DEFAULT '',
    scheduled_time TEXT NOT NULL,
    timezone_name TEXT DEFAULT 'UTC',
    status TEXT DEFAULT 'pending',
    result TEXT DEFAULT '',
    error TEXT DEFAULT '',
    created_at TEXT DEFAULT ''
);
"""


class ScheduleManager:
    """Manages scheduled video publishing"""

    def __init__(self, db_path: str = None):
        if db_path:
            self._db_path = db_path
        else:
            from app.config.config_v2 import get_config_dir
            self._db_path = str(get_config_dir() / "scheduler.db")
        self._init_db()
        self._running = False
        self._thread = None

    def _init_db(self):
        conn = sqlite3.connect(self._db_path)
        conn.executescript(SCHEDULER_SCHEMA)
        conn.close()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        # Ensure table exists (handles DB deleted/recreated)
        conn.executescript(SCHEDULER_SCHEMA)
        return conn

    def schedule_post(
        self,
        task_id: str,
        platform: str,
        title: str,
        description: str = "",
        tags: list[str] = None,
        scheduled_time: str = "",
        timezone_name: str = "UTC",
    ) -> ScheduledPost:
        """Schedule a video for publishing"""
        post = ScheduledPost(
            id=utils.get_uuid(),
            task_id=task_id,
            platform=platform,
            title=title,
            description=description,
            tags=",".join(tags) if tags else "",
            scheduled_time=scheduled_time,
            timezone_name=timezone_name,
            status="pending",
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        conn = self._get_conn()
        conn.execute(
            """INSERT INTO scheduled_posts
               (id, task_id, platform, title, description, tags, scheduled_time, timezone_name, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (post.id, post.task_id, post.platform, post.title, post.description,
             post.tags, post.scheduled_time, post.timezone_name, post.status, post.created_at),
        )
        conn.commit()
        conn.close()

        logger.info(f"Scheduled post {post.id} for {platform} at {scheduled_time}")
        return post

    def get_post(self, post_id: str) -> Optional[dict]:
        conn = self._get_conn()
        row = conn.execute("SELECT * FROM scheduled_posts WHERE id = ?", (post_id,)).fetchone()
        conn.close()
        if row:
            return ScheduledPost(**dict(row)).to_dict()
        return None

    def list_posts(self, status: str = None, platform: str = None) -> list[dict]:
        conn = self._get_conn()
        query = "SELECT * FROM scheduled_posts"
        params = []
        conditions = []
        if status:
            conditions.append("status = ?")
            params.append(status)
        if platform:
            conditions.append("platform = ?")
            params.append(platform)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY scheduled_time ASC"

        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [ScheduledPost(**dict(row)).to_dict() for row in rows]

    def cancel_post(self, post_id: str) -> bool:
        conn = self._get_conn()
        result = conn.execute(
            "UPDATE scheduled_posts SET status = 'cancelled' WHERE id = ? AND status = 'pending'",
            (post_id,),
        )
        conn.commit()
        affected = result.rowcount
        conn.close()
        return affected > 0

    def delete_post(self, post_id: str) -> bool:
        conn = self._get_conn()
        result = conn.execute("DELETE FROM scheduled_posts WHERE id = ?", (post_id,))
        conn.commit()
        affected = result.rowcount
        conn.close()
        return affected > 0

    def get_due_posts(self) -> list[dict]:
        """Get posts that are due for publishing (scheduled_time <= now)"""
        # Use local time since frontend sends local datetime
        now = datetime.now().strftime("%Y-%m-%dT%H:%M")
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM scheduled_posts WHERE status = 'pending' AND scheduled_time <= ? ORDER BY scheduled_time ASC",
            (now,),
        ).fetchall()
        conn.close()
        return [ScheduledPost(**dict(row)).to_dict() for row in rows]

    def update_post_status(self, post_id: str, status: str, result: dict = None, error: str = ""):
        conn = self._get_conn()
        conn.execute(
            "UPDATE scheduled_posts SET status = ?, result = ?, error = ? WHERE id = ?",
            (status, json.dumps(result or {}), error, post_id),
        )
        conn.commit()
        conn.close()

    def start_scheduler(self, interval: int = 60):
        """Start background scheduler thread that checks for due posts"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._scheduler_loop, args=(interval,), daemon=True)
        self._thread.start()
        logger.info(f"Scheduler started (check interval: {interval}s)")

    def stop_scheduler(self):
        self._running = False

    def _scheduler_loop(self, interval: int):
        """Background loop that processes due posts"""
        while self._running:
            try:
                due_posts = self.get_due_posts()
                for post in due_posts:
                    self._publish_post(post)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
            time.sleep(interval)

    def _publish_post(self, post: dict):
        """Publish a single scheduled post"""
        post_id = post["id"]
        platform = post["platform"]

        try:
            self.update_post_status(post_id, "publishing")

            from app.services.publisher import publish_manager
            from app.plugins.utils import run_async
            from app.services import state as sm

            # Get video path from task
            task = sm.state.get_task(post["task_id"])
            if not task or not task.get("videos"):
                raise ValueError(f"No video found for task {post['task_id']}")

            video_path = task["videos"][0]

            result = run_async(publish_manager.publish_to_platform(
                platform=platform,
                video_path=video_path,
                title=post["title"],
                description=post["description"],
                tags=post["tags"],
            ))

            self.update_post_status(post_id, "published", result=result)
            logger.info(f"Scheduled post {post_id} published to {platform}")

        except Exception as e:
            self.update_post_status(post_id, "failed", error=str(e))
            logger.error(f"Scheduled post {post_id} failed: {e}")
