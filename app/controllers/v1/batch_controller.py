from typing import Optional
from pydantic import BaseModel
from app.controllers.v1.base import new_router
from app.services.batch import batch_processor
from app.utils import utils

router = new_router()


class BatchFromListRequest(BaseModel):
    topics: list[dict]
    name: str = ""
    max_concurrent: int = 2


@router.post("/batch", summary="Create batch job from topic list")
def create_batch(body: BatchFromListRequest):
    job = batch_processor.create_job_from_list(body.topics, body.name, body.max_concurrent)
    return utils.get_response(200, job.to_dict())


@router.post("/batch/{job_id}/start", summary="Start batch job")
def start_batch(job_id: str):
    ok = batch_processor.start_job(job_id)
    if not ok:
        return utils.get_response(404, message="Job not found")
    return utils.get_response(200, {"message": "Job started"})


@router.get("/batch", summary="List all batch jobs")
def list_batches():
    return utils.get_response(200, batch_processor.list_jobs())


@router.get("/batch/{job_id}", summary="Get batch job status")
def get_batch(job_id: str):
    job = batch_processor.get_job(job_id)
    if not job:
        return utils.get_response(404, message="Job not found")
    return utils.get_response(200, job)


@router.post("/batch/{job_id}/cancel", summary="Cancel batch job")
def cancel_batch(job_id: str):
    ok = batch_processor.cancel_job(job_id)
    if not ok:
        return utils.get_response(404, message="Job not found or not running")
    return utils.get_response(200, {"message": "Job cancelled"})
