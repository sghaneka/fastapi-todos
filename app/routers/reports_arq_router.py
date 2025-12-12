"""
Arq-based reports router - same process background jobs
Alternative to RQ that works like NestJS Bull
"""

import logging
from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from arq.jobs import Job

from app.arq_jobs import arq_pool, generate_report_arq

router = APIRouter(prefix="/reports-arq", tags=["reports-arq"])
logger = logging.getLogger("fastapi.arq_jobs")


class CreateReportRequestArq(BaseModel):
    user_id: str
    filters: dict | None = None


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_report_arq(req: CreateReportRequestArq):
    """
    Queue a report generation job using Arq (same process as FastAPI)
    Similar to NestJS Bull - workers run in same process with async concurrency
    """
    if not arq_pool:
        raise HTTPException(status_code=500, detail="Arq not initialized")

    # Enqueue job - this runs in the same process!
    job = await arq_pool.enqueue_job(
        generate_report_arq,  # Function reference (like RQ)
        req.user_id,
        req.filters or {},
        _job_timeout=600,  # 10 minutes
    )

    logger.info(f"🔄 ARQ job queued: {job.job_id} for user {req.user_id}")

    return {
        "message": "Report generation started (ARQ - same process)",
        "job_id": job.job_id,
        "worker_type": "arq_async",
        "enqueued_at": job.enqueue_time.isoformat() if job.enqueue_time else None,
    }


@router.get("/{job_id}")
async def get_report_status_arq(job_id: str):
    """
    Get ARQ job status and result
    """
    if not arq_pool:
        raise HTTPException(status_code=500, detail="Arq not initialized")

    try:
        job = Job(job_id, redis=arq_pool)

        # Get job info
        job_info = await job.info()

        if not job_info:
            return {"job_id": job_id, "status": "not_found", "worker_type": "arq_async"}

        response = {
            "job_id": job_id,
            "status": job_info.job_status.value if job_info.job_status else "unknown",
            "enqueued_at": (
                job_info.enqueue_time.isoformat() if job_info.enqueue_time else None
            ),
            "started_at": (
                job_info.start_time.isoformat() if job_info.start_time else None
            ),
            "finished_at": (
                job_info.finish_time.isoformat() if job_info.finish_time else None
            ),
            "worker_type": "arq_async",
        }

        # Add result or error
        if job_info.job_status and job_info.job_status.value == "complete":
            response["result"] = job_info.result
        elif job_info.job_status and job_info.job_status.value == "failed":
            response["error"] = (
                str(job_info.result) if job_info.result else "Job failed"
            )

        return response

    except Exception as e:
        logger.error(f"Error fetching ARQ job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching job: {e}")


@router.get("/queue/stats")
async def get_arq_queue_stats():
    """
    Get ARQ queue statistics
    """
    if not arq_pool:
        raise HTTPException(status_code=500, detail="Arq not initialized")

    try:
        # Get some basic Redis info
        info = await arq_pool.info()

        return {
            "queue_type": "arq_async",
            "redis_info": {
                "connected_clients": info.get("connected_clients"),
                "used_memory_human": info.get("used_memory_human"),
                "uptime_in_seconds": info.get("uptime_in_seconds"),
            },
            "message": "ARQ workers run in the same process as FastAPI",
        }

    except Exception as e:
        logger.error(f"Error getting ARQ stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting queue stats: {e}")
