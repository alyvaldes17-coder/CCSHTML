"""Nike/VTEX Integration Service"""
import logging
from typing import Optional
import httpx

from vtex import VTEXClient

logger = logging.getLogger(__name__)


class NikeService:
    """Servicio para operaciones de Nike/VTEX"""
    
    # Nike Chile VTEX base URL (puedes cambiar según región)
    NIKE_BASE_URL = "https://www.nike.cl"
    
    def __init__(self):
        self.client = VTEXClient(
            base_url=self.NIKE_BASE_URL,
            session=httpx.Client(http2=True, timeout=30.0)
        )
        self.logger = logging.getLogger(__name__)
    
    # ===== STOCK METHODS =====
    
    async def check_stock(self, sku_id: str, seller: Optional[str] = None) -> dict:
        """
        Verifica disponibilidad de stock para un SKU
        
        Args:
            sku_id: ID del producto en VTEX
            seller: ID del vendedor (opcional)
            
        Returns:
            {"available": bool, "sku_id": str, "message": str}
        """
        try:
            has_stock = self.client.has_stock(sku_id, seller)
            
            return {
                "available": has_stock,
                "sku_id": sku_id,
                "message": "Stock disponible" if has_stock else "Sin stock",
                "seller": seller
            }
        except Exception as e:
            self.logger.error(f"Error checking stock for {sku_id}: {e}")
            return {
                "available": False,
                "sku_id": sku_id,
                "message": f"Error: {str(e)}",
                "error": True
            }
    
    # ===== CART METHODS =====
    
    async def get_cart(self) -> dict:
        """Obtiene el carrito actual"""
        try:
            order_form = self.client.get_order_form()
            
            items = order_form.get("items", [])
            total = order_form.get("value", 0) / 100  # VTEX devuelve en centavos
            
            return {
                "items": items,
                "total": total,
                "order_form_id": order_form.get("orderFormId"),
                "status": "ok"
            }
        except Exception as e:
            self.logger.error(f"Error getting cart: {e}")
            return {
                "items": [],
                "total": 0,
                "error": str(e),
                "status": "error"
            }
    
    async def add_to_cart(self, sku_id: str, seller: str, quantity: int = 1) -> dict:
        """Añade un item al carrito"""
        try:
            result = self.client.add_to_cart(sku_id, seller, quantity)
            
            return {
                "success": True,
                "sku_id": sku_id,
                "quantity": quantity,
                "cart": result,
                "message": "Item añadido al carrito"
            }
        except Exception as e:
            self.logger.error(f"Error adding to cart: {e}")
            return {
                "success": False,
                "sku_id": sku_id,
                "error": str(e),
                "message": "Error al añadir al carrito"
            }
    
    async def clear_cart(self) -> dict:
        """Limpia el carrito"""
        try:
            self.client.clear_cart()
            return {
                "success": True,
                "message": "Carrito limpiado"
            }
        except Exception as e:
            self.logger.error(f"Error clearing cart: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error al limpiar carrito"
            }
    
    # ===== CHECKOUT METHODS =====
    
    async def get_payment_methods(self) -> dict:
        """Obtiene métodos de pago disponibles"""
        try:
            order_form = self.client.get_order_form()
            payment_systems = self.client.get_payment_systems(order_form)
            
            return {
                "payment_systems": payment_systems,
                "count": len(payment_systems),
                "status": "ok"
            }
        except Exception as e:
            self.logger.error(f"Error getting payment methods: {e}")
            return {
                "payment_systems": [],
                "error": str(e),
                "status": "error"
            }
    
    async def get_order_summary(self) -> dict:
        """Obtiene resumen del orderfom actual (carrito + opciones de pago)"""
        try:
            order_form = self.client.get_order_form()
            
            total_cents = order_form.get("value", 0)
            total = total_cents / 100
            
            items = order_form.get("items", [])
            payment_systems = self.client.get_payment_systems(order_form)
            
            return {
                "items_count": len(items),
                "items": items,
                "total": total,
                "total_cents": total_cents,
                "payment_methods_available": len(payment_systems),
                "order_form_id": order_form.get("orderFormId"),
                "status": "ok"
            }
        except Exception as e:
            self.logger.error(f"Error getting order summary: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
