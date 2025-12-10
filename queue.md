# Queue Systems: NestJS Bull vs Python RQ

A comparison of background job processing between NestJS Bull (Redis-based) and Python RQ (Redis Queue) for handling long-running tasks.

## Overview

Both systems solve the same problem: **how to handle time-consuming operations without blocking your API responses**. Instead of making users wait 15+ seconds for a report to generate, you queue the work and return immediately.

## Key Process Architecture Difference

**🔴 MAJOR DIFFERENCE**: How workers run

- **Python RQ**: Workers run in **separate processes** - you manually start `python worker.py` in another terminal
- **NestJS Bull**: Workers run in **the same process** as your API - they start automatically when your app starts

## ⚡ Threading & Blocking Behavior

### NestJS Bull (Same Process, Non-Blocking)

- ✅ **Safe**: Workers use `async/await` and non-blocking operations
- ✅ **Non-blocking**: `setTimeout()`, `Promise.resolve()`, database calls with async
- ❌ **Would block API**: Synchronous operations like `Thread.sleep()` or CPU-intensive loops
- 🔄 **Event Loop**: Uses Node.js event loop to handle concurrency

### Python RQ (Separate Process, Blocking OK)

- ✅ **Safe**: Workers can use blocking operations like `time.sleep()`
- ✅ **Isolated**: Worker blocks don't affect the API process
- 🔄 **Process isolation**: Complete separation between API and worker processes

## Architecture Comparison

### NestJS Bull Queue Architecture (Same Process)

```
Terminal 1:
npm start
├── FastAPI Server (Express)
├── Bull Workers (same process) ← Workers start automatically
└── All running together

API Request → Controller → Queue Job → Immediate Response (202)
                    ↓
               Redis Queue
                    ↓
          Bull Worker (same process) → Process Job → Update Job Status
```

### Python RQ Architecture (Separate Process)

```
Terminal 1:                    Terminal 2:
uv run python main.py          uv run python worker.py
└── FastAPI Server             └── RQ Worker Process

API Request → Router → Queue Job → Immediate Response (202)
                 ↓
            Redis Queue
                 ↓
          RQ Worker (separate process) → Process Job → Update Job Status
```

## Implementation Comparison

### NestJS Bull Implementation

**Setup Dependencies:**

```bash
npm install @nestjs/bull bull
npm install @types/bull
```

**Queue Module:**

```typescript
// app.module.ts
import { BullModule } from "@nestjs/bull";

@Module({
  imports: [
    BullModule.forRoot({
      redis: {
        host: "localhost",
        port: 6379,
      },
    }),
    BullModule.registerQueue({
      name: "reports",
    }),
  ],
})
export class AppModule {}
```

**Job Processor:**

```typescript
// reports.processor.ts
import { Process, Processor } from "@nestjs/bull";
import { Job } from "bull";

@Processor("reports")
export class ReportsProcessor {
  @Process("generateReport")
  async handleReportGeneration(job: Job) {
    const { userId, filters } = job.data;

    // ✅ NON-BLOCKING: Uses async/await with setTimeout
    // This does NOT block the main API thread!
    for (let i = 0; i < 5; i++) {
      console.log(`Processing step ${i + 1}/5...`);
      await new Promise((resolve) => setTimeout(resolve, 3000));
    }

    // ❌ WOULD BLOCK: If you did this instead:
    // for (let i = 0; i < 5; i++) {
    //   console.log(`Processing step ${i + 1}/5...`);
    //   Thread.sleep(3000); // This would block the entire API!
    // }

    return {
      status: "completed",
      userId,
      filters,
      reportUrl: `https://example.com/reports/${userId}/report-id`,
      generatedAt: new Date().toISOString(),
    };
  }
}
```

**Controller:**

```typescript
// reports.controller.ts
import { InjectQueue } from "@nestjs/bull";
import { Queue } from "bull";

@Controller("reports")
export class ReportsController {
  constructor(@InjectQueue("reports") private reportsQueue: Queue) {}

