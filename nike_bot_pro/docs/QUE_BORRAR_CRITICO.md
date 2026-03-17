# 🔥 QUÉ ELIMINAR DEL REPO - AUDITORIA CRÍTICA

**Si dejas esto en el código, viola el pseudocódigo final.**

**Si viola el pseudocódigo, PIERDE en drops.**

---

## Categoría 1: ATC en browser (SUPER CRÍTICO)

### Buscar y BORRAR completamente:

```python
❌ page.click("Add to cart")
❌ page.click("Agregar al carrito")
❌ locator("button:has-text('Add to cart')").click()
❌ locator("button[data-testid='add-to-cart']").click()
❌ page.evaluate("vtexjs.checkout.addToCart(...)")
❌ frontend_add_to_cart()
❌ browser_add_to_cart()
❌ checkout_add_item()
❌ add_to_cart_frontend()
```

### Archivos probables:

- `runner/` (TODO)
- `controller/` (TODO)
- `engine/` (TODO)
- Cualquier archivo con "browser_atc" en el nombre
- Cualquier archivo con "checkout" en el name

### Acción:

```bash
# Búsqueda rápida
grep -r "\.click.*add" .
grep -r "\.click.*cart" .
grep -r "vtexjs\.checkout" .
grep -r "evaluate.*addToCart" .
```

Si encuentras algo:
- **BORRAR** la función completa
- **BORRAR** las llamadas a esa función
- **BORRAR** el archivo si SOLO contenía ATC browser

---

## Categoría 2: Session seed (MUY CRÍTICO)

### Buscar y DESACTIVAR:

```python
❌ seed_golden_session()
❌ copy_cookies_browser_to_session()
❌ copy_cookies_session_to_browser()
❌ sync_session_state()
❌ copy_orderForm()
❌ inherit_cookies()
❌ use_golden_session()
❌ apply_session_seed()
```

### Archivos probables:

- `runner/session_seed.py` (BORRAR)
- `vtex/session.py` (revisar)
- `engines/` (TODO)
- Cualquier archivo con "seed" en el nombre

### Acción:

```bash
# Búsqueda
grep -r "seed" . --include="*.py"
grep -r "copy_cookies" . --include="*.py"
grep -r "sync_session" . --include="*.py"
```

Si encuentras:
- Si es función STANDALONE → **BORRAR archivo**
- Si es parte de otra función → **COMENTAR o BORRAR líneas**
- Si es llamada → **ELIMINAR la llamada**

---

## Categoría 3: Reintentos después de ATC OK (CRÍTICO)

### Buscar y BORRAR:

```python
❌ if atc_ok:
       for retry in range(N):
           revalidate_price()
           ❌

❌ if atc_result.success:
       time.sleep(0.1)
       verify_atc_again()  # ❌

❌ after_atc_wait_and_recheck()

❌ double_check_atc()

❌ confirm_add_to_cart()

❌ price_monitor_after_atc()
```

### Patrón a buscar:

```python
# ❌ ESTO NO DEBE EXISTIR
if atc_ok:
    # Cualquier cosa después es sospechosa
    ...
```

Después de ATC OK, SOLO debe haber FREEZE + HANDOVER.

### Archivos probables:

- `runner/` (TODO)
- `controller/` (TODO)
- `engines/` (TODO)

### Acción:

Buscar: `if.*atc.*ok` o `if.*atc.*success`

Revisar qué viene después. Si hay más de FREEZE + HANDOVER → **BORRAR**.

---

## Categoría 4: Chrome en el loop (CRÍTICO)

### Buscar y BORRAR:

```python
❌ while True:
       browser = open_chrome()  # ← AQUÍ NO

❌ for retry in range(N):
       browser = launch()       # ← AQUÍ NO

❌ if price > 0:
       browser = new_browser()  # ← AQUÍ NO

❌ price_monitor(browser)        # ← Chrome no entra

❌ check_with_browser()          # ← En el loop
```

### Regla:

**Chrome SOLO se abre una vez, DESPUÉS de FREEZE, en HANDOVER.**

### Archivos probables:

- `engine/` (TODO)
- `controller/` (TODO)
- Cualquier función con "while True" que use Playwright

