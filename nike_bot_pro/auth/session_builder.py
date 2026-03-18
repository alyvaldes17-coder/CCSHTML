"""Builder de sesiones requests — FUENTE DE VERDAD = profile_pw/

Estrategia (definitiva):
1. Intenta leer cookies del perfil Chromium (profile_pw/Default/Network/Cookies)
2. Si no existen → fallback a tokens.json (legacy, opcional)
3. Nunca falla solo por extensión
"""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Optional

import httpx  # Reemplaza requests para mejor compatibilidad HTTP/2
import base64
import tempfile
import shutil
try:
    import win32crypt  # pywin32
    from Crypto.Cipher import AES  # pycryptodome
except Exception:
    win32crypt = None
    AES = None

from config.settings import BASE_URL

PROFILE_ROOT = Path("profile_pw")


def _get_chrome_key(local_state_path: Path) -> Optional[bytes]:
    """Obtiene la clave AES de Chrome desde Local State (Windows)."""
    try:
        if not local_state_path.exists():
            return None
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        enc_key_b64 = local_state.get("os_crypt", {}).get("encrypted_key")
        if not enc_key_b64:
            return None
        enc_key = base64.b64decode(enc_key_b64)[5:]  # strip "DPAPI"
        if win32crypt is None:
            return None
        key = win32crypt.CryptUnprotectData(enc_key, None, None, None, 0)[1]
        return key
    except Exception:
        return None


def _decrypt_cookie(encrypted_value: bytes, key: Optional[bytes]) -> Optional[str]:
    """Desencripta cookie Chrome (AES-GCM v10/v11 o DPAPI)."""
    try:
        if encrypted_value is None:
            return None
        if encrypted_value.startswith(b"v10") or encrypted_value.startswith(b"v11"):
            if AES is None or key is None:
                return None
            iv = encrypted_value[3:15]
            payload = encrypted_value[15:]
            ct, tag = payload[:-16], payload[-16:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted = cipher.decrypt_and_verify(ct, tag)
            # Chrome v10+ agrega 32 bytes de nonce al inicio; buscar contenido válido (JWT típicamente empieza con "ey")
            full = decrypted.decode("utf-8", errors="ignore")
            idx = full.find("ey")  # JWT standard
            if idx > 0:
                return full[idx:]
            # Si no hay JWT, retornar lo desencriptado limpio
            return full.lstrip('\x00').strip()
        # Fallback DPAPI
        if win32crypt is not None:
            try:
                return win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode()
            except Exception:
                return None
        return None
    except Exception:
        return None


def extract_cookies_from_chromium_db(cookies_db_path: str, local_state_path: Path) -> dict:
    """
    Lee cookies del archivo Chromium Cookies (SQLite), desencriptando en Windows.
    Retorna dict: {name: value} para cookies críticas Nike/VTEX.
    """
    try:
        if not os.path.exists(cookies_db_path):
            return {}

        # Copiar DB a temp para evitar locks
        temp_db = Path(tempfile.gettempdir()) / "Cookies_temp.db"
        try:
            shutil.copy2(cookies_db_path, temp_db)
            db_path = str(temp_db)
        except Exception:
            db_path = cookies_db_path

        # Obtener AES key (Windows)
        key = _get_chrome_key(local_state_path)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT host_key, name, value, encrypted_value FROM cookies WHERE host_key LIKE '%nike%' OR host_key LIKE '%vtex%' ORDER BY host_key DESC"
        )

        cookies = {}
        rows = cursor.fetchall()
        conn.close()

        def _normalize(name: str, v: str) -> str:
            # Quita basura inicial/control chars y recorta heurísticamente
            v2 = ''.join(ch for ch in v if ch >= ' ')
            if name in ("VtexIdclientAutCookie_nikeclprod", "vtex_session", "vtex_segment"):
                idx = v2.find("ey")
                if idx > 0:
                    v2 = v2[idx:]
            return v2

        for host_key, name, value, encrypted_value in rows:
            # Seleccionar valor correcto
            cookie_val = value or None
            if (not cookie_val) and encrypted_value:
                cookie_val = _decrypt_cookie(encrypted_value, key)

            if not cookie_val:
                continue

            # Guardar solo críticas (PREFERIR .www.nike.cl sobre otros)
            if name in [
                "VtexIdclientAutCookie_nikeclprod",
                "vtex_session",
                "vtex_segment",
            ]:
                # Si ya existe, solo reemplazar si el host actual es .www.nike.cl
                if name in cookies:
                    if ".www.nike.cl" not in host_key and ".www.nike.cl" in str(cookies.get(f"_{name}_host", "")):
                        continue  # Mantener el .www.nike.cl
                
                cookies[name] = _normalize(name, cookie_val)
                cookies[f"_{name}_host"] = host_key  # Guardar host para debug

        # Limpiar claves de debug
        final_cookies = {k: v for k, v in cookies.items() if not k.startswith("_")}
        return final_cookies

    except Exception as e:
        print(f"[-] No se pudieron leer cookies de Chromium: {e}")
        return {}


