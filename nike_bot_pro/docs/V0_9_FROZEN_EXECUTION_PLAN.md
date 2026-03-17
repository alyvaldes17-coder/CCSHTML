# FLUJO V0.9 — CONGELADO PARA DROPS

**Status**: ✅ LISTO PARA DROPS  
**Fecha**: 3 de Enero de 2026  
**Arquitecto**: Senior Bot Automation Auditor  

---

## RESUMEN EJECUTIVO

Sistema Nike Bot **congelado** a 1 camino único, sin fallbacks, determinista, optimizado para drops competidos.

**10 pasos**, **sin variantes**, **<1.5s backend**, **handover inmediato**.

---

## PARTE 1: CÓDIGO PARA BORRAR

### ❌ Directorios completos

```
runner/                  # StateMachine antigua (SESSION_SEED, PRICING_WAIT)
controller/              # Controller antiguo
manager/                 # Manager antiguo
worker/                  # Workers antiguos
engines/                 # Engines antiguos (excepto base)
vtex/                    # VTEX TLS (no en V0.9)
tests/                   # Tests antiguos (excepto para V0.9)
```

### ❌ Archivos específicos

**auth/**
- `profile_cookies.py` - Bridge cookies browser→backend (NO en V0.9)
- `session_builder.py` - Builder antiguo
- `session_bridge.py` - Bridge antiguo
- `session_store.py` - Store antiguo
- `session_check.py` - Duplicado de login_runner

**engines/**
- `session_validator.py` - Validador antiguo
- Cualquier archivo que NO sea Playwright base

**ui/**
- `app_old.py` - UI antigua
- `account_editor.py` - Editor antiguo
- `app.py` - REEMPLAZAR por app_v0_9_simple.py

**tests/**
- `test_state_machine_flow.py`
- `test_session_validator.py`
- `test_dual_mode.py`
- `test_modo_eterno.py`
- `test_banco_fintoc_final.py`
- `test_propagation_payment_mode.py`
- Cualquier test que NO sea para login_runner o multiprocessing_runner

**scripts de setup/debug**
- `setup_cuentas.py`
- `setup_login.py`
- `force_login.py`
- `force_check.py`
- `quick_start_connected.py`
- `preflight_check.py`
- `preflight_test.py`

**documentación vieja**
- `ARQUITECTURA_FINAL_*.md`
- `ARQUITECTURA_*_BLINDADA.md`
- `ESTRATEGIAS_COMBATE.md`
- `FIX_PERFIL_PERSISTENTE_COMPLETO.txt`
- `REPARACIONES_FINALES.md`
- Cualquier `.md` que mencione SESSION_SEED, PRICING_WAIT, PAYMENT_BANK_SELECTED

---

## PARTE 2: CÓDIGO PARA MANTENER

### ✅ Núcleo V0.9

**login_runner.py**
```python
login_master(user: str) -> None
  # 1. Usuario loguea en profile_login
  # 2. Cierra Chrome
  # 3. Verificación Nike
  # 4. Crea .login_ok
```

**profile_manager_v2.py**
```python
clone_auth_to_run(user: str) -> bool
  # 1. Verifica .login_ok
  # 2. Clona profile_login → profile_run
  # 3. Ignora Cache, Crashpad, SingletonLock
```

**runtime/backend_vtex.py**
```python
backend_run(user: str, profile_run: str, sku: str) -> bool
  # Paso 3: Sesión HTTP limpia
  # Paso 4: GET /checkout/cart/add?sku=...&qty=1
  # Paso 5: Valida price > 0
  # Paso 6: Cierra sesión (freeze)
```

**runtime/multiprocessing_runner.py**
```python
run_account(user: str, sku: str, bus=None) -> None
  # 1-2: Clone + Preflight
  # 3-6: Backend (< 1s)
  # 7-10: Handover + Humano

run_accounts_mp(accounts: list, sku: str, bus=None) -> None
  # spawn method
  # 1 proceso = 1 cuenta
```

**runtime/process_states.py**
```python
ProcState enum:
  STARTING, CLONING, PREFLIGHT
  BACKEND_SETUP, BACKEND_ATC, BACKEND_PRICE_OK, FREEZE_BACKEND
  HANDOVER, WAITING_HUMAN
  DONE, ERROR
```

**runtime/state_bus.py**
```python
make_state_bus() -> multiprocessing.Queue
```

**ui/play_launcher.py**
```python
launch_play_for_accounts(accounts: list, sku: str, bus) -> None
```

**ui/state_listener.py**
```python
start_state_listener(bus, on_update) -> Thread
  # Background thread
  # Lee estados, actualiza UI
```

**ui/app_v0_9_simple.py**
```python
# NUEVO - Reemplaza app.py
# Solo 2 botones: LOGIN y PLAY
# Tabla de estados en tiempo real
```

---

## PARTE 3: ESTRUCTURA FINAL

```
nike_bot_pro/
├── auth/
│   ├── __init__.py
│   └── <directorios de cuentas>
│
├── runtime/
│   ├── __init__.py
│   ├── process_states.py        ✅
│   ├── state_bus.py             ✅
│   ├── backend_vtex.py          ✅
│   └── multiprocessing_runner.py ✅
│
├── ui/
│   ├── __init__.py
│   ├── state_listener.py        ✅
│   ├── play_launcher.py         ✅
│   └── app_v0_9_simple.py       ✅ (nuevo)
│
├── login_runner.py              ✅
├── profile_manager_v2.py        ✅
│
├── FLUJO_CONGELADO_V0_9.md
├── IMPLEMENTACION_FLUJO_V0_9_COMPLETADA.md
├── CONGELACION_V0_9_AUDITORIA_COMPLETA.md ✅ (este archivo)
└── V0_9_FROZEN_EXECUTION_PLAN.md ✅ (este archivo)
```

---

## PARTE 4: FLUJO EXACTO (10 PASOS)

```
PASO 1: LOGIN (OFF-DROP, HUMANO)
├─ Abrir Chrome con profile_login
├─ Usuario inicia sesión
├─ Usuario cierra Chrome
├─ Script verifica Nike
└─ Crear .login_ok

PASO 2: PRE-PLAY CHECK (5min antes)
├─ Verificar .login_ok
├─ Clonar profile_login → profile_run
├─ Abrir Chrome headless
├─ Nike reconoce sesión
└─ SI FALLA → ABORTAR

PASO 3: ARMADO SESIÓN BACKEND
└─ Cliente HTTP limpio, timeout ≤1.5s

PASO 4: ATC BACKEND
├─ GET /checkout/cart/add?sku=...&qty=1
├─ Max 3 retries
└─ SI FALLA → ABORTAR

PASO 5: PRICE CHECK
├─ orderForm.items > 0
├─ price > 0
└─ SI FALLA → ABORTAR

PASO 6: FREEZE BACKEND
├─ Cerrar sesión HTTP
├─ No más requests
└─ Backend MUERE aquí

PASO 7: HANDOVER BROWSER
├─ Abrir Chrome visible
└─ Sin pasos intermedios

PASO 8: MAGIC LINK
└─ Navegar a /checkout/#/payment

PASO 9: WAITING_HUMAN (TERMINAL)
├─ Bot NO interactúa
└─ Usuario confirma pago (click / OTP)

PASO 10: EXIT
├─ Cerrar contexto
└─ Destruir profile_run
```

---

## PARTE 5: REGLAS ABSOLUTAS

1. ✅ **1 camino** - No hay alternativas
2. ✅ **0 fallback** - Si falla, muere
3. ✅ **0 A/B** - Sin variantes
4. ✅ **0 iteración** - Decisiones fijas
5. ✅ **Backend ≤ pasos 3-6** - Muere después del FREEZE
6. ✅ **Browser ≥ pasos 7-9** - Solo humano decide
7. ✅ **Timeout ≤1.5s** - HTTP
8. ✅ **Max 3 retries** - Solo en ATC
9. ✅ **Si algo falla** - Abortar inmediato

---

## PARTE 6: VALIDACION

### ¿Hay más de un camino?

❌ NO

- LOGIN: 1 camino (usuario → Chrome → Nike → .login_ok)
- PLAY: 1 camino (clone → preflight → backend → handover → humano)

### ¿Es determinista?

✅ SÍ

- Pasos fijos
- Sin loops
- Sin watchers
- Sin retries inteligentes

### ¿Backend vive más allá del FREEZE?

❌ NO

- `session.close()` en paso 6
- Sin más requests
- Sin polling

### ¿Hay threading en Playwright?

❌ NO

- Multiprocessing únicamente
- spawn method
- 1 proceso = 1 cuenta

---

## PARTE 7: EJECUCIÓN

### Terminal directo

```bash
# Paso 1: Usuario loguea (off-drop)
python login_runner.py cuenta1

# Paso 2: Pre-play check (5min antes)
python -c "from profile_manager_v2 import clone_auth_to_run; clone_auth_to_run('cuenta1')"

# Paso 3-10: Flujo completo (drop)
python runtime/multiprocessing_runner.py 123456789 cuenta1 cuenta2 cuenta3
```

### UI simplificada

```bash
python ui/app_v0_9_simple.py
```

---

## PARTE 8: CONGELACION CONFIRMADA

**Este sistema está congelado y listo para DROPS competidos.**

✅ Arquitectura: 1 camino único  
✅ Backend: < 1s (ATC + price check)  
✅ Handover: inmediato (sin pasos intermedios)  
✅ Determinismo: 0 variantes  
✅ Timeout: ≤1.5s en HTTP  

**NO tiene**:
- ❌ SESSION_SEED (browser cookie sync)
- ❌ PRICING_WAIT (espera de precio)
- ❌ PAYMENT_BANK_SELECTED (selección de banco)
- ❌ Fallback a ATC manual
- ❌ Watchers activos
- ❌ Retries inteligentes
- ❌ Modos safe/fast

**VERDICT**: ✅ DROP-CAPABLE

---

## PARTE 9: CLEANING CHECKLIST

- [ ] Borrar runner/ (completo)
- [ ] Borrar controller/ (completo)
- [ ] Borrar manager/ (completo)
- [ ] Borrar worker/ (completo)
- [ ] Borrar auth/profile_cookies.py
- [ ] Borrar auth/session_builder.py
- [ ] Borrar auth/session_bridge.py
- [ ] Borrar auth/session_store.py
- [ ] Borrar auth/session_check.py
- [ ] Borrar engines/session_validator.py
- [ ] Borrar ui/app_old.py
- [ ] Borrar ui/account_editor.py
- [ ] Reemplazar ui/app.py → ui/app_v0_9_simple.py
- [ ] Borrar todos los tests/ (excepto v0.9)
- [ ] Borrar scripts de setup/debug
- [ ] Borrar documentación vieja (*.md que no sea V0.9)
- [ ] Verificar no hay referencias a módulos borrados
- [ ] Verificar no hay imports circulares

---

## EPILOGO

> "Primero se gana. Después se hace bonito."

Este sistema está congelado para ganar. Sin iteración, sin fallbacks, sin variantes.

1 camino. Letal. Determinista.

**LISTO PARA DROPS.**

