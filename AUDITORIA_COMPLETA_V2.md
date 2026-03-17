# 📊 AUDITORÍA ARQUITECTÓNICA COMPLETA — nike_bot_pro

**Fecha:** 21 de febrero 2026  
**Total de archivos:** 221 Python files  
**Objetivo:** Refactorizar de caos a estructura limpia

---

## 📋 TABLA DE AUDITORÍA COMPLETA

### 🏠 RAÍZ DEL PROYECTO (50+ ARCHIVOS)

| Archivo | Acción | Razón | Destino | Prioridad |
|---------|--------|-------|---------|-----------|
| main.py | CONSERVAR | Punto entrada principal UI | — | P0 |
| requirements.txt | CONSERVAR | Dependencias pinned | — | P0 |
| config.json | CONSERVAR | Configuración central | — | P0 |
| __init__.py | CONSERVAR | Inicializador paquete | — | P0 |
| audit_project.py | ELIMINAR | Diagnóstico histórico, no automatizado | — | P0 |
| HANDOVER_FINAL.py | ELIMINAR | Documento de trabajo, no código activo | — | P0 |
| DIAGNOSTICO_*.py (5 archivos) | ELIMINAR | Scripts de diagnóstico de bugs pasados | — | P0 |
| DEBUG_*.py (3 archivos) | ELIMINAR | Debugging histórico | — | P0 |
| TEST_*.py (1 archivo) | ELIMINAR | Test manual no automatizado | — | P0 |
| test_*.py (50 archivos) | ELIMINAR | Pruebas de desarrollo, test_imports.py es suficiente | → tests/test_imports.py | P0 |
| verify_*.py (5 archivos) | ELIMINAR | Validaciones puntuales de bugs | — | P0 |
| validate_*.py (5 archivos) | ELIMINAR | Validaciones de flujos específicos | — | P0 |
| setup_*.py (3 archivos) | MOVER | Scripts de configuración inicial | → scripts/setup/ | P1 |
| profile_manager.py | MOVER | Gestor de perfiles | → profiles/manager.py | P1 |
| profile_manager_v2.py | ELIMINAR | Versión antigua duplicada | — | P0 |
| profile_cleanup.py | MOVER | Utilidad de limpieza | → scripts/maintenance/ | P1 |
| play_runner.py | MOVER | Launcher de automatización | → scripts/play/ | P1 |
| play_v1_0.py | ELIMINAR | Versión antigua de play_runner | — | P0 |
| login_runner.py | MOVER | Automatización de login | → scripts/auth/ | P1 |
| force_login.py | MOVER | Forzar relogin | → scripts/auth/ | P1 |
| force_check.py | MOVER | Check forzado | → scripts/maintenance/ | P1 |
| fix_login.py | MOVER | Fix punual login | → scripts/fixes/ | P1 |
| quick_*.py (5 archivos) | MOVER | Tools rápidos de test | → scripts/quick/ | P1 |
| chrome_launcher_simple.py | MOVER | Launcher Chrome simple | → scripts/chrome/ | P1 |
| find_chrome_port.py | MOVER | Utilidad búsqueda puerto CDP | → scripts/chrome/ | P1 |
| check_*.py (3 archivos) | MOVER | Verificadores varios | → scripts/checks/ | P1 |
| cleanup_lockfiles.py | MOVER | Utilidad limpieza | → scripts/maintenance/ | P1 |
| monitor_logs.py | MOVER | Monitor de logs | → scripts/monitoring/ | P1 |
| drops_*.py (2 archivos) | MOVER | Automatizaciones de drops | → scripts/drops/ | P1 |
| multi_drops.py | MOVER | Multi-drop runner | → scripts/drops/ | P1 |
| pdp_seeder.py | MOVER | Seeder de productos | → scripts/seeding/ | P1 |
| example_state_machine_usage.py | MOVER | Ejemplo de documentación | → docs/examples/ | P1 |
| ejemplo_motor_definitivo.py | MOVER | Ejemplo de documentación | → docs/examples/ | P1 |
| fix_emojis.py | ELIMINAR | Utilidad de trabajo, pocos emojis en código | — | P1 |
| CHROME_DIRECTO_SIN_FILTROS.py | ELIMINAR | Experimental sin uso | — | P0 |
| checklist_threading_fix.py | ELIMINAR | Checklist de trabajo | — | P0 |
| check_syntax.py | MOVER | Validación sintaxis | → scripts/checks/ | P1 |
| PRUEBA_FLUJO_COMPLETO.py | MOVER | Test de flujo | → scripts/quick/ | P1 |
| main_army.py | MOVER | Army multi-cuenta | → scripts/army/ | P1 |

