import ast
import json
import sqlite3
import threading
from abc import ABC, abstractmethod

from loguru import logger

from app.config import config
from app.models import const


# Base class for state management
class BaseState(ABC):
    @abstractmethod
    def update_task(self, task_id: str, state: int, progress: int = 0, **kwargs):
        pass

    @abstractmethod
    def get_task(self, task_id: str):
        pass

    @abstractmethod
    def get_all_tasks(self, page: int, page_size: int):
        pass


# Memory state management
class MemoryState(BaseState):
    def __init__(self):
        self._tasks = {}

    def get_all_tasks(self, page: int, page_size: int):
        start = (page - 1) * page_size
        end = start + page_size
        tasks = list(self._tasks.values())
        total = len(tasks)
        return tasks[start:end], total

    def update_task(
        self,
        task_id: str,
        state: int = const.TASK_STATE_PROCESSING,
        progress: int = 0,
        **kwargs,
    ):
        progress = int(progress)
        if progress > 100:
            progress = 100

        self._tasks[task_id] = {
            "task_id": task_id,
            "state": state,
            "progress": progress,
            **kwargs,
        }

    def get_task(self, task_id: str):
        return self._tasks.get(task_id, None)

    def delete_task(self, task_id: str):
        if task_id in self._tasks:
            del self._tasks[task_id]


# Redis state management
class RedisState(BaseState):
    def __init__(self, host="localhost", port=6379, db=0, password=None):
        import redis

        self._redis = redis.StrictRedis(host=host, port=port, db=db, password=password)

    def get_all_tasks(self, page: int, page_size: int):
        start = (page - 1) * page_size
        end = start + page_size
        tasks = []
        cursor = 0
        total = 0
        while True:
            cursor, keys = self._redis.scan(cursor, count=page_size)
            total += len(keys)
            if total > start:
                for key in keys[max(0, start - total):end - total]:
                    task_data = self._redis.hgetall(key)
                    task = {
                        k.decode("utf-8"): self._convert_to_original_type(v) for k, v in task_data.items()
                    }
                    tasks.append(task)
                    if len(tasks) >= page_size:
                        break
            if cursor == 0 or len(tasks) >= page_size:
                break
        return tasks, total

    def update_task(
        self,
        task_id: str,
        state: int = const.TASK_STATE_PROCESSING,
        progress: int = 0,
        **kwargs,
    ):
        progress = int(progress)
        if progress > 100:
            progress = 100

        fields = {
            "task_id": task_id,
            "state": state,
            "progress": progress,
            **kwargs,
        }

        for field, value in fields.items():
            self._redis.hset(task_id, field, str(value))

    def get_task(self, task_id: str):
        task_data = self._redis.hgetall(task_id)
        if not task_data:
            return None

        task = {
            key.decode("utf-8"): self._convert_to_original_type(value)
            for key, value in task_data.items()
        }
        return task

    def delete_task(self, task_id: str):
        self._redis.delete(task_id)

    @staticmethod
    def _convert_to_original_type(value):
        """
        Convert the value from byte string to its original data type.
        You can extend this method to handle other data types as needed.
        """
        value_str = value.decode("utf-8")

        try:
            # try to convert byte string array to list
            return ast.literal_eval(value_str)
        except (ValueError, SyntaxError):
            pass

        if value_str.isdigit():
            return int(value_str)
        # Add more conversions here if needed
        return value_str


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    state INTEGER DEFAULT 0,
    progress REAL DEFAULT 0,
    data TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


class SQLiteState(BaseState):
    """Thread-safe SQLite state for desktop mode"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA_SQL)

    def update_task(self, task_id: str, state: int = 0, progress: float = 0, **kwargs):
        data_json = json.dumps(kwargs) if kwargs else "{}"
        with self._lock:
            self._conn.execute(
                """INSERT INTO tasks (id, state, progress, data, updated_at)
                   VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                   ON CONFLICT(id) DO UPDATE SET
                     state=excluded.state,
                     progress=excluded.progress,
                     data=excluded.data,
                     updated_at=CURRENT_TIMESTAMP""",
                (task_id, state, progress, data_json),
            )
            self._conn.commit()

    def get_task(self, task_id: str):
        with self._lock:
            row = self._conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            return None
        result = {"state": row["state"], "progress": row["progress"]}
        if row["data"]:
            result.update(json.loads(row["data"]))
        return result

    def get_all_tasks(self, page: int = 1, page_size: int = 10):
        with self._lock:
            total = self._conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
            offset = (page - 1) * page_size
            rows = self._conn.execute(
                "SELECT * FROM tasks ORDER BY updated_at DESC LIMIT ? OFFSET ?",
                (page_size, offset),
            ).fetchall()
        tasks = []
        for row in rows:
            task = {"id": row["id"], "state": row["state"], "progress": row["progress"]}
            if row["data"]:
                task.update(json.loads(row["data"]))
            tasks.append(task)
        return tasks, total

    def delete_task(self, task_id: str):
        with self._lock:
            self._conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            self._conn.commit()


# Global state - select implementation based on mode
import os as _os

def _create_state():
    """Create state instance based on running mode"""
    mode = _os.environ.get("MPT_MODE", "api")

    if mode == "desktop":
        # Desktop mode: use SQLite for persistent task history
        try:
            from app.config.config_v2 import get_config_dir
            db_path = str(get_config_dir() / "tasks.db")
            logger.info(f"Desktop mode: using SQLiteState at {db_path}")
            return SQLiteState(db_path)
        except Exception as e:
            logger.warning(f"Failed to create SQLiteState, falling back to MemoryState: {e}")
            return MemoryState()

    # API/server mode: use Redis if enabled, else MemoryState
    _enable_redis = config.app.get("enable_redis", False)
    if _enable_redis:
        _redis_host = config.app.get("redis_host", "localhost")
        _redis_port = config.app.get("redis_port", 6379)
        _redis_db = config.app.get("redis_db", 0)
        _redis_password = config.app.get("redis_password", None)
        return RedisState(
            host=_redis_host, port=_redis_port, db=_redis_db, password=_redis_password
        )

    return MemoryState()


state = _create_state()
