"""Analytics — track video performance across platforms"""

import json
import sqlite3
import time
from datetime import datetime, timezone
from typing import Optional
from loguru import logger


ANALYTICS_SCHEMA = """
CREATE TABLE IF NOT EXISTS video_analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    video_url TEXT DEFAULT '',
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    watch_time_hours REAL DEFAULT 0,
    recorded_at TEXT NOT NULL,
    metadata TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS performance_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    snapshot_date TEXT NOT NULL,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    UNIQUE(task_id, platform, snapshot_date)
);
"""


class AnalyticsManager:
    """Track and query video performance metrics"""

    def __init__(self, db_path: str = None):
        if db_path:
            self._db_path = db_path
        else:
            from app.config.config_v2 import get_config_dir
            self._db_path = str(get_config_dir() / "analytics.db")
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self._db_path)
        conn.executescript(ANALYTICS_SCHEMA)
        conn.close()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def record_metrics(
        self,
        task_id: str,
        platform: str,
        views: int = 0,
        likes: int = 0,
        comments: int = 0,
        shares: int = 0,
        watch_time_hours: float = 0,
        video_url: str = "",
        metadata: dict = None,
    ):
        """Record a performance snapshot for a video"""
        conn = self._get_conn()
        now = datetime.now(timezone.utc).isoformat()
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Insert detailed record
        conn.execute(
            """INSERT INTO video_analytics
               (task_id, platform, video_url, views, likes, comments, shares, watch_time_hours, recorded_at, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (task_id, platform, video_url, views, likes, comments, shares, watch_time_hours, now, json.dumps(metadata or {})),
        )

        # Upsert daily snapshot
        conn.execute(
            """INSERT INTO performance_snapshots (task_id, platform, snapshot_date, views, likes, comments, shares)
               VALUES (?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(task_id, platform, snapshot_date) DO UPDATE SET
                 views=excluded.views, likes=excluded.likes, comments=excluded.comments, shares=excluded.shares""",
            (task_id, platform, today, views, likes, comments, shares),
        )

        conn.commit()
        conn.close()

    def get_video_metrics(self, task_id: str) -> list[dict]:
        """Get all metrics for a specific video across platforms"""
        conn = self._get_conn()
        rows = conn.execute(
            """SELECT platform, MAX(views) as views, MAX(likes) as likes,
                      MAX(comments) as comments, MAX(shares) as shares,
                      MAX(watch_time_hours) as watch_time_hours
               FROM video_analytics WHERE task_id = ? GROUP BY platform""",
            (task_id,),
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_platform_summary(self, platform: str = None) -> dict:
        """Get summary metrics, optionally filtered by platform"""
        conn = self._get_conn()
        query = """SELECT
            COUNT(DISTINCT task_id) as total_videos,
            COALESCE(SUM(views), 0) as total_views,
            COALESCE(SUM(likes), 0) as total_likes,
            COALESCE(SUM(comments), 0) as total_comments,
            COALESCE(SUM(shares), 0) as total_shares,
            COALESCE(SUM(watch_time_hours), 0) as total_watch_hours
            FROM (
                SELECT task_id, platform,
                       MAX(views) as views, MAX(likes) as likes,
                       MAX(comments) as comments, MAX(shares) as shares,
                       MAX(watch_time_hours) as watch_time_hours
                FROM video_analytics
        """
        params = []
        if platform:
            query += " WHERE platform = ?"
            params.append(platform)
        query += " GROUP BY task_id, platform)"

        row = conn.execute(query, params).fetchone()
        conn.close()

        if row:
            return dict(row)
        return {"total_videos": 0, "total_views": 0, "total_likes": 0,
                "total_comments": 0, "total_shares": 0, "total_watch_hours": 0}

    def get_top_performing(self, metric: str = "views", limit: int = 10) -> list[dict]:
        """Get top performing videos by a specific metric"""
        valid_metrics = {"views", "likes", "comments", "shares", "watch_time_hours"}
        if metric not in valid_metrics:
            metric = "views"

        conn = self._get_conn()
        rows = conn.execute(
            f"""SELECT task_id, platform, MAX({metric}) as value, MAX(video_url) as video_url
                FROM video_analytics GROUP BY task_id, platform
                ORDER BY value DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        conn.close()
        return [{"task_id": r["task_id"], "platform": r["platform"],
                 metric: r["value"], "video_url": r["video_url"]} for r in rows]

    def get_trend(self, task_id: str = None, days: int = 30) -> list[dict]:
        """Get daily performance trend"""
        conn = self._get_conn()
        query = """SELECT snapshot_date, SUM(views) as views, SUM(likes) as likes,
                          SUM(comments) as comments, SUM(shares) as shares
                   FROM performance_snapshots"""
        params = []
        if task_id:
            query += " WHERE task_id = ?"
            params.append(task_id)
        query += " GROUP BY snapshot_date ORDER BY snapshot_date DESC LIMIT ?"
        params.append(days)

        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(row) for row in reversed(rows)]

    def export_csv(self, filepath: str):
        """Export all analytics to CSV"""
        import csv
        conn = self._get_conn()
        rows = conn.execute(
            """SELECT task_id, platform, video_url, views, likes, comments, shares,
                      watch_time_hours, recorded_at
               FROM video_analytics ORDER BY recorded_at DESC"""
        ).fetchall()
        conn.close()

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["task_id", "platform", "video_url", "views", "likes",
                           "comments", "shares", "watch_time_hours", "recorded_at"])
            for row in rows:
                writer.writerow(list(row))
