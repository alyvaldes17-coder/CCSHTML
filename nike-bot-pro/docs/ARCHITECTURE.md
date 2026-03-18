# Arquitectura - Nike Bot Commercial

## Diagrama General

```
┌─────────────────────────────────────────────┐
│ Desktop App (Tauri + React + TypeScript)    │
├─────────────────────────────────────────────┤
│ • Token Dialog (startup)                    │
│ • Dashboard (main UI)                       │
│ • Local token validation (offline mode)     │
└─────────────────────────────────────────────┘
        ↓ invoke Rust commands
┌─────────────────────────────────────────────┐
│ Tauri Bridge (Rust)                         │
├─────────────────────────────────────────────┤
│ • Command handlers                          │
│ • File system access                        │
│ • Process spawning                          │
└─────────────────────────────────────────────┘
        ↓ Python subprocess
┌─────────────────────────────────────────────┐
│ Python Core (token_manager.py)              │
├─────────────────────────────────────────────┤
│ • Token persistence (encrypted)             │
│ • Hardware ID binding                       │
│ • Online/offline validation                 │
└─────────────────────────────────────────────┘
        ↓ HTTPS (api:8000)
┌─────────────────────────────────────────────┐
│ FastAPI Backend                             │
├─────────────────────────────────────────────┤
│ • POST /validate-token                      │
│ • POST /generate-token                      │
│ • POST /webhook/stripe                      │
│ • GET /check-version                        │
└─────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────┐
│ External Services                           │
├─────────────────────────────────────────────┤
│ • Stripe API (payment)                      │
│ • Nike.com (automation target)              │
└─────────────────────────────────────────────┘
```

## Componentes Principales

### 1. Frontend (Tauri + React)
- **Location:** `app/src/`
- **Purpose:** UI for token input and dashboard
- **Key Files:**
  - `pages/TokenDialog.tsx` - License activation form
  - `pages/Dashboard.tsx` - Main application UI
  - `utils/tokenManager.ts` - Client-side token handling
- **Framework:** React 18 + TypeScript + Vite

### 2. Bridge (Tauri Rust)
- **Location:** `app/src-tauri/`
- **Purpose:** Interface between JavaScript frontend and Python
- **Call Python:** `invoke('command_name', {args})`

### 3. Core (Python)
- **Location:** `core/`
- **Key Components:**
  - `token_manager.py` - Token validation logic
  - `engine.py` (from original) - Nike automation
  - `bot_controller.py` (from original) - Account management

### 4. Backend API (FastAPI)
- **Location:** `backend/`
- **Purpose:** Token generation, validation, Stripe webhooks
- **Database:** SQLite (development), PostgreSQL (production)

## Flow Diagram: Token Activation

```
User launches app
    ↓
[No token found?] → TokenDialog
    ↓
User pastes JWT
    ↓
TokenManager.validateToken()
    ↓
Try online: POST /validate-token
    ↓
Fallback to offline (if no internet)
    ↓
Valid? → Save encrypted locally
    ↓
Dashboard loaded
```

## Flow Diagram: Payment (via Stripe)

```
User clicks "Get Token"
    ↓
Redirects to Stripe checkout
    ↓
Payment successful
    ↓
Stripe webhook → POST /webhook/stripe
    ↓
Backend generates JWT  
    ↓
Send token via email
    ↓
User pastes in app
```

## Data Persistence

### Token File Location
- **Windows:** `%USERPROFILE%\.nike-bot\token` (encrypted)
- **Mac:** `~/.nike-bot/token` (encrypted)
- **Linux:** `~/.nike-bot/token` (encrypted)

### Encryption
- **Algorithm:** Fernet (AES-128)
- **Key Location:** `~/.nike-bot/.key` (generated on first run)

### Hardware ID Binding
- CPU info + MAC address + disk ID
- Prevents token sharing across machines
- Stored in token file for validation

## Security Considerations

1. **Token Protection**
   - Encrypted with Fernet (HTTPS + AES)
   - Hardware ID binding (1 token = 1 machine)
   - 30-day expiry

2. **API Communication**
   - HTTPS only (enforced)
   - JWT signed with secret key
   - CORS enabled for Tauri desktop

3. **Offline Mode**
   - JWT signature validated locally
   - Expiry checked against system time
   - No engine.py access without valid token

## Technology Choices

| Component | Technology | Why? |
|-----------|-----------|------|
| Desktop | Tauri | Lightweight, secure, easier distribution |
| Frontend | React | Familiar, component-based, easy to maintain |
| Styling | CSS | Simple, no bloat |
| Backend | FastAPI | Fast, async, great for payment webhooks |
| Auth | JWT | Stateless, 30-day expiry is simple |
| Encryption | Fernet | Python built-in, secure by default |
| Database | SQLite | No setup needed for dev, scales with PostgreSQL |

## Future Extensibility

Current architecture allows:
- Adding more API endpoints (leaderboards, stats)
- Integrating analytics/telemetry
- Multi-user licensing per machine
- Rate limiting and abuse detection
- Premium features gating per plan tier
