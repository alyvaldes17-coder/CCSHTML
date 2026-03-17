# engines/modal_handlers.py
"""
Handlers para modales comunes en Nike checkout.
"""
import logging
from typing import Optional
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout


class CheckoutModals:
    """Maneja modales que aparecen durante el checkout de Nike."""

    def __init__(self, log: Optional[object] = None):
        self.log = log or logging.getLogger("CheckoutModals")

    def handle_confirm_data_modal(self, page: Page, timeout_sec: int = 3) -> bool:
        """
        Maneja el modal "¡CONFIRMA TUS DATOS!" que aparece en Nike CL.
        
        ✅ Este modal es NORMAL y ESPERADO.
        ✅ Debe ser aceptado SIEMPRE antes de elegir método de pago.
        
        Args:
            page: Playwright Page
            timeout_sec: Timeout en segundos
            
        Returns:
            True si modal fue encontrado y aceptado
            False si modal no apareció (también OK)
        """
        try:
            self.log.info("   🔍 Buscando modal 'Confirma tus datos'...")
            
            # Buscar el modal (puede tener varios selectores)
            modal_selectors = [
                "text=¡CONFIRMA TUS DATOS!",
                "text=Confirma tus datos",
                "text=Confirmar datos",
                "[data-testid='confirm-data-modal']",
            ]
            
            button_selectors = [
                "text=Continuar compra",
                "text=Continuar",
                "button:has-text('Continuar')",
            ]
            
            # 1. Esperar que el modal sea visible
            modal_found = False
            for selector in modal_selectors:
                try:
                    page.wait_for_selector(selector, timeout=timeout_sec * 1000)
                    self.log.info(f"   ✅ Modal encontrado: {selector}")
                    modal_found = True
                    break
                except PlaywrightTimeout:
                    continue
            
            if not modal_found:
                self.log.debug("   ⏭️  Modal 'Confirma tus datos' no apareció (OK)")
                return False
            
            # 2. Clickear botón "Continuar compra"
            for btn_selector in button_selectors:
                try:
                    page.click(btn_selector)
                    self.log.info(f"✅ Modal aceptado (botón: {btn_selector})")
                    
                    # Esperar a que el modal se cierre
                    page.wait_for_function(
                        """() => !document.body.innerText.includes('CONFIRMA TUS DATOS')""",
                        timeout=2000
                    )
                    return True
                except:
                    continue
            
            self.log.warning("⚠️ Modal encontrado pero no se pudo aceptar")
            return False
            
        except Exception as e:
            self.log.error(f"❌ Error en handle_confirm_data_modal: {e}")
            return False

    def select_transfer_payment(self, page: Page, timeout_sec: int = 5) -> bool:
        """
        Selecciona "Transferencia con tu banco" como método de pago.
        
        Args:
            page: Playwright Page
            timeout_sec: Timeout en segundos
            
        Returns:
            True si se seleccionó exitosamente
        """
        try:
            self.log.info("   Seleccionando 'Transferencia con tu banco'...")
            
            selectors = [
                "text=Transferencia con tu banco",
                "text=Transferencia",
                "[data-testid='transfer-payment']",
                "label:has-text('Transferencia')",
            ]
            
            for selector in selectors:
                try:
                    page.click(selector)
                    self.log.info(f"✅ Método seleccionado: {selector}")
                    return True
                except:
                    continue
            
            self.log.warning("⚠️ No se pudo seleccionar 'Transferencia con tu banco'")
            return False
            
        except Exception as e:
            self.log.error(f"❌ Error seleccionando método: {e}")
            return False

    def click_finalize_payment(self, page: Page, timeout_sec: int = 5) -> bool:
        """
        Clickea botón "Finalizar compra" UNA SOLA VEZ.
        
        Espera a que el botón esté habilitado antes de hacer click.
        
        Args:
            page: Playwright Page
            timeout_sec: Timeout para esperar botón habilitado
            
        Returns:
            True si se clickeó exitosamente
        """
        try:
            self.log.info("   Esperando botón 'Finalizar compra' habilitado...")
            
            # Esperar a que el botón exista y esté habilitado
            page.wait_for_function(
                """() => {
                    const buttons = document.querySelectorAll('button');
                    const finalize = [...buttons].find(b => 
                        b.innerText.includes('Finalizar') && 
                        !b.disabled
                    );
                    return finalize != null;
                }""",
                timeout=timeout_sec * 1000
            )
            
            self.log.info("✅ Botón 'Finalizar compra' habilitado")
            
            # Click UNA SOLA VEZ
            page.click("button:has-text('Finalizar')")
            self.log.info("✅ Pago iniciado (botón clickeado)")
            
            return True
            
        except PlaywrightTimeout:
            self.log.error("❌ Timeout esperando botón 'Finalizar compra'")
            return False
        except Exception as e:
            self.log.error(f"❌ Error clickeando 'Finalizar': {e}")
            return False
