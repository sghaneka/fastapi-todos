from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Optional, Dict, Any

from rq.job import Job
from rq.exceptions import NoSuchJobError

from app.queue import get_reports_queue, get_redis_connection
from app.tasks import generate_report

router = APIRouter(prefix="/reports", tags=["reports"])


class CreateReportRequest(BaseModel):
    user_id: str
    filters: dict | None = None


@router.post("", status_code=status.HTTP_202_ACCEPTED)
def create_report(req: CreateReportRequest):
    """
    Accept a long-running job and return immediately with a job_id.
    """
    # Get our report queue
    report_queue = get_reports_queue()

    # Enqueue the RQ job – this is fast
    job: Job = report_queue.enqueue(
        generate_report,
        req.user_id,
        req.filters or {},
        # optional options:
        job_timeout=600,  # 10 mins
        retry=None,  # or Retry(max=3, interval=[10, 30, 60])
    )

    return {
        "message": "Report generation started",
        "job_id": job.id,
        "queue": job.origin,
        "enqueued_at": job.enqueued_at,
    }


@router.get("/{job_id}")
def get_report_status(job_id: str):
    """
    Check the status (and result) of a job by job_id.
    Now includes progress information from job meta!
    """
    redis_conn = get_redis_connection()

    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except NoSuchJobError:
        return {
            "job_id": job_id,
            "status": "not_found",
        }

    # RQ states: 'queued', 'started', 'finished', 'failed', 'deferred'
    status_str = job.get_status()

    response: dict = {
        "job_id": job_id,
        "status": status_str,
        "enqueued_at": job.enqueued_at,
        "started_at": job.started_at,
        "ended_at": job.ended_at,
    }

    # Add progress information from job meta
    if hasattr(job, "meta") and job.meta:
        response["progress"] = {
            "percentage": job.meta.get("progress", 0),
            "current_step": job.meta.get("current_step"),
            "total_steps": job.meta.get("total_steps"),
            "message": job.meta.get("message", ""),
            "detailed_status": job.meta.get("status", status_str),
        }

    if status_str == "finished":
        response["result"] = job.result
    elif status_str == "failed":
        # You can introspect job.exc_info for debugging (don't expose all in prod)
        response["error"] = str(job.exc_info)[:500] if job.exc_info else "Unknown error"

    return response


@router.get("/{job_id}/progress")
def get_job_progress_and_log(job_id: str):
    """
    Get job progress and also log it to FastAPI console
    Call this endpoint to see progress in your FastAPI terminal!
    """
    import logging

    logger = logging.getLogger("fastapi.background_jobs")

    redis_conn = get_redis_connection()

    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except NoSuchJobError:
        logger.warning(f"❌ Job {job_id} not found")
        return {"job_id": job_id, "status": "not_found"}

    status_str = job.get_status()

    # Build progress info
    progress_info = {
        "job_id": job_id,
        "status": status_str,
        "progress": 0,
        "message": "No progress information available",
    }

    if hasattr(job, "meta") and job.meta:
        progress_info.update(
            {
                "progress": job.meta.get("progress", 0),
                "current_step": job.meta.get("current_step"),
                "total_steps": job.meta.get("total_steps"),
                "message": job.meta.get("message", ""),
                "detailed_status": job.meta.get("status", status_str),
            }
        )

    # Log current status to FastAPI console
    if status_str == "started" and job.meta:
        progress = job.meta.get("progress", 0)
        message = job.meta.get("message", "Processing...")
        logger.info(f"🔄 Job {job_id[:8]}... - {progress}% - {message}")
    elif status_str == "finished":
        logger.info(f"✅ Job {job_id[:8]}... completed successfully!")
    elif status_str == "failed":
        logger.error(f"❌ Job {job_id[:8]}... failed")

    return progress_info


@router.get("/queue/status")
def get_queue_status():
    """
    Get status of the reports queue.
    Useful for monitoring.
    """
    report_queue = get_reports_queue()

    return {
        "queue_name": "reports",
        "length": len(report_queue),
        "is_empty": report_queue.is_empty(),
        "job_ids": report_queue.job_ids[:10],  # First 10 job IDs
    }
