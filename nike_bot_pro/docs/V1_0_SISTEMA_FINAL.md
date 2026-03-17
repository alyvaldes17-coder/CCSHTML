## SISTEMA FINAL v1.0 DROP-READY

**Arquitectura completa, cerrada, sin medias tintas.**

---

### 🎯 Flujo FINAL (cerrado, reproducible)

```
0️⃣  LOGIN (humano, OFF-DROP)
    → Chrome real + Nike.cl/login
    → Usuario loguea manualmente + cierra Chrome
    → Script crea: auth/cuenta2/.login_ok

1️⃣  PLAY (bot, DURANTE DROP)
    → Valida preflight (filesystem only)
    → Si falla → ABORT (sin intentos)
    → Si pasa → Ejecuta ATC backend
    → Detecta precio
    → Handover a Playwright
    → Espera pago humano
    → FIN
```

---

### 📋 Paso 0: LOGIN (humano)

```bash
cd c:\Users\beriann\Documents\Repos\nike_bot_pro
python login_runner.py cuenta2
```

**Qué hace:**
1. Abre Chrome real en `auth/cuenta2/profile_login`
2. Navega a `https://www.nike.cl/login`
3. Te espera a que loguees + cierres Chrome
4. Crea: `auth/cuenta2/.login_ok`

**Output esperado:**
```
[LOGIN] Account path: C:\...\auth\cuenta2
[LOGIN] Profile path: C:\...\auth\cuenta2\profile_login
[LOGIN] Login OK path: C:\...\auth\cuenta2\.login_ok
[LOGIN] Por favor loguéate en Nike.cl
[LOGIN] Cuando termines, CIERRA Chrome
[LOGIN] Chrome cerrado
[SUCCESS] LOGIN OK → C:\...\auth\cuenta2\.login_ok
```

**Resultado:**
```
auth/cuenta2/
├─ profile_login/        (con cookies de Nike después de loguearse)
└─ .login_ok             (archivo vacío, solo marca)
```

---

### 📋 Paso 1: PLAY (bot)

```bash
python play_v1_0.py cuenta2 170369
```

**Qué hace:**
1. Valida PRE-FLIGHT (5 checks filesystem-only)
2. Si alguno falla → ABORT con motivo claro
3. Si todos pasan → Ejecuta flujo ATC + navegador

**Output esperado (preflight OK):**
```
[PLAY v1.0] Account: cuenta2
[PLAY v1.0] SKU: 170369
[PLAY v1.0] 🔍 PRE-FLIGHT...
[PLAY v1.0] ✅ PRE-FLIGHT OK
[PLAY v1.0] 🚀 Ejecutar backend ATC
[PLAY v1.0] 🚀 Detectar precio
[PLAY v1.0] 🚀 Handover a navegador
[PLAY v1.0] ✅ FLUJO COMPLETADO
```

**Output si falla preflight:**
```
[PLAY v1.0] 🔍 PRE-FLIGHT...
❌ [ABORT] PREFLIGHT FAIL: NO_LOGIN_OK
```

---

### 🔍 PRE-FLIGHT (v1.0): Qué valida (y SOLO esto)

```python
from runtime.preflight import preflight
from config.settings import AUTH_ROOT, CHROME_PATH
import os

account = "cuenta2"
sku = "170369"
account_path = os.path.join(AUTH_ROOT, account)

ok, reason = preflight(account_path, sku, CHROME_PATH)

# Returns:
# (True, "OK")                     → PLAY
# (False, "NO_LOGIN_OK")           → Falta .login_ok
# (False, "PROFILE_LOGIN_MISSING") → Falta profile_login/
# (False, "CLONE_FAIL: ...")       → Error al clonar
# (False, "CHROME_NOT_FOUND")      → Chrome no existe
# (False, "SKU_INVALID")           → SKU vacío/inválido
```

**PRE-FLIGHT valida SOLO:**
1. ✅ `.login_ok` existe
2. ✅ `profile_login/` existe
3. ✅ Clone `profile_login` → `profile_run` funciona
4. ✅ Chrome ejecutable existe
5. ✅ SKU válido

