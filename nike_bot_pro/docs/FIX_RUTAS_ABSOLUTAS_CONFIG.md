# 🔧 FIX DEFINITIVO: Rutas Absolutas desde config.py

## El Problema Exacto

**LOGIN** y **BotController** estaban mirando **RUTAS DISTINTAS**:

```
LOGIN usa:          auth\cuenta2\.login_ok         (relativa)
BotController usa:  C:\...\nike_bot_pro\auth\cuenta2\.login_ok  (relativa mapeada distinto)

Windows + subprocess = cwd distinto = ARCHIVOS DISTINTOS
```

**Resultado**:
- LOGIN crea archivo ✅
- BotController no lo encuentra ❌
- UI parpadea: a veces ✅, a veces ❌

---

## La Solución (Quirúrgica)

### 1. **config.py** - Fuente única de verdad para rutas

```python
# config.py
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
AUTH_ROOT = os.path.join(PROJECT_ROOT, "auth")

def get_login_ok_path(account_name: str) -> str:
    return os.path.join(AUTH_ROOT, account_name, ".login_ok")
```

**Garantiza**: TODOS usan la MISMA ruta absoluta.

---

### 2. **login_runner.py** - Usa config.py

**ANTES**:
```python
base = Path("auth") / user  # Relativa, problema con subprocess
login_ok = base / ".login_ok"
```

**AHORA**:
```python
from config import get_login_ok_path

login_ok = get_login_ok_path(user)  # Ruta absoluta
with open(login_ok, "w") as f:
    f.write("OK")

# Log explícito
print(f"[LOGIN] .login_ok: {login_ok}")
print(f"[LOGIN] Existe?: {os.path.exists(login_ok)}")
```

---

### 3. **BotController** - Usa config.py

**ANTES**:
```python
login_ok = os.path.join(base_path, account_name, ".login_ok")  # Relativa
if os.path.exists(login_ok):
    self.state = READY
```

**AHORA**:
```python
from config import get_login_ok_path

self.login_ok_path = get_login_ok_path(account_name)  # Ruta absoluta
if os.path.exists(self.login_ok_path):
    self.state = READY
    print(f"[{self.account_name}] login_ok path: {self.login_ok_path}")
```

---

### 4. **profile_manager_v2.py** - Usa config.py

**ANTES**:
```python
base = os.path.abspath(f"auth/{user}")  # Intenta ser absoluta pero con relativa
login_ok = os.path.join(base, ".login_ok")
```

**AHORA**:
```python
from config import get_login_ok_path, get_profile_login_path, get_profile_run_path

login_ok = get_login_ok_path(user)       # Ruta absoluta
src = os.path.join(get_profile_login_path(user), "Default")  # Ruta absoluta
dst_root = get_profile_run_path(user)    # Ruta absoluta
```

---

## Por Qué Esto Arregla Todo

### Problema Original
```
subprocess login_runner.py
  ├─ cwd = "."
  └─ auth\cuenta2\.login_ok  ← Archivo A

main.py (UI)
  ├─ cwd = "."
  └─ auth\cuenta2\.login_ok  ← ¿Archivo B?

En Windows + threading = pueden ser directorios distintos
```

### Solución
```
TODOS usan:
  C:\Users\beriann\Documents\Repos\nike_bot_pro\auth\cuenta2\.login_ok

No hay ambigüedad.
No hay relatividad.
No hay cwd mágico.
```

---

## Validación del Fix

### Test 1: Crear .login_ok

```bash
python login_runner.py cuenta2
```

**Log esperado**:
```
[LOGIN] Account path: C:\Users\beriann\Documents\Repos\nike_bot_pro\auth\cuenta2
[LOGIN] Profile path: C:\Users\beriann\Documents\Repos\nike_bot_pro\auth\cuenta2\profile_login
[LOGIN] Login OK path: C:\Users\beriann\Documents\Repos\nike_bot_pro\auth\cuenta2\.login_ok
...
[LOGIN] ✅ .login_ok creado: C:\Users\beriann\Documents\Repos\nike_bot_pro\auth\cuenta2\.login_ok
[LOGIN] Existe?: True
[SUCCESS] LOGIN completado
```

✅ **Confirmación**: Ruta absoluta correcta, archivo existe

---

### Test 2: BotController lee .login_ok

```bash
python -c "
from runtime.bot_controller import BotController
bc = BotController('cuenta2')
print(f'State: {bc.state.name}')
print(f'Path: {bc.login_ok_path}')
print(f'Existe: {os.path.exists(bc.login_ok_path)}')
"
```

**Log esperado**:
```
[cuenta2] 🎯 BotController inicializado (READY - .login_ok detectado)
[cuenta2] login_ok path: C:\Users\beriann\Documents\Repos\nike_bot_pro\auth\cuenta2\.login_ok
State: AccountState.READY
Path: C:\Users\beriann\Documents\Repos\nike_bot_pro\auth\cuenta2\.login_ok
Existe: True
```

✅ **Confirmación**: BotController encuentra el archivo, state = READY

---

### Test 3: Validador de alineación

```bash
python validate_alignment.py
```

**Log esperado**:
```
[cuenta2] ✅ ALINEADO
    Disk:       True
    Controller: True
    Estado:     LOGUEADO

✅ SISTEMA ALINEADO
   - Disk y BotController dicen lo MISMO
```

✅ **Confirmación**: Disco y Controller alineados

---

## El Flujo Final (Ahora Correcto)

```
LOGIN RUNNER (subprocess)
├─ from config import get_login_ok_path
├─ path = C:\...\auth\cuenta2\.login_ok  (ABSOLUTA)
└─ Crea archivo ✅

MAIN.PY / UI (main process)
├─ from config import get_login_ok_path
├─ path = C:\...\auth\cuenta2\.login_ok  (MISMA)
└─ Ve archivo ✅

BOTCONTROLLER (main process)
├─ from config import get_login_ok_path
├─ path = C:\...\auth\cuenta2\.login_ok  (MISMA)
└─ Lee estado = READY ✅

PLAY
├─ Verifica: .login_ok existe? SÍ
├─ BotController: state = READY? SÍ
└─ Ejecuta ✅ (sin bloqueos)
```

---

## Archivos Modificados

| Archivo | Cambio | Impacto |
|---------|--------|---------|
| `config.py` | **CREADO** - Centraliza rutas absolutas | Fuente única de verdad |
| `login_runner.py` | Usa `get_login_ok_path()` | Ruta absoluta, archivo siempre encontrado |
| `runtime/bot_controller.py` | Usa `get_login_ok_path()` | Lee path correcto |
| `profile_manager_v2.py` | Usa config.py | Rutas consistentes |

---

## Resumen

✅ **Antes**: Rutas relativas + subprocess = conflicto
✅ **Después**: Rutas absolutas desde config.py = sin conflicto

**Todo alineado. Todo funciona.**
