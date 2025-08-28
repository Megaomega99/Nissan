# Test script specifically for the Predictions functionality
Write-Host "Testing EV Battery Predictor - Predictions Module..." -ForegroundColor Green

$baseUrl = "http://localhost:8000"
$apiUrl = "$baseUrl/api/v1"

# Function to test authenticated endpoint
function Test-AuthenticatedEndpoint {
    param(
        [string]$url,
        [string]$method = "GET",
        [string]$description,
        [string]$token,
        [string]$body = $null
    )
    
    Write-Host "Testing: $description" -ForegroundColor Yellow
    Write-Host "URL: $url" -ForegroundColor Gray
    
    try {
        $headers = @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }
        
        $params = @{
            Uri = $url
            Method = $method
            Headers = $headers
            UseBasicParsing = $true
        }
        
        if ($body) {
            $params.Body = $body
        }
        
        $response = Invoke-WebRequest @params
        Write-Host "✓ Status: $($response.StatusCode)" -ForegroundColor Green
        
        # Try to parse JSON response
        try {
            $jsonResponse = $response.Content | ConvertFrom-Json
            Write-Host "Response preview: $($jsonResponse | ConvertTo-Json -Depth 2 -Compress)" -ForegroundColor Cyan
        } catch {
            Write-Host "Response: $($response.Content.Substring(0, [Math]::Min(100, $response.Content.Length)))" -ForegroundColor Cyan
        }
        
        return $true
    }
    catch {
        Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            Write-Host "Status Code: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
        }
        return $false
    }
}

Write-Host "`n=== Testing Predictions Flow ===" -ForegroundColor Cyan

# First, test if we can register a user (if needed)
Write-Host "`n1. Testing user registration/login..." -ForegroundColor Yellow

$registerBody = @{
    username = "testuser_$(Get-Random)"
    email = "test_$(Get-Random)@example.com"
    password = "testpass123"
    first_name = "Test"
    last_name = "User"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-WebRequest -Uri "$apiUrl/auth/register" -Method POST -Body $registerBody -ContentType "application/json" -UseBasicParsing
    Write-Host "✓ User registered successfully" -ForegroundColor Green
    $userInfo = $registerResponse.Content | ConvertFrom-Json
    
    # Now login to get token
    $loginBody = "username=$($userInfo.username)&password=testpass123"
    $loginResponse = Invoke-WebRequest -Uri "$apiUrl/auth/login" -Method POST -Body $loginBody -ContentType "application/x-www-form-urlencoded" -UseBasicParsing
    $loginInfo = $loginResponse.Content | ConvertFrom-Json
    $token = $loginInfo.access_token
    
    Write-Host "✓ Login successful, token obtained" -ForegroundColor Green
    
} catch {
    Write-Host "⚠ Registration/Login failed. Using test endpoints without auth..." -ForegroundColor Yellow
    $token = $null
}

if ($token) {
    Write-Host "`n2. Testing authenticated endpoints with token..." -ForegroundColor Yellow
    
    # Test vehicles endpoint
    Test-AuthenticatedEndpoint -url "$apiUrl/vehicles/" -description "Get vehicles" -token $token
    
    # Test models endpoint
    Test-AuthenticatedEndpoint -url "$apiUrl/ml-models/" -description "Get ML models" -token $token
    
    # If we have models, test predictions
    try {
        $modelsResponse = Invoke-WebRequest -Uri "$apiUrl/ml-models/" -Headers @{"Authorization"="Bearer $token"} -UseBasicParsing
        $models = ($modelsResponse.Content | ConvertFrom-Json)
        
        if ($models -and $models.Count -gt 0) {
            $modelId = $models[0].id
            Write-Host "`nFound model ID: $modelId" -ForegroundColor Cyan
            
            # Test metrics endpoint
            Test-AuthenticatedEndpoint -url "$apiUrl/predictions/metrics/$modelId" -description "Get model metrics" -token $token
            
            # Test SOH forecast
            $forecastBody = @{
                model_id = $modelId
                prediction_steps = 100
                time_step_days = 7
            } | ConvertTo-Json
            
            Test-AuthenticatedEndpoint -url "$apiUrl/predictions/soh-forecast" -method "POST" -description "SOH Forecast" -token $token -body $forecastBody
            
        } else {
            Write-Host "⚠ No trained models found to test predictions" -ForegroundColor Yellow
        }
        
    } catch {
        Write-Host "⚠ Could not retrieve models for testing" -ForegroundColor Yellow
    }
    
} else {
    Write-Host "`n⚠ No authentication token available. Skipping authenticated tests." -ForegroundColor Yellow
}

Write-Host "`n=== Testing Summary ===" -ForegroundColor Cyan
Write-Host "Predictions testing completed!" -ForegroundColor Green
Write-Host "If you see 500 errors on metrics, the fix has been applied." -ForegroundColor Yellow
Write-Host "Try the predictions functionality in the frontend at: http://localhost:3000" -ForegroundColor Cyan
