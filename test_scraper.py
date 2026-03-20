#!/usr/bin/env python
"""Test del Nike Scraper"""
from nike_scraper import NikeScraper

scraper = NikeScraper()
url = 'http://nike.cl/hv0823-108-air-jordan-4-retro/p?skuId=191697'

print(f'[TEST] Scrapeando: {url}')
print('-' * 60)

try:
    product = scraper.scrape_product(url)
    
    if product and product.get('name') != 'Unknown':
        print('✓ ÉXITO - Producto scrapeado correctamente:')
        print(f'  SKU: {product.get("sku")}')
        print(f'  Nombre: {product.get("name")}')
        print(f'  Precio: ${product.get("price")}')
        print(f'  Tallas: {len(product.get("sizes", []))} disponibles - {product.get("sizes")[:3]}...')
        print(f'  Imagen: {"Sí" if product.get("image") else "No"}')
        print(f'  URL: {product.get("url")}')
    else:
        print('✗ FALLÓ - No se pudieron extraer datos válidos del producto')
        if product:
            print(f'\n  Datos retornados:')
            for k, v in product.items():
                print(f'    {k}: {v}')
except Exception as e:
    print(f'✗ ERROR: {e}')
    import traceback
    traceback.print_exc()
