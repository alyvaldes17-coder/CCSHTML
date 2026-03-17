"""
ARQUITECTURA FINAL - 6 MEJORAS IMPLEMENTADAS
============================================

Diagrama de flujo y responsabilidades claras.
"""

# ═══════════════════════════════════════════════════════════════════════
# DIAGRAMA 1: TRANSICIONES DE ESTADOS
# ═══════════════════════════════════════════════════════════════════════

"""
                    ┌─────────────────────────────────────┐
                    │  NO_AUTH (Inicial)                  │
                    │  Usuario no logueado en Nike        │
                    └─────────────┬───────────────────────┘
                                  │
                    ┌─────────────▼──────────────────────┐
                    │ LOGIN_IN_PROGRESS (MEJORA #2)       │
                    │ Chrome abierto, usuario logueando   │
                    │ [LOGIN BUTTON BLOQUEADO]            │
                    └─────────────┬───────────────────────┘
                                  │
                          ┌────────┴────────┐
                          │                 │
                    ❌ FALLA         ✅ READY
                          │                 │
                    ┌─────▼──┐      ┌──────▼───────────┐
                    │ NO_AUTH │      │ READY (MEJORA #1)│
                    └────────┘      │ Sesión validada  │
                                    │ [PLAY habilitado]│
                                    └──────┬───────────┘
                                           │
                                   CLICK [PLAY]
                                           │
                                    ┌──────▼─────────────┐
                                    │ MONITORING         │
                                    │ Backend-only loop  │
                                    │ Sin Chrome abierto │
                                    └──────┬─────────────┘
                                           │
                                    [MONITOREAR...]
                                           │
                              precio ENCONTRADO
                                           │
                                    ┌──────▼──────────────────┐
                                    │ PRICE_LOCKED (MEJORA #4)│
                                    │ Precio guardado + bloq.  │
                                    │ Transición → EXECUTING   │
                                    └──────┬──────────────────┘
                                           │
                                    ┌──────▼────────────────────┐
                                    │ EXECUTING (MEJORA #5)      │
                                    │ Chrome abierto + /payment  │
                                    │ Esperando pago humano      │
                                    └────────────────────────────┘
"""

# ═══════════════════════════════════════════════════════════════════════
# DIAGRAMA 2: RESPONSABILIDADES CLARAS
# ═══════════════════════════════════════════════════════════════════════

"""
┌─────────────────────────────────────────────────────────────────┐
│                          UI LAYER (CustomTkinter)               │
│  - Mostrar botones LOGIN/PLAY                                   │
│  - Habilitar/deshabilitar según estado (MEJORA #6)              │
│  - Mostrar status en tiempo real                                │
│  - Llamar controller.handle_btn_login_click()                   │
│  - Llamar controller.handle_btn_play_click()                    │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│                 BotController (runtime/bot_controller.py)       │
│  ✅ Gestionar estados (NO booleanos)                            │
│  ✅ Validación REAL de sesión (headless check) - MEJORA #1      │
│  ✅ LOGIN_IN_PROGRESS bloqueado - MEJORA #2                     │
│  ✅ Worker confía en estado, no flags - MEJORA #3               │
│  ✅ Price lock persistente - MEJORA #4                          │
│  ✅ Magic link a /payment - MEJORA #5                           │
│  ✅ Botones bloqueados - MEJORA #6                              │
│                                                                  │
│  Métodos públicos:                                              │
│  - handle_btn_login_click() → abre PlaywrightEngine             │
│  - handle_btn_play_click(sku) → lanza worker_loop()             │
│  - validate_session_real() → valida con headless                │
│  - is_login_enabled() → para UI                                 │
│  - is_play_enabled() → para UI                                  │
│  - get_status_text() → para mostrar                             │
│  - stop_worker() → parar gracefully                             │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│           PlaywrightEngine (engines/playwright_engine_v2.py)    │
│  ✅ launch_manual_login() → Chrome para usuario                 │
│  ✅ launch_checkout_mission() → Chrome para pago                │
│  ✅ validate_session_real() → headless check                    │
│                                                                  │
│  CRÍTICO: NO toma decisiones, solo ejecuta lo que se le pide    │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│         Playwright SDK (sync_playwright)                         │
│  - launch_persistent_context()                                  │
│  - page.goto()                                                  │
│  - page.wait_for_event()                                        │
└─────────────────────────────────────────────────────────────────┘
"""

# ═══════════════════════════════════════════════════════════════════════
# TABLA: COMPARACIÓN ANTES vs DESPUÉS
# ═══════════════════════════════════════════════════════════════════════

"""
┌──────────────────────────────────────────────────────────────────────────┐
│ MEJORA # │ PROBLEMA ANTES         │ SOLUCIÓN IMPLEMENTADA              │
├──────────────────────────────────────────────────────────────────────────┤
│    1     │ is_logged_in = True    │ validate_session_real() (headless)  │
│          │ (débil, solo bool)     │ (navegación real, no check archivo) │
├──────────────────────────────────────────────────────────────────────────┤
│    2     │ Podías spamear LOGIN   │ LOGIN_IN_PROGRESS estado            │
│          │ 5 veces               │ (botón bloqueado durante)           │
├──────────────────────────────────────────────────────────────────────────┤
│    3     │ Worker dependía de     │ Worker solo confía en                │
│          │ is_logged_in flag      │ state == AccountState.READY          │
├──────────────────────────────────────────────────────────────────────────┤
│    4     │ print("PRICE_LOCKED")  │ self.price_lock = {"sku", "price",  │
│          │ (perdible)             │ "ts"} (persistente)                 │
├──────────────────────────────────────────────────────────────────────────┤
│    5     │ Navegación implícita   │ page.goto("/checkout/#/payment")    │
│          │ en browser             │ explícito (MEJORA #5)               │
├──────────────────────────────────────────────────────────────────────────┤
│    6     │ Botones siempre        │ is_login_enabled() e                │
│          │ habilitados            │ is_play_enabled() en UI             │
│          │ (user error)           │ (bloquean según estado)             │
└──────────────────────────────────────────────────────────────────────────┘
"""

