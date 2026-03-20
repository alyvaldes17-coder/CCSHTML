"""Nike Bot - Automatización de carrito en nike.cl"""
import re
import time
import pickle
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class NikeBot:
    """Bot para automatizar compras en nike.cl"""
    
    PROFILE_DIR = "nike_profile"  # Directorio del perfil persistente
    
    def __init__(self, headless=False):
        """
        Inicializa el bot de Nike
        
        Args:
            headless: Si True, ejecuta sin interfaz gráfica
        """
        options = webdriver.ChromeOptions()
        
        # Usar un perfil persistente que mantiene sesión, cookies, etc.
        print(f"[Nike Bot] Usando perfil: {self.PROFILE_DIR}")
        options.add_argument(f"--user-data-dir={os.path.abspath(self.PROFILE_DIR)}")
        
        if headless:
            options.add_argument("--headless")
        
        # Argumentos para ocultar que es automatizado y quitar banner
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        # Ocultar webdriver de forma adicional
        try:
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false,
                    });
                """
            })
        except:
            pass  # Algunos navegadores no soportan CDP
        
        self.wait = WebDriverWait(self.driver, 10)
    
    def load_cookies(self, filename: str = "nike_cookies.pkl") -> bool:
        """Carga las cookies guardadas de una sesión anterior"""
        if not os.path.exists(filename):
            print(f"[Nike Bot] ⚠️ No hay cookies guardadas. Ejecuta: python nike_login.py")
            return False
        
        try:
            print(f"[Nike Bot] Cargando cookies de sesión anterior...")
            # Primero navega a Nike para poder agregar cookies
            self.driver.get("https://nike.cl")
            time.sleep(1)
            
            # Cargar cookies
            cookies = pickle.load(open(filename, "rb"))
            for cookie in cookies:
                try:
                    # Algunos cookies pueden tener campos que Chrome no acepta
                    if 'expiry' in cookie:
                        cookie['expiry'] = int(cookie['expiry'])
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    pass  # Ignorar cookies que fallan
            
            print(f"[Nike Bot] ✓ {len(cookies)} cookies cargadas - Sesión activa")
            return True
        except Exception as e:
            print(f"[Nike Bot] ✗ Error cargando cookies: {e}")
            return False
    
    def extract_sku_from_url(self, url: str) -> str:
        """
        Extrae el SKU de la URL de Nike
        
        Soporta dos formatos:
        - https://nike.cl/products/123456789 → 123456789
        - https://nike.cl/product-name/p?skuId=191697 → 191697
        """
        # Intenta primer formato: /products/SKU
        match = re.search(r'/products/(\d+)', url)
        if match:
            return match.group(1)
        
        # Intenta segundo formato: ?skuId=SKU
        match = re.search(r'skuId=(\d+)', url)
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
            # El perfil persistente mantiene la sesión automáticamente
            print(f"[Nike Bot] Abriendo: {url}")
            self.driver.get(url)
            time.sleep(4)
            
            print(f"[Nike Bot] Seleccionando talla: {size}")
            
            # Estrategia 1: Buscar botones que contengan el texto de la talla
            try:
                size_buttons = self.driver.find_elements(By.XPATH, f"//button[contains(text(), '{size}')]")
                if size_buttons:
                    size_buttons[0].click()
                    print(f"[Nike Bot] ✓ Talla {size} seleccionada (método 1)")
                    time.sleep(1)
                else:
                    raise Exception("No encontrado")
            except:
                # Estrategia 2: Buscar por data-testid
                try:
                    size_buttons = self.driver.find_elements(By.XPATH, f"//*[contains(@data-testid, 'size') and contains(text(), '{size}')]")
                    if size_buttons:
                        size_buttons[0].click()
                        print(f"[Nike Bot] ✓ Talla {size} seleccionada (método 2)")
                        time.sleep(1)
                    else:
                        raise Exception("No encontrado")
                except:
                    # Estrategia 3: Buscar por aria-label
                    try:
                        size_buttons = self.driver.find_elements(By.XPATH, f"//button[contains(@aria-label, '{size}')]")
                        if size_buttons:
                            size_buttons[0].click()
                            print(f"[Nike Bot] ✓ Talla {size} seleccionada (método 3)")
                            time.sleep(1)
                        else:
                            raise Exception("No encontrado")
                    except:
                        # Estrategia 4: Buscar todos los botones y comparar texto
                        print("[Nike Bot] Intentando método alternativo...")
                        all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        for button in all_buttons:
                            try:
                                if size in button.text:
                                    button.click()
                                    print(f"[Nike Bot] ✓ Talla {size} seleccionada (método 4)")
                                    time.sleep(1)
                                    break
                            except:
                                continue
                        else:
                            print(f"[Nike Bot] ⚠ No se encontró botón de talla {size}")
                            print("[Nike Bot] Intentando proceder sin seleccionar talla...")
            
            time.sleep(2)
            
            # Click en "Agregar al carrito" - varios intentos
            print("[Nike Bot] Buscando botón 'Agregar al carrito'...")
            try:
                # Intentar por texto exacto
                add_btn = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Agregar al carrito')]")
                if add_btn:
                    add_btn[0].click()
                else:
                    # Intentar variaciones
                    add_btn = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Agregar') or contains(text(), 'Añadir')]")
                    if add_btn:
                        add_btn[0].click()
                    else:
                        raise Exception("No encontrado")
                
                print("[Nike Bot] ✓ Agregado al carrito")
                time.sleep(3)
            except Exception as e:
                print(f"[Nike Bot] ⚠ No se pudo agregar al carrito: {e}")
                print("[Nike Bot] Intentando ir directo al checkout...")
            
            # Proceder a checkout
            print("[Nike Bot] Buscando botón de checkout...")
            try:
                checkout_btns = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Proceder al pago')] | //button[contains(text(), 'Ir al carrito')] | //button[contains(text(), 'Checkout')]")
                if checkout_btns:
                    checkout_btns[0].click()
                    print("[Nike Bot] Navegando a checkout...")
                    time.sleep(3)
            except:
                pass
            
            # Esperar a Fintoc
            print("[Nike Bot] Esperando a pantalla de pago...")
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Fintoc') or contains(text(), 'banco') or contains(text(), 'Banco')]"))
                )
                print("[Nike Bot] ✓ LISTO PARA PAGO - Selecciona tu banco")
                return True
            except:
                # Si no encuentra Fintoc, verificar si al menos está en checkout
                try:
                    current_url = self.driver.current_url
                    if "checkout" in current_url.lower() or "pay" in current_url.lower():
                        print("[Nike Bot] ✓ Estás en la página de checkout/pago")
                        return True
                except:
                    pass
                
                print("[Nike Bot] ⚠ No se detectó pantalla de pago")
                return False
            
        except Exception as e:
            print(f"[Nike Bot] ✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()
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
