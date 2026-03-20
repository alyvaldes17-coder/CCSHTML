"""
Script local para ejecutar el Nike Bot
Uso: python nike_bot_local.py <URL_PRODUCTO> <TALLA>

Ejemplo:
  python nike_bot_local.py "http://nike.cl/hv0823-108-air-jordan-4-retro/p?skuId=191697" "9"
"""

import sys
import requests
from nike_bot import NikeBot

def main():
    if len(sys.argv) < 3:
        print("❌ Uso: python nike_bot_local.py <URL_PRODUCTO> <TALLA>")
        print("\nEjemplo:")
        print('  python nike_bot_local.py "http://nike.cl/hv0823-108-air-jordan-4-retro/p?skuId=191697" "9"')
        sys.exit(1)
    
    url = sys.argv[1]
    size = sys.argv[2]
    
    print(f"🤖 Nike Bot Local")
    print(f"URL: {url}")
    print(f"Talla: {size}")
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
