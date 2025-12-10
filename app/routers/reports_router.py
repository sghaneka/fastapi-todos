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

    if status_str == "finished":
        response["result"] = job.result
    elif status_str == "failed":
        # You can introspect job.exc_info for debugging (don't expose all in prod)
        response["error"] = str(job.exc_info)[:500] if job.exc_info else "Unknown error"

    return response


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
