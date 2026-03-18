# Test script para validar todos los endpoints en producción
# Uso: .\TEST_ENDPOINTS.ps1

param(
    [string]$BaseUrl = "https://nike-bot-pro-production.up.railway.app",
    [string]$TestEmail = $null,
    [string]$TestPassword = "TestPass123!"
)

# Generate random email si no se proporciona
if (-not $TestEmail) {
    $TestEmail = "test_$(Get-Random -Minimum 1000 -Maximum 9999)@example.com"
}

$token = $null
$userId = $null

# Color helpers
function Success($msg) { Write-Host "✅ $msg" -ForegroundColor Green }
function Error($msg) { Write-Host "❌ $msg" -ForegroundColor Red }
function Info($msg) { Write-Host "ℹ️  $msg" -ForegroundColor Cyan }
function Section($msg) { Write-Host "`n$msg" -ForegroundColor Yellow; Write-Host ("=" * $msg.Length) -ForegroundColor Yellow }

Section "🧪 PRODUCCIÓN ENDPOINT TESTING"

Info "Base URL: $BaseUrl"
Info "Test Email: $TestEmail"
Info "Test Password: $TestPassword"

# ==============================================================================
# 1. REGISTER
# ==============================================================================
Section "1. Testing /auth/register"

try {
    $body = @{
        email = $TestEmail
        password = $TestPassword
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "$BaseUrl/auth/register" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -UseBasicParsing

    $data = $response.Content | ConvertFrom-Json
    
    Success "Registration successful!"
    Info "User ID: $($data.id)"
    Info "Email: $($data.email)"
    Info "Is Admin: $($data.is_admin)"
    
    $userId = $data.id
} catch {
    Error "Registration failed!"
    Write-Host "Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Response: $($_.ErrorDetails.Message)" -ForegroundColor Red
    exit 1
}

# ==============================================================================
# 2. LOGIN
# ==============================================================================
Section "2. Testing /auth/login"

try {
    $body = @{
        email = $TestEmail
        password = $TestPassword
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "$BaseUrl/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -UseBasicParsing

    $data = $response.Content | ConvertFrom-Json
    
    Success "Login successful!"
    Info "Token type: $($data.token_type)"
    Info "Token: $($data.access_token.Substring(0, 20))..."
    
    $token = $data.access_token
} catch {
    Error "Login failed!"
    Write-Host "Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# ==============================================================================
# 3. VALIDATE
# ==============================================================================
Section "3. Testing /auth/validate"

try {
    $body = @{
        token = $token
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "$BaseUrl/auth/validate" `
        -Method POST `
        -ContentType "application/json" `
        -Headers @{Authorization = "Bearer $token"} `
        -Body $body `
        -UseBasicParsing

    $data = $response.Content | ConvertFrom-Json
    
    Success "Token validation successful!"
    Info "User Email: $($data.email)"
    Info "Is Admin: $($data.is_admin)"
} catch {
    Error "Validation failed!"
    Write-Host "Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# ==============================================================================
# 4. REVOKE
# ==============================================================================
Section "4. Testing /auth/revoke"

try {
    $body = @{
        token = $token
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "$BaseUrl/auth/revoke" `
        -Method POST `
        -ContentType "application/json" `
        -Headers @{Authorization = "Bearer $token"} `
        -Body $body `
        -UseBasicParsing

    $data = $response.Content | ConvertFrom-Json
    
    Success "Token revoked successfully!"
    Info "Message: $($data.message)"
} catch {
    Error "Revoke failed!"
    Write-Host "Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# ==============================================================================
# FINAL
# ==============================================================================
Section "✨ ALL TESTS COMPLETED"
Info "Test user created: $TestEmail"
Info "User ID: $userId"
