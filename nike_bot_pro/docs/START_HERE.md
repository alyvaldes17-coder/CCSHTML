# 🚀 EMPIEZA AQUÍ - NIKE BOT PRO v0.9

**Lee esto primero. Luego ejecuta.**

---

## ¿Qué es esto?

Bot para Nike drops.

- **INPUT**: User loguea manualmente
- **PROCESS**: Bot agrega al carrito (backend)
- **OUTPUT**: Chrome abre, user completa pago

**Duración**: 15 segundos hasta magic link.

---

## Setup inicial (5 minutos)

### 1. Loguear en Nike

```bash
python login_runner.py cuenta1
```

Espera a que se abra Chrome. Loguea en Nike.cl. Cierra la ventana.

✅ Script crea `.login_ok`

### 2. Listo

Eso es TODO lo que necesitas para setup.

---

## Drop day (2 minutos)

### 1. Abrir UI

```bash
python ui/app_v0_9_simple.py
```

### 2. Ingresar datos

- Cuenta: `cuenta1`
- SKU: `123456789` (el del drop)
- Click: `PLAY`

### 3. Observar

Logs en tiempo real. Chrome se abre. Item está en carrito.

### 4. User completa checkout

Tú completas el pago manualmente en Chrome.

**FIN.**

---

## Documentación (RECOMENDADO leer)

| Documento | Tiempo | Leer si... |
|-----------|--------|-----------|
| [RESUMEN_EJECUTIVO_FINAL.md](RESUMEN_EJECUTIVO_FINAL.md) | 3 min | Necesitas visión general |
| [CHECKLIST_EJECUCION_FINAL.md](CHECKLIST_EJECUCION_FINAL.md) | 10 min | Vas a ejecutar ahora |
| [INDICE_DOCUMENTACION_FINAL.md](INDICE_DOCUMENTACION_FINAL.md) | 5 min | Quieres saber todo |

**Lectura mínima**: RESUMEN + CHECKLIST = 13 minutos

---

## ¿Qué hace exactamente el bot?

```
1. LOGIN (manual, off-drop)
   └→ User loguea en Nike

2. CLONE
   └→ Bot copia el profile

3. PREFLIGHT
   └→ Bot verifica sesión

4. PRICE LOOP
   └→ Bot espera a que precio > 0

5. ATC
   └→ Bot agrega al carrito (GET request)

6. FREEZE
   └→ Bot cierra todo

7. HANDOVER
   └→ Bot abre Chrome

8. MAGIC LINK
   └→ Item ya está en carrito

9. USER CHECKOUT
   └→ User completa pago

10. DONE
```

**Duración bot**: ~15 segundos (pasos 1-8)

**Duración user**: Variable (pasos 9-10)

---

## ¿Por qué funciona?

1. **Simple**: 1 camino, 0 variantes
2. **Rápido**: 15 segundos hasta magic link
3. **Consistente**: Sin retries innecesarios
4. **Congelado**: No interfiere con user

---

## ¿Cuál es el "secreto"?

```
GET https://www.nike.cl/checkout/cart/add?sku=SKU&qty=1&seller=1&sc=1
```

Eso es TODO.

- GET (no POST)
- /checkout/cart/add (no /payment)
- Exactos parámetros (qty=1, seller=1, sc=1)
- No hay variantes
- No hay alternativas

---

## ¿Qué pasa si falla?

```
❌ "Sesión inválida"     → python profile_cleanup.py cuenta1
❌ "ATC Status 400"      → Verificar SKU
❌ "Chrome no se abre"   → Instalar Chrome real
❌ Otra cosa             → Leer CHECKLIST_EJECUCION_FINAL.md
```

---

## Archivos importantes

**El bot necesita estos 9 archivos:**

