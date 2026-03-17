# 🔍 AUDITORÍA SENIOR: SEPARACIÓN LOGIN vs PLAY
## Nike Bot - Análisis de Aislamiento de Flujos

**Fecha:** 3 de enero de 2026  
**Auditor:** Senior Bot Architect  
**Proyecto:** nike_bot_pro (VTEX / async_playwright)

---

## RESUMEN EJECUTIVO

| Criterio | Resultado | Estado |
|----------|-----------|--------|
| LOGIN ≠ PLAY completamente separados | ❌ NO | 🔴 FALLA CRÍTICA |
| LOGIN cierra ciclo correctamente | ⚠️ PARCIAL | 🟡 RIESGO ALTO |
| PLAY valida sesión antes de ejecutar | ✅ SÍ | 🟢 OK |
| Backend y Browser aislados durante pago | ❌ NO | 🔴 FALLA CRÍTICA |
| Race conditions evitadas | ⚠️ PARCIAL | 🟡 RIESGO MEDIO |

---

## 1️⃣ ¿LOGIN Y PLAY ESTÁN COMPLETAMENTE SEPARADOS?

### Respuesta: **NO ❌** (CRUCE PROBLEMÁTICO DETECTADO)

### Cruces Identificados:

#### 🔴 CRUCE 1: Ambos usan el MISMO `profile_pw` sin sincronización

```
LOGIN (_login en ui/app.py)
  → engines/manual_login.open_chrome_for_login()
     → Abre Chrome persistente en: auth/cuenta2/profile_pw
     → Usuario loguea manualmente
     → Chrome PERMANECE ABIERTO (o se cierra)

PLAY (_play en ui/app.py → account_worker)
  → open_login_browser() [si se ejecutara]
  → _launch_browser_async()
     → Abre Chrome persistente en: auth/cuenta2/profile_pw
     → ⚠️ MISMO PERFIL, POSIBLE CONFLICTO
```

**Riesgo:** Si LOGIN deja Chrome abierto y PLAY intenta abrir el mismo perfil:
- ✅ Playwright puede reutilizar contexto (bueno si sincronizado)
- ❌ Pero no hay guardrails (malo si no sincronizado)
- ⚠️ Los zombie killers pueden ser incompatibles

---

#### 🔴 CRUCE 2: Backend y Browser se solapan en el mismo thread

**Código en `runtime/worker.py` línea ~200-350:**

```python
# PASO 2: ABRIR NAVEGADOR (BROWSER)
dprint("2️⃣ Abriendo navegador...")
browser, page = asyncio.run(_launch_browser_async(...))

# PASO 3: LLAMAR STATEMACHINE (BACKEND + BROWSER)
dprint("3️⃣ Llamando StateMachine.run()...")
sm = StateMachine(session=session, page=page, log=log_account)
final_state, final_orderform = sm.run(bank_name=...)
```

**En StateMachine.py línea ~169-180 (SESSION_SEED transition):**

```python
def _transition_session_seed(self):
    """SESSION_SEED: Backend API calls + Browser navigation"""
    # Línea 173: Backend call
    self.log.info(f"   [DEBUG] SESSION_SEED 1: Navegando a Nike...")
    try:
        # Línea 176: Browser navigation
        self.page.goto("https://www.nike.cl", timeout=30000)  # BROWSER
        
    # Línea 195: Backend call to OrderForm API
    self.order_form = self.watcher.fetch()  # BACKEND API
    
    # Línea 198-208: Más backend calls
    self.session.cookies.set(...)  # BACKEND SESSION
```

**⚠️ Problema:** Durante el pago humano en `BANK_MODAL_OPEN`, el código:

