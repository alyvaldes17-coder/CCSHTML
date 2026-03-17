import subprocess
import os
import sys

# ==========================================
# CONFIGURA AQUÍ LA CUENTA
CUENTA_OBJETIVO = "auth/cuenta2" 
# ==========================================

def forzar_inspeccion():
    print(f"🕵️‍♂️ CHECK MANUAL DE PERFIL: {CUENTA_OBJETIVO}")
    
    # 1. RUTA ABSOLUTA (La clave para que funcione)
    # Esto convierte "auth/cuenta2" en "C:\Users\beriann\..."
    base_dir = os.getcwd()
    profile_path = os.path.join(base_dir, CUENTA_OBJETIVO, "profile_pw")
    abs_profile_path = os.path.abspath(profile_path)
    
    print(f"📂 Ruta del Perfil: {abs_profile_path}")

    # 2. BUSCAR CHROME
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    chrome_exe = next((p for p in chrome_paths if os.path.exists(p)), None)

    if not chrome_exe:
        print("❌ Chrome no encontrado.")
        return

    # 3. LANZAR CHROME
    # Vamos directo al CARRITO para ver si estás logueado de verdad
    cmd = [
        chrome_exe,
        f"--user-data-dir={abs_profile_path}",
        "--no-first-run",
        "--start-maximized",
        "https://www.nike.cl/checkout/#/cart"
    ]
    
    print(f"🚀 Lanzando Chrome...")
    try:
        subprocess.Popen(cmd)
        print("✅ VENTANA ABIERTA.")
        print("👉 Si ves tu nombre y el carro: ESTÁS LOGUEADO.")
        print("👉 Si ves el login: EL PERFIL ESTÁ VACÍO (El bot te mentía).")
    except Exception as e:
        print(f"❌ Error lanzando: {e}")

if __name__ == "__main__":
    forzar_inspeccion()
