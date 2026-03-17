# NIKE BOT V0.9 — START HERE

**Nike Bot V0.9 congelado. 1 camino. 0 fallbacks. Listo para drops.**

---

## ⚡ QUICK START (5 minutos)

### 1. LOGIN (manual)

```bash
python login_runner.py cuenta1
```

- Chrome abre
- Loguéate en Nike.cl
- Cierra Chrome
- `.login_ok` se crea automáticamente

### 2. PLAY (automático)

```bash
python runtime/multiprocessing_runner.py 123456789 cuenta1
```

- PRE-FLIGHT verifica sesión
- Backend ejecuta ATC en < 1s
- Chrome abre con magic link
- Confirmas pago (tú decides)

**Done.**

---

## 🛠️ TROUBLESHOOTING (si hay problemas)

```bash
# Reset suave del perfil
python profile_cleanup.py cuenta1

# Diagnóstico (test normal + incógnito)
python diagnose_login_issue.py cuenta1
```

---

## 📁 ESTRUCTURA

```
auth/cuenta1/
├── profile_login/       (dónde logueas)
├── profile_run/         (dónde ejecuta bot, se clona)
└── .login_ok            (marca: LOGIN OK)

runtime/
├── backend_vtex.py      (ATC)
└── multiprocessing_runner.py (flujo 10 pasos)

ui/
└── app_v0_9_simple.py   (UI minimal)
```

---

## 🎯 FLUJO (10 PASOS)

```
1. LOGIN (Chrome real)
   └─ Usuario loguea manualmente

2. PRE-FLIGHT (verificación)
   └─ Nike verifica sesión con headless

3-6. BACKEND (< 1.5s)
   ├─ ATC: GET /checkout/cart/add?sku=...
   ├─ Price: price > 0
   └─ FREEZE: cierra sesión HTTP

7-10. HANDOVER + HUMANO
   ├─ Magic link: /checkout/#/payment
   ├─ Usuario confirma pago
   └─ EXIT
```

---

## ✅ CARACTERÍSTICAS

✅ 1 camino único  
✅ 0 fallbacks  
✅ Chrome real en LOGIN (Nike acepta)  
✅ Playwright en PLAY (bot ejecuta)  
✅ PRE-FLIGHT verifica antes de jugar  
✅ Backend < 1.5s  
✅ Determinista (sin loops)  
✅ Master/Slave separado  

---

## 🚫 PROHIBIDO

❌ Variantes (safe, fast, fallback)  
❌ SESSION_SEED (browser cookie sync)  
❌ PRICING_WAIT (esperas)  
❌ Watchers activos  
❌ Threading en Playwright  

---

## 📖 DOCS

| Doc | Propósito |
|-----|-----------|
| [LOGIN_RUNNER_FINAL.md](LOGIN_RUNNER_FINAL.md) | Cómo funciona LOGIN |
| [FLUJO_CONGELADO_V0_9.md](FLUJO_CONGELADO_V0_9.md) | Flujo exacto |
| [INDICE_V0_9_COMPLETO.md](INDICE_V0_9_COMPLETO.md) | Índice maestro |
| [ACCIONES_RECOMENDADAS_AHORA.md](ACCIONES_RECOMENDADAS_AHORA.md) | Si hay problemas |

---

## ⚙️ SETUP

```bash
# Primera vez
python login_runner.py cuenta1
# → Loguéate → Cierra Chrome → .login_ok creado

# Verificar
ls -la auth/cuenta1/.login_ok
# → Debe existir

# Ejecutar PLAY
python runtime/multiprocessing_runner.py <SKU> cuenta1
# → PRE-FLIGHT verifica
# → Backend ejecuta (< 1s)
# → Chrome abre con magic link
# → Confirmas pago
```

---

## 🏆 STATUS

✅ **SISTEMA CONGELADO Y LISTO**

- Código: 100% implementado
- Debug: 3 scripts completos
- Docs: 10+ archivos
- Testing: Sintaxis validada
- Architecture: 1 camino único

---

**Run:** `python login_runner.py <cuenta>` → `python runtime/multiprocessing_runner.py <SKU> <cuenta>`

**Done.**