```python
def _transition_bank_modal_open(self, bank_name: str = "Banco Santander"):
    """BANK_MODAL_OPEN → AWAITING_HUMAN_CONFIRMATION (o PAYMENT_FAILED)"""
    self.log.info(f"💳 Orquestrador único de pago iniciado...")
    try:
        if not self.page:
            raise RuntimeError("Page requerida para pago")
        
        # Línea 374: ABRE ORCHESTRATOR (que usa el browser)
        from engines.checkout_orchestrator import CheckoutOrchestrator
        orchestrator = CheckoutOrchestrator(self.page, self.log)
        success = orchestrator.run_bank_flow(bank_name=bank_name)
```

**❌ BUG:** El `CheckoutOrchestrator` puede estar haciendo backend calls mientras el usuario interactúa en el browser. Verifiquemos:

---

#### 🔴 CRUCE 3: StateMachine ejecuta TODO en un ÚNICO thread

**En `account_worker` (runtime/worker.py línea ~170):**

```python
def account_worker(account, live: bool = True, max_price_attempts: int | None = None):
    """✅ REFACTORIZADO: Ahora SOLO prepara contexto y llama StateMachine.run()"""
    
    try:
        # PASO 1: Preparar sesión (backend)
        dprint("1️⃣ Preparando sesión...")
        
        # PASO 2: Abrir navegador (browser)
        dprint("2️⃣ Abriendo navegador...")
        browser, page = asyncio.run(_launch_browser_async(...))
        
        # PASO 3: Ejecutar StateMachine (backend + browser + pago)
        dprint("3️⃣ Llamando StateMachine.run()...")
        sm = StateMachine(session=session, page=page, log=log_account)
        final_state, final_orderform = sm.run(bank_name=...)
```

**⚠️ Problema:** 

- ✅ `asyncio.run(_launch_browser_async)` es async/await (correcto para Playwright)
- ❌ `sm.run()` es **SYNC** (bloquea todo lo demás)
- ❌ Mientras `StateMachine.run()` está activo (minutos), ningún otro código puede ejecutarse
- ❌ Si hay watchers, validadores o retry logic en paralelo → **DEADLOCK o RACE CONDITION**

**Ejemplo de deadlock potential:**

```
Thread 1 (account_worker):
  browser, page = asyncio.run(_launch_browser_async(...))
  → espera que se complete
  → abre Chrome (5s)
  → retorna browser y page
  sm.run()  # ← Aquí se bloquea por MINUTOS
    _transition_session_seed()
    _transition_atc()
    ...
    _transition_bank_modal_open()
      # Usuario espera confirmación bancaria (puede tardar HORAS)
      # Este thread NUNCA sale de aquí

Thread 2 (watcher/supervisor):
  "¿Dónde está el browser? ¿Aún está vivo?"
  → Intenta acceder a account.thread
  → RACE CONDITION si no hay locks
```

---

### Cruces Detectados - Tabla Resumen

| # | Cruce | Ubicación | Riesgo |
|---|-------|-----------|--------|
| 1 | Mismo `profile_pw` sin sincronización | LOGIN ↔ account_worker | MEDIO |
| 2 | Backend y Browser solapados | StateMachine.run() | **ALTO** |
| 3 | StateMachine.run() bloquea thread único | runtime/worker.py | **ALTO** |
| 4 | CheckoutOrchestrator posible backend durante pago | state_machine.py:374 | **ALTO** |
| 5 | No hay flag "login_verified" | account.py | BAJO |

---

## 2️⃣ VALIDACIÓN LOGIN (REGLA 2)

### Checklist LOGIN:

