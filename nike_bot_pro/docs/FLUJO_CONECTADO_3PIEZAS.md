# FLUJO CONECTADO - 3 PIEZAS (FINAL)

## Visión Global (1 frase)

```
LOGIN humano deja marca (.login_ok) 
  → PLAY clona solo si marca existe 
    → preflight valida sesion 
      → backend + drop
```

---

## 1️⃣ MARCA DE INTEGRIDAD (LOGIN MASTER)

**Archivo:** `login_runner.py`

**Regla:** LOGIN cierra ciclo solo si Nike confirma logon.

```python
# Ejecucion (una sola vez por cuenta)
python login_runner.py cuenta2

# FLUJO INTERNO:
# 1. Usuario loguea en profile_login
# 2. Cierra Chrome
# 3. Script verifica: GET /mi-cuenta headless
# 4. Si OK -> crea .login_ok (marca de integridad)
# 5. Si ERROR -> no crea marca, PLAY bloqueado
```

**Resultado:**
```
auth/cuenta2/
├── profile_login/         (MASTER - sacrosanto)
│   ├── Cookies (OK)
│   ├── Local Storage
│   └── ...
│
└── .login_ok              (MARCA - exists = verificado)
```

**Contrato:** Sin `.login_ok`, no se puede jugar.

---

## 2️⃣ CLONACION QUIRURGICA (MASTER -> SLAVE)

**Archivo:** `profile_manager_v2.py`

**Regla:** PLAY clona solo si `.login_ok` existe. Ignora cache.

```python
from profile_manager_v2 import clone_auth_to_run

# Uso interno (llamado por play_runner.py / multiprocessing_runner.py)
success = clone_auth_to_run("cuenta2")

# FLUJO INTERNO:
# 1. Verifica .login_ok (guardia dura)
# 2. Elimina profile_run anterior (limpieza total)
# 3. Clona profile_login/Default -> profile_run/Default
# 4. Ignora: Cache, Code Cache, Crashpad, ShaderCache, GrShaderCache
```

**Resultado:**
```
auth/cuenta2/
├── profile_login/         (MASTER - unchanged)
│   └── Default/
│       ├── Cookies
│       └── Local Storage
│
└── profile_run/           (SLAVE - fresh clone)
    └── Default/
        ├── Cookies (copy)
        └── Local Storage (copy)
        # NO cache, NO locks, <1MB
```

**Contrato:** profile_run siempre nace limpio. Ningún lock heredado.

---

## 3️⃣ VERIFICACION PRE-PLAY (PREFLIGHT)

**Archivos:** `play_runner.py` (single) / `multiprocessing_runner.py` (multi)

**Regla:** Bloquear si Nike no reconoce sesion.

```python
# Uso single (test)
python play_runner.py cuenta2
# Resultado: clone -> preflight -> handover humano -> done

# Uso multi (produccion)
from runtime.multiprocessing_runner import run_accounts_mp
run_accounts_mp(["cuenta1", "cuenta2", "cuenta3"])
# Resultado: 3 procesos en paralelo, cada uno: clone -> preflight -> drop
```

**FLUJO INTERNO (por cuenta):**
```
STARTING
  ↓
CLONING (clone_auth_to_run)
  ↓
PREFLIGHT (session_valid = nike reconoce?)
  ├─ NO  → ERROR + BLOCKED
  └─ SÍ  → BACKEND
           ↓
           HANDOVER (visible)
             ↓
             WAITING_HUMAN (input pause)
               ↓
               DONE
```

**Contrato:** Si Nike no reconoce sesion → PLAY NO PARTE.

---

## 4️⃣ ESTADOS Y CANAL (STATE BUS)

**Archivos:** `runtime/process_states.py`, `runtime/state_bus.py`

**Regla:** Cada proceso emite estados via Queue. UI escucha.

