#!/usr/bin/env python3
"""
login_runner.py - LOGIN manual con Chrome real

Después de que el usuario cierra Chrome, extrae el email automáticamente
desde el perfil y lo guarda en config.json.
"""
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from config.settings import AUTH_ROOT, CHROME_PATH


def _extraer_email_chrome(profile_login: str) -> str:
    """
    Intenta leer el email Nike desde el perfil Chrome.
    1. Login Data SQLite (Chrome guarda usuario/contraseña)
    2. Preferences JSON (cuentas Google sincronizadas)
    """
    # Opción 1: Login Data
    login_db = os.path.join(profile_login, "Default", "Login Data")
    if os.path.exists(login_db):
        try:
            tmp = os.path.join(tempfile.gettempdir(), "nike_ld_tmp.db")
            shutil.copy2(login_db, tmp)
            conn = sqlite3.connect(tmp)
            cur = conn.execute(
                "SELECT username_value FROM logins "
                "WHERE origin_url LIKE '%nike%' AND username_value LIKE '%@%' "
                "LIMIT 1"
            )
            row = cur.fetchone()
            conn.close()
            try:
                os.unlink(tmp)
            except Exception:
                pass
            if row and row[0] and "@" in row[0]:
                return row[0].strip()
        except Exception:
            pass

    # Opción 2: Preferences (cuenta Google)
    prefs = os.path.join(profile_login, "Default", "Preferences")
    if os.path.exists(prefs):
        try:
            with open(prefs, encoding="utf-8") as f:
                data = json.load(f)
            for acc in data.get("account_info", []):
                email = acc.get("email", "").strip()
                if email and "@" in email:
                    return email
        except Exception:
            pass

    return ""


def _guardar_email(account_path: str, email: str):
    """Guarda el email en config.json sin pisar otros campos."""
    cfg_path = os.path.join(account_path, "config.json")
    try:
        existing = {}
        if os.path.exists(cfg_path):
            with open(cfg_path, encoding="utf-8") as f:
                existing = json.load(f)
        existing["email"]      = email
        existing["nike_email"] = email
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
        print(f"[LOGIN] Email guardado: {email}")
    except Exception as e:
        print(f"[LOGIN] No se pudo guardar email: {e}")


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Uso: python login_runner.py <cuenta>")

    user = sys.argv[1]

    account_path  = os.path.join(AUTH_ROOT, user)
    profile_login = os.path.join(account_path, "profile_login")
    login_ok      = os.path.join(account_path, ".login_ok")

    os.makedirs(account_path, exist_ok=True)
    os.makedirs(profile_login, exist_ok=True)

    print("\n" + "=" * 70)
    print(f"[LOGIN] Abriendo Chrome para {user}")
    print("=" * 70)

    if not CHROME_PATH or not os.path.exists(CHROME_PATH):
        raise RuntimeError("[LOGIN] Chrome no encontrado")

    args = [
        CHROME_PATH,
        f"--user-data-dir={profile_login}",
        "--start-maximized",
        "--no-first-run",
        "--no-default-browser-check",
        "https://www.nike.cl/login",
    ]

    print("[LOGIN] Por favor loguéate en Nike.cl")
    print("[LOGIN] Cuando termines, CIERRA Chrome")

    try:
        proc = subprocess.Popen(args)
    except Exception as e:
        print(f"[ERROR] No se pudo abrir Chrome: {e}")
        return False

    print("[LOGIN] Esperando que cierres Chrome...")
    while proc.poll() is None:
        time.sleep(1)

    print("[LOGIN] Chrome cerrado")

    # Extraer y guardar email automáticamente
    email = _extraer_email_chrome(profile_login)
    if email:
        _guardar_email(account_path, email)
    else:
        print("[LOGIN] ⚠️ No se pudo extraer email — agrégalo manualmente en Edit")

    # Crear .login_ok
    try:
        with open(login_ok, "w") as f:
            f.write("OK")
        print(f"[LOGIN] ✅ .login_ok creado")
        print("[SUCCESS] LOGIN completado")
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo crear .login_ok: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


