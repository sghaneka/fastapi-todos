from contextlib import asynccontextmanager
import logging
import uvicorn

from fastapi import FastAPI

from app.config import get_settings
from app.db import init_db
from app.routers import todo_router
from app.routers import user_router
from app.routers import reports_router
from app.routers import reports_arq_router
from app.arq_jobs import init_arq, close_arq

# Configure logging to see worker job logs in FastAPI console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Console output
    ],
)

# Create logger for background jobs
logger = logging.getLogger("fastapi.background_jobs")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting up...")
    settings = get_settings()
    await init_db(settings)
    print("✅ Database initialized")

    # Initialize Arq for same-process background jobs
    await init_arq()
    print("✅ Arq background jobs initialized")

    yield

    # Shutdown
    await close_arq()
    print("🛑 Arq background jobs closed")
    print("🛑 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Todo API",
    description="A FastAPI application for managing todos with MongoDB",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(todo_router.router)
app.include_router(user_router.router)
app.include_router(reports_router.router)  # RQ-based (separate process)
app.include_router(reports_arq_router.router)  # Arq-based (same process)


# Health check endpoint for Docker
@app.get("/health")
def health_check():
    """Health check endpoint for Docker containers"""
    return {
        "status": "healthy",
        "service": "fastapi-todos",
        "timestamp": "2025-12-10T00:00:00Z",
    }


@app.get("/")
async def root():
    return {"message": "Welcome to Todo API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


def main():
    """Run the FastAPI application"""
    uvicorn.run(
        "main:app",  # Now points to app in this same file
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
