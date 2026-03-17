#!/usr/bin/env python3
"""
💀 FORCE_LOGIN.PY - PROTOCOLO DE FUERZA BRUTA

El log miente: dice "Chrome opened" pero tú ves el escritorio vacío.

Razones:
  ❌ Rutas relativas que Windows no resuelve
  ❌ Procesos zombie de Chrome invisibles
  ❌ Permisos bloqueados
  ❌ Rutas mal construidas

Solución: RUTAS ABSOLUTAS + SUBPROCESS DIRECTO + ERROR REPORTING

Este script:
  ✅ Construye ruta ABSOLUTA (no relativa)
  ✅ Verifica que exista
  ✅ Busca Chrome en rutas estándar
  ✅ Lanza con Popen (no blocking)
  ✅ Captura TODOS los errores

USO:
  python force_login.py
  (Cambia CUENTA_OBJETIVO si quieres otra cuenta)
"""

import subprocess
import os
import sys
import time

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚙️ CONFIGURACIÓN - EDITA ESTO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CUENTA_OBJETIVO = "cuenta2"  # ← Cambiar a la cuenta que quieras
URL_LOGIN = "https://www.nike.cl/login"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def log(msg, prefix=""):
    """Log con timestamp"""
    print(f"{prefix} {msg}")


def forzar_login():
    """
    PROTOCOLO DE FUERZA BRUTA
    
    1. Ruta ABSOLUTA (no relativa)
    2. Verifica que existe
    3. Busca Chrome
    4. LANZA CON POPEN
    5. Captura errores
    """
    
    print("\n" + "=" * 70)
    log("💀 PROTOCOLO DE FUERZA BRUTA ACTIVADO", "")
    print("=" * 70)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PASO 1: CONSTRUIR RUTA ABSOLUTA
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print("\n[PASO 1] Construyendo ruta ABSOLUTA...")
    
    # Obtener el directorio actual (debería ser nike_bot_pro/)
    base_dir = os.getcwd()
    log(f"Base directory: {base_dir}", "   ")
    
    # Construir la ruta del perfil
    profile_path = os.path.join(base_dir, "auth", CUENTA_OBJETIVO, "profile_pw")
    
    # Convertir a absoluta (resuelve . y .. y todo eso)
    abs_profile_path = os.path.abspath(profile_path)
    
    print(f"\n   Ruta solicitada: auth/{CUENTA_OBJETIVO}/profile_pw")
    print(f"   Ruta absoluta:   {abs_profile_path}")
    print(f"\n   ✅ RUTA ABSOLUTA CONSTRUIDA")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PASO 2: VERIFICA QUE LA CARPETA EXISTE (O CRÉALA)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print("\n[PASO 2] Verificando/creando carpeta del perfil...")
    
    if os.path.exists(abs_profile_path):
        size = os.path.getsize(abs_profile_path)
        log(f"✅ Carpeta EXISTS: {abs_profile_path}", "   ")
        log(f"   Tamaño: {size} bytes", "   ")
    else:
        log(f"⚠️  Carpeta NO EXISTE, creando...", "   ")
        try:
            os.makedirs(abs_profile_path, exist_ok=True)
            log(f"✅ Carpeta CREADA", "   ")
        except Exception as e:
            log(f"❌ ERROR creando carpeta: {e}", "   ")
            return False
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PASO 3: BUSCAR CHROME.EXE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print("\n[PASO 3] Buscando chrome.exe...")
    
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    ]
    
    chrome_exe = None
    for path in chrome_paths:
        log(f"   Buscando: {path}", "   ")
        if os.path.exists(path):
            chrome_exe = path
            log(f"✅ ENCONTRADO", "   ")
            break
    
    if not chrome_exe:
        print("\n❌ FATAL: chrome.exe NO ENCONTRADO en rutas estándar")
        print("\n   Rutas buscadas:")
        for p in chrome_paths:
            print(f"     • {p}")
        print("\n   Soluciones:")
        print("     1. Instala Chrome desde google.com/chrome")
        print("     2. O verifica que está en una de esas rutas")
        return False
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PASO 4: CONSTRUIR COMANDO
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print("\n[PASO 4] Construyendo comando...")
    
    cmd = [
        chrome_exe,
        f"--user-data-dir={abs_profile_path}",
        "--no-first-run",
        "--no-default-browser-check",
        "--start-maximized",
        URL_LOGIN,
    ]
    
    print("\n   Comando:")
    print(f"   {chrome_exe}")
    print(f"   --user-data-dir={abs_profile_path}")
    print(f"   --no-first-run")
    print(f"   --no-default-browser-check")
    print(f"   --start-maximized")
    print(f"   {URL_LOGIN}")
    
    print(f"\n   ✅ COMANDO CONSTRUIDO")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PASO 5: LANZAR CHROME CON POPEN
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print("\n[PASO 5] Lanzando Chrome...")
    
    try:
        process = subprocess.Popen(cmd)
        pid = process.pid
        log(f"✅ CHROME LANZADO (PID: {pid})", "   ")
        
        print("\n" + "=" * 70)
        print("✅ PROTOCOLO COMPLETADO EXITOSAMENTE")
        print("=" * 70)
        
        print("\n👉 PRÓXIMAS ACCIONES:")
        print("   1. Chrome debería estar abriendo AHORA")
        print("   2. Si ves la ventana: ¡ÉXITO!")
        print("   3. Loguéate en Nike")
        print("   4. Espera a ver 'Hola, [Tu Nombre]'")
        print("   5. CIERRA Chrome (con la X)")
        print("   6. El perfil se habrá guardado\n")
        
        return True
        
    except FileNotFoundError as e:
        log(f"❌ ERROR: Archivo no encontrado: {e}", "   ")
        return False
    except PermissionError as e:
        log(f"❌ ERROR: Permiso denegado: {e}", "   ")
        return False
    except Exception as e:
        log(f"❌ ERROR DESCONOCIDO: {e}", "   ")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "🔓 FORCE_LOGIN - PROTOCOLO ABSOLUTO" + " " * 19 + "║")
    print("╚" + "═" * 68 + "╝")
    
    print(f"\nCuenta objetivo: {CUENTA_OBJETIVO}")
    print(f"URL login: {URL_LOGIN}\n")
    
    success = forzar_login()
    
    if not success:
        print("\n❌ El protocolo falló. Revisa los errores arriba.")
        return 1
    
    print("\n⏳ Esperando 3 segundos para que Chrome se estabilice...")
    time.sleep(3)
    
    print("✅ Completado. Chrome está abierto.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
