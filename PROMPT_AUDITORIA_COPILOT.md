# 📋 PROMPT PARA IA DE EDITOR (Copilot / Cursor)

Copia el contenido de abajo exactamente en el chat de tu IA de editor (GitHub Copilot, Cursor, etc):

---

## SISTEMA

Eres un arquitecto de software senior especializado en refactoring de proyectos caóticos. Tu tarea es hacer una **auditoría arquitectónica completa y ejecutable** de un proyecto Python de automatización web.

---

## PROYECTO

**nike_bot_pro** — Bot de automatización web VTEX + Nike  
Stack: Python 3.8+ | CustomTkinter GUI | Playwright | WebSocket + Chrome Remote Debugging Protocol

**Estado actual:** 221 archivos Python, 80+ documentos .md, 50+ archivos en raíz (CAOS)

---

## REGLAS DE AUDITORÍA (NO NEGOCIABLES)

1. ✅ Cada archivo = UNA sola responsabilidad
2. ✅ NO pueden existir dos archivos haciendo lo mismo
3. ✅ La RAÍZ solo puede tener: `main.py`, `requirements.txt`, `config.json`, `README.md`
4. ✅ NO archivos con sufijos: `_old`, `_v2`, `_legacy`, `_backup`, `_test` (excepto en carpeta `/tests`)
5. ✅ `utils/` ≤ 7 archivos
6. ✅ `engines/` = 1 ÚNICO motor (consolidar hybrid_engine_v6, hybrid_assassin_fusion, playwright_engine_v2)
7. ✅ `vtex/` = 1 ÚNICO cliente HTTP (consolidar curl_client, tls_client_vtex, vtex_client)
8. ✅ `runner/` y `runtime/` solo uno (determinar cuál eliminar)

---

## ESTRUCTURA ACTUAL

```
nike_bot_pro/
├── __init__.py
├── main.py ✅
├── config.json ✅
├── requirements.txt ✅ (NUEVO)
├── README.md ✅
│
├── [50+ archivos sueltos en raíz] ❌ CAOS
│   ├── accounts.json (→ config/)
│   ├── cookies_extracted.json (→ config/)
│   ├── *.md (80+ documentos) (→ docs/)
│   ├── *_old.py, *_v*.py (13+ archivos) (→ ELIMINAR)
│   └── ...
│
├── engines/
│   ├── hybrid_engine_v6.py ✅ ACTIVO
│   ├── hybrid_assassin_fusion.py ❌ DUPLICADO
│   ├── playwright_engine_v2.py ❌ DUPLICADO
│   └── [5+ archivos más] ❌ ELIMINAR
│
├── runtime/
│   ├── bot_controller.py ✅ (1072 líneas, estado machine)
│   ├── state_machine.py ❌ (duplicado en runner/)
│
├── runner/
│   ├── account_runner.py ❌ (duplicado con runtime/)
│   ├── state_machine.py ❌ (duplicado)
│   │
├── vtex/
│   ├── curl_client.py ✅
│   ├── tls_client_vtex.py ❌ DUPLICADO
│   ├── vtex_client.py ❌ DUPLICADO
│
├── ui/
│   ├── app.py ✅ (UI principal)
│   ├── app_old.py ❌ ELIMINAR
│
├── config/
│   ├── settings.py ✅
│   └── ...
│
├── profiles/
│   ├── profile_manager.py ✅
│   └── profile_manager_v2.py ❌ DUPLICADO
│
└── [utils/, helpers/, lib/, etc]
```

---

## ENTREGA REQUERIDA

Para **CADA ARCHIVO** hazme una tabla con este formato EXACTO:

```
| Archivo | Acción | Razón Técnica | Destino/Fusionar Con | Prioridad |
|---------|--------|---------------|-----------------------|-----------|
| engines/hybrid_engine_v6.py | CONSERVAR | Motor único activo, importado por bot_controller.py | Renombrar a engines/engine.py | P0 |
| engines/hybrid_assassin_fusion.py | FUSIONAR | Código redundante, métodos iguales | engines/engine.py (consolidar ataque_backend + ataque_frontend) | P1 |
| engines/playwright_engine_v2.py | ELIMINAR | Nunca usado, bot_controller no lo importa | — | P1 |
```

**ACCIONES VÁLIDAS:**
- `CONSERVAR` — archivo crítico, mantener igual
- `ELIMINAR` — archivo innecesario, borrar
- `FUSIONAR` — combinar con otro archivo
- `MOVER` — cambiar de carpeta
- `RENOMBRAR` — cambiar nombre
- `REESCRIBIR` — refactorizar sin cambiar ubicación

---

## AL FINAL ENTREGA:

### 1. TABLA COMPLETA DE AUDITORÍA
- Todas las clases/módulos de nike_bot_pro/
- Estado de cada archivo (conservar/eliminar/mover/fusionar)
- Razón técnica específica

