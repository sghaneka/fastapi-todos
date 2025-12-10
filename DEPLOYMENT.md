# Cloud Deployment Examples

This document shows how to deploy the FastAPI Todo application to various cloud platforms where dependencies (MongoDB, Redis) are managed services.

## Docker Image Usage

The `Dockerfile` creates a single image that can run both FastAPI and workers:

```bash
# Build the image
docker build -t fastapi-todos .

# Run FastAPI server
docker run -p 8000:8000 --env-file .env.production fastapi-todos

# Run worker (override command)
docker run --env-file .env.production fastapi-todos uv run python worker.py
```

## AWS Deployment

### Dependencies

- **Database**: AWS DocumentDB (MongoDB-compatible)
- **Cache**: AWS ElastiCache Redis
- **Container**: AWS ECS Fargate

### Environment Variables

```bash
# DocumentDB
MONGO_URI=mongodb://username:password@docdb-cluster.cluster-abc123.us-west-2.docdb.amazonaws.com:27017/?ssl=true&replicaSet=rs0

# ElastiCache Redis
REDIS_URL=redis://master.redis-cluster.abc123.cache.amazonaws.com:6379

# Application
ENVIRONMENT=production
```

### ECS Task Definition (example)

```json
{
  "family": "fastapi-todos",
  "taskRoleArn": "arn:aws:iam::123:role/ecsTaskRole",
  "networkMode": "awsvpc",
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "your-registry/fastapi-todos:latest",
      "portMappings": [{ "containerPort": 8000 }],
      "environmentFiles": [
        { "value": "arn:aws:s3:::bucket/.env.production", "type": "s3" }
      ]
    },
    {
      "name": "worker",
      "image": "your-registry/fastapi-todos:latest",
      "command": ["uv", "run", "python", "worker.py"],
      "environmentFiles": [
        { "value": "arn:aws:s3:::bucket/.env.production", "type": "s3" }
      ]
    }
  ]
}
```

## Azure Deployment

### Dependencies

- **Database**: Azure Cosmos DB (MongoDB API)
- **Cache**: Azure Cache for Redis
- **Container**: Azure Container Apps

### Environment Variables

```bash
# Cosmos DB
MONGO_URI=mongodb://myaccount:key@myaccount.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb

# Azure Redis Cache
REDIS_URL=redis://:password@myredis.redis.cache.windows.net:6379

# Application
ENVIRONMENT=production
```

### Container App YAML

```yaml
apiVersion: 2022-03-01
kind: ContainerApp
properties:
  configuration:
    secrets:
      - name: mongo-uri
        value: "mongodb://..."
      - name: redis-url
        value: "redis://..."
  template:
    containers:
      - image: your-registry/fastapi-todos:latest
        name: api
        env:
          - name: MONGO_URI
            secretRef: mongo-uri
          - name: REDIS_URL
            secretRef: redis-url
        resources:
          cpu: 0.25
          memory: 0.5Gi
    scale:
      minReplicas: 1
      maxReplicas: 3
```

## Google Cloud Platform

### Dependencies

- **Database**: Google Cloud MongoDB Atlas / Cloud SQL
- **Cache**: Google Cloud Memorystore Redis
- **Container**: Google Cloud Run

### Environment Variables

```bash
# MongoDB Atlas
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/fastapi_todos?retryWrites=true&w=majority

# Memorystore Redis
REDIS_URL=redis://10.0.0.3:6379

# Application
ENVIRONMENT=production
```

### Cloud Run Deployment

```bash
# Deploy API
gcloud run deploy fastapi-todos-api \
  --image gcr.io/project/fastapi-todos:latest \
  --env-vars-file .env.production \
  --port 8000 \
  --allow-unauthenticated

# Deploy Worker (Cloud Run Jobs)
gcloud run jobs create fastapi-todos-worker \
  --image gcr.io/project/fastapi-todos:latest \
  --env-vars-file .env.production \
  --command "uv,run,python,worker.py" \
  --parallelism 3
```

## Kubernetes Deployment

### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-todos-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-todos-api
  template:
    spec:
      containers:
        - name: api
          image: fastapi-todos:latest
          ports:
            - containerPort: 8000
          envFrom:
            - secretRef:
                name: fastapi-todos-secrets
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "200m"

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-todos-workers
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-todos-workers
  template:
    spec:
      containers:
        - name: worker
          image: fastapi-todos:latest
          command: ["uv", "run", "python", "worker.py"]
          envFrom:
            - secretRef:
                name: fastapi-todos-secrets
```

## Local Development vs Production

### Local Development

```bash
# Start dependencies only
docker-compose up -d

# Run application locally
uv run python main.py        # FastAPI
uv run python worker.py      # Workers
```

### Production

```bash
# Dependencies are cloud services (DocumentDB, ElastiCache, etc.)
# Application runs in containers with external config

# Build and push
docker build -t myregistry/fastapi-todos .
docker push myregistry/fastapi-todos

# Deploy to cloud platform of choice
```

The key insight: **Dependencies are externalized in production**, making the application truly cloud-native and platform-agnostic.
