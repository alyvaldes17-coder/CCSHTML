"""
Script local para ejecutar el Nike Bot

PRIMERO: Iniciar sesión una sola vez
  python nike_setup.py    (abre Nike.cl para que inicies sesión)
                          (la sesión se guarda automáticamente)

DESPUÉS: Ejecutar el bot cuantas veces quieras
  python nike_bot_local.py <URL_PRODUCTO>           (busca talla en BD)
  python nike_bot_local.py <URL_PRODUCTO> <TALLA>   (usa talla específica)

Ejemplos:
  python nike_bot_local.py "http://nike.cl/hv0823-108-air-jordan-4-retro/p?skuId=191697"
  python nike_bot_local.py "http://nike.cl/hv0823-108-air-jordan-4-retro/p?skuId=191697" "9"
"""

import sys
import re
import requests
from nike_bot import NikeBot

API_BASE = "https://nike-bot-pro-production.up.railway.app"

def extract_sku(url: str) -> str:
    """Extrae el SKU de la URL"""
    match = re.search(r'skuId=(\d+)', url)
    if match:
        return match.group(1)
    match = re.search(r'/products/(\d+)', url)
    if match:
        return match.group(1)
    return None

def get_size_from_api(sku: str) -> str:
    """Busca la talla configurada para el SKU en la API"""
    try:
        response = requests.get(f"{API_BASE}/nike/sku/{sku}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("size")
    except Exception as e:
        print(f"⚠️ No se pudo obtener talla de la API: {e}")
    return None

def main():
    if len(sys.argv) < 2:
        print("❌ Uso: python nike_bot_local.py <URL_PRODUCTO> [TALLA]")
        print("\nEjemplos:")
        print('  python nike_bot_local.py "http://nike.cl/hv0823-108-air-jordan-4-retro/p?skuId=191697"')
        print('  python nike_bot_local.py "http://nike.cl/hv0823-108-air-jordan-4-retro/p?skuId=191697" "9"')
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Obtener talla (desde argumento o desde BD)
    size = None
    if len(sys.argv) >= 3:
        # Talla especificada como argumento
        size = sys.argv[2]
        print(f"📌 Usando talla especificada: {size}")
    else:
        # Buscar talla en la BD
        sku = extract_sku(url)
        if sku:
            print(f"🔍 Buscando talla para SKU {sku} en la BD...")
            size = get_size_from_api(sku)
            if size:
                print(f"✓ Talla encontrada en BD: {size}")
            else:
                print(f"❌ SKU {sku} no tiene talla configurada en BD")
                print("   Usa: python nike_bot_local.py URL TALLA")
                sys.exit(1)
        else:
            print("❌ No se pudo extraer SKU de la URL")
            sys.exit(1)
    
    print(f"\n🤖 Nike Bot Local")
    print(f"URL: {url}")
    print(f"Talla: {size}")
    print("-" * 60)
    print()
    
    # Inicializar bot
    bot = NikeBot(headless=False)  # headless=False para que veas Chrome
    
    try:
        success = bot.add_to_cart(url, size)
        
        if success:
            print("\n✅ Producto en carrito. Completa el pago en Fintoc.")
            print("\nPresiona Enter para cerrar el navegador...")
            input()
        else:
            print("❌ Error al agregar al carrito")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        bot.close()

if __name__ == "__main__":
    main()