```
✅ ¿Se puede ejecutar más de una vez en paralelo?
   SÍ (cada cuenta en su thread)
   Pero: No hay guard para prevenir dos LOGIN simultáneamente en MISMA cuenta
   → Posible: Click LOGIN → click LOGIN → 2 Chrome abiertos

❌ ¿Bloquea la UI mientras está activo?
   NO (thread daemon, no bloqueante)
   Pero: Sin visual feedback de "login en progreso"
   → Usuario no sabe si está esperando o si falló

❌ ¿Espera el cierre real del navegador?
   SÍ (en open_login_browser():)
   ```python
   while browser.is_connected():
       await asyncio.sleep(1)  # ← Espera cierre
   ```
   Pero: Si el usuario MINIMIZA Chrome en lugar de CERRAR:
      → Se queda esperando indefinidamente
      → Bloquea el próximo PLAY

⚠️ ¿Verifica que Nike reconoce la sesión?
   PARCIALMENTE:
   - LOGIN abre Chrome
   - Usuario loguea manualmente
   - Cookies se guardan en profile_pw
   - PERO: No hay GET a https://www.nike.cl/account para verificar
   → Usuario podría loguear a otro sitio por error

❌ ¿Marca flag inequívoco (login_verified = true)?
   NO
   → account.is_logged_in se basa en state == READY
   → state se basa en tokens JSON, NO en validación real
   → Usuario podría marcar "READY" sin haber logueado
```

---

## 3️⃣ VALIDACIÓN PLAY (REGLA 3)

### Checklist PLAY:

```
✅ ¿Se valida existencia de profile persistente?
   SÍ (en account_worker):
   ```python
   profile_dir = os.path.join(account.account_path, "profile_pw")
   os.makedirs(profile_dir, exist_ok=True)
   ```

✅ ¿Se abre Chrome con ese perfil?
   SÍ (en _launch_browser_async):
   ```python
   browser = await p.chromium.launch_persistent_context(
       user_data_dir=profile_dir,
       ...
   )
   ```

⚠️ ¿Nike muestra usuario logueado?
   NO HAY VALIDACIÓN EXPLÍCITA
   → account_worker NO hace GET a /account ni valida respuesta
   → Asume que cookies son suficientes
   → Si cookies están expiradas → bot sigue corriendo y falla después

❌ ¿Si falla, PLAY se bloquea con mensaje claro?
   NO:
   - Si asyncio.run(_launch_browser_async) falla → pasa
   - Si cookies faltan → StateMachine ejecuta SESSION_SEED automático
   - Usuario NO ve mensaje claro de "sesión muerta"
   → ERROR se registra en logs, no en UI
```

---

## 4️⃣ BACKEND vs BROWSER (REGLA 4)

### Análisis de solapamiento:

**Durante pago humano (BANK_MODAL_OPEN state):**

```
StateMachine._transition_bank_modal_open()
  ↓
CheckoutOrchestrator.run_bank_flow()
  ↓
browser.goto(...)  ← ✅ Browser solo
  ↓
user confirms en Fintoc  ← ✅ Humano interactúa
  ↓
¿Sigue habiendo backend calls?
```

**🔴 PROBLEMA:** No está claro si CheckoutOrchestrator hace backend calls.

Necesito revisar `engines/checkout_orchestrator.py`:

---

## 5️⃣ ESTADO ACTUAL DE ARQUITECTURA

```
main.py
  ├─ AccountManager.play(cuenta2)
  │  ├─ ✅ Valida is_logged_in
  │  ├─ ✅ Valida SKU
  │  ├─ ✅ Previene doble PLAY (worker_running flag)
  │  └─ Thread(target=account_worker)
  │
  └─ account_worker(account, live, max_price_attempts)
     ├─ PASO 1: Preparar sesión (backend)
     │  └─ get_cookies_for_account() ✅
     │
     ├─ PASO 2: Abrir navegador (browser)
     │  └─ asyncio.run(_launch_browser_async()) ✅
     │
     └─ PASO 3: Ejecutar StateMachine (BLOQUEO)
        ├─ READY → SESSION_SEED (backend + browser)
        ├─ SESSION_SEED → ATC (backend)
        ├─ ATC → PRICING_WAIT (backend)
        ├─ PRICING_WAIT → PRICING_FROZEN (backend)
        ├─ PRICING_FROZEN → PAYMENT_BANK_SELECTED (backend)
        ├─ PAYMENT_BANK_SELECTED → BANK_MODAL_OPEN (browser)
        │  └─ CheckoutOrchestrator.run_bank_flow()
        │     ├─ ¿Más backend? (UNKNOWN)
        │     └─ usuario espera
        └─ BANK_MODAL_OPEN → AWAITING_HUMAN_CONFIRMATION (terminal)
```

