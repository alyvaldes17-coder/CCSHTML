# 🔴 DIAGNÓSTICO: Por qué se bloquea en "2️⃣ Abriendo navegador"

## 🎯 El Problema

El bot llega a imprimir:
```
[cuenta2] 2️⃣ Abriendo navegador...
```

Y **se queda esperando indefinidamente** sin avanzar.

No hay error. No hay crash. No hay excepción.

Está **bloqueado silenciosamente** esperando algo.

---

## 🔍 Los 3 Lugares Posibles de Bloqueo

### 🔴 LUGAR A: launch_persistent_context colgado

```python
[DEBUG] 2.1 Iniciando Chromium...
# ↓ AQUÍ SE QUEDA SI ES ESTE CASO
```

**Síntomas:**
- Chrome no se abre (pero sin error)
- El contexto Playwright no se completa
- Suele pasar si:
  - El perfil ya estaba abierto (aunque sin zombie visible)
  - Hay un lock file corrupto que no se borró

---

### 🔴 LUGAR B: page.goto() nunca retorna

```python
[DEBUG] 2.2 Context creado, obteniendo página...
# ↓ AQUÍ SE QUEDA SI ES ESTE CASO (goto Nike)
page.goto("https://www.nike.cl", timeout=30000)
```

**Síntomas:**
- Chrome se abre
- Pero page.goto("https://www.nike.cl") nunca retorna
- Nike puede:
  - Redirigir a fila de espera
  - Quedar cargando eternamente
  - Bloquear por JS hydration lento
  - Devolver error 429/blocked

---

### 🔴 LUGAR C: wait_for_* sin timeout

```python
page.wait_for_selector("text=Finalizar", timeout=None)  # ❌ MORTAL
page.wait_for_function("..." )  # sin timeout ❌
```

**Síntomas:**
- Si el selector nunca aparece → espera eternamente

---

## 🛠️ Cómo Identificarlo (que ya hicimos)

Hemos añadido prints de DEBUG:

```python
dprint("   [DEBUG] 2.1 Iniciando Chromium...")
browser = p.chromium.launch_persistent_context(...)

dprint("   [DEBUG] 2.2 Context creado, obteniendo página...")
page = browser.pages[0] if browser.pages else browser.new_page()

dprint("   [DEBUG] SESSION_SEED 1: Navegando a Nike...")
page.goto("https://www.nike.cl", timeout=30000)

dprint("   [DEBUG] SESSION_SEED 2: Nike cargado")
```

**El último print que veas = donde está bloqueado**

---

## ✅ Cambios Hechos

### 1. Contradicción de Cookies (CORREGIDA)

**Antes:**
```
✅ Cookies encontradas en profile_pw
ℹ️ Sin cookies locales (usuario puede estar logueando)
```
❌ Contradictorio

**Ahora:**
```
✅ Cookies cargadas y válidas (profile_pw)
```
o
```
ℹ️ Sin cookies válidas (pero continuando - confianza ciega)
```
✅ Consistente

### 2. Timeouts Añadidos

```python
# ANTES (mortal):
page.goto("https://www.nike.cl", wait_until="networkidle", timeout=15000)

# AHORA (seguro):
page.goto("https://www.nike.cl", timeout=30000)  # Sin wait_until "networkidle"
```

**Por qué:**
- `wait_until="networkidle"` espera a que TODOS los requests terminen
- Si Nike tiene fondo de pantalla que carga lentamente → espera eternamente
- `timeout=30000` = máximo 30 segundos, luego falla

### 3. Try/Except en Transiciones

```python
try:
    page.goto("https://www.nike.cl", timeout=30000)
except Exception as goto_error:
    self.log.error(f"Nike navigation failed: {goto_error}")
    self.state = BotState.PAYMENT_FAILED
    return
```

**Resultado:**
- Si goto falla → se marca PAYMENT_FAILED
- No se queda esperando
- El bot continúa y termina

### 4. Debug Points en worker.py

```python
dprint("   [DEBUG] 2.1 Iniciando Chromium...")
dprint("   [DEBUG] 2.2 Context creado, obteniendo página...")
dprint("   ✅ Navegador abierto")
```

---

## 🧪 Cómo Probar Ahora

```bash
python main.py
```

Mira los prints:
```
[cuenta2] 2️⃣ Abriendo navegador...
[cuenta2]    [DEBUG] 2.1 Iniciando Chromium...
[cuenta2]    [DEBUG] 2.2 Context creado, obteniendo página...
[cuenta2]    ✅ Navegador abierto
[cuenta2]    [DEBUG] SESSION_SEED 1: Navegando a Nike...
[cuenta2]    [DEBUG] SESSION_SEED 2: Nike cargado
[cuenta2]    [DEBUG] SESSION_SEED 3: Extrayendo cookies...
```

- Si se queda en **2.1** → Chromium colgado
- Si se queda en **SESSION_SEED 1** → Nike goto colgado
- Si continúa → ¡ÉXITO!

---

## 📋 Próximos Pasos

1. Ejecuta `python main.py`
2. Copia el último print que ves antes del bloqueo
3. Si llega a "Nike cargado" pero no avanza más → buscar next bottleneck
4. Si avanza completamente → ¡EL BOT FUNCIONA! 🎉

