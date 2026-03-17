@echo off
REM ==============================================================================
REM SCRIPT DE LIMPIEZA ARQUITECTÓNICA — nike_bot_pro
REM ==============================================================================
REM Ejecuta las 3 FASES de refactoring en orden
REM FASE 0: Preparación
REM FASE 1: Eliminación (85 archivos)
REM FASE 2: Consolidación (fusiones)
REM FASE 3: Reorganización (movimientos)
REM ==============================================================================

setlocal enabledelayedexpansion

cd /d "%~dp0nike_bot_pro"

echo.
echo ============================================================
echo  AUDITORÍA ARQUITECTÓNICA Nike Bot Pro
echo ============================================================
echo.
echo Este script va a ELIMINAR 85 archivos redundantes
echo y REORGANIZAR ~51 archivos a nuevas carpetas.
echo.
echo Ubicación: %CD%
echo.
pause

REM ==============================================================================
REM FASE 0: PREPARACIÓN
REM ==============================================================================
echo.
echo [FASE 0] PREPARACIÓN — Crear estructura de carpetas...
echo.

mkdir scripts\setup 2>nul
mkdir scripts\auth 2>nul
mkdir scripts\maintenance 2>nul
mkdir scripts\play 2>nul
mkdir scripts\drops 2>nul
mkdir scripts\army 2>nul
mkdir scripts\checks 2>nul
mkdir scripts\chrome 2>nul
mkdir scripts\stock 2>nul
mkdir scripts\seeding 2>nul
mkdir scripts\monitoring 2>nul
mkdir scripts\quick 2>nul
mkdir scripts\fixes 2>nul
mkdir scripts\payment 2>nul
mkdir scripts\tools 2>nul

mkdir docs\examples 2>nul
mkdir docs\archive 2>nul

mkdir engines\experimental 2>nul

mkdir profiles 2>nul

echo ✅ Carpetas creadas.
pause

REM ==============================================================================
REM FASE 1: ELIMINACIÓN (85 archivos)
REM ==============================================================================
echo.
echo [FASE 1] ELIMINACIÓN — Borrando archivos redundantes/diagnóstico...
echo.

REM DEL RAÍZ — Test / Diagnóstico
echo - Eliminando test_*.py y diagnósticos...
for /f "delims=" %%F in ('dir /b test_*.py 2^>nul') do del "%%F"
for /f "delims=" %%F in ('dir /b verify_*.py 2^>nul') do del "%%F"
for /f "delims=" %%F in ('dir /b validate_*.py 2^>nul') do del "%%F"
for /f "delims=" %%F in ('dir /b DIAGNOSTICO_*.py 2^>nul') do del "%%F"
for /f "delims=" %%F in ('dir /b DEBUG_*.py 2^>nul') do del "%%F"

del CHROME_DIRECTO_SIN_FILTROS.py 2>nul
del checklist_threading_fix.py 2>nul
del fix_emojis.py 2>nul
del TEST_MULTI_CUENTA.py 2>nul
del TEST_FLUJO_FINAL.py 2>nul

REM DEL RAÍZ — Versiones viejas
echo - Eliminando versiones antiguas (v2, old, etc)...
del profile_manager_v2.py 2>nul
del play_v1_0.py 2>nul

REM DEL ENGINES — Versiones viejas
echo - Eliminando versiones viejas de engines...
del engines\playwright_engine.py 2>nul
del engines\playwright_engine_v2.py 2>nul
del engines\playwright_engine_v3.py 2>nul
del engines\hybrid_assassin_cdp_puro.py 2>nul
del engines\hybrid_assassin_cdp_puro_v2.py 2>nul
del engines\hybrid_assassin_cdp_puro_v7.py 2>nul
del engines\hybrid_assassin_cdp_puro_v8.py 2>nul
del engines\hybrid_assassin_cdp_puro_v9.py 2>nul
del engines\hybrid_assassin_cdp_puro_v10.py 2>nul
del engines\hybrid_assassin_cdp_puro_v11.py 2>nul
del engines\hybrid_assassin_cdp_puro_v13.py 2>nul

REM DEL RUNTIME — Duplicados
echo - Eliminando duplicados en runtime...
del runtime\state_machine.py 2>nul
del runtime\worker_fixed.py 2>nul

REM DEL RUNNER — Duplicados
echo - Eliminando duplicados en runner...
del runner\controller.py 2>nul

REM DEL WORKER
echo - Eliminando worker duplicado...
rmdir /s /q worker 2>nul

REM DEL UI — Viejos
echo - Eliminando versiones viejas UI...
del ui\app_old.py 2>nul
del ui\app_v0_9_simple.py 2>nul

REM DEL CONTROLLER
echo - Eliminando controller duplicado...
rmdir /s /q controller 2>nul

echo ✅ FASE 1 completada — 85 archivos eliminados.
echo.
pause

REM ==============================================================================
REM FASE 2: CONSOLIDACIÓN — FUSIONES DE CÓDIGO
REM ==============================================================================
echo.
echo [FASE 2] CONSOLIDACIÓN — Fusionando código duplicado...
echo.
echo ⚠️  MANUAL: Los cambios de código deben hacerse en VS Code:
echo    1. Fusionar hybrid_engine_v6.py + hybrid_assassin_fusion.py
echo       → Crear engines\engine.py (desde hybrid_engine_v6.py)
echo       → Agregar métodos de hybrid_assassin_fusion
echo       → Eliminar hybrid_engine_v6.py, hybrid_assassin_fusion.py
echo.
echo    2. Fusionar vtex/curl_client.py + tls_client_vtex.py + vtex_client.py
echo       → Crear vtex\client.py (desde curl_client.py)
echo       → Agregar métodos de tls_client_vtex y vtex_client
echo       → Eliminar tls_client_vtex.py, vtex_client.py
echo.
echo    3. Actualizar imports en runtime\bot_controller.py:
echo       from engines.hybrid_engine_v6 → from engines.engine
echo       from engines.hybrid_assassin_fusion → (mover al nuevo engine.py)
echo.
echo ✅ Esperar instrucciones para completar FASE 2
echo.
pause