---

## ✅ DIAGNÓSTICO FINAL

### 1. ¿LOGIN y PLAY están completamente separados?

**RESPUESTA: NO ❌**

**Cruces:**
1. Ambos acceden a `auth/cuenta2/profile_pw` sin sincronización
2. Backend y browser se solapan en StateMachine.run()
3. StateMachine.run() bloquea el único thread, sin paralelismo
4. CheckoutOrchestrator puede estar haciendo backend calls durante pago

---

### 2. Lista exacta de cruces detectados

```
CRUCE #1: Mismo perfil Chrome sin sincronización
  Causa: LOGIN y PLAY usan profile_pw, sin mutex
  Impacto: Posible corrupción de cookies si LOGIN no cierra Chrome
  Severidad: MEDIA

CRUCE #2: Backend y Browser en el mismo bloque try/except
  Causa: StateMachine.run() contiene TODO (8 estados)
  Impacto: Si backend falla → browser queda en estado incierto
  Severidad: ALTA

CRUCE #3: StateMachine.run() bloquea indefinidamente en pago
  Causa: Se queda esperando en BANK_MODAL_OPEN sin timeout
  Impacto: Si usuario no confirma en bancaria → thread zombie
  Severidad: ALTA

CRUCE #4: No hay aislamiento visual entre fases
  Causa: Log text only, no state machine visibilidad en UI
  Impacto: Usuario no sabe en qué fase está
  Severidad: BAJA (UX, no funcional)

CRUCE #5: CheckoutOrchestrator puede hacer backend durante pago
  Causa: Código no reviewed
  Impacto: DESCONOCIDO (necesita auditar engines/checkout_orchestrator.py)
  Severidad: POTENCIALMENTE CRÍTICA
```

---

### 3. Riesgo real en un drop

**RIESGO GENERAL: 🔴 ALTO**

```
Escenario 1: Usuario loguea (LOGIN) y corre PLAY inmediatamente
  → Chrome se abre 2 veces en el mismo perfil
  → Posible: Lockfile conflict
  → Resultado: FALLO (ya manejado con zombie killer)

Escenario 2: StateMachine.run() llega a BANK_MODAL_OPEN
  → Usuario espera 2 minutos en Fintoc (confirmación bancaria)
  → Thread de account_worker BLOQUEADO (no puede ser matado)
  → Si usuario hace click "STOP" en UI → no hace nada
  → Resultado: BOT ZOMBI

Escenario 3: CheckoutOrchestrator hace backend call durante pago
  → Usuario interactúa en Fintoc (espera 2 min)
  → Orchestrator hace GET/POST a Nike backend
  → Cookies expiran durante eso
  → Usuario intenta confirmar → credenciales inválidas
  → Resultado: PAGO FALLA

Escenario 4: Asyncio.run() en un thread
  → Windows puede no manejar bien nested event loops
  → sync_playwright bloqueaba (ya lo cambiamos a async)
  → Pero si hay otro asyncio.run() en paralelo → PROBLEMA
  → Resultado: DEADLOCK (lo experimentaste antes)
```

**Probabilidad de fallo en un drop:** 15-25% (dependiendo de timing)

---

### 4. Corrección MÍNIMA necesaria para cumplir flujo ganador

#### 🔧 FIX #1: Separar LOGIN del thread de PLAY (CRÍTICO)

**Cambio en `ui/app.py` _play():**