**PRE-FLIGHT NO hace:**
- ❌ No toca red
- ❌ No abre Chrome
- ❌ No valida cookies
- ❌ No arregla nada
- ❌ Si falla → ABORT

---

### 🏗️ Estructura FINAL

```
nike_bot_pro/
├─ config/
│  └─ settings.py                    (paths absolutos + Chrome)
├─ auth/
│  └─ cuenta2/
│     ├─ profile_login/              (cookies Nike después de LOGIN)
│     ├─ profile_run/                (clonado en preflight, listo para usar)
│     └─ .login_ok                   (archivo vacío, marca de login)
├─ runtime/
│  ├─ preflight.py                   (validaciones filesystem)
│  ├─ multiprocessing_runner.py      (orquestador)
│  └─ worker.py                      (ejecución)
├─ login_runner.py                   (LOGIN con Chrome real)
├─ play_v1_0.py                      (PLAY con preflight)
└─ main.py
```

---

### 🔧 Configuración (config/settings.py)

```python
# PATHS ABSOLUTAS (fuente única de verdad)
PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
AUTH_ROOT = os.path.join(PROJECT_ROOT, "auth")

# Chrome (Windows - auto-detecta)
CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]
CHROME_PATH = next(p for p in CHROME_PATHS if os.path.exists(p))
```

---

### 🚨 Reglas FINALES (no se rompen)

1. **LOGIN**
   - Humano loguea en Chrome real
   - `.login_ok` creado → DROP-READY
   - Nunca tocar durante drop

2. **PREFLIGHT**
   - Filesystem only (sin red, sin Chrome abierto)
   - Si falla → ABORT
   - Sin intentos, sin correcciones

3. **PLAY**
   - Ejecuta si preflight OK
   - 0 decisiones en runtime
   - 0 paths ambiguos
   - Reproducible

4. **ABORT**
   - Si algo falla → parar
   - Sin intentar arreglar
   - Limpio y claro

---

### ✅ Testing

```bash
# Test 1: Config imports
python -c "from config.settings import AUTH_ROOT, CHROME_PATH; print('✅ OK')"

# Test 2: Preflight imports  
python -c "from runtime.preflight import preflight; print('✅ OK')"

# Test 3: Full flow (preflight)
python play_v1_0.py cuenta2 170369
```

---

### 📚 Archivos modificados esta sesión

1. **config/settings.py**
   - ✅ Agregado: `PROJECT_ROOT`, `AUTH_ROOT`, `CHROME_PATH`
   - ✅ Source única de verdad para paths absolutos

2. **login_runner.py**
   - ✅ Actualizado: imports de `config.settings`
   - ✅ Rutas absolutas desde config

3. **runtime/preflight.py**
   - ✅ NUEVO: Validación filesystem v1.0
   - ✅ 5 checks, ABORT si falla

4. **runtime/multiprocessing_runner.py**
   - ✅ Actualizado: usa `preflight` de `runtime.preflight`
   - ✅ Rutas absoltas desde `config.settings`

5. **runtime/bot_controller.py**
   - ✅ Actualizado: imports y paths desde `config.settings`

6. **profile_manager_v2.py**
   - ✅ Actualizado: imports y paths desde `config.settings`

7. **runner/account_worker.py**
   - ✅ Actualizado: imports y paths desde `config.settings`

8. **play_v1_0.py**
   - ✅ NUEVO: Script de PLAY con preflight

---

### 🎯 Qué ganaste

✅ Login fuera del drop
✅ 0 decisiones en runtime
✅ 0 paths ambiguos
✅ 0 heurísticas
✅ Sistema reproducible
✅ Abort limpio si algo falla
✅ Drop-ready v1.0

---

### 🔒 Regla final (la más importante)

**Nunca arregles nada durante un drop.**
**Si falla, se arregla después.**

---

**Sistema v1.0: CERRADO. LISTO. FINAL.**
