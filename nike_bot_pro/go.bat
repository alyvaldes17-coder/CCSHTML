@echo off
echo 🛑 Matando Chrome...
taskkill /F /IM chrome.exe >nul 2>&1
timeout /t 1 /nobreak

echo 🛑 Matando Python...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 1 /nobreak

echo 🟢 Limpio. Abriendo bot...
cd /d "%~dp0"

if exist ".venv312\Scripts\python.exe" (
	.venv312\Scripts\python.exe main.py
	goto :eof
)

if exist ".venv\Scripts\python.exe" (
	.venv\Scripts\python.exe main.py
	goto :eof
)

py main.py
