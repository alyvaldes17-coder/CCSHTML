# 🔐 Master/Slave Profile Architecture - Guía Completa

## El Problema (Windows Chromium SingletonLock)

**Síntoma:** 
```
❌ Chrome won't open
❌ SingletonLock file locked by another process
❌ Bot falla en segundo intento
```

**Causa Raíz:**
Windows Chromium crea un `SingletonLock` file que persiste aunque cerremos Chrome. 
Esto bloquea intentos posteriores de abrir el mismo perfil.

**Solución Definitiva: Master/Slave Architecture**

---

## 🏗️ Arquitectura Master/Slave

```
auth/cuenta2/
│
├── profile_login/           ← MASTER (conservado, sacrosanto)
│   ├── Local Storage        ├─ Usuario loguea UNA SOLA VEZ
│   ├── Cookies              ├─ Contiene sesión válida
│   └── SessionStorage       └─ NUNCA tocado por el bot
│
└── profile_run/             ← SLAVE (descartable)
    ├── Local Storage (copia)├─ Clonado de master
    ├── Cookies (copia)      ├─ Usado por bot para ejecutar
    └── SessionStorage (cpia)└─ Destruido después
```

**Ventajas:**
✅ Master nunca se corrompe (usuario loguea una sola vez)
✅ Bot siempre arranca con sesión fresca (clona master)
✅ SingletonLock se limpia automáticamente (slave es descartable)
✅ Multi-cuenta simultáneo sin conflictos

---

## 📋 Flujo de Uso

### PASO 1: Setup Inicial (UNA SOLA VEZ por cuenta)

```bash
# Loguear cuenta2
python setup_login.py cuenta2

# El script:
# 1. Abre Chrome con auth/cuenta2/profile_login
# 2. TÚ logueas (email + contraseña)
# 3. Cierras Chrome
# 4. Cookies se guardan automáticamente
```

**Resultado:**
```
auth/cuenta2/
├── profile_login/
│   ├── Cookies (✅ sesión Nike guardada)
│   ├── Local Storage
│   └── ...
```

### PASO 2: Bot Ejecuta (automático, múltiples veces)

```python
# main.py o main_army.py
bot = BotController("cuenta2")

# Internamente:
# 1. Verifica que profile_login tiene cookies (master check)
# 2. Limpia profile_run del run anterior (desbloqueador)
# 3. Clona profile_login → profile_run (<0.5s)
# 4. Valida sesión en profile_run
# 5. Abre Playwright con profile_run LIMPIO
# 6. Ejecuta bot (monitoreo, compra, etc)
# 7. Descarta profile_run (listo para siguiente run)
```

**Resultado:**
```
auth/cuenta2/
├── profile_login/              (unchanged, pristine)
│   ├── Cookies (✅ original)
│   └── ...
│
└── profile_run/                (fresh clone)
    ├── Cookies (copia)
    ├── Local Storage (copia)
    └── [SingletonLock se limpia automáticamente]
```

### PASO 3: Multi-Cuenta Simultáneo

```bash
# Loguear múltiples cuentas (una sola vez)
python setup_login.py cuenta2
python setup_login.py cuenta3
python setup_login.py cuenta_vip

# Luego, ejecutar Ejército (simultáneo)
python main_army.py
  → Recluta cuenta2, cuenta3, cuenta_vip
  → Lanza ataques coordinados
  → Cada cuenta: clona su master, compra, descarta slave
  → Sin bloqueos de lock
```

---

## 🔧 API - ProfileManager

**Ubicación:** `profile_manager.py`

### Crear instancia

```python
from profile_manager import ProfileManager

pm = ProfileManager("cuenta2")  # o "cuenta3", "cuenta_vip", etc
```

### Métodos principales

#### `verify_master_profile() → bool`
Verifica que profile_login tiene cookies válidas.

```python
if pm.verify_master_profile():
    print("✅ Master profile tiene sesión")
else:
    print("❌ Ejecuta: python setup_login.py cuenta2")
```

#### `cleanup_run_profile(force=False) → bool`
Limpia profile_run (elimina locks).

```python
if pm.cleanup_run_profile():
    print("✅ profile_run limpiado")
else:
    print("⚠️ No pude limpiar (Chrome abierto?)")
    # Intenta con force=True si persiste
    pm.cleanup_run_profile(force=True)
```

#### `clone_login_to_run() → bool`
Clona master → slave (<0.5s).

```python
if pm.clone_login_to_run():
    print("✅ Clonado exitosamente")
    profile_run = pm.get_run_profile_path()
    # Usar profile_run para Playwright
else:
    print("❌ Error clonando")
```

#### `get_login_profile_path() → str`
Retorna ruta a master profile.

```python
path = pm.get_login_profile_path()
# → "auth/cuenta2/profile_login"
```

#### `get_run_profile_path() → str`
Retorna ruta a slave profile.

```python
path = pm.get_run_profile_path()
# → "auth/cuenta2/profile_run"
```

---

## 🤖 Integración con BotController

