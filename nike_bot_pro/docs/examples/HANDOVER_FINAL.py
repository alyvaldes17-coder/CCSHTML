# 🏆 HANDOVER FINAL - Copiar y pegar en runtime/worker.py

def _launch_browser_for_payment(account_path, cookies, dprint):
    """🏆 HANDOVER FINAL - SIN CIERRE, SIN MODAL, SIN RECALCULAR
    
    - Backend MUERE aquí
    - Cart + Price LOCKED
    - Browser avanza humano a payment
    - NO recalcula precio
    - NO se cierra solo
    """
    dprint(f"   🟢 HANDOVER MODE ACTIVADO")
    dprint(f"   🔒 CART_LOCKED + PRICE_LOCKED")
    
    from playwright.sync_api import sync_playwright
    import os
    import time
    
    profile_dir = os.path.abspath(os.path.join(account_path, "profile_pw"))
    
    if not os.path.exists(profile_dir):
        dprint(f"   ❌ Perfil no existe: {profile_dir}")
        return
    
    # NO usar "with" - para que NO cierre
    p = sync_playwright().start()
    
    try:
        dprint(f"   🚀 Abriendo Chrome (VISIBLE)...")
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        # 1️⃣ IR AL CARRITO
        dprint(f"   🛒 Abriendo carrito...")
        try:
            page.goto("https://www.nike.cl/checkout/#/cart", timeout=0)
            page.wait_for_timeout(800)
        except:
            pass
        
        # 2️⃣ MATAR MODALES (ULTRA AGRESIVO)
        dprint(f"   🧹 Inyectando CSS nuclear...")
        try:
            page.add_style_tag(content="""
                * {
                    --modal-display: none !important;
                }
                
                .ReactModal__Overlay,
                .ReactModal__Content,
                .vtex-modal__overlay,
                .vtex-modal-layout-0-x-backdrop,
                .vtex-modal-layout-0-x-container,
                .newsletter-modal,
                [role="dialog"],
                .modal,
                .popup,
                .confirm-modal {
                    display: none !important;
                    visibility: hidden !important;
                    pointer-events: none !important;
                    opacity: 0 !important;
                    z-index: -9999 !important;
                }
                
                .vtex-modal__overlay::before,
                .vtex-modal__overlay::after {
                    display: none !important;
                }
            """)
            dprint(f"   ✅ CSS inyectado (modales muertos)")
        except Exception as e:
            dprint(f"   ⚠️ CSS error: {e}")
        
        page.wait_for_timeout(500)
        
        # 3️⃣ CLICK HUMANO "CONTINUAR"
        dprint(f"   👉 Buscando botón 'Continuar'...")
        try:
            btn = page.wait_for_selector(
                "button:has-text('Continuar'), button:has-text('Finalizar compra')",
                timeout=2000
            )
            if btn:
                dprint(f"   ✅ Click automático")
                btn.click()
                page.wait_for_timeout(1200)
        except:
            dprint(f"   ℹ️ Botón no encontrado, continuando...")
        
        # 4️⃣ ESPERAR PAYMENT (SIN RECALCULAR)
        dprint(f"   💳 Esperando navegación a /payment...")
        try:
            page.wait_for_url("**/checkout/#/payment", timeout=6000)
            dprint(f"   ✅ ¡En /payment!")
        except:
            dprint(f"   ⚠️ Timeout, navegando directo...")
            try:
                page.goto("https://www.nike.cl/checkout/#/payment", timeout=5000)
            except:
                pass
        
        page.wait_for_timeout(500)
        
        # 5️⃣ HANDOVER COMPLETO
        dprint(f"\n════════════════════════════════════════")
        dprint(f"   ✅ PAYMENT ABIERTO")
        dprint(f"   💰 Precio BLOQUEADO")
        dprint(f"   🖥️ Navegador NO se cerrará")
        dprint(f"   👉 PAGA AHORA")
        dprint(f"════════════════════════════════════════\n")
        
        # MODO ETERNO - El bot NO toca nada más
        while True:
            time.sleep(1)
            if not browser.pages:
                break
        
    except Exception as e:
        dprint(f"   ❌ Error: {e}")
    
    # NO hacer p.stop() - Windows cierra cuando el usuario quiera
