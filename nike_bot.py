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
            time.sleep(5)  # Espera más tiempo para que cargue JavaScript
            
            # Scroll para asegurar visibilidad de elementos
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            print(f"[Nike Bot] Seleccionando talla: {size}")
            
            # Estrategia para encontrar selector de talla más robusto
            found_size = False
            
            # 1. Buscar label + input (manera moderna de hacer selectores)
            try:
                print(f"[Nike Bot] Intentando por label/input...")
                size_labels = self.driver.find_elements(By.XPATH, f"//label[contains(., '{size}')] | //*[contains(@class, 'size') and contains(text(), '{size}')]")
                if size_labels:
                    parent = size_labels[0].find_element(By.XPATH, "..")
                    parent.click()
                    print(f"[Nike Bot] ✓ Talla {size} seleccionada (por label)")
                    found_size = True
                    time.sleep(1)
            except:
                pass
            
            # 2. Buscar cualquier elemento clickeable con la talla
            if not found_size:
                try:
                    print(f"[Nike Bot] Intentando por elemento clickeable...")
                    # Busca radio buttons, checkboxes o buttons con la talla
                    size_elements = self.driver.find_elements(By.XPATH, f"//*[(@role='radio' or @role='checkbox' or @type='radio' or @type='checkbox') and contains(., '{size}')] | //*[contains(text(), '{size}') and (@onclick or @data-testid)]")
                    if size_elements:
                        # Scroll el elemento a vista
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", size_elements[0])
                        time.sleep(0.5)
                        size_elements[0].click()
                        print(f"[Nike Bot] ✓ Talla {size} seleccionada (elemento clickeable)")
                        found_size = True
                        time.sleep(1)
                except:
                    pass
            
            # 3. Buscar botones con texto exacto
            if not found_size:
                try:
                    print(f"[Nike Bot] Buscando all buttons con talla...")
                    all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    for button in all_buttons:
                        try:
                            btn_text = button.text.strip()
                            if btn_text == size or btn_text == str(size):
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                                time.sleep(0.3)
                                button.click()
                                print(f"[Nike Bot] ✓ Talla {size} seleccionada (botón)")
                                found_size = True
                                break
                        except:
                            continue
                except:
                    pass
            
            if not found_size:
                print(f"[Nike Bot] ⚠ No se encontró selector de talla {size}")
                print(f"[Nike Bot] ℹ Elementos encontrados en página:")
                # Debug: mostrar qué elementos hay
                try:
                    all_text = self.driver.execute_script("return document.body.innerText")
                    if size in all_text:
                        print(f"[Nike Bot] ✓ Talla {size} EXISTE en la página")
                    else:
                        print(f"[Nike Bot] ✗ Talla {size} NO existe en la página")
                except:
                    pass
            
            time.sleep(2)
            
            # Buscar botón "Agregar al carrito" con múltiples estrategias
            print("[Nike Bot] Buscando botón 'Agregar al carrito'...")
            
            buttons_found = False
            
            # 1. XPath simple por texto
            try:
                add_btns = self.driver.find_elements(By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'agregar')]")
                if add_btns:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", add_btns[0])
                    time.sleep(0.5)
                    add_btns[0].click()
                    print("[Nike Bot] ✓ Agregado al carrito (botón encontrado)")
                    buttons_found = True
            except:
                pass
            
            # 2. Buscar por class name común
            if not buttons_found:
                try:
                    add_btns = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'add') or contains(@class, 'cart')]//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'agregar')] | //button[@type='submit']")
                    if add_btns:
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", add_btns[0])
                        time.sleep(0.5)
                        add_btns[0].click()
                        print("[Nike Bot] ✓ Agregado al carrito (por clase)")
                        buttons_found = True
                except:
                    pass
            
            # 3. Buscar cualquier botón principal (último, más grande)
            if not buttons_found:
                try:
                    all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    # Filtrar botones visibles
                    visible_buttons = [b for b in all_buttons if b.is_displayed()]
                    if visible_buttons:
                        # Click el último botón visible (suele ser el principal)
                        last_btn = visible_buttons[-1]
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", last_btn)
                        time.sleep(0.5)
                        last_btn.click()
                        print("[Nike Bot] ✓ Agregado al carrito (último botón)")
                        buttons_found = True
                except:
                    pass
            
            if not buttons_found:
                print("[Nike Bot] ⚠ No se encontró botón de agregar al carrito")
            
            time.sleep(3)
            
            # Ir a checkout si es necesario
            print("[Nike Bot] Navegando a checkout...")
            try:
                # Buscar botones de checkout
                checkout_btns = self.driver.find_elements(By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'checkout')] | //button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'pago')] | //button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'carrito')]")
                if checkout_btns:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", checkout_btns[0])
                    time.sleep(0.5)
                    checkout_btns[0].click()
                    print("[Nike Bot] ✓ Navegando a checkout...")
            except:
                pass
            
            # Esperar a Fintoc o pantalla de pago
            print("[Nike Bot] Esperando a pantalla de pago...")
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Fintoc') or contains(text(), 'banco') or contains(text(), 'Banco') or contains(text(), 'selecciona')]"))
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
