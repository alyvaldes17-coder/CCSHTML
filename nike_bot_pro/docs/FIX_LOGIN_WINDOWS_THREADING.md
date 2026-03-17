# FIX CRÍTICO: LOGIN + Threading + SingletonLock (Windows Playwright)

## 🔴 PROBLEMA REAL IDENTIFICADO

El ciclo de fallo:

```
1. Presionas LOGIN
   ↓
2. Playwright intenta abrir Chrome
   ↓
3. Si está en MAIN THREAD → UI se congela ("se pega")
   ↓
4. Usuario fuerza cierre por impaciencia
   ↓
5. Queda archivo SingletonLock bloqueando el perfil
   ↓
6. Siguiente intento: Chrome no abre ("No abre")
   ↓
7. Vuelves al paso 1 (bucle infinito)
```

## ✅ SOLUCIÓN IMPLEMENTADA (3 partes)

### PARTE 1: THREAD SEPARADO en `_login_v2()`

**Antes:** Ejecutaba en main thread → UI se congelaba ❌

**Ahora:** Ejecuta en daemon thread → UI responde ✅

```python
def _login_v2(self, controller, account_name: str):
    def do_login():
        controller.handle_btn_login_click()  # ← EN THREAD
        self.root.after(0, lambda: self._refresh_single_row(account_name))
    
    thread = threading.Thread(target=do_login, daemon=True)
    thread.start()  # ← NO BLOQUEA UI
```

**Ventaja:** UI sigue respondiendo mientras Chrome está abierto

### PARTE 2: LIMPIEZA DE SingletonLock

Se agrega en dos lugares:

**2a. En `BotController.handle_btn_login_click()`**

```python
import os

lock_file = os.path.join(self.profile_path, "SingletonLock")
if os.path.exists(lock_file):
    try:
        os.remove(lock_file)
        print(f"[{self.account_name}] 🧹 SingletonLock eliminado")
    except Exception:
        print(f"[{self.account_name}] ⚠️ No pude borrar SingletonLock")
```

**2b. En `PlaywrightEngine.launch_manual_login()`**

```python
lock_file = os.path.join(self.profile_path, "SingletonLock")
if os.path.exists(lock_file):
    try:
        os.remove(lock_file)
        print("[PlaywrightEngine] 🧹 SingletonLock eliminado")
    except:
        pass
```

**Ventaja:** Se desbloquea el perfil automáticamente antes de intentar abrir Chrome

### PARTE 3: MEJORA EN `launch_manual_login()`

```python
try:
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=self.profile_path,
            headless=False,
            viewport=None,
            args=["--start-maximized", ...]
        )
        
        page = browser.pages[0]
        page.goto("https://www.nike.cl/account/login")
        
        # ESPERA hasta que usuario cierre Chrome
        page.wait_for_event("close", timeout=0)
        
        return True
        
except Exception as e:
    return False
    
finally:
    print("[PlaywrightEngine] 🔒 Cerrando contexto de Playwright...")
```

**Ventaja:** Try/finally asegura limpieza even si hay error

## 🎯 FLUJO CORRECTO AHORA

```
[UI] Usuario presiona botón "LOGIN"
  ↓
_login_v2() → lanza THREAD
  ↓
[THREAD] handle_btn_login_click()
  ├─ 🧹 Limpia SingletonLock
  ├─ 🟢 Abre Chrome
  └─ ⏳ Espera a que usuario cierre
  ↓
[MAIN THREAD] UI sigue respondiendo (NO congelada)
  ↓
[USUARIO] Loguea en Nike y cierra Chrome
  ↓
[THREAD] Valida sesión (validate_session_real)
  ├─ Si OK → state = READY
  └─ Si fail → state = NO_AUTH
  ↓
[THREAD] Termina
  ↓
[UI] Se actualiza automáticamente (refresh cada 1s)
```

## 📋 CHECKLIST DE CAMBIOS

- ✅ `ui/app.py - _login_v2()`: Ahora usa `threading.Thread()`
- ✅ `bot_controller.py - handle_btn_login_click()`: Limpia SingletonLock
- ✅ `playwright_engine_v2.py - launch_manual_login()`: Limpia SingletonLock + try/finally
- ✅ `playwright_engine_v2.py`: Agregado `import os`

## 🧪 CÓMO VERIFICAR QUE FUNCIONA

### Prueba 1: Limpieza manual (UNA SOLA VEZ)

```bash
cd auth/cuenta2/profile_pw
# Si ves un archivo "SingletonLock" → BÓRRALO
# Si no está → OK
```

### Prueba 2: Desde UI
```bash
python main.py
```

1. Presiona LOGIN en cualquier cuenta
2. Chrome debe abrir **INMEDIATAMENTE** (sin congelamientos)
3. La UI debe permanecer **RESPONSIVA** (prueba hacer scroll)
4. Loguéate en Nike
5. Cierra Chrome
6. Espera 2-3 segundos (validación real)
7. El botón PLAY debe estar habilitado (verde)

### Prueba 3: Cierre forzado (simulando fallo)
```
1. Presiona LOGIN
2. Abre Chrome
3. Presiona CTRL+ALT+DEL → Cierra Chrome manualmente
4. Presiona LOGIN de nuevo
5. Chrome debe abrir sin problemas (gracias a limpieza de lock)
```

## 📊 ANTES vs DESPUÉS

| Aspecto | Antes | Después |
|---------|-------|---------|
| UI se congela | ✅ Sí | ❌ No |
| Chrome abre | ❌ NO (o con delay) | ✅ SÍ (inmediato) |
| SingletonLock bloqueado | ✅ Sí | ❌ Se limpia automáticamente |
| Se puede cerrar app durante LOGIN | ❌ NO | ✅ SÍ |
| Thread daemon | ❌ NO | ✅ SÍ |
| Try/finally | ❌ NO | ✅ SÍ |

## 🔧 REGLA DE ORO

### Para ABRIR Chrome (LOGIN):
```python
✅ SIEMPRE en thread → No congela UI
✅ Limpiar SingletonLock primero
✅ Try/finally para limpieza
```

### Para MONITOREAR backend (PLAY):
```python
✅ También en thread (worker_loop)
✅ Sin Chrome (es backend-only)
```

## 📝 RESUMEN

- ✅ Threading separado → UI no se congela
- ✅ SingletonLock limpiado automáticamente
- ✅ Try/finally asegura limpieza
- ✅ Compatible con Windows + Playwright
- ✅ Sigue arquitectura 6-mejoras

**Resultado esperado:** Chrome se abre al presionar LOGIN sin congelamientos ✅

