"""
================================================================================
STOCK CHECKER - Nike.cl API
================================================================================
Verifica stock disponible usando la API pública de Nike antes de comprar
"""

import requests
from typing import Dict, Any


def verificar_stock_nike(sku: str) -> Dict[str, Any]:
    """
    Verifica stock disponible en Nike.cl usando API pública
    
    Args:
        sku: SKU del producto (ej: "191681")
    
    Returns:
        dict: {
            'tiene_stock': bool,
            'cantidad': int,
            'precio': int,
            'nombre': str,
            'sku': str,
            'error': str (opcional)
        }
    
    Example:
        >>> stock = verificar_stock_nike("191681")
        >>> if stock['tiene_stock']:
        >>>     print(f"Stock disponible: {stock['cantidad']} unidades")
    """
    
    try:
        url = f"https://www.nike.cl/api/catalog_system/pub/products/search?fq=skuId:{sku}"
        
        print(f"🔍 [STOCK API] Verificando SKU {sku}...")
        
        # Request con User-Agent para evitar bloqueos
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
        }
        
        response = requests.get(url, timeout=10, headers=headers)
        
        # Validar respuesta HTTP
        if response.status_code != 200:
            print(f"❌ [STOCK API] Error HTTP {response.status_code}")
            return {
                'tiene_stock': False,
                'cantidad': 0,
                'precio': 0,
                'nombre': '',
                'sku': sku,
                'error': f'HTTP {response.status_code}'
            }
        
        data = response.json()
        
        # Validar que exista data
        if not data or len(data) == 0:
            print(f"❌ [STOCK API] SKU {sku} no encontrado en catálogo")
            return {
                'tiene_stock': False,
                'cantidad': 0,
                'precio': 0,
                'nombre': '',
                'sku': sku,
                'error': 'SKU no existe'
            }
        
        # Extraer info del producto
        producto = data[0]
        product_name = producto.get('productName', 'Producto sin nombre')
        items = producto.get('items', [])
        
        # Buscar el SKU específico en items
        for item in items:
            if str(item.get('itemId')) == str(sku):
                
                item_name = item.get('name', product_name)
                sellers = item.get('sellers', [])
                
                if not sellers:
                    print(f"⚠️ [STOCK API] Sin sellers para SKU {sku}")
                    return {
                        'tiene_stock': False,
                        'cantidad': 0,
                        'precio': 0,
                        'nombre': item_name,
                        'sku': sku,
                        'error': 'Sin sellers'
                    }
                
                # Obtener info del seller principal (Nike oficial)
                seller = sellers[0]
                commercial_offer = seller.get('commertialOffer', {})
                
                cantidad = commercial_offer.get('AvailableQuantity', 0)
                disponible = commercial_offer.get('IsAvailable', False)
                precio = commercial_offer.get('Price', 0)
                
                tiene_stock = disponible and cantidad > 0
                
                # Log resultado
                if tiene_stock:
                    print(f"✅ [STOCK API] {item_name}")
                    print(f"   SKU: {sku}")
                    print(f"   Stock: {cantidad} unidades disponibles")
                    print(f"   Precio: ${precio:,}")
                else:
                    print(f"❌ [STOCK API] SIN STOCK")
                    print(f"   Producto: {item_name}")
                    print(f"   SKU: {sku}")
                    print(f"   Cantidad: {cantidad}")
                
                return {
                    'tiene_stock': tiene_stock,
                    'cantidad': cantidad,
                    'precio': precio,
                    'nombre': item_name,
                    'sku': sku
                }
        
        # Si llegamos aquí, el SKU no está en los items
        print(f"❌ [STOCK API] SKU {sku} no encontrado en items del producto")
        return {
            'tiene_stock': False,
            'cantidad': 0,
            'precio': 0,
            'nombre': product_name,
            'sku': sku,
            'error': 'SKU no está en items'
        }
        
    except requests.exceptions.Timeout:
        print(f"⏱️ [STOCK API] Timeout verificando stock (>10s)")
        return {
            'tiene_stock': False,
            'cantidad': 0,
            'precio': 0,
            'nombre': '',
            'sku': sku,
            'error': 'Timeout'
        }
    
    except requests.exceptions.ConnectionError:
        print(f"🌐 [STOCK API] Error de conexión (sin internet o Nike caído)")
        return {
            'tiene_stock': False,
            'cantidad': 0,
            'precio': 0,
            'nombre': '',
            'sku': sku,
            'error': 'Sin conexión'
        }
    
    except Exception as e:
        print(f"❌ [STOCK API] Error inesperado: {e}")
        return {
            'tiene_stock': False,
            'cantidad': 0,
            'precio': 0,
            'nombre': '',
            'sku': sku,
            'error': str(e)
        }


def test_stock_checker():
    """Test rápido del checker de stock"""
    
    print("🧪 Testing Stock Checker\n")
    
    # Test con SKU sin stock (ejemplo)
    sku_sin_stock = "191681"
    result1 = verificar_stock_nike(sku_sin_stock)
    print(f"\nResultado: {result1}\n")
    
    # Test con SKU con stock (ejemplo)
    sku_con_stock = "176816"
    result2 = verificar_stock_nike(sku_con_stock)
    print(f"\nResultado: {result2}\n")


if __name__ == "__main__":
    test_stock_checker()
