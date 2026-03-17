# API Documentation - Nike Bot Backend

## Base URL
- Development: `http://localhost:8000`
- Production: `https://api.your-domain.com`

## Endpoints

### 1. Validate Token
**Endpoint:** `POST /auth/validate-token`

**Purpose:** Verify JWT token validity (called by desktop app)

**Request:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Success Response (200):**
```json
{
  "valid": true,
  "email": "user@example.com",
  "plan": "pro",
  "expires": 1704067200
}
```

**Error Response (401):**
```json
{
  "detail": "Token expired"
}
```

---

### 2. Generate Token
**Endpoint:** `POST /auth/generate-token`

**Purpose:** Create new JWT token (called after Stripe payment)

**Request:**
```json
{
  "email": "user@example.com",
  "plan": "pro"
}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 2592000,
  "plan": "pro"
}
```

---

### 3. Stripe Webhook
**Endpoint:** `POST /auth/webhook/stripe`

**Purpose:** Handle Stripe payment events

**Event Types:**
- `payment_intent.succeeded` - Handle successful payment

**Payload (from Stripe):**
```json
{
  "type": "payment_intent.succeeded",
  "data": {
    "object": {
      "metadata": {
        "customer_email": "user@example.com",
        "plan": "pro"
      }
    }
  }
}
```

**Response:**
```json
{
  "status": "token_generated",
  "token": "eyJ..."
}
```

---

### 4. Check Version
**Endpoint:** `GET /check-version`

**Purpose:** Check if app update is available

**Response:**
```json
{
  "version": "1.0.0",
  "latest_version": "1.0.1",
  "update_available": true,
  "download_url": "https://github.com/your-repo/releases/v1.0.1"
}
```

---

### 5. Health Check
**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## Authentication

- Endpoints use **JWT Bearer Token** in header: `Authorization: Bearer <token>`
- Generated tokens expire in **30 days**
- Refresh by calling `/generate-token` again

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (missing fields) |
| 401 | Unauthorized (invalid/expired token) |
| 404 | Resource not found |
| 500 | Server error |

## Rate Limiting

Current setup has no rate limits. For production:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app = Limiter(app)

@app.post("/auth/validate-token")
@limiter.limit("10/minute")
async def validate_token(...):
    ...
```

## Example Requests

### cURL
```bash
# Validate token
curl -X POST http://localhost:8000/auth/validate-token \
  -H "Content-Type: application/json" \
  -d '{"token":"eyJ..."}'

# Generate token
curl -X POST http://localhost:8000/auth/generate-token \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","plan":"pro"}'
```

### Python (requests)
```python
import requests

# Validate
resp = requests.post(
    "http://localhost:8000/auth/validate-token",
    json={"token": "eyJ..."}
)
print(resp.json())

# Generate
resp = requests.post(
    "http://localhost:8000/auth/generate-token",
    json={"email": "user@example.com", "plan": "pro"}
)
print(resp.json()["token"])
```

### JavaScript (fetch)
```javascript
// Validate
const response = await fetch("http://localhost:8000/auth/validate-token", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ token: "eyJ..." })
});
const data = await response.json();
console.log(data);
```
