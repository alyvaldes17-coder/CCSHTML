# FREEZE - QUÉ SIGNIFICA REALMENTE

## Definition

**FREEZE = Detención ABSOLUTA de todo lo que no es el browser.**

Después de FREEZE, NADA más sucede en el backend.

---

## Lo que OCURRE en FREEZE

```python
# Paso 6: FREEZE_BACKEND

# 1. Cerrar sesión HTTP
session.close()

# 2. Detener todos los threads de backend
backend_thread.terminate()
request_loop.stop()
retry_worker.kill()

# 3. Deshabilitar timeouts, watchers, loggers
backend.disable()
metrics.stop()

# 4. Limpiar recursos
gc.collect()
```

**Resultado**: Backend está MUERTO.

---

## Lo que NO ocurre después de FREEZE

❌ No hay más GET requests
❌ No hay más retries
❌ No hay pricing monitors
❌ No hay watchers
❌ No hay loggers que escriban
❌ No hay threads activos
❌ No hay iteración

**Solo**: Browser abierto con magic link

---

## Por qué FREEZE es crítico

### Antes de FREEZE (Pasos 1-6)

```
Paso 1: LOGIN - User entra credenciales
Paso 2: CLONAR - profile_run listo
Paso 3: PREFLIGHT - Nike verifica sesión
Paso 4: ATC BACKEND - GET /checkout/cart/add
Paso 5: PRICE CHECK - Validar item en carrito
Paso 6: FREEZE - BACKEND MUERE
```

**Duración**: ~15 segundos

**Control**: Bot (determinístico, sin user input)

### Después de FREEZE (Pasos 7-10)

```
Paso 7: HANDOVER - Abrir magic link en browser
Paso 8: WAITING_HUMAN - Esperar a user
Paso 9: CHECKOUT - User completa pago
Paso 10: DONE - Fin
```

**Duración**: Variable (user depend)

**Control**: User (manual, decisiones humanas)

---

## Separación crítica: BEFORE/AFTER FREEZE

```
BEFORE FREEZE: Máquina en control
┌─────────────────────────────────┐
│ 1. LOGIN (Chrome manual)          │
│ 2. CLONAR (profile_run)           │
│ 3. PREFLIGHT (headless Nike)      │
│ 4. ATC BACKEND (GET request)      │
│ 5. PRICE CHECK (validar)          │
│ 6. FREEZE ← ← ← CORTE ABSOLUTO    │
└─────────────────────────────────┘
       ▼
   BACKEND DEAD
       ▼
   SOCKET CLOSED
       ▼
   THREADS KILLED
       ▼
   TIMEOUT = 0
       ▼

AFTER FREEZE: Usuario en control
┌─────────────────────────────────┐
│ 7. HANDOVER (magic link)          │
│ 8. WAITING_HUMAN (timeout ∞)      │
│ 9. CHECKOUT (user input)          │
│ 10. DONE                           │
└─────────────────────────────────┘
```

---

## Lo que NO es FREEZE

❌ **No es "pausa temporalmente"**
   - Es "detención permanente del backend"

❌ **No es "esperar un timeout"**
   - Es "eliminar todos los timeouts"

❌ **No es "dejar el thread dormido"**
   - Es "matar el thread definitivamente"

❌ **No es "desconectar la sesión"**
   - Es "destruir la sesión completa"

❌ **No es "saltar a step 7"**
   - Es "el cambio de responsabilidad de máquina a usuario"

---

## Implementación de FREEZE

```python
class BackendRunner:
    def run_account(self, user, sku, bus):
        """10-step frozen flow"""
        
        session = None
        browser = None
        
        try:
            # Pasos 1-5: Control del bot
            # (login, clone, preflight, atc, price check)
            
            # ─── FREEZE AQUÍ ───
            if session:
                session.close()  # HTTP muere
            
            if browser:
                browser.quit()   # Playwright muere
            
            # De aquí en adelante, SOLO browser del user existe
            
            # Paso 7: HANDOVER
            magic_link = f"https://www.nike.cl/checkout/cart/add?sku={sku}&qty=1&seller=1&sc=1"
            os.startfile(magic_link)  # Windows
            
            # Paso 8: WAITING_HUMAN
            # Esperar indefinidamente (no timeout)
            self.state = "WAITING_HUMAN"
            while True:
                time.sleep(60)  # Solo chequear cada minuto
                
        except Exception as e:
            self.state = "ERROR"
        finally:
            # Cleanup final (pero backend ya está muerto)
            if session:
                session.close()
```

---

## Timing exacto

### Pasos 1-6 (BEFORE FREEZE)

```
Paso 1: LOGIN (headless Chrome)           5s
Paso 2: CLONAR profile                    3s
Paso 3: PREFLIGHT (Nike verification)     4s
Paso 4: ATC BACKEND                       2s
Paso 5: PRICE CHECK                       0.5s
Paso 6: FREEZE                            0.5s
─────────────────────────────────────────
TOTAL: ~15 segundos (determinístico)
```

### Pasos 7-10 (AFTER FREEZE)

```
Paso 7: HANDOVER (abrir link)             1s
Paso 8: WAITING_HUMAN (esperar)          ∞ (indefinido)
Paso 9: CHECKOUT (user input)            ? (variable)
Paso 10: DONE                            (cuando user termina)
─────────────────────────────────────────
TOTAL: Variable (user-dependent)
```

---

## Señales de FREEZE correcto

✅ `session.close()` fue llamado
✅ `browser.quit()` fue llamado
✅ Ningún thread abierto (solo main + listener)
✅ No hay sockets activos
✅ No hay requests pendientes
✅ Log muestra "FREEZE_BACKEND: OK"

---

## Señales de FREEZE incorrecto

❌ Todavía hay requests en red
❌ Threads siguen ejecutando (retry_worker)
❌ Timeouts siguen activos
❌ Price monitors siguen buscando
❌ Watchers siguen iterando

**Si ves estas señales**: El bot seguirá interfiriendo. Eso MATA la compra.

---

## Por qué FREEZE elimina el "multiple paths" problem

**El problema**: Bot tenía múltiples formas de ATC
- ATC backend
- ATC browser
- Session seed
- Retry loops
- Price monitors

**El resultado**: No determinístico. A veces funcionaba, a veces no.

**La solución FREEZE**: Todo se detiene después de step 6.
- Backend ATC sucede 1 vez (step 4)
- Backend se cierra 1 vez (step 6)
- DONE. Browser abierto. Fin.

**Ahora**: 1 path, 0 variantes, 100% predecible.

---

## Conclusión

**FREEZE no es un feature, es el PUNTO DE TRANSICIÓN.**

Del mundo del bot (determinístico, máquina) al mundo del usuario (variable, humano).

Después de FREEZE:
- Bot no toca nada
- Usuario completa checkout
- No hay interferencia
- No hay competencia con otros bots

**Eso es lo que gana drops.**
