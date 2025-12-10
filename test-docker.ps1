# Test script for Local Development with Docker Dependencies

Write-Host "🔧 Starting Local Development Dependencies..." -ForegroundColor Green
Write-Host "📋 Starting MongoDB and Redis for local development..." -ForegroundColor Yellow

# Start only dependencies
docker-compose up -d

Write-Host "⏳ Waiting for dependencies to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "🔍 Checking dependency status..." -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "📊 Dependencies ready! Now run your application locally:" -ForegroundColor Green
Write-Host "   Terminal 1: uv run python main.py" -ForegroundColor White
Write-Host "   Terminal 2: uv run python worker.py" -ForegroundColor White
Write-Host "   Terminal 3: uv run python worker.py (optional)" -ForegroundColor White

Write-Host ""
Write-Host "🌐 Available services:" -ForegroundColor Cyan
Write-Host "   MongoDB: localhost:27018" -ForegroundColor White
Write-Host "   Redis: localhost:6379" -ForegroundColor White  
Write-Host "   MongoDB Express: http://localhost:8081" -ForegroundColor White
Write-Host "   Redis Commander: http://localhost:8082" -ForegroundColor White

Write-Host ""
Write-Host "🐋 For production deployment, see DEPLOYMENT.md" -ForegroundColor Magenta
Write-Host "   Single Dockerfile works with cloud services (DocumentDB, ElastiCache, etc.)" -ForegroundColor White

Write-Host ""
Write-Host "🛑 To stop dependencies:" -ForegroundColor Red
Write-Host "   docker-compose down" -ForegroundColor White