"""RQ Worker script for processing background jobs"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rq import Worker
from app.queue import get_redis_connection


def run_worker():
    """Run RQ worker to process background jobs"""
    import os

    redis_conn = get_redis_connection()

    # Listen to multiple queues (high priority first)
    queues = ["reports", "notifications", "emails", "default"]

    # Get worker name from environment or default
    worker_name = os.getenv("WORKER_NAME", f"worker-{os.getpid()}")

    print(f"🚀 Starting RQ Worker: {worker_name}")
    print(f"📋 Listening to queues: {', '.join(queues)}")
    print(f"🔗 Redis connection: {redis_conn}")

    worker = Worker(queues, connection=redis_conn, name=worker_name)
    worker.work()


if __name__ == "__main__":
    run_worker()
