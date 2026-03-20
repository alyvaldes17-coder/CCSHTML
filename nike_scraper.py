"""Nike Scraper - Extrae productos de nike.cl"""
import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Optional, Dict, List

class NikeScraper:
    """Scraper para Nike Chile"""
    
    BASE_URL = "https://nike.cl"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
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
            
            # Descargar página
            response = requests.get(url, headers=cls.HEADERS, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer SKU de la URL
            sku_match = re.search(r'skuId=(\d+)', url)
            if not sku_match:
                sku_match = re.search(r'/products/(\d+)', url)
            
            sku = sku_match.group(1) if sku_match else None
            
            # Extraer nombre del producto
            name_elem = soup.find('h1', {'data-testid': 'product-title'})
            if not name_elem:
                name_elem = soup.find('h1')
            name = name_elem.text.strip() if name_elem else "Unknown"
            
            # Extraer precio
            price_elem = soup.find('div', {'data-testid': 'product-price'})
            if not price_elem:
                price_elem = soup.find(string=re.compile(r'\$\s*[\d,]+'))
            
            price = None
            if price_elem:
                price_text = price_elem.text if hasattr(price_elem, 'text') else price_elem
                price_match = re.search(r'\$\s*([\d,]+)', price_text)
                if price_match:
                    price = int(price_match.group(1).replace(',', ''))
            
            # Extraer tallas disponibles
            sizes = []
            size_buttons = soup.find_all('button', {'data-testid': re.compile(r'size')})
            if not size_buttons:
                # Intenta otra estrategia
                size_buttons = soup.find_all('button', string=re.compile(r'^\d+\.?\d*$'))
            
            for btn in size_buttons:
                size_text = btn.text.strip()
                if size_text and not size_text.startswith('$'):
                    sizes.append(size_text)
            
            # Extraer imagen
            image_elem = soup.find('img', {'alt': re.compile(name, re.IGNORECASE)})
            if not image_elem:
                image_elem = soup.find('img', {'data-testid': 'product-image'})
            
            image = image_elem.get('src') if image_elem else None
            
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
