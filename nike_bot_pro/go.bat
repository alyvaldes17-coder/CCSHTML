@echo off
echo 🛑 Matando Chrome...
taskkill /F /IM chrome.exe >nul 2>&1
timeout /t 1 /nobreak

echo 🛑 Matando Python...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 1 /nobreak

echo 🟢 Limpio. Abriendo bot...
cd /d "c:\Users\beriann\Documents\Repos\nikebotprofuncionalv1\nike_bot_pro"
python.exe main.py
