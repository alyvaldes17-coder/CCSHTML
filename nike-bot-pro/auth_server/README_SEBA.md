# Nike Bot Pro - Auth Server (feat/auth-stripe)

Backend de autenticación para Nike Bot Pro SaaS.

## Responsabilidades (Seba)

- ✅ JWT token generation & validation
- ✅ User registration & login (email/password)
- ✅ Plan management (Starter/Pro/Elite)
- ✅ Hardware ID binding (1 token = 1 machine)
- ✅ Stripe/MercadoPago webhook processing
- ✅ Admin endpoints (user management)

## NO Tocas

- ❌ `client_app/` - Eso es de Aly (feat/tauri-client)
- ❌ `engines/` - Nike automation logic
- ❌ Cualquier cosa fuera de `auth_server/`

## Setup Local

```bash
cd auth_server

# Virtual env
python -m venv venv
venv\Scripts\activate  # Windows
# o source venv/bin/activate  # Mac/Linux

# Install deps
pip install -r requirements.txt

# Setup .env
cp .env.example .env
# Edit .env con tus valores de Stripe
```

## Correr servidor

```bash
python main.py
# http://localhost:8000
# Docs: http://localhost:8000/docs
```

## API Contract (Acordado con Aly)

```
POST /auth/register
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
→ { token, plan, expires_in, max_accounts }

POST /auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
→ { token, expires, plan, max_accounts }

GET /auth/validate
Headers:
  Authorization: Bearer <token>
  X-HWID: <hwid>
→ { valid, email, plan, max_accounts, expires }

POST /auth/revoke
{ "token": "<token>" }
→ { ok, message }

GET /admin/users
→ [ { id, email, plan, max_accounts, is_active, created_at } ]

PUT /admin/plan/{user_id}
{ "plan": "pro" }
→ { user object updated }

POST /webhook/stripe
(Stripe sends event)
→ { ok }
```

## Stack

- **Framework:** FastAPI 0.115
- **DB:** SQLModel + SQLite (dev), PostgreSQL (prod)
- **Auth:** JWT (python-jose) + bcrypt (passlib)
- **Payments:** Stripe SDK
- **Env:** python-dotenv

## Deploy (Railway)

1. Connect GitHub repo
2. Select `auth_server/` as root directory
3. Add env vars (STRIPE_SECRET_KEY, JWT_SECRET_KEY, etc)
4. Deploy!

## Merge Strategy

1. Trabajas en `feat/auth-stripe`
2. Mergeas a `dev` (PR review)
3. NUNCA directo a `main`
4. Aly mergeará `feat/tauri-client` a `dev` cuando termine

## Testing

```bash
# En Swagger: http://localhost:8000/docs
# Prueba endpoints interactivamente
```

## Notas

- Q-HWID header es custom, asegúrate que esté en CORS
- Aly usará mocks mientras tu servidor no esté listo
- Token expira en 30 días (configurable en .env)
- TODO: Token blacklist para logout (opcional Week 2)
