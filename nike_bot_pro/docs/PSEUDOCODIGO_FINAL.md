# 🎯 PSEUDOCÓDIGO FINAL - EL ÚNICO FLUJO VÁLIDO

**Esta es la fuente de verdad. Si tu código hace algo diferente, está ROTO.**

---

## Estructura general (~30 líneas)

```python
# =========================
# BOT FLOW DEFINITIVO
# =========================

# ---- LOGIN (previo al drop, manual) ----
if UI.click_login:
    open_chrome(profile_path)
    wait_user_login_and_close()
    mark_account_login_ok()
    return

# ---- PLAY (drop time) ----
if UI.click_play:
    if not account.login_ok:
        block("Debes loguearte primero")
        return

    start_worker_thread()

# ---- WORKER (backend loop, determinístico) ----
def worker():
    
    # PRE-FLIGHT (rápido)
    if not check_profile_exists(profile_path):
        fail("Perfil inválido")
        return
    
    # BACKEND LOOP (SIN CHROME)
    while True:
        # Paso 1: Price check
        price = backend_check_price(sku)
        
        if price == 0:
            sleep(0.3)
            continue  # Reintentar check precio
        
        # Paso 2: ATC BACKEND (UNA SOLA VEZ)
        ok = backend_add_to_cart(sku)
        if not ok:
            retry_fast()  # Max 1 retry
            continue
        
        # Paso 3: FREEZE ABSOLUTO
        disable_all_requests()    # No más HTTP
        disable_all_retries()     # No más loops
        disable_all_timers()      # No más timeouts
        
        # Paso 4: HANDOVER (abrir Chrome)
        open_chrome(profile_path)
        open_magic_link(sku)
        
        # Paso 5: FIN DEL BOT
        return
```

---

## Componentes principales (EXACTOS)

### 1. LOGIN (manual)

```python
def login_runner(account):
    """
    Usuario loguea manualmente en Nike.cl
    
    REGLAS:
    ✅ Abrir Chrome real (subprocess, no Playwright)
    ✅ Esperar a que user cierre la ventana
    ✅ Crear archivo .login_ok
    
    ❌ NO verificar login automáticamente
    ❌ NO inyectar cookies
    ❌ NO usar Playwright
    """
    chrome_path = find_chrome()
    profile_path = get_profile_path(account)
    
    subprocess.Popen([
        chrome_path,
        f"--user-data-dir={profile_path}",
        "https://www.nike.cl/login"
    ])
    
    # Esperar a que Chrome se cierre
    wait_for_chrome_close()
    
    # Marcar como logueado
    (profile_path / ".login_ok").write_text("OK")
```

### 2. PRE-FLIGHT (headless validation)

```python
def preflight(account, sku):
    """
    Verificar que Nike reconoce la sesión
    
    REGLAS:
    ✅ Usar Playwright headless
    ✅ Ir a Nike.cl/mi-cuenta
    ✅ Buscar locator "Hola"
    ✅ Si no lo ve = sesión inválida = FAIL
    
    ❌ NO obtener cookies
    ❌ NO inyectar sesión
    ❌ NO modificar profile
    """
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(user_data_dir=profile_path)
    page = context.new_page()
    
    page.goto("https://www.nike.cl/mi-cuenta")
    
    try:
        page.locator("text=Hola").wait_for()
        return True  # ✅ Sesión válida
    except:
        return False  # ❌ Sesión inválida
    finally:
        browser.close()
```

### 3. PRICE CHECK (backend only)

```python
def backend_check_price(sku):
    """
    Verificar si el precio está disponible en VTEX
    
    REGLAS:
    ✅ GET https://www.nike.cl/api/checkout/pub/orderForm
    ✅ Retornar price (0 si no disponible)
    ✅ Timeout: 1.5s
    
    ❌ NO abrir Chrome
    ❌ NO usar Playwright
    ❌ NO inyectar JS
    """
    session = get_session(account)
    
    try:
        r = session.get(
            "https://www.nike.cl/api/checkout/pub/orderForm",
            timeout=1.5
        )
        
        if r.status_code == 200:
            data = r.json()
            items = data.get("items", [])
            
            if items:
                return items[0].get("price", 0)
        
        return 0
    
    except:
        return 0
```

### 4. ATC BACKEND (EXACTO)

```python
def backend_add_to_cart(sku):
    """
    Agregar al carrito vía VTEX backend
    
    REGLAS:
    ✅ GET /checkout/cart/add?sku=SKU&qty=1&seller=1&sc=1
    ✅ Status 200 o 302 = éxito
    ✅ Timeout: 2s max
    ✅ Retries: máx 1 (solo por timeout)
    
    ❌ NO hacer POST
    ❌ NO usar /api/
    ❌ NO cambiar qty/seller/sc
    ❌ NO hacer retry por lógica
    ❌ NO abrir Chrome
    """
    session = get_session(account)
    
    try:
        r = session.get(
            "https://www.nike.cl/checkout/cart/add",
            params={
                "sku": sku,
                "qty": 1,
                "seller": 1,
                "sc": 1
            },
            timeout=2,
            allow_redirects=False
        )
        
        if r.status_code in (200, 302):
            return True
    
    except requests.Timeout:
        return False
    
    except:
        return False
```

### 5. FREEZE (OBLIGATORIO)

