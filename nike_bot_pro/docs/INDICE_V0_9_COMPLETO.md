# NIKE BOT V0.9 — SISTEMA CONGELADO PARA DROPS

**Status**: ✅ LISTO PARA DROPS COMPETIDOS

**Arquitecto**: Senior Bot Automation Auditor  
**Fecha**: 3 de Enero de 2026

---

## 📋 ÍNDICE COMPLETO

### 🎯 EMPEZAR AQUÍ

1. **[ACCION_INMEDIATA_DEBUG.md](ACCION_INMEDIATA_DEBUG.md)** — Quick start (si hay problemas)
2. **[LOGIN_TROUBLESHOOTING_V0_9.md](LOGIN_TROUBLESHOOTING_V0_9.md)** — Troubleshooting completo
3. **[HERRAMIENTAS_DEBUG_V0_9.md](HERRAMIENTAS_DEBUG_V0_9.md)** — Documentación de scripts

### 📐 ARQUITECTURA

4. **[FLUJO_CONGELADO_V0_9.md](FLUJO_CONGELADO_V0_9.md)** — Flujo exacto (10 pasos)
5. **[IMPLEMENTACION_FLUJO_V0_9_COMPLETADA.md](IMPLEMENTACION_FLUJO_V0_9_COMPLETADA.md)** — Implementación
6. **[CONGELACION_V0_9_AUDITORIA_COMPLETA.md](CONGELACION_V0_9_AUDITORIA_COMPLETA.md)** — Auditoría exhaustiva
7. **[V0_9_FROZEN_EXECUTION_PLAN.md](V0_9_FROZEN_EXECUTION_PLAN.md)** — Plan de ejecución
8. **[CONGELACION_FINAL_RESUMEN.md](CONGELACION_FINAL_RESUMEN.md)** — Resumen ejecutivo

---

## 🛠️ HERRAMIENTAS Y SCRIPTS

### LOGIN (Manual, Off-Drop)
```bash
python login_runner.py <cuenta>
```
- Usuario loguea en Chrome
- Script verifica con Nike
- Crea .login_ok

### PROFILE CLEANUP (Debug)
```bash
python profile_cleanup.py <cuenta>
```
- Borra Cache, Code Cache, Service Worker
- Mantiene cookies y auth tokens
- Reset suave sin perder sesión

### DIAGNÓSTICO (Debug)
```bash
python diagnose_login_issue.py <cuenta>
```
- Test con Chrome normal
- Test con incógnito
- Detecta perfil contaminado

### PLAY (Automatizado, Drop)
```bash
python runtime/multiprocessing_runner.py <SKU> <cuenta1> [cuenta2]...
```
- Backend ATC (< 1s)
- Handover automático
- 1 proceso = 1 cuenta

---

## 📊 FLUJO V0.9 (10 PASOS, SIN VARIANTES)

```
PASO 1: LOGIN (humano, off-drop)
  └─ Abrir Chrome, loguear, verificar Nike, crear .login_ok

PASO 2: PRE-PLAY CHECK
  └─ Verificar .login_ok, clonar profile_login → profile_run, headless test

PASO 3-6: BACKEND (< 1.5s)
  ├─ Paso 3: Sesión HTTP limpia
  ├─ Paso 4: GET /checkout/cart/add?sku=...&qty=1
  ├─ Paso 5: price > 0
  └─ Paso 6: Cerrar sesión (FREEZE)

PASO 7-10: HANDOVER + HUMANO
  ├─ Paso 7: Abrir Chrome visible
  ├─ Paso 8: Navegar a /checkout/#/payment (magic link)
  ├─ Paso 9: Usuario confirma pago (click / OTP)
  └─ Paso 10: EXIT (cerrar, destruir profile_run)
```

**Características**:
- ✅ 1 camino único
- ✅ 0 fallbacks
- ✅ 0 A/B
- ✅ Backend muere después del FREEZE
- ✅ Determinista (sin loops, sin watchers)

---

## 📁 ESTRUCTURA FINAL

```
nike_bot_pro/
│
├── auth/
│   └── <cuentas>/
│       ├── profile_login/        (MASTER - usuario loguea)
│       ├── profile_run/          (SLAVE - clona automático)
│       └── .login_ok             (marca: LOGIN OK)
│
├── runtime/
│   ├── process_states.py         (11 estados)
│   ├── state_bus.py              (Queue para estados)
│   ├── backend_vtex.py           (HTTP ATC + price check)
│   └── multiprocessing_runner.py (Flujo 10 pasos)
│
├── ui/
│   ├── app_v0_9_simple.py        (UI minimal: LOGIN + PLAY)
│   ├── state_listener.py         (Background thread)
│   └── play_launcher.py          (Bridge UI → multiprocessing)
│
├── login_runner.py               (LOGIN manual)
├── profile_manager_v2.py         (Clone guardado)
├── profile_cleanup.py            (Reset suave)
├── diagnose_login_issue.py       (Test normal + incógnito)
│
└── (documentación V0.9)
```

---

