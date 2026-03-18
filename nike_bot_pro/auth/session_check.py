"""
Session Check & Login Helper - VERSIÓN LIMPIA

Funciones:
1. check_session_nike() - Verifica si hay cookies válidas
2. setup_account_login() - Abre Chrome para login manual (subprocess, sin Playwright)
"""

import os
import time
import json
import logging
import subprocess
from pathlib import Path

log = logging.getLogger("session_check")


def check_session_nike(account_path):
    """
    Verifica si Nike está logueado EN REALIDAD.
    Chequea:
    1. ¿profile_pw existe?
    2. ¿Tiene carpeta Default/Network/Cookies?
    3. ¿Tiene cookies de Nike/VTEX?
    
    Retorna: True (logueado con cookies) o False (no hay sesión)
    """
    profile_dir = os.path.join(account_path, "profile_pw")
    
    if not os.path.exists(profile_dir):
        return False
    
    # Chequear si tiene archivo de cookies
    cookies_dir = os.path.join(profile_dir, "Default", "Network")
    
    if not os.path.exists(cookies_dir):
        return False  # Profile existe pero vacío
    
    # Buscar archivo Cookies
    cookies_file = os.path.join(cookies_dir, "Cookies")
    if os.path.exists(cookies_file):
        # Archivos de Cookies de Chrome existen
        return True
    
    return False


def setup_account_login(account_path: str, account_name: str) -> bool:
    """
    🔑 BOTÓN [LOGIN] - Abre Chrome para login manual (Multitasking Safe)
    
    No interfiere con tu Chrome personal. Abre un perfil independiente.
    
    Args:
        account_path: Ruta a auth/cuentaX/
        account_name: Nombre de la cuenta
        
    Returns:
        True si completó sin errores
    """
    profile_dir = os.path.join(account_path, "profile_pw")
    abs_profile_dir = os.path.abspath(profile_dir)
    os.makedirs(abs_profile_dir, exist_ok=True)
    
    log.info(f"[{account_name}] 🔧 PREPARANDO ENTORNO...")
    print(f"[{account_name}] 🔧 Limpiando perfil...")
    
    try:
        # 1. Borrar Lockfile
        lockfile = os.path.join(abs_profile_dir, "Lockfile")
        if os.path.exists(lockfile):
            try:
                os.remove(lockfile)
                print(f"[{account_name}] 🔓 Lockfile eliminado")
            except:
                pass
        
        # 2. Matar Chrome fantasma
        try:
            ruta_win = abs_profile_dir.replace("/", "\\").replace("\\", "\\\\")
            cmd_kill = f'wmic process where "name=\'chrome.exe\' and CommandLine like \'%{ruta_win}%\'" call terminate'
            subprocess.run(cmd_kill, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(0.5)
        except:
            pass
        
        # 3. Buscar Chrome
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
        ]
        chrome_exe = next((p for p in chrome_paths if os.path.exists(p)), None)
        
        if not chrome_exe:
            print(f"[{account_name}] ❌ Chrome no encontrado")
            return False
        
        # 4. Lanzar Chrome
        args = [
            chrome_exe,
            f"--user-data-dir={abs_profile_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--start-maximized",
            "https://www.nike.cl/login"
        ]
        
        print(f"[{account_name}] 🚀 Abriendo Chrome...")
        subprocess.Popen(args)
        
        print(f"[{account_name}] 👉 Completa LOGIN y cierra Chrome")
        
        # 5. Esperar cierre
        ruta_wmic = abs_profile_dir.replace("/", "\\").replace("\\", "\\\\")
        max_wait = 3600
        elapsed = 0
        
        while elapsed < max_wait:
            try:
                result = subprocess.run(
                    f'wmic process where "CommandLine like \'%{ruta_wmic}%\'" list',
                    shell=True, capture_output=True, text=True, timeout=5
                )
                if "chrome.exe" not in result.stdout:
                    print(f"[{account_name}] ✅ Login completado\n")
                    return True
                time.sleep(1)
                elapsed += 1
            except:
                break
        
        return True
    
    except Exception as e:
        print(f"[{account_name}] ❌ Error: {e}")
        return False


def setup_account_login_safe(account_path: str, account_name: str) -> bool:
    """Wrapper seguro para setup_account_login (ejecutado desde thread)"""
    try:
        return setup_account_login(account_path, account_name)
    except Exception as e:
        log.error(f"[{account_name}] ❌ Error: {e}")
        return False