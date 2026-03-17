# 🔥 INYECCIÓN FRANKENSTEIN - REFERENCIA TÉCNICA

## ¿Cómo funciona exactamente?

### 1. Chrome Remote Debugging Protocol (CDP)

Chrome expone un **protocolo de depuración** diseñado para herramientas de desarrollo:

```
User: Yo quiero debuggear mi página web
Chrome: Perfecto, abre un WebSocket en http://127.0.0.1:9222/json
User: OK, déjame ver qué pestañas tienes...
Chrome: Claro, aquí están todas
User: OK, quiero ejecutar código JavaScript en la pestaña 1
Chrome: Adelante, envíame el comando CDP
```

### 2. Los 3 Comandos CDP que Usamos

#### Comando 1: `GET /json`
Obtiene lista de pestañas abiertas en el Chrome.

**Ejemplo:**
```bash
curl http://127.0.0.1:9222/json
```

**Respuesta:**
```json
[
  {
    "description": "",
    "devtoolsFrontendUrl": "...",
    "id": "69a5918e...",
    "title": "",
    "type": "page",
    "url": "about:blank",
    "webSocketDebuggerUrl": "ws://127.0.0.1:9222/devtools/browser/69a5918e..."
  }
]
```

**Qué hace:** Nos da la lista de pestañas y, MÁS IMPORTANTE, el URL del WebSocket para conectarnos.

---

#### Comando 2: `Page.navigate` (vía WebSocket)
Navega a una URL DIRECTO en el motor de Chrome (sin simular clicks).

**Protocolo:**
1. Conectarse al `webSocketDebuggerUrl` de la respuesta anterior
2. Enviar JSON:
```json
{
  "id": 1,
  "method": "Page.navigate",
  "params": {"url": "https://www.nike.cl/nstrike/checkout/..."}
}
```

3. Chrome INSTANTÁNEAMENTE cambia la URL

**Por qué es rápido:**
- No simula escribir en la barra de direcciones (Playwright sí lo hace)
- No espera a que el usuario cierre el teclado virtual
- Es un comando DIRECTO al motor del navegador

---

#### Comando 3: `Page.bringToFront` (vía WebSocket)
Trae la ventana al frente del SO.

**Protocolo:**
```json
{
  "id": 2,
  "method": "Page.bringToFront"
}
```

**Resultado:** Chrome pasa de background a foreground (visible al usuario).

---

### 3. Timeline de la Inyección Frankenstein

```
T-600 seg:  Ejecutas spawn_zombie_chrome(puerto=9222)
            ↓
            Chrome se abre en about:blank
            ↓
            Chrome escucha en http://127.0.0.1:9222

T-300 seg:  Usuario navega por Chrome manualmente
            ↓
            (o verificas que .login_ok existe en el perfil)

T-10 seg:   Ejecutas get_zombie_status(9222)
            ↓
            Chrome responde con su lista de pestañas
            ↓
            ✅ Listo para inyectar

T-0 seg:    Ejecutas teleport_chrome(9222, magic_link)
            ↓
            requests.get("http://127.0.0.1:9222/json")
            ↓
            websocket.create_connection(webSocketUrl)
            ↓
            ws.send(Page.navigate command)
            ↓
            Chrome empieza a cargar magic_link
            ↓
            INSTANTÁNEO ⚡

T+1 seg:    Chrome está cargando el checkout
            Usuario ve la página cargando
            🚀
```

---

## Ventajas Técnicas

### 1. **Velocidad Extrema**
```
Método          | Tiempo
----------------|--------
Playwright      | 1-2 segundos (abrir browser, ir a URL, esperar página)
Frankenstein    | 0.01 segundos (solo latencia de red)
Humano manual   | 2-5 segundos (clickear, escribir, enter)
Headless bot    | 1-2 segundos (sin display, más lento)
```

### 2. **Navegador REAL**
- Usa Chrome nativo
- Lleva cookies cargadas
- Tiene contexto de la sesión del usuario
- Antidetección: Es un Chrome legítimo

