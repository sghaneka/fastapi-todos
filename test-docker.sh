#!/bin/bash
# Test script for Docker setup with FastAPI + 3 Workers

echo "🐋 Starting FastAPI + 3 RQ Workers with Docker..."
echo "📋 Building and starting all services..."

# Build and start all services
docker-compose up --build -d

echo "⏳ Waiting for services to start..."
sleep 10

echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "📊 Testing the API..."

# Test health endpoint
echo "1. Health Check:"
curl -s http://localhost:8000/health | python -m json.tool

echo ""
echo "2. Queue a job:"
curl -s -X POST http://localhost:8000/reports \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user-1", "filters": {"type": "demo"}}' | python -m json.tool

echo ""
echo "3. Queue another job:"
curl -s -X POST http://localhost:8000/reports \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user-2", "filters": {"type": "demo"}}' | python -m json.tool

echo ""
echo "4. Queue a third job:"
curl -s -X POST http://localhost:8000/reports \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user-3", "filters": {"type": "demo"}}' | python -m json.tool

echo ""
echo "🔄 Check worker logs to see jobs being processed by different workers:"
echo "   docker-compose logs worker1"
echo "   docker-compose logs worker2" 
echo "   docker-compose logs worker3"

echo ""
echo "📊 Monitor Redis queue:"
echo "   Visit http://localhost:8081 (Redis Commander)"

echo ""
echo "🛑 To stop all services:"
echo "   docker-compose down"