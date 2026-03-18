"""Nike/VTEX API Endpoints"""
from fastapi import APIRouter
from services.nike_service import NikeService

router = APIRouter(prefix="/api/nike", tags=["nike"])
nike_service = NikeService()


# ===== STOCK ENDPOINTS =====

@router.get("/stock/{sku_id}")
async def check_stock(sku_id: str, seller: str = None):
    """
    Verifica disponibilidad de stock para un SKU
    
    Query Parameters:
    - seller: ID del vendedor (opcional)
    
    Response:
    {
        "available": bool,
        "sku_id": str,
        "message": str,
        "seller": str
    }
    """
    return await nike_service.check_stock(sku_id, seller)


# ===== CART ENDPOINTS =====

@router.get("/cart")
async def get_cart():
    """
    Obtiene el carrito actual
    
    Response:
    {
        "items": list,
        "total": float,
        "order_form_id": str,
        "status": str
    }
    """
    return await nike_service.get_cart()


@router.post("/cart/add")
async def add_to_cart(sku_id: str, seller: str, quantity: int = 1):
    """
    Añade un item al carrito
    
    Query Parameters:
    - sku_id: ID del producto
    - seller: ID del vendedor
    - quantity: Cantidad (default: 1)
    
    Response:
    {
        "success": bool,
        "sku_id": str,
        "quantity": int,
        "message": str
    }
    """
    return await nike_service.add_to_cart(sku_id, seller, quantity)


@router.post("/cart/clear")
async def clear_cart():
    """
    Limpia el carrito
    
    Response:
    {
        "success": bool,
        "message": str
    }
    """
    return await nike_service.clear_cart()


# ===== CHECKOUT ENDPOINTS =====

@router.get("/payment-methods")
async def get_payment_methods():
    """
    Obtiene métodos de pago disponibles
    
    Response:
    {
        "payment_systems": list,
        "count": int,
        "status": str
    }
    """
    return await nike_service.get_payment_methods()


@router.get("/order-summary")
async def get_order_summary():
    """
    Obtiene resumen del carrito y opciones de pago
    
    Response:
    {
        "items_count": int,
        "items": list,
        "total": float,
        "payment_methods_available": int,
        "order_form_id": str,
        "status": str
    }
    """
    return await nike_service.get_order_summary()
