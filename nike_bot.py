"""Nike Bot - Automatización de carrito en nike.cl"""
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class NikeBot:
    """Bot para automatizar compras en nike.cl"""
    
    def __init__(self, headless=False):
        """
        Inicializa el bot de Nike
        
        Args:
            headless: Si True, ejecuta sin interfaz gráfica
        """
        options = webdriver.ChromeOptions()
        
        if headless:
            options.add_argument("--headless")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.wait = WebDriverWait(self.driver, 10)
    
    def extract_sku_from_url(self, url: str) -> str:
        """
        Extrae el SKU de la URL de Nike
        
        Ej: https://nike.cl/products/123456789 → 123456789
        """
        match = re.search(r'/products/(\d+)', url)
        if match:
            return match.group(1)
        raise ValueError(f"No se pudo extraer SKU de: {url}")
    
    def add_to_cart(self, url: str, size: str) -> bool:
        """
        Agrega un producto al carrito de Nike
        
        Args:
            url: URL completa del producto en nike.cl
            size: Talla a agregar (ej: "9", "9.5")
        
        Returns:
            True si llegó hasta Fintoc, False si hubo error
        """
        try:
            print(f"[Nike Bot] Abriendo: {url}")
            self.driver.get(url)
            time.sleep(3)
            
            print(f"[Nike Bot] Seleccionando talla: {size}")
            # Buscar botón de talla
            size_buttons = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid*='size']")
            
            size_selected = False
            for button in size_buttons:
                if size in button.text:
                    button.click()
                    size_selected = True
                    print(f"[Nike Bot] ✓ Talla {size} seleccionada")
                    break
            
            if not size_selected:
                # Intenta alternativa: buscar por aria-label
                size_buttons = self.driver.find_elements(By.XPATH, f"//button[contains(@aria-label, '{size}')]")
                if size_buttons:
                    size_buttons[0].click()
                    size_selected = True
                    print(f"[Nike Bot] ✓ Talla {size} seleccionada (alternativa)")
            
            if not size_selected:
                print(f"[Nike Bot] ✗ No se pudo seleccionar talla {size}")
                return False
            
            time.sleep(1)
            
            # Click en "Agregar al carrito"
            print("[Nike Bot] Buscando botón 'Agregar al carrito'...")
            add_to_cart_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Agregar al carrito')]"))
            )
            add_to_cart_btn.click()
            print("[Nike Bot] ✓ Agregado al carrito")
            
            time.sleep(2)
            
            # Click en "Ir al carrito" o "Proceder al pago"
            print("[Nike Bot] Buscando botón de checkout...")
            try:
                checkout_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Proceder al pago')]"))
                )
                checkout_btn.click()
            except:
                # Alternativa: ir al carrito
                cart_btn = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'cart')]")
                if cart_btn:
                    cart_btn[0].click()
                    print("[Nike Bot] Navegando al carrito...")
            
            time.sleep(3)
            
            # Esperar a que llegue a Fintoc
            print("[Nike Bot] Esperando a Fintoc...")
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Fintoc') or contains(text(), 'Banco')]"))
            )
            
            print("[Nike Bot] ✓ LISTO PARA PAGO - Selecciona tu banco en Fintoc")
            print("[Nike Bot] El navegador permanece abierto para que completes la compra manualmente")
            
            return True
            
        except Exception as e:
            print(f"[Nike Bot] ✗ Error: {str(e)}")
            return False
    
    def keep_open(self):
        """Mantiene el navegador abierto esperando que el usuario complete la compra"""
        try:
            print("[Nike Bot] Presiona Enter para cerrar el navegador cuando termines...")
            input()
        except KeyboardInterrupt:
            pass
        finally:
            self.close()
    
    def close(self):
        """Cierra el navegador"""
        self.driver.quit()
        print("[Nike Bot] Navegador cerrado")
