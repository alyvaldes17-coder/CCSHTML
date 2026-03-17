# 🗑️ CLEANUP FINAL - ARCHIVOS A ELIMINAR

**Ejecuta estos comandos para limpiar el repo.**

---

## ⚠️ IMPORTANTE

**Antes de ejecutar limpieza**:

1. Haz backup del repo
2. Verifica que no hay nada importante a eliminar
3. Ejecuta los comandos uno a uno
4. Valida que el sistema sigue funcionando

---

## Paso 1: Directorios COMPLETAMENTE innecesarios

```bash
# Windows (PowerShell)
Remove-Item -Recurse -Force runner/
Remove-Item -Recurse -Force controller/
Remove-Item -Recurse -Force manager/
Remove-Item -Recurse -Force worker/
Remove-Item -Recurse -Force engines/
Remove-Item -Recurse -Force vtex/

# O con command prompt
rmdir /s /q runner
rmdir /s /q controller
rmdir /s /q manager
rmdir /s /q worker
rmdir /s /q engines
rmdir /s /q vtex
```

**Estos directorios**:
- ❌ Viejo state machine (runner/)
- ❌ Viejo controller pattern (controller/)
- ❌ Viejo manager pattern (manager/)
- ❌ Viejo worker pattern (worker/)
- ❌ Viejos engines (engines/)
- ❌ Viejo VTEX module (vtex/)

**Después de eliminar**: El sistema sigue 100% funcional.

---

## Paso 2: Archivos específicos a eliminar

```bash
# Windows PowerShell
Remove-Item -Force check_syntax.py
Remove-Item -Force quick_check.py
Remove-Item -Force preflight_check.py
Remove-Item -Force pdp_seeder.py
Remove-Item -Force monitor_logs.py
Remove-Item -Force fix_emojis.py
Remove-Item -Force fix_login.py
Remove-Item -Force example_state_machine_usage.py

# O con command prompt
del check_syntax.py
del quick_check.py
del preflight_check.py
del pdp_seeder.py
del monitor_logs.py
del fix_emojis.py
del fix_login.py
del example_state_machine_usage.py
```

---

## Paso 3: Archivos de tests antiguos

```bash
# Eliminar tests viejos
Remove-Item -Force test_*.py (excepto los core)

# Los que SÍ mantienes:
# - quick_test_threading_fix.py (debug tool válido)

# Los que ELIMINAS:
# - test_bank_fintoc_final.py
# - test_browser.py
# - Y otros test_*.py viejos
```

---

## Paso 4: Documentación histórica (OPCIONAL)

Si quieres solo lo FINAL, elimina estos (son históricos):

```bash
Remove-Item -Force FLUJO_CONGELADO_V0_9.md
Remove-Item -Force COMIENZA_AQUI_8ESTADOS.md
Remove-Item -Force COMIENZA_AQUI.txt
Remove-Item -Force IMPLEMENTACION_FLUJO_V0_9_COMPLETADA.md
Remove-Item -Force CONGELACION_V0_9_AUDITORIA_COMPLETA.md
Remove-Item -Force CONGELACION_FINAL_RESUMEN.md
Remove-Item -Force V0_9_FROZEN_EXECUTION_PLAN.md
Remove-Item -Force LA_VERDAD_DEL_SISTEMA.md
Remove-Item -Force ACCION_INMEDIATA_DEBUG.md
Remove-Item -Force ACCIONES_RECOMENDADAS_AHORA.md
Remove-Item -Force HERRAMIENTAS_DEBUG_V0_9.md
Remove-Item -Force ACCION_INMEDIATA_DEBUG.md
Remove-Item -Force LOGIN_TROUBLESHOOTING_V0_9.md
Remove-Item -Force STATUS_FINAL_V0_9.md
Remove-Item -Force ENTREGA_FINAL_V0_9.md
Remove-Item -Force README_V0_9.md
Remove-Item -Force FINAL_CONCLUSIONES.md
Remove-Item -Force INDICE_V0_9_COMPLETO.md
Remove-Item -Force README_FINAL.md

# Y otros FLUJO_*, ANALISIS_*, ARQUITECTURA_*, etc
```

**Nota**: Estos documentos son referencia histórica. Puedes eliminarlos o mantenerlos.

**MANTENER SIEMPRE**:
- PSEUDOCODIGO_FINAL.md
- ATC_EXACTO_LA_VERDAD.md
- FREEZE_QUE_SIGNIFICA.md
- QUE_BORRAR_CRITICO.md
- VERDAD_FINAL_SISTEMA.md
- CHECKLIST_EJECUCION_FINAL.md
- AUDITORIA_FINAL_ESTADO.md
- RESUMEN_EJECUTIVO_FINAL.md
- INDICE_DOCUMENTACION_FINAL.md
- CAMBIOS_FINALES_REALIZADOS.md
- README.md

---

## Paso 5: Archivos JSON de estado (OPCIONAL)

Si necesitas limpiar cookies/tokens:

```bash
Remove-Item -Force cookies_extracted.json
Remove-Item -Force session_token.json
Remove-Item -Force accounts.json (CUIDADO: contiene cuentas)

# MANTENER SIEMPRE:
# - accounts.json (tiene la config de cuentas)
```