### 3. **Sin Overhead de Playwright**
```
Playwright flow:
1. Lanzar browser
2. Crear contexto persistente
3. Abrir página
4. Ir a URL
5. Esperar red
6. Esperar página

Frankenstein flow:
1. Conectar WebSocket (ya existe)
2. Enviar comando CDP
3. ✅ Done
```

### 4. **Sincronización Ultra-Precisa**
Múltiples Zombies pueden ser inyectados al mismo milisegundo:

```python
# Todos los threads lanzan esto SIMULTÁNEAMENTE
teleport_chrome(9222, link1)
teleport_chrome(9223, link2)
teleport_chrome(9224, link3)
# → 3 Chromes cargando al mismo tiempo (0ms delay)
```

---

## Protección Anti-WAF

### ¿Por qué no la detectan?

1. **Es un Chrome real**
   - No hay headless
   - Tiene interfaz gráfica
   - No hay WebDriver (Playwright usa Playwright protocol)

2. **La URL se cambia como lo haría un humano**
   - Clicks y input simula acciones
   - CDP Page.navigate es lo que hace un "refresh" manual
   - No hay comportamiento sospechoso

3. **La conexión CDP es LOCAL**
   ```
   Nike WAF: ¿Quién está visitando?
   Chrome: Soy chrome.exe en localhost (PID 4892)
   Nike: ✅ OK, usuario legítimo
   ```

4. **Cookies y sesión ya están cargadas**
   - No hay login suspechoso
   - No hay bot pattern recognition
   - Ya lleva 1 hora de "navegación"

### Comparación con herramientas bloqueadas

```
Playwright headless:
- Nike: "Hmm, headless=true? 🚫 BAN"

Selenium:
- Nike: "WebDriver string en HTTP headers? 🚫 BAN"

TLS Client (sin browser):
- Nike: "No hay User-Agent de Chrome real? 🚫 BAN"

Frankenstein:
- Nike: "Chrome de verdad, cookies válidas, 1 hora open? ✅ OK"
```

---

## Limitaciones Técnicas

### 1. **Chrome debe estar ya abierto**
```
✅ Works:
   1. spawn_zombie() (abre Chrome)
   2. Espera 5 seg
   3. teleport_chrome() (inyecta)

❌ Fails:
   1. teleport_chrome() sin spawn primero
   → Puerto 9222 no existe
```

### 2. **Latencia de red es el bottleneck**
```
Tiempo total = WebSocket connect (5ms) + Page.navigate (5ms) = ~10ms

En redes lentas (300ms ping):
   = WebSocket (300ms) + Chrome rendering (500ms) = ~800ms

En datacenter (0.1ms ping):
   = ~100ms total ⚡⚡⚡
```

### 3. **Una pestaña por Chrome**
```
❌ No puedes:
   Chrome 1 puerto 9222 → 3 pestañas en paralelo

✅ Puedes:
   Chrome 1 puerto 9222 → 1 pestaña
   Chrome 2 puerto 9223 → 1 pestaña
   Chrome 3 puerto 9224 → 1 pestaña
```

---

## Comandos CDP Disponibles (Referencia)

Si quieres experimentar más allá de Page.navigate y Page.bringToFront:

```python
# Simular clicks
ws.send(json.dumps({
    "id": 3,
    "method": "Input.dispatchMouseEvent",
    "params": {
        "type": "mousePressed",
        "x": 100,
        "y": 200,
        "button": "left"
    }
}))

# Ejecutar JavaScript
ws.send(json.dumps({
    "id": 4,
    "method": "Runtime.evaluate",
    "params": {"expression": "document.title"}
}))

# Captura de pantalla
ws.send(json.dumps({
    "id": 5,
    "method": "Page.captureScreenshot"
}))

# Leer console logs
ws.send(json.dumps({
    "id": 6,
    "method": "Runtime.startListening"
}))
```

---

## Arquitectura Detallada