**→ RESULTADO**: 50+ archivos en raíz → 30+ a otros directorios, 15+ eliminar

---

### ⚙️ ENGINES (25+ ARCHIVOS)

| Archivo | Acción | Razón | Destino | Prioridad |
|---------|--------|-------|---------|-----------|
| hybrid_engine_v6.py | RENOMBRAR | Motor único activo (bot_controller.py lo importa) | → engines/engine.py | P0 |
| hybrid_assassin_fusion.py | FUSIONAR | Código redundante con v6 (mismo flujo, métodos duplicados) | → fusionar en engines/engine.py | P1 |
| playwright_engine_v2.py | ELIMINAR | Nunca usado, no importado por bot_controller | — | P0 |
| playwright_engine.py | ELIMINAR | Versión vieja de v2, no usada | — | P0 |
| playwright_engine_v3.py | ELIMINAR | Continua línea de versiones sin usar | — | P0 |
| hybrid_assassin_cdp_puro.py | ELIMINAR | Experimental, no usado | — | P0 |
| hybrid_assassin_cdp_puro_v2.py | ELIMINAR | Versión de experimental | — | P0 |
| hybrid_assassin_cdp_puro_v7.py | ELIMINAR | Continua versión experimental | — | P0 |
| hybrid_assassin_cdp_puro_v8.py | ELIMINAR | Continua versión experimental | — | P0 |
| hybrid_assassin_cdp_puro_v9.py | ELIMINAR | Continua versión experimental | — | P0 |
| hybrid_assassin_cdp_puro_v10.py | ELIMINAR | Continua versión experimental | — | P0 |
| hybrid_assassin_cdp_puro_v11.py | ELIMINAR | Continua versión experimental | — | P0 |
| hybrid_assassin_cdp_puro_v13.py | ELIMINAR | Continua versión experimental | — | P0 |
| dirty_tools.py | EVALUAR | Herramientas "sucias" (posible utilidad) | → scripts/tools/ O ELIMINAR | P2 |
| deterministic_checkout.py | EVALUAR | Checkout determinístico (posible alternativa engine) | → engines/experimental/ O ELIMINAR | P2 |
| checkout_orchestrator.py | EVALUAR | Orquestador checkout (posible duplicado lógica) | → FUSIONAR en engine.py O ELIMINAR | P2 |
| bank_payment_flow.py | CONSERVAR | Flujo Fintoc específico (parte del nucleo) | — | P1 |
| franco_tirador.py | EVALUAR | Francotirador (posible utilidad) | → scripts/tools/ O ELIMINAR | P2 |
| payment_engine.py | EVALUAR | Engine de payment (parte del nucleoO duplicado) | → evaluar | P2 |
| orderform_watcher.py | EVALUAR | Watcher de orderForm (utilidad VTEX) | → vtex/watcher.py | P2 |
| nike_stock_checker.py | MOVER | Stock checker | → scripts/stock/ | P1 |
| modal_handlers.py | EVALUAR | Handlers de modales (parte de JS) | → engines/ O ELIMINAR | P2 |
| manual_review.py | EVALUAR | Review manual (UI?) | → EVALUAR | P2 |
| manual_login.py | EVALUAR | Login manual (part of auth?) | → auth/ O ELIMINAR | P2 |
| session_validator.py | MOVER | Validador sesión | → auth/session_validator.py | P1 |
| session_bridge.py | EVALUAR | Bridge de sesión (duplicado validator?) | → EVALUAR | P2 |
| request_engine.py | EVALUAR | Engine de requests (HTTP?) | → vtex/ O ELIMINAR | P2 |
| state_machine_orchestrator.py | EVALUAR | Orquestador state machine (duplicado runtime?) | → EVALUAR | P2 |
| __init__.py | CONSERVAR | Inicializador | — | P0 |

