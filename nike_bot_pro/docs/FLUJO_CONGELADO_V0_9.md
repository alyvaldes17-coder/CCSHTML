# FLUJO V0.9 — DROP-ONLY (CONGELADO)

**Principio**: 1 camino, 0 fallback, 0 A/B, 0 iteración durante combate.

---

## PASO 1: LOGIN (HUMANO, OFF-DROP)

**Quién**: Usuario  
**Cuándo**: Antes del drop, cualquier hora  
**Cómo**:
- Abrir Chrome con `profile_login`
- Usuario inicia sesión
- Usuario agrega método de pago
- Usuario cierra Chrome

**Verificación**:
- Script verifica Nike reconoce sesión (GET /mi-cuenta headless)
- Crear archivo `.login_ok` en `auth/{user}/`

**Prohibido**:
- Backend
- ATC
- Cookie bridge
- Iteración

---

## PASO 2: PRE-PLAY CHECK (ANTES DEL DROP)

**Quién**: Script  
**Cuándo**: 5min antes de drop start  
**Cómo**:
- Verificar `.login_ok` existe
- Clonar `profile_login` → `profile_run`
- Abrir Chrome **headless** con `profile_run`
- GET /mi-cuenta → verificar Nike reconoce sesión
- Cerrar Chrome

**Resultado**: SI OK → continuar | SI FALLA → abortar

**Prohibido**:
- Segundo intento
- Fallback a otro profile
- Cache reuse

---

## PASO 3: ARMADO DE SESIÓN BACKEND

**Quién**: Script  
**Cuándo**: Drop start - 2s  
**Cómo**:
- Crear cliente HTTP limpio (`requests.Session()`)
- Extraer cookies mínimas de `profile_run` (si aplica)
- Timeout global ≤1.5s
- Sin headers complejos

**Prohibido**:
- Session seed desde browser
- Browser requests
- Watchers
- Retry loops

---

## PASO 4: ATC BACKEND (ÚNICO CAMINO)

**Quién**: Script  
**Cuándo**: Drop start  
**Cómo**:
```
GET /checkout/cart/add?sku=<SKU>&qty=1
```
- Máx 3 retries (si timeout)
- Éxito = `orderForm.items.length > 0`
- Timeout 1.5s por intento

**Si falla** → abortar, fin

**Prohibido**:
- Fallback a UI ATC
- Espera de pricing
- Watchers
- Segundo flujo

---

## PASO 5: PRICE CHECK

**Quién**: Script  
**Cuándo**: Inmediato después de PASO 4  
**Cómo**:
- Leer `orderForm.items[0].price`
- Verificar `price > 0`

**Si falla** → abortar, fin

**Prohibido**:
- Pricing wait
- Precio variable
- Backend después de esto

---

## PASO 6: FREEZE BACKEND

**Quién**: Script  
**Cuándo**: Después de PASO 5  
**Cómo**:
- Cerrar cliente HTTP
- Matar todos los threads backend
- No más requests

**Desde aquí**: El backend muere. Punto de no retorno.

---

## PASO 7: HANDOVER BROWSER (INMEDIATO)

**Quién**: Script  
**Cuándo**: Inmediatamente después de FREEZE  
**Cómo**:
- Abrir Chrome **visible** con `profile_run`
- Sin navegación paso a paso
- Sin esperas

**Tiempo total Paso 1-7**: ~1.5s

---

## PASO 8: MAGIC LINK

**Quién**: Script  
**Cuándo**: Cuando Chrome está visible  
**Cómo**:
```
page.goto("https://www.nike.cl/checkout/#/payment")
```
- O el endpoint real de checkout post-ATC

**Prohibido**:
- Volver a /home
- ATC desde browser
- Navegación adicional

---

## PASO 9: WAITING_HUMAN (TERMINAL)

**Quién**: Usuario  
**Cuándo**: Cuando ve Chrome en checkout  
**Cómo**:
- 1 click para confirmar
- 1 OTP si pide
- Pago se ejecuta

**Script hace**: Nada. Solo espera `input()`.

**Prohibido**:
- Interacción automática de pago
- Llenar OTP
- Confirmación sin usuario

---

## PASO 10: EXIT

**Quién**: Script  
**Cuándo**: Después de que usuario cierra Chrome  
**Cómo**:
- Cerrar contexto Playwright
- Destruir `profile_run`
- Reportar estado DONE

---

## MAPA DE ESTADOS

```
STARTING
  ↓ (Paso 1-2: verificación)
CLONING
  ↓ (Paso 3: armado HTTP)
BACKEND_SETUP
  ↓ (Paso 4: ATC)
BACKEND_ATC
  ↓ (Paso 5: price check)
BACKEND_PRICE_OK
  ↓ (Paso 6: freeze)
FREEZE_BACKEND
  ↓ (Paso 7-8: handover)
HANDOVER
  ↓ (Paso 9: espera humana)
WAITING_HUMAN
  ↓ (Paso 10: cleanup)
DONE / ERROR (aborto en cualquier falla)
```

---

## REGLAS ABSOLUTAS

1. **1 camino**: No hay alternativas
2. **0 fallback**: Si falla, muere
3. **0 A/B**: Sin variantes
4. **0 iteración**: Decisiones fijas, no "intentar de nuevo"
5. **Backend = Pasos 3-6**: Después de eso, muere
6. **Browser = Pasos 7-9**: Solo el humano decide
7. **Timeout ≤1.5s**: Global en HTTP
8. **Max 3 retries**: Solo en ATC por timeout
9. **Si algo falla**: Abortar inmediato, no esperar

---

## VALIDACIÓN DEL FLUJO

- ✅ ATC < 1s
- ✅ Handover inmediato
- ✅ Checkout humano preparado
- ✅ Drop-capable
- ✅ Sin iteración (muere rápido)
- ✅ Determinista (1 solo camino)
- ✅ Velocidad máxima (no esperas, no fallbacks)

---

## MAPA A CÓDIGO ACTUAL

| Paso | Función Actual | Estado |
|------|-----------------|--------|
| 1 | `login_runner.py` | ✅ Existe |
| 2 | `preflight()` + `clone_auth_to_run()` | ✅ Existe |
| 3-6 | `backend_run()` (TODO) | ❌ Falta implementar |
| 7-9 | `run_account()` handover | ⚠️ Parcial (sin magic link) |
| 10 | `ctx.close()` + cleanup | ✅ Existe |