```python
from runtime.process_states import ProcState
from runtime.state_bus import make_state_bus

# Estados disponibles
ProcState.STARTING       # proceso inicia
ProcState.CLONING        # clonando perfil
ProcState.PREFLIGHT      # validando sesion
ProcState.BACKEND        # procesando
ProcState.HANDOVER       # entregando a humano
ProcState.WAITING_HUMAN  # esperando input
ProcState.DONE           # completado
ProcState.ERROR          # error

# Mensaje en bus
{
    "user": "cuenta2",
    "state": "CLONING",
    "msg": ""  # error message si aplica
}
```

**Contrato:** 1 mensaje por transicion. UI actualiza tabla.

---

## 5️⃣ INTEGRACION UI (LISTENER)

**Archivos:** `ui/state_listener.py`, `ui/play_launcher.py`, `ui/app_integration_example.py`

**Regla:** UI nunca ejecuta Playwright ni multiprocessing directo.

```python
# En app.py
from ui.app_integration_example import PlayIntegration

class AppUI:
    def __init__(self):
        self.play = PlayIntegration()  # Crea bus + listener
    
    def on_play_clicked(self):
        selected = self.table.get_selected_accounts()
        self.play.on_play_clicked(selected)  # Lanza en thread, no bloquea
```

**FLUJO INTERNO:**
```
UI: Click PLAY
  ↓
launch_play_for_accounts(["cuenta1", "cuenta2"], bus)
  ↓
run_accounts_mp(["cuenta1", "cuenta2"], bus)  # multiprocessing
  ├─ Process 1: run_account("cuenta1", bus)
  │   └─ emit(bus, "cuenta1", STARTING)
  │   └─ emit(bus, "cuenta1", CLONING)
  │   └─ emit(bus, "cuenta1", PREFLIGHT)
  │   └─ ... DONE/ERROR
  │
  └─ Process 2: run_account("cuenta2", bus)
      └─ ... mismo flujo
  ↓
state_listener escucha bus en background
  ↓
on_state_update(user, state, msg)  # callback en main thread
  ↓
UI: actualizar tabla
    STARTING  → amarillo
    CLONING   → spinner
    PREFLIGHT → "verificando..."
    BACKEND   → "procesando..."
    HANDOVER  → "entregando..."
    WAITING_HUMAN → resaltado
    DONE      → verde
    ERROR     → rojo + mensaje
```

**Contrato:** UI no se congela. Estados emitidos en tiempo real.

---

## FLUJO FINAL (EXACTO)

```
┌─────────────────────────────────────────────────────────────┐
│                      ARQUITECTURA FINAL                      │
└─────────────────────────────────────────────────────────────┘

[1] SETUP (una sola vez por cuenta)
────────────────────────────────────
$ python login_runner.py cuenta2
  
  User loguea en Nike
  ↓
  Script verifica: GET /mi-cuenta
  ↓
  Nike reconoce? → YES ✓ crear .login_ok
                → NO ✗ bloquear PLAY


[2] UI BUTTON: PLAY
───────────────────
Click PLAY en tabla
  ↓
selected = [cuenta1, cuenta2, cuenta3]
  ↓
PlayIntegration.on_play_clicked(selected)
  ↓
launch_play_for_accounts(selected, bus)
  ↓
run_accounts_mp(selected, bus)
  ↓
  ├─ Process 1: run_account("cuenta1", bus)
  ├─ Process 2: run_account("cuenta2", bus)
  └─ Process 3: run_account("cuenta3", bus)


[3] CADA PROCESO (PARALELO)
──────────────────────────
run_account("cuenta2", bus)
  │
  ├─ emit(STARTING)
  │
  ├─ clone_auth_to_run("cuenta2")  # master -> run
  │  └─ emit(CLONING)
  │
  ├─ preflight(profile_run)  # validate session
  │  └─ emit(PREFLIGHT)
  │  └─ if not ok: emit(ERROR) + return
  │
  ├─ backend (TODO: tu logica aqui)
  │  └─ emit(BACKEND)
  │
  ├─ handover humano (visible)
  │  ├─ emit(HANDOVER)
  │  ├─ emit(WAITING_HUMAN)
  │  └─ input("presiona ENTER")
  │
  └─ emit(DONE)


[4] STATE LISTENER (BACKGROUND)
───────────────────────────────
state_listener hilo
  │
  ├─ escucha bus
  │ └─ get mensaje
  │    └─ on_state_update(user, state, msg)
  │
  └─ callback ejecuta en main thread
     └─ table.update_row(user, state, color)


[5] RESULTADO FINAL
──────────────────
Tabla actualiza en tiempo real:
┌──────────┬───────────┬──────────┐
│ Cuenta   │ Estado    │ Info     │
├──────────┼───────────┼──────────┤
│ cuenta1  │ DONE      │ [verde]  │
│ cuenta2  │ HANDOVER  │ [amarill]│
│ cuenta3  │ PREFLIGHT │ [azul]   │
└──────────┴───────────┴──────────┘
```