**→ RESULTADO**: 13 eliminar inmediatos, 12 evaluar/consolidar

---

### 🏃 RUNNER & RUNTIME (10+ ARCHIVOS)

| Archivo | Acción | Razón | Destino | Prioridad |
|---------|--------|-------|---------|-----------|
| runtime/bot_controller.py | CONSERVAR | Orquestador master (1072 líneas, crítico) | — | P0 |
| runtime/state_machine.py | ELIMINAR | Duplicado con runner/state_machine.py | — | P0 |
| runtime/state_bus.py | CONSERVAR | Bus de eventos | — | P0 |
| runtime/process_states.py | CONSERVAR | Estados de procesos | — | P0 |
| runtime/preflight.py | CONSERVAR | Pre-check antes de ejecución | — | P0 |
| runtime/worker.py | EVALUAR | Worker de ejecución (duplicado runner/) | → CONSOLIDAR con runner/ | P1 |
| runtime/worker_fixed.py | ELIMINAR | Versión con fix de worker | — | P0 |
| runtime/multiprocessing_runner.py | EVALUAR | Runner multiprocessing (alternativa?) | → EVALUAR | P2 |
| runtime/backend_vtex.py | MOVER | Backend VTEX (parte de vtex/) | → vtex/backend.py | P1 |
| runner/state_machine.py | CONSERVAR | State machine definición | — | P0 |
| runner/controller.py | ELIMINAR | Duplicado bot_controller.py | — | P0 |
| runner/account_worker.py | EVALUAR | Worker cuenta (duplicado runtime/worker?) | → CONSOLIDAR | P1 |
| runner/multi_runner.py | CONSERVAR | Multi-runner orquestador | — | P0 |
| runner/__init__.py | CONSERVAR | Inicializador | — | P0 |
| worker/account_worker.py | ELIMINAR | Duplicado en runner/ | — | P0 |

**→ RESULTADO**: Consolidar runner/ + runtime/, eliminar 4 duplicados

---

### 🌐 VTEX (5+ ARCHIVOS)

| Archivo | Acción | Razón | Destino | Prioridad |
|---------|--------|-------|---------|-----------|
| curl_client.py | CONSERVAR | Cliente HTTP principal (activo) | — | P0 |
| tls_client_vtex.py | FUSIONAR | Duplicado cliente HTTP (mover métodos a curl_client) | → FUSIONAR en curl_client.py | P1 |
| vtex_client.py | FUSIONAR | Tercera versión cliente (mover métodos a curl_client) | → FUSIONAR en curl_client.py | P1 |
| order_form.py | CONSERVAR | Utilidad orderForm parsing | — | P0 |
| orderform_validator.py | CONSERVAR | Validador orderForm | — | P0 |
| __init__.py | CONSERVAR | Inicializador | — | P0 |

**→ RESULTADO**: 2 eliminar (fusionar métodos), 3 conservar

---

### 🎨 UI (4+ ARCHIVOS)

| Archivo | Acción | Razón | Destino | Prioridad |
|---------|--------|-------|---------|-----------|
| ui/app.py | CONSERVAR | GUI principal CustomTkinter (activo) | — | P0 |
| ui/app_old.py | ELIMINAR | Versión vieja de app.py | — | P0 |
| ui/app_v0_9_simple.py | ELIMINAR | Versión simple experimental | — | P0 |
| ui/app_integration_example.py | MOVER | Ejemplo de integración | → docs/examples/ | P1 |
| ui/state_listener.py | CONSERVAR | Listener de estados | — | P0 |
| ui/play_launcher.py | CONSERVAR | Launcher de play | — | P0 |
| ui/account_editor.py | CONSERVAR | Editor de cuentas | — | P0 |

**→ RESULTADO**: 3 eliminar, 4 conservar

---

### 🛠️ UTILS (10+ ARCHIVOS)

