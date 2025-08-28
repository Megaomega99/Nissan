# Test EV Battery Predictor Frontend
Write-Host "Testing EV Battery Predictor Frontend..." -ForegroundColor Green

# Check if node_modules exists
if (!(Test-Path "frontend/node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
}

# Start the frontend development server
Write-Host "Starting frontend development server..." -ForegroundColor Yellow
Set-Location frontend
npm start
