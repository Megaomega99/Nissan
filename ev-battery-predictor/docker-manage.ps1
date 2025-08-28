# EV Battery Predictor - Docker Management Script
# This script helps manage the Docker deployment

Write-Host "EV Battery Predictor - Docker Management" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

$action = $args[0]

switch ($action) {
    "up" {
        Write-Host "Starting all services..." -ForegroundColor Yellow
        docker-compose up -d
        Write-Host "Services started successfully!" -ForegroundColor Green
        Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
        Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
    }
    "down" {
        Write-Host "Stopping all services..." -ForegroundColor Yellow
        docker-compose down
        Write-Host "Services stopped successfully!" -ForegroundColor Green
    }
    "build" {
        Write-Host "Building Docker images..." -ForegroundColor Yellow
        docker-compose build
        Write-Host "Images built successfully!" -ForegroundColor Green
    }
    "restart" {
        Write-Host "Restarting all services..." -ForegroundColor Yellow
        docker-compose restart
        Write-Host "Services restarted successfully!" -ForegroundColor Green
    }
    "logs" {
        $service = $args[1]
        if ($service) {
            Write-Host "Showing logs for $service..." -ForegroundColor Yellow
            docker-compose logs -f $service
        } else {
            Write-Host "Showing logs for all services..." -ForegroundColor Yellow
            docker-compose logs -f
        }
    }
    "status" {
        Write-Host "Service status:" -ForegroundColor Yellow
        docker-compose ps
    }
    "clean" {
        Write-Host "Cleaning up Docker resources..." -ForegroundColor Yellow
        docker-compose down -v
        docker system prune -f
        Write-Host "Cleanup completed!" -ForegroundColor Green
    }
    "init" {
        Write-Host "Initializing EV Battery Predictor..." -ForegroundColor Yellow
        Write-Host "Building images..." -ForegroundColor Yellow
        docker-compose build
        Write-Host "Starting services..." -ForegroundColor Yellow
        docker-compose up -d
        Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
        Write-Host "Initialization completed!" -ForegroundColor Green
        Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
        Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
    }
    default {
        Write-Host "Usage: .\docker-manage.ps1 [command]" -ForegroundColor White
        Write-Host ""
        Write-Host "Available commands:" -ForegroundColor Yellow
        Write-Host "  init     - Build and start all services (first time setup)" -ForegroundColor White
        Write-Host "  up       - Start all services" -ForegroundColor White
        Write-Host "  down     - Stop all services" -ForegroundColor White
        Write-Host "  build    - Build Docker images" -ForegroundColor White
        Write-Host "  restart  - Restart all services" -ForegroundColor White
        Write-Host "  logs     - Show logs (optionally specify service name)" -ForegroundColor White
        Write-Host "  status   - Show service status" -ForegroundColor White
        Write-Host "  clean    - Stop services and clean up Docker resources" -ForegroundColor White
        Write-Host ""
        Write-Host "Examples:" -ForegroundColor Yellow
        Write-Host "  .\docker-manage.ps1 init" -ForegroundColor Gray
        Write-Host "  .\docker-manage.ps1 up" -ForegroundColor Gray
        Write-Host "  .\docker-manage.ps1 logs backend" -ForegroundColor Gray
        Write-Host "  .\docker-manage.ps1 status" -ForegroundColor Gray
    }
}