  @Post()
  async createReport(@Body() createReportRequest: CreateReportRequest) {
    const job = await this.reportsQueue.add(
      "generateReport",
      {
        userId: createReportRequest.userId,
        filters: createReportRequest.filters || {},
      },
      {
        removeOnComplete: 10, // Keep last 10 completed jobs
        removeOnFail: 5, // Keep last 5 failed jobs
        attempts: 3, // Retry up to 3 times
        backoff: "exponential", // Exponential backoff on retry
      }
    );

    return {
      message: "Report generation started",
      jobId: job.id,
      queue: "reports",
      enqueuedAt: job.timestamp,
    };
  }

  @Get(":jobId")
  async getReportStatus(@Param("jobId") jobId: string) {
    const job = await this.reportsQueue.getJob(jobId);

    if (!job) {
      return { jobId, status: "not_found" };
    }

    const state = await job.getState();

    return {
      jobId,
      status: state,
      enqueuedAt: job.timestamp,
      processedOn: job.processedOn,
      finishedOn: job.finishedOn,
      result: job.returnvalue,
      failedReason: job.failedReason,
    };
  }
}
```

### Python RQ Implementation

**Setup Dependencies:**

```bash
pip install rq redis
# or
uv add rq redis
```

**Queue Setup:**

```python
# app/queue.py
import redis
from rq import Queue
from app.config import get_settings

def get_redis_connection():
    """Get Redis connection from settings"""
    settings = get_settings()
    return redis.from_url(settings.redis_url)

def get_reports_queue():
    """Get reports-specific queue for long-running jobs"""
    redis_conn = get_redis_connection()
    return Queue('reports', connection=redis_conn, default_timeout='30m')
```

**Job Function:**

```python
# app/tasks.py
import time
from datetime import datetime

def generate_report(user_id: str, filters: dict = None) -> dict:
    """
    Simulate a long-running job.
    This runs inside an RQ worker, separate from FastAPI.
    """
    filters = filters or {}

    print(f"🔄 Starting report generation for user {user_id}...")

    # ✅ BLOCKING IS OK: This runs in separate worker process
    # So it's safe to use time.sleep() here
    for i in range(5):
        print(f"⏳ Processing step {i+1}/5...")
        time.sleep(3)  # This blocks the worker, NOT the API

    result = {
        "status": "completed",
        "user_id": user_id,
        "filters": filters,
        "report_url": f"https://example.com/reports/{user_id}/report-id",
        "generated_at": datetime.utcnow().isoformat()
    }

    return result
```

**Router:**

```python
# app/routers/reports_router.py
from fastapi import APIRouter, status
from pydantic import BaseModel
from rq.job import Job
from rq.exceptions import NoSuchJobError

from app.queue import get_reports_queue, get_redis_connection
from app.tasks import generate_report

router = APIRouter(prefix="/reports", tags=["reports"])

class CreateReportRequest(BaseModel):
    user_id: str
    filters: dict | None = None

@router.post("", status_code=status.HTTP_202_ACCEPTED)
def create_report(req: CreateReportRequest):
    """Accept a long-running job and return immediately with a job_id."""
    report_queue = get_reports_queue()

    job: Job = report_queue.enqueue(
        generate_report,
        req.user_id,
        req.filters or {},
        job_timeout=600,  # 10 mins
        retry=None,
    )

    return {
        "message": "Report generation started",
        "job_id": job.id,
        "queue": job.origin,
        "enqueued_at": job.enqueued_at,
    }

@router.get("/{job_id}")
def get_report_status(job_id: str):
    """Check the status (and result) of a job by job_id."""
    redis_conn = get_redis_connection()

    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except NoSuchJobError:
        return {"job_id": job_id, "status": "not_found"}

    status_str = job.get_status()

    response = {
        "job_id": job_id,
        "status": status_str,
        "enqueued_at": job.enqueued_at,
        "started_at": job.started_at,
        "ended_at": job.ended_at,
    }

    if status_str == "finished":
        response["result"] = job.result
    elif status_str == "failed":
        response["error"] = str(job.exc_info)[:500] if job.exc_info else "Unknown error"

    return response
```

**Worker Process (SEPARATE PROCESS REQUIRED):**

```python
# worker.py - Must run in separate terminal/process!
from rq import Worker
from app.queue import get_redis_connection

