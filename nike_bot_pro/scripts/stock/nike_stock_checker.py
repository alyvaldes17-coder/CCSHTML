"""
================================================================================
NIKE STOCK CHECKER - VERIFICACIÓN DE STOCK VÍA API OFICIAL
================================================================================

✅ Consulta API oficial de Nike.cl
✅ Retorna: cantidad, disponibilidad, precio, nombre
✅ Zero detección (request legítimo)
✅ Verificación ANTES de atacar

AUTOR: Nike Bot Pro
FECHA: 2025-02-07
================================================================================
"""

import requests
import json
from typing import Dict, Any


class NikeStockChecker:
    """Verificador de stock usando API oficial de Nike.cl"""
    
    BASE_URL = "https://www.nike.cl/api/catalog_system/pub/products/search"
    TIMEOUT = 10
    
    @staticmethod
    def verificar_stock(sku: str) -> Dict[str, Any]:
        """
        Verifica stock disponible en Nike.cl vía API oficial
        
        Args:
            sku: SKU del producto (ej: "191681")
        
        Returns:
            {
                'tiene_stock': bool,
                'cantidad': int,
                'disponible': bool,
                'precio': int,
                'nombre': str,
                'sku': str,
                'error': str (si aplica)
            }
        """
        
        try:
            # Construir URL
            url = f"{NikeStockChecker.BASE_URL}?fq=skuId:{sku}"
            
            # Request a API
            response = requests.get(url, timeout=NikeStockChecker.TIMEOUT)
            
            if response.status_code != 200:
                print(f"❌ [API] Error HTTP {response.status_code}")
                return {
                    'tiene_stock': False,
                    'cantidad': 0,
                    'disponible': False,
                    'precio': 0,
                    'nombre': 'Desconocido',
                    'sku': sku,
                    'error': f'HTTP {response.status_code}'
                }
            
            data = response.json()
            
            # Validar que hay datos
            if not data or len(data) == 0:
                print(f"❌ [API] SKU {sku} no encontrado en Nike.cl")
                return {
                    'tiene_stock': False,
                    'cantidad': 0,
                    'disponible': False,
                    'precio': 0,
                    'nombre': 'No encontrado',
                    'sku': sku,
                    'error': 'SKU no existe'
                }
            
            producto = data[0]
            items = producto.get('items', [])
            
            # Buscar el SKU específico en items
            for item in items:
                if str(item.get('itemId')) == str(sku):
                    
                    # Obtener comercial offer del primer seller (Nike principal)
                    sellers = item.get('sellers', [])
                    
                    if sellers:
                        seller = sellers[0]
                        offer = seller.get('commertialOffer', {})
                        
                        cantidad = offer.get('AvailableQuantity', 0)
                        disponible = offer.get('IsAvailable', False)
                        precio = offer.get('Price', 0)
                        nombre = item.get('name', producto.get('productName', 'Desconocido'))
                        
                        tiene_stock = disponible and cantidad > 0
                        
                        resultado = {
                            'tiene_stock': tiene_stock,
                            'cantidad': cantidad,
                            'disponible': disponible,
                            'precio': precio,
                            'nombre': nombre,
                            'sku': sku,
                            'error': None if tiene_stock else 'Sin stock'
                        }
                        
                        return resultado
            
            # SKU no encontrado en items
            print(f"❌ [API] SKU {sku} no encontrado en items")
            return {
                'tiene_stock': False,
                'cantidad': 0,
                'disponible': False,
                'precio': 0,
                'nombre': 'No encontrado',
                'sku': sku,
                'error': 'SKU no en items'
            }
            
        except requests.exceptions.Timeout:
            print(f"⏱️ [API] Timeout (>{NikeStockChecker.TIMEOUT}s)")
            return {
                'tiene_stock': False,
                'cantidad': 0,
                'disponible': False,
                'precio': 0,
                'nombre': 'Error',
                'sku': sku,
                'error': 'Timeout'
            }
        
        except requests.exceptions.ConnectionError:
            print(f"🌐 [API] Error de conexión")
            return {
                'tiene_stock': False,
                'cantidad': 0,
                'disponible': False,
                'precio': 0,
                'nombre': 'Error',
                'sku': sku,
                'error': 'No hay conexión'
            }
        
        except json.JSONDecodeError:
            print(f"❌ [API] Respuesta no es JSON válida")
            return {
                'tiene_stock': False,
                'cantidad': 0,
                'disponible': False,
                'precio': 0,
                'nombre': 'Error',
                'sku': sku,
                'error': 'JSON inválido'
            }
        
        except Exception as e:
            print(f"❌ [API] Error inesperado: {type(e).__name__}")
            return {
                'tiene_stock': False,
                'cantidad': 0,
                'disponible': False,
                'precio': 0,
                'nombre': 'Error',
                'sku': sku,
                'error': str(e)
            }

    @staticmethod
    def imprimir_resultado(stock_info: Dict[str, Any], verbose: bool = True) -> None:
        """Imprime resultado de forma legible"""
        
        if not verbose:
            return
        
        print(f"\n{'─'*70}")
        
        if stock_info['tiene_stock']:
            print(f"✅ [STOCK] Disponible")
            print(f"   Producto: {stock_info['nombre']}")
            print(f"   SKU: {stock_info['sku']}")
            print(f"   Cantidad: {stock_info['cantidad']} unidades")
            print(f"   Precio: ${stock_info['precio']:,}")
        else:
            print(f"❌ [STOCK] No disponible")
            print(f"   SKU: {stock_info['sku']}")
            print(f"   Cantidad: {stock_info['cantidad']}")
            if stock_info['error']:
                print(f"   Razón: {stock_info['error']}")
        
        print(f"{'─'*70}\n")


# Función de compatibilidad (para códigos antiguos)
def verificar_stock_sku(sku: str) -> Dict[str, Any]:
    """Alias para NikeStockChecker.verificar_stock()"""
    return NikeStockChecker.verificar_stock(sku)


# Testing
if __name__ == "__main__":
    print("🧪 [TEST] Nike Stock Checker\n")
    
    # Prueba con SKU sin stock (del ejemplo anterior)
    print("=" * 70)
    print("Prueba 1: SKU sin stock (191681)")
    print("=" * 70)
    resultado1 = NikeStockChecker.verificar_stock("191681")
    NikeStockChecker.imprimir_resultado(resultado1)
    
    # Prueba con SKU con stock
    print("=" * 70)
    print("Prueba 2: SKU con stock (176816)")
    print("=" * 70)
    resultado2 = NikeStockChecker.verificar_stock("176816")
    NikeStockChecker.imprimir_resultado(resultado2)
    
    # Prueba con SKU inválido
    print("=" * 70)
    print("Prueba 3: SKU inválido (999999)")
    print("=" * 70)
    resultado3 = NikeStockChecker.verificar_stock("999999")
    NikeStockChecker.imprimir_resultado(resultado3)