```
login_runner.py ................. Login
profile_manager_v2.py ........... Clone
runtime/backend_vtex.py ......... ATC
runtime/process_states.py ....... Estados
runtime/multiprocessing_runner.py Orquestación
runtime/state_bus.py ............ Messaging
ui/play_launcher.py ............ Bridge
ui/state_listener.py ........... Listener
ui/app_v0_9_simple.py .......... UI
```

**Otros archivos son opcional:**

```
profile_cleanup.py .............. Debug
diagnose_login_issue.py ......... Debug
quick_test_threading_fix.py ..... Debug
```

---

## Validación rápida

```bash
# ¿El bot funciona?
python -m py_compile runtime/backend_vtex.py
python -m py_compile runtime/multiprocessing_runner.py
# Debe retornar sin errores

# ¿Los imports funcionan?
python -c "from runtime.backend_vtex import backend_run"
python -c "from runtime.multiprocessing_runner import run_account"
# Debe retornar sin errores

# ¿La UI abre?
python ui/app_v0_9_simple.py
# Click para cerrar: Ctrl+C
```

---

## ¿Qué no DEBE tener el bot?

```
❌ page.click("Add to cart")      ← ATC en browser
❌ copy_cookies()                 ← Session seed
❌ if atc_ok: verify_again()      ← Retries después de ATC
❌ while price == 0: browser()    ← Chrome en loop
❌ MODE_A / MODE_B                ← Múltiples caminos
❌ Fallback logic                 ← Plans B
```

Si ves alguna de estas: **BORRA**

---

## Responsabilidades

**Bot**:
- ✅ Agregar al carrito
- ✅ Abrir magic link

**User**:
- ✅ Seleccionar talle
- ✅ Ingresar dirección
- ✅ Completar pago

**Nike**:
- ✅ Procesar orden
- ✅ Confirmar compra

---

## Próximos pasos

### Ahora (10 min)

1. Ejecutar: `python login_runner.py cuenta1`
2. Loguear en Nike
3. Cerrar Chrome
4. ✅ `.login_ok` debe existir

### Próximo drop (cuando Nike libera)

1. Ejecutar: `python ui/app_v0_9_simple.py`
2. Ingresar cuenta + SKU
3. Click: PLAY
4. Esperar: 15 segundos
5. Chrome abre automáticamente
6. Completar checkout
7. ✅ COMPRADO

---

## Documentación completa

**Para entender el sistema en profundidad:**

- [INDICE_DOCUMENTACION_FINAL.md](INDICE_DOCUMENTACION_FINAL.md) — Índice completo
- [README.md](README.md) — Descripción general
- [PSEUDOCODIGO_FINAL.md](PSEUDOCODIGO_FINAL.md) — Código exacto
- [ATC_EXACTO_LA_VERDAD.md](ATC_EXACTO_LA_VERDAD.md) — Endpoint HTTP
- [CONCLUSION_FINAL.md](CONCLUSION_FINAL.md) — Resumen final

---

## Checklists

**Pre-drop** (leer antes de cada drop):
→ [CHECKLIST_EJECUCION_FINAL.md](CHECKLIST_EJECUCION_FINAL.md)

**Problemas comunes**:
→ [LOGIN_TROUBLESHOOTING_V0_9.md](LOGIN_TROUBLESHOOTING_V0_9.md)

---

## Verdad final

> "El bot no es complicado."
>
> "Es consistente."
>
> "1 camino. Congelado. Gana."

---

## Status

```
✅ Código: LISTO
✅ Documentación: COMPLETA
✅ Validación: PASADA
✅ Producción: READY
```

---

## Acción inmediata

1. **Setup**: `python login_runner.py cuenta1` (ahora)
2. **Wait**: Esperar drop Nike
3. **Execute**: `python ui/app_v0_9_simple.py` (drop day)
4. **Win**: Completar checkout

---

**Eso es TODO.**

El sistema está listo.

¿Preguntas?

→ [INDICE_DOCUMENTACION_FINAL.md](INDICE_DOCUMENTACION_FINAL.md)

---

🚀 **Buena suerte.**
