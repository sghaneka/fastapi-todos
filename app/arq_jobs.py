"""
Arq-based background jobs - runs in same process as FastAPI
Alternative to RQ that doesn't require separate worker processes
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from arq import create_pool
from arq.connections import RedisSettings

from app.config import get_settings

# Logger for job tracking
logger = logging.getLogger("fastapi.arq_jobs")


async def generate_report_arq(
    ctx, user_id: str, filters: dict = None
) -> Dict[str, Any]:
    """
    Arq job function - runs async in same process as FastAPI
    Similar to NestJS Bull but in Python
    """
    filters = filters or {}

    logger.info(f"🔄 Starting report generation for user {user_id} (ARQ)")
    logger.info(f"📋 Parameters: {filters}")

    # Simulate heavy async work (non-blocking!)
    total_steps = 5
    for i in range(total_steps):
        step_num = i + 1
        progress = int((step_num / total_steps) * 100)

        logger.info(f"⏳ Processing step {step_num}/{total_steps} ({progress}%)")

        # Non-blocking sleep - other jobs can run simultaneously!
        await asyncio.sleep(3)

    # Generate result
    result = {
        "status": "completed",
        "user_id": user_id,
        "filters": filters,
        "report_url": f"https://example.com/reports/{user_id}/arq-report-id",
        "generated_at": datetime.utcnow().isoformat(),
        "processing_time_seconds": 15,
        "worker_type": "arq_async",
    }

    logger.info(f"✅ Report generation completed for user {user_id} (ARQ)")
    logger.info(f"📊 Report URL: {result['report_url']}")

    return result


async def send_notification_email_arq(
    ctx, user_email: str, message: str, event_type: str
) -> Dict[str, Any]:
    """
    Async email notification job
    """
    logger.info(f"📧 Sending email to {user_email}: {event_type}")

    # Simulate email sending
    await asyncio.sleep(2)

    result = {
        "status": "sent",
        "email": user_email,
        "event_type": event_type,
        "sent_at": datetime.utcnow().isoformat(),
        "worker_type": "arq_async",
    }

    logger.info(f"✅ Email sent to {user_email}")
    return result


# Arq settings
def get_arq_settings() -> RedisSettings:
    """Get Arq Redis settings from app config"""
    settings = get_settings()
    # Simply use localhost:6379 to match docker-compose
    return RedisSettings(host="localhost", port=6379)


# Job functions registry for Arq
ARQ_FUNCTIONS = [
    generate_report_arq,
    send_notification_email_arq,
]


# Global Arq pool (will be initialized in FastAPI startup)
arq_pool = None


async def init_arq():
    """Initialize Arq connection pool"""
    global arq_pool
    try:
        arq_pool = await create_pool(get_arq_settings())
        logger.info("🚀 Arq connection pool initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Arq: {e}")
        arq_pool = None
        # Don't raise - let FastAPI start but Arq endpoints will return 500


async def close_arq():
    """Close Arq connection pool"""
    global arq_pool
    if arq_pool:
        await arq_pool.close()
        logger.info("🛑 Arq connection pool closed")
