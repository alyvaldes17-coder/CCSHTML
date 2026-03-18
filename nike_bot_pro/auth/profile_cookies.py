import os
import json
import time
import tempfile
import subprocess
import sys
from playwright.sync_api import sync_playwright
from config.settings import AUTH_ROOT
from utils.zombie_killer import matar_zombies_del_perfil

def get_cookies_for_account(account_name):
    """
    Extrae cookies lanzando una instancia rápida de Chrome.
    Bypasea la encriptación DPAPI/App-Bound al usar el propio navegador.
    
    OPTIMIZACIÓN: Si se ejecuta desde Tkinter, usa archivo temp (via subprocess).
    Si se ejecuta desde CLI, usa Playwright directo.
    """
    # Opción 1: Intentar leer de archivo temp (si fue extraído via subprocess)
    temp_file = os.path.join(tempfile.gettempdir(), f"cookies_{account_name}.json")
    if os.path.exists(temp_file):
        try:
            print(f"[COOKIES] 📂 Leyendo cookies de archivo temp...")
            with open(temp_file, "r") as f:
                cookies = json.load(f)
            print(f"[COOKIES] ✅ {len(cookies)} cookies cargadas desde temp")
            # Limpiar archivo temp
            try:
                os.remove(temp_file)
            except:
                pass
            return cookies
        except Exception as e:
            print(f"[COOKIES] ⚠️ Error leyendo temp: {e}")
    
    # Opción 2: Extraer directamente (para CLI)
    # Manejo de argumentos (puede venir path o nombre)
    if "auth" in account_name or "\\" in account_name or "/" in account_name:
        # Es un path, intentamos deducir el nombre
        if "auth" in account_name:
            try:
                # Ejemplo: .../auth/cuenta2/profile_run -> cuenta2
                parts = account_name.replace("\\", "/").split("/")
                idx = parts.index("auth")
                if idx + 1 < len(parts):
                    account_name = parts[idx+1]
            except:
                pass
        else:
            # Fallback simple
            account_name = os.path.basename(account_name)

    # Definir ruta MAESTRA (Login)
    profile_path = os.path.join(AUTH_ROOT, account_name, "profile_login")
    profile_path = os.path.abspath(profile_path)
    
    print(f"[COOKIES] 🍪 Extrayendo vía Browser (Bypass Encriptación)...")
    print(f"[COOKIES] 📂 Perfil: {profile_path}")
    
    # --- CRÍTICO: Matar procesos Chrome zombie antes de abrir ---
    print(f"[COOKIES] 🧟 Limpiando zombies del perfil...")
    matar_zombies_del_perfil(profile_path)
    print(f"[COOKIES] ✅ Zombies eliminados")
    # ---------------------------------------------------------

    if not os.path.exists(profile_path):
        print(f"[COOKIES] ❌ Perfil no existe: {profile_path}")
        return {}

    cookies_dict = {}

    try:
        # Lanzamos Chrome Headless (Invisible)
        print(f"[COOKIES] ⏳ Abriendo Chrome headless...")
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=profile_path,
                channel="chrome",     # Usar Chrome real
                headless=True,        # Invisible
                args=[
                    "--no-sandbox"
                ]
            )
            
            print(f"[COOKIES] 🌐 Chrome abierto, extrayendo cookies...")
            # Obtener cookies nativas desencriptadas por Chrome
            raw_cookies = browser.cookies()
            
            count = 0
            for c in raw_cookies:
                # Filtrar solo las útiles para no llenar de basura
                if any(domain in c["domain"] for domain in ["nike", "vtex", "checkout"]):
                    cookies_dict[c["name"]] = c["value"]
                    count += 1
            
            print(f"[COOKIES] ✅ {count} cookies extraídas exitosamente.")
            browser.close()
            
    except Exception as e:
        print(f"[COOKIES] ⚠️ Error en extracción browser: {e}")
        # Intento de fallback: Si falla Playwright, retornamos vacío
        return {}

    return cookies_dict

# Test rápido
if __name__ == "__main__":
    import sys
    acc = sys.argv[1] if len(sys.argv) > 1 else "cuenta2"
    cks = get_cookies_for_account(acc)
    print(f"Resultado: {len(cks)} cookies")
    if "vtex_session" in cks:
        print("✅ vtex_session encontrada!")

