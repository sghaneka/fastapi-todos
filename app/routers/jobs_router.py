from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.queue import get_reports_queue, get_redis_connection
from app.tasks import generate_report
import json

router = APIRouter(prefix="/jobs", tags=["background-jobs"])


class ReportRequest(BaseModel):
    user_id: str
    report_type: str = "user_activity"
    params: Optional[Dict[str, Any]] = None


class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str


@router.post("/reports", response_model=JobResponse)
async def queue_report_generation(request: ReportRequest):
    """
    Queue a report generation job.
    This returns immediately while the job runs in background.
    """
    reports_queue = get_reports_queue()

    # Queue the job
    job = reports_queue.enqueue(generate_report, request.user_id, request.params)

    return JobResponse(
        job_id=job.id,
        status="queued",
        message=f"Report generation queued for user {request.user_id}",
    )


@router.get("/reports/{job_id}")
async def get_job_status(job_id: str):
    """
    Check the status of a background job.
    Shows: queued, started, finished, failed
    """
    from rq import Job

    redis_conn = get_redis_connection()

    try:
        job = Job.fetch(job_id, connection=redis_conn)

        # Build response based on job status
        response = {
            "job_id": job_id,
            "status": job.get_status(),
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "ended_at": job.ended_at.isoformat() if job.ended_at else None,
        }

        # Add result if job is finished
        if job.is_finished:
            response["result"] = job.result
            response["message"] = "Job completed successfully"
        elif job.is_failed:
            response["error"] = str(job.exc_info) if job.exc_info else "Unknown error"
            response["message"] = "Job failed"
        elif job.is_started:
            response["message"] = "Job is currently running"
        else:
            response["message"] = "Job is queued"

        return response

    except Exception as e:
        return {
            "job_id": job_id,
            "status": "not_found",
            "message": f"Job not found: {str(e)}",
        }


@router.get("/queue-status")
async def get_queue_status():
    """
    Get status of all queues.
    Useful for monitoring.
    """
    redis_conn = get_redis_connection()
    reports_queue = get_reports_queue()

    from rq import Queue

    # Get all queue info
    all_queues = ["default", "notifications", "emails", "reports"]
    queue_info = {}

    for queue_name in all_queues:
        try:
            queue = Queue(queue_name, connection=redis_conn)
            queue_info[queue_name] = {
                "length": len(queue),
                "is_empty": queue.is_empty(),
                "job_ids": queue.job_ids[:5],  # First 5 job IDs
            }
        except Exception as e:
            queue_info[queue_name] = {"error": str(e)}

    return {"queues": queue_info, "redis_connected": True}
