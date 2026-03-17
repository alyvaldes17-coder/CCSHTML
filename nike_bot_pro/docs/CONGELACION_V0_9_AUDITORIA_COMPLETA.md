# CONGELACION FLUJO V0.9 - AUDITORIA COMPLETA

**Objetivo**: 1 camino ganador. Eliminar TODO lo demás.

---

## PARTE 1: CÓDIGO A BORRAR DEFINITIVAMENTE

### ❌ ARQUITECTURA ALTERNATIBA (NO MANTENER)

**runner/ (TODO)**
- `state_machine.py` - Máquina de 8+ estados (SESSION_SEED, PRICING_WAIT, etc)
- `state_machine_orchestrator.py` - Orquestador async
- `worker.py` - Worker con loops
- `worker_fixed.py` - Worker fijo

**Por qué**: Flujo V0.9 es simple (10 pasos secuenciales). StateMachine es complejo y tiene caminos alternativos (SESSION_SEED, PRICING_WAIT, PAYMENT_BANK_SELECTED, etc). INCOMPATIBLE.

---

### ❌ BRIDGE DE COOKIES ENTRE BROWSER ↔ BACKEND

**auth/profile_cookies.py**
- `extract_cookies_from_profile()` - Extrae cookies del SQLite de Chrome
- `get_cookies_for_account()` - Fallback a tokens.json
- **Por qué**: Flujo V0.9 NO usa bridge. Backend limpio, aislado. No hereda cookies de browser.

**auth/session_builder.py**
- `build_requests_session()` - Construye sesión con cookies del profile
- **Problema**: Intenta leer SQLite de Chrome. En V0.9, backend crea su propia sesión HTTP.

**auth/session_bridge.py**
- `async_extract_cookies()` - Extrae de Playwright context
- **Problema**: V0.9 no sincroniza cookies. Backend muere después del freeze.

**auth/session_store.py**
- `SessionStore` - "Fuente única de verdad para cookies"
- **Problema**: Implica que cookies persisten y se reutilizan. V0.9 crea sesión nueva cada drop.

**auth/session_check.py**
- `check_session_nike()` - Valida cookies contra VTEX
- `setup_account_login()` - Abre Chrome para login
- **Problema**: Duplicado de `login_runner.py`. Eliminar.

---

### ❌ CAMINOS ALTERNATIVOS (SESSION_SEED, PRICING_WAIT, etc)

**engines/session_validator.py**
- `SessionValidator.has_valid_cookies()` - Valida contra /api/checkout/pub/orderForm
- **Problema**: V0.9 NO hace session seed. El backend es directo: HTTP GET → ATC.

**engines/state_machine_orchestrator.py**
- Estados: ATC, PRICING_WAIT, PAYMENT_BANK_SELECTED
- **Problema**: V0.9 solo tiene: ATC → PRICE_CHECK → FREEZE → HANDOVER.

---

### ❌ WATCHERS Y RETRIES INTELIGENTES

