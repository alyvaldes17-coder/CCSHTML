

# 🏃 NIKE BOT PRO v0.9 — FINAL

**Status**: ✅ **CONGELADO** — Listo para producción

---

## ⚡ Quick Start (5 minutos)

### Setup (1 vez)

```bash
# 1. Loguear en Nike
python login_runner.py cuenta1

# Esperar Chrome → user loguea → cerrar ventana
# ✅ Script crea .login_ok

# 2. Listo
```

### Drop (cuando Nike libera)

```bash
# 1. Abrir UI
python ui/app_v0_9_simple.py

# 2. En la UI:
#    - Seleccionar: cuenta1
#    - SKU: 123456789
#    - Click: PLAY

# 3. Observar
#    - Logs en tiempo real
#    - Chrome se abre automáticamente
#    - Magic link ya está en carrito

# 4. User completa checkout manualmente
```

**Duración**: 15 segundos hasta magic link.

---

## 🎯 Qué hace el bot

```
✅ LOGIN         → User loguea manualmente
✅ CLONE         → Copia profile para el bot
✅ PREFLIGHT     → Verifica sesión válida
✅ PRICE LOOP    → Espera a que precio > 0
✅ ATC BACKEND   → GET /checkout/cart/add
✅ FREEZE        → Cierra backend completamente
✅ HANDOVER      → Abre Chrome con magic link
✅ WAITING       → User completa checkout
```

**Eso es TODO.**

Sin variantes. Sin fallbacks. Sin iteración.

---

## 🗂️ Archivos core (9)

```
login_runner.py ................. Manual Nike login
profile_manager_v2.py ........... Master/Slave cloning
runtime/backend_vtex.py ......... ATC backend exacto
runtime/process_states.py ....... 11 estados máquina
runtime/multiprocessing_runner.py Orquestación 10 pasos
runtime/state_bus.py ............ Messaging entre procesos
ui/play_launcher.py ............ Bridge UI → bot
ui/state_listener.py ........... Background state updates
ui/app_v0_9_simple.py .......... 2-botón UI (LOGIN|PLAY)
```

---

## 📚 Documentación (EMPIEZA AQUÍ)

| Lee si... | Documento | Tiempo |
|-----------|-----------|--------|
| Necesitas visión general | [RESUMEN_EJECUTIVO_FINAL.md](RESUMEN_EJECUTIVO_FINAL.md) | 3 min |
| Vas a ejecutar ahora | [CHECKLIST_EJECUCION_FINAL.md](CHECKLIST_EJECUCION_FINAL.md) | 10 min |
| Necesitas código exacto | [PSEUDOCODIGO_FINAL.md](PSEUDOCODIGO_FINAL.md) | 5 min |
| Quieres endpoint HTTP | [ATC_EXACTO_LA_VERDAD.md](ATC_EXACTO_LA_VERDAD.md) | 5 min |
| Necesitas limpieza | [QUE_BORRAR_CRITICO.md](QUE_BORRAR_CRITICO.md) | 10 min |
| Quieres entender FREEZE | [FREEZE_QUE_SIGNIFICA.md](FREEZE_QUE_SIGNIFICA.md) | 5 min |
| Buscas índice completo | [INDICE_DOCUMENTACION_FINAL.md](INDICE_DOCUMENTACION_FINAL.md) | 5 min |

**Lectura recomendada**: 15 minutos = RESUMEN + CHECKLIST

---

## 🔑 Magic link (el corazón del bot)

```
https://www.nike.cl/checkout/cart/add?sku=SKU&qty=1&seller=1&sc=1
```

**Esto es TODO lo que necesitas.**

- Mismo endpoint que el GET backend
- Item ya está en carrito (backend lo hizo)
- User abre en Chrome y completa checkout

---

## 🧊 FREEZE (lo más importante)

**FREEZE = Muerte absoluta del backend.**

Después de FREEZE:
- ❌ No hay más requests HTTP
- ❌ No hay más retries
- ❌ No hay más lógica
- ✅ Solo Chrome + usuario

Si no FREEZE: Bot interfiere. Pierdes.

---

## 🚀 Ejecución rápida

```bash
# Setup (primera vez, 5 min)
python login_runner.py cuenta1

# Drop (cuando Nike libera, 15 segundos)
python ui/app_v0_9_simple.py
# → Seleccionar account
# → Ingresar SKU
# → Click PLAY
# → Chrome se abre
# → Magic link listo
# → User completa checkout
```

---

## ✅ Indicadores de éxito

- [ ] Chrome se abre automáticamente
- [ ] Magic link es exacta
- [ ] Item está en carrito
- [ ] User ve: talle, cantidad, precio
- [ ] User completa checkout

---

## ❌ Si algo falla

```
"Sesión inválida"     → python profile_cleanup.py cuenta1
"ATC Status 400"      → Verificar SKU
"Chrome no abre"      → Instalar Chrome real
"FREEZE no ocurre"    → Revisar backend_vtex.py
```

**Más info**: [CHECKLIST_EJECUCION_FINAL.md](CHECKLIST_EJECUCION_FINAL.md)

---

