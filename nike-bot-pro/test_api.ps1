#!/usr/bin/env pwsh
# Quick test script for Nike Bot Pro Auth API

$API = "https://nike-bot-pro-production.up.railway.app"
$EMAIL = "test_$(Get-Random -Minimum 10000 -Maximum 99999)@test.com"
$PASSWORD = "TestPass123!"

Write-Host "🧪 Testing $API`n" -ForegroundColor Cyan
Write-Host "═" * 50 -ForegroundColor Gray

# 1. Health Check
Write-Host "1️⃣  Health Check" -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest "$API/health" -UseBasicParsing | ConvertFrom-Json
    Write-Host "✅ Health: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health check failed" -ForegroundColor Red
    exit 1
}

# 2. Register
Write-Host "`n2️⃣  Register User" -ForegroundColor Yellow
try {
    $regBody = @{ email = $EMAIL; password = $PASSWORD } | ConvertTo-Json
    $reg = Invoke-WebRequest "$API/auth/register" `
        -Method POST `
        -ContentType "application/json" `
        -Body $regBody `
        -UseBasicParsing | ConvertFrom-Json
    Write-Host "✅ Registered: $EMAIL" -ForegroundColor Green
    $TOKEN = $reg.access_token
    Write-Host "   Token: $($TOKEN.Substring(0,20))..." -ForegroundColor Gray
} catch {
    Write-Host "❌ Registration failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 3. Login
Write-Host "`n3️⃣  Login User" -ForegroundColor Yellow
try {
    $loginBody = @{ email = $EMAIL; password = $PASSWORD } | ConvertTo-Json
    $login = Invoke-WebRequest "$API/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginBody `
        -UseBasicParsing | ConvertFrom-Json
    Write-Host "✅ Login successful" -ForegroundColor Green
    $TOKEN2 = $login.access_token
} catch {
    Write-Host "❌ Login failed" -ForegroundColor Red
    exit 1
}

# 4. Validate Token
Write-Host "`n4️⃣  Validate Token" -ForegroundColor Yellow
try {
    $valBody = @{ token = $TOKEN } | ConvertTo-Json
    $val = Invoke-WebRequest "$API/auth/validate" `
        -Method POST `
        -ContentType "application/json" `
        -Body $valBody `
        -UseBasicParsing | ConvertFrom-Json
    Write-Host "✅ Token valid for: $($val.email)" -ForegroundColor Green
} catch {
    Write-Host "❌ Validation failed" -ForegroundColor Red
    exit 1
}

Write-Host "`n" + ("═" * 50) -ForegroundColor Gray
Write-Host "🎉 ALL TESTS PASSED!" -ForegroundColor Green
Write-Host "API is working correctly ✅" -ForegroundColor Green