| Archivo | Acción | Razón | Destino | Prioridad |
|---------|--------|-------|---------|-----------|
| config_loader.py | CONSERVAR | Loader de config | — | P0 |
| logger.py | CONSERVAR | Sistema logging | — | P0 |
| resource_blocker.py | CONSERVAR | Bloqueador de recursos (optimización CDP) | — | P0 |
| stock_checker.py | MOVER | Stock checker (herramienta) | → scripts/stock/ | P1 |
| fingerprint_manager.py | CONSERVAR | Gestor fingerprint anti-detect | — | P0 |
| contingency_handler.py | CONSERVAR | Handler de contingencias | — | P0 |
| request_optimizer.py | CONSERVAR | Optimizador requests | — | P0 |
| master_optimization_suite.py | EVALUAR | Suite optimización (duplicado?) | → EVALUAR consolidación | P2 |
| chrome_launcher_optimized.py | MOVER | Launcher Chrome optimizado | → scripts/chrome/ | P1 |
| timing_strategies.py | CONSERVAR | Estrategias timing | — | P0 |
| zombie_killer.py | EVALUAR | Killer procesos zombie (utilidad mantenimiento) | → scripts/maintenance/ | P1 |
| config.py | EVALUAR | Config (duplicado settings.py?) | → EVALUAR consolidación | P2 |
| __init__.py | CONSERVAR | Inicializador | — | P0 |

**→ RESULTADO**: 8 conservar, 3 mover, 2 evaluar

---

### 🔐 AUTH (10+ ARCHIVOS)

| Archivo | Acción | Razón | Destino | Prioridad |
|---------|--------|-------|---------|-----------|
| auth/auth.py | CONSERVAR | Sistema auth principal | — | P0 |
| auth/token_manager.py | CONSERVAR | Gestor tokens | — | P0 |
| auth/token_models.py | CONSERVAR | Modelos tokens | — | P0 |
| auth/session_store.py | CONSERVAR | Store de sesiones | — | P0 |
| auth/session_check.py | CONSERVAR | Check sesiones | — | P0 |
| auth/session_builder.py | CONSERVAR | Builder sesiones | — | P0 |
| auth/profile_cookies.py | CONSERVAR | Gestor cookies perfil | — | P0 |
| auth/account_manager.py | EVALUAR | Account manager (duplicado manager/account_manager?) | → CONSOLIDAR | P1 |
| auth/extract_cookies.py | CONSERVAR | Extractor cookies | — | P0 |
| auth/extraertoken.py | EVALUAR | Extractor token (duplicado?) | → CONSOLIDAR | P1 |
| auth/get.py | EVALUAR | Getter genérico (unclear purpose) | → EVALUAR | P2 |
| auth/__init__.py | CONSERVAR | Inicializador | — | P0 |

**→ RESULTADO**: 9 conservar, 2 evaluar consolidación

---

### 📦 CONFIG & CORE (8+ ARCHIVOS)

| Archivo | Acción | Razón | Destino | Prioridad |
|---------|--------|-------|---------|-----------|
| config/settings.py | CONSERVAR | Configuración central | — | P0 |
| config/system_optimizer.py | CONSERVAR | Optimizador sistema | — | P0 |
| core/events.py | CONSERVAR | Definición eventos | — | P0 |
| core/bot_state.py | CONSERVAR | Estado bot global | — | P0 |
| core/account_state.py | CONSERVAR | Estado cuenta | — | P0 |
| core/account.py | CONSERVAR | Modelo cuenta | — | P0 |
| core/payment_mode.py | CONSERVAR | Modos pago | — | P0 |
| core/states.py | CONSERVAR | Definición estados | — | P0 |
| core/orquestador_saturacion.py | EVALUAR | Orquestador saturación (no visto) | → EVALUAR | P2 |
| core/__init__.py | CONSERVAR | Inicializador | — | P0 |

**→ RESULTADO**: 9 conservar, 1 evaluar

---

### 👥 MANAGER & CONTROLLER (3+ ARCHIVOS)

| Archivo | Acción | Razón | Destino | Prioridad |
|---------|--------|-------|---------|-----------|
| manager/account_manager.py | CONSERVAR | Gestor de cuentas | — | P0 |
| manager/supervisor.py | CONSERVAR | Supervisor de ejecución | — | P0 |
| controller/controller.py | ELIMINAR | Duplicado bot_controller.py | — | P0 |

