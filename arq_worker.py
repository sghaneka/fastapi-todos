"""
Optional Arq worker script

Arq can run workers in the same process as FastAPI (which we do by default),
OR you can run dedicated Arq workers separately for better isolation.

This is optional - by default Arq workers run inside FastAPI process.
"""

import asyncio
import logging
from arq import create_pool, run_worker
from arq.worker import Worker

from app.arq_jobs import ARQ_FUNCTIONS, get_arq_settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("arq.worker")


class Settings:
    """Arq worker settings"""

    functions = ARQ_FUNCTIONS
    redis_settings = get_arq_settings()

    # Worker settings
    max_jobs = 10
    job_timeout = 600  # 10 minutes
    keep_result = 3600  # Keep results for 1 hour


async def main():
    """Run Arq worker"""
    logger.info("🚀 Starting dedicated Arq worker...")
    logger.info("💡 Note: By default, Arq workers run inside FastAPI process")
    logger.info("💡 This separate worker is optional for better isolation")

    await run_worker(Settings)


if __name__ == "__main__":
    asyncio.run(main())
