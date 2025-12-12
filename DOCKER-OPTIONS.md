# Docker Deployment Options

This document shows the different ways to run the FastAPI Todo application in containers.

## 🐋 Container Deployment Options

### 1. **FastAPI + RQ Workers (Same Container)** - Default

```bash
# Uses start.sh to run FastAPI + 3 RQ workers in one container
docker build -t fastapi-todos .
docker run -p 8000:8000 --env-file .env.production fastapi-todos

# Or override the command explicitly:
docker run -p 8000:8000 --env-file .env.production fastapi-todos ./start.sh
```

**Benefits:**

- ✅ Single container deployment
- ✅ Multiple RQ worker processes for true parallelism
- ✅ Process isolation (RQ workers separate from FastAPI)
- ✅ Traditional RQ behavior with job persistence

### 2. **FastAPI Only (Arq Same Process)**

```bash
# Run FastAPI with built-in Arq workers (like NestJS Bull)
docker run -p 8000:8000 --env-file .env.production \
  fastapi-todos uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

**Benefits:**

- ✅ Single process (like NestJS Bull)
- ✅ Async concurrency within same process
- ✅ Simpler resource usage
- ✅ No separate worker management needed

### 3. **FastAPI Only (External Workers)**

```bash
# Run just FastAPI, workers deployed separately
docker run -p 8000:8000 --env-file .env.production \
  fastapi-todos uv run uvicorn main:app --host 0.0.0.0 --port 8000

# Run workers separately (different containers/pods)
docker run --env-file .env.production \
  fastapi-todos uv run python worker.py
```

**Benefits:**

- ✅ Maximum scalability
- ✅ Independent scaling of API vs workers
- ✅ Better for Kubernetes deployments

### 4. **RQ Worker Only**

```bash
# Run as dedicated worker container
docker run --env-file .env.production \
  fastapi-todos uv run python worker.py
```

## 🚀 Production Examples

### AWS ECS - Single Container with Multiple Processes

```json
{
  "family": "fastapi-todos",
  "containerDefinitions": [
    {
      "name": "app",
      "image": "your-registry/fastapi-todos:latest",
      "memory": 512,
      "portMappings": [{ "containerPort": 8000 }],
      "environmentFiles": [
        { "value": "arn:aws:s3:::bucket/.env.production", "type": "s3" }
      ]
    }
  ]
}
```

### Kubernetes - Multiple Container Approach

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-todos
spec:
  template:
    spec:
      containers:
        # FastAPI container
        - name: api
          image: fastapi-todos:latest
          command:
            [
              "uv",
              "run",
              "uvicorn",
              "main:app",
              "--host",
              "0.0.0.0",
              "--port",
              "8000",
            ]
          ports: [{ "containerPort": 8000 }]

        # Worker containers
        - name: worker
          image: fastapi-todos:latest
          command: ["uv", "run", "python", "worker.py"]
          replicas: 3
```

### Docker Compose - Local Testing

```yaml
# docker-compose.test.yml
version: "3.8"
services:
  app:
    build: .
    ports: ["8000:8000"]
    environment:
      - MONGO_URI=mongodb://mongodb:27017/test
      - REDIS_URL=redis://redis:6379
    depends_on: [mongodb, redis]
    # Uses default ./start.sh command
```

## ⚙️ Environment Variables

All deployment options use the same environment variables:

```bash
# Database
MONGO_URI=mongodb://your-db-host:27017/dbname

# Cache
REDIS_URL=redis://your-redis-host:6379

# Application
ENVIRONMENT=production
DEBUG=false
```

## 🎯 Choose Your Deployment Style

| Approach                | Use Case                                       | Pros                               | Cons                                |
| ----------------------- | ---------------------------------------------- | ---------------------------------- | ----------------------------------- |
| **start.sh**            | Simple deployments, single container platforms | Single container, full RQ features | More complex process management     |
| **Arq Only**            | NestJS-like behavior, serverless               | Simplest, single process           | Less traditional job queue features |
| **Separate Containers** | Kubernetes, complex scaling                    | Maximum flexibility                | More complex orchestration          |

The **default `./start.sh`** approach gives you the best balance of simplicity and RQ's full feature set! 🚀
