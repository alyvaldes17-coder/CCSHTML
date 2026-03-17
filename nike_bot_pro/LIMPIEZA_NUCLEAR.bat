@echo off
REM 🧨 LIMPIEZA NUCLEAR - Mata TODO Chrome fantasma
REM Ejecuta esto ANTES de usar drops_uno.py

echo.
echo 🧨 ===== LIMPIEZA NUCLEAR DE CHROME =====
echo.

REM 1. Matar todos los procesos Chrome
echo 🔪 Matando todos los procesos Chrome...
taskkill /F /IM chrome.exe /T >nul 2>&1

REM 2. Esperar a que se mueran completamente
echo ⏳ Esperando limpieza (3 segundos)...
timeout /t 3 /nobreak

REM 3. Verificar que no quedan Chrome
echo.
echo ✅ Verificando que Chrome está muerto...
tasklist | findstr /I "chrome"
if %errorlevel% equ 0 (
    echo 🔴 ADVERTENCIA: Aún hay Chrome abierto
) else (
    echo 🟢 OK: Chrome completamente muerto
)

echo.
echo ✅ LIMPIEZA COMPLETA
echo.
echo 📋 PRÓXIMO PASO:
echo    1. Abre una terminal
echo    2. Ejecuta: python drops_uno.py
echo    3. Presiona Opción 1 (Iniciar Chrome Stealth)
echo    4. Espera a que se cargue y loguéate
echo    5. Presiona Opción 2 (Vaciar)
echo.
pause
