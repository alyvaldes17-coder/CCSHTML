#!/usr/bin/env python
"""
Scraper local para Nike.cl
Abre Chrome, scrapea el producto y lo envía a la API en Railway
"""
import sys
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import re
import json

API_URL = "https://nike-bot-pro-production.up.railway.app/nike/products/add"

def scrape_product(url: str):
    """Scrapea un producto de Nike.cl con Selenium"""
    print(f"[SCRAPER] Abriendo Chrome para: {url}")
    
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        driver.get(url)
        
        # Esperar a que cargue
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
        )
        
        print("[SCRAPER] Página cargada, extrayendo datos...")
        
        # Extraer SKU
        sku = None
        sku_match = re.search(r'skuId=(\d+)', url)
        if sku_match:
            sku = sku_match.group(1)
        
        # Extraer nombre
        name = "Unknown"
        try:
            name_elem = driver.find_element(By.TAG_NAME, "h1")
            name = name_elem.text.strip()
        except:
            pass
        
        # Extraer precio
        price = None
        try:
            price_elems = driver.find_elements(By.XPATH, "//*[contains(text(), '$')]")
            if price_elems:
                price_text = price_elems[0].text
                price_match = re.search(r'\$\s*([\d,]+)', price_text)
                if price_match:
                    price = int(price_match.group(1).replace(',', ''))
        except Exception as e:
            print(f"[SCRAPER] ⚠️ No se encontró precio: {e}")
        
        # Extraer tallas
        sizes = []
        try:
            size_elements = driver.find_elements(By.XPATH, "//button[contains(@class, 'size') or contains(text(), '.')]")
            for elem in size_elements[:20]:
                text = elem.text.strip()
                if text and len(text) < 10 and text not in sizes:
                    sizes.append(text)
                    if len(sizes) >= 15:
                        break
        except Exception as e:
            print(f"[SCRAPER] ⚠️ No se encontraron tallas: {e}")
        
        if not sizes:
            sizes = ["6", "6.5", "7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "12", "13"]
            print("[SCRAPER] Usando tallas estándar como fallback")
        
        # Extraer imagen
        image = None
        try:
            img_elem = driver.find_element(By.TAG_NAME, "img")
            image = img_elem.get_attribute("src")
        except:
            pass
        
        driver.quit()
        print("[SCRAPER] ✓ Chrome cerrado")
        
        if not sku or name == "Unknown":
            print(f"✗ ERROR: No se extrajeron datos válidos")
            print(f"  SKU: {sku}, Nombre: {name}")
            return None
        
        product = {
            "sku": sku,
            "name": name,
            "price": price,
            "sizes": list(set(sizes)),
            "image": image,
            "url": url
        }
        
        print("[SCRAPER] ✓ Datos extraídos:")
        print(f"  SKU: {product['sku']}")
        print(f"  Nombre: {product['name']}")
        print(f"  Precio: ${product['price']}")
        print(f"  Tallas: {len(product['sizes'])} disponibles")
        print(f"  Imagen: {'Sí' if product['image'] else 'No'}")
        
        return product
        
    except Exception as e:
        print(f"[SCRAPER] ✗ Error con Selenium: {e}")
        import traceback
        traceback.print_exc()
        return None

def upload_to_api(product: dict) -> bool:
    """Envía el producto a la API en Railway"""
    try:
        print(f"\n[API] Enviando producto {product['sku']} a Railway...")
        
        response = requests.post(API_URL, json=product, timeout=10)
        
        if response.status_code == 200:
            print(f"✓ [API] Producto guardado en BD")
            print(f"  Respuesta: {response.json()}")
            return True
        else:
            print(f"✗ [API] Error {response.status_code}")
            print(f"  Respuesta: {response.json()}")
            return False
            
    except Exception as e:
        print(f"✗ [API] Error conectando a Railway: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Uso: python scrape_and_upload.py 'URL_DEL_PRODUCTO'")
        print("\nEjemplo:")
        print('  python scrape_and_upload.py "http://nike.cl/hv0823-108-air-jordan-4-retro/p?skuId=191697"')
        sys.exit(1)
    
    url = sys.argv[1]
    
    if "nike" not in url.lower():
        print("✗ ERROR: URL debe contener 'nike'")
        sys.exit(1)
    
    print("=" * 70)
    print("NIKE SCRAPER + UPLOAD LOCAL")
    print("=" * 70)
    
    # Scrappear localmente
    product = scrape_product(url)
    
    if not product:
        print("\n✗ Scraping falló")
        sys.exit(1)
    
    # Enviar a API
    if upload_to_api(product):
        print("\n" + "=" * 70)
        print("✓ TODO COMPLETADO - Producto guardado en la BD")
        print("=" * 70)
        sys.exit(0)
    else:
        print("\n✗ No se pudo enviar a la API")
        sys.exit(1)

if __name__ == "__main__":
    main()
