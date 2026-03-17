#!/usr/bin/env python3
"""
MODE B FINAL - Abre Chrome REAL con sesion Nike y entra directo a PAYMENT.
NO toca carrito. NO pierde precio.
"""

import sys
import time
import os
from playwright.sync_api import sync_playwright

def main():
    account_path = sys.argv[1] if len(sys.argv) > 1 else None
    account_name = sys.argv[2] if len(sys.argv) > 2 else "ACCOUNT"
    
    if not account_path:
        print("[LAUNCHER] ERROR: Falta account_path")
        sys.exit(1)
    
    profile_dir = os.path.join(account_path, "profile_pw")
    
    if not os.path.exists(profile_dir):
        print("[LAUNCHER] ERROR: No existe {}".format(profile_dir))
        print("[LAUNCHER] Debes loguearte una vez en Nike antes")
        sys.exit(1)
    
    print("[{}] HANDOVER A PAGO (MODE B REAL)".format(account_name))
    
    try:
        with sync_playwright() as p:
            print("[{}] Abriendo Chrome con perfil REAL...".format(account_name))
            
            # Obtener ruta de la extensión
            repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            extension_path = os.path.join(repo_root, "extension")
            
            browser = p.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                headless=False,
                args=[
                    "--start-maximized",
                    "--disable-blink-features=AutomationControlled",
                    f"--load-extension={extension_path}",
                    "--disable-extensions-except=" + extension_path
                ],
                viewport=None
            )
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.bring_to_front()
            
            print("[{}] Abriendo PAYMENT directo (extension activa)...".format(account_name))
            page.goto("https://www.nike.cl/checkout/#/payment", timeout=0)
            
            try:
                page.add_style_tag(content="""
                .ReactModal__Overlay,
                .newsletter-modal,
                iframe[src*="recaptcha"] {
                    display: none !important;
                }
                """)
            except:
                pass
            
            print("")
            print("=" * 50)
            print("[{}] CHECKOUT ABIERTO".format(account_name))
            print("[{}] -> SOLO CONFIRMA Y PAGA".format(account_name))
            print("[{}] -> NO REFRESCAR".format(account_name))
            print("=" * 50)
            print("")
            
            while True:
                time.sleep(1)
    
    except Exception as e:
        print("[{}] ERROR: {}".format(account_name, e))
        import traceback
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()



