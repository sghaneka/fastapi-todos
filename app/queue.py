"""Redis Queue setup and configuration"""

import redis
from rq import Queue
from app.config import get_settings


# Redis connection
def get_redis_connection():
    """Get Redis connection from settings"""
    settings = get_settings()
    return redis.from_url(settings.redis_url)


# RQ Queues
def get_default_queue():
    """Get default RQ queue"""
    redis_conn = get_redis_connection()
    return Queue("default", connection=redis_conn)


def get_notification_queue():
    """Get notification-specific queue"""
    redis_conn = get_redis_connection()
    return Queue("notifications", connection=redis_conn)


def get_email_queue():
    """Get email-specific queue"""
    redis_conn = get_redis_connection()
    return Queue("emails", connection=redis_conn)


def get_reports_queue():
    """Get reports-specific queue for long-running jobs"""
    redis_conn = get_redis_connection()
    return Queue(
        "reports", connection=redis_conn, default_timeout="30m"
    )  # 30 minute timeout