---

## Paso 6: Verificación final

Después de limpiar, verifica:

```bash
# Buscar patrones prohibidos
grep -r "\.click.*cart" . --include="*.py"
# Debe retornar CERO

grep -r "seed" . --include="*.py"
# Debe retornar CERO (excepto en docs)

grep -r "monitor" . --include="*.py"
# Debe retornar CERO

# Verificar que archivos core existen
ls -la login_runner.py
ls -la profile_manager_v2.py
ls -la runtime/backend_vtex.py
ls -la runtime/multiprocessing_runner.py
ls -la ui/app_v0_9_simple.py

# Syntax check
python -m py_compile runtime/*.py
python -m py_compile ui/*.py
# Debe retornar sin errores
```

---

## Estructura FINAL (después de limpieza)

```
nike_bot_pro/
├── login_runner.py
├── profile_manager_v2.py
├── accounts.json
├── cookies_extracted.json (opcional)
├── session_token.json (opcional)
├── auth/
│   ├── cuenta1/
│   │   ├── profile_login/
│   │   └── profile_run/
│   └── ...
├── runtime/
│   ├── __init__.py
│   ├── backend_vtex.py
│   ├── process_states.py
│   ├── multiprocessing_runner.py
│   └── state_bus.py
├── ui/
│   ├── __init__.py
│   ├── play_launcher.py
│   ├── state_listener.py
│   └── app_v0_9_simple.py
├── profile_cleanup.py
├── diagnose_login_issue.py
├── quick_test_threading_fix.py
├── .gitignore
├── README.md
├── PSEUDOCODIGO_FINAL.md
├── ATC_EXACTO_LA_VERDAD.md
├── FREEZE_QUE_SIGNIFICA.md
├── QUE_BORRAR_CRITICO.md
├── VERDAD_FINAL_SISTEMA.md
├── CHECKLIST_EJECUCION_FINAL.md
├── AUDITORIA_FINAL_ESTADO.md
├── RESUMEN_EJECUTIVO_FINAL.md
├── INDICE_DOCUMENTACION_FINAL.md
└── CAMBIOS_FINALES_REALIZADOS.md
```

---

## Checklist de limpieza

```
[ ] Backup del repo realizado
[ ] Directorios viejos eliminados (runner/, controller/, etc)
[ ] Archivos innecesarios eliminados
[ ] Tests viejos eliminados
[ ] Documentación histórica eliminada (opcional)
[ ] Búsqueda de "page.click" → 0 resultados
[ ] Búsqueda de "seed" → 0 resultados
[ ] Búsqueda de "monitor" → 0 resultados
[ ] Archivos core existen: login_runner.py ✅
[ ] Archivos core existen: runtime/ ✅
[ ] Archivos core existen: ui/ ✅
[ ] Syntax check → 0 errores
[ ] Sistema sigue funcionando ✅
```

---

## Comandos rápidos (Windows PowerShell)

```powershell
# Limpiar TODO de una vez
Remove-Item -Recurse -Force runner, controller, manager, worker, engines, vtex
Remove-Item -Force check_syntax.py, quick_check.py, preflight_check.py, pdp_seeder.py
Remove-Item -Force monitor_logs.py, fix_emojis.py, fix_login.py, example_state_machine_usage.py

# Verificar búsquedas
grep -r "\.click.*cart" . --include="*.py"
grep -r "seed" . --include="*.py"
grep -r "monitor" . --include="*.py"

# Syntax check
python -m py_compile runtime/*.py
python -m py_compile ui/*.py

# Test rápido
python ui/app_v0_9_simple.py
# (Cerrar con Ctrl+C)
```

---

## Comandos rápidos (Windows CMD)

```cmd
# Limpiar directorios
rmdir /s /q runner
rmdir /s /q controller
rmdir /s /q manager
rmdir /s /q worker
rmdir /s /q engines
rmdir /s /q vtex

# Limpiar archivos
del check_syntax.py
del quick_check.py
del preflight_check.py
del pdp_seeder.py
del monitor_logs.py
del fix_emojis.py
del fix_login.py
del example_state_machine_usage.py

# Syntax check
python -m py_compile runtime\*.py
python -m py_compile ui\*.py
```

---

## ¿Qué pasa después de limpiar?

**El sistema sigue siendo EXACTAMENTE el mismo.**

- ✅ 10 pasos del flujo idénticos
- ✅ Magic link exacto
- ✅ FREEZE funcionando
- ✅ UI igual
- ✅ Ejecución 100% igual

**Solo**: Sin código viejo/innecesario.

---

## ¿Qué si me arrepiento?

Simplemente restaura desde tu backup.

El repo estará igual que antes (pero con documentación nueva).

---

## Status después de limpiar

```
Archivos core: 9 (solo esenciales)
Debug tools: 3 (opcionales pero útiles)
Documentación: 10 (referencia)
Directorios viejos: 0 (eliminados)
Archivos innecesarios: 0 (eliminados)

Sistema: ✅ CONGELADO
Status: ✅ LISTO PARA DROPS
```

---

**Eso es TODO lo que necesitas.**

Sistema limpio. Código puro. Listo para ejecutar.

🚀