---

## ARCHIVOS (MAPA)

```
nike_bot_pro/
│
├── [LOGIN MASTER]
│   └── login_runner.py
│       └── .login_ok (marca)
│
├── [CLONE QUIRURGICO]
│   └── profile_manager_v2.py
│       └── clone_auth_to_run()
│
├── [PLAY SINGLE]
│   └── play_runner.py
│       └── preflight()
│
├── runtime/
│   ├── [MULTIPROCESSING]
│   │   └── multiprocessing_runner.py
│   │       ├── run_account()
│   │       └── run_accounts_mp()
│   │
│   ├── [STATES]
│   │   ├── process_states.py
│   │   │   └── ProcState (Enum)
│   │   │
│   │   └── state_bus.py
│   │       └── make_state_bus()
│   │
│   └── [OTROS]
│       ├── bot_controller.py
│       ├── worker.py
│       └── ...
│
└── ui/
    ├── [LISTENER]
    │   └── state_listener.py
    │       └── start_state_listener()
    │
    ├── [LAUNCHER]
    │   └── play_launcher.py
    │       └── launch_play_for_accounts()
    │
    ├── [EXAMPLE]
    │   └── app_integration_example.py
    │       └── PlayIntegration class
    │
    └── [MAIN APP]
        └── app.py
            └── (integra PlayIntegration)
```

---

## REGLAS (RESUMEN)

1. **LOGIN** crea `.login_ok` (solo si Nike confirma)
2. **CLONE** verifica `.login_ok` antes de copiar
3. **PREFLIGHT** valida sesion con profile_run
4. **BACKEND** recibe profile_run limpio + validado
5. **HANDOVER** esperando input del usuario
6. **ESTADOS** emitidos via Queue (no bloqueantes)
7. **UI** escucha estados en background thread
8. **MULTIPROCESSING** = 1 cuenta = 1 proceso (paralelo)

---

## TESTING (PASO A PASO)

```bash
# Test 1: Setup LOGIN
python login_runner.py cuenta2
# -> Loguéate en Nike
# -> Verifica .login_ok fue creado
# -> ls auth/cuenta2/ | grep .login_ok

# Test 2: Play single
python play_runner.py cuenta2
# -> clone + preflight + handover + done

# Test 3: Multiprocessing
python -c "from runtime.multiprocessing_runner import run_accounts_mp; run_accounts_mp(['cuenta2', 'cuenta3'])"
# -> 2 procesos en paralelo

# Test 4: Con UI
python main.py
# -> Click PLAY
# -> Ver estados en tabla
# -> STARTING -> CLONING -> PREFLIGHT -> ... -> DONE
```

---

**Status:** ✅ CONECTADO Y FUNCIONANDO  
**Complejidad:** MINIMA (solo lo necesario)  
**Flexibilidad:** MAXIMA (extensible para backend logic)
