"""Background tasks for async processing"""

import time
import logging
from datetime import datetime
from typing import Dict, Any
from rq import get_current_job

# Set up logger that can be captured by FastAPI
logger = logging.getLogger("fastapi.background_jobs")


def generate_report(user_id: str, params: dict | None = None) -> dict:
    """
    Simulate a long-running job.
    This runs inside an RQ worker, separate from FastAPI.
    """
    params = params or {}

    # Get current RQ job to update its meta (status info)
    job = get_current_job()

    # Method 1: Update job meta (visible in FastAPI via job status)
    if job:
        job.meta["status"] = "starting"
        job.meta["progress"] = 0
        job.meta["message"] = f"Starting report generation for user {user_id}"
        job.save_meta()

    # Method 2: Use logger (can be configured to show in FastAPI console)
    logger.info(f"🔄 Starting report generation for user {user_id}")
    logger.info(f"📋 Parameters: {params}")

    # Method 3: Still print to worker console for debugging
    print(f"🔄 Starting report generation for user {user_id}...")
    print(f"📋 Parameters: {params}")

    # Simulate heavy work with progress updates
    total_steps = 5
    for i in range(total_steps):
        step_num = i + 1
        progress = int((step_num / total_steps) * 100)

        # Update job progress that FastAPI can read
        if job:
            job.meta["status"] = "processing"
            job.meta["progress"] = progress
            job.meta["current_step"] = step_num
            job.meta["total_steps"] = total_steps
            job.meta["message"] = f"Processing step {step_num}/{total_steps}..."
            job.save_meta()

        # Log progress (visible in FastAPI if logging configured)
        logger.info(f"⏳ Processing step {step_num}/{total_steps} ({progress}%)")

        # Worker console output
        print(f"⏳ Processing step {step_num}/{total_steps}...")

        # Pretend to do some work
        time.sleep(3)

    # Final status update
    if job:
        job.meta["status"] = "finalizing"
        job.meta["progress"] = 95
        job.meta["message"] = "Finalizing report..."
        job.save_meta()

    # In a real app, you'd generate some artifact and store it (S3, DB, etc.)
    report_url = f"https://example.com/reports/{user_id}/some-report-id"

    result = {
        "status": "completed",
        "user_id": user_id,
        "params": params,
        "report_url": report_url,
        "generated_at": datetime.utcnow().isoformat(),
        "processing_time_seconds": 15,
    }

    # Final completion update
    if job:
        job.meta["status"] = "completed"
        job.meta["progress"] = 100
        job.meta["message"] = f"Report generation completed! URL: {report_url}"
        job.save_meta()

    logger.info(f"✅ Report generation completed for user {user_id}")
    logger.info(f"📊 Report URL: {report_url}")

    print(f"✅ Report generation completed for user {user_id}")
    print(f"📊 Report URL: {report_url}")

    # Whatever you return here will be accessible as job.result
    return result


def send_notification_email(
    user_email: str, message: str, event_type: str
) -> Dict[str, Any]:
    """
    Background task to send notification email
    This would integrate with actual email service in production
    """
    print(f"🔄 Processing email job...")
    print(f"📧 Sending notification to: {user_email}")
    print(f"📩 Message: {message}")
    print(f"🏷️  Event: {event_type}")

    # Simulate email sending delay
    time.sleep(2)

    result = {
        "status": "sent",
        "recipient": user_email,
        "message": message,
        "event_type": event_type,
        "sent_at": datetime.utcnow().isoformat(),
        "provider": "mock_email_service",
    }

    print(f"✅ Email sent successfully to {user_email}")
    return result


def process_todo_completion_analytics(
    user_id: str, todo_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Background task to process todo completion for analytics
    """
    print(f"🔄 Processing analytics for user {user_id}...")
    print(f"📊 Todo data: {todo_data}")

    # Simulate analytics processing
    time.sleep(1)

    result = {
        "status": "processed",
        "user_id": user_id,
        "todo_id": todo_data.get("id"),
        "completed_at": todo_data.get("completed_at"),
        "processing_time": 1.0,
        "analytics_updated": True,
    }

    print(f"✅ Analytics processed for user {user_id}")
    return result


def cleanup_old_notifications(days_old: int = 30) -> Dict[str, Any]:
    """
    Background task to clean up old notifications
    """
    print(f"🧹 Cleaning up notifications older than {days_old} days...")

    # Simulate cleanup process
    time.sleep(3)

    # In real implementation, this would call NotificationService
    deleted_count = 42  # Mock number

    result = {
        "status": "completed",
        "deleted_count": deleted_count,
        "days_old": days_old,
        "processed_at": datetime.utcnow().isoformat(),
    }

    print(f"✅ Cleanup completed. Deleted {deleted_count} old notifications")
    return result


def send_welcome_email(user_email: str, username: str) -> Dict[str, Any]:
    """
    Background task to send welcome email to new users
    """
    print(f"🔄 Sending welcome email to new user...")
    print(f"📧 Email: {user_email}")
    print(f"👤 Username: {username}")

    # Simulate email sending
    time.sleep(1.5)

    result = {
        "status": "sent",
        "recipient": user_email,
        "username": username,
        "email_type": "welcome",
        "sent_at": datetime.utcnow().isoformat(),
    }

    print(f"✅ Welcome email sent to {username} ({user_email})")
    return result
