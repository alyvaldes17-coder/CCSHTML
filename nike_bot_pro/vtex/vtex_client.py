# vtex/vtex_client.py
import logging
from typing import Optional, Union

import httpx


class VTEXClient:
    """
    Cliente para interactuar con VTEX Checkout API.
    Soporta httpx.Client (HTTP/2) y requests.Session (legacy).
    """

    def __init__(self, base_url: str, session: Optional[Union[httpx.Client, object]] = None, log_level: str = "INFO"):
        self.base_url = base_url.rstrip("/")
        self.session = session or httpx.Client(http2=True, timeout=30.0)
        self.log = logging.getLogger(f"VTEXClient")
        self.log.setLevel(log_level.upper())

        # Configurar headers por defecto si no están en session
        if not self.session.headers.get("User-Agent"):
            self.session.headers.update({
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json",
            })

    def get_order_form(self) -> dict:
        """
        Obtiene el orderForm actual del carrito.
        """
        url = f"{self.base_url}/api/checkout/pub/orderForm"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def clear_cart(self) -> dict:
        """
        Limpia todos los items del carrito.
        """
        url = f"{self.base_url}/api/checkout/pub/orderForm/items/removeAll"
        response = self.session.post(url, json={})
        response.raise_for_status()
        return response.json()

    def add_to_cart(self, sku_id: str, seller: str, quantity: int = 1) -> dict:
        """
        Añade un SKU al carrito.
        """
        url = f"{self.base_url}/api/checkout/pub/orderForm/items"
        payload = {
            "items": [
                {
                    "id": sku_id,
                    "quantity": quantity,
                    "seller": seller,
                }
            ]
        }
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def has_stock(self, sku_id: str, seller: Optional[str] = None) -> bool:
        """Comprueba stock de un SKU llamando al endpoint de SKU.

        Nota: este método intenta una llamada a un endpoint privado de VTEX. Fallos son tratados y devuelven False.
        """
        try:
            url = f"{self.base_url}/api/catalog_system/pvt/sku/stockkeepingunitbyid/{sku_id}"
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            # data suele contener un array de sellers con stock
            sellers = data.get("sellers") or data.get("Sellers") or []
            if not sellers:
                return False
            if seller:
                for s in sellers:
                    if str(s.get("sellerId")) == str(seller) and s.get("availableQuantity", 0) > 0:
                        return True
                return False
            # any seller with availableQuantity > 0
            for s in sellers:
                if s.get("availableQuantity", 0) > 0:
                    return True
            return False
        except Exception:
            # si algo falló, tratamos como no stock para no comprometer
            return False

    # --- Payment helpers ---
    def get_payment_systems(self, order_form: dict) -> list[dict]:
        """Devuelve los métodos de pago disponibles para este orderForm."""
        payment_data = order_form.get("paymentData", {})
        return payment_data.get("paymentSystems", [])

    def find_mercadopago_id(self, order_form: dict) -> int | None:
        """Busca el paymentSystemId real de MercadoPago."""
        systems = self.get_payment_systems(order_form)

        for ps in systems:
            name = (ps.get("name") or "").lower()
            group = (ps.get("groupName") or "").lower()

            if "mercado" in name or "mercado" in group:
                return ps.get("id")

        return None

    def checkout_with_payment_system(self, order_form: dict, payment_system_id: int):
        order_form_id = order_form["orderFormId"]

        url = (
            f"{self.base_url}/api/checkout/pub/orderForm/"
            f"{order_form_id}/attachments/paymentData"
        )

        payload = {
            "payments": [
                {
                    "paymentSystem": payment_system_id,
                    "installments": 1,
                    "value": order_form["value"]
                }
            ]
        }

        r = self.session.post(url, json=payload)
        r.raise_for_status()
        return r.json()

    def extract_price(self, order_form: dict) -> float:
        """
        Extrae el precio REAL del OrderForm desde totalizers (en centavos).
        
        FUENTE CORRECTA: orderForm.totalizers[id="Items"].value
        
        Args:
            order_form: OrderForm dict desde VTEX API
            
        Returns:
            Precio en CLP (ej: 135990 para $135.990)
        """
        try:
            totalizers = order_form.get("totalizers", [])
            
            for t in totalizers:
                if t.get("id") == "Items":
                    price_cents = t.get("value", 0)
                    price = price_cents / 100
                    return price
            
            return 0
        except Exception as e:
            self.log.error(f"Error extrayendo precio: {e}")
            return 0