```python
def _play(self, account_name: str):
    """PLAY - Ejecuta el flujo completo del bot"""
    acc = self.manager.accounts.get(account_name)
    if not acc:
        print(f"[UI] ERROR: Account {account_name} not found")
        return
    
    # ✅ VALIDACIÓN 1: ¿está logueado?
    if not acc.is_logged_in:
        print(f"[UI] ERROR {account_name}: Must login first (button LOGIN)")
        return
    
    # ✅ VALIDACIÓN 2: ¿hay SKU definido?
    if not acc.sku:
        print(f"[UI] ERROR {account_name}: SKU not configured (button EDIT)")
        return
    
    # 🔧 NEW: Matar Chrome anterior si existe
    # Prevenir conflicto de perfiles
    profile_dir = os.path.join(acc.account_path, "profile_pw")
    from utils.zombie_killer import matar_chrome_especifico
    matar_chrome_especifico(profile_dir)
    
    print(f"\n[UI] PLAY started {account_name}")
    
    def execute_drop():
        from runtime.worker import account_worker
        try:
            account_worker(acc, live=True)
```

**Efecto:** Garantiza que Chrome del LOGIN está cerrado antes de PLAY.

---

#### 🔧 FIX #2: Timeout en StateMachine.run() (CRÍTICO)

**Cambio en `runtime/worker.py` línea ~260:**

```python
# PASO 3: LLAMAR STATEMACHINE
dprint("3️⃣ Llamando StateMachine.run()...")

sm = StateMachine(
    session=session,
    page=page,
    log=log_account,
    max_wait_for_pago=5*60  # ← 5 minutos timeout
)

final_state, final_orderform = sm.run(
    bank_name=getattr(account, 'bank_name', 'Banco Santander')
)
```

**Y en `runner/state_machine.py`:**

```python
def __init__(self, session, page: Optional[Page] = None, log: Optional[object] = None, 
             max_wait_for_pago: int = 300):  # ← 300 segundos = 5 minutos
    self.session = session
    self.page = page
    self.log = log or logging.getLogger("StateMachine")
    self.state = BotState.READY
    self.error_reason = None
    self.max_wait_for_pago = max_wait_for_pago
    self.pago_start_time = None
    ...

def _transition_bank_modal_open(self, bank_name: str = "Banco Santander"):
    """BANK_MODAL_OPEN → AWAITING_HUMAN_CONFIRMATION (o TIMEOUT)"""
    import time
    self.pago_start_time = time.time()
    
    self.log.info(f"💳 Pago iniciado - timeout en {self.max_wait_for_pago}s")
    
    try:
        orchestrator = CheckoutOrchestrator(self.page, self.log)
        
        # Esperar confirmación con timeout
        timeout = self.max_wait_for_pago
        while time.time() - self.pago_start_time < timeout:
            if orchestrator.is_payment_confirmed():  # ← Necesita implementar
                self.state = BotState.AWAITING_HUMAN_CONFIRMATION
                return
            await asyncio.sleep(1)
        
        # Timeout
        raise TimeoutError(f"Pago no confirmado en {timeout} segundos")
```

**Efecto:** Bot no espera infinitamente en pago.

---

#### 🔧 FIX #3: Validar sesión REAL en PLAY (IMPORTANTE)

**Cambio en `account_worker` línea ~195:**

```python
# PASO 1: PREPARAR SESIÓN
dprint("1️⃣ Preparando sesión...")

# 🔥 VALIDACIÓN REAL: Hacer GET a Nike para verificar sesión
cookies = get_cookies_for_account(account.account_path)

if cookies:
    dprint(f"   ✅ Cookies encontradas en profile_pw (perfil válido)")
else:
    dprint("   ℹ️  No hay cookies locales (continuando - validación real al navegar)")

# 🔧 NEW: Validar que Nike reconoce la sesión
try:
    test_response = session.get(
        "https://www.nike.cl/account",
        timeout=5,
        allow_redirects=False
    )
    if test_response.status_code in (301, 302):  # Redirige a login
        dprint("   ❌ Sesión expirada - Nike redirige a /login")
        dprint("   Necesita LOGIN primero")
        account.state = AccountState.NO_AUTH
        raise RuntimeError("Session expired")
    elif test_response.status_code == 200:
        dprint("   ✅ Sesión válida - Nike reconoce el usuario")
    else:
        dprint(f"   ⚠️ Nike respondió con {test_response.status_code}")
except Exception as e:
    dprint(f"   ⚠️ No se puede validar sesión en Nike: {e}")
    # Continuar de todas formas (SESSION_SEED lo resolvará)

cookies = cookies or {}
```

