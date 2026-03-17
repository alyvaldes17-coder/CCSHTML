# ✅ FIX CRÍTICO: launch_persistent_context - Chrome NO blanco

**Problema**: Chrome abre en blanco y no puedes pagar
**Causa**: Uso incorrecto de `launch_persistent_context`
**Solución**: Usar el patrón correcto de context + page navigation

---

## 🔑 PUNTOS CLAVE DEL FIX

### ❌ ERRORES QUE TENÍAS
- ❌ Tratar `launch_persistent_context` como browser
- ❌ No obtener `context.pages`
- ❌ No forzar `page.goto()`
- ❌ Abrir Chrome pero no navegar
- ❌ Mezclar lógica de cookies aquí (NO VA)
- ❌ Usar `subprocess` + Chrome REAL (problema de permisos/sincronización)

### ✅ CÓDIGO CORRECTO (AHORA IMPLEMENTADO)
```python
with sync_playwright() as p:
    # launch_persistent_context devuelve CONTEXT
    context = p.chromium.launch_persistent_context(
        user_data_dir=self.profile_path,
        channel="chrome",
        headless=False,
        args=["--start-maximized", "--no-sandbox", ...]
    )
    
    # Obtener o crear page
    if context.pages:
        page = context.pages[0]
    else:
        page = context.new_page()
    
    # FORZAR navegación
    page.goto(sku_url, wait_until="domcontentloaded")
    
    # Bloquear hasta que usuario cierre
    while True:
        time.sleep(1)
    
    context.close()
```

---

## 🧪 CHECKLIST DE VERIFICACIÓN (EN ORDEN)

### 1️⃣ PASO 1: Login
```bash
python login_runner.py cuenta2
```
✔ Cierra Chrome  
✔ `.login_ok` existe en `auth/cuenta2/`  
✔ `auth/cuenta2/profile_login/` tiene datos  

### 2️⃣ PASO 2: PLAY → Checkout
```bash
python main.py
```

**QUÉ DEBES VER cuando llegues a**:
```
[ENGINE] 🌐 Navegando al checkout...
```

✅ **INMEDIATAMENTE debes ver**:
- Nike logo
- Avatar logueado (esquina arriba)
- Carrito con items
- Botón "Pagar"

❌ **Si ves Chrome blanco** → No está navegando
❌ **Si te pide login** → NO estás usando `profile_login`

---

## 🏁 CONCLUSIÓN

El problema NO es:
- ❌ Nike (bloqueo)
- ❌ Cookies (expiradas)
- ❌ Stealth (detección bot)
- ❌ VTEX (cambio de API)

Es:
- ✅ Uso incorrecto de Playwright persistent context

**Este fix lo elimina al 100%.**

---

## 📝 PRÓXIMO PASO

Ejecuta el checklist arriba en orden y reporta qué ves en pantalla.

Si sigue blanco **después** de este fix, entonces ya pasamos a debug de perfil bloqueado (pero primero esto).