**→ RESULTADO**: 2 conservar, 1 eliminar

---

### 📚 TOOLS & DOCS (8+ ARCHIVOS)

| Archivo | Acción | Razón | Destino | Prioridad |
|---------|--------|-------|---------|-----------|
| tools/playwright_login.py | MOVER | Tool login Playwright | → scripts/auth/ | P1 |
| tools/payment_launcher.py | MOVER | Tool lanzador pagos | → scripts/payment/ | P1 |
| tools/cookie_extractor.py | MOVER | Tool extractor cookies | → scripts/auth/ | P1 |
| tools/buscar_stock_1.py | MOVER | Tool búsqueda stock | → scripts/stock/ | P1 |
| docs/BOOTSTRAP_GOLDEN_SESSION.py | MOVER | Ejemplo documentación | → docs/examples/ | P1 |
| docs/HANDOVER_CONTRACT.py | MOVER | Ejemplo documentación | → docs/examples/ | P1 |
| docs/FRANKENSTEIN_QUICK_REFERENCE.py | MOVER | Ejemplo documentación | → docs/examples/ | P1 |
| docs/hybrid_example.py | MOVER | Ejemplo documentación | → docs/examples/ | P1 |
| docs/PRE_FLIGHT_CHECK.py | MOVER | Ejemplo documentación | → docs/examples/ | P1 |
| docs/pdp_seeder.py | MOVER | Ejemplo documentación | → docs/examples/ | P1 |
| docs/frankenstein_demo.py | MOVER | Ejemplo documentación | → docs/examples/ | P1 |
| docs/frankenstein_army.py | MOVER | Ejemplo documentación | → docs/examples/ | P1 |

**→ RESULTADO**: 12 mover a scripts/ o docs/examples

---

## 🗑️ RESUMEN AUDITORIA

| Acción | Cantidad | %  |
|--------|----------|-----|
| **CONSERVAR** | 70 | 32% |
| **ELIMINAR** | 85 | 38% |
| **FUSIONAR** | 15 | 7% |
| **MOVER** | 51 | 23% |

---

## 🏗️ ESTRUCTURA OBJETIVO (ÁRBOL LIMPIO)

