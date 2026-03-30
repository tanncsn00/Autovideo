"""Batch video production — import topic lists and generate multiple videos"""

import csv
import json
import os
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from pathlib import Path
from loguru import logger
from app.utils import utils


class BatchStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BatchItem:
    """A single item in a batch job"""
    id: str
    topic: str
    template_id: str = ""
    platform: str = "general"
    language: str = "en"
    params_override: dict = field(default_factory=dict)
    status: BatchStatus = BatchStatus.PENDING
    task_id: str = ""
    error: str = ""
    progress: float = 0


@dataclass
class BatchJob:
    """A batch production job containing multiple items"""
    id: str
    name: str
    items: list[BatchItem] = field(default_factory=list)
    status: BatchStatus = BatchStatus.PENDING
    created_at: str = ""
    max_concurrent: int = 2
    completed_count: int = 0
    failed_count: int = 0

    @property
    def total_count(self) -> int:
        return len(self.items)

    @property
    def progress(self) -> float:
        if self.total_count == 0:
            return 0
        return (self.completed_count + self.failed_count) / self.total_count * 100

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "total": self.total_count,
            "completed": self.completed_count,
            "failed": self.failed_count,
            "progress": self.progress,
            "created_at": self.created_at,
            "items": [
                {
                    "id": item.id,
                    "topic": item.topic,
                    "template_id": item.template_id,
                    "platform": item.platform,
                    "status": item.status.value,
                    "task_id": item.task_id,
                    "error": item.error,
                    "progress": item.progress,
                }
                for item in self.items
            ],
        }


class BatchProcessor:
    """Manages batch video production jobs"""

    def __init__(self):
        self._jobs: dict[str, BatchJob] = {}
        self._lock = threading.Lock()

    def create_job_from_csv(self, csv_path: str, name: str = "", max_concurrent: int = 2) -> BatchJob:
        """Create a batch job from a CSV file.

        CSV format: topic,template_id,platform,language
        """
        items = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                item = BatchItem(
                    id=utils.get_uuid(),
                    topic=row.get("topic", "").strip(),
                    template_id=row.get("template_id", row.get("template", "")).strip(),
                    platform=row.get("platform", "general").strip(),
                    language=row.get("language", "en").strip(),
                )
                if item.topic:
                    items.append(item)

        job = BatchJob(
            id=utils.get_uuid(),
            name=name or f"Batch {len(items)} videos",
            items=items,
            created_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
            max_concurrent=max_concurrent,
        )

        with self._lock:
            self._jobs[job.id] = job

        return job

    def create_job_from_list(self, topics: list[dict], name: str = "", max_concurrent: int = 2) -> BatchJob:
        """Create a batch job from a list of topic dicts.

        Each dict: {"topic": "...", "template_id": "...", "platform": "...", "language": "..."}
        """
        items = []
        for t in topics:
            item = BatchItem(
                id=utils.get_uuid(),
                topic=t.get("topic", "").strip(),
                template_id=t.get("template_id", ""),
                platform=t.get("platform", "general"),
                language=t.get("language", "en"),
                params_override=t.get("params", {}),
            )
            if item.topic:
                items.append(item)

        job = BatchJob(
            id=utils.get_uuid(),
            name=name or f"Batch {len(items)} videos",
            items=items,
            created_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
            max_concurrent=max_concurrent,
        )

        with self._lock:
            self._jobs[job.id] = job

        return job

    def start_job(self, job_id: str) -> bool:
        """Start processing a batch job in background"""
        job = self._jobs.get(job_id)
        if not job:
            return False

        job.status = BatchStatus.PROCESSING
        thread = threading.Thread(target=self._process_job, args=(job,), daemon=True)
        thread.start()
        return True

    def _process_job(self, job: BatchJob):
        """Process all items in a batch job with concurrency control"""
        from app.services import task as tm
        from app.services.template import TemplateManager
        from app.models.schema import VideoParams

        template_mgr = TemplateManager()
        semaphore = threading.Semaphore(job.max_concurrent)

        threads = []
        for item in job.items:
            if job.status == BatchStatus.CANCELLED:
                break
            semaphore.acquire()
            t = threading.Thread(
                target=self._process_item,
                args=(job, item, template_mgr, semaphore),
                daemon=True,
            )
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        if job.status != BatchStatus.CANCELLED:
            job.status = BatchStatus.COMPLETED
        logger.info(f"Batch job {job.id} finished: {job.completed_count}/{job.total_count} succeeded")

    def _process_item(self, job: BatchJob, item: BatchItem, template_mgr, semaphore):
        """Process a single batch item"""
        try:
            item.status = BatchStatus.PROCESSING

            # Build video params
            params = {}
            if item.template_id:
                try:
                    params = template_mgr.apply_template(item.template_id)
                except ValueError:
                    pass

            params["video_subject"] = item.topic
            params["video_language"] = item.language
            if item.params_override:
                params.update(item.params_override)

            # Create task
            from app.models.schema import VideoParams as VP
            task_id = utils.get_uuid()
            item.task_id = task_id

            from app.services import state as sm
            sm.state.update_task(task_id)

            from app.services import task as tm
            video_params = VP(**{k: v for k, v in params.items() if hasattr(VP, k) or k in VP.model_fields})
            tm.start(task_id=task_id, params=video_params)

            item.status = BatchStatus.COMPLETED
            item.progress = 100
            with threading.Lock():
                job.completed_count += 1

        except Exception as e:
            item.status = BatchStatus.FAILED
            item.error = str(e)
            with threading.Lock():
                job.failed_count += 1
            logger.error(f"Batch item {item.id} failed: {e}")
        finally:
            semaphore.release()

    def get_job(self, job_id: str) -> Optional[dict]:
        job = self._jobs.get(job_id)
        return job.to_dict() if job else None

    def list_jobs(self) -> list[dict]:
        return [job.to_dict() for job in self._jobs.values()]

    def cancel_job(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if job and job.status == BatchStatus.PROCESSING:
            job.status = BatchStatus.CANCELLED
            return True
        return False


# Global instance
batch_processor = BatchProcessor()