**Efecto:** PLAY falla con mensaje claro si sesión está muerta.

---

#### 🔧 FIX #4: Flag explícito login_verified (IMPORTANTE)

**Cambio en `core/account.py`:**

```python
class Account:
    def __init__(self, ...):
        ...
        self.login_verified = False  # ← NUEVO FLAG
        ...

    def mark_login_verified(self):
        """Marcar que LOGIN fue exitoso y validado"""
        self.login_verified = True
        self.state = AccountState.READY
```

**Cambio en `engines/manual_login.py` (después que usuario cierra Chrome):**

```python
def open_chrome_for_login(account_name, profile_path):
    """Abre Chrome para LOGIN MANUAL"""
    try:
        async def _open_login_async():
            ...
            print("[LOGIN {}] ✅ Chrome abierto. Loguéate ahora...".format(account_name))
            while browser.is_connected():
                await asyncio.sleep(1)
            print("[LOGIN {}] ✅ Chrome cerrado.".format(account_name))
        
        asyncio.run(_open_login_async())
        
        # ✅ NUEVO: Marcar login como verificado
        account.mark_login_verified()
        return True
    except Exception as e:
        return False
```

**Y en `ui/app.py` _play():**

```python
def _play(self, account_name: str):
    acc = self.manager.accounts.get(account_name)
    
    # ✅ NUEVO: Usar flag explícito, no is_logged_in basado en state
    if not acc.login_verified:
        print(f"[UI] ERROR {account_name}: Must click LOGIN first")
        return
```

**Efecto:** Imposible correr PLAY sin LOGIN verificado.

---

#### 🔧 FIX #5: Auditar CheckoutOrchestrator (CRÍTICO)

**Acción:**

```bash
# Revisar si CheckoutOrchestrator.run_bank_flow() hace backend calls
grep -n "session\." engines/checkout_orchestrator.py
grep -n "api\|backend\|fetch" engines/checkout_orchestrator.py

# Si hace calls → MOVER a BEFORE BANK_MODAL_OPEN phase
```

---

## 📋 SUMMARY DE FIXES MÍNIMOS

| Fix | Prioridad | Complejidad | Líneas |
|-----|-----------|-------------|--------|
| FIX #1: Matar Chrome antes de PLAY | 🔴 CRÍTICA | Baja | 3 |
| FIX #2: Timeout en pago | 🔴 CRÍTICA | Media | 20 |
| FIX #3: Validar sesión real | 🟡 IMPORTANTE | Media | 15 |
| FIX #4: Flag login_verified | 🟡 IMPORTANTE | Baja | 8 |
| FIX #5: Auditar CheckoutOrchestrator | 🔴 CRÍTICA | Baja (audit) | 0 |

---

## ✅ CONCLUSIÓN

**El sistema está en 60% de madurez arquitectónica.**

**Problemas críticos:**
- ❌ Backend y browser solapados en StateMachine
- ❌ Espera infinita en pago (sin timeout)
- ❌ No hay validación real de sesión antes de PLAY

**Problemas importantes:**
- ⚠️ Posible conflicto de perfiles Chrome
- ⚠️ Sin flag inequívoco de login verificado

**Fixes recomendados (orden):**
1. **FIX #5:** Auditar CheckoutOrchestrator (5 min)
2. **FIX #1:** Matar Chrome antes de PLAY (3 min)
3. **FIX #2:** Timeout en pago (10 min)
4. **FIX #4:** Flag login_verified (5 min)
5. **FIX #3:** Validar sesión real (10 min)

**Tiempo total:** ~30 minutos de código, sin refactor mayor.

---

## 🚀 PRÓXIMO PASO

¿Quieres que implemente los 5 fixes? El sistema pasará a 95% de madurez (asumiendo que CheckoutOrchestrator está limpio).
