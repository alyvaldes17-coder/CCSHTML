"""Nike Scraper - Extrae productos de nike.cl"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import json
import re
import time
from typing import Optional, Dict, List

class NikeScraper:
    """Scraper para Nike Chile"""
    
    BASE_URL = "https://nike.cl"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "es-CL,es;q=0.9",
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Referer": "https://nike.cl/",
        "DNT": "1",
    }
    
    @classmethod
    def scrape_product(cls, url: str) -> Optional[Dict]:
        """
        Scrapea un producto de Nike y extrae info
        
        Args:
            url: URL completa del producto
        
        Returns:
            Dict con: sku, nombre, precio, tallas, imagen
            O None si hay error
        """
        try:
            print(f"[Nike Scraper] Scrapeando: {url}")
            
            # Crear sesión con reintentos automáticos
            session = requests.Session()
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            # Agregar delay pequeño para no parecer bot
            time.sleep(0.5)
            
            # Descargar página con manejo de errores
            response = session.get(url, headers=cls.HEADERS, timeout=15, verify=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer SKU de la URL
            sku_match = re.search(r'skuId=(\d+)', url)
            if not sku_match:
                sku_match = re.search(r'/products/(\d+)', url)
            
            sku = sku_match.group(1) if sku_match else None
            
            # Extraer nombre - Múltiples estrategias
            name = "Unknown"
            for selector in ['h1', 'h2', '[data-testid="product-title"]', '.product-title']:
                name_elem = soup.select_one(selector)
                if name_elem and name_elem.text.strip():
                    name = name_elem.text.strip()
                    break
            
            # También buscar en etiqueta meta og:title (común en tiendas)
            if name == "Unknown":
                og_title = soup.find('meta', {'property': 'og:title'})
                if og_title:
                    name = og_title.get('content', 'Unknown').strip()
            
            # Extraer precio - Múltiples estrategias
            price = None
            
            # Estrategia 1: Buscar el json-ld con producto
            script_tag = soup.find('script', {'type': 'application/ld+json'})
            if script_tag:
                try:
                    json_data = json.loads(script_tag.string)
                    if isinstance(json_data, dict) and 'offers' in json_data:
                        price = json_data['offers'].get('price')
                        if isinstance(price, str):
                            price = int(float(price))
                except:
                    pass
            
            # Estrategia 2: Search for price patterns in text
            if not price:
                price_pattern = soup.find(string=re.compile(r'\$\s*[\d,]+'))
                if price_pattern:
                    price_match = re.search(r'\$\s*([\d,]+)', price_pattern)
                    if price_match:
                        price = int(price_match.group(1).replace(',', ''))
            
            # Estrategia 3: Meta og:price
            if not price:
                og_price = soup.find('meta', {'property': 'og:price:amount'})
                if og_price:
                    try:
                        price = int(float(og_price.get('content')))
                    except:
                        pass
            
            # Extraer tallas disponibles
            sizes = []
            
            # Estrategia 1: Botones con data-testid
            size_buttons = soup.find_all('button', {'data-testid': re.compile(r'size', re.I)})
            
            # Estrategia 2: Cualquier button con números
            if not size_buttons:
                size_buttons = soup.find_all('button', string=re.compile(r'^\d+\.?\d*$'))
            
            # Estrategia 3: Divs o spans con clases size
            if not size_buttons:
                size_buttons = soup.find_all(['div', 'span'], {'class': re.compile(r'size', re.I)})
            
            for btn in size_buttons:
                size_text = btn.text.strip() if hasattr(btn, 'text') else btn.get_text()
                size_text = size_text.strip()
                if size_text and len(size_text) < 10 and not size_text.startswith('$'):
                    sizes.append(size_text)
            
            # Si no encontramos tallas, usar tallas estándar (fallback)
            if not sizes:
                sizes = ["6", "6.5", "7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "12", "13"]
                print(f"[Nike Scraper] ⚠️ No se encontraron tallas reales, usando tallas estándar")
            
            # Extraer imagen
            image = None
            
            # Estrategia 1: og:image
            og_image = soup.find('meta', {'property': 'og:image'})
            if og_image:
                image = og_image.get('content')
            
            # Estrategia 2: img con alt relevante
            if not image:
                img_elems = soup.find_all('img')
                for img in img_elems:
                    alt = img.get('alt', '').lower()
                    if ('nike' in alt or 'product' in alt or 'shoe' in alt or 'zapatilla' in alt):
                        image = img.get('src')
                        break
            
            # Estrategia 3: Primera imagen importante
            if not image:
                img_elem = soup.find('img', {'src': re.compile(r'product|shoe|item', re.I)})
                if img_elem:
                    image = img_elem.get('src')
            
            # Limpiar imagen URL si es relativa
            if image and image.startswith('/'):
                image = cls.BASE_URL + image
            
            product = {
                "sku": sku,
                "name": name,
                "price": price,
                "sizes": list(set(sizes)),  # Remover duplicados
                "image": image,
                "url": url
            }
            
            print(f"[Nike Scraper] ✓ Producto scrapeado:")
            print(f"  SKU: {sku}")
            print(f"  Nombre: {name}")
            print(f"  Precio: ${price}")
            print(f"  Tallas: {product['sizes']}")
            
            return product
            
        except requests.exceptions.RequestException as e:
            print(f"[Nike Scraper] ✗ Error de red: {e}")
            return None
        except Exception as e:
            print(f"[Nike Scraper] ✗ Error: {e}")
            return None
    
    @classmethod
    def scrape_collection(cls, collection_url: str) -> List[Dict]:
        """
        Scrapea una colección de Nike y extrae todos los productos
        (Más avanzado - para futuro)
        """
        products = []
        try:
            print(f"[Nike Scraper] Scrapeando colección: {collection_url}")
            response = requests.get(collection_url, headers=cls.HEADERS, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar links a productos
            product_links = soup.find_all('a', {'data-testid': re.compile(r'product-link')})
            if not product_links:
                product_links = soup.find_all('a', {'href': re.compile(r'/products/')})
            
            for link in product_links[:10]:  # Limitar a 10 primeros
                product_url = link.get('href')
                if not product_url.startswith('http'):
                    product_url = cls.BASE_URL + product_url
                
                product = cls.scrape_product(product_url)
                if product:
                    products.append(product)
            
            print(f"[Nike Scraper] ✓ {len(products)} productos scrapeados")
            return products
            
        except Exception as e:
            print(f"[Nike Scraper] ✗ Error scrapeando colección: {e}")
            return []
