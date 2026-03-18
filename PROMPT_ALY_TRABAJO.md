# PROMPT PARA ALY — Tu Área de Trabajo Independiente
## Nike Bot Pro — App Tauri (React + Rust + Python)

---

## CONTEXTO GENERAL

Estamos migrando el Nike Bot de CustomTkinter a una app de escritorio Tauri (React frontend + Rust backend nativo + Python bot engine). La app tiene 6 secciones: **Login, Home, SKUs, Drop, Wallet, Config**.

### Arquitectura actual
```
client_app/          ← App Tauri (React + TypeScript + Rust)
├── src/
│   ├── pages/       ← Páginas principales (Login, Home, SKUs, Drop, Wallet, Config)
│   ├── services/    ← api.ts (Railway auth), botSocket.ts (WebSocket local)
│   ├── components/  ← Sidebar, Toast, SnakeLogo
│   └── App.tsx      ← Router principal + estado de sesión
├── src-tauri/       ← Backend Rust (comandos nativos)
│   └── src/lib.rs   ← Comandos: get_hwid, greet

nike_bot_pro/        ← Bot engine Python
├── bot_api.py       ← FastAPI server local (localhost:8000) — WebSocket + REST
├── stock_monitor.py ← Monitor de stock VTEX async
├── auth/            ← Módulo de autenticación (tokens, cookies, sesiones)
├── core/            ← Lógica de cuentas y estados
├── engines/         ← Motor de compra (Selenium/Playwright)
├── runtime/         ← Controller del bot
└── config/          ← Settings
```

### Servidores
| Servidor | URL | Propósito |
|----------|-----|-----------|
| Railway (remoto) | `https://nike-bot-pro-production.up.railway.app` | Auth/licencias JWT |
| Bot API (local) | `http://127.0.0.1:8000` | Control del bot, WebSocket |
| VTEX Nike.cl | `https://www.nike.cl/api/catalog_system/pub/products/search` | Catálogo productos |

---

## TU ÁREA DE TRABAJO (ALY)

### Archivos que TÚ modificas:
```
client_app/src/pages/Home.tsx      ← Dashboard (actualmente placeholder estático)
client_app/src/pages/Wallet.tsx    ← Gestión de cuentas (actualmente placeholder)
client_app/src/pages/Config.tsx    ← Configuración (60% implementado)
client_app/src/components/         ← Componentes compartidos si necesitas crear nuevos
```

### Archivos que NO debes tocar (los manejo yo):
```
client_app/src/pages/Drop.tsx       ← Bot control panel (implementado)
client_app/src/pages/Skus.tsx       ← Búsqueda VTEX (implementado)
client_app/src/pages/Login.tsx      ← Auth JWT (implementado)
client_app/src/services/api.ts      ← API Railway + Tauri Store
client_app/src/services/botSocket.ts ← WebSocket bot_api.py
client_app/src/App.tsx              ← Router principal (compartido, consultar antes de editar)
client_app/src-tauri/               ← Backend Rust
nike_bot_pro/bot_api.py             ← FastAPI server
nike_bot_pro/stock_monitor.py       ← Monitor stock
```

---

## TAREAS CONCRETAS PARA ALY

### 1. HOME.tsx — Dashboard Real (Prioridad ALTA)
**Estado actual:** 4 widgets con datos hardcoded, 3 botones que no hacen nada.

**Lo que necesita:**
- Conectar con `bot_api.py` para obtener datos reales:
  - Número real de cuentas (`GET http://127.0.0.1:8000/accounts`)
  - Cuentas autenticadas vs no autenticadas
  - Estado general del bot (corriendo/detenido)
- Los 3 botones de acción rápida deben navegar a las secciones correspondientes:
  - "Buscar SKU" → navegar a SKUs (`onNavigate("skus")`)
  - "Lanzar Drop" → navegar a Drop (`onNavigate("drop")`)
  - "Limpiar Carrito" → puede ser un `fetch POST` al bot_api
- Mostrar último evento de stock si hay uno guardado
- El plan y expiración del token ya vienen en `session.plan` y `session.exp`

**Props disponibles:** `{ session: UserSession, theme: string }`
Para navegar entre secciones, necesitas recibir `onNavigate` como prop desde App.tsx. Pide que se te pase.

### 2. WALLET.tsx — CRUD de Cuentas Nike (Prioridad ALTA)
**Estado actual:** Tabla estática con 7 cuentas mockeadas.

**Lo que necesita:**
- **Listar cuentas reales** desde `GET http://127.0.0.1:8000/accounts`
- **Agregar cuenta**: Formulario modal con email + password + SKU target
- **Editar cuenta**: Modal para cambiar SKU target, talla, etc.
- **Eliminar cuenta**: Con confirmación
- **Importar/Exportar**: Botón para cargar JSON con múltiples cuentas
- Estado de cada cuenta: `NO_AUTH`, `AUTHENTICATED`, `RUNNING`, `SUCCESS`, `ERROR`
- **API endpoints disponibles** (ya existen en bot_api.py):
  ```
  GET  /accounts          → Lista todas las cuentas
  POST /accounts          → Agregar cuenta { email, password, sku? }
  PUT  /accounts/{email}  → Editar cuenta
  DELETE /accounts/{email} → Eliminar cuenta
  ```