**Automático** - BotController ya usa ProfileManager internamente:

```python
from runtime.bot_controller import BotController

# Crear bot (usa Master/Slave automáticamente)
bot = BotController("cuenta2")

# handle_btn_login_click() hace:
# 1. Verifica profile_login tiene cookies
# 2. Limpia profile_run
# 3. Clona profile_login → profile_run
# 4. Valida sesión
# 5. Marca como READY
```

---

## 🎯 Guía Rápida (Quick Start)

### Configuración inicial (una vez por servidor)

```bash
# 1. Loguear conta1
python setup_login.py cuenta2

# Espera a que Chrome se abra
# → Loguéate con tu Nike account
# → Cierra Chrome
# → Cookies guardadas

# 2. Loguear cuenta2 (opcional, para multi-account)
python setup_login.py cuenta3

# 3. Verificar que funciona
python main.py
# → Debería detectar sesión en cuenta2
# → Click en "LOGIN" → valida sin abrir Chrome
# → Listo para monitorear drops
```

### Ejecución normal

```bash
# Single account
python main.py

# Multi-account (simultáneo)
python main_army.py
```

---

## 🔍 Troubleshooting

### "❌ No hay sesión guardada en profile_login"

**Causa:** Nunca ejecutaste `setup_login.py` para esa cuenta.

**Solución:**
```bash
python setup_login.py cuenta2
```

### "❌ Chrome won't open" o "SingletonLock blocked"

**Causa:** El anterior run no limpió bien el slave.

**Solución:**
```python
from profile_manager import ProfileManager

pm = ProfileManager("cuenta2")
pm.cleanup_run_profile(force=True)  # Intenta agresivamente
```

**Si persiste:**
1. Cierra Chrome completamente
2. Elimina manualmente: `auth/cuenta2/profile_run`
3. Reintenta

### "⚠️ Timeout navigating to Nike"

**Causa:** Conexión lenta o Nike está caído.

**Solución:**
- Intenta de nuevo en unos segundos
- Verifica internet está activo
- Si es error consistente, Nike podría estar caído

### "Error clonando perfil"

**Causa:** Permisos de archivo o disco lleno.

**Solución:**
```bash
# Verifica que puedes escribir en auth/
# Libera espacio en disco (clone toma <100MB)
# Verifica permisos: auth/cuenta2/ debe ser writable
```

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Nike Bot Pro                          │
│           Master/Slave Profile System                    │
└─────────────────────────────────────────────────────────┘

┌─ SETUP PHASE (One-time) ─────────────────────────────┐
│                                                        │
│  python setup_login.py cuenta2                        │
│         ↓                                              │
│  login_runner.py opens Chrome                         │
│         ↓                                              │
│  User logs in (email + password)                      │
│         ↓                                              │
│  Cookies saved → auth/cuenta2/profile_login           │
│         ↓                                              │
│  ✅ Master profile ready                              │
└────────────────────────────────────────────────────────┘

┌─ EXECUTION PHASE (Repeating) ────────────────────────┐
│                                                        │
│  BotController("cuenta2")                             │
│         ↓                                              │
│  ProfileManager.verify_master_profile() → ✅          │
│         ↓                                              │
│  ProfileManager.cleanup_run_profile()                 │
│         ↓                                              │
│  ProfileManager.clone_login_to_run()                  │
│         ↓                                              │
│  Playwright opens auth/cuenta2/profile_run            │
│         ↓                                              │
│  Bot executes (monitor, checkout, etc)               │
│         ↓                                              │
│  Close Playwright                                      │
│         ↓                                              │
│  Delete profile_run (cleanup for next run)            │
│         ↓                                              │
│  ✅ Ready for next execution                          │
└────────────────────────────────────────────────────────┘

[MASTER] profile_login     [SLAVE] profile_run
   ↑                           ↑
   │                           └─ Cloned fresh each run
   │
   └─ User logs in once
```

---

## 🚀 Production Checklist

- [ ] Ejecutaste `python setup_login.py` para cada cuenta
- [ ] Verifica que `auth/cuentaX/profile_login` existe y tiene cookies
- [ ] BotController usa `ProfileManager` (check: `from profile_manager import ProfileManager`)
- [ ] PlaywrightEngine recibe `profile_run` path (no hardcoded `profile_pw`)
- [ ] `profile_manager.py` está en workspace root
- [ ] main.py y main_army.py importan BotController (que ya usa ProfileManager)

---

## 📝 Notes

**Clone Speed:** <0.5 segundos (solo copia Cookies, Local Storage, Session Storage)

**Profile Size:** 
- Master: ~10-50MB (sesión completa)
- Clone: <1MB (sin cache innecesario)

**Security:** 
- Master profile nunca es tocado por el bot
- Slave es descartable y contiene solo cookies clonadas
- No hay credenciales en disco (solo cookies de sesión)

---

**Status:** ✅ Production Ready  
**Last Updated:** [Implementación actual]  
**Tested on:** Windows 10/11 with Chromium + Playwright sync