### Acción:

Buscar: `while.*:` y revisar si hay `browser = ` o `page = `

Si lo encuentras → **BORRAR esa rama**

---

## Categoría 5: Lógica paralela/fallback (MUY CRÍTICO)

### Buscar y BORRAR:

```python
❌ if mode == "MODE_A":
       atc_backend()
   elif mode == "MODE_B":
       atc_browser()

❌ if api_fails:
       try_browser()

❌ MODE_FAST / MODE_SAFE / MODE_HYBRID

❌ ATC_VARIANT_1, ATC_VARIANT_2, ATC_VARIANT_3

❌ if backend_atc() fails:
       fallback_to_browser()

❌ try_backend_then_browser()
```

### Regla:

**UN camino. No hay alternativas. No hay Plans B.**

### Archivos probables:

- `runner/` (TODO)
- `controller/` (TODO)
- `manager/` (TODO)

### Acción:

Buscar: `if.*mode` o `if.*variant` o `if.*fail.*then`

**BORRAR TODO MENOS UNO DE LOS CAMINOS.**

El camino que queda:
```
LOGIN → PREFLIGHT → PRICE_LOOP → ATC_BACKEND → FREEZE → HANDOVER → DONE
```

---

## Categoría 6: Pricing loops (CRÍTICO)

### Buscar y BORRAR:

```python
❌ price_monitor()        # Continuous loop
❌ pricing_watcher()      # Watching prices
❌ monitor_prices()       # Monitoring
❌ watch_for_availability()
❌ wait_for_price_drop()
❌ check_price_every_x_ms()
```

### Acción:

**CONSERVAR**: `backend_check_price()` (se usa en PRICE_LOOP)

**BORRAR**: Cualquier función que MONITOR o WATCH el precio continuamente.

---

## Categoría 7: Verification loops (CRÍTICO)

### Buscar y BORRAR:

```python
❌ verify_atc()
❌ validate_atc()
❌ confirm_item_in_cart()
❌ check_orderform()
❌ revalidate()
❌ double_check()
```

**DESPUÉS de ATC OK, NO hay verificación.**

Solo FREEZE.

---

## Categoría 8: Thread management (REVISAR)

### BORRAR:

```python
❌ retry_worker_thread()
❌ watcher_thread()
❌ monitor_thread()
❌ seed_thread()
```

### CONSERVAR:

```python
✅ main_thread (flujo principal)
✅ ui_listener_thread (read-only)
✅ state_listener_thread (read-only)
```

Solo threads que LEEN estado, no threads que ejecutan lógica.

---

## Categoría 9: Async/concurrent logic (CRÍTICO)

### BORRAR:

```python
❌ asyncio.gather(...)
❌ asyncio.create_task(...)
❌ concurrent.futures()
❌ ThreadPoolExecutor para ejecutar ATC en paralelo
❌ multiprocessing.Pool para parallelize ATC
```

**TODO debe ser SECUENCIAL:**

```
LOGIN → CLONE → PREFLIGHT → PRICE_LOOP → ATC → FREEZE → HANDOVER
```

### CONSERVAR:

```python
✅ multiprocessing.Process (1 proceso = 1 account)
✅ Threading para UI listeners (SOLO lectura)
```

---

## Checklist de búsqueda rápida

```bash
# 1. Búsqueda de patrones prohibidos
grep -r "\.click.*cart" . --include="*.py"
grep -r "\.click.*add" . --include="*.py"
grep -r "vtexjs" . --include="*.py"
grep -r "seed" . --include="*.py"
grep -r "monitor" . --include="*.py"
grep -r "watcher" . --include="*.py"
grep -r "verify.*atc" . --include="*.py"
grep -r "double.*check" . --include="*.py"
grep -r "while True:" . --include="*.py" | grep -E "sleep|browser|page"
grep -r "MODE_" . --include="*.py"
grep -r "VARIANT" . --include="*.py"
grep -r "fallback" . --include="*.py"
grep -r "try.*except.*browser" . --include="*.py"

# 2. Búsqueda de directorios sospechosos
find . -type d -name "runner" -o -name "controller" -o -name "manager" -o -name "worker" -o -name "engine"
```

