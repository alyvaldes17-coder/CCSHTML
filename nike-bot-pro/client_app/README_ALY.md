# Nike Bot Pro - Client App (feat/tauri-client)

App Tauri + React para Nike Bot Pro.

## Responsabilidades (Aly)

- ✅ Interfaz Tauri (Login, Dashboard, Accounts, Drop)
- ✅ WebSocket para logs en tiempo real
- ✅ FastAPI local que wrappea engine.py
- ✅ Multiprocessing (un proceso por cuenta Nike)
- ✅ Integración con auth_server (Seba)

## NO Tocas

- ❌ `auth_server/` - Eso es de Seba (feat/auth-stripe)
- ❌ `engines/` - Nike automation logic (importas, no modificas)
- ❌ Cualquier cosa fuera de `client_app/`

## MOCKS mientras esperas auth_server (Seba)

Usa esto en tu estado local:

```typescript
const AUTH_MOCK = {
  validate: () => ({ valid: true, plan: "elite", max_accounts: 10 }),
  login: () => ({
    token: "NK-TEST-2026",
    expires: "2026-04-17",
    plan: "elite",
    max_accounts: 10
  }),
  register: () => ({ token: "NK-TEST-2026", plan: "starter", max_accounts: 3 })
}
```

Cuando Seba termine auth_server, reemplazas con llamadas reales.

## API Contract (Acordado con Seba)

```
POST /auth/register     → { token, plan, max_accounts }
POST /auth/login        → { token, expires, plan, max_accounts }
GET  /auth/validate     → { valid, email, plan, max_accounts, expires }
POST /auth/revoke       → { ok }
```

Headers:
- `Authorization: Bearer <token>`
- `X-HWID: <hardware_id>`

## Stack

- **Frontend:** Tauri 2.0 + React 18 + TypeScript + Tailwind
- **Backend Local:** Python FastAPI (wrappea engine.py)
- **WebSocket:** Logs en tiempo real
- **Process:** multiprocessing (1 proceso = 1 cuenta Nike)

## Engine Integration

El `engine.py` ya existe en `engines/`. Los importas así:

```python
from engines.engine import NikeBotEngine

# en FastAPI local:
@app.post("/accounts/{account_id}/attack")
async def start_attack(account_id: int):
    engine = NikeBotEngine(account_id=account_id)
    # engine.ejecutar_ataque_completo()
    return {"status": "attacking"}
```

## Merge Strategy

1. Trabajas en `feat/tauri-client`
2. Mergeas a `dev` (PR review)
3. NUNCA directo a `main`
4. Seba mergeará `feat/auth-stripe` a `dev` cuando termine

## Local Development

```bash
cd client_app
npm install
npm run tauri dev
```

Docs en `src/mocks/AUTH_MOCK.ts` mientras esperas server.
