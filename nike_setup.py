#!/usr/bin/env python
"""
Abre Nike.cl en el navegador del bot para que inicies sesión
Las cookies y sesión se guardan automáticamente en el perfil
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

PROFILE_DIR = "nike_profile"

def setup_login():
    """Abre Nike.cl con el perfil persistente para login"""
    print("\n" + "="*70)
    print("NIKE.CL - SETUP INICIAL DE SESIÓN")
    print("="*70)
    print("\n📍 Abriendo Nike.cl con tu perfil persistente...")
    print("Por favor inicia sesión manualmente.")
    print("\nLa sesión se guardará automáticamente en el navegador.")
    print("Presiona ENTER aquí cuando hayas completado el login.\n")
    
    options = Options()
    options.add_argument(f"--user-data-dir={os.path.abspath(PROFILE_DIR)}")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        # Ocultar webdriver
        try:
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false,
                    });
                """
            })
        except:
            pass
        
        driver.get("https://www.nike.cl")
        
        print("⏳ Esperando login...")
        print("(Presiona ENTER aquí cuando hayas iniciado sesión)\n")
        input()
        
        print("\n✓ Perfil guardado con sesión activa")
        print("✓ Ahora puedes usar el bot:")
        print('  python nike_bot_local.py "URL"')
        print("\nLa sesión se mantendrá en futuros usos del bot.\n")
        
        time.sleep(2)
        driver.quit()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    setup_login()
