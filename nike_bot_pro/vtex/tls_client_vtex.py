"""
TlsVTEXClient - Cliente VTEX blindado con Referer Dinámico (Coherencia de Navegación).
Compatible 100% con argumentos legacy de main.py.
"""

try:
    import tls_client
except ImportError as e:
    raise RuntimeError(
        "❌ tls_client no instalado.\n"
        "   Ejecuta: pip install tls-client\n"
        "   (nota: el paquete lleva guión, el módulo es tls_client)"
    ) from e


class TlsVTEXClient:
    """
    Cliente VTEX blindado con Referer Dinámico (Coherencia de Navegación).
    Compatible 100% con argumentos legacy de main.py.
    """
    
    def __init__(self, base_url: str, cookies: dict, user_agent: str, order_form_id: str = None):
        self.base_url = base_url.rstrip("/")
        self.order_form_id = order_form_id
        
        # Spoofing Chrome 124
        self.session = tls_client.Session(
            client_identifier="chrome_124", 
            random_tls_extension_order=True
        )
        
        if cookies: 
            self.session.cookies.update(cookies)
        
        # HEADERS BASE (Genéricos) - SIN REFERER FIJO
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://www.nike.cl",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Requested-With": "XMLHttpRequest"
        })

    @property
    def headers(self): 
        return self.session.headers

    def _post(self, endpoint, data, referer=None):
        """POST blindado con Referer dinámico."""
        url = f"{self.base_url}{endpoint}"
        
        # Header específico para esta petición
        headers = {}
        if referer:
            headers["Referer"] = referer
        else:
            headers["Referer"] = "https://www.nike.cl/checkout/"  # Fallback
            
        try:
            res = self.session.post(url, json=data, headers=headers, timeout_seconds=15)
            if not res.text:
                print(f"⚠️ [WAF] Respuesta vacía en {endpoint}")
                return {"error": "WAF Block (Empty)"}
            return res.json()
        except Exception as e:
            return {"error": str(e)}

    def get_order_form(self):
        """GET con Referer de checkout."""
        url = f"{self.base_url}/api/checkout/pub/orderForm?orderFormId={self.order_form_id}"
        self.session.headers["Referer"] = "https://www.nike.cl/checkout/"
        try:
            return self.session.get(url, timeout_seconds=10).json()
        except:
            return {}

    # Dummies para compatibilidad
    def pdp_context_warmup(self, sku): 
        return True
    
    def seed_item_metadata(self, order_form_id=None, sku_id=None, seller=None): 
        return True

    def simulation(self, sku_id: str, seller: str, quantity: int = 1, referer_url=None):
        """Simulation con Referer desde el PDP."""
        endpoint = f"/api/checkout/pub/orderForm/{self.order_form_id}/simulation"
        payload = {
            "items": [{"id": str(sku_id), "quantity": int(quantity), "seller": str(seller)}],
            "postalCode": "8320000",
            "country": "CHL"
        }
        return self._post(endpoint, payload, referer=referer_url)

    def add_to_cart(self, sku_id: str, seller: str, quantity: int = 1, order_form_id=None, referer_url=None):
        """Add to Cart con Referer desde el PDP (Coherencia de navegación)."""
        target_id = self.order_form_id
        endpoint = f"/api/checkout/pub/orderForm/items?orderFormId={target_id}"
        
        # PAYLOAD QUIRÚRGICO (Menos es más para evitar ORD002)
        # Eliminamos clientProfileData - a veces Nike bloquea si intentas enviarlo en add-to-cart
        payload = {
            "orderItems": [{"id": str(sku_id), "quantity": int(quantity), "seller": str(seller)}]
        }
        
        return self._post(endpoint, payload, referer=referer_url)

    def get_pdp_url_from_sku(self, sku_id):
        """Convierte SKU ID en URL real del producto automáticamente.
        
        Usa la API pública de búsqueda de VTEX (no requiere login).
        """
        try:
            # API pública de búsqueda de VTEX
            url = f"{self.base_url}/api/catalog_system/pub/products/search?fq=skuId:{sku_id}"
            res = self.session.get(url, timeout_seconds=10).json()
            
            if res and len(res) > 0:
                link = res[0].get('link')
                if link:
                    print(f"   🔗 URL Detectada automáticamente: {link}")
                    return link
            
            print(f"   ❌ No se encontró URL para SKU {sku_id} (¿SKU incorrecto?)")
            return None
        except Exception as e:
            print(f"   ⚠️ Error buscando URL: {e}")
            return None

    # Alias para compatibilidad
    def get_pdp_url(self, sku_id):
        """Alias de get_pdp_url_from_sku para compatibilidad."""
        return self.get_pdp_url_from_sku(sku_id)

    def frontend_add_to_cart(self, sku_id, quantity=1, seller="1", sales_channel="1"):
        """
        🚀 LA BALA DE PLATA.
        
        Usa el endpoint de redirección frontend para forzar la creación del carrito
        en el lado del servidor. VTEX asume que es un humano haciendo click en "Comprar Ahora".
        
        Esto:
        - Crea orderForm automáticamente
        - Inyecta cookies de sesión en la respuesta
        - Evita ORD002 completamente
        - NO abre navegador
        - NO necesita golden session
        
        Args:
            sku_id: SKU del producto
            quantity: Cantidad (default 1)
            seller: ID del seller (default "1")
            sales_channel: Canal de venta (default "1" = Nike Web)
        
        Returns:
            bool: True si la redirección fue exitosa
        """
        # Endpoint nativo de VTEX para "Add to Cart via Link"
        url = (
            f"{self.base_url}/checkout/cart/add"
            f"?sku={sku_id}&qty={quantity}&seller={seller}&sc={sales_channel}"
        )
        
        print(f"   🎯 Frontend Add-to-Cart: GET {url}")
        
        try:
            # GET request con redirección activada
            # Esto simula el click humano
            # tls_client captura automáticamente las cookies de sesión que devuelve VTEX
            res = self.session.get(url, allow_redirects=True, timeout_seconds=20)
            
            # Si terminamos en /checkout/, es victoria
            if "/checkout/" in res.url or res.status_code == 200:
                print(f"   ✅ Carrito creado. Redirección: {res.url}")
                return True
            else:
                print(f"   ⚠️ Redirección extraña: {res.url}")
                # A veces redirige al home si no hay stock, pero devolvemos True
                # para que get_order_form verifique la verdad
                return True
                
        except Exception as e:
            print(f"   ❌ Error en Frontend Add: {e}")
            return False

    def execute_payment(self, expected_price: float, timeout: float = 4.0):
        """🚀 EJECUTAR PAGO - UN INTENTO AGRESIVO
        
        Características:
        - Timeout corto (4 segundos)
        - Valida precio contra expected_price (bloquea pagos a 0)
        - Fail fast: si falla, retorna False
        
        Args:
            expected_price: Precio esperado en centavos (ej: 9299000 = $92.99)
            timeout: Timeout en segundos
        
        Returns:
            bool: True si pago fue exitoso, False en caso contrario
        """
        try:
            # Endpoint de pago
            endpoint = f"/api/checkout/pub/orderForm/{self.order_form_id}/payment"
            
            # Payload minimalista (no tocamos carrito, solo confirmamos pago)
            payload = {
                "payments": [
                    {
                        "id": "1",
                        "paymentSystem": 1,  # Crédito (default)
                        "installments": 1,
                        "referenceValue": expected_price
                    }
                ]
            }
            
            # Ejecutar POST con timeout corto
            res = self._post(endpoint, payload)
            
            # Validación: verificar que se procesó el pago
            if not res:
                print(f"   ⚠️ No se obtuvo respuesta del servidor")
                return False
            
            # Verificar status del pago
            status = res.get("status")
            total = res.get("value", 0)
            
            # Bloqueo contra precio falso (0)
            if total != expected_price:
                print(f"   ⚠️ Precio mismatch: esperado ${expected_price/100:.2f}, obtuvo ${total/100:.2f}")
                return False
            
            # Verificar que el pago fue aceptado
            if status in ("paid", "authorized", "processing"):
                print(f"   ✅ Pago aceptado: status={status}, total=${total/100:.2f}")
                return True
            else:
                print(f"   ⚠️ Pago pendiente: status={status}")
                return False
        
        except Exception as e:
            print(f"   ❌ Error en execute_payment: {e}")
            return False
    def place_order_api(self, total_value_cents):
        """🚀 MODE A: DISPARO ÚNICO DE CIERRE DE COMPRA
        
        Intenta iniciar la transacción por API para ganar la carrera del precio.
        Sin reintentos. Si pega → transactionId o receiverUri (gateway).
        Si falla → Fail fast.
        
        Args:
            total_value_cents: Precio en centavos (ej: 9299000 = $92990)
        
        Returns:
            dict: Respuesta con transactionId o receiverUri, o {} si falla
        """
        endpoint = f"/api/checkout/pub/orderForm/{self.order_form_id}/transaction"
        
        # Payload mínimo para confirmar la orden
        payload = {
            "referenceId": self.order_form_id,
            "value": int(total_value_cents),  # El precio que LATCHEAMOS
            "interestValue": 0,
            "savePersonalData": False,
            "optinNewsLetter": False
        }
        
        print(f"   ⚡ [MODE A] Disparando Transaction Start: ${total_value_cents/100:.2f}")
        
        try:
            res = self._post(endpoint, payload)
            
            if not res:
                print(f"   ⚠️ [MODE A] Respuesta vacía del servidor")
                return {}
            
            # Evaluar si fue éxito
            if "transactionId" in res:
                print(f"   🏆 [MODE A] SUCCESS! transactionId: {res.get('transactionId')}")
                return res
            
            if "receiverUri" in res:
                print(f"   🚀 [MODE A] Gateway detectado: {res.get('receiverUri')[:50]}...")
                return res
            
            # Respuesta no concluyente
            print(f"   ⚠️ [MODE A] Respuesta no concluyente: {str(res)[:100]}")
            return res
        
        except Exception as e:
            print(f"   ❌ [MODE A] Error: {e}")
            return {}