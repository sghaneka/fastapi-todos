from contextlib import asynccontextmanager
import uvicorn

from fastapi import FastAPI

from app.config import get_settings
from app.db import init_db
from app.routers import todo_router
from app.routers import user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting up...")
    settings = get_settings()
    await init_db(settings)
    print("✅ Database initialized")
    yield
    # Shutdown - add cleanup code here if needed
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
