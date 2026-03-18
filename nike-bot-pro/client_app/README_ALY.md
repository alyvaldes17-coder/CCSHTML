# Nike Bot Pro - Client App (feat/tauri-client)

App Tauri + React para Nike Bot Pro.

## ✅ Backend Deployado en Producción

El auth_server ya está running en:
```
https://nike-bot-pro-production.up.railway.app
```

**Estado:** ✅ Running + todas las variables de entorno configuradas

## Responsabilidades (Aly)

- ✅ Interfaz Tauri (Login, Dashboard, Accounts, Drop)
- ✅ WebSocket para logs en tiempo real
- ✅ FastAPI local que wrappea engine.py
- ✅ Multiprocessing (un proceso por cuenta Nike)
- ✅ Integración con auth_server (LISTA - ya deployada)

## NO Tocas

- ❌ `auth_server/` - Backend deployado en producción (Seba)
- ❌ `engines/` - Nike automation logic (importas, no modificas)
- ❌ Cualquier cosa fuera de `client_app/`

## Endpoints Disponibles (Ya Integrados)

El cliente está configurado para usar los siguientes endpoints en producción:

### 1. **Registrar usuario**
```
POST https://nike-bot-pro-production.up.railway.app/auth/register

Body:
{
  "email": "usuario@example.com",
  "password": "password123"
}

Response:
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "plan": "starter",
  "expires_in": 2592000,
  "max_accounts": 3
}
```

### 2. **Login**
```
POST https://nike-bot-pro-production.up.railway.app/auth/login

Body:
{
  "email": "usuario@example.com",
  "password": "password123"
}

Response:
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "expires": "2026-04-17T10:30:00",
  "plan": "elite",
  "max_accounts": 10
}
```

### 3. **Validar Token** (Usado internamente)
```
GET https://nike-bot-pro-production.up.railway.app/auth/validate

Headers:
  Authorization: Bearer {token}
  X-HWID: 00000000-0000-0000-0000-000000000000

Response:
{
  "valid": true,
  "email": "usuario@example.com",
  "plan": "elite",
  "max_accounts": 10,
  "expires": "2026-04-17T10:30:00"
}
```

### 4. **Revocar Token (Logout)**
```
POST https://nike-bot-pro-production.up.railway.app/auth/revoke

Response:
{
  "ok": true,
  "message": "Token revoked"
}
```

## Cómo Funciona la Integración Actual

1. **En `src/utils/tokenManager.ts`:**
   - La URL está configurada a: `https://nike-bot-pro-production.up.railway.app`
   - El método `validateToken()` usa `GET /auth/validate` con Bearer token
   - El método `saveToken()` valida y guarda en localStorage

2. **En `src/App.tsx`:**
   - `checkAuthentication()` valida el token al iniciar
   - `handleTokenSubmit()` procesa cuando el usuario ingresa un token manualmente

3. **En `src/pages/TokenDialog.tsx`:**
   - El usuario pega un JWT token
   - Se valida automáticamente contra el backend de producción

## Testing Manual

Para probar la integración:

### 1. Registra un usuario
```bash
curl -X POST https://nike-bot-pro-production.up.railway.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}'
```

### 2. Copia el token de la respuesta

### 3. En la app Tauri, pega el token en el dialog

### 4. Si funciona, verás automáticamente validado ✅

## Documentación del Backend

Swagger UI disponible en:
```
https://nike-bot-pro-production.up.railway.app/docs
```

Allí puedes ver todos los esquemas, tipos de respuesta y probar endpoints directamente.

## Notas Importantes

- ✅ El cliente AHORA usa la URL de producción (antes usaba localhost)
- ✅ Los endpoints están correctos y coinciden con el backend
- ✅ Las variables de entorno en Railway ya están configuradas
- ✅ El backend valida tokens JWT correctamente
- ✅ Los headers `X-HWID` se envían automáticamente

## Próximos Pasos (Si Necesario)

1. **Agregar login/registro en la UI** - Actualmente solo valida tokens existentes
2. **Integrar endpoints de Stripe** - Para suscripciones premium
3. **Mejorar manejo de errores** - Con mensajes más amigables
4. **Testing E2E** - Prueba completa registro → validación → dashboard

¿Preguntas? Revisa el `tokenManager.ts` o pregunta en Discord.


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