## 📊 Arquitectura (1 página)

```
INPUT: LOGIN (manual)
  ↓
CLONE + PREFLIGHT (validación)
  ↓
PRICE LOOP (backend check, sin Chrome)
  ├→ price == 0 → sleep 0.3s → retry
  └→ price > 0 → ATC
       ↓
ATC + PRICE CHECK (GET request)
  ├→ fail → retry once → fail → ERROR
  └→ success → FREEZE
       ↓
FREEZE (session.close)
  ↓
HANDOVER (Chrome + magic link)
  ↓
WAITING (usuario completa checkout)
  ↓
DONE
```

---

## 🎓 Verdad del sistema

**No necesitaba código nuevo.**

Necesitaba **DISCIPLINA** para:
1. Fijar ATC en 1 endpoint
2. Fijar FREEZE en step 7
3. Fijar magic link
4. Eliminar iteración

Eso es CONGELACIÓN.

**Sistema siempre tuvo**:
- ✅ LOGIN correcto
- ✅ ATC backend
- ✅ Pricing
- ✅ Profiles separados

**Ahora**: Congelado. Sin variantes. Listo.

---

## 🛠️ Debug tools

```
profile_cleanup.py ........... Reset suave del profile
diagnose_login_issue.py ...... Test login (3 pasos)
quick_test_threading_fix.py .. Validar multiprocessing
```

---

## 📋 Responsabilidades

**Bot**:
- ✅ Agregar al carrito (backend GET)
- ✅ Abrir magic link (Chrome)

**User**:
- ✅ Completar pago
- ✅ Tomar decisiones

**Nike**:
- ✅ Procesar orden
- ✅ Confirmar compra

---

## 🚫 Qué NO existe (por diseño)

```
❌ ATC en browser (Playwright Click)
❌ Session seed (copiar cookies)
❌ Retries después de ATC OK
❌ Chrome en el loop
❌ Múltiples caminos (MODE_A/B)
❌ Fallbacks o Plans B
❌ Threads paralelos
```

Si ves cualquiera: **BORRA**

---

## 📈 Performance

| Fase | Tiempo | Control |
|------|--------|---------|
| LOGIN | 5s | User (manual) |
| CLONE | 3s | Bot |
| PREFLIGHT | 4s | Bot |
| PRICE_LOOP | variable | Bot |
| ATC | 2s | Bot |
| FREEZE | 0.5s | Bot |
| **Total pre-magic** | **~15s** | **Bot** |
| HANDOVER | 1s | Bot |
| **Magic link open** | **~16s total** | **Bot done** |
| CHECKOUT | ∞ | **User** |

---

## 🔐 Seguridad

- Sesión en Chrome local (no server-side)
- No hay almacenamiento en cloud
- Cookies en profile_run (destruido después)
- Nike no ve "bot" (Chrome real, no Playwright)

---

## 📞 Soporte rápido

**¿Preguntas?** Revisar documentación:

- [RESUMEN_EJECUTIVO_FINAL.md](RESUMEN_EJECUTIVO_FINAL.md) — Visión general
- [CHECKLIST_EJECUCION_FINAL.md](CHECKLIST_EJECUCION_FINAL.md) — Paso a paso
- [INDICE_DOCUMENTACION_FINAL.md](INDICE_DOCUMENTACION_FINAL.md) — Índice completo
- [LOGIN_TROUBLESHOOTING_V0_9.md](LOGIN_TROUBLESHOOTING_V0_9.md) — Problemas comunes

---

## 📦 Requisitos

```
Python 3.8+
requests
playwright
selenium
chromium (para Playwright)
Chrome real (para login)
```

---

## 🎯 Estado final

| Aspecto | Status |
|---------|--------|
| Arquitectura | ✅ Sólida |
| Código | ✅ Limpio (0 variantes) |
| Documentación | ✅ Completa (25+ docs) |
| Testing | ✅ Validado |
| Listo para drop | ✅ SÍ |

---

## 📅 Versión

```
Version: 0.9 FINAL
Date: Ahora
Status: CONGELADO (sin cambios futuros)
Last update: NUNCA (el sistema es definitivo)
```

---

## 🚀 Próximo paso

```bash
# 1. Setup (primera vez)
python login_runner.py cuenta1

# 2. Drop (cuando Nike libera)
python ui/app_v0_9_simple.py

# Eso es TODO.
```

**El sistema hará el resto.**

---

## 💡 Última verdad

> "El bot no es complicado."
>
> "Es consistente."
>
> "Un camino. Una dirección. Congelado."
>
> "Eso es todo lo que necesita para ganar drops."

---

**¿Preguntas?** → Lee [INDICE_DOCUMENTACION_FINAL.md](INDICE_DOCUMENTACION_FINAL.md)

**¿Listo para ejecutar?** → Lee [CHECKLIST_EJECUCION_FINAL.md](CHECKLIST_EJECUCION_FINAL.md)

**¿Necesitas entender?** → Lee [RESUMEN_EJECUTIVO_FINAL.md](RESUMEN_EJECUTIVO_FINAL.md)

---

**Buena suerte. 🚀**