### Topología de Red
```
┌─────────────────────────────────────────┐
│  Tu PC / Bot Server                     │
├─────────────────────────────────────────┤
│                                         │
│  Python (bot_controller.py)             │
│  ↓                                      │
│  websocket-client library               │
│  ↓                                      │
│  ws://127.0.0.1:9222/devtools/...       │ ← Conexión LOCAL
│  ↓                                      │
│  Chrome Process (chrome.exe)            │
│  ├─ PID 4892                           │
│  ├─ --remote-debugging-port=9222       │
│  └─ --user-data-dir=auth/cuenta2       │
│     ├─ Cookies (Nike sesión)            │
│     ├─ Cache                            │
│     └─ Local Storage                    │
│                                         │
└─────────────────────────────────────────┘
         ↓ (cuando inyectas)
    ┌──────────────────────────────┐
    │ NIKE.CL                      │
    ├──────────────────────────────┤
    │                              │
    │ WAF checks:                  │
    │ ✅ Real Chrome               │
    │ ✅ Cookies válidas           │
    │ ✅ Hace 1 hora está abierto  │
    │ ✅ Comportamiento normal     │
    │                              │
    │ → PERMITIDO ✅              │
    │                              │
    │ Checkout se carga...         │
    │                              │
    └──────────────────────────────┘
```

### Capas de Comunicación
```
Capa 1 (HTTP): GET /json
   - Simple HTTP request
   - Devuelve JSON de pestañas

Capa 2 (WebSocket): Page.navigate
   - Conexión persistente
   - Protocolo CDP (Chrome DevTools Protocol)
   - Comandos binarios/JSON

Capa 3 (Chrome IPC): Ejecución
   - Chrome recibe comando
   - Motor de renderizado procesa
   - Resultado visible
```

---

## Debugging

### Ver qué está enviando Python
```python
import json
command = {
    "id": 1,
    "method": "Page.navigate",
    "params": {"url": "https://nike.cl/..."}
}
print("Enviando:", json.dumps(command, indent=2))
ws.send(json.dumps(command))
```

### Capturar respuestas CDP
```python
response = ws.recv()
response_obj = json.loads(response)
print("Respuesta de Chrome:", json.dumps(response_obj, indent=2))

if "error" in response_obj:
    print(f"❌ Error: {response_obj['error']}")
```

### Monitorear en Chrome DevTools
1. Abre Chrome con `--remote-debugging-port=9222`
2. Ve a `chrome://inspect`
3. Haz click en "inspect" en la pestaña
4. Abre DevTools
5. En la consola, verás los comandos CDP siendo ejecutados

---

## Casos de Uso Avanzados

### 1. **Multi-account Synchronization**
```python
import time

accounts = [
    (9222, "link1"),
    (9223, "link2"),
    (9224, "link3"),
]

# Todos inyectan al MISMO timestamp
drop_time = time.time() + 5  # En 5 segundos

for port, link in accounts:
    while time.time() < drop_time:
        pass  # Spin wait
    
    teleport_chrome(port, link)
    # ↓ Todos llegan a Nike en < 1ms de diferencia
```

### 2. **Fallback si el primero falla**
```python
for attempt in range(3):
    success = teleport_chrome(9222, magic_link)
    if success:
        break
    time.sleep(0.5)
```

### 3. **Logging centralizado**
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("frankenstein")

def teleport_logged(port, link):
    logger.info(f"[{port}] Iniciando inyección")
    # ...
    logger.info(f"[{port}] ✅ Inyección exitosa")
```

---

## Resumen Técnico

| Aspecto | Detalle |
|--------|--------|
| **Protocolo** | Chrome Remote Debugging Protocol (CDP) |
| **Conexión** | WebSocket localhost |
| **Velocidad** | 0.01s (+ latencia red) |
| **Autenticación** | None (es local) |
| **Detección** | Muy difícil (es un Chrome real) |
| **Sincronización** | Hasta milisegundos |
| **Escalabilidad** | N cuentas = N puertos (9222+) |
| **Dependencias** | websocket-client, requests |

---

## Referencias

- [Chrome DevTools Protocol Docs](https://chromedevtools.github.io/devtools-protocol/)
- [Playwright Source Code](https://github.com/microsoft/playwright/blob/main/packages/playwright-core/src/server/browser.ts) (para ver cómo ellos usan CDP)
- [WebSocket RFC 6455](https://tools.ietf.org/html/rfc6455)

**🚀 Domina el protocolo, domina el drop.**