# ═══════════════════════════════════════════════════════════════════════
# FLUJO IDEAL DE UNA COMPRA (Con las 6 mejoras)
# ═══════════════════════════════════════════════════════════════════════

"""
[USUARIO]
   │
   └─► [UI] Clickea botón LOGIN
       │
       └─► controller.handle_btn_login_click()
           │
           ├─► state = LOGIN_IN_PROGRESS ✅ MEJORA #2
           │
           ├─► engine.launch_manual_login()
           │   │
           │   └─► Chrome abre + Nike login
           │       Usuario loguea
           │       Usuario cierra Chrome
           │       Cookies se guardan en profile_pw
           │
           ├─► engine.validate_session_real() ✅ MEJORA #1
           │   │
           │   └─► Headless check (NO solo "archivo existe")
           │       Navega a /checkout → ¿redirect a /login?
           │       SI → sesión expirada
           │       NO → sesión válida ✅
           │
           └─► state = READY (o NO_AUTH si falló)

[USUARIO ESPERA]
   │
   └─► [UI] Clickea botón PLAY
       │
       ├─► if state != READY: return ✅ MEJORA #3
       │
       └─► controller.handle_btn_play_click("12345")
           │
           └─► worker_loop("12345")
               │
               ├─► state = MONITORING
               │   
               ├─► [LOOP sin Chrome]
               │   Golpear endpoints
               │   Monitorear precio
               │   SIN Playwright abierto = RÁPIDO
               │   
               ├─► [Si precio ENCONTRADO]
               │   │
               │   ├─► self.price_lock = {...} ✅ MEJORA #4
               │   │
               │   ├─► state = PRICE_LOCKED
               │   │
               │   └─► state = EXECUTING
               │
               └─► engine.launch_checkout_mission(sku_url)
                   │
                   ├─► page.goto(magic_link)
                   │
                   ├─► page.goto("/checkout/#/payment") ✅ MEJORA #5
                   │   (Explícito, no confiar en navegación implícita)
                   │
                   └─► Chrome espera confirmación humana
                       Usuario ve Nike en /payment
                       Usuario confirma en su banco
                       Fin

[SUCCESS]
"""

# ═══════════════════════════════════════════════════════════════════════
# GUÍA DE INTEGRACIÓN EN 5 PASOS
# ═══════════════════════════════════════════════════════════════════════

"""
PASO 1: Crear/reemplazar archivos
   ├─ core/account_state.py (NEW) ✅
   ├─ engines/playwright_engine_v2.py (NEW) ✅
   ├─ runtime/bot_controller.py (NEW) ✅
   └─ INTEGRACION_BOTCONTROLLER.md (referencia)

PASO 2: Actualizar ui/app.py
   ├─ Importar BotController + AccountState
   ├─ En __init__: crear self.controllers = {}
   ├─ En _build_accounts(): BotController(name, profile_path)
   ├─ Reemplazar _add_account_row()
   └─ Agregar _login_v2(), _play_v2(), _refresh_single_row()

PASO 3: Prueba de LOGIN
   └─► python main.py
       └─► Click LOGIN
           └─► Chrome abre → User loguea → Cierra
               └─► UI muestra ✅ READY

PASO 4: Prueba de PLAY
   └─► Click PLAY (solo disponible si READY)
       └─► Backend monitoreando (sin Chrome)
           └─► Precio encontrado
               └─► Chrome abre + /payment
                   └─► User confirma en banco

PASO 5: Validar todas las mejoras
   └─ Mejora #1: ✅ Validación real (headless)
   └─ Mejora #2: ✅ LOGIN_IN_PROGRESS bloquea botón
   └─ Mejora #3: ✅ Worker confía en state
   └─ Mejora #4: ✅ Price lock guardado
   └─ Mejora #5: ✅ Navegación a /payment explícita
   └─ Mejora #6: ✅ Botones bloqueados en UI
"""

# ═══════════════════════════════════════════════════════════════════════
# CHECKLIST PRE-DROP (Validación final antes de competencia)
# ═══════════════════════════════════════════════════════════════════════

"""
□ State machine completa (6 estados)
□ LOGIN abre Chrome 1 sola vez per click
□ LOGIN valida sesión real (headless)
□ PLAY solo funciona si state == READY
□ Worker monitorea sin Chrome abierto
□ Price lock se guarda cuando se detecta
□ Chrome abre con /payment explícito
□ Botones deshabilitados según estado
□ No hay asyncio, no hay deadlocks
□ Logs claros en cada transición
□ Sesión persiste entre LOGIN y PLAY (mismo profile_pw)
□ Tarjeta/Dirección guardadas en Nike (login persistent)
"""
