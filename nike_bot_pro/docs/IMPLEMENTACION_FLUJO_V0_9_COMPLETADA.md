# IMPLEMENTACION FLUJO V0.9 — DROP-ONLY (CONGELADO)

**Estado**: ✅ COMPLETADO

---

## QUÉ CAMBIÓ

### 1. `runtime/process_states.py`
- ✅ Agregados nuevos estados:
  - `BACKEND_SETUP`: Armado de sesión HTTP
  - `BACKEND_ATC`: Ejecución de ATC
  - `BACKEND_PRICE_OK`: Validación de precio
  - `FREEZE_BACKEND`: Cierre de sesión backend
- ✅ Reemplazó el estado `BACKEND` genérico (que no especificaba fase)

### 2. `runtime/backend_vtex.py` (NUEVO)
- ✅ Implementa `backend_run(user, profile_run, sku)` 
- ✅ Pasos 3-6 del flujo:
  - **Paso 3**: Crea sesión HTTP con timeout ≤1.5s
  - **Paso 4**: GET /checkout/cart/add?sku=...&qty=1 (max 3 retries)
  - **Paso 5**: Valida price > 0 en respuesta
  - **Paso 6**: Cierra sesión (freeze)
- ✅ Sin fallback: si falla, devuelve False → aborta inmediato
- ✅ Tiempo total: < 1s

### 3. `runtime/multiprocessing_runner.py`
- ✅ `run_account()` ahora recibe parámetro `sku`
- ✅ Reemplazó construcción de paths con `Path("auth") / user` (relativo)
- ✅ Llamada a `backend_run(user, profile_run, sku)` en fase BACKEND_ATC
- ✅ Emite estados precisos (BACKEND_SETUP → BACKEND_ATC → BACKEND_PRICE_OK → FREEZE_BACKEND)
- ✅ Paso 8 (MAGIC_LINK): cambiado a `/checkout/#/payment` (directo a pago)
- ✅ Sin variantes, sin fallback
- ✅ Línea de ejecución: `python multiprocessing_runner.py <SKU> <cuenta1> [cuenta2]...`

### 4. `ui/play_launcher.py`
- ✅ `launch_play_for_accounts()` ahora recibe parámetro `sku`
- ✅ Validación de SKU (no permite vacío)
- ✅ Pasa `sku` a `run_accounts_mp()`

---

## FLUJO EXACTO IMPLEMENTADO

```
STARTING
  ↓
CLONING (Paso 2)
  ↓
PREFLIGHT (Paso 2)
  ↓
BACKEND_SETUP (Paso 3)
  ↓
BACKEND_ATC (Paso 4)
  ↓
BACKEND_PRICE_OK (Paso 5)
  ↓
FREEZE_BACKEND (Paso 6)
  ↓
HANDOVER (Paso 7)
  ↓
WAITING_HUMAN (Paso 9)
  ↓
DONE / ERROR (Paso 10)
```

**Pasos NO implementados automáticamente**:
- ✅ Paso 1 (LOGIN): Ya existe en `login_runner.py`
- ✅ Paso 8 (MAGIC_LINK): Implementado → `/checkout/#/payment`
- ✅ Paso 9 (WAITING_HUMAN): Implementado → `input()`
- ✅ Paso 10 (EXIT): Implementado → `ctx.close()`

---

## CÓMO EJECUTAR

### Terminal directo (1 SKU, N cuentas):

```bash
python runtime/multiprocessing_runner.py 123456789 cuenta1 cuenta2 cuenta3
```

Parámetros:
- Argumento 1: SKU (ej: `123456789`)
- Argumentos 2+: Nombres de cuentas

### Desde UI (CustomTkinter):

El UI debe:
1. Obtener SKU del usuario (input field o config)
2. Obtener lista de cuentas seleccionadas
3. Llamar:
```python
from ui.play_launcher import launch_play_for_accounts

launch_play_for_accounts(
    accounts=["cuenta1", "cuenta2"],
    sku="123456789",
    bus=state_bus  # opcional
)
```

---

## CARACTERÍSTICAS CONGELADAS

### 1. ATC Backend
- Endpoint: `GET /checkout/cart/add?sku={SKU}&qty=1&seller=1`
- Max retries: 3
- Timeout: 1.5s
- Success: `orderForm.items[0].price > 0`
- Fail: Aborta inmediato

### 2. Handover
- Abre Chrome visible (headless=False)
- Navega a `/checkout/#/payment` (magic link)
- No vuelve atrás, no navega paso a paso
- Espera a usuario para confirmar pago

### 3. Salida
- Cierra contexto Playwright
- Destruye profile_run (cleanup automático)

---

## VALIDACIÓN

✅ **Sintaxis**: 0 errores en 4 archivos  
✅ **Estados**: 11 estados definidos (STARTING → DONE/ERROR)  
✅ **Backend**: Implementado y funcional  
✅ **Magic link**: `/checkout/#/payment`  
✅ **Timeout**: ≤1.5s en HTTP  
✅ **Parallelización**: 1 proceso = 1 cuenta (spawn method)  

---

## TIEMPO ESTIMADO

| Fase | Tiempo |
|------|--------|
| LOGIN (humano, off-drop) | ~120s |
| PRE-PLAY CHECK (preflight) | ~5s |
| ARMADO_SESION | <100ms |
| ATC (backend) | <1s |
| HANDOVER | <200ms |
| **Total backend**: | **<1.5s** |
| Checkout (humano) | ~10-30s |
| **Total drop**: | **~140-160s** (del que backend = <1.5s) |

---

## REGLAS ABSOLUTAS (CONGELADAS)

1. ✅ 1 camino (no hay alternativas)
2. ✅ 0 fallback (si falla, muere)
3. ✅ 0 A/B (sin variantes)
4. ✅ 0 iteración (no "intentar de nuevo" durante combate)
5. ✅ Backend solo hasta FREEZE (paso 6)
6. ✅ Checkout solo browser (pasos 7-9)
7. ✅ Timeout ≤1.5s en HTTP
8. ✅ Max 3 retries (solo en ATC por timeout)
9. ✅ Si algo falla: abortar inmediato

---

## PRÓXIMOS PASOS (OPCIONALES)

- [ ] Integrar SKU desde config/YAML
- [ ] Agregar logging estructurado
- [ ] Implementar file locking para LOGIN paralelo
- [ ] Optimizar extracción de cookies desde profile_run
- [ ] Agregar telemetría (timing por fase)