### 2. ESTRUCTURA OBJETIVO (ÁRBOL LIMPIO)
```
nike_bot_pro/
├── main.py
├── requirements.txt
├── config.json
├── README.md
├── engines/
│   └── engine.py (hybrid_engine_v6 + hybrid_assassin_fusion consolidados)
├── runtime/
│   ├── bot_controller.py
│   └── state_manager.py
├── vtex/
│   └── client.py (curl_client + tls_client_vtex consolidados)
├── ui/
│   └── app.py
├── config/
│   ├── settings.py
│   └── ...
├── profiles/
│   └── manager.py
├── docs/
│   ├── README.md (documento principal)
│   ├── API.md
│   └── ARCHITECTURE.md
├── tests/
│   └── test_imports.py
└── scripts/
    ├── setup_profiles.py
    └── debug_chrome.py
```

### 3. PLAN DE EJECUCIÓN (ORDEN POR RIESGO)
**FASE 0 (Minutos - CERO RIESGO):**
- Eliminar archivos _old, _v*, _legacy, _backup

**FASE 1 (30 min - BAJO RIESGO):**
- Mover archivos sueltos a carpetas (config/, docs/, scripts/)
- Reorganizar raíz

**FASE 2 (1 hora - MEDIO RIESGO):**
- Fusionar engines en 1 (hybrid_engine_v6 + hybrid_assassin_fusion)
- Fusionar vtex clients en 1
- Actualizar imports en bot_controller.py

**FASE 3 (30 min - MEDIO RIESGO):**
- Eliminar runner/ OR consolidar con runtime/
- Actualizar imports en main.py y bot_controller.py

### 4. IMPORTS A ACTUALIZAR (POR ARCHIVO)
- `runtime/bot_controller.py` — cambiar `from engines.hybrid_engine_v6 import HybridAssassinV6` → `from engines.engine import HybridAssassinV6`
- `main.py` — cualquier import de engines/runtime que cambie de ubicación
- **Lista completa de todos los cambios de import necesarios**

### 5. VERIFICACIÓN POST-AUDITORÍA
- [ ] ¿main.py todavía carga sin errores?
- [ ] ¿Los imports se resolvieron correctamente?
- [ ] ¿Se eliminaron 150+ archivos innecesarios?
- [ ] ¿La raíz ahora tiene solo 5 archivos?

---

## ENTREGA FINAL: GENÉRAME UN SCRIPT BASH/BATCH

Con comandos exactos para ejecutar la limpieza:
```bash
# Ejemplo formato esperado
del engines\hybrid_assassin_fusion.py
del engines\playwright_engine_v2.py
move config\*.json config\backup\
# ... etc
```

---

## INFORMACIÓN ADICIONAL IMPORTANTE

**Archivos ACTIVOS (verificados en código):**
- `runtime/bot_controller.py` — orquestador master, importa `hybrid_engine_v6`
- `engines/hybrid_engine_v6.py` — motor único en uso
- `ui/app.py` — GUI principal
- `vtex/curl_client.py` — cliente VTEX activo
- `profiles/profile_manager.py` — gestor de perfiles

**Archivos DUPLICADOS (identificados):**
- `hybrid_engine_v6.py` vs `hybrid_assassin_fusion.py` vs `playwright_engine_v2.py` (→ Consolidar 3 en 1)
- `profile_manager.py` vs `profile_manager_v2.py` (→ Mantener solo uno)
- `runner/state_machine.py` vs `runtime/state_machine.py` (→ Eliminar duplicado)
- `curl_client.py` vs `tls_client_vtex.py` vs `vtex_client.py` (→ Consolidar 3 en 1)

**Documentación EXISTENTE (80+ .md):**
- Mayormente work notes / diagnostic files de debugging
- NO son documentación oficial
- → Mover a `docs/ARCHIVE/` o eliminar
- Mantener solo: `README.md`, `ARQUITECTURA.md`, `API.md`

---

## CONTEXTO TÉCNICO (Para ayudarte)

**Stack:**
- Python 3.8+
- Playwright 1.40.0 (primary web automation)
- Selenium 4.15.2 (backup)
- CustomTkinter 5.2.0 (GUI)
- WebSocket + Chrome Remote Debugging Protocol (CDP)
- tls-client 1.7.1 (CloudFlare bypass)

**Patrones Usados:**
- Master/Slave profile pattern
- State machine (NO_AUTH → READY → EXECUTING)
- WebSocket CDP for browser control
- JavaScript injection for React interaction

---

## ENVÍO PARA AUDITORÍA

Una vez que me des todo lo anterior, yo me encargaré de:
1. ✅ Ejecutar la eliminación de archivos sin riesgo
2. ✅ Consolidar engines/vtex con fusiones de código
3. ✅ Actualizar imports en cascada
4. ✅ Testear que todo sigue funcionando
5. ✅ Commit final con estructura limpia

