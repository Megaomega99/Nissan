# Test script for EV Battery Predictor API endpoints
Write-Host "Testing EV Battery Predictor API Endpoints..." -ForegroundColor Green

$baseUrl = "http://localhost:8000"
$apiUrl = "$baseUrl/api/v1"

# Function to test endpoint
function Test-Endpoint {
    param(
        [string]$url,
        [string]$method = "GET",
        [string]$description,
        [hashtable]$headers = @{},
        [string]$body = $null
    )
    
    Write-Host "Testing: $description" -ForegroundColor Yellow
    Write-Host "URL: $url" -ForegroundColor Gray
    
    try {
        $params = @{
            Uri = $url
            Method = $method
            Headers = $headers
            UseBasicParsing = $true
        }
        
        if ($body) {
            $params.Body = $body
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-WebRequest @params
        Write-Host "✓ Status: $($response.StatusCode)" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

Write-Host "`n=== Testing API Health ===" -ForegroundColor Cyan

# Test root endpoint
Test-Endpoint -url $baseUrl -description "Root endpoint"

# Test API docs
Test-Endpoint -url "$baseUrl/docs" -description "API Documentation"

# Test health endpoint (if exists)
Test-Endpoint -url "$apiUrl/health" -description "Health check"

Write-Host "`n=== Testing Authentication Endpoints ===" -ForegroundColor Cyan

# Test register endpoint structure
Test-Endpoint -url "$apiUrl/auth/register" -method "POST" -description "Register endpoint (structure test)" -body '{"username":"test","email":"test@test.com","password":"testpass"}'

Write-Host "`n=== Testing Vehicle Endpoints ===" -ForegroundColor Cyan

# Test vehicles endpoint (should require auth)
Test-Endpoint -url "$apiUrl/vehicles" -description "Vehicles endpoint (should return 401)"

Write-Host "`n=== Testing ML Models Endpoints ===" -ForegroundColor Cyan

# Test models endpoint (should require auth)
Test-Endpoint -url "$apiUrl/ml-models" -description "ML Models endpoint (should return 401)"

Write-Host "`n=== Testing Predictions Endpoints ===" -ForegroundColor Cyan

# Test predictions endpoint (should require auth)
Test-Endpoint -url "$apiUrl/predictions/predict" -method "POST" -description "Predictions endpoint (should return 401)"

Write-Host "`n=== Testing Battery Data Endpoints ===" -ForegroundColor Cyan

# Test battery data endpoint (should require auth)
Test-Endpoint -url "$apiUrl/battery-data" -description "Battery data endpoint (should return 401)"

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "API testing completed!" -ForegroundColor Green
Write-Host "Note: 401 Unauthorized responses are expected for protected endpoints" -ForegroundColor Yellow
Write-Host "Frontend should be available at: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend API docs at: http://localhost:8000/docs" -ForegroundColor Cyan
