# Nike Bot Pro - SaaS Edition

Professional desktop automation bot for Nike.cl drops.

## Project Structure

```
nike-bot-pro/
├── auth_server/        (feat/auth-stripe) - Seba
│   ├── models.py       User, Subscription, StripePayment
│   ├── routes/         /auth/*, /admin/*, /webhook/*
│   ├── services/       Auth logic, Stripe, User management
│   └── main.py         FastAPI server
│
├── client_app/         (feat/tauri-client) - Aly
│   ├── src/            React + TypeScript
│   ├── src-tauri/      Tauri bridge (Rust)
│   └── package.json    npm deps
│
├── engines/            Nike automation (DO NOT MODIFY)
│   └── engine.py       v11.2 - import only
│
├── docs/               Shared documentation
└── .github/            CI/CD workflows
```

## Team Responsibilities

| Person | Branch | Folder | Focus |
|--------|--------|--------|-------|
| **Seba** | `feat/auth-stripe` | `auth_server/` | Backend auth, Stripe, JWT, HWID |
| **Aly** | `feat/tauri-client` | `client_app/` | Tauri app, React UI, engine wrapper |

## Tech Stack

### Backend (Seba)
- Python 3.11
- FastAPI 0.115
- SQLModel + SQLite/PostgreSQL
- JWT (python-jose) + bcrypt
- Stripe SDK

### Frontend (Aly)
- Tauri 2.0
- React 18
- TypeScript
- Tailwind CSS
- Python FastAPI (local wrapper)

## API Contract

Seba implements these endpoints, Aly consumes them:

```
POST /auth/register     { email, password } → { token, plan, max_accounts }
POST /auth/login        { email, password } → { token, expires, plan, max_accounts }
GET  /auth/validate     Bearer token + X-HWID header → { valid, email, plan, max_accounts, expires }
POST /auth/revoke       { token } → { ok }
GET  /admin/users       → [ users ]
PUT  /admin/plan/{id}   { plan } → updated user
```

## Getting Started

### Seba (Auth Server)

```bash
cd auth_server
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with Stripe keys
python main.py
```

→ http://localhost:8000 (docs at /docs)

### Aly (Client App)

```bash
cd client_app
npm install
npm run tauri dev
```

Uses AUTH_MOCK until Seba's server is ready.

## Plans & Pricing

| Plan | Price | Accounts |
|------|-------|----------|
| **Starter** | $15k CLP | 3 |
| **Pro** | $25k CLP | 6 |
| **Elite** | $40k CLP | 10 |

## Merge Strategy

- **Feature branches:** `feat/auth-stripe`, `feat/tauri-client`
- **Integration:** Merge to `dev` (never directly to `main`)
- **Production:** Merge `dev` → `main` after testing

## Important Rules

🚫 **Seba:** Never touch `client_app/` or `engines/`  
🚫 **Aly:** Never touch `auth_server/` or `engines/`  
✅ Shared: `docs/`, `.github/`, `README.md`

## Deploy

### Auth Server (Railway)
1. Connect GitHub
2. Select `auth_server/` folder
3. Add env vars
4. Deploy

### Client App (GitHub Releases)
1. Build: `npm run tauri build`
2. Upload to releases
3. Discord download link

## Status

- **Week 1:** Initial setup ✅
  - Seba: Auth endpoints (register, login, validate)
  - Aly: Tauri setup + Login UI (with mocks)

- **Week 2:** Integration
  - Seba: Stripe webhooks, token blacklist
  - Aly: Connect to Seba's API, Dashboard

- **Week 3:** Beta launch
  - Full integration testing
  - Discord server setup
  - Release v1.0.0

## Questions?

- Seba → auth_server/README_SEBA.md
- Aly → client_app/README_ALY.md