**engines/** (TODO lo que no sea Playwright base)
- `playwright_engine_v2.py` - Motor con watchers
- Cualquier lógica de "retry inteligente"
- **Problema**: V0.9 = 0 watchers. Si falla, muere.

---

### ❌ MODOS ALTERNATIVOS (safe, fast, fallback)

**controller/controller.py**
- `Controller` - Orquestador con múltiples modos
- **Problema**: V0.9 = 1 modo único.

**runtime/bot_controller.py**
- Manejo de múltiples estados
- Price lock persistente
- **Problema**: V0.9 no tiene price lock. Backend deja orderForm en estado congelado.

---

### ❌ UI AVANZADA

**ui/app.py** (líneas >100)
- Botones de CHECK_SESSION, MONITORING, etc
- Suscriptores de eventos
- **Problema**: V0.9 solo necesita 2 botones: LOGIN y PLAY. Eliminar complejidad.

**ui/account_editor.py**
- Editor de cuentas
- **Problema**: V0.9 no necesita editar. Solo seleccionar y ejecutar.

**ui/app_old.py**
- Interfaz antigua
- **Problema**: BORRAR completamente.

---

### ❌ MANAGER Y SUPERVISOR

**manager/account_manager.py**
- Gestor de cuentas con estados persistentes
- **Problema**: V0.9 usa subprocess. No necesita manager.

**manager/supervisor.py**
- Supervisor con workers backend
- **Problema**: V0.9 no tiene workers. Multiprocessing directo.

---

### ❌ TESTS DE ARQUITECTURA ANTIGUA

Eliminar completamente:
- `tests/test_state_machine_flow.py` - Tests para StateMachine (no existe en V0.9)
- `tests/test_session_validator.py` - Tests para validador (no existe en V0.9)
- `test_dual_mode.py` - Modo dual (no existe)
- `test_modo_eterno.py` - Modo eterno (no existe)
- `test_banco_fintoc_final.py` - FINTOC (no existe en V0.9)
- `test_propagation_payment_mode.py` - Payment mode (no existe)
- Todos los `test_*.py` que NO sean para login_runner.py o multiprocessing_runner.py

---

### ❌ DOCUMENTACIÓN OBSOLETA

Eliminar:
- `ARQUITECTURA_FINAL_6MEJORAS.md` - Vieja arquitectura
- `ARQUITECRURA_FINAL_BLINDADA.md` - Vieja arquitectura
- `ESTRATEGIAS_COMBATE.md` - Vieja estrategia
- `FIX_PERFIL_PERSISTENTE_COMPLETO.txt` - Vieja solución
- `REPARACIONES_FINALES.md` - Vieja estrategia
- Cualquier `.md` que mencione SESSION_SEED, PRICING_WAIT, etc

---

### ❌ CONFIG Y SETUP ANTIGUO

Eliminar:
- `setup_cuentas.py` - Setup antiguo
- `setup_login.py` - Setup antiguo
- `force_login.py` - Debug antiguo
- `force_check.py` - Debug antiguo
- `quick_start_connected.py` - Script antiguo
- Cualquier `test_*.py` de debug

---

### ❌ DIRECTORIES CON CÓDIGO MUERTO

- `controller/` - Control antiguo
- `manager/` - Manager antiguo
- `worker/` - Workers antiguos
- `runner/` - Runner antiguo (EXCEPTO si es el nuevo multiprocessing_runner)
- `engines/` - Engines antiguos
- `vtex/` - VTEX TLS/HTTP (no en V0.9)

---

## PARTE 2: CÓDIGO A MANTENER

### ✅ LOGIN

**login_runner.py**
- `login_master(user)` - Abre Chrome, usuario loguea, crea .login_ok
- Status: MANTENER tal cual
- No modificar

---

### ✅ PROFILE MANAGEMENT

**profile_manager_v2.py**
- `clone_auth_to_run(user)` - Clona profile_login → profile_run, verifica .login_ok
- Status: MANTENER tal cual
- No modificar

---

### ✅ BACKEND ATC

**runtime/backend_vtex.py**
- `backend_run(user, profile_run, sku)` - HTTP GET /checkout/cart/add, price check
- Status: MANTENER - YA IMPLEMENTADO EN FLUJO V0.9
- No modificar

---

### ✅ MULTIPROCESSING EXECUTOR

**runtime/multiprocessing_runner.py**
- `preflight(user, profile_run)` - Headless Nike verify
- `run_account(user, sku, bus)` - Flujo 10 pasos
- `run_accounts_mp(accounts, sku, bus)` - Parallelización (spawn)
- Status: MANTENER - YA IMPLEMENTADO EN FLUJO V0.9
- No modificar

---

### ✅ PROCESS STATES

**runtime/process_states.py**
- Estados: STARTING, CLONING, PREFLIGHT, BACKEND_SETUP, BACKEND_ATC, BACKEND_PRICE_OK, FREEZE_BACKEND, HANDOVER, WAITING_HUMAN, DONE, ERROR
- Status: MANTENER - ACTUALIZADO PARA FLUJO V0.9
- No modificar

---

### ✅ STATE BUS

**runtime/state_bus.py**
- `make_state_bus()` - Crea multiprocessing.Queue()
- Status: MANTENER
- No modificar

---

### ✅ UI (MINIMAL)

**ui/play_launcher.py**
- `launch_play_for_accounts(accounts, sku, bus)` - Bridge UI → multiprocessing
- Status: MANTENER - ACTUALIZADO PARA FLUJO V0.9
- No modificar

**ui/state_listener.py**
- `start_state_listener(bus, on_update)` - Background thread, lee estados
- Status: MANTENER
- No modificar

---

### ✅ MINIMAL UI APP

**ui/app.py** (SIMPLIFICADO)
- Solo 2 funciones principales:
  1. `on_login_button()` → `subprocess.Popen([..., "login_runner.py", account_name])`
  2. `on_play_button()` → `launch_play_for_accounts([...], sku, bus)`
- Helpers:
  - `profile_login_path(account_name)`
  - `profile_run_path(account_name)`
- Status: SIMPLIFICAR - eliminar todo excepto estos 2 botones y helpers
- Reescribir para que sea minimal

---

### ✅ DOCUMENTACION NUEVA

**FLUJO_CONGELADO_V0_9.md** - MANTENER
**IMPLEMENTACION_FLUJO_V0_9_COMPLETADA.md** - MANTENER

---

## PARTE 3: MAPA DE BORRADOS

| Archivo/Directorio | Acción | Razón |
|-------------------|--------|-------|
| runner/ | BORRAR | Estado machine antigua |
| controller/ | BORRAR | Controller antiguo |
| manager/ | BORRAR | Manager antiguo |
| worker/ | BORRAR | Workers antiguos |
| engines/ | BORRAR | Engines antiguos (excepto base) |
| vtex/ | BORRAR | VTEX TLS no en V0.9 |
| auth/profile_cookies.py | BORRAR | Bridge de cookies |
| auth/session_builder.py | BORRAR | Builder antiguo |
| auth/session_bridge.py | BORRAR | Bridge antiguo |
| auth/session_store.py | BORRAR | Store antiguo |
| auth/session_check.py | BORRAR | Duplicado de login_runner |
| engines/session_validator.py | BORRAR | Validador antiguo |
| ui/app_old.py | BORRAR | UI antigua |
| ui/account_editor.py | BORRAR | Editor antiguo |
| tests/ | BORRAR (todos) | Tests antiguos |
| setup_cuentas.py | BORRAR | Setup antiguo |
| setup_login.py | BORRAR | Setup antiguo |
| force_login.py | BORRAR | Debug antiguo |
| force_check.py | BORRAR | Debug antiguo |
| quick_start_connected.py | BORRAR | Script antiguo |
| *.md (arquitectura vieja) | BORRAR | Documentación obsoleta |

---

## PARTE 4: ESQUELETO FINAL (V0.9 CONGELADO)

```
nike_bot_pro/
├── auth/
│   ├── __init__.py
│   └── (solo directorios: cuenta1/, cuenta2/, etc)
│
├── runtime/
│   ├── __init__.py
│   ├── process_states.py     ✅ (ProcState enum)
│   ├── state_bus.py          ✅ (make_state_bus)
│   ├── backend_vtex.py       ✅ (backend_run)
│   └── multiprocessing_runner.py ✅ (run_account, run_accounts_mp)
│
├── ui/
│   ├── __init__.py
│   ├── state_listener.py     ✅ (start_state_listener)
│   ├── play_launcher.py      ✅ (launch_play_for_accounts)
│   └── app.py                ✅ (UI SIMPLIFICADA - solo 2 botones)
│
├── login_runner.py           ✅ (login_master)
├── profile_manager_v2.py     ✅ (clone_auth_to_run)
│
├── FLUJO_CONGELADO_V0_9.md   ✅ (Documentación)
├── IMPLEMENTACION_FLUJO_V0_9_COMPLETADA.md ✅
│
└── config/ (OPCIONAL - si hay SKU config)
    └── drop_config.json (SKU, URL, etc)
```

---

## PARTE 5: CONFIRMACION EXPLÍCITA

### ¿Hay más de un camino de ejecución?

**LOGIN**: ✅ 1 camino único
- Usuario abre Chrome → loguea → cierra → verifica → .login_ok

**PLAY**: ✅ 1 camino único
- clone → preflight → backend_setup → backend_atc → price_check → freeze → handover → magic_link → waiting_human → exit

**No hay**:
- ❌ SESSION_SEED (browser cookie sync)
- ❌ PRICING_WAIT (espera de precio)
- ❌ PAYMENT_BANK_SELECTED (selección de banco)
- ❌ Fallback a ATC manual
- ❌ Watchers activos después del freeze
- ❌ Retries inteligentes
- ❌ Modos safe/fast

---

### ¿Es determinista?

✅ SÍ. Flujo fijo:
1. LOGIN (off-drop)
2. PRE-PLAY CHECK (5min antes)
3-6. BACKEND (< 1s)
7-10. HANDOVER + HUMANO

Si algo falla → ERROR, fin. Sin variantes.

---

### ¿Backend vive más allá del FREEZE?

❌ NO. Backend muere en PASO 6 (FREEZE_BACKEND):
- `session.close()` después de price_check
- No hay más requests HTTP
- No hay watchers, no hay polling

A partir de PASO 7 → solo browser + humano.

---

## VERDICT FINAL

**✅ CONGELADO PARA V0.9**

Este sistema está listo para:
- ✅ Setups de cuentas (LOGIN)
- ✅ Pre-drop checks (PREFLIGHT)
- ✅ Drops competidos (BACKEND < 1s + HANDOVER inmediato)

NO tiene:
- ❌ Caminos alternativos
- ❌ Fallbacks
- ❌ Iteración durante combate
- ❌ Complejidad innecesaria

**CONGELADO. LISTO PARA DROPS.**

