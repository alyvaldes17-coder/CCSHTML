@echo off
REM kill_chrome.bat - MATA TODOS LOS PROCESOS DE CHROME

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║        💀 LIMPIEZA TOTAL: Matando procesos Chrome             ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

echo [1] Matando chrome.exe...
taskkill /F /IM chrome.exe /T 2>nul

if %ERRORLEVEL% EQU 0 (
    echo ✅ Chrome fue matado (habia procesos activos)
) else (
    echo ✅ Chrome ya no estaba corriendo (limpio)
)

echo.
echo [2] Matando chromedriver.exe (si existe)...
taskkill /F /IM chromedriver.exe /T 2>nul

if %ERRORLEVEL% EQU 0 (
    echo ✅ Chromedriver fue matado
) else (
    echo ✅ Chromedriver no estaba corriendo
)

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                   ✅ LIMPIEZA COMPLETADA                      ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.
echo Ahora puedes ejecutar:
echo   python force_login.py
echo.
pause