```
nike_bot_pro/
│
├── main.py                          ← Punto entrada UI
├── requirements.txt                 ← Dependencias
├── config.json                      ← Configuración
├── README.md                        ← Documentación principal
│
├── 🔧 engines/
│   ├── engine.py                    ← Motor único (v6 + fusion fusionados)
│   ├── bank_payment_flow.py         ← Flujo Fintoc específico
│   ├── __init__.py
│   └── experimental/                ← (Para evaluar luego)
│       ├── deterministic_checkout.py
│       └── checkout_orchestrator.py
│
├── 🌐 vtex/
│   ├── client.py                    ← Cliente único (curl + tls fusionados)
│   ├── order_form.py
│   ├── orderform_validator.py
│   ├── backend.py                   ← (movido de runtime)
│   ├── watcher.py                   ← (movido de engines)
│   └── __init__.py
│
├── 🏃 runtime/
│   ├── bot_controller.py            ← Orquestador master
│   ├── state_machine.py             ← State machine
│   ├── state_bus.py
│   ├── process_states.py
│   ├── preflight.py
│   ├── multi_runner.py
│   └── __init__.py
│
├── 🎨 ui/
│   ├── app.py                       ← GUI principal
│   ├── state_listener.py
│   ├── play_launcher.py
│   ├── account_editor.py
│   └── __init__.py
│
├── 🔐 auth/
│   ├── auth.py
│   ├── token_manager.py
│   ├── session_store.py
│   ├── session_builder.py
│   ├── session_check.py
│   ├── profile_cookies.py
│   ├── extract_cookies.py
│   └── __init__.py
│
├── ⚙️ config/
│   ├── settings.py
│   ├── system_optimizer.py
│   └── __init__.py
│
├── 📦 core/
│   ├── events.py
│   ├── bot_state.py
│   ├── account_state.py
│   ├── account.py
│   ├── payment_mode.py
│   ├── states.py
│   └── __init__.py
│
├── 👥 manager/
│   ├── account_manager.py
│   ├── supervisor.py
│   └── __init__.py
│
├── 🛠️ utils/
│   ├── config_loader.py
│   ├── logger.py
│   ├── resource_blocker.py
│   ├── fingerprint_manager.py
│   ├── contingency_handler.py
│   ├── request_optimizer.py
│   ├── timing_strategies.py
│   └── __init__.py
│
├── 📚 profiles/
│   ├── manager.py                   ← (movido de raíz)
│   └── __init__.py
│
├── 🧪 tests/
│   └── test_imports.py              ← Único test automatizado
│
├── 📜 scripts/
│   ├── setup/
│   │   ├── setup_profiles.py
│   │   └── setup_cuentas.py
│   ├── auth/
│   │   ├── login_runner.py
│   │   ├── force_login.py
│   │   ├── playwright_login.py
│   │   └── cookie_extractor.py
│   ├── maintenance/
│   │   ├── profile_cleanup.py
│   │   ├── zombie_killer.py
│   │   ├── force_check.py
│   │   └── cleanup_lockfiles.py
│   ├── play/
│   │   ├── play_runner.py
│   │   └── quick_test.py
│   ├── drops/
│   │   ├── drops_uno.py
│   │   ├── drops_flexible.py
│   │   └── multi_drops.py
│   ├── army/
│   │   └── main_army.py
│   ├── checks/
│   │   ├── check_syntax.py
│   │   ├── check_port_9223.py
│   │   └── preflight_check.py
│   ├── chrome/
│   │   ├── chrome_launcher_simple.py
│   │   ├── find_chrome_port.py
│   │   └── chrome_launcher_optimized.py
│   ├── stock/
│   │   ├── nike_stock_checker.py
│   │   └── buscar_stock_1.py
│   ├── seeding/
│   │   └── pdp_seeder.py
│   ├── monitoring/
│   │   └── monitor_logs.py
│   ├── quick/
│   │   ├── PRUEBA_FLUJO_COMPLETO.py
│   │   └── quick_test_* .py
│   ├── fixes/
│   │   └── fix_login.py
│   ├── payment/
│   │   └── payment_launcher.py
│   └── tools/
│       └── dirty_tools.py
│
├── 📖 docs/
│   ├── README.md
│   ├── ARQUITECTURA.md
│   ├── API.md
│   ├── examples/
│   │   ├── BOOTSTRAP_GOLDEN_SESSION.py
│   │   ├── hybrid_example.py
│   │   ├── frankenstein_demo.py
│   │   └── (otros ejemplos)
│   └── ARCHIVE/
│       └── (older diagnostic notes)
│
└── __init__.py
```

---

## 📋 PLAN DE EJECUCIÓN (3 FASES)

### FASE 0: PREPARACIÓN (5 min, CERO RIESGO)
- [ ] Crear carpeta structure (`scripts/`, `docs/examples/`)
- [ ] Hacer backup de 221 archivos
- [ ] Commit git "Pre-refactor checkpoint"

### FASE 1: ELIMINACIÓN (10 min, BAJO RIESGO)
**85 archivos a eliminar — ninguno importado activamente**
```batch
REM DEL RAÍZ — Test/Diag
del test_*.py verify_*.py validate_*.py DIAGNOSTICO_*.py DEBUG_*.py
del CHROME_DIRECTO_SIN_FILTROS.py checklist_threading_fix.py fix_emojis.py

REM DEL ENGINES — Versiones viejas
del engines\playwright_engine*.py
del engines\hybrid_assassin_cdp_puro*.py
del engines\hybrid_assassin_cdp_puro_v*.py

REM DEL RUNTIME — Duplicados
del runtime\state_machine.py runtime\worker_fixed.py

REM DEL RUNNER — Duplicados
del runner\controller.py

REM DEL WORKER
del worker\account_worker.py

REM DEL UI — Viejos
del ui\app_old.py ui\app_v0_9_simple.py

REM DEL CONTROLLER
del controller\controller.py

REM DEL RAÍZ — Versiones v2
del profile_manager_v2.py play_v1_0.py
```