def run_worker():
    """Run RQ worker to process background jobs"""
    redis_conn = get_redis_connection()
    queues = ["reports", "notifications", "emails", "default"]

    print(f"🚀 Starting RQ Worker...")
    print(f"📋 Listening to queues: {', '.join(queues)}")

    worker = Worker(queues, connection=redis_conn)
    worker.work()

if __name__ == '__main__':
    run_worker()
```

## Key Differences

| Feature                | NestJS Bull                      | Python RQ                       |
| ---------------------- | -------------------------------- | ------------------------------- |
| **🔴 Process Model**   | **Same process as API**          | **Separate worker process**     |
| **Worker Startup**     | **Automatic with app**           | **Manual (`python worker.py`)** |
| **Setup Complexity**   | Medium (decorators, DI)          | Simple (functions, imports)     |
| **Job Definition**     | Class methods with decorators    | Plain functions                 |
| **Retry Logic**        | Built-in with backoff strategies | Basic retry support             |
| **Job Priorities**     | Yes (priority queue)             | Yes (multiple queues)           |
| **Scheduled Jobs**     | Yes (cron, delay)                | Via `rq-scheduler`              |
| **Web UI**             | Bull Dashboard                   | RQ Dashboard                    |
| **Job Cleanup**        | Automatic                        | Manual configuration            |
| **TypeScript Support** | Native                           | N/A                             |
| **Monitoring**         | Rich (Bull Board)                | Basic (RQ Dashboard)            |
| **Production Setup**   | Single deployment                | Multiple processes needed       |

## Running the Systems

### NestJS Bull (Same Process)

**Start the application:**

```bash
npm run start:dev  # Workers start automatically!
```

Workers start automatically with the application - no separate process needed.

**Queue a job:**

```bash
POST /reports
{
  "userId": "user123",
  "filters": {"include_analytics": true}
}
```

### Python RQ (Separate Process)

**❗ REQUIRES TWO TERMINALS:**

**Terminal 1 - Start the API:**

```bash
uv run python main.py
```

**Terminal 2 - Start the worker (REQUIRED!):**

```bash
uv run python worker.py  # Must run this or jobs won't process!
```

**Queue a job:**

```bash
POST /reports
{
  "user_id": "user123",
  "filters": {"include_analytics": true}
}
```

## Common Usage Patterns

### Both Systems Support

1. **Immediate Response Pattern**

   - API returns 202 Accepted immediately
   - Client polls for job status
   - Job runs asynchronously

2. **Job Status Tracking**

   - queued → started → finished/failed
   - Timestamps for each state
   - Error information for failed jobs

3. **Redis-Based Storage**
   - Jobs persisted in Redis
   - Survive worker restarts
   - Distributed worker support

### Example API Flow

```bash
# 1. Queue the job
curl -X POST /reports \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "filters": {"type": "monthly"}}'

# Response (immediate):
{
  "message": "Report generation started",
  "job_id": "abc-123-def",
  "enqueued_at": "2025-12-10T10:00:00"
}

# 2. Check status (poll every few seconds)
curl /reports/abc-123-def

# Response (while running):
{
  "job_id": "abc-123-def",
  "status": "started",
  "started_at": "2025-12-10T10:00:05"
}

# Response (completed):
{
  "job_id": "abc-123-def",
  "status": "finished",
  "result": {
    "status": "completed",
    "report_url": "https://example.com/reports/user123/report-id"
  }
}
```

## When to Choose Which

### Choose NestJS Bull When:

- ✅ Already using NestJS ecosystem
- ✅ Need advanced retry strategies
- ✅ Want automatic worker management
- ✅ Prefer TypeScript throughout
- ✅ Need rich monitoring/dashboard
- ✅ Complex job dependencies

### Choose Python RQ When:

- ✅ Simplicity is preferred
- ✅ Using Python/FastAPI stack
- ✅ Want explicit worker control
- ✅ Minimal configuration needed
- ✅ Job functions are standalone
- ✅ Quick prototyping/learning

Both systems are excellent for handling background jobs. NestJS Bull offers more enterprise features out of the box, while Python RQ provides simplicity and explicit control. The choice often comes down to your existing stack and complexity requirements.