```python
def freeze_backend(session):
    """
    Detener COMPLETAMENTE el backend
    
    REGLAS:
    ✅ Cerrar sesión HTTP
    ✅ Detener todos los threads
    ✅ Deshabilitar todos los timers
    ✅ Deshabilitar todos los retries
    
    ❌ NO seguir haciendo requests
    ❌ NO mantener threads abiertos
    ❌ NO tener timeouts activos
    ❌ NO iterar más
    
    Después de esto, SOLO Chrome + usuario.
    """
    if session:
        session.close()
    
    self.running = False
    self.allow_http = False
    self.allow_seed = False
    self.allow_refresh = False
    
    # Matar todos los threads
    for thread in self.threads:
        thread.stop()
    
    # Limpiar timers
    for timer in self.timers:
        timer.cancel()
```

### 6. HANDOVER (abrir magic link)

```python
def handover(account, sku):
    """
    Abrir Chrome con magic link
    
    REGLAS:
    ✅ Abrir Chrome real (mismo profile del login)
    ✅ Ir a magic link exacto
    ✅ Dejar abierto (user completa checkout)
    
    ❌ NO automatizar checkout
    ❌ NO hacer más requests
    ❌ NO cerrar Chrome
    """
    magic_link = f"https://www.nike.cl/checkout/cart/add?sku={sku}&qty=1&seller=1&sc=1"
    
    chrome_path = find_chrome()
    profile_path = get_profile_path(account)
    
    subprocess.Popen([
        chrome_path,
        f"--user-data-dir={profile_path}",
        magic_link
    ])
    
    # No hacer nada más
    # User completa checkout
```

---

## Magic link (NO CAMBIAR NUNCA)

```
https://www.nike.cl/checkout/cart/add?sku=SKU&qty=1&seller=1&sc=1
```

**Es exactamente el mismo endpoint que el GET backend.**

**Por qué?**
- GET backend agrega al carrito (VTEX side)
- Magic link abre el mismo sitio en browser (user side)
- Nike.cl reconoce que el item ya está en carrito
- User termina el checkout

**No es:**
- ❌ /checkout/#/payment
- ❌ /checkout (sin /cart/add)
- ❌ /api/checkout
- ❌ Otra URL

---

## Lo que NUNCA debe ocurrir

### ❌ 1. ATC en browser

```python
# NUNCA HAGAS ESTO
page.click("Add to cart")                    # ❌
frontend_add_to_cart()                       # ❌
vtexjs.checkout.addToCart()                  # ❌
execute_js("document.addToCart()")           # ❌
```

**ATC SOLO ES BACKEND.**

### ❌ 2. Session seed automático

```python
# NUNCA HAGAS ESTO
seed_golden_session()                        # ❌
copy_cookies_browser_to_session()            # ❌
copy_cookies_session_to_browser()            # ❌
sync_session_state()                         # ❌
```

**El profile de Chrome YA ES la sesión. No se toca.**

### ❌ 3. Retries después de ATC OK

```python
# NUNCA HAGAS ESTO
if atc_ok:
    for retry in range(3):                   # ❌
        revalidate_price()
        double_check_orderform()
        confirm_status()
        sleep(0.1)
```

**Si ATC OK → FREEZE. Fin. No hay más lógica.**

### ❌ 4. Chrome dentro del loop

```python
# NUNCA HAGAS ESTO
while True:
    browser = open_chrome()                  # ❌
    check_page()
    browser.close()
    
    price = check_backend()
    if price > 0:
        atc()
        break
```

**Chrome SOLO se abre una vez y solo al final.**

### ❌ 5. Múltiples caminos

```python
# NUNCA HAGAS ESTO
if mode == "fast":                           # ❌
    atc_backend()
elif mode == "safe":
    atc_browser()
elif mode == "hybrid":
    atc_backend()
    atc_browser()
```

**Un camino. Fin.**

---

## State machine simplificado

```
START
  ↓
LOGIN (manual)
  ↓
PREFLIGHT (validate)
  ↓
PRICE_LOOP (backend check)
  ├→ price == 0 → sleep → PRICE_LOOP
  └→ price > 0 → ATC
       ↓
ATC (backend)
  ├→ fail → ATC (1 retry)
  ├→ success after retry → FREEZE
  └→ success first try → FREEZE
       ↓
FREEZE (kill backend)
  ↓
HANDOVER (open magic link)
  ↓
WAITING_HUMAN (user completes checkout)
  ↓
DONE
```

---

## Logging (para debugging)

```python
# ✅ Log ESTOS eventos
print("[LOGIN] Chrome abierto")
print("[PREFLIGHT] Nike reconoce sesión ✅")
print("[PRICE] Price = 0 (esperando...)")
print("[PRICE] Price > 0 → ATC")
print("[ATC] Status 200 → OK")
print("[FREEZE] Backend cerrado")
print("[HANDOVER] Magic link abierto")
print("[DONE] Waiting for user")

# ❌ NO loguees
session_seed()
seed_cookies()
retry loop iterations
verification loops
```

---

## Validación final

**Antes de ejecutar en un drop:**

✅ Todos los 10 pasos están presentes
✅ No hay ATC en browser
✅ No hay session seed
✅ No hay retries innecesarios
✅ No hay Chrome en el loop
✅ FREEZE es absoluto
✅ Magic link es exacto
✅ No hay múltiples caminos

---

## TL;DR

**Este pseudocódigo es TODO lo que necesitas para ganar drops.**

No es complejidad. Es disciplina.

No es innovación. Es consistencia.

No necesita más features. Necesita menos.

**Ejecuta esto exactamente como está escrito, sin variaciones.**

Eso gana.
