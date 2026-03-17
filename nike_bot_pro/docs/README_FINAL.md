# 🏃 NIKE BOT PRO - VERSIÓN 0.9 FINAL

**Status**: ✅ LISTO PARA USAR

## TL;DR

**3 archivos, 2 botones, 10 pasos, 1 camino.**

```bash
# Setup (1 vez)
python login_runner.py cuenta1         # Manual login
python profile_cleanup.py cuenta1      # Reset (si es necesario)

# Drop day
python ui/app_v0_9_simple.py          # Abrir UI
# Click: PLAY
# Esperar magic link en browser
# User completa checkout
```

---

## Verdad del sistema

**No es una joya de código. Es un camino ganador congelado.**

- ✅ ATC backend: GET `/checkout/cart/add?sku=...&qty=1&seller=1&sc=1`
- ✅ Magic link: MISMO endpoint
- ✅ FREEZE: `session.close()` después de ATC
- ✅ No hay loops, no hay variantes, no hay iteración

**Eso es todo lo que necesitas.**

---

## Flujo exacto (10 pasos)

```
1. LOGIN           → Chrome manual, user loguea en Nike.cl
2. CLONAR          → profile_run clonado de profile_login
3. PREFLIGHT       → Headless verify que Nike reconoce sesión
4. ATC BACKEND     → GET /checkout/cart/add (1 intento)
5. PRICE CHECK     → Validar price > 0
6. FREEZE          → session.close(), backend DEAD
7. HANDOVER        → Abrir magic link en browser
8. WAITING_HUMAN   → Esperar a user
9. CHECKOUT        → User completa pago
10. DONE           → Fin
```

**Tiempo**: 15 segundos hasta magic link.

---

## Archivos principales

| Archivo | Función |
|---------|---------|
| `login_runner.py` | Chrome subprocess, manual login |
| `profile_manager_v2.py` | Master/Slave profile separation |
| `runtime/backend_vtex.py` | ATC backend exacto |
| `runtime/multiprocessing_runner.py` | 10-step orchestration |
| `ui/app_v0_9_simple.py` | 2-button UI (LOGIN \| PLAY) |

---

## Quick start

### Paso 1: Setup

```bash
# Crear profile login (primera vez)
python login_runner.py cuenta1

# Esperar a que la ventana Chrome se abra
# User loguea en Nike.cl
# Cerrar la ventana cuando termines
# Script crea .login_ok automáticamente
```

### Paso 2: Drop day

```bash
# Abrir UI
python ui/app_v0_9_simple.py

# En la UI:
# 1. Seleccionar cuenta (ej: "cuenta1")
# 2. Ingresar SKU (ej: "123456789")
# 3. Click "PLAY"
# 4. Esperar a que aparezca magic link en browser
# 5. Completar checkout manualmente
```

### Paso 3: Debug (si hay problemas)

```bash
# Limpiar cache del profile
python profile_cleanup.py cuenta1

# Diagnosticar login
python diagnose_login_issue.py cuenta1
# - Normal Chrome test
# - Incógnito test
# - Interpretación automática
```

---

## Verdades importantes

### ✅ Lo que funciona

- Chrome real login (no Playwright)
- ATC backend exacto
- Magic link = mismo endpoint que ATC
- Profile cloning con integridad
- State machine determinístico

### ❌ Lo que NO funciona

- Retries en loop (diseño)
- Session seed (diseño)
- Pricing monitors (diseño)
- Multiple ATC paths (diseño)

Estas cosas NO funcionan porque **no están diseñadas para funcionar**. El sistema es 1 camino, no múltiples variantes.

---

## Requisitos

```
Python 3.8+
requests
playwright
selenium
chromium (para Playwright)
Chrome real (para login)
```

---

## Indicadores de éxito

✅ `.login_ok` existe después de LOGIN
✅ Todos los 10 pasos aparecen en logs
✅ Magic link se abre automáticamente en browser
✅ State log muestra transiciones correctas

---

## Documentación extendida

**Si quieres entender el sistema en profundidad:**

- `VERDAD_FINAL_SISTEMA.md` - Auditoría honesta completa
- `ATC_EXACTO_LA_VERDAD.md` - Endpoint exacto explicado
- `FREEZE_QUE_SIGNIFICA.md` - FREEZE explicado
- `V0_9_FROZEN_EXECUTION_PLAN.md` - Plan completo

---

## Responsabilidad

**Este bot:**
- ✅ Agrega al carrito (backend)
- ✅ Abre el magic link (browser)

**El usuario:**
- ✅ Completa el pago
- ✅ Toma decisiones en checkout

**Nike:**
- ✅ Acepta o rechaza la compra

---

## Última verdad

> "El sistema no necesitaba ser reescrito. Necesitaba ser CREÍDO."

Tenía TODO lo que hace ganar drops. Solo necesitaba **disciplina** para dejar el camino ganador quieto.

Ahora está quieto.

Ahora gana.

---

**Fecha**: Ahora
**Status**: CONGELADO
**Última revisión**: NUNCA

¡Buena suerte! 🚀