### 3. CONFIG.tsx — Completar Funcionalidades (Prioridad MEDIA)
**Estado actual:** 60% implementado. Logout funciona. Theme toggle funciona.

**Lo que falta:**
- **Botón "Copiar token"**: Implementar `navigator.clipboard.writeText(session.token)` con feedback Toast
- **Botón "Renovar plan"**: Puede redirigir a un link externo o mostrar info de contacto
- **Sección de configuración del bot** (NUEVA):
  - Delay entre intentos (ms)
  - Número máximo de reintentos
  - Región/país target
  - Proxy settings (host:port:user:pass)
  - Guardar config en `POST http://127.0.0.1:8000/config`
  - Cargar config con `GET http://127.0.0.1:8000/config`
- **Info del sistema**: Versión de la app, HWID (ya disponible con `invoke("get_hwid")`)

---

## REGLAS TÉCNICAS

### Stack y Convenciones
- **React 19** + **TypeScript** (strict)
- **NO usar librerías UI** adicionales — todo es CSS inline con el objeto `theme` de [theme.ts](client_app/src/theme.ts)
- Tema dark/light via prop `theme` (tipo `"dark" | "light"`)
- Para colores: `import { getTheme } from "../theme"` → `const t = getTheme(theme)`
- Toast notifications: `import Toast from "../components/Toast"`
- **NO usar localStorage** — usar `@tauri-apps/plugin-store` (ver api.ts para ejemplo)
- Para llamadas IPC a Rust: `import { invoke } from "@tauri-apps/api/core"`

### Cómo hacer fetch al bot (localhost:8000)
```tsx
// GET
const res = await fetch("http://127.0.0.1:8000/accounts");
const accounts = await res.json();

// POST
await fetch("http://127.0.0.1:8000/accounts", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ email, password, sku })
});
```

### Tipos disponibles (types.ts)
```tsx
interface UserSession {
  user: string;
  plan: string;
  token: string;
  exp: number;
  hwid: string;
}

interface BotAccount {
  email: string;
  state: string;
  sku?: string;
  size?: string;
}
```

### Estructura de un componente página
```tsx
import React, { useState, useEffect } from "react";
import { getTheme } from "../theme";
import Toast from "../components/Toast";
import type { UserSession } from "../types";

interface Props {
  session: UserSession;
  theme: "dark" | "light";
}

export default function MiPagina({ session, theme }: Props) {
  const t = getTheme(theme);
  const [toast, setToast] = useState<{ msg: string; type: "ok" | "err" } | null>(null);

  return (
    <div style={{ padding: 32, color: t.text }}>
      {toast && <Toast message={toast.msg} type={toast.type} onClose={() => setToast(null)} />}
      {/* tu contenido */}
    </div>
  );
}
```

---

## GIT WORKFLOW

### Rama de trabajo
```bash
git checkout feat/tauri-client     # Trabaja siempre en esta rama
git pull origin feat/tauri-client   # Antes de empezar, actualiza
```

### Antes de commitear
```bash
cd client_app
npm run build                      # Verificar que compila sin errores
```

### Commit
```bash
git add client_app/src/pages/Home.tsx client_app/src/pages/Wallet.tsx client_app/src/pages/Config.tsx
git commit -m "feat(wallet): CRUD de cuentas Nike con API local"
git push origin feat/tauri-client
```

### Prefijos de commit
- `feat(home):` para Home.tsx
- `feat(wallet):` para Wallet.tsx
- `feat(config):` para Config.tsx
- `fix(page):` para correcciones
- `style(page):` para cambios visuales

---

## CÓMO PROBAR

### 1. Levantar el bot API (en una terminal)
```bash
cd nike_bot_pro
python bot_api.py
# Debería decir: Uvicorn running on http://127.0.0.1:8000
```

### 2. Levantar la app Tauri (en otra terminal)
```bash
cd client_app
npm run tauri dev
# Abre la ventana de la app
```

### 3. O solo el frontend (más rápido, sin Rust)
```bash
cd client_app
npm run dev
# Abre http://localhost:1420 en el navegador
```

---

## CONTACTO / DUDAS
- Si necesitas que `App.tsx` te pase props adicionales (como `onNavigate`), mándame mensaje y lo agrego.
- Si necesitas un nuevo endpoint en `bot_api.py`, descríbeme qué necesitas y lo creo.
- **NO modifiques** archivos fuera de tu área — si algo te bloquea, avísame.

---

*Última actualización: $(date). Rama: `feat/tauri-client`*
