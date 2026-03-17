from curl_cffi import requests
import time

def radar_stock_critico():
    print("📡 Iniciando Radar: Buscando SKUs con exactamente 1 unidad en Nike.cl...")
    
    # Buscamos los 50 productos más recientes de la tienda
    url = "https://www.nike.cl/api/catalog_system/pub/products/search?O=OrderByReleaseDateDESC&_from=0&_to=49"
    
    try:
        # Usamos nuestro camuflaje nivel Dios
        resp = requests.get(url, impersonate="chrome120", timeout=10)
        
        if resp.status_code == 403:
            print("❌ Bloqueo WAF (403).")
            return
            
        productos = resp.json()
        encontrados = 0
        
        print("-" * 60)
        for prod in productos:
            nombre_producto = prod.get('productName', 'Desconocido')
            link = prod.get('linkText', '')
            
            for item in prod.get('items', []):
                sku = item.get('itemId')
                nombre_talla = item.get('name')
                
                sellers = item.get('sellers', [])
                if sellers:
                    # Aquí leemos el stock real de VTEX
                    stock = sellers[0].get('commertialOffer', {}).get('AvailableQuantity', 0)
                    precio = sellers[0].get('commertialOffer', {}).get('Price', 0)
                    
                    # EL FILTRO MÁGICO
                    if stock == 1:
                        print(f"🎯 [STOCK=1] SKU: {sku} | Talla: {nombre_talla}")
                        print(f"👟 {nombre_producto} (${precio})")
                        print(f"🔗 https://www.nike.cl/{link}/p")
                        print("-" * 60)
                        encontrados += 1
                        
        print(f"✅ Escaneo terminado. Se encontraron {encontrados} SKUs vulnerables para hacer la prueba.")

    except Exception as e:
        print(f"❌ Error en el radar: {e}")

# Ejecutar el radar
if __name__ == "__main__":
    radar_stock_critico()