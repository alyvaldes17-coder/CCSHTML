# example_state_machine_usage.py
"""
Ejemplo pragmático de cómo usar StateMachine.

Flujo:
1. Instanciar requests.Session con cookies VTEX
2. Abrir Playwright (Browser + Page)
3. Crear StateMachine con session + page
4. Llamar .run()
5. Máquina ejecuta los 8 estados y se detiene en AWAITING_HUMAN_CONFIRMATION
"""

import logging
from requests import Session
from playwright.sync_api import sync_playwright
from runner.state_machine import StateMachine
from core.bot_state import BotState

# Setup logging
logging.basicConfig(
    format="[%(asctime)s] [%(levelname)-8s] [%(name)-20s] %(message)s",
    level=logging.INFO
)
log = logging.getLogger("main")


def main():
    """Ejemplo completo"""
    
    # 1. Crear session con cookies VTEX
    log.info("🔑 Preparando sesión...")
    session = Session()
    
    # Aquí cargarías tokens desde auth/cuenta1/tokens.json
    # session.headers.update({"Authorization": "bearer ..."})
    # session.cookies.update({"vtex_session": "...", ...})
    
    # 2. Abrir Playwright
    log.info("🌐 Abriendo Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Navegar a Nike
        log.info("📍 Navegando a Nike...")
        page.goto("https://www.nike.com/cl/es")
        
        # 3. Crear máquina de estados
        log.info("🤖 Instanciando StateMachine...")
        sm = StateMachine(
            session=session,
            page=page,
            log=log
        )
        
        # 4. Ejecutar
        log.info("▶️  Iniciando máquina...")
        final_state, order_form = sm.run(bank_name="Banco Santander")
        
        # 5. Resultado
        log.info(f"🎯 Máquina terminada")
        log.info(f"   Estado final: {final_state.name}")
        log.info(f"   OrderFormId: {order_form.get('orderFormId', 'N/A')}")
        log.info(f"   Total: {order_form.get('value', 'N/A')} cents")
        
        # ========================================================================
        # En este punto:
        # - Modal Fintoc está abierto
        # - Usuario ve selector de banco
        # - Bot se detiene y espera que usuario completa:
        #   1. Selecciona banco
        #   2. Autoriza 2FA
        #   3. Confirma transacción
        # ========================================================================
        
        # Mantener página abierta
        log.info("⏸️  Esperando confirmación manual...")
        page.wait_for_timeout(60000)  # 1 minuto
        
        browser.close()
    
    log.info("✅ Ejemplo completado")


if __name__ == "__main__":
    main()