def _build_session_from_cookies(cookies_dict: dict) -> httpx.Client:
    """Construye cliente httpx desde dict de cookies."""
    # Crear cliente con HTTP/2 habilitado
    client = httpx.Client(http2=True, timeout=30.0, follow_redirects=True)
    
    client.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "es-CL,es;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": BASE_URL.rstrip("/") + "/",
        "Origin": BASE_URL.rstrip("/"),
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    })

    def _ascii(v: str) -> str:
        try:
            return v.encode("ascii", "ignore").decode("ascii")
        except Exception:
            return "".join(ch for ch in v if ord(ch) < 128)

    # Agregar cookies al cliente
    for name, value in cookies_dict.items():
        if not value:
            continue
        val_ascii = _ascii(str(value))
        client.cookies.set(name, val_ascii)

    return client


def build_requests_session(account_identifier: str) -> httpx.Client:
    """
    Crea cliente httpx para la cuenta.

    Estrategia (PRIORIDAD):
    1. PRIMERO: Cookies del perfil Chromium (profile_pw/Default/Network/Cookies)
    2. FALLBACK: tokens.json en auth/<cuenta>/
    3. Si ambos fallan -> excepción clara

    account_identifier: nombre de cuenta (ej. "trysnkrs20@gmail.com") o ruta absoluta.
    
    Retorna: httpx.Client con HTTP/2 habilitado y cookies configuradas.
    """

    # Normalizar account_identifier
    if os.path.isdir(account_identifier):
        account_path = account_identifier
        account_name = os.path.basename(account_path.rstrip("/\\"))
    else:
        account_name = account_identifier
        account_path = os.path.join("auth", account_identifier)

    print(f"[{account_name}] Construyendo sesión requests...")

    # 🔷 ESTRATEGIA 1: Leer cookies del perfil Chromium (PRIMERO)
    cookies_db = PROFILE_ROOT / "Default" / "Network" / "Cookies"
    local_state = PROFILE_ROOT / "Local State"
    if cookies_db.exists():
        print(f"[{account_name}] [+] Leyendo cookies del perfil...")
        cookies = extract_cookies_from_chromium_db(str(cookies_db), local_state)

        if cookies:
            print(f"[{account_name}] [OK] Sesión creada desde perfil Chromium")
            return _build_session_from_cookies(cookies)
        else:
            print(f"[{account_name}] [-] Perfil existe pero sin cookies Nike/VTEX")

    # 🔷 FALLBACK: tokens.json (legacy, opcional)
    tokens_file = os.path.join(account_path, "tokens.json")
    if os.path.exists(tokens_file):
        try:
            with open(tokens_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validar campos mínimos
            auth_cookie = data.get("auth_cookie")
            vtex_session = data.get("vtex_session")
            vtex_segment = data.get("vtex_segment")

            if auth_cookie and vtex_session and vtex_segment:
                print(f"[{account_name}] [OK] Sesión creada desde tokens.json")
                cookies = {
                    "VtexIdclientAutCookie_nikeclprod": auth_cookie,
                    "vtex_session": vtex_session,
                    "vtex_segment": vtex_segment,
                }
                return _build_session_from_cookies(cookies)
        except Exception as e:
            print(f"[{account_name}] [-] tokens.json inválido: {e}")

    # Ambas estrategias fallaron
    raise RuntimeError(
        f"\nError: No se pudo crear sesión para {account_name}:\n"
        f"   - Perfil (profile_pw/Default/Network/Cookies) no existe o sin cookies\n"
        f"   - tokens.json incompleto o inexistente\n"
        f"\n   Solucion:\n"
        f"   1. Ejecuta: python auth/auth.py {account_name}\n"
        f"   2. Luego: python run.py\n"
    )

