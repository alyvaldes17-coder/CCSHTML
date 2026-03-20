#!/usr/bin/env python
"""
Login en Nike.cl y guardar cookies para el bot
Ejecuta esto primero para autenticarte
"""
import pickle
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

COOKIES_FILE = "nike_cookies.pkl"

def save_cookies(driver, filename=COOKIES_FILE):
    """Guarda las cookies del navegador a un archivo"""
    print(f"\n[COOKIES] Guardando cookies en {filename}...")
    try:
        pickle.dump(driver.get_cookies(), open(filename, "wb"))
        print(f"✓ Cookies guardadas exitosamente")
        return True
    except Exception as e:
        print(f"✗ Error guardando cookies: {e}")
        return False

def load_cookies(driver, filename=COOKIES_FILE):
    """Carga las cookies desde un archivo previo"""
    if not os.path.exists(filename):
        print(f"⚠️ No hay cookies guardadas ({filename})")
        return False
    
    try:
        print(f"[COOKIES] Cargando cookies desde {filename}...")
        cookies = pickle.load(open(filename, "rb"))
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception:
                pass  # Algunos cookies pueden fallar, ignorar
        print(f"✓ {len(cookies)} cookies cargadas")
        return True
    except Exception as e:
        print(f"✗ Error cargando cookies: {e}")
        return False

def login_nike():
    """Abre Nike y espera a que inicies sesión manualmente"""
    print("\n" + "="*70)
    print("NIKE.CL LOGIN HELPER")
    print("="*70)
    print("\n📍 Abriendo Nike.cl...")
    print("Por favor inicia sesión manualmente en el navegador que se abrirá.")
    print("Una vez autenticado, presiona ENTER aquí para guardar las cookies.")
    print()
    
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        # Ocultar automación
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
            """
        })
        
        driver.get("https://nike.cl")
        
        print("⏳ Esperando que inicies sesión...")
        print("(Presiona ENTER cuando hayas completado el login en el navegador)")
        input()
        
        # Guardar cookies
        if save_cookies(driver):
            print("\n✓ LISTO - Ahora puedes usar el bot con: python nike_bot_local.py URL")
        
        time.sleep(2)
        driver.quit()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    login_nike()