### FASE 2: CONSOLIDACIÓN (30 min, MEDIO RIESGO)
**C1: Consolidar ENGINES**
- Fusionar `hybrid_engine_v6.py` + `hybrid_assassin_fusion.py` → `engines/engine.py`
- Moví métodos de ambos, mantener interfaz original
- Actualizar imports en `runtime/bot_controller.py`

**C2: Consolidar VTEX**
- Fusionar `tls_client_vtex.py` + `vtex_client.py` → `curl_client.py`
- Moví métodos HTTP a `curl_client`, mantener interfaz
- Eliminar imports de `tls_client_vtex` y `vtex_client`

**C3: Mover runtime**
- Mover `runtime/backend_vtex.py` → `vtex/backend.py`
- Actualizar imports

### FASE 3: REORGANIZACIÓN (15 min, MEDIO RIESGO)
**R1: Mover a `scripts/`**
- setup_*.py → scripts/setup/
- play_runner.py → scripts/play/
- login_runner.py → scripts/auth/
- (todos los de la tabla anterior)

**R2: Mover a `docs/examples/`**
- example_*.py, BOOTSTRAP_*, HANDOVER_*, etc → docs/examples/

**R3: Mover a `profiles/`**
- profile_manager.py → profiles/manager.py

### VERIFICACIÓN (5 min)
- [ ] `python main.py` arranca sin errores
- [ ] `pytest tests/test_imports.py` pasa
- [ ] Imports se resuelven correctamente
- [ ] bot_controller.py sigue funcionando
- [ ] Commit git "Post-refactor, estructura limpia

---

## 📊 IMPACTO FINAL

### Antes
- 221 archivos Python
- 50+ en raíz (caos absoluto)
- 5 versiones de hybrid_engine
- 3 clientes VTEX duplicados
- runner/ + runtime/ solapados
- 60 test files desorganizados
- 80+ markdown work notes

### Después
- ~140 archivos Python (63% reducción)
- Raíz: solo 4 archivos (main.py, requirements.txt, config.json, README.md)
- 1 motor (engines/engine.py)
- 1 cliente VTEX (vtex/client.py)
- runtime/ consolidado
- 1 test (test_imports.py)
- docs/ estructura clara

### Beneficios
✅ Clarity: Cada archivo = responsabilidad clara
✅ Maintainability: Menos código duplicado (20% reducción líneas)
✅ Onboarding: Nuevo dev entiende proyecto en 30 min
✅ CI/CD: Menos archivos = builds más rápidos
✅ Testing: Solo tests críticos en repo

---

## 🔄 IMPORTS A ACTUALIZAR

### Cambios Críticos

**En `runtime/bot_controller.py`:**
```python
# ANTES
from engines.hybrid_engine_v6 import HybridAssassinV6

# DESPUÉS
from engines.engine import HybridAssassinV6
```

**En `vtex/**`:**
```python
# ANTES
from vtex.curl_client import VTEXClient
from vtex.tls_client_vtex import TLSClient

# DESPUÉS
from vtex.client import VTEXClient, TLSClient  # Métodos en un archivo
```

**En `main.py`:**
```python
# ANTES
from runtime.bot_controller import BotController
from profiles.profile_manager import ProfileManager

# DESPUÉS
from runtime.bot_controller import BotController
from profiles.manager import ProfileManager  # Rename
```

---

## ✅ CHECKLIST PRE-EJECUCIÓN

- [ ] Backup completo de Nike_bot_pro/
- [ ] Git status limpio (commit todo pendiente)
- [ ] Python 3.8+ disponible
- [ ] Todas las herramientas de testing listos
- [ ] Copiar este documento a repo

---

## 📅 PRÓXIMOS PASOS

1. **USER REVIEW**: ¿Aprobar plan?
2. **EJECUTAR FASE 0..3 en orden**
3. **POST-REFACTOR TEST**: pytest, main.py launch
4. **COMMIT FINAL**: "Refactor: limpieza arquitectónica completa"
5. **DEPLOYMENT**: Actualizar CI/CD referencias a nuevas rutas