---

## Archivos a BORRAR COMPLETAMENTE

```
❌ runner/                 (TODO - viejo state machine)
❌ controller/             (TODO - viejo controller)
❌ manager/                (TODO - viejo manager)
❌ worker/                 (TODO - viejo workers)
❌ engines/                (TODO - viejo engines)
❌ vtex/                   (TODO - revisar, probablemente viejo)

❌ check_syntax.py
❌ quick_check.py
❌ preflight_check.py
❌ pdp_seeder.py

❌ test_*.py (old tests)
❌ FIX_*.py (old fixes)
❌ FLUJO_*.md (old documentation)
❌ TEMP_*.py (any temp files)
```

---

## Archivos a REVISAR y LIMPIAR

```
⚠️  runtime/backend_vtex.py
    → Debe tener SOLO: atc_backend(), price_check()
    → BORRAR: session_seed(), retry_loops(), verification()

⚠️  runtime/process_states.py
    → Debe tener SOLO: Estados (STARTING, PREFLIGHT, ATC, FREEZE, HANDOVER, DONE, ERROR)
    → BORRAR: Estados innecesarios (RETRY, VERIFY, MONITOR, etc)

⚠️  runtime/multiprocessing_runner.py
    → Debe tener SOLO: run_account() con 10 pasos lineales
    → BORRAR: Loops de reintento, mode switching, fallbacks

⚠️  profile_manager_v2.py
    → Debe tener SOLO: clone_auth_to_run()
    → BORRAR: seed_from_browser(), sync_cookies()
```

---

## Archivos SEGUROS (NO TOCAR)

```
✅ login_runner.py              (LOGIN manual)
✅ profile_manager_v2.py        (Clone + .login_ok guard)
✅ runtime/backend_vtex.py      (ATC backend exacto)
✅ runtime/process_states.py    (11 estados)
✅ runtime/multiprocessing_runner.py (10-step flow)
✅ runtime/state_bus.py         (Queue messaging)
✅ ui/play_launcher.py          (SKU input bridge)
✅ ui/state_listener.py         (Background read-only)
✅ ui/app_v0_9_simple.py        (2-button UI)
```

---

## Proceso de limpieza (ORDEN IMPORTANTE)

1. **Paso 1**: Borrar directorios completos
   ```bash
   rm -rf runner/ controller/ manager/ worker/ engines/ vtex/
   ```

2. **Paso 2**: Buscar y borrar funciones prohibidas
   ```bash
   grep -r "page.click.*cart" . --include="*.py"
   # → BORRAR esas líneas
   
   grep -r "seed_golden" . --include="*.py"
   # → BORRAR funciones completas
   ```

3. **Paso 3**: Revisar archivos críticos
   - Abrir `runtime/backend_vtex.py` → Verificar que SOLO tiene atc_backend() y price_check()
   - Abrir `runtime/multiprocessing_runner.py` → Verificar que SOLO tiene 10 pasos lineales

4. **Paso 4**: Syntax check
   ```bash
   python -m py_compile runtime/*.py
   ```

5. **Paso 5**: Validación
   - Ejecutar: `python login_runner.py cuenta1`
   - Debería abrir Chrome, esperar login, crear .login_ok
   - ✅ Si funciona → Limpieza OK

---

## Validation checklist

Después de limpiar, verifica:

```python
✅ No hay "page.click" en el repo
✅ No hay "seed" en el repo
✅ No hay "monitor" en el repo
✅ No hay "watcher" en el repo
✅ No hay directorios runner/, controller/, etc
✅ backend_vtex.py tiene SOLO 2 funciones
✅ multiprocessing_runner.py tiene SOLO 1 función principal
✅ No hay mientras_true con browser/page dentro
✅ No hay MODE_A/MODE_B/etc
✅ No hay fallback lógica
```

---

## TL;DR

**Tres cosas que MATAN el bot:**

1. **ATC en browser** → Playwrig vuelto loco
2. **Session seed** → Interferencia de cookies
3. **Retries después de ATC OK** → Competencia con usuario

Si dejas cualquiera de estas, PIERDES en drops.

**Limpia hasta la verdad.**
