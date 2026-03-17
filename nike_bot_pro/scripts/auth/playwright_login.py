#!/usr/bin/env python3
"""
LOGIN UNICO - Ejecuta esto UNA SOLA VEZ para cada cuenta.
Crea el perfil logueado en Nike que Playwright va a usar.
"""

import os
import sys
from playwright.sync_api import sync_playwright

ACCOUNT = "auth/cuenta2"
PROFILE = os.path.join(ACCOUNT, "profile_pw")

print("")
print("=" * 50)
print("PLAYWRIGHT LOGIN - NIKE")
print("=" * 50)
print("")
print("Este script loguea en Nike usando Playwright")
print("Solo se ejecuta UNA SOLA VEZ por cuenta")
print("")

os.makedirs(PROFILE, exist_ok=True)

print("Abriendo Chrome con perfil: {}".format(PROFILE))
print("")

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE,
        headless=False,
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
        viewport=None
    )

    page = browser.new_page()
    
    print("Navegando a Nike.cl...")
    page.goto("https://www.nike.cl/login", timeout=0)
    
    print("")
    print("=" * 50)
    print("IMPORTANTE:")
    print("=" * 50)
    print("")
    print("1. LOGUÉATE MANUALMENTE en Nike")
    print("2. Ingresa tu usuario y contraseña")
    print("3. Completa cualquier verificación")
    print("4. Cuando veas tu CUENTA LOGUEADA")
    print("5. Presiona ENTER aqui")
    print("")
    
    input("Presiona ENTER cuando hayas logueado completamente...")
    
    print("")
    print("Guardando sesion...")
    time_waited = 0
    import time
    time.sleep(3)
    
    print("Sesion guardada en: {}".format(PROFILE))
    print("")
    print("Puedes cerrar Chrome ahora (o cerralo manualmente)")
    print("")
