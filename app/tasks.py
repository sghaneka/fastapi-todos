"""Background tasks for async processing"""

import time
from datetime import datetime
from typing import Dict, Any


def generate_report(user_id: str, params: dict | None = None) -> dict:
    """
    Simulate a long-running job.
    This runs inside an RQ worker, separate from FastAPI.
    """
    params = params or {}

    print(f"🔄 Starting report generation for user {user_id}...")
    print(f"📋 Parameters: {params}")

    # Simulate heavy work
    for i in range(5):
        print(f"⏳ Processing step {i+1}/5...")
        # Pretend to do some work, e.g. DB queries, API calls, etc.
        time.sleep(3)

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