## 🚀 EJECUCIÓN RÁPIDA

### Setup (primera vez)

```bash
# 1. Crear perfil login (manual)
python login_runner.py cuenta1
# → Loguéate en Chrome
# → Script crea .login_ok

# 2. Verificar
ls -la auth/cuenta1/.login_ok
# → Debe existir
```

### Play (repetible)

```bash
# 1. Ejecutar drop
python runtime/multiprocessing_runner.py 123456789 cuenta1

# O desde UI:
python ui/app_v0_9_simple.py
# → Selecciona cuenta1
# → Ingresa SKU
# → Click PLAY
```

### Debug (si hay problemas)

```bash
# 1. Cleanup
python profile_cleanup.py cuenta1

# 2. Reintenta LOGIN
python login_runner.py cuenta1

# 3. Si sigue fallando, diagnóstico
python diagnose_login_issue.py cuenta1
```

---

## ⚡ PERFORMANCE

| Fase | Tiempo |
|------|--------|
| LOGIN (manual) | ~2 min |
| CLONE + PREFLIGHT | ~5 sec |
| BACKEND (ATC + price) | < 1 sec |
| HANDOVER | ~200 ms |
| **Total backend** | **< 1.5 sec** |
| CHECKOUT (humano) | ~10-30 sec |

---

## ✅ VALIDACIÓN FINAL

### Arquitectura
- ✅ 1 camino único (no hay alternativas)
- ✅ 0 fallbacks (si falla, muere)
- ✅ 0 A/B (sin variantes)
- ✅ Determinista (pasos fijos)

### Backend
- ✅ Sesión HTTP limpia
- ✅ ATC directo (GET /checkout/cart/add)
- ✅ Price check inmediato
- ✅ FREEZE después de price

### Handover
- ✅ Magic link directo (/checkout/#/payment)
- ✅ Sin pasos intermedios
- ✅ Usuario decide pago

### Perfiles
- ✅ profile_login: MASTER (dónde logueas)
- ✅ profile_run: SLAVE (clona fresco cada vez)
- ✅ Separación absoluta

### Ejecución
- ✅ Multiprocessing (spawn method)
- ✅ 1 proceso = 1 cuenta
- ✅ Estado bus para reporting

---

## 🎯 CHECKLIST PRE-DROP

- [ ] LOGIN completado: `ls auth/cuenta1/.login_ok`
- [ ] SKU configurado en config o parámetro
- [ ] Cuentas seleccionadas (UI o línea de comando)
- [ ] Backend funcionando: `python runtime/backend_vtex.py` (test)
- [ ] Multiprocessing OK: `python runtime/multiprocessing_runner.py <SKU> cuenta1`
- [ ] Estado listeners funcionando (ver estados en tiempo real)

---

## 🔐 ARQUITECTURA MASTER/SLAVE

**Protección crítica**: Separación absoluta de perfiles

```
profile_login (MASTER)
├─ Usuario loguea manualmente
├─ Sesión verificada por Nike
├─ Marca .login_ok creada
└─ NUNCA toca bot durante PLAY

profile_run (SLAVE)
├─ Clonado de profile_login
├─ Bot ejecuta ATC + handover
├─ Destruido después de PLAY
└─ Perfil_login nunca se toca
```

**Garantía**: Si profile_login falla, es LOGIN. Si profile_run falla, crea nuevo (no toca master).

---

## 🚫 PROHIBIDO

- ❌ SESSION_SEED (browser cookie sync)
- ❌ PRICING_WAIT (espera de precio)
- ❌ Fallback a ATC manual
- ❌ Watchers activos después del FREEZE
- ❌ Retries inteligentes
- ❌ Modos safe/fast
- ❌ Threading en Playwright (solo multiprocessing)
- ❌ Iteración durante combate

---

## 📞 SOPORTE RÁPIDO

**¿LOGIN falla?**
→ Ejecuta: `python profile_cleanup.py cuenta1` + `python diagnose_login_issue.py cuenta1`

**¿PLAY falla?**
→ Verifica .login_ok: `ls auth/cuenta1/.login_ok`

**¿Perfil corrupto?**
→ `rm -rf auth/cuenta1/profile_login` + nuevo LOGIN

**¿Performance lenta?**
→ Normal: backend ~1s. Si > 2s, revisar ISP.

---

## 📖 DOCUMENTACIÓN

**Por leer en orden**:
1. ACCION_INMEDIATA_DEBUG.md (si hay problemas)
2. FLUJO_CONGELADO_V0_9.md (entender flujo)
3. CONGELACION_V0_9_AUDITORIA_COMPLETA.md (arquitectura)
4. LOGIN_TROUBLESHOOTING_V0_9.md (debug detallado)

---

## 🏆 VERDICT FINAL

**✅ SISTEMA CONGELADO Y LISTO PARA DROPS COMPETIDOS**

- Arquitectura: 1 camino único
- Backend: < 1.5s
- Determinismo: 100%
- Production-ready: SÍ

**Próxima acción**: Ejecutar LOGIN, luego PLAY.