REM ==============================================================================
REM FASE 3: REORGANIZACIÓN — MOVER A scripts/, docs/, profiles/
REM ==============================================================================
echo.
echo [FASE 3] REORGANIZACIÓN — Moviendo archivos a carpetas...
echo.

REM MOVER A scripts/setup/
echo - Moviendo setup scripts...
move setup_*.py scripts\setup\ 2>nul

REM MOVER A scripts/auth/
echo - Moviendo auth scripts...
move login_runner.py scripts\auth\ 2>nul
move force_login.py scripts\auth\ 2>nul
move fix_login.py scripts\auth\ 2>nul
for /f "delims=" %%F in ('dir /b tools\*login*.py 2^>nul') do move "tools\%%F" scripts\auth\ 2>nul
for /f "delims=" %%F in ('dir /b tools\*cookie*.py 2^>nul') do move "tools\%%F" scripts\auth\ 2>nul

REM MOVER A scripts/maintenance/
echo - Moviendo maintenance scripts...
move profile_cleanup.py scripts\maintenance\ 2>nul
move force_check.py scripts\maintenance\ 2>nul
move cleanup_lockfiles.py scripts\maintenance\ 2>nul

REM MOVER A scripts/play/
echo - Moviendo play scripts...
move play_runner.py scripts\play\ 2>nul

REM MOVER A scripts/drops/
echo - Moviendo drops scripts...
move drops_*.py scripts\drops\ 2>nul
move multi_drops.py scripts\drops\ 2>nul

REM MOVER A scripts/army/
echo - Moviendo army scripts...
move main_army.py scripts\army\ 2>nul

REM MOVER A scripts/checks/
echo - Moviendo check scripts...
move check_*.py scripts\checks\ 2>nul
move checklist_threading_fix.py scripts\checks\ 2>nul
move preflight_check.py scripts\checks\ 2>nul
move preflight_test.py scripts\checks\ 2>nul

REM MOVER A scripts/chrome/
echo - Moviendo chrome scripts...
move chrome_launcher_simple.py scripts\chrome\ 2>nul
move find_chrome_port.py scripts\chrome\ 2>nul
move CHROME_DIRECTO_SIN_FILTROS.py scripts\chrome\ 2>nul
for /f "delims=" %%F in ('dir /b utils\chrome*.py 2^>nul') do move "utils\%%F" scripts\chrome\ 2>nul

REM MOVER A scripts/stock/
echo - Moviendo stock scripts...
move engines\nike_stock_checker.py scripts\stock\ 2>nul
for /f "delims=" %%F in ('dir /b tools\*stock*.py 2^>nul') do move "tools\%%F" scripts\stock\ 2>nul
for /f "delims=" %%F in ('dir /b utils\stock*.py 2^>nul') do move "utils\%%F" scripts\stock\ 2>nul

REM MOVER A scripts/seeding/
echo - Moviendo seeding scripts...
move pdp_seeder.py scripts\seeding\ 2>nul

REM MOVER A scripts/monitoring/
echo - Moviendo monitoring scripts...
move monitor_logs.py scripts\monitoring\ 2>nul

REM MOVER A scripts/quick/
echo - Moviendo quick test scripts...
move quick_*.py scripts\quick\ 2>nul
move PRUEBA_FLUJO_COMPLETO.py scripts\quick\ 2>nul

REM MOVER A scripts/payment/
echo - Moviendo payment scripts...
for /f "delims=" %%F in ('dir /b tools\*payment*.py 2^>nul') do move "tools\%%F" scripts\payment\ 2>nul

REM MOVER A scripts/tools/
echo - Moviendo tools varios...
move engines\dirty_tools.py scripts\tools\ 2>nul

REM MOVER A docs/examples/
echo - Moviendo ejemplos a docs...
move example_*.py docs\examples\ 2>nul
move ejemplo_*.py docs\examples\ 2>nul
move HANDOVER_FINAL.py docs\examples\ 2>nul
for /f "delims=" %%F in ('dir /b docs\*.py 2^>nul') do move "docs\%%F" docs\examples\ 2>nul

REM MOVER A profiles/
echo - Moviendo profile manager...
move profile_manager.py profiles\ 2>nul
ren profiles\profile_manager.py manager.py 2>nul

REM LIMPIAR tools/ si está vacío
if exist tools (
    dir /b tools | find "." >nul
    if errorlevel 1 rmdir tools
)

echo ✅ FASE 3 completada — ~51 archivos reorganizados.
echo.

REM ==============================================================================
REM RESUMEN FINAL
REM ==============================================================================
echo.
echo ============================================================
echo  RESUMEN FINAL
echo ============================================================
echo.
echo ✅ 85 archivos eliminados
echo ✅ Carpetas reorganizadas (scripts/, docs/examples/, profiles/)
echo.
echo ⚠️  PRÓXIMOS PASOS MANUALES:
echo    1. Ejecutar FASE 2 (consolidación de código en VS Code)
echo    2. Actualizar imports en runtime\bot_controller.py
echo    3. Actualizar imports en main.py
echo    4. Ejecutar: python main.py (para probar que arranca)
echo    5. Ejecutar: pytest tests\test_imports.py
echo    6. Commit git "Refactor: limpieza arquitectónica completa"
echo.
echo ============================================================
echo.
pause

echo.
echo 🎉 ¡FASE 1 y 3 completadas! Ahora edita código para FASE 2.
echo.
timeout /t 5

